"""Agent spécialisé hydraulique — create_agent avec les outils sdis-eau.
Pattern: create_agent + system_prompt (cours Guyeux, chapitre 04)."""
import sys
from pathlib import Path

from langchain.agents import create_agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import get_llm
from state import SDISState
from tools.eau import calculer_autonomie_hydraulique, localiser_eau

_SYSTEM = (
    "Tu es l'expert hydraulique d'une cellule de crise SDIS. "
    "Utilise les outils disponibles pour localiser les points d'eau et calculer l'autonomie. "
    "Présente tes résultats de façon opérationnelle : liste les bornes les plus proches, "
    "indique si l'autonomie est suffisante ou si des renforts sont nécessaires. "
    "Sois concis et factuel — tu t'adresses à des sapeurs-pompiers en intervention."
)


def agent_eau_node(state: SDISState) -> dict:
    agent = create_agent(
        model=get_llm(temperature=0),
        tools=[localiser_eau, calculer_autonomie_hydraulique],
        system_prompt=_SYSTEM,
    )

    question = (
        f"Analyse les ressources hydrauliques pour l'intervention au : {state['adresse']}. "
        f"Rayon de recherche : {state['rayon_m']}m. "
        "Localise les bornes incendie disponibles."
    )

    resultat = agent.invoke({"messages": [{"role": "user", "content": question}]})
    reponse = resultat["messages"][-1].content

    # Retire "eau" de la file d'attente
    restants = [i for i in state.get("intents_restants", []) if i != "eau"]
    return {"reponse_eau": reponse, "intents_restants": restants}
