"""
ultimatum_game.py
=================
Payoff-functie voor het Ultimatum Game (eenmalig spel, twee fasen).

Fase 1 — Proposer: stelt een verdeling voor van 100€ (bv. 30€ voor de responder).
Fase 2 — Responder: aanvaardt (ACCEPT) of verwerpt (REJECT) het voorstel.
    - ACCEPT: proposer krijgt (100 − aanbod)€, responder krijgt aanbod€
    - REJECT: beide spelers krijgen 0€

Nash-evenwicht:
    Proposer biedt 1€, responder accepteert (elk positief bedrag is beter dan 0).
Empirisch menselijk gedrag:
    - Proposers bieden gemiddeld 40–50%
    - Aanbiedingen onder ~20% worden vaak verworpen (fairness-norm)
"""

NAME = "ultimatum_game"


def get_payoff(offer: int, response: str) -> tuple:
    """
    Berekent de payoffs op basis van het aanbod en de beslissing van de responder.

    Parameters
    ----------
    offer : int
        Het bedrag (in euro) dat de proposer aanbiedt aan de responder (0–100).
    response : str
        De beslissing van de responder: "ACCEPT" of "REJECT".

    Returns
    -------
    tuple
        (proposer_payoff, responder_payoff)
    """
    offer = max(0, min(100, int(offer)))
    if response == "ACCEPT":
        return (100 - offer, offer)
    return (0, 0)  # REJECT: beide spelers krijgen niets
