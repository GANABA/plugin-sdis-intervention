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
git clone https://github.com/GANABA/plugin-sdis-intervention.git
cd plugin-sdis-intervention

# 2. Installer les dépendances Python
pip install -r requirements.txt

# 3. Copier les skills dans Claude Code
cp -r skills/* ~/.claude/skills/
```

### Données INSEE — accès depuis l'install globale

`sdis-population` utilise des fichiers CSV locaux (RP 2022, BPE). Deux options :

**Option A — Copier les données dans le dossier skills (recommandé)**
```bash
mkdir -p ~/.claude/skills/data
cp data/rp2022_iris.csv data/bpe-ensemble.csv ~/.claude/skills/data/
```
Le script les trouvera automatiquement au chemin `~/.claude/skills/data/`.

**Option B — Variable d'environnement (données dans le repo)**
```bash
# Ajouter dans ~/.bashrc ou ~/.zshrc :
export SDIS_DATA_DIR="/chemin/absolu/vers/plugin-sdis-intervention/data"
```
Le script lit `$SDIS_DATA_DIR` en priorité — les données restent dans le repo.

Sans ces fichiers, `sdis-population` fonctionne en mode dégradé (OSM + estimation globale).

## Usage

Les skills se déclenchent automatiquement sur les questions naturelles en session Claude.

### Exemples de scénarios opérationnels

Voici des scénarios types que vous pouvez tester :

1.  **Incendie d'une maison individuelle** : "Un incendie est signalé au **15 Rue de Dole, 25000 Besançon**. Identifie les bornes incendie les plus proches, estime les besoins en eau, analyse les risques de propagation aux habitations voisines et fournis un résumé opérationnel de la situation."
2.  **Feu dans un immeuble collectif** : "Un feu est déclaré au **42 Avenue Fontaine-Argent, 25000 Besançon**, au quatrième étage d'un immeuble résidentiel. Détermine la hauteur du bâtiment, le nombre estimé d'occupants, les accès disponibles pour les secours et les risques de propagation verticale."
3.  **Incendie à proximité d'une école** : "Un incendie s'est déclaré au **8 Rue de Trey, 25000 Besançon**. Analyse les établissements recevant du public situés dans un rayon de 500 mètres, notamment les écoles, et évalue les risques pour les occupants."
4.  **Ressources en eau insuffisantes** : "Un incendie important est en cours au **120 Rue de Belfort, 25000 Besançon**. Vérifie si les bornes incendie à proximité sont suffisantes et identifie d'autres sources d'approvisionnement en eau telles que les rivières, bassins ou retenues d'eau."
5.  **Feu de forêt** : "Un départ de feu est signalé à proximité de la **Forêt de Chailluz, Besançon**. Analyse la topographie, les conditions météorologiques, les ressources en eau disponibles et les habitations potentiellement menacées dans les prochaines heures."
6.  **Incendie industriel** : "Un incendie est signalé dans une zone industrielle au **6 Rue Auguste Jouchoux, 25000 Besançon**. Identifie les activités présentes sur le site, les risques particuliers associés et les établissements sensibles situés à proximité."
7.  **Analyse de la population exposée** : "Un incendie majeur est en cours au **25 Rue Battant, 25000 Besançon**. Estime le nombre de personnes potentiellement impactées, identifie les populations vulnérables et les établissements sensibles dans un rayon de 1 kilomètre."
8.  **Risque de propagation urbaine** : "Un entrepôt est en feu au **3 Rue Thomas Edison, 25000 Besançon**. Identifie les bâtiments voisins susceptibles d'être touchés et évalue le risque de propagation en fonction de la distance et des caractéristiques du bâti."
9.  **Données cartographiques incomplètes** : "Un incendie est signalé au **18 Chemin des Journaux, 25000 Besançon**. Certaines données cartographiques sont manquantes. Recherche des informations complémentaires à partir d'autres sources et indique le niveau de confiance associé aux données restituées."
10. **Évaluation de l'autonomie hydraulique** : "Un incendie est en cours au **7 Rue de Vesoul, 25000 Besançon**. En tenant compte des moyens engagés et des ressources en eau disponibles, estime si les réserves actuelles permettront de maintenir les opérations pendant 45 minutes."
11. **Incident multi-sites** : "Une explosion est survenue au **14 Rue Alfred de Vigny, 25000 Besançon**, provoquant plusieurs départs de feu dans les bâtiments environnants. Identifie les zones prioritaires, les populations exposées et propose un ordre d'intervention."
12. **Centre-ville dense** : "Un incendie majeur est signalé au **1 Grande Rue, 25000 Besançon**. Analyse l'ensemble des bâtiments, ERP, ressources en eau et populations présentes dans un rayon de 500 mètres afin de produire une synthèse opérationnelle destinée au commandant des opérations de secours."
13. **Test complet du système agentique** : "Un incendie est signalé au **10 Rue Mégevand, 25000 Besançon**. Fournis une analyse complète comprenant les caractéristiques du bâtiment, les ressources hydrauliques disponibles, les ERP à proximité, la population exposée, les risques de propagation, l'impact des conditions météorologiques et les recommandations opérationnelles prioritaires."

### Déclenchement explicite
Si besoin, vous pouvez forcer l'appel d'un skill via les commandes : `/sdis-eau`, `/sdis-batiment`, `/sdis-population`, `/sdis-meteo`, `/sdis-bilan`.

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
