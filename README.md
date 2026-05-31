# Plugin SDIS Intervention — Claude Code

Plugin Claude Code d'aide à la décision opérationnelle pour les sapeurs-pompiers. Fournit une lecture rapide d'un territoire en situation d'urgence : points d'eau, bâtiment sinistré, population exposée, météo et vigilances.

## Skills disponibles

| Skill | Déclenchement | Capacité |
|-------|---------------|----------|
| `sdis-eau` | "bornes incendie", "eau disponible", "autonomie hydraulique" | Points d'eau + calcul autonomie citerne |
| `sdis-batiment` | "qualifier le bâtiment", "hauteur", "accès pompiers" | Type, hauteur, accès, bâtiments adjacents |
| `sdis-population` | "combien de personnes", "vulnérables", "ERP dans le périmètre" | Population, seniors, écoles, hôpitaux |
| `sdis-meteo` | "météo", "vent", "risque propagation", "vigicrues" | Météo temps réel, FWI, vigilances crues |
| `sdis-bilan` | "fiche de situation", "synthèse intervention" | Rapport consolidé depuis les 4 autres skills |

## Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-groupe>/<votre-repo>
cd plugin-sdis-intervention

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Copier les skills dans Claude Code
cp -r skills/* ~/.claude/skills/
```

### Données INSEE (optionnel mais recommandé)

Pour des données démographiques précises, télécharger les fichiers INSEE dans `data/` :

```bash
# Voir data/README.md pour les URLs et instructions détaillées
```

Sans ces fichiers, `sdis-population` fonctionne en mode dégradé (OSM + estimation globale).

## Usage

Les skills se déclenchent automatiquement sur les questions naturelles en session Claude.

```
> "Combien de personnes dans un rayon de 500m autour du 14 rue de la Préfecture, Besançon ?"
→ sdis-population se déclenche

> "Quelles sont les bornes incendie disponibles près du sinistre ?"
→ sdis-eau se déclenche

> "Génère la fiche de situation complète pour cette intervention"
→ sdis-bilan se déclenche et agrège les autres
```

Déclenchement explicite :
```
/sdis-eau
/sdis-batiment
/sdis-population
/sdis-meteo
/sdis-bilan
```

## Tests

```bash
cd tests/
python test_sdis_eau.py
python test_sdis_batiment.py
python test_sdis_meteo.py
python test_sdis_population.py
```

## Sources de données

| Donnée | Source | Auth |
|--------|--------|------|
| Bornes incendie | OSM Overpass | Aucune |
| Cours d'eau, bâtiments | IGN BD Topo WFS | Aucune |
| Géocodage adresses | BAN | Aucune |
| Communes | Geo API gouvernement | Aucune |
| Démographie | INSEE RP (fichiers locaux) | Aucune |
| Équipements BPE | INSEE BPE (fichiers locaux) | Aucune |
| Météo + FWI | OpenMeteo | Aucune |
| Vigilances crues | Vigicrues | Aucune |

Toutes les sources sont **publiques et gratuites**. Aucune clé API requise.

## Structure

```
plugin-sdis-intervention/
├── README.md
├── requirements.txt
├── data/                        # Fichiers INSEE à télécharger (voir data/README.md)
├── skills/
│   ├── sdis-eau/
│   ├── sdis-batiment/
│   ├── sdis-population/
│   ├── sdis-meteo/
│   └── sdis-bilan/
└── tests/
```
