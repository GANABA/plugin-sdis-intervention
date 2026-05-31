# API — sdis-batiment

## BAN — Géocodage

**Endpoint :** `GET https://api-adresse.data.gouv.fr/search/`
**Auth :** aucune
**Params clés :** `q` (adresse), `limit` (nb résultats), `citycode` (filtre commune INSEE)

Champs retournés utiles : `label`, `score`, `housenumber`, `street`, `citycode`, `postcode`, `lat`, `lon`

## IGN Géoplateforme WFS — Bâtiments BD Topo

**Endpoint :** `GET https://data.geopf.fr/wfs`
**Auth :** aucune
**Layer :** `BDTOPO_V3:batiment`
**Format BBOX :** `lat_min,lon_min,lat_max,lon_max,urn:ogc:def:crs:EPSG::4326`

Attributs disponibles :
| Attribut | Description |
|----------|-------------|
| `nature` | Type (Bâtiment résidentiel, commercial, industriel...) |
| `usage_1` | Usage principal |
| `usage_2` | Usage secondaire |
| `hauteur` | Hauteur en mètres |
| `nombre_d_etages` | Nombre de niveaux |
| `nombre_de_logements` | Nb logements (résidentiel) |
| `materiaux_des_murs` | (béton, maçonnerie, métal...) |
| `date_de_construction` | Période de construction |
| `etat_de_l_objet` | En service, en construction... |

## OSM Overpass — Voirie

**Endpoint :** `POST https://overpass-api.de/api/interpreter`
**Format body :** `data=<query>` (form-urlencoded)

Types highway utiles pour pompiers :
| Valeur | Description |
|--------|-------------|
| `primary` | Route principale |
| `secondary` | Route secondaire |
| `residential` | Voie résidentielle |
| `service` | Voie de service |
| `track` | Chemin rural |

Tags largeur : `width` (en mètres), `maxwidth`, `maxweight` (en tonnes)
