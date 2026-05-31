#!/usr/bin/env python3
"""Skill sdis-population — Population exposée, personnes vulnérables et ERP dans un rayon."""
import argparse
import csv
import json
import math
import os
import sys
import requests

BAN_URL = "https://api-adresse.data.gouv.fr/search/"
GEO_API_URL = "https://geo.api.gouv.fr/communes"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TIMEOUT = 20

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
RP_FILE = os.path.join(DATA_DIR, "rp2022_iris.csv")
BPE_FILE = os.path.join(DATA_DIR, "bpe-ensemble.csv")

# Codes BPE (data.gouv.fr) — A=administration, C=enseignement, D=santé, F=sports
BPE_TYPES_PREFIX = {"A": "administration", "C": "enseignement", "D": "sante", "F": "sports_loisirs"}
ERP_PRIORITAIRES_PREFIX = {"D1", "D3", "C1"}  # D1x=hôpitaux, D3x=EHPAD, C1x=maternelle


def geocode(address):
    resp = requests.get(BAN_URL, params={"q": address, "limit": 1}, timeout=TIMEOUT)
    resp.raise_for_status()
    feats = resp.json().get("features", [])
    if not feats:
        return None, None, None
    feat = feats[0]
    coords = feat["geometry"]["coordinates"]
    return coords[1], coords[0], feat["properties"].get("citycode")


def get_commune_from_coords(lat, lon):
    resp = requests.get(
        GEO_API_URL,
        params={"lat": lat, "lon": lon, "fields": "code,nom,population,codeDepartement"},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else {}


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return round(R * 2 * math.asin(math.sqrt(a)))


def _detect_rp_prefix(fieldnames):
    """Détecte automatiquement le préfixe d'année RP (P22_, P20_, etc.)."""
    return next(
        (h[:3] for h in fieldnames if h.startswith("P") and h[1:3].isdigit() and "_POP" in h),
        "P22"
    )


def cmd_zone(args):
    if args.address:
        lat, lon, _ = geocode(args.address)
        if lat is None:
            print(json.dumps({"error": "Adresse introuvable"}), file=sys.stderr)
            sys.exit(1)
    else:
        lat, lon = args.lat, args.lon

    commune = get_commune_from_coords(lat, lon)
    pop_commune = commune.get("population", "inconnue")
    nom_commune = commune.get("nom", "inconnue")

    # Estimation dans le rayon (proportionnelle à la surface, superficie moyenne commune ~17km²)
    pop_estimee = None
    if isinstance(pop_commune, int):
        ratio = min(math.pi * args.rayon ** 2 / 17_000_000, 1.0)
        pop_estimee = round(pop_commune * ratio)

    # Données RP fines : agrégation de tous les IRIS de la commune
    rp_data = {}
    if os.path.exists(RP_FILE):
        code_com = commune.get("code", "")
        totaux = {"pop": 0, "pop65": 0, "pop80": 0, "men": 0, "nb_iris": 0}
        with open(RP_FILE, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter=";")
            prefix = _detect_rp_prefix(reader.fieldnames or [])
            for row in reader:
                if row.get("COM", "") != code_com:
                    continue
                try:
                    totaux["pop"] += float(row.get(f"{prefix}_POP", 0))
                    totaux["pop65"] += float(row.get(f"{prefix}_POP65P", 0))
                    totaux["pop80"] += float(row.get(f"{prefix}_POP80P", 0))
                    totaux["men"] += float(row.get(f"{prefix}_PMEN", 0))
                    totaux["nb_iris"] += 1
                except (ValueError, TypeError):
                    pass
        if totaux["nb_iris"] > 0:
            rp_data = {
                "pop_totale": round(totaux["pop"]),
                "pop_65plus": round(totaux["pop65"]),
                "pop_80plus": round(totaux["pop80"]),
                "nb_menages": round(totaux["men"]),
                "nb_iris": totaux["nb_iris"],
                "millesime": f"RP {prefix[1:]}",
            }

    return {
        "commune": nom_commune,
        "code_commune": commune.get("code"),
        "coordonnees": {"lat": lat, "lon": lon},
        "rayon_m": args.rayon,
        "population_commune": pop_commune,
        "population_estimee_rayon": pop_estimee,
        "donnees_rp_commune": rp_data if rp_data else "absent — voir data/README.md",
        "note": "Estimation proportionnelle surface. Précision IRIS dans donnees_rp_commune.",
    }


def cmd_vulnerables(args):
    commune_code = args.commune

    if not os.path.exists(RP_FILE):
        return {
            "erreur": "Fichier data/rp2022_iris.csv absent.",
            "action": "Télécharger sur https://www.insee.fr/fr/statistiques/8647014",
        }

    iris_data = []
    with open(RP_FILE, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter=";")
        prefix = _detect_rp_prefix(reader.fieldnames or [])
        for row in reader:
            if not row.get("COM", "").startswith(commune_code[:5]):
                continue
            try:
                pop = float(row.get(f"{prefix}_POP", 0))
                pop65 = float(row.get(f"{prefix}_POP65P", 0))
                pop80 = float(row.get(f"{prefix}_POP80P", 0))
                men = float(row.get(f"{prefix}_PMEN", 0))
                if pop > 0:
                    iris_data.append({
                        "iris": row.get("IRIS"),
                        "iris_code": row.get("IRIS", ""),
                        "pop_totale": round(pop),
                        "pop_65plus": round(pop65),
                        "pop_80plus": round(pop80),
                        "pct_65plus": round(pop65 / pop * 100, 1),
                        "nb_menages": round(men),
                    })
            except (ValueError, TypeError, ZeroDivisionError):
                pass

    if not iris_data:
        return {"erreur": f"Aucun IRIS trouvé pour le code commune {commune_code}"}

    iris_data.sort(key=lambda x: x["pct_65plus"], reverse=True)
    totaux = {
        "pop_totale": sum(i["pop_totale"] for i in iris_data),
        "pop_65plus": sum(i["pop_65plus"] for i in iris_data),
        "pop_80plus": sum(i["pop_80plus"] for i in iris_data),
    }

    return {
        "commune_code": commune_code,
        "millesime": f"RP {prefix[1:]}",
        "totaux": totaux,
        "iris_les_plus_vulnerables": iris_data[:5],
        "source": "INSEE RP local",
    }


def cmd_erp(args):
    if args.address:
        lat, lon, _ = geocode(args.address)
        if lat is None:
            print(json.dumps({"error": "Adresse introuvable"}), file=sys.stderr)
            sys.exit(1)
    else:
        lat, lon = args.lat, args.lon

    erp_list = []

    if os.path.exists(BPE_FILE):
        # Format data.gouv.fr : colonnes françaises, coordonnées WGS84, données agrégées par commune
        seen = set()  # dédoublonner par (commune, type)
        with open(BPE_FILE, encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                code_eq = row.get("Code d'équipement", "")
                if args.type != "tous" and not code_eq.startswith(args.type):
                    continue
                coords_str = row.get("Coordonnées géo (commune)", "")
                if not coords_str or "," not in coords_str:
                    continue
                try:
                    eq_lat, eq_lon = map(float, coords_str.split(","))
                    dist = haversine(lat, lon, eq_lat, eq_lon)
                    if dist > args.rayon:
                        continue
                    key = (row.get("Code INSEE", ""), code_eq)
                    if key in seen:
                        continue
                    seen.add(key)
                    erp_list.append({
                        "type_code": code_eq,
                        "type_label": row.get("Type d'équipement", code_eq),
                        "commune": row.get("Commune", ""),
                        "code_insee": row.get("Code INSEE", ""),
                        "nombre": row.get("Nombre", ""),
                        "distance_m_centroide": dist,
                        "prioritaire": code_eq[:2] in ERP_PRIORITAIRES_PREFIX,
                        "note": "Distance au centroïde commune (approximation)",
                    })
                except (ValueError, TypeError):
                    continue
        erp_list.sort(key=lambda x: (not x["prioritaire"], x["distance_m_centroide"]))
        source = "BPE local (data.gouv.fr)"
    else:
        # Fallback OSM — données individuelles précises
        amenity_map = {
            "tous": ["hospital", "clinic", "school", "kindergarten", "nursing_home", "fire_station"],
            "A": ["hospital", "clinic", "pharmacy", "nursing_home"],
            "C": ["school", "kindergarten", "college", "university"],
            "F": ["sports_centre", "stadium"],
        }
        amenities = "|".join(amenity_map.get(args.type, amenity_map["tous"]))
        query = (
            f"[out:json];"
            f"(node[\"amenity\"~\"{amenities}\"](around:{args.rayon},{lat},{lon});"
            f"way[\"amenity\"~\"{amenities}\"](around:{args.rayon},{lat},{lon}););"
            f"out center;"
        )
        try:
            resp = requests.post(
                OVERPASS_URL, data={"data": query},
                headers={"Accept": "application/json"}, timeout=20,
            )
            resp.raise_for_status()
            for el in resp.json().get("elements", []):
                tags = el.get("tags", {})
                el_lat = el.get("lat") or el.get("center", {}).get("lat")
                el_lon = el.get("lon") or el.get("center", {}).get("lon")
                if el_lat and el_lon:
                    erp_list.append({
                        "type_code": tags.get("amenity"),
                        "type_label": tags.get("amenity"),
                        "nom": tags.get("name", "Sans nom"),
                        "distance_m": haversine(lat, lon, el_lat, el_lon),
                    })
            erp_list.sort(key=lambda x: x["distance_m"])
        except Exception as e:
            return {"error": f"OSM Overpass: {e}", "note": "BPE local absent, OSM en fallback"}
        source = "OSM Overpass (fallback — BPE absent)"

    return {
        "point_reference": {"lat": lat, "lon": lon, "rayon_m": args.rayon},
        "nb_erp_trouves": len(erp_list),
        "erp": erp_list[:15],
        "source": source,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pz = sub.add_parser("zone", help="Population dans un périmètre")
    grp = pz.add_mutually_exclusive_group(required=True)
    grp.add_argument("--address")
    grp.add_argument("--lat", type=float)
    pz.add_argument("--lon", type=float)
    pz.add_argument("--rayon", type=int, default=500)

    pv = sub.add_parser("vulnerables", help="Profil vulnérabilité IRIS par commune")
    pv.add_argument("--commune", required=True, help="Code INSEE commune (ex: 25056)")

    pe = sub.add_parser("erp", help="ERP dans un rayon")
    grp2 = pe.add_mutually_exclusive_group(required=True)
    grp2.add_argument("--address")
    grp2.add_argument("--lat", type=float)
    pe.add_argument("--lon", type=float)
    pe.add_argument("--rayon", type=int, default=500)
    pe.add_argument("--type", default="tous", choices=["tous", "D", "C", "F"],
                    help="D=sante, C=enseignement, F=sports")

    args = p.parse_args()

    try:
        if args.cmd == "zone":
            if args.lat is not None and args.lon is None:
                p.error("--lon requis avec --lat")
            result = cmd_zone(args)
        elif args.cmd == "vulnerables":
            result = cmd_vulnerables(args)
        else:
            if args.lat is not None and args.lon is None:
                p.error("--lon requis avec --lat")
            result = cmd_erp(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.Timeout:
        print(json.dumps({"error": "timeout"}), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(json.dumps({"error": "reseau", "detail": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
