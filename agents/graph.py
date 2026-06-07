"""Graphe LangGraph SDIS — orchestrateur + agents spécialisés + bilan.
Pattern: StateGraph + add_conditional_edges + boucle (cours Guyeux, chapitre 06)."""
import sys
from pathlib import Path
from typing import Literal

from langgraph.graph import END, START, StateGraph

sys.path.insert(0, str(Path(__file__).parent))
from nodes.agent_batiment import agent_batiment_node
from nodes.agent_bilan import agent_bilan_node
from nodes.agent_eau import agent_eau_node
from nodes.agent_meteo import agent_meteo_node
from nodes.agent_population import agent_population_node
from nodes.orchestrateur import orchestrateur_node
from state import SDISState

# ---------------------------------------------------------------------------
# Routeur — lit la tête de la file intents_restants et dispatche vers le bon agent
# Bonne pratique cours : routeur = fonction pure rapide, pas de LLM
# ---------------------------------------------------------------------------

def router(
    state: SDISState,
) -> Literal["agent_eau", "agent_batiment", "agent_population", "agent_meteo", "agent_bilan", "__end__"]:
    restants = state.get("intents_restants", [])
    if not restants:
        return "__end__"
    prochain = restants[0]
    mapping = {
        "eau": "agent_eau",
        "batiment": "agent_batiment",
        "population": "agent_population",
        "meteo": "agent_meteo",
        "bilan": "agent_bilan",
    }
    return mapping.get(prochain, "__end__")


# ---------------------------------------------------------------------------
# Construction du graphe
# ---------------------------------------------------------------------------

def build_graph(checkpointer=None):
    g = StateGraph(SDISState)

    # Nœuds
    g.add_node("orchestrateur", orchestrateur_node)
    g.add_node("agent_eau", agent_eau_node)
    g.add_node("agent_batiment", agent_batiment_node)
    g.add_node("agent_population", agent_population_node)
    g.add_node("agent_meteo", agent_meteo_node)
    g.add_node("agent_bilan", agent_bilan_node)

    # Entrée → orchestrateur
    g.add_edge(START, "orchestrateur")

    # Après orchestrateur → routeur décide quel agent appeler
    g.add_conditional_edges("orchestrateur", router)

    # Après chaque agent → retour au routeur (boucle du cours, page 86)
    for agent in ["agent_eau", "agent_batiment", "agent_population", "agent_meteo"]:
        g.add_conditional_edges(agent, router)

    # Après bilan → fin
    g.add_edge("agent_bilan", END)

    return g.compile(checkpointer=checkpointer)
