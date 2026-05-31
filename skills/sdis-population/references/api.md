# API — sdis-population

## Geo API gouvernement — Communes

**Endpoint :** `GET https://geo.api.gouv.fr/communes`
**Auth :** aucune

Paramètres utiles : `lat`, `lon`, `fields` (code,nom,population,codeDepartement)

⚠ L'endpoint `/communes/{code}/iris` a été **supprimé**. Ne pas l'utiliser.

## INSEE — Fichiers RP locaux (recommandé)

Télécharger une fois, stocker dans `data/` :

**Fichier RP 2022 par IRIS :**
`https://www.insee.fr/fr/statistiques/8647014`
→ Télécharger le CSV "France hors Mayotte" (22 Mo)
→ Placer dans `data/rp2022_iris.csv`

> **Historique des liens :** `7704076` = RP 2020 (toujours accessible, préfixe `P20_`).
> `8647014` = RP 2022 (plus récent, préfixe `P22_`). Le script détecte automatiquement le préfixe.

Colonnes utiles (préfixe auto-détecté) :
| Colonne générique | RP 2022 | Description |
|-------------------|---------|-------------|
| `{prefix}_POP` | `P22_POP` | Population totale |
| `{prefix}_POP65P` | `P22_POP65P` | Population 65 ans et plus |
| `{prefix}_POP80P` | `P22_POP80P` | Population 80 ans et plus |
| `{prefix}_PMEN` | `P22_PMEN` | Population des ménages |
| `COM` | — | Code commune INSEE |
| `IRIS` | — | Code IRIS (9 chiffres) |

## INSEE BPE — Équipements

**BPE 2024 — présentation :** `https://www.insee.fr/fr/metadonnees/source/operation/s2216/presentation`

⚠ L'ancienne URL `3568638` retourne HTTP 404 (page supprimée en 2025).
L'URL de téléchargement direct BPE 2024 est instable côté INSEE.

**Alternative data.gouv.fr :** `https://www.data.gouv.fr/fr/datasets/base-permanente-des-equipements/`
→ Fichier CSV disponible (~150 Mo)
→ Placer dans `data/bpe_ensemble.csv`

Sans ce fichier : le script utilise automatiquement OSM Overpass en fallback.

⚠ Coordonnées en **Lambert 93 (EPSG:2154)** — colonnes `LAMBERT_X`, `LAMBERT_Y`
→ Convertir avec `pyproj` avant calcul de distance WGS84.

Types BPE pertinents pour SDIS :
| Code | Libellé |
|------|---------|
| `A107` | Hôpital |
| `A109` | Urgences |
| `A206` | EHPAD |
| `C101` | École maternelle |
| `C201` | École primaire |
| `D5` | Pompiers / SDIS |

## OSM Overpass — ERP (fallback sans BPE)

Amenity tags utiles : `hospital`, `clinic`, `school`, `kindergarten`, `nursing_home`, `fire_station`
