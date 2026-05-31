---
name: sdis-eau
description: |
  Trigger when user asks "points d'eau", "bornes incendie", "hydrantes proches",
  "eau disponible", "alimentation en eau", "ressources hydrauliques", "cours d'eau",
  "étang à proximité", "autonomie hydraulique", "débit nécessaire", "combien de
  temps d'eau", "citerne", "réapprovisionnement", "poteau incendie", "bouche incendie",
  "water supply", "fire hydrant".
  Mots-clés : eau, borne, hydrant, poteau, bouche, citerne, autonomie, débit,
  rivière, cours d'eau, étang, retenue, OSM, IGN, hydraulique, extinction, L/min.
allowed-tools: Bash(python3 *)
---

# Skill `sdis-eau`

Localise les points d'eau mobilisables (bornes, cours d'eau, plans d'eau) et calcule l'autonomie hydraulique des citernes engagées.

## Localiser les points d'eau

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py localise --address "14 rue de la Préfecture, Besançon" --rayon 500
python3 ${CLAUDE_SKILL_DIR}/main.py localise --lat 47.24 --lon 6.02 --rayon 300
```

## Calculer l'autonomie hydraulique

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py autonomie --type habitation --surface 400 --citernes 2
python3 ${CLAUDE_SKILL_DIR}/main.py autonomie --type foret --surface 2 --citernes 3 --distance-eau 340
```

Types disponibles : `habitation`, `commercial`, `industriel`, `entrepot`, `foret`

La sortie est du JSON. Reformuler en langage naturel avant de répondre.
Pour les débits de référence SDIS et les seuils, voir `references/api.md`.
