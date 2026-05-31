# API — sdis-meteo

## OpenMeteo — Météo temps réel

**Endpoint :** `GET https://api.open-meteo.com/v1/forecast`
**Auth :** aucune (libre)
**Params clés :**

| Param | Description |
|-------|-------------|
| `latitude`, `longitude` | Coordonnées WGS84 |
| `current` | Variables temps réel (CSV) |
| `daily` | Variables journalières (CSV) |
| `wind_speed_unit` | `kmh`, `ms`, `mph`, `kn` |
| `timezone` | ex: `Europe/Paris` |
| `forecast_days` | 1 à 16 |

Variables `current` utiles :
- `temperature_2m`, `relative_humidity_2m`
- `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`
- `precipitation`, `weather_code`

Variable `daily` clé pour SDIS :
- `fire_danger_index_max` — **Fire Weather Index (FWI)** journalier

## Interprétation FWI

| FWI | Niveau | Action |
|-----|--------|--------|
| < 5 | FAIBLE | Normal |
| 5–12 | MODÉRÉ | Surveillance |
| 12–20 | ÉLEVÉ | Propagation rapide possible |
| 20–30 | TRÈS ÉLEVÉ | Renforts à anticiper |
| > 30 | EXTRÊME | Sécurité maximale, retrait si nécessaire |

## Vigicrues — Vigilances crues

**Endpoint :** `GET https://www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson/`
**Auth :** aucune
**Format :** GeoJSON, France entière, mis à jour toutes les heures

Propriétés utiles :
| Propriété | Description |
|-----------|-------------|
| `lbentcru` | Libellé du cours d'eau / tronçon |
| `CdEntCru` | Code de l'entité de vigilance |
| `NivSituVigiCruEnt` | Niveau : 1=vert, 2=jaune, 3=orange, 4=rouge |

⚠ L'URL `api.vigicrues.gouv.fr` n'existe pas — utiliser `www.vigicrues.gouv.fr/services/`.
