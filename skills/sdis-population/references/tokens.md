# Empreinte tokens — sdis-population

> Estimation : 1 token ≈ 3,5 caractères (texte français).
> Mesure exacte : `/context` dans Claude Code avant/après chargement du skill.

## États de chargement

| État | Tokens estimés | Chargé quand |
|------|----------------|--------------|
| **Idle** (name + description) | ~152 tokens | Toujours — dès que le plugin est installé |
| Actif (SKILL.md complet) | ~439 tokens | Quand la description matche la requête |
| Actif + main.py | ~3 999 tokens | Quand Claude exécute une commande |
| Actif + main.py + api.md | ~4 632 tokens | Si Claude consulte la doc API |

## Note sur la taille de main.py

sdis-population est le skill le plus lourd (~4k tokens actif) car il gère trois sources de données
(RP local, BPE local, OSM fallback) avec leur logique de détection automatique.
Le coût n'est payé qu'à l'activation — jamais en idle.

## Comparaison MCP équivalent

| Approche | Tokens permanents |
|----------|-------------------|
| sdis-population idle | ~152 tokens |
| MCP équivalent (3 outils + docstrings) | ~2 000 tokens |
| **Gain** | **x13,2** |

## Bilan plugin complet (5 skills)

| Métrique | Valeur |
|----------|--------|
| Total idle 5 skills | ~701 tokens |
| Équivalent 5 MCPs | ~7 500 tokens |
| Ratio obtenu | ~9% (objectif prof : ≤ 33%) |
