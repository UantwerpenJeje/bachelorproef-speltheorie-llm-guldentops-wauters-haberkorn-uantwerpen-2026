"""
dictator_game.py
================
Payoff-functie voor het Dictator Game (eenmalig spel).

De dictator heeft 100€ en beslist hoeveel hij deelt met een passieve ontvanger.
De ontvanger heeft geen enkele inbreng: hij accepteert altijd.

    Dictator deelt X€  →  dictator houdt (100 - X)€, ontvanger krijgt X€

Nash-evenwicht:    X = 0  (rationeel maximaliseren = alles houden)
Empirisch gemiddelde bij mensen: X ≈ 28€  (altruïsme en fairness-normen)
"""

NAME = "dictator_game"


def get_payoff(amount_shared: int) -> tuple:
    """
    Berekent de payoffs voor de dictator en de passieve ontvanger.

    Parameters
    ----------
    amount_shared : int
        Het bedrag (in euro) dat de dictator deelt met de ontvanger (0–100).

    Returns
    -------
    tuple
        (dictator_payoff, ontvanger_payoff)
    """
    amount_shared = max(0, min(100, int(amount_shared)))
    return (100 - amount_shared, amount_shared)
