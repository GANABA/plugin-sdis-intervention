---
name: sdis-bilan
description: |
  Trigger when user asks "fiche de situation", "bilan opérationnel", "synthèse
  d'intervention", "résumé complet", "situation globale", "rapport d'intervention",
  "vue d'ensemble", "consolide les informations", "fiche intervention", "récapitulatif",
  "donne-moi tout sur cette intervention".
  Mots-clés : bilan, synthèse, fiche, situation, rapport, intervention, consolidation,
  résumé, tableau de bord, récapitulatif, pompiers, SDIS.
allowed-tools: Bash(python3 *)
---

# Skill `sdis-bilan`

Génère une fiche de situation opérationnelle consolidée en agrégeant les données des 4 autres skills du plugin.

## Procédure

Pour produire un bilan complet sur une adresse, exécuter dans l'ordre :

```bash
# 1. Bâtiment
python3 ~/.claude/skills/sdis-batiment/main.py qualifier --address "ADRESSE"

# 2. Points d'eau
python3 ~/.claude/skills/sdis-eau/main.py localise --address "ADRESSE" --rayon 500

# 3. Population exposée
python3 ~/.claude/skills/sdis-population/main.py zone --address "ADRESSE" --rayon 500
python3 ~/.claude/skills/sdis-population/main.py erp --address "ADRESSE" --rayon 300

# 4. Météo
python3 ~/.claude/skills/sdis-meteo/main.py conditions --address "ADRESSE"
```

Puis formater la fiche selon le template dans `references/template.md`.

## Format de sortie

Après avoir collecté les résultats JSON, produire la fiche en Markdown structuré selon le template normalisé. Mettre en gras les alertes et prioriser les actions immédiates en tête.
