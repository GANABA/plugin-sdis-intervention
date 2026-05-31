# Exemples — sdis-meteo

## Exemple 1 : Conditions météo — feu de forêt

```bash
python3 main.py conditions --lat 47.30 --lon 6.08
```

Sortie attendue :
```json
{
  "temperature_c": 38.1,
  "humidite_pct": 19,
  "vent_kmh": 48,
  "vent_direction": "NE",
  "rafales_kmh": 67,
  "precipitation_mm": 0.0,
  "risque_propagation_fwi": {
    "niveau": "EXTRÊME",
    "description": "Conditions de feu extrêmes — sécurité maximale",
    "valeur": 42.3
  }
}
```

**Interprétation :** FWI 42 → conditions extrêmes. Vent NE 48km/h, rafales 67. Propagation vers SO rapide (>3km/h en végétation sèche).

## Exemple 2 : Vigilances crues — secteur Besançon

```bash
python3 main.py vigicrues --lat 47.24 --lon 6.02 --rayon 0.3
```

Sortie attendue :
```json
{
  "alerte_maximale": "ORANGE",
  "nb_troncons": 2,
  "vigilances": [
    { "cours_eau": "Doubs amont", "niveau": "ORANGE", "label": "Risque important", "valeur_numerique": 3 },
    { "cours_eau": "Ognon", "niveau": "JAUNE", "label": "Risque de débordement", "valeur_numerique": 2 }
  ]
}
```
