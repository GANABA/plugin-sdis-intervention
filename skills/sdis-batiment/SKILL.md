---
name: sdis-batiment
description: |
  Trigger when user asks "type de bâtiment", "qualifier le bâtiment", "hauteur de
  l'immeuble", "combien d'étages", "accès pour les secours", "largeur de la rue",
  "bâtiments adjacents", "risque de propagation", "matériaux de construction",
  "immeuble résidentiel ou industriel", "accès pompiers", "building type", "floors".
  Mots-clés : bâtiment, immeuble, hauteur, étages, accès, voirie, propagation,
  matériaux, résidentiel, industriel, commercial, IGN, BD Topo, OSM, cadastre.
allowed-tools: Bash(python3 *)
---

# Skill `sdis-batiment`

Qualifie un bâtiment depuis une adresse : type, hauteur, nombre d'étages, matériaux, bâtiments adjacents et accès véhicules.

## Qualifier un bâtiment

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py qualifier --address "14 rue de la Préfecture, Besançon"
```

La sortie est du JSON. Reformuler en langage naturel : indiquer le type, la hauteur, les accès disponibles et les bâtiments à risque de propagation.

Pour les codes nature IGN et les types OSM highway, voir `references/api.md`.
