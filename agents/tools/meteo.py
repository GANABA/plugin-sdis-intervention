"""Outils LangChain wrappant sdis-meteo/main.py via subprocess."""
import json
import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

_SCRIPT = str(Path(__file__).parent.parent.parent / "skills" / "sdis-meteo" / "main.py")


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        err = result.stderr.strip() or "Erreur sdis-meteo"
        return json.dumps({"error": err})
    return result.stdout.strip()


@tool
def conditions_meteo_et_risque(adresse: str) -> str:
    """Récupère les conditions météo actuelles pour l'adresse du sinistre :
    température, humidité, vent (vitesse + direction), précipitations.
    Calcule l'indice de risque incendie (FWI / indice Angström modifié)."""
    return _run([sys.executable, _SCRIPT, "conditions", "--address", adresse])


@tool
def alertes_crues_vigicrues(adresse: str) -> str:
    """Consulte les vigilances crues Vigicrues pour la zone d'intervention.
    Retourne le niveau d'alerte (vert/jaune/orange/rouge) et les cours d'eau concernés."""
    return _run([sys.executable, _SCRIPT, "vigicrues", "--address", adresse])
