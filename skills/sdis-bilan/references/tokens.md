# Empreinte tokens — sdis-bilan

> Estimation : 1 token ≈ 3,5 caractères (texte français).
> Mesure exacte : `/context` dans Claude Code avant/après chargement du skill.

## États de chargement

| État | Tokens estimés | Chargé quand |
|------|----------------|--------------|
| **Idle** (name + description) | ~128 tokens | Toujours — dès que le plugin est installé |
| Actif (SKILL.md complet) | ~428 tokens | Quand la description matche la requête |

## Avantage Markdown-only

sdis-bilan est un skill Markdown pur (pas de main.py). Il instrumente Claude pour
appeler les 4 autres skills et formatter le résultat — zéro code à charger.
C'est le skill le plus économique à l'activation (~428 tokens vs 2 000-4 000 pour les autres).

## Comparaison MCP équivalent

| Approche | Tokens permanents |
|----------|-------------------|
| sdis-bilan idle | ~128 tokens |
| MCP équivalent | ~1 000 tokens |
| **Gain** | **x7,8** |

## Bilan plugin complet (5 skills)

| Métrique | Valeur |
|----------|--------|
| Total idle 5 skills | ~701 tokens |
| Équivalent 5 MCPs | ~7 500 tokens |
| Ratio obtenu | ~9% (objectif prof : ≤ 33%) |
