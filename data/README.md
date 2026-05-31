# Données locales — à télécharger manuellement

Ces fichiers améliorent la précision de `sdis-population` mais ne sont pas bloquants.
Sans eux, le plugin fonctionne en mode dégradé (OSM + estimation communale).

---

## rp2022_iris.csv — INSEE Recensement de la Population 2022

**URL de téléchargement :** https://www.insee.fr/fr/statistiques/8647014
**Format :** CSV (22 Mo) ou Excel (45 Mo)
**Couverture :** ~15 500 IRIS, France hors Mayotte
**Publié :** octobre 2025

**Action :**
1. Aller sur https://www.insee.fr/fr/statistiques/8647014
2. Télécharger le fichier CSV "France hors Mayotte"
3. Placer dans `data/rp2022_iris.csv`

**Colonnes utilisées par le script :**

| Colonne | Description |
|---------|-------------|
| `COM` | Code commune INSEE (5 chiffres) |
| `IRIS` | Code IRIS (9 chiffres) |
| `LIBIRIS` | Libellé de l'IRIS |
| `P22_POP` | Population totale 2022 |
| `P22_POP65P` | Population 65 ans et plus |
| `P22_POP80P` | Population 80 ans et plus |
| `P22_PMEN` | Population des ménages |

> **Note :** Les colonnes utilisent le préfixe `P22_` (RP 2022). Ne pas utiliser le RP 2020 (`P20_`) ni un hypothétique RP 2021 (`P21_`) — les données IRIS 2021 n'ont pas été publiées à ce niveau.

---

## bpe_ensemble.csv — Base Permanente des Équipements 2024

**Présentation officielle :** https://www.insee.fr/fr/metadonnees/source/operation/s2216/presentation
**Couverture :** 2,85 millions d'équipements, 229 types, France entière
**Coordonnées :** Lambert 93 (EPSG:2154) — conversion pyproj nécessaire

### Comment obtenir le fichier

L'URL de téléchargement INSEE est instable (page réorganisée en 2025).
Options dans l'ordre de fiabilité :

1. **Via data.gouv.fr :** https://www.data.gouv.fr/fr/datasets/base-permanente-des-equipements/
   - Fichier CSV disponible (~150 Mo)
   - Millésime potentiellement 2020-2024 selon la mise à jour

2. **Via la page INSEE BPE 2024 :** Rechercher "BPE 2024 téléchargement" sur https://www.insee.fr/fr/statistiques
   - Chercher un lien vers un fichier `bpe24_ensemble_csv.zip`

3. **Sans BPE :** le script bascule automatiquement sur OSM Overpass pour les ERP
   — suffisant pour le projet

**Action si fichier trouvé :**
- Extraire et placer dans `data/bpe_ensemble.csv`
- Modifier `sdis-population/main.py` ligne `BPE_FILE` si le nom diffère

**Colonnes utilisées :**

| Colonne | Description |
|---------|-------------|
| `TYPEQU` | Code type d'équipement (A=santé, C=enseignement...) |
| `LAMBERT_X` | Coordonnée X Lambert 93 |
| `LAMBERT_Y` | Coordonnée Y Lambert 93 |
| `LIBCOM` | Libellé commune |
| `SDOM` | Sous-domaine / nom équipement |

---

## Sans ces fichiers — mode dégradé

| Sous-commande | Avec fichiers locaux | Sans fichiers |
|--------------|----------------------|---------------|
| `zone` | Population IRIS précise | Estimation proportionnelle communale |
| `vulnerables` | Par IRIS, tri par vulnérabilité | ❌ Non disponible |
| `erp` | BPE exhaustif (229 types) | OSM Overpass (moins exhaustif) |
