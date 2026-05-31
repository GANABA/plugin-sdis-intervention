# Troubleshooting — sdis-eau

## OSM Overpass — HTTP 406 depuis un browser

**Cause :** L'API Overpass rejette certains User-Agents navigateur.
**Solution :** Le script utilise `requests.post(..., data={'data': query})` en Python — fonctionne normalement. Si persistant, utiliser le miroir : `https://overpass.kumi.systems/api/interpreter`

## Aucune borne trouvée dans le rayon

**Cause probable :** Zone non couverte dans OSM, ou rayon trop petit.
**Solution :**
1. Augmenter le rayon : `--rayon 1000`
2. Croiser avec le SIG du SDIS local (source autoritaire)
3. Vérifier sur openstreetmap.org si les bornes sont cartographiées

## IGN WFS — résultats vides avec CQL_FILTER

**Cause :** Le filtre `DWITHIN` ne fonctionne pas sur ce serveur.
**Solution :** Utiliser `BBOX` avec l'ordre `lat_min,lon_min,lat_max,lon_max,CRS`. Le script utilise déjà BBOX.

## Hub'Eau — HTTP 403

Hub'Eau a restreint l'accès à ses APIs hydrometrie.
**Alternative :** IGN WFS `BDTOPO_V3:cours_d_eau` (déjà utilisé en remplacement).
