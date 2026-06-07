"""Outils LangChain wrappant sdis-batiment/main.py via subprocess."""
import json
import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

_SCRIPT = str(Path(__file__).parent.parent.parent / "skills" / "sdis-batiment" / "main.py")


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        err = result.stderr.strip() or "Erreur sdis-batiment"
        return json.dumps({"error": err})
    return result.stdout.strip()


@tool
def qualifier_batiment(adresse: str) -> str:
    """Qualifie le bâtiment à l'adresse du sinistre : type, hauteur, nombre d'étages,
    matériaux, état, bâtiments adjacents et voies d'accès pour les véhicules de secours."""
    return _run([sys.executable, _SCRIPT, "qualifier", "--address", adresse])
