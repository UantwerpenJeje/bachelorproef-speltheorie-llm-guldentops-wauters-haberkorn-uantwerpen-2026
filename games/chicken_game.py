"""
chicken_game.py
===============
Payoff-functie voor het Chicken Game.

Conform figuur 2.5 van de bachelorproef:
    | LLM | Opponent | LLM payoff | Opponent payoff |
    |-----|----------|------------|-----------------|
    |  C  |    C     |     0      |        0        |   (beide stoppen)
    |  C  |    D     |    -1      |        1        |
    |  D  |    C     |     1      |       -1        |
    |  D  |    D     |   -10      |      -10        |   (botsing)

C = Stoppen (cooperate / safe)
D = Doorrijden (defect / aggressive)
"""

NAME = "chicken_game"

PAYOFF_MATRIX = {
    ("C", "C"): (0, 0),
    ("C", "D"): (-1, 1),
    ("D", "C"): (1, -1),
    ("D", "D"): (-10, -10),
}


def get_payoff(llm_action: str, opponent_action: str) -> tuple:
    """Geeft (llm_payoff, opponent_payoff) terug voor een actiepaar."""
    return PAYOFF_MATRIX[(llm_action, opponent_action)]
