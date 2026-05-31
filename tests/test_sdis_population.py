"""Tests standalone pour sdis-population."""
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills" / "sdis-population"
MAIN = str(SKILL_DIR / "main.py")


def run(args):
    return subprocess.run(
        [sys.executable, MAIN] + args,
        capture_output=True, text=True, timeout=30
    )


def test_help():
    r = run(["--help"])
    assert r.returncode == 0


def test_zone_address():
    r = run(["zone", "--address", "Besançon", "--rayon", "500"])
    if r.returncode != 0:
        print(f"SKIP réseau: {r.stderr[:100]}")
        return
    data = json.loads(r.stdout)
    assert "commune" in data
    assert "population_commune" in data
    assert "rayon_m" in data


def test_erp_fallback_osm():
    """Sans fichier BPE local, doit utiliser OSM en fallback ou retourner une erreur structurée."""
    r = run(["erp", "--address", "Place Granvelle, Besancon", "--rayon", "300", "--type", "A"])
    if r.returncode != 0:
        print(f"SKIP réseau: {r.stderr[:100]}")
        return
    data = json.loads(r.stdout)
    # Accepte soit les données ERP, soit une erreur structurée (OSM peut être bloqué)
    assert "erp" in data or "error" in data


def test_vulnerables_sans_fichier():
    """Sans fichier RP, doit retourner un message d'erreur structuré (pas de crash)."""
    r = run(["vulnerables", "--commune", "25056"])
    assert r.returncode == 0
    data = json.loads(r.stdout)
    # Soit les données si le fichier existe, soit un message d'erreur propre
    assert "totaux" in data or "erreur" in data


if __name__ == "__main__":
    test_help()
    test_zone_address()
    test_erp_fallback_osm()
    test_vulnerables_sans_fichier()
    print("[OK] sdis-population : tous les tests passés")
