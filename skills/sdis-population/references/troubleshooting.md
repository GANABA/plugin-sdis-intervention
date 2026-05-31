# Troubleshooting — sdis-population

## "fichier data/rp2021_iris.csv absent"

Les fichiers INSEE ne sont pas inclus dans le dépôt (trop volumineux).
Télécharger depuis : `https://www.insee.fr/fr/statistiques/7704076`
Placer dans `data/rp2021_iris.csv`.

## "fichier data/bpe23_ensemble.csv absent"

Télécharger depuis : `https://www.insee.fr/fr/statistiques/3568638`
Extraire et placer dans `data/bpe23_ensemble.csv`.
Le script bascule automatiquement sur OSM Overpass si le fichier est absent.

## Erreur pyproj lors de la conversion Lambert 93

```
ImportError: No module named 'pyproj'
```
Installer : `pip install pyproj`
Sans pyproj, la conversion Lambert→WGS84 échoue et les ERP BPE ne peuvent pas être géolocalisés.

## Population très sous-estimée

L'estimation par proportion de surface est une approximation grossière.
Pour les zones denses (centre-ville), la vraie densité peut être 5-10x supérieure à la moyenne communale.
Utiliser les fichiers RP IRIS pour une estimation plus précise à l'échelle infra-communale.
