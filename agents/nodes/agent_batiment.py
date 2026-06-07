"""Agent spécialisé bâtiment — create_agent avec les outils sdis-batiment.
Pattern: create_agent + system_prompt (cours Guyeux, chapitre 04)."""
import sys
from pathlib import Path

from langchain.agents import create_agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import get_llm
from state import SDISState
from tools.batiment import qualifier_batiment

_SYSTEM = (
    "Tu es l'expert bâtiment d'une cellule de crise SDIS. "
    "Qualifie le bâtiment sinistré : type de construction, hauteur, matériaux, risques de propagation, "
    "voies d'accès pour les engins de secours. "
    "Identifie les bâtiments adjacents qui pourraient être exposés. "
    "Utilise le vocabulaire opérationnel des sapeurs-pompiers."
)


def agent_batiment_node(state: SDISState) -> dict:
    agent = create_agent(
        model=get_llm(temperature=0),
        tools=[qualifier_batiment],
        system_prompt=_SYSTEM,
    )

    question = (
        f"Qualifie le bâtiment sinistré à l'adresse : {state['adresse']}. "
        "Donne les caractéristiques du bâtiment, les accès disponibles pour les engins, "
        "et évalue le risque de propagation aux bâtiments voisins."
    )

    resultat = agent.invoke({"messages": [{"role": "user", "content": question}]})
    reponse = resultat["messages"][-1].content

    restants = [i for i in state.get("intents_restants", []) if i != "batiment"]
    return {"reponse_batiment": reponse, "intents_restants": restants}
