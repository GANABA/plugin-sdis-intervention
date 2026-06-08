#!/usr/bin/env python3
"""Génère graph.png avec un diagramme Mermaid propre via l'API Mermaid.ink.

Représente les transitions réelles uniquement (file d'intents, sens unique),
avec layout LR (left-to-right) pour un pipeline lisible.
"""
import base64
import sys
from pathlib import Path

import requests

HERE = Path(__file__).parent

MERMAID = """
flowchart LR
    S([__start__]) --> O[orchestrateur]

    O  --> AE[agent_eau]
    AE --> AB[agent_batiment]
    AB --> AP[agent_population]
    AP --> AM[agent_meteo]
    AM --> AG[agent_bilan]
    AG --> E([__end__])

    O  -.->|"file vide"| E
    AE -.->|"file vide"| E
    AB -.->|"file vide"| E
    AP -.->|"file vide"| E
    AM -.->|"file vide"| E

    classDef default fill:#f2f0ff,stroke:#9b8fef,line-height:1.2
    classDef first  fill-opacity:0,stroke-dasharray:5 5
    classDef last   fill:#bfb6fc,stroke:#7c6fe0
    class S first
    class E last
"""


def main():
    encoded = base64.urlsafe_b64encode(MERMAID.encode()).decode()
    url = f"https://mermaid.ink/img/{encoded}?bgColor=white"

    print("Appel Mermaid.ink...", flush=True)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    out = HERE / "graph.png"
    out.write_bytes(resp.content)
    print(f"Graphe sauvegarde : {out}")


if __name__ == "__main__":
    main()
