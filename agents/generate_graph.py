#!/usr/bin/env python3
"""Génère la visualisation du graphe LangGraph SDIS.

Usage:
    python generate_graph.py            # affiche le Mermaid + sauvegarde graph.png
    python generate_graph.py --mermaid  # affiche seulement la chaine Mermaid
"""
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

from graph import build_graph

HERE = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mermaid", action="store_true",
                        help="Affiche uniquement la chaine Mermaid (pas de PNG)")
    parser.add_argument("--output", default=str(HERE / "graph.png"),
                        help="Chemin du fichier PNG (defaut: graph.png)")
    args = parser.parse_args()

    app = build_graph()

    # Chaine Mermaid depuis le graphe compile
    mermaid_str = app.get_graph(xray=True).draw_mermaid()
    print("=== Mermaid ===")
    print(mermaid_str)
    print("===============")

    if args.mermaid:
        return

    # PNG via l'API Mermaid.ink (necessite internet)
    try:
        png_bytes = app.get_graph(xray=True).draw_mermaid_png()
        out = Path(args.output)
        out.write_bytes(png_bytes)
        print(f"\nGraphe sauvegarde : {out}")
    except Exception as e:
        print(f"\n[PNG non genere] {e}")
        print("Installez 'pip install pyppeteer' pour un rendu local,")
        print("ou copiez la chaine Mermaid ci-dessus dans https://mermaid.live")


if __name__ == "__main__":
    main()
