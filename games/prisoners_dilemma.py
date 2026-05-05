"""
prisoners_dilemma.py
====================
Payoff-functie voor het Prisoner's Dilemma.

Conform figuur 2.4 van de bachelorproef:
    | LLM | Opponent | LLM payoff | Opponent payoff |
    |-----|----------|------------|-----------------|
    |  C  |    C     |     9      |        9        |
    |  C  |    D     |     0      |       10        |
    |  D  |    C     |    10      |        0        |
    |  D  |    D     |     6      |        6        |
"""

NAME = "prisoners_dilemma"

PAYOFF_MATRIX = {
    ("C", "C"): (9, 9),
    ("C", "D"): (0, 10),
    ("D", "C"): (10, 0),
    ("D", "D"): (6, 6),
}


def get_payoff(llm_action: str, opponent_action: str) -> tuple:
    """Geeft (llm_payoff, opponent_payoff) terug voor een actiepaar."""
    return PAYOFF_MATRIX[(llm_action, opponent_action)]
