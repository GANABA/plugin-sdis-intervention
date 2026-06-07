"""Outils LangChain wrappant sdis-population/main.py via subprocess."""
import json
import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

_SCRIPT = str(Path(__file__).parent.parent.parent / "skills" / "sdis-population" / "main.py")


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        err = result.stderr.strip() or "Erreur sdis-population"
        return json.dumps({"error": err})
    return result.stdout.strip()


@tool
def analyser_zone_population(adresse: str, rayon_m: int = 500) -> str:
    """Estime la population totale dans un rayon autour du sinistre.
    Données INSEE RP 2022 par IRIS. Retourne population, ménages, proportion de seniors."""
    return _run([sys.executable, _SCRIPT, "zone",
                 "--address", adresse, "--rayon", str(rayon_m)])


@tool
def analyser_vulnerables(code_commune: str) -> str:
    """Analyse la vulnérabilité démographique par IRIS dans une commune.
    code_commune: code INSEE à 5 chiffres (ex: 90010 pour Belfort).
    Retourne les IRIS avec les plus fortes concentrations de personnes âgées (+65, +80 ans)."""
    return _run([sys.executable, _SCRIPT, "vulnerables", "--commune", code_commune])


@tool
def lister_erp(adresse: str, rayon_m: int = 500, type_erp: str = "tous") -> str:
    """Liste les établissements recevant du public (ERP) dans un rayon.
    type_erp: tous | D (santé: hôpitaux, EHPAD) | C (enseignement: écoles) | F (sports).
    Les ERP prioritaires (hôpitaux, EHPAD, écoles maternelles) sont signalés en premier."""
    return _run([sys.executable, _SCRIPT, "erp",
                 "--address", adresse, "--rayon", str(rayon_m), "--type", type_erp])
