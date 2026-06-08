#!/usr/bin/env python3
"""Génère un graph.png simplifié ne montrant que les transitions réellement possibles.

Le routeur générique expose toutes les arêtes possibles (chaque nœud vers tous
les autres). Ce script construit un graphe de visualisation où chaque agent
ne déclare que les transitions vers l'avant dans la file d'intents :
  orchestrateur → eau → batiment → population → meteo → bilan → __end__
avec sortie possible vers __end__ à chaque étape.
"""
import sys
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

HERE = Path(__file__).parent


class _VizState(TypedDict):
    """État minimal pour le graphe de visualisation."""
    x: str


def _make_router(targets: list[str]):
    """Retourne une fonction de routage vers les cibles données."""
    target_type = Literal[tuple(targets)]  # type: ignore[valid-type]

    def _router(state: _VizState) -> target_type:  # type: ignore[valid-type]
        return targets[0]

    _router.__annotations__["return"] = Literal[tuple(targets)]  # type: ignore[assignment]
    return _router


def build_viz_graph():
    g = StateGraph(_VizState)

    for name in ["orchestrateur", "agent_eau", "agent_batiment",
                 "agent_population", "agent_meteo", "agent_bilan"]:
        g.add_node(name, lambda s: s)

    g.add_edge(START, "orchestrateur")

    # Orchestrateur peut envoyer vers n'importe quel premier agent ou terminer
    g.add_conditional_edges(
        "orchestrateur",
        _make_router(["agent_eau", "agent_batiment", "agent_population",
                      "agent_meteo", "agent_bilan", "__end__"]),
    )
    # Chaque agent ne peut aller que vers les agents suivants dans la file
    g.add_conditional_edges(
        "agent_eau",
        _make_router(["agent_batiment", "agent_population", "agent_meteo",
                      "agent_bilan", "__end__"]),
    )
    g.add_conditional_edges(
        "agent_batiment",
        _make_router(["agent_population", "agent_meteo", "agent_bilan", "__end__"]),
    )
    g.add_conditional_edges(
        "agent_population",
        _make_router(["agent_meteo", "agent_bilan", "__end__"]),
    )
    g.add_conditional_edges(
        "agent_meteo",
        _make_router(["agent_bilan", "__end__"]),
    )
    # Bilan termine toujours
    g.add_edge("agent_bilan", END)

    return g.compile()


def main():
    app = build_viz_graph()

    mermaid_str = app.get_graph().draw_mermaid()
    print("=== Mermaid simplifie ===")
    print(mermaid_str)
    print("=========================")

    try:
        png_bytes = app.get_graph().draw_mermaid_png()
        out = HERE / "graph.png"
        out.write_bytes(png_bytes)
        print(f"\nGraphe sauvegarde : {out}")
    except Exception as e:
        print(f"\n[PNG non genere] {e}")


if __name__ == "__main__":
    main()
