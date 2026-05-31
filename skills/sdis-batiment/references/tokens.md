# Empreinte tokens — sdis-batiment

> Estimation : 1 token ≈ 3,5 caractères (texte français).
> Mesure exacte : `/context` dans Claude Code avant/après chargement du skill.

## États de chargement

| État | Tokens estimés | Chargé quand |
|------|----------------|--------------|
| **Idle** (name + description) | ~142 tokens | Toujours — dès que le plugin est installé |
| Actif (SKILL.md complet) | ~306 tokens | Quand la description matche la requête |
| Actif + main.py | ~2 163 tokens | Quand Claude exécute une commande |
| Actif + main.py + api.md | ~2 598 tokens | Si Claude consulte la doc API |

## Comparaison MCP équivalent

| Approche | Tokens permanents |
|----------|-------------------|
| sdis-batiment idle | ~142 tokens |
| MCP équivalent (2 outils + docstrings) | ~1 500 tokens |
| **Gain** | **x10,6** |

## Bilan plugin complet (5 skills)

| Métrique | Valeur |
|----------|--------|
| Total idle 5 skills | ~701 tokens |
| Équivalent 5 MCPs | ~7 500 tokens |
| Ratio obtenu | ~9% (objectif prof : ≤ 33%) |
