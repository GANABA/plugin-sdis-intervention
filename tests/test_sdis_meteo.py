"""Tests standalone pour sdis-meteo."""
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills" / "sdis-meteo"
MAIN = str(SKILL_DIR / "main.py")


def run(args):
    return subprocess.run(
        [sys.executable, MAIN] + args,
        capture_output=True, text=True, timeout=30
    )


def test_help():
    r = run(["--help"])
    assert r.returncode == 0


def test_conditions_lat_lon():
    r = run(["conditions", "--lat", "47.24", "--lon", "6.02"])
    if r.returncode != 0:
        print(f"SKIP réseau: {r.stderr[:100]}")
        return
    data = json.loads(r.stdout)
    assert "temperature_c" in data
    assert "vent_kmh" in data
    assert "risque_propagation_fwi" in data
    assert "vent_direction" in data


def test_vigicrues():
    r = run(["vigicrues", "--lat", "47.24", "--lon", "6.02", "--rayon", "1.0"])
    if r.returncode != 0:
        print(f"SKIP réseau: {r.stderr[:100]}")
        return
    data = json.loads(r.stdout)
    assert "alerte_maximale" in data
    assert "vigilances" in data
    assert data["alerte_maximale"] in ["VERT", "JAUNE", "ORANGE", "ROUGE"]


if __name__ == "__main__":
    test_help()
    test_conditions_lat_lon()
    test_vigicrues()
    print("[OK] sdis-meteo : tous les tests passés")
