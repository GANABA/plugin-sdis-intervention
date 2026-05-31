---
name: sdis-population
description: |
  Trigger when user asks "combien de personnes", "population dans la zone",
  "personnes âgées", "seniors isolés", "personnes vulnérables", "ménages exposés",
  "densité de population", "qui vit là", "habitants", "personnes à évacuer",
  "hôpital proche", "école dans le périmètre", "ERP", "établissements recevant
  du public", "maison de retraite", "EHPAD", "crèche".
  Mots-clés : population, habitants, vulnérables, seniors, IRIS, INSEE, RP,
  BPE, ERP, école, hôpital, EHPAD, crèche, évacuation, densité, ménages.
allowed-tools: Bash(python3 *)
---

# Skill `sdis-population`

Évalue les enjeux humains dans un périmètre : population totale, personnes vulnérables et équipements sensibles (ERP).

## Population dans un périmètre

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py zone --address "Devecey" --rayon 1000
python3 ${CLAUDE_SKILL_DIR}/main.py zone --lat 47.34 --lon 5.98 --rayon 500
```

## Personnes vulnérables

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py vulnerables --commune 25056
```

## Équipements sensibles (ERP) dans un rayon

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py erp --address "Devecey" --rayon 500
python3 ${CLAUDE_SKILL_DIR}/main.py erp --lat 47.34 --lon 5.98 --rayon 1000 --type A
```

Types ERP : `A` santé, `C` enseignement, `F` sports, `tous` (défaut)

La sortie est du JSON. Reformuler en indiquant les ERP prioritaires (crèches, EHPAD) en premier.
Données démographiques : fichiers INSEE RP locaux (`data/`). Voir `references/api.md` pour le téléchargement.
