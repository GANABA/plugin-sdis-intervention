"""Chatbot CLI SDIS — interface de conversation avec streaming et mémoire par session.
Pattern: InMemorySaver + thread_id + stream_mode (cours Guyeux, chapitres 05 et 06).

Usage:
    python chatbot.py
    python chatbot.py --thread mon-intervention-42
"""
import argparse
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

from graph import build_graph

BANNER = """
╔══════════════════════════════════════════════════════╗
║        CELLULE DE CRISE SDIS — Assistant IA          ║
║  Posez vos questions en langage naturel.             ║
║  Tapez 'quitter' ou Ctrl+C pour terminer.            ║
╚══════════════════════════════════════════════════════╝"""

INDICATEURS = {
    "orchestrateur":  "[Dispatch en cours...]",
    "agent_eau":       "[Agent Hydraulique en cours...]",
    "agent_batiment":  "[Agent Batiment en cours...]",
    "agent_population": "[Agent Population en cours...]",
    "agent_meteo":     "[Agent Meteo en cours...]",
    "agent_bilan":     "[Agent Bilan — synthese...]",
}


def run_chatbot(thread_id: str):
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": thread_id}}

    print(BANNER)
    print(f"\n  Session : {thread_id}\n")

    while True:
        try:
            question = input("Pompier > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession terminee.")
            break

        if not question:
            continue
        if question.lower() in ("quitter", "exit", "quit"):
            print("Session terminee.")
            break

        print()
        noeud_actif = None
        rapport_final = None

        for etat in graph.stream(
            {"messages": [HumanMessage(content=question)]},
            config=config,
            stream_mode="updates",
        ):
            for noeud, mise_a_jour in etat.items():
                # Afficher l'indicateur de nœud au changement
                if noeud != noeud_actif:
                    noeud_actif = noeud
                    print(f"  {INDICATEURS.get(noeud, f'[{noeud}...]')}", flush=True)

                # Réponse d'un agent spécialisé (pas bilan)
                if noeud.startswith("agent_") and noeud != "agent_bilan":
                    champ = f"reponse_{noeud.replace('agent_', '')}"
                    reponse = mise_a_jour.get(champ, "")
                    if reponse:
                        print(f"\n{reponse}\n", flush=True)

                # Rapport final du bilan
                if "rapport_final" in mise_a_jour and mise_a_jour["rapport_final"]:
                    rapport_final = mise_a_jour["rapport_final"]

        if rapport_final:
            print(f"\n{'=' * 60}")
            print("FICHE DE SITUATION — COS")
            print(f"{'=' * 60}")
            print(rapport_final)
            print(f"{'=' * 60}\n")
        elif not noeud_actif:
            print("  [Aucune reponse generee]\n")

        print()


def main():
    parser = argparse.ArgumentParser(description="Chatbot SDIS multi-agents")
    parser.add_argument(
        "--thread", default=None,
        help="Identifiant de session (defaut: UUID aleatoire)"
    )
    args = parser.parse_args()
    thread_id = args.thread or f"sdis-{uuid.uuid4().hex[:8]}"
    run_chatbot(thread_id)


if __name__ == "__main__":
    main()
