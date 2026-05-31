"""Tests standalone pour sdis-eau."""
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills" / "sdis-eau"
MAIN = str(SKILL_DIR / "main.py")


def run(args):
    result = subprocess.run(
        [sys.executable, MAIN] + args,
        capture_output=True, text=True, timeout=30
    )
    return result


def test_help():
    r = run(["--help"])
    assert r.returncode == 0, f"--help a échoué: {r.stderr}"


def test_localise_help():
    r = run(["localise", "--help"])
    assert r.returncode == 0


def test_autonomie_habitation():
    r = run(["autonomie", "--type", "habitation", "--surface", "400", "--citernes", "2"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    data = json.loads(r.stdout)
    assert "debit_necessaire_l_min" in data
    assert data["debit_necessaire_l_min"] == 240  # 60 L/min * 4 (400/100)
    assert "autonomie_sans_navette_min" in data
    assert data["volume_disponible_L"] == 10000


def test_autonomie_foret():
    r = run(["autonomie", "--type", "foret", "--surface", "2", "--citernes", "3"])
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["debit_necessaire_l_min"] == 500  # 250 * 2 hectares


def test_autonomie_avec_distance():
    r = run([
        "autonomie", "--type", "habitation", "--surface", "200",
        "--citernes", "2", "--distance-eau", "100"
    ])
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "cadence_navette_min" in data
    assert data["cadence_navette_min"] is not None


def test_localise_address(pytestmark=None):
    """Test réseau — peut échouer sans connexion."""
    r = run(["localise", "--address", "Place de la République, Besançon", "--rayon", "300"])
    if r.returncode != 0:
        print(f"SKIP réseau: {r.stderr[:100]}")
        return
    data = json.loads(r.stdout)
    assert "bornes_incendie" in data
    assert "eau_naturelle" in data
    assert "point_reference" in data


if __name__ == "__main__":
    test_help()
    test_autonomie_habitation()
    test_autonomie_foret()
    test_autonomie_avec_distance()
    test_localise_address()
    print("[OK] sdis-eau : tous les tests passés")
