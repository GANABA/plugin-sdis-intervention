"""Agent spécialisé météo et risques — create_agent avec les outils sdis-meteo.
Pattern: create_agent + system_prompt"""
import sys
from pathlib import Path

from langchain.agents import create_agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import get_llm
from state import SDISState
from tools.meteo import alertes_crues_vigicrues, conditions_meteo_et_risque

_SYSTEM = (
    "Tu es l'expert météo et risques d'une cellule de crise SDIS. "
    "Évalue les conditions météo actuelles et leur impact sur l'intervention : "
    "direction et force du vent (propagation des flammes), humidité (risque incendie), "
    "vigilances crues (risque inondation). "
    "Donne les recommandations tactiques : positionnement des engins par rapport au vent, "
    "niveau d'alerte incendie, risques d'inondation à surveiller."
)


def agent_meteo_node(state: SDISState) -> dict:
    agent = create_agent(
        model=get_llm(temperature=0),
        tools=[conditions_meteo_et_risque, alertes_crues_vigicrues],
        system_prompt=_SYSTEM,
    )

    question = (
        f"Évalue les conditions météo et les risques pour l'intervention au : {state['adresse']}. "
        "Donne le risque incendie (FWI), la direction du vent pour anticiper la propagation, "
        "et vérifie les vigilances crues Vigicrues pour la zone."
    )

    resultat = agent.invoke({"messages": [{"role": "user", "content": question}]})
    reponse = resultat["messages"][-1].content

    restants = [i for i in state.get("intents_restants", []) if i != "meteo"]
    return {"reponse_meteo": reponse, "intents_restants": restants}
