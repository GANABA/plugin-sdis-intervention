# Exemples — sdis-batiment

## Exemple 1 : Immeuble résidentiel centre-ville

```bash
python3 main.py qualifier --address "14 rue de la Préfecture, Besançon"
```

Sortie attendue :
```json
{
  "adresse_geocodee": "14 rue de la préfecture 25000 Besançon",
  "coordonnees": { "lat": 47.234893, "lon": 6.024664 },
  "batiment_principal": {
    "nature": "Bâtiment résidentiel",
    "usage_principal": "Résidentiel",
    "hauteur_m": 15.2,
    "nombre_etages": 4,
    "nombre_logements": 18,
    "materiaux_murs": "Maçonnerie",
    "annee_construction": "Avant 1946"
  },
  "batiments_adjacents": [
    { "nature": "Bâtiment résidentiel", "hauteur_m": 12.0, "distance_m": 3 },
    { "nature": "Bâtiment commercial", "hauteur_m": 8.0, "distance_m": 18 }
  ],
  "acces_vehicules": [
    { "nom": "rue de la Préfecture", "type": "residential", "largeur_m": "6", "sens_unique": false }
  ]
}
```

**Interprétation :** R+4, maçonnerie ancienne. Adjacent à 3m côté est = risque de propagation. Accès uniquement par la rue de la Préfecture (6m, bi-directionnel).

## Exemple 2 : Entrepôt zone industrielle

```bash
python3 main.py qualifier --address "3 rue de l'Industrie, Devecey"
```

Sortie attendue :
```json
{
  "batiment_principal": {
    "nature": "Bâtiment industriel",
    "usage_principal": "Industriel",
    "hauteur_m": 9.0,
    "nombre_etages": 1,
    "materiaux_murs": "Métal"
  },
  "acces_vehicules": [
    { "nom": "rue de l'Industrie", "type": "service", "largeur_m": "8", "sens_unique": false },
    { "nom": "voie sans nom", "type": "track", "largeur_m": null, "sens_unique": false }
  ]
}
```
