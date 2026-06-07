"""État partagé qui circule à travers tous les nœuds du graphe SDIS."""
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class SDISState(TypedDict):
    # Historique complet de la conversation (reducer add_messages évite les doublons)
    messages: Annotated[list, add_messages]
    # Paramètres de l'intervention extraits par l'orchestrateur
    adresse: str
    rayon_m: int
    # File d'attente des agents à exécuter (l'orchestrateur la remplit, chaque agent se retire)
    intents_restants: list[str]
    # Réponses en langage naturel de chaque agent spécialisé
    reponse_eau: str
    reponse_batiment: str
    reponse_population: str
    reponse_meteo: str
    # Rapport final consolidé par agent_bilan
    rapport_final: str
