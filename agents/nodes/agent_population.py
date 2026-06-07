"""Agent spécialisé population — create_agent avec les outils sdis-population.
Pattern: create_agent + system_prompt (cours Guyeux, chapitre 04)."""
import sys
from pathlib import Path

from langchain.agents import create_agent

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import get_llm
from state import SDISState
from tools.population import analyser_vulnerables, analyser_zone_population, lister_erp

_SYSTEM = (
    "Tu es l'expert démographie et ERP d'une cellule de crise SDIS. "
    "Évalue la population exposée dans le périmètre du sinistre : nombre d'habitants, "
    "personnes vulnérables (âgées, à mobilité réduite), établissements recevant du public "
    "(hôpitaux, EHPAD, écoles) qui pourraient nécessiter une évacuation prioritaire. "
    "Classe les risques par ordre de priorité opérationnelle."
)


def agent_population_node(state: SDISState) -> dict:
    agent = create_agent(
        model=get_llm(temperature=0),
        tools=[analyser_zone_population, lister_erp, analyser_vulnerables],
        system_prompt=_SYSTEM,
    )

    question = (
        f"Analyse la population exposée au sinistre au : {state['adresse']}, "
        f"dans un rayon de {state['rayon_m']}m. "
        "Identifie les ERP prioritaires (hôpitaux, EHPAD, écoles) "
        "et les zones à forte concentration de personnes vulnérables."
    )

    resultat = agent.invoke({"messages": [{"role": "user", "content": question}]})
    reponse = resultat["messages"][-1].content

    restants = [i for i in state.get("intents_restants", []) if i != "population"]
    return {"reponse_population": reponse, "intents_restants": restants}
