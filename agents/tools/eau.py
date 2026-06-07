"""Outils LangChain wrappant sdis-eau/main.py via subprocess."""
import json
import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

_SCRIPT = str(Path(__file__).parent.parent.parent / "skills" / "sdis-eau" / "main.py")


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        err = result.stderr.strip() or "Erreur sdis-eau"
        return json.dumps({"error": err})
    return result.stdout.strip()


@tool
def localiser_eau(adresse: str, rayon_m: int = 500) -> str:
    """Localise les bornes incendie, poteaux, bouches et cours d'eau dans un rayon
    autour de l'adresse du sinistre. Retourne la liste triée par distance."""
    return _run([sys.executable, _SCRIPT, "localise",
                 "--address", adresse, "--rayon", str(rayon_m)])


@tool
def calculer_autonomie_hydraulique(
    type_sinistre: str,
    surface: float,
    citernes: int = 2,
    vol_citerne: int = 5000,
    distance_eau_m: int = 0,
) -> str:
    """Calcule l'autonomie hydraulique des citernes et le besoin en navettes.
    type_sinistre: habitation | commercial | industriel | entrepot | foret.
    surface: en m² (ou hectares pour forêt).
    distance_eau_m: distance au point d'eau le plus proche en mètres (0 = non applicable)."""
    cmd = [sys.executable, _SCRIPT, "autonomie",
           "--type", type_sinistre, "--surface", str(surface),
           "--citernes", str(citernes), "--vol-citerne", str(vol_citerne)]
    if distance_eau_m > 0:
        cmd += ["--distance-eau", str(distance_eau_m)]
    return _run(cmd)
