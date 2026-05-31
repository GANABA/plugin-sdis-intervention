# Empreinte tokens — sdis-eau

> Estimation : 1 token ≈ 3,5 caractères (texte français).
> Mesure exacte : `/context` dans Claude Code avant/après chargement du skill.

## États de chargement

| État | Tokens estimés | Chargé quand |
|------|----------------|--------------|
| **Idle** (name + description) | ~153 tokens | Toujours — dès que le plugin est installé |
| Actif (SKILL.md complet) | ~415 tokens | Quand la description matche la requête |
| Actif + main.py | ~2 568 tokens | Quand Claude exécute une commande |
| Actif + main.py + api.md | ~2 966 tokens | Si Claude consulte la doc API |

## Comparaison MCP équivalent

| Approche | Tokens permanents |
|----------|-------------------|
| sdis-eau idle | ~153 tokens |
| MCP équivalent (2 outils + docstrings) | ~1 500 tokens |
| **Gain** | **x9,8** |

## Bilan plugin complet (5 skills)

| Métrique | Valeur |
|----------|--------|
| Total idle 5 skills | ~701 tokens |
| Équivalent 5 MCPs | ~7 500 tokens |
| Ratio obtenu | ~9% (objectif prof : ≤ 33%) |
