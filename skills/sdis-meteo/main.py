#!/usr/bin/env python3
"""Skill sdis-meteo — Météo temps réel, indice FWI et vigilances crues Vigicrues."""
import argparse
import json
import math
import sys
import requests

OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
VIGICRUES_URL = "https://www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson/"
BAN_URL = "https://api-adresse.data.gouv.fr/search/"
TIMEOUT = 15

# Interprétation FWI
FWI_NIVEAUX = [
    (0, 5, "FAIBLE", "Conditions normales"),
    (5, 12, "MODÉRÉ", "Surveillance recommandée"),
    (12, 20, "ÉLEVÉ", "Risque de propagation rapide"),
    (20, 30, "TRÈS ÉLEVÉ", "Intervention difficile, renforts à anticiper"),
    (30, float("inf"), "EXTRÊME", "Conditions de feu extrêmes — sécurité maximale"),
]

# Vigilances Vigicrues
VIGI_NIVEAUX = {1: "VERT", 2: "JAUNE", 3: "ORANGE", 4: "ROUGE"}
VIGI_LABELS = {1: "Pas de vigilance", 2: "Risque de débordement", 3: "Risque important", 4: "Risque majeur"}


def geocode(address):
    resp = requests.get(BAN_URL, params={"q": address, "limit": 1}, timeout=TIMEOUT)
    resp.raise_for_status()
    feats = resp.json().get("features", [])
    if not feats:
        return None, None
    coords = feats[0]["geometry"]["coordinates"]
    return coords[1], coords[0]


def fwi_interpretation(fwi_val):
    if fwi_val is None:
        return "inconnu"
    for vmin, vmax, label, desc in FWI_NIVEAUX:
        if vmin <= fwi_val < vmax:
            return {"niveau": label, "description": desc, "valeur": round(fwi_val, 1)}
    return {"niveau": "EXTRÊME", "valeur": round(fwi_val, 1)}


def cmd_conditions(args):
    if args.address:
        lat, lon = geocode(args.address)
        if lat is None:
            print(json.dumps({"error": "Adresse introuvable"}), file=sys.stderr)
            sys.exit(1)
    else:
        lat, lon = args.lat, args.lon

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "precipitation",
            "weather_code",
        ]),
        "daily": "precipitation_sum,wind_speed_10m_max,wind_gusts_10m_max,precipitation_hours",
        "wind_speed_unit": "kmh",
        "timezone": "Europe/Paris",
        "forecast_days": 1,
    }

    try:
        resp = requests.get(OPENMETEO_URL, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout:
        print(json.dumps({"error": "OpenMeteo timeout"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    current = data.get("current", {})
    daily = data.get("daily", {})

    # FWI non disponible sur OpenMeteo — calcul simplifié (indice Angstrom modifié)
    # Angstrom : H/20 + (27-T)/10 — plus bas = plus dangereux
    # On inverse et normalise pour obtenir un score 0-50+ comparable au FWI canadien
    humidity = current.get("relative_humidity_2m", 50)
    temperature = current.get("temperature_2m", 15)
    wind = current.get("wind_speed_10m", 0)
    precip = current.get("precipitation", 0)
    angstrom = (humidity / 20) + ((27 - temperature) / 10)
    fwi_approx = max(0, (3 - angstrom) * 10 + wind * 0.3)
    if precip > 2:
        fwi_approx = max(0, fwi_approx - 10)

    wind_dir = current.get("wind_direction_10m")
    wind_dir_label = _direction_label(wind_dir) if wind_dir is not None else "inconnu"

    result = {
        "coordonnees": {"lat": lat, "lon": lon},
        "horodatage": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "humidite_pct": current.get("relative_humidity_2m"),
        "vent_kmh": current.get("wind_speed_10m"),
        "vent_direction_deg": wind_dir,
        "vent_direction": wind_dir_label,
        "rafales_kmh": current.get("wind_gusts_10m"),
        "precipitation_mm": current.get("precipitation"),
        "risque_propagation_fwi": fwi_interpretation(fwi_approx),
        "note_fwi": "Indice approche (Angstrom modifié). FWI officiel via Météo-France.",
        "max_journee": {
            "vent_max_kmh": daily.get("wind_speed_10m_max", [None])[0],
            "rafales_max_kmh": daily.get("wind_gusts_10m_max", [None])[0],
            "precipitation_totale_mm": daily.get("precipitation_sum", [None])[0],
        },
        "source": "OpenMeteo (libre, sans clé API)",
    }
    return result


def _direction_label(deg):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                  "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    idx = round(deg / 22.5) % 16
    return directions[idx]


def _bbox_contains(geometry, lat, lon, margin):
    """Vérifie si un point est dans le bounding box d'une géométrie + marge."""
    try:
        coords_list = geometry.get("coordinates", [])
        geom_type = geometry.get("type", "")
        if geom_type == "MultiLineString":
            all_pts = [pt for line in coords_list for pt in line]
        elif geom_type == "LineString":
            all_pts = coords_list
        else:
            return False
        lons = [p[0] for p in all_pts]
        lats = [p[1] for p in all_pts]
        return (min(lons) - margin <= lon <= max(lons) + margin and
                min(lats) - margin <= lat <= max(lats) + margin)
    except Exception:
        return False


def cmd_vigicrues(args):
    lat, lon = args.lat, args.lon
    rayon_deg = args.rayon

    try:
        resp = requests.get(VIGICRUES_URL, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout:
        print(json.dumps({"error": "Vigicrues timeout"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    vigilances = []
    for feat in data.get("features", []):
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        if not _bbox_contains(geom, lat, lon, rayon_deg):
            continue
        niv = props.get("NivSituVigiCruEnt", 1)
        vigilances.append({
            "cours_eau": props.get("lbentcru", "inconnu"),
            "code": props.get("CdEntCru"),
            "niveau": VIGI_NIVEAUX.get(niv, str(niv)),
            "label": VIGI_LABELS.get(niv, "inconnu"),
            "valeur_numerique": niv,
        })

    vigilances.sort(key=lambda x: -x["valeur_numerique"])
    alerte_max = max((v["valeur_numerique"] for v in vigilances), default=1)

    return {
        "coordonnees": {"lat": lat, "lon": lon, "rayon_deg": rayon_deg},
        "alerte_maximale": VIGI_NIVEAUX.get(alerte_max, "VERT"),
        "nb_troncons": len(vigilances),
        "vigilances": vigilances[:10],
        "source": "Vigicrues — www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson/",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("conditions", help="Météo actuelle et indice FWI")
    grp = pc.add_mutually_exclusive_group(required=True)
    grp.add_argument("--address")
    grp.add_argument("--lat", type=float)
    pc.add_argument("--lon", type=float)

    pv = sub.add_parser("vigicrues", help="Vigilances crues dans un rayon")
    pv.add_argument("--lat", type=float, required=True)
    pv.add_argument("--lon", type=float, required=True)
    pv.add_argument("--rayon", type=float, default=0.5,
                    help="Rayon de recherche en degrés (défaut: 0.5 ≈ 55km)")

    args = p.parse_args()

    try:
        if args.cmd == "conditions":
            if args.lat is not None and args.lon is None:
                p.error("--lon requis avec --lat")
            result = cmd_conditions(args)
        else:
            result = cmd_vigicrues(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except requests.Timeout:
        print(json.dumps({"error": "timeout"}), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(json.dumps({"error": "reseau", "detail": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
