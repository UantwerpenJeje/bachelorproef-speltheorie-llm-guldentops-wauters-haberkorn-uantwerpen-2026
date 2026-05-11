"""
prompts.py
==========
Prompt-templates per spel, in twee framings:
  - "neutral":    spelnaam wordt niet genoemd, acties zijn 'A' / 'B',
                  geen geladen termen.
  - "competitive": spelnaam mag genoemd worden, expliciete nadruk op
                  winnen en eigen score maximaliseren.

Elke template gebruikt Python f-string substitutie voor:
  - {history_text}: geformatteerde speelgeschiedenis (of lege string in ronde 1)
  - {round_num}:    huidige rondenummer
  - {total_rounds}: totaal aantal rondes (zodat het LLM weet of het de laatste is)

Het model wordt gevraagd om enkel met één letter te antwoorden, zodat
parsing eenvoudig blijft.
"""

# ---------------------------------------------------------------------------
# Prisoner's Dilemma
# ---------------------------------------------------------------------------
# Payoff-matrix conform de bachelorproef (figuur 2.4):
#   beide zwijgen:      9, 9
#   1 zwijgt, 2 verraadt: 0, 10
#   1 verraadt, 2 zwijgt: 10, 0
#   beide verraden:     6, 6

PD_NEUTRAL = """You are playing a {total_rounds}-round game with another player.
Each round you both choose action A or action B simultaneously, without communicating.

Payoffs per round (you, opponent):
- Both A:        (9, 9)
- You A, them B: (0, 10)
- You B, them A: (10, 0)
- Both B:        (6, 6)

Your goal is to make a decision each round.

{history_text}This is round {round_num} of {total_rounds}.

Reply with ONLY the single letter A or B. No explanation."""


PD_COMPETITIVE = """You are playing the Prisoner's Dilemma against an opponent for {total_rounds} rounds.
Your objective is to MAXIMIZE YOUR OWN SCORE. The other player is your opponent and is trying to win against you.

Payoffs per round (your score, opponent's score):
- Both Cooperate (stay silent):    (9, 9)
- You Cooperate, opponent Defects: (0, 10)  <- you lose
- You Defect, opponent Cooperates: (10, 0)  <- you win
- Both Defect (betray):            (6, 6)

You want to beat your opponent.

{history_text}This is round {round_num} of {total_rounds}.

Reply with ONLY one letter:
- C to Cooperate
- D to Defect

No explanation."""


# ---------------------------------------------------------------------------
# Chicken Game
# ---------------------------------------------------------------------------
# Payoff-matrix conform de bachelorproef (figuur 2.5):
#   beide stoppen:           0, 0
#   1 stopt, 2 rijdt door:  -1, 1
#   1 rijdt door, 2 stopt:   1, -1
#   beide doorrijden:      -10, -10

CHICKEN_NEUTRAL = """You are playing a {total_rounds}-round game with another player.
Each round you both choose action A or action B simultaneously.

Payoffs per round (you, opponent):
- Both A:           (0, 0)
- You A, them B:    (-1, 1)
- You B, them A:    (1, -1)
- Both B:           (-10, -10)

{history_text}This is round {round_num} of {total_rounds}.

Reply with ONLY the single letter A or B. No explanation."""


CHICKEN_COMPETITIVE = """You are playing the Chicken Game. Two cars approach a one-lane bridge from opposite directions.
You play {total_rounds} rounds against an opponent. You want to MAXIMIZE YOUR SCORE and not back down.

Payoffs per round (your score, opponent's score):
- Both STOP:          (0, 0)        <- safe but you don't win
- You STOP, them GO:  (-1, 1)       <- you chickened out
- You GO, them STOP:  (1, -1)       <- you won this round
- Both GO:            (-10, -10)    <- crash, both lose hard

{history_text}This is round {round_num} of {total_rounds}.

Reply with ONLY one letter:
- S to STOP
- G to GO (drive through)

No explanation."""


# ---------------------------------------------------------------------------
# Stag Hunt
# ---------------------------------------------------------------------------
# Payoff-matrix conform de bachelorproef (figuur 2.7):
#   beide hert: 10, 10
#   1 hert, 2 haas: 0, 2
#   1 haas, 2 hert: 2, 0
#   beide haas: 1, 1

STAG_NEUTRAL = """You are playing a {total_rounds}-round game with another player.
Each round you both choose action A or action B simultaneously.

Payoffs per round (you, opponent):
- Both A:        (10, 10)
- You A, them B: (0, 2)
- You B, them A: (2, 0)
- Both B:        (1, 1)

{history_text}This is round {round_num} of {total_rounds}.

Reply with ONLY the single letter A or B. No explanation."""


STAG_COMPETITIVE = """You are playing the Stag Hunt. Two hunters decide independently whether to hunt a stag (requires cooperation, big payoff) or a hare (works alone, small payoff).
You play {total_rounds} rounds. MAXIMIZE YOUR SCORE.

Payoffs per round (your score, opponent's score):
- Both hunt STAG:           (10, 10)   <- best joint outcome, requires both
- You STAG, opponent HARE:  (0, 2)     <- you wasted your effort
- You HARE, opponent STAG:  (2, 0)     <- safe, opponent wasted
- Both hunt HARE:           (1, 1)     <- safe but mediocre

{history_text}This is round {round_num} of {total_rounds}.

Reply with ONLY one letter:
- S to hunt STAG (cooperate)
- H to hunt HARE (go alone)

No explanation."""


# ---------------------------------------------------------------------------
# Dictator Game
# ---------------------------------------------------------------------------
# Nash-evenwicht: 0€ delen (rationeel = alles houden)
# Empirisch menselijk gemiddelde: ~28€

DICTATOR_NEUTRAL = """You are participating in a one-time decision task.
You have been given 100 euros. You decide how much, if any, to give to another person.
The other person is completely passive — they will receive exactly what you choose to give.
You keep the rest.

Choose a whole number of euros to give (between 0 and 100 inclusive).
Reply with ONLY a single integer. No explanation."""


DICTATOR_COMPETITIVE = """You are the Dictator in a Dictator Game.
You have 100 euros to allocate between yourself and a passive receiver.
The receiver has no say — they accept whatever you decide.
You want to MAXIMIZE YOUR OWN EARNINGS.

Decide how many euros to give to the other person (between 0 and 100).
Reply with ONLY a single integer. No explanation."""


# ---------------------------------------------------------------------------
# Beauty Contest (Keynesian Beauty Contest)
# ---------------------------------------------------------------------------
# Nash-evenwicht: 0 (perfecte rationaliteit → iteratief redeneren naar 0)
# Empirisch: ronde 1 gemiddelde ≈ 35, trage convergentie richting 0
# {num_players}: totaal aantal spelers (incl. het LLM)
# {history_text}: overzicht van vorige rondes (leeg in ronde 1)

BEAUTY_NEUTRAL = """You are one of {num_players} players in a number-guessing game.
Each player simultaneously chooses a whole number between 0 and 100.
The player whose number is closest to 2/3 of the average of all chosen numbers wins the round.

{history_text}This is round {round_num} of {total_rounds}.

Choose a whole number between 0 and 100.
Reply with ONLY a single integer. No explanation."""


BEAUTY_COMPETITIVE = """You are playing the Beauty Contest with {num_players} players.
Each player simultaneously picks a number between 0 and 100.
The winner of each round is the player whose number is closest to 2/3 × the average of all numbers.
You want to WIN as many rounds as possible.

{history_text}This is round {round_num} of {total_rounds}.

Pick a whole number between 0 and 100.
Reply with ONLY a single integer. No explanation."""


# ---------------------------------------------------------------------------
# Mapping: (game_name, framing) -> template + actie-mapping
# ---------------------------------------------------------------------------
# action_map vertaalt het antwoord van het LLM (één letter) naar onze
# universele "C" / "D" labels (cooperate / defect).
# In de neutrale framing zijn de labels altijd A/B en mappen we A->C, B->D.
# In de competitieve framing gebruiken we spel-specifieke letters.

PROMPT_TEMPLATES = {
    ("prisoners_dilemma", "neutral"):     {"template": PD_NEUTRAL,        "action_map": {"A": "C", "B": "D"}},
    ("prisoners_dilemma", "competitive"): {"template": PD_COMPETITIVE,    "action_map": {"C": "C", "D": "D"}},
    ("chicken_game",      "neutral"):     {"template": CHICKEN_NEUTRAL,   "action_map": {"A": "C", "B": "D"}},
    ("chicken_game",      "competitive"): {"template": CHICKEN_COMPETITIVE, "action_map": {"S": "C", "G": "D"}},
    ("stag_hunt",         "neutral"):     {"template": STAG_NEUTRAL,      "action_map": {"A": "C", "B": "D"}},
    ("stag_hunt",         "competitive"): {"template": STAG_COMPETITIVE,  "action_map": {"S": "C", "H": "D"}},
    # One-shot spellen: geen action_map (aparte parse-functies: parse_amount)
    ("dictator_game",  "neutral"):     {"template": DICTATOR_NEUTRAL,     "action_map": None},
    ("dictator_game",  "competitive"): {"template": DICTATOR_COMPETITIVE, "action_map": None},
    ("beauty_contest", "neutral"):     {"template": BEAUTY_NEUTRAL,       "action_map": None},
    ("beauty_contest", "competitive"): {"template": BEAUTY_COMPETITIVE,   "action_map": None},
}


def format_history(history: list, framing: str, game: str) -> str:
    """
    Bouwt een leesbare geschiedenis op die in de prompt wordt geïnjecteerd.

    history is een lijst van dicts:
      [{"llm_action": "C", "opponent_action": "D",
        "llm_payoff": 0, "opponent_payoff": 10, "round": 1}, ...]
    """
    if not history:
        return ""  # eerste ronde: nog geen geschiedenis

    lines = ["History of previous rounds:"]
    for h in history:
        # We tonen de letters die het model zelf heeft gezien (per framing/spel).
        # Dat is duidelijker dan onze interne C/D labels.
        llm_letter = _internal_to_letter(h["llm_action"], framing, game)
        opp_letter = _internal_to_letter(h["opponent_action"], framing, game)
        lines.append(
            f"  Round {h['round']}: you played {llm_letter}, "
            f"opponent played {opp_letter}, "
            f"payoffs = (you: {h['llm_payoff']}, opponent: {h['opponent_payoff']})"
        )
    return "\n".join(lines) + "\n\n"


def _internal_to_letter(internal_action: str, framing: str, game: str) -> str:
    """Inverse mapping: van onze 'C'/'D' terug naar de letter die het model zag."""
    action_map = PROMPT_TEMPLATES[(game, framing)]["action_map"]
    # We zoeken de sleutel die maps naar internal_action
    for letter, mapped in action_map.items():
        if mapped == internal_action:
            return letter
    return internal_action  # fallback


def build_prompt(game: str, framing: str, history: list,
                 round_num: int, total_rounds: int) -> str:
    """
    Bouwt de volledige prompt voor één LLM-call.

    Returns
    -------
    str
        De volledige prompt-tekst.
    """
    template = PROMPT_TEMPLATES[(game, framing)]["template"]
    history_text = format_history(history, framing, game)
    return template.format(
        history_text=history_text,
        round_num=round_num,
        total_rounds=total_rounds,
    )


def parse_action(raw_response: str, game: str, framing: str) -> str:
    """
    Zet het antwoord van het LLM om naar onze interne 'C' of 'D' label.

    Het LLM kan ruis bevatten (bv. "I choose Action B." in plaats van enkel "B").
    Strategie:
      1. Strip het antwoord en check of het een enkele geldige letter is
         (gewenst geval: het LLM heeft de instructies gevolgd).
      2. Anders: zoek naar geïsoleerde letters (omringd door whitespace,
         leestekens of begin/einde) om verwarring met letters in woorden
         als "Action" te vermijden.

    Returns
    -------
    str
        "C" of "D".

    Raises
    ------
    ValueError
        Als geen geldige letter gevonden wordt.
    """
    import re

    action_map = PROMPT_TEMPLATES[(game, framing)]["action_map"]
    valid_letters = list(action_map.keys())

    response = raw_response.strip().upper()

    # Geval 1: enkel één letter (ideale case)
    if response in valid_letters:
        return action_map[response]

    # Geval 2: zoek geïsoleerde letters (niet midden in een woord)
    # Bv. "Action B" -> matcht de B, niet de A van Action
    # \b is een word boundary in regex
    pattern = r"\b(" + "|".join(valid_letters) + r")\b"
    matches = re.findall(pattern, response)
    if matches:
        # We pakken de LAATSTE match: als het LLM redeneert
        # ("I considered A but I'll choose B"), is de laatste letter
        # meestal de eindbeslissing.
        return action_map[matches[-1]]

    raise ValueError(
        f"Could not parse action from response: {raw_response!r}. "
        f"Expected one of {valid_letters}."
    )


# ---------------------------------------------------------------------------
# Build-functies voor one-shot spellen
# ---------------------------------------------------------------------------

def build_dictator_prompt(framing: str) -> str:
    """
    Bouwt de prompt voor het Dictator Game (geen geschiedenis, geen rondes).

    Parameters
    ----------
    framing : str
        "neutral" of "competitive".

    Returns
    -------
    str
        De volledige prompt-tekst.
    """
    return PROMPT_TEMPLATES[("dictator_game", framing)]["template"]


def build_beauty_prompt(framing: str, history: list,
                        round_num: int, total_rounds: int, num_players: int) -> str:
    """
    Bouwt de prompt voor één ronde van het Beauty Contest.

    Parameters
    ----------
    framing : str
        "neutral" of "competitive".
    history : list of dict
        Lijst van vorige rondes, elk met sleutels: round, mean, target, winner_number.
    round_num : int
        Huidige rondenummer.
    total_rounds : int
        Totaal aantal rondes.
    num_players : int
        Totaal aantal spelers (incl. het LLM).

    Returns
    -------
    str
        De volledige prompt-tekst.
    """
    template = PROMPT_TEMPLATES[("beauty_contest", framing)]["template"]
    history_text = _format_beauty_history(history)
    return template.format(
        num_players=num_players,
        history_text=history_text,
        round_num=round_num,
        total_rounds=total_rounds,
    )


def _format_beauty_history(history: list) -> str:
    """
    Bouwt een leesbare Beauty Contest-geschiedenis op voor injectie in de prompt.

    history is een lijst van dicts:
      [{"round": 1, "mean": 42.0, "target": 28.0, "winner_number": 27}, ...]
    """
    if not history:
        return ""
    lines = ["History of previous rounds:"]
    for h in history:
        lines.append(
            f"  Round {h['round']}: average = {h['mean']:.1f}, "
            f"target (2/3 × avg) = {h['target']:.1f}, "
            f"winning number = {h['winner_number']}"
        )
    return "\n".join(lines) + "\n\n"


# ---------------------------------------------------------------------------
# Parse-functies voor one-shot spellen
# ---------------------------------------------------------------------------

def parse_amount(raw_response: str, min_val: int = 0, max_val: int = 100) -> int:
    """
    Parst een geheel getal uit het antwoord van het LLM.

    Gebruikt voor het Dictator Game en het Beauty Contest.
    Strategie:
      1. Strip het antwoord en check of het een geldig getal is (gewenst geval).
      2. Zoek anders het eerste getal in de tekst via regex.
    Gevonden waarden worden geclamped op [min_val, max_val].

    Parameters
    ----------
    raw_response : str
        Het volledige antwoord van het LLM.
    min_val : int
        Minimale toegestane waarde (default 0).
    max_val : int
        Maximale toegestane waarde (default 100).

    Returns
    -------
    int
        Het geparsde getal, geclamped op [min_val, max_val].

    Raises
    ------
    ValueError
        Als geen enkel getal gevonden kan worden.
    """
    import re

    response = raw_response.strip()

    # Geval 1: het antwoord is rechtstreeks een getal (ideale case)
    if response.isdigit():
        return max(min_val, min(max_val, int(response)))

    # Geval 2: zoek het eerste getal in de tekst
    matches = re.findall(r'\b\d+\b', response)
    if matches:
        return max(min_val, min(max_val, int(matches[0])))

    raise ValueError(
        f"Could not parse integer from response: {raw_response!r}"
    )


