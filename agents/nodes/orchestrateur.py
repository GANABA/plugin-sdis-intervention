"""Nœud orchestrateur — classifie l'intention et extrait les paramètres du sinistre.
Pattern: sortie structurée avec Pydantic (cours Guyeux, chapitre 02)."""
import sys
from pathlib import Path
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm import get_llm
from state import SDISState

_DOMAINES = Literal["eau", "batiment", "population", "meteo", "bilan"]


class IntentionSinistre(BaseModel):
    """Paramètres extraits du message d'un sapeur-pompier."""
    adresse: str = Field(
        description=(
            "Adresse complète du sinistre. "
            "Si le message ne contient pas d'adresse, reprendre l'adresse_connue fournie telle quelle. "
            "Ne jamais inventer une adresse."
        )
    )
    rayon_m: int = Field(
        default=500,
        description="Rayon d'analyse en mètres autour du sinistre (défaut 500m, max 2000m)",
        ge=100, le=2000,
    )
    intents: list[_DOMAINES] = Field(
        description=(
            "Liste des domaines à analyser selon la question. "
            "eau = bornes incendie / hydraulique. "
            "batiment = structure / accès. "
            "population = habitants / ERP / vulnérables. "
            "meteo = vent / risque incendie / crues. "
            "bilan = rapport complet (déclenche tous les autres)."
        )
    )


_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Tu es le dispatcher de la cellule de crise SDIS. "
     "Analyse le message d'un sapeur-pompier et extrais l'adresse, le rayon d'analyse "
     "et les domaines à traiter. Si 'bilan' est demandé, liste aussi tous les autres domaines. "
     "Si le rayon n'est pas précisé, utilise 500m par défaut. "
     "IMPORTANT : si le message ne contient pas d'adresse, utilise obligatoirement l'adresse_connue."),
    ("human",
     "Adresse connue (session en cours) : {adresse_connue}\n\n"
     "Message : {message}"),
])


def orchestrateur_node(state: SDISState) -> dict:
    llm = get_llm(temperature=0)
    structured_llm = llm.with_structured_output(IntentionSinistre)

    dernier = state["messages"][-1]
    contenu = dernier.content if hasattr(dernier, "content") else str(dernier)

    # Adresse déjà connue dans la session (tour précédent)
    adresse_connue = state.get("adresse") or "non précisée"

    intention = structured_llm.invoke(
        _PROMPT.invoke({"message": contenu, "adresse_connue": adresse_connue})
    )

    # Si le LLM a renvoyé une adresse vide ou générique, conserver l'adresse connue
    adresse_finale = intention.adresse.strip()
    if not adresse_finale or adresse_finale.lower() in ("non précisée", "inconnue", ""):
        adresse_finale = adresse_connue

    # "bilan" active tous les domaines
    if "bilan" in intention.intents:
        intents = ["eau", "batiment", "population", "meteo", "bilan"]
    else:
        intents = list(intention.intents)

    return {
        "adresse": adresse_finale,
        "rayon_m": intention.rayon_m,
        "intents_restants": intents,
    }
