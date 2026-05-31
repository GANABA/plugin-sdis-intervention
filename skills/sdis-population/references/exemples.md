# Exemples — sdis-population

## Exemple 1 : Population dans un périmètre de 500m

```bash
python3 main.py zone --address "Devecey" --rayon 1000
```

Sortie attendue :
```json
{
  "commune": "Devecey",
  "code_commune": "25193",
  "rayon_m": 1000,
  "population_commune": 1780,
  "population_estimee_rayon": 331,
  "note": "Estimation proportionnelle à la surface."
}
```

## Exemple 2 : ERP dans 300m — accident chimique

```bash
python3 main.py erp --address "3 rue de l'Industrie, Devecey" --rayon 500 --type tous
```

Sortie attendue :
```json
{
  "nb_erp_trouves": 3,
  "erp": [
    { "type_code": "C101", "nom": "École maternelle de Devecey", "distance_m": 290, "prioritaire": true },
    { "type_code": "A206", "nom": "EHPAD Les Tilleuls", "distance_m": 380, "prioritaire": true },
    { "type_code": "C201", "nom": "École primaire", "distance_m": 420, "prioritaire": true }
  ],
  "source": "INSEE BPE local"
}
```

**Interprétation :** Crèche et école en direction du nuage → évacuation immédiate. EHPAD à mobilité réduite → évacuation longue, déclencher maintenant.

## Exemple 3 : Vulnérables par commune

```bash
python3 main.py vulnerables --commune 25056
```

Sortie attendue :
```json
{
  "commune_code": "25056",
  "totaux": { "pop_totale": 117000, "pop_65plus": 21060, "pop_80plus": 8424 },
  "iris_les_plus_vulnerables": [
    { "lib_iris": "Battant", "pop_totale": 2840, "pct_65plus": 22.4 },
    { "lib_iris": "Planoise Nord", "pop_totale": 3100, "pct_65plus": 18.1 }
  ]
}
```
