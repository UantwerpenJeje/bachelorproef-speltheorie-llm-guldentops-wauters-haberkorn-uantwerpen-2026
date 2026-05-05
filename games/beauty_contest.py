"""
beauty_contest.py
=================
Hulpfuncties voor het Beauty Contest (ook: Keynesian Beauty Contest).

Spelregels:
    - N spelers kiezen elk een geheel getal tussen 0 en 100.
    - De winnaar is de speler wiens getal het dichtst bij 2/3 × gemiddelde ligt.
    - Het spel wordt meerdere rondes gespeeld, met feedback na elke ronde.

In ons experiment speelt 1 LLM tegen (N-1) gesimuleerde spelers die telkens
een willekeurig getal kiezen (uniform tussen 0 en 100).

Nash-evenwicht:    0  (perfecte rationaliteit → iteratief redeneren naar 0)
Empirisch menselijk gedrag:
    - Ronde 1: gemiddelde ≈ 35  (één niveau van redeneren: 2/3 × 50 ≈ 33)
    - Trage convergentie naar 0 over meerdere rondes
"""

NAME = "beauty_contest"

TARGET_FRACTION = 2 / 3  # het winnende getal is 2/3 van het gemiddelde


def compute_target(numbers: list) -> float:
    """
    Berekent het doelgetal voor een ronde: 2/3 van het gemiddelde.

    Parameters
    ----------
    numbers : list of int
        De gekozen getallen van alle spelers (incl. LLM en simulaties).

    Returns
    -------
    float
        Het doelgetal.
    """
    return TARGET_FRACTION * (sum(numbers) / len(numbers))


def get_winner_index(numbers: list) -> int:
    """
    Geeft de index van de winnaar: de speler wiens getal het dichtst bij
    het doelgetal zit. Bij gelijkspel wint de speler met de laagste index.

    Parameters
    ----------
    numbers : list of int
        De gekozen getallen van alle spelers.

    Returns
    -------
    int
        Index van de winnaar in de lijst.
    """
    target = compute_target(numbers)
    return min(range(len(numbers)), key=lambda i: abs(numbers[i] - target))


def get_payoff(player_idx: int, numbers: list) -> int:
    """
    Geeft 1 als de speler wint, anders 0.

    Parameters
    ----------
    player_idx : int
        De index van de speler in `numbers` (het LLM staat op index 0).
    numbers : list of int
        De gekozen getallen van alle spelers.

    Returns
    -------
    int
        1 als de speler wint, 0 als hij verliest.
    """
    winner_idx = get_winner_index(numbers)
    return 1 if player_idx == winner_idx else 0
