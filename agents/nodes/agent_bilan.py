"""Agent bilan — synthétise les réponses de tous les agents spécialisés.
Pattern: LLM avec prompt structuré"""
import sys
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import get_llm
from state import SDISState

_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Tu es le coordinateur de la cellule de crise SDIS. "
     "Tu reçois les analyses de plusieurs experts (hydraulique, bâtiment, population, météo) "
     "et tu rédiges la fiche de situation opérationnelle pour le commandant des opérations de secours (COS). "
     "Structure le rapport avec les sections : SITUATION / RISQUES PRIORITAIRES / RESSOURCES / RECOMMANDATIONS. "
     "Sois factuel, concis, en langage SDIS. Mets en évidence les points critiques."),
    ("human",
     "Adresse du sinistre : {adresse}\n\n"
     "=== ANALYSE HYDRAULIQUE ===\n{eau}\n\n"
     "=== ANALYSE BÂTIMENT ===\n{batiment}\n\n"
     "=== ANALYSE POPULATION & ERP ===\n{population}\n\n"
     "=== ANALYSE MÉTÉO & RISQUES ===\n{meteo}\n\n"
     "Rédige la fiche de situation consolidée pour le COS."),
])


def agent_bilan_node(state: SDISState) -> dict:
    llm = get_llm(temperature=0)
    chain = _PROMPT | llm

    rapport = chain.invoke({
        "adresse": state.get("adresse", "inconnue"),
        "eau": state.get("reponse_eau") or "Non analysé.",
        "batiment": state.get("reponse_batiment") or "Non analysé.",
        "population": state.get("reponse_population") or "Non analysé.",
        "meteo": state.get("reponse_meteo") or "Non analysé.",
    })

    restants = [i for i in state.get("intents_restants", []) if i != "bilan"]
    return {"rapport_final": rapport.content, "intents_restants": restants}
