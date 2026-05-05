"""
strategies.py
=============
Implementatie van de vier vaste tegenstanderstrategieën voor de iteratieve
spellen (Prisoner's Dilemma, Chicken Game, Stag Hunt).

Elke strategie krijgt de speelgeschiedenis en moet één actie teruggeven:
  - "C" voor de coöperatieve actie (Zwijgen / Stoppen / Hert)
  - "D" voor de niet-coöperatieve actie (Verraden / Doorrijden / Haas)

We gebruiken bewust C/D als universele labels. De vertaling naar
spel-specifieke termen (Hert/Haas etc.) gebeurt in elk game-bestand.
"""

import random


def always_cooperate(history: list) -> str:
    """
    Always Cooperate (AC).
    Speelt altijd de coöperatieve actie, ongeacht wat er eerder gebeurd is.
    """
    return "C"


def always_defect(history: list) -> str:
    """
    Always Defect (AD).
    Speelt altijd de niet-coöperatieve actie.
    """
    return "D"


def tit_for_tat(history: list) -> str:
    """
    Tit-for-Tat (TfT).
    In de eerste ronde: coöpereren.
    Daarna: kopieer de vorige zet van de tegenstander (= het LLM).

    De geschiedenis is een lijst van dicts:
      [{"llm_action": "C", "opponent_action": "D", "round": 1}, ...]
    """
    if len(history) == 0:
        return "C"  # eerste ronde: vertrouw de tegenstander
    return history[-1]["llm_action"]  # kopieer de laatste zet van het LLM


def random_strategy(history: list) -> str:
    """
    Random.
    Kiest met kans 50/50 tussen C en D.
    """
    return random.choice(["C", "D"])


# Mapping van strategienaam (uit config.py) naar functie.
# Hierdoor kunnen we in run_experiment.py simpelweg
# STRATEGY_FUNCS[name](history) doen.
STRATEGY_FUNCS = {
    "AC":     always_cooperate,
    "AD":     always_defect,
    "TfT":    tit_for_tat,
    "Random": random_strategy,
}
