# Troubleshooting — sdis-meteo

## FWI retourne null ou absent

OpenMeteo peut ne pas avoir le FWI pour certaines zones (données de modélisation).
Le champ `risque_propagation_fwi` affichera `"inconnu"` dans ce cas.
Alternative : calculer manuellement depuis vent + humidité + température.

## Vigicrues — aucun tronçon trouvé

**Cause :** La zone n'a pas de cours d'eau sous surveillance Vigicrues, ou le rayon est trop petit.
**Solution :** Augmenter `--rayon` (en degrés, 0.5 ≈ 55km).
Vigicrues ne couvre que les cours d'eau à risque significatif — les petits ruisseaux ne sont pas couverts.

## Vigicrues — URL api.vigicrues.gouv.fr (DNS NXDOMAIN)

Ce sous-domaine n'existe pas. Utiliser uniquement :
`https://www.vigicrues.gouv.fr/services/1/InfoVigiCru.geojson/`

## OpenMeteo — timeout

OpenMeteo est un service gratuit sans SLA. En cas de timeout, réessayer.
Le timeout par défaut est 15s.
