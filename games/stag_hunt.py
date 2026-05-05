"""
stag_hunt.py
============
Payoff-functie voor het Stag Hunt.

Conform figuur 2.7 van de bachelorproef:
    | LLM | Opponent | LLM payoff | Opponent payoff |
    |-----|----------|------------|-----------------|
    |  C  |    C     |    10      |       10        |   (beide hert)
    |  C  |    D     |     0      |        2        |
    |  D  |    C     |     2      |        0        |
    |  D  |    D     |     1      |        1        |   (beide haas)

C = Hert (cooperate / risky-but-rewarding)
D = Haas (defect / safe)

Opmerking: in de bachelorproef-tekst (sectie 3.3.4) staan de stratgieën
'Always Stag' en 'Always Hare' vermeld i.p.v. AC/AD/TfT/Random.
In ons systeem werken we met universele C/D labels:
    Always Stag  = AC (always Cooperate)
    Always Hare  = AD (always Defect)
TfT en Random houden we ook hier aan voor consistentie met de andere spellen.
"""

NAME = "stag_hunt"

PAYOFF_MATRIX = {
    ("C", "C"): (10, 10),
    ("C", "D"): (0, 2),
    ("D", "C"): (2, 0),
    ("D", "D"): (1, 1),
}


def get_payoff(llm_action: str, opponent_action: str) -> tuple:
    """Geeft (llm_payoff, opponent_payoff) terug voor een actiepaar."""
    return PAYOFF_MATRIX[(llm_action, opponent_action)]
