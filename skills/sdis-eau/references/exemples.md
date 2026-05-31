# Exemples — sdis-eau

## Exemple 1 : Localiser les points d'eau

```bash
python3 main.py localise --address "14 rue de la Préfecture, Besançon" --rayon 500
```

Sortie attendue :
```json
{
  "point_reference": { "lat": 47.234893, "lon": 6.024664, "rayon_m": 500 },
  "bornes_incendie": [
    { "type": "pillar", "diametre_mm": "100", "distance_m": 45, "lat": 47.235, "lon": 6.025 },
    { "type": "underground", "diametre_mm": "80", "distance_m": 112, "lat": 47.236, "lon": 6.023 }
  ],
  "eau_naturelle": [
    { "type": "cours_eau", "nom": "Doubs", "exploitable": true }
  ],
  "avertissement": "Couverture OSM variable. Croiser avec SIG SDIS local."
}
```

## Exemple 2 : Calculer l'autonomie

```bash
python3 main.py autonomie --type habitation --surface 320 --citernes 2 --distance-eau 45
```

Sortie attendue :
```json
{
  "type_sinistre": "habitation",
  "surface": 320,
  "debit_necessaire_l_min": 192,
  "volume_disponible_L": 10000,
  "autonomie_sans_navette_min": 52.1,
  "cadence_navette_min": 3,
  "citernes_pour_continuite": 1,
  "demander_renfort_a_min": 36,
  "note": "Débits SDIS standard. Adapter selon nature réelle du sinistre."
}
```

**Interprétation :** 52 min d'autonomie, navette de 3 min depuis le poteau à 45m — 1 citerne suffit pour la continuité. Demander renfort à T+36min.
