# Troubleshooting — sdis-batiment

## IGN WFS retourne des résultats vides

**Cause :** CQL_FILTER DWITHIN non supporté. Le script utilise BBOX.
**Vérification :** S'assurer que le BBOX est au format `lat_min,lon_min,lat_max,lon_max,CRS`.
L'ordre lat/lon (pas lon/lat) est obligatoire avec `urn:ogc:def:crs:EPSG::4326`.

## Bâtiment principal non trouvé (rayon 60m)

**Cause :** BD Topo peut ne pas avoir le bâtiment exact, surtout en zone rurale.
**Solution :** Augmenter le rayon en modifiant `bbox_from_point(lat, lon, 60)` → `100`.

## API Carto IGN retourne de mauvaises coordonnées

L'API Carto `/api/cadastre/parcelle` retourne parfois des données incorrectes.
Ne pas l'utiliser. IGN WFS BD Topo est la source fiable.

## OSM — accès voirie incomplets

OSM peut manquer des voies privées ou des impasses. En opération, croiser avec le SIG SDIS ou un GPS terrain.
