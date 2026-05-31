# API — sdis-eau

## OSM Overpass — bornes incendie

**Endpoint :** `POST https://overpass-api.de/api/interpreter`
**Auth :** aucune
**Format body :** `data=<query_url_encoded>` (form-urlencoded)

Tags OSM utiles :
| Tag | Valeurs |
|-----|---------|
| `emergency` | `fire_hydrant`, `suction_point` |
| `fire_hydrant:type` | `pillar` (poteau), `underground` (bouche), `wall` |
| `fire_hydrant:diameter` | en mm (80, 100, 150) |
| `fire_hydrant:pressure` | en bar |

Limitation : couverture incomplète selon communes. Certains SDIS ont leur propre SIG.

## IGN Géoplateforme WFS — Hydrographie

**Endpoint :** `GET https://data.geopf.fr/wfs`
**Auth :** aucune
**Format BBOX :** `lat_min,lon_min,lat_max,lon_max,urn:ogc:def:crs:EPSG::4326`

Layers disponibles :
| Layer | Contenu |
|-------|---------|
| `BDTOPO_V3:cours_d_eau` | Rivières, ruisseaux |
| `BDTOPO_V3:plan_d_eau` | Lacs, étangs, retenues |
| `BDTOPO_V3:reservoir` | Réservoirs et citernes |

Attributs `cours_d_eau` : `toponyme`, `largeur_en_l`, `navigabilite`
Attributs `plan_d_eau` : `toponyme`, `nature` (lac, étang, retenue), `superficie`

## Débits SDIS de référence

| Type sinistre | Débit (L/min pour 100m²) |
|---------------|--------------------------|
| Habitation | 60 |
| Commercial | 120 |
| Industriel / Entrepôt | 180 |
| Forêt | 250 L/min/hectare |

Source : Guide national de référence SDIS — Alimentation en eau.
