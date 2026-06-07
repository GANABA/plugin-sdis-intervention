#!/usr/bin/env python3
"""Skill sdis-eau — Localise les points d'eau mobilisables et calcule l'autonomie hydraulique."""
import argparse
import json
import math
import sys
import requests

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
IGN_WFS_URL = "https://data.geopf.fr/wfs"
BAN_URL = "https://api-adresse.data.gouv.fr/search/"
TIMEOUT = 20
OVERPASS_HEADERS = {
    "User-Agent": "sdis-intervention-plugin/1.0 (urgence territoriale)",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
}

# Débits de référence SDIS (L/min pour 100m² de surface, sauf forêt = L/min par hectare)
DEBITS_SDIS = {
    "habitation": 60,
    "commercial": 120,
    "industriel": 180,
    "entrepot": 180,
    "foret": 250,
}


def overpass_query(query):
    """Exécute une requête Overpass avec fallback sur miroir alternatif."""
    for url in OVERPASS_URLS:
        try:
            resp = requests.post(
                url,
                data={"data": query},
                headers=OVERPASS_HEADERS,
                timeout=15,
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
        return None, None
    coords = feats[0]["geometry"]["coordinates"]
    return coords[1], coords[0]  # lat, lon


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


def cmd_localise(args):
    if args.address:
        lat, lon = geocode(args.address)
        if lat is None:
            print(json.dumps({"error": "Adresse introuvable via BAN"}), file=sys.stderr)
            sys.exit(1)
    else:
        lat, lon = args.lat, args.lon

    rayon = args.rayon
    bornes = []
    eau_naturelle = []
    erreurs = []

    # OSM Overpass — bornes incendie et points d'aspiration
    query = (
        f"[out:json][timeout:25];"
        f"(node[\"emergency\"=\"fire_hydrant\"](around:{rayon},{lat},{lon});"
        f"node[\"emergency\"=\"suction_point\"](around:{rayon},{lat},{lon}););"
        f"out body;"
    )
    try:
        result = overpass_query(query)
        if result is None:
            erreurs.append("OSM Overpass: tous les miroirs ont échoué (406/timeout)")
            result = {"elements": []}
        for el in result.get("elements", []):
            tags = el.get("tags", {})
            bornes.append({
                "type": tags.get("fire_hydrant:type", "inconnu"),
                "diametre_mm": tags.get("fire_hydrant:diameter", "inconnu"),
                "pression": tags.get("fire_hydrant:pressure"),
                "distance_m": haversine(lat, lon, el["lat"], el["lon"]),
                "lat": el["lat"],
                "lon": el["lon"],
            })
        bornes.sort(key=lambda x: x["distance_m"])
    except requests.Timeout:
        erreurs.append("OSM Overpass: timeout")
    except Exception as e:
        erreurs.append(f"OSM Overpass: {e}")

    # IGN WFS — cours d'eau et plans d'eau
    bbox = bbox_from_point(lat, lon, rayon)
    for layer, label in [
        ("BDTOPO_V3:cours_d_eau", "cours_eau"),
        ("BDTOPO_V3:plan_d_eau", "plan_eau"),
    ]:
        try:
            params = {
                "SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
                "TYPENAMES": layer, "OUTPUTFORMAT": "application/json",
                "COUNT": "5", "BBOX": bbox,
            }
            resp = requests.get(IGN_WFS_URL, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            for feat in resp.json().get("features", []):
                props = feat.get("properties", {})
                eau_naturelle.append({
                    "type": label,
                    "nom": props.get("toponyme") or props.get("nom") or "Sans nom",
                    "exploitable": True,
                })
        except Exception as e:
            erreurs.append(f"IGN WFS {layer}: {e}")

    result = {
        "point_reference": {"lat": lat, "lon": lon, "rayon_m": rayon},
        "bornes_incendie": bornes[:5],
        "eau_naturelle": eau_naturelle[:5],
        "avertissement": "Couverture OSM variable. Croiser avec SIG SDIS local.",
    }
    if erreurs:
        result["erreurs"] = erreurs
    return result


def cmd_autonomie(args):
    type_s = args.type
    debit_ref = DEBITS_SDIS[type_s]

    if type_s == "foret":
        # Surface en hectares
        debit_l_min = debit_ref * args.surface
    else:
        # Surface en m², débit pour 100m²
        debit_l_min = debit_ref * (args.surface / 100)

    vol_total = args.citernes * args.vol_citerne
    autonomie_min = vol_total / debit_l_min if debit_l_min > 0 else 0

    cadence_min = None
    citernes_necessaires = None
    renfort_a = None

    if args.distance_eau:
        vitesse_kmh = 30
        t_trajet = (args.distance_eau / 1000) / vitesse_kmh * 60 * 2
        t_remplissage = args.vol_citerne / 1000  # ~1 min / 1000L
        cadence_min = round(t_trajet + t_remplissage)
        t_vidange_citerne = args.vol_citerne / debit_l_min
        citernes_necessaires = math.ceil(cadence_min / t_vidange_citerne)
        renfort_a = round(autonomie_min * 0.7)

    return {
        "type_sinistre": type_s,
        "surface": args.surface,
        "debit_necessaire_l_min": round(debit_l_min),
        "volume_disponible_L": vol_total,
        "autonomie_sans_navette_min": round(autonomie_min, 1),
        "cadence_navette_min": cadence_min,
        "citernes_pour_continuite": citernes_necessaires,
        "demander_renfort_a_min": renfort_a,
        "note": "Débits SDIS standard. Adapter selon nature réelle du sinistre.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("localise", help="Localiser les points d'eau dans un rayon")
    grp = pl.add_mutually_exclusive_group(required=True)
    grp.add_argument("--address", help="Adresse du sinistre")
    grp.add_argument("--lat", type=float, help="Latitude (requiert --lon)")
    pl.add_argument("--lon", type=float)
    pl.add_argument("--rayon", type=int, default=500, help="Rayon en mètres (défaut: 500)")

    pa = sub.add_parser("autonomie", help="Calculer l'autonomie hydraulique")
    pa.add_argument("--type", required=True,
                    choices=["habitation", "commercial", "industriel", "entrepot", "foret"])
    pa.add_argument("--surface", type=float, required=True,
                    help="Surface en m² (ou hectares pour forêt)")
    pa.add_argument("--citernes", type=int, default=2)
    pa.add_argument("--vol-citerne", type=int, default=5000, dest="vol_citerne",
                    help="Volume d'une citerne en litres (défaut: 5000)")
    pa.add_argument("--distance-eau", type=int, dest="distance_eau",
                    help="Distance au point d'eau en mètres")

    args = p.parse_args()

    try:
        if args.cmd == "localise":
            if args.lat is not None and args.lon is None:
                p.error("--lon requis avec --lat")
            result = cmd_localise(args)
        else:
            result = cmd_autonomie(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.Timeout:
        print(json.dumps({"error": "timeout", "detail": "API non disponible"}), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(json.dumps({"error": "reseau", "detail": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
