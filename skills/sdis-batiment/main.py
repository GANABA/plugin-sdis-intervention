#!/usr/bin/env python3
"""Skill sdis-batiment — Qualifie un bâtiment : type, hauteur, accès, propagation."""
import argparse
import json
import math
import sys
import requests

BAN_URL = "https://api-adresse.data.gouv.fr/search/"
IGN_WFS_URL = "https://data.geopf.fr/wfs"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
OVERPASS_HEADERS = {
    "User-Agent": "sdis-intervention-plugin/1.0 (urgence territoriale)",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}
TIMEOUT = 20


def overpass_query(query):
    """Exécute une requête Overpass avec fallback sur miroir alternatif."""
    for url in OVERPASS_URLS:
        try:
            resp = requests.post(
                url,
                data={"data": query},
                headers=OVERPASS_HEADERS,
                timeout=25,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            continue
    return None


def geocode(address):
    resp = requests.get(BAN_URL, params={"q": address, "limit": 1}, timeout=TIMEOUT)
    resp.raise_for_status()
    feats = resp.json().get("features", [])
    if not feats:
        return None, None, {}
    feat = feats[0]
    coords = feat["geometry"]["coordinates"]
    return coords[1], coords[0], feat.get("properties", {})


def bbox_from_point(lat, lon, rayon_m):
    dlat = rayon_m / 111320
    dlon = rayon_m / (111320 * math.cos(math.radians(lat)))
    return f"{lat-dlat},{lon-dlon},{lat+dlat},{lon+dlon},urn:ogc:def:crs:EPSG::4326"


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return round(R * 2 * math.asin(math.sqrt(a)))


def _centroid(geometry):
    """Calcule le centroïde approximatif d'une géométrie GeoJSON."""
    coords = geometry.get("coordinates", [])
    geom_type = geometry.get("type", "")
    try:
        if geom_type == "Point":
            return coords[1], coords[0]
        if geom_type in ("Polygon", "MultiPolygon"):
            flat = coords[0][0] if geom_type == "MultiPolygon" else coords[0]
            lats = [c[1] for c in flat]
            lons = [c[0] for c in flat]
            return sum(lats) / len(lats), sum(lons) / len(lons)
    except Exception:
        pass
    return None, None


def cmd_qualifier(args):
    lat, lon, ban_props = geocode(args.address)
    if lat is None:
        print(json.dumps({"error": "Adresse introuvable via BAN"}), file=sys.stderr)
        sys.exit(1)

    erreurs = []
    batiment_principal = {}
    adjacents = []

    # --- IGN WFS : bâtiment principal (rayon 60m) ---
    bbox_proche = bbox_from_point(lat, lon, 60)
    try:
        params = {
            "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
            "TYPENAMES": "BDTOPO_V3:batiment", "OUTPUTFORMAT": "application/json",
            "COUNT": "1", "BBOX": bbox_proche,
        }
        resp = requests.get(IGN_WFS_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        feats = resp.json().get("features", [])
        if feats:
            props = feats[0].get("properties", {})
            batiment_principal = {
                "nature": props.get("nature", "inconnu"),
                "usage_principal": props.get("usage_1", "inconnu"),
                "hauteur_m": props.get("hauteur"),
                "nombre_etages": props.get("nombre_d_etages"),
                "nombre_logements": props.get("nombre_de_logements"),
                "materiaux_murs": props.get("materiaux_des_murs", "inconnu"),
                "annee_construction": props.get("date_de_construction"),
                "etat": props.get("etat_de_l_objet", "inconnu"),
            }
        else:
            batiment_principal = {"note": "Aucun bâtiment IGN trouvé dans un rayon de 60m"}
    except Exception as e:
        erreurs.append(f"IGN WFS bâtiment: {e}")

    # --- IGN WFS : bâtiments adjacents (rayon 120m) ---
    bbox_adj = bbox_from_point(lat, lon, 120)
    try:
        params["COUNT"] = "15"
        params["BBOX"] = bbox_adj
        resp = requests.get(IGN_WFS_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        for feat in resp.json().get("features", [])[1:8]:
            props = feat.get("properties", {})
            geom = feat.get("geometry", {})
            clat, clon = _centroid(geom)
            dist = haversine(lat, lon, clat, clon) if clat else None
            adjacents.append({
                "nature": props.get("nature", "inconnu"),
                "usage": props.get("usage_1", "inconnu"),
                "hauteur_m": props.get("hauteur"),
                "distance_m": dist,
            })
    except Exception as e:
        erreurs.append(f"IGN WFS adjacents: {e}")

    # --- OSM Overpass : voirie et accès ---
    query = (
        f"[out:json];"
        f"way[\"highway\"](around:200,{lat},{lon});"
        f"out body geom;"
    )
    acces = []
    try:
        result = overpass_query(query)
        if result is None:
            erreurs.append("OSM voirie: tous les miroirs Overpass ont échoué")
            result = {"elements": []}
        types_utiles = {"residential", "primary", "secondary", "tertiary", "service", "unclassified"}
        for el in result.get("elements", []):
            tags = el.get("tags", {})
            if tags.get("highway") in types_utiles:
                acces.append({
                    "nom": tags.get("name", "voie sans nom"),
                    "type": tags.get("highway"),
                    "largeur_m": tags.get("width"),
                    "sens_unique": tags.get("oneway") == "yes",
                    "tonnage_max_t": tags.get("maxweight"),
                })
        acces = acces[:5]
    except Exception as e:
        erreurs.append(f"OSM voirie: {e}")

    result = {
        "adresse_geocodee": ban_props.get("label", args.address),
        "coordonnees": {"lat": round(lat, 6), "lon": round(lon, 6)},
        "batiment_principal": batiment_principal,
        "batiments_adjacents": adjacents,
        "acces_vehicules": acces,
        "source": "BAN + IGN BD Topo WFS + OSM Overpass",
    }
    if erreurs:
        result["erreurs"] = erreurs
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pq = sub.add_parser("qualifier", help="Qualifier un bâtiment depuis une adresse")
    pq.add_argument("--address", required=True, help="Adresse complète du bâtiment")

    args = p.parse_args()

    try:
        if args.cmd == "qualifier":
            result = cmd_qualifier(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.Timeout:
        print(json.dumps({"error": "timeout"}), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(json.dumps({"error": "reseau", "detail": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
