---
name: sdis-meteo
description: |
  Trigger when user asks "météo", "conditions météo", "vent", "direction du vent",
  "risque de propagation", "humidité", "indice FWI", "feu de forêt risque",
  "vigilance crue", "inondation", "niveau de la rivière", "vigicrues",
  "temperature", "précipitations", "rafales", "fire weather index".
  Mots-clés : météo, vent, humidité, FWI, propagation, incendie, forêt,
  vigicrues, crue, inondation, température, rafales, OpenMeteo.
allowed-tools: Bash(python3 *)
---

# Skill `sdis-meteo`

Fournit les conditions météo en temps réel (vent, humidité, FWI) et les vigilances crues Vigicrues pour une localisation donnée.

## Conditions météo et risque propagation

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py conditions --lat 47.24 --lon 6.02
python3 ${CLAUDE_SKILL_DIR}/main.py conditions --address "Chailluz, Besançon"
```

## Vigilances crues

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py vigicrues --lat 47.24 --lon 6.02 --rayon 0.5
```

La sortie est du JSON. Mettre en avant le risque de propagation (FWI) et les vigilances actives.
Interprétation FWI : <5 faible | 5-12 modéré | 12-20 élevé | 20-30 très élevé | >30 extrême.
Pour les variables météo disponibles et les niveaux Vigicrues, voir `references/api.md`.
