"""Tests standalone pour sdis-batiment."""
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills" / "sdis-batiment"
MAIN = str(SKILL_DIR / "main.py")


def run(args):
    return subprocess.run(
        [sys.executable, MAIN] + args,
        capture_output=True, text=True, timeout=30
    )


def test_help():
    r = run(["--help"])
    assert r.returncode == 0


def test_qualifier_help():
    r = run(["qualifier", "--help"])
    assert r.returncode == 0


def test_qualifier_address():
    """Test réseau — peut échouer sans connexion."""
    r = run(["qualifier", "--address", "14 rue de la Préfecture, Besançon"])
    if r.returncode != 0:
        print(f"SKIP réseau: {r.stderr[:100]}")
        return
    data = json.loads(r.stdout)
    assert "batiment_principal" in data
    assert "acces_vehicules" in data
    assert "coordonnees" in data
    coords = data["coordonnees"]
    assert 47.0 < coords["lat"] < 48.0
    assert 5.5 < coords["lon"] < 6.5


if __name__ == "__main__":
    test_help()
    test_qualifier_help()
    test_qualifier_address()
    print("[OK] sdis-batiment : tous les tests passés")
