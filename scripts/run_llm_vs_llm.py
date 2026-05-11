"""
run_llm_vs_llm.py
=================
Orchestrator voor LLM-vs-LLM experimenten in game theory.

In dit script spelen twee LLMs tegen elkaar, in plaats van een LLM
tegen een vaste strategie (zie run_experiment.py). Elk LLM krijgt
zijn eigen prompt met de geschiedenis vanuit zijn eigen perspectief.

Er worden TWEE rijen per ronde weggeschreven naar de CSV-output,
zodat het gedrag van elk model apart geanalyseerd kan worden met
dezelfde analysecode als voor LLM-vs-strategie experimenten.

Gebruik:
    # Één specifiek paar
    python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat

    # Alle paren binnen een lijst van modellen
    python run_llm_vs_llm.py --models gpt-4o-mini deepseek-chat claude-haiku

    # Selectie van spellen en framings
    python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat \\
        --games prisoners_dilemma --framings neutral

    # Zonder echte API-calls (test)
    python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat --dry-run
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from itertools import combinations, product

from tqdm import tqdm

import config
from llm_client import call_llm
from prompts import build_prompt, parse_action
from games import prisoners_dilemma, chicken_game, stag_hunt

# Mapping van spelnaam naar de bijhorende module (zelfde als run_experiment.py)
GAME_MODULES = {
    "prisoners_dilemma": prisoners_dilemma,
    "chicken_game":      chicken_game,
    "stag_hunt":         stag_hunt,
}


# ---------------------------------------------------------------------------
# Eén ronde spelen tussen twee LLMs
# ---------------------------------------------------------------------------

def play_round_llm_vs_llm(
    model1_string: str,
    model2_string: str,
    game_name: str,
    framing: str,
    history_p1: list,
    history_p2: list,
    round_num: int,
    total_rounds: int,
    temperature: float,
    dry_run: bool = False,
) -> dict:
    """
    Speelt één ronde waarbij twee LLMs simultaan beslissen.

    Elke speler krijgt zijn eigen prompt met de geschiedenis vanuit
    zijn eigen perspectief. De acties worden daarna simultaan verwerkt:
    geen van beiden ziet de keuze van de ander vóór zijn eigen beslissing.

    Parameters
    ----------
    model1_string : str
        Volledige LiteLLM-modelstring van speler 1 (bv. "gpt-4o-mini").
    model2_string : str
        Volledige LiteLLM-modelstring van speler 2 (bv. "deepseek/deepseek-chat").
    game_name : str
        Naam van het spel (bv. "prisoners_dilemma").
    framing : str
        Framing van de prompt ("neutral" of "competitive").
    history_p1 : list
        Spelgeschiedenis vanuit het perspectief van speler 1.
    history_p2 : list
        Spelgeschiedenis vanuit het perspectief van speler 2.
    round_num : int
        Huidige rondenummer.
    total_rounds : int
        Totaal aantal rondes in deze run.
    dry_run : bool
        Als True, worden geen echte API-calls gedaan.

    Returns
    -------
    dict
        Bevat de acties, payoffs en ruwe antwoorden van beide spelers.
    """
    game_module = GAME_MODULES[game_name]

    # 1. Prompt bouwen voor elke speler vanuit zijn eigen perspectief
    prompt_p1 = build_prompt(game_name, framing, history_p1, round_num, total_rounds)
    prompt_p2 = build_prompt(game_name, framing, history_p2, round_num, total_rounds)

    if dry_run:
        # Geen echte API-calls in dry-run modus, dummy-waarden gebruiken
        action_p1, action_p2 = "C", "C"
        raw_p1, raw_p2 = "[DRY RUN]", "[DRY RUN]"
    else:
        # 2. Beide LLMs beslissen (worden na elkaar opgeroepen, maar staan
        #    logisch simultaan: geen van beiden heeft de keuze van de ander gezien)
        raw_p1 = call_llm(
            model=model1_string,
            prompt=prompt_p1,
            temperature=temperature,
        )
        raw_p2 = call_llm(
            model=model2_string,
            prompt=prompt_p2,
            temperature=temperature,
        )

        # 3. Antwoorden parsen naar interne C/D labels
        try:
            action_p1 = parse_action(raw_p1, game_name, framing)
        except ValueError as e:
            print(f"  [parse error p1] {e}")
            action_p1 = "PARSE_ERROR"

        try:
            action_p2 = parse_action(raw_p2, game_name, framing)
        except ValueError as e:
            print(f"  [parse error p2] {e}")
            action_p2 = "PARSE_ERROR"

    # 4. Payoffs berekenen (enkel als beide acties geldig zijn)
    if action_p1 in ("C", "D") and action_p2 in ("C", "D"):
        payoff_p1, payoff_p2 = game_module.get_payoff(action_p1, action_p2)
    else:
        payoff_p1, payoff_p2 = 0, 0  # bij parse error, geen punten toegekend

    return {
        "action_p1": action_p1,
        "action_p2": action_p2,
        "payoff_p1": payoff_p1,
        "payoff_p2": payoff_p2,
        "raw_p1":    raw_p1,
        "raw_p2":    raw_p2,
    }


# ---------------------------------------------------------------------------
# Eén volledige run (= meerdere rondes binnen één conditie)
# ---------------------------------------------------------------------------

def play_run_llm_vs_llm(
    model1_name: str,
    model1_string: str,
    model2_name: str,
    model2_string: str,
    game_name: str,
    framing: str,
    run_id: int,
    temperature: float,
    csv_writer,
    dry_run: bool = False,
) -> None:
    """
    Speelt een volledige run en schrijft voor elke ronde TWEE rijen weg.

    De eerste rij bevat het perspectief van speler 1 (model1 als "llm"),
    de tweede rij het perspectief van speler 2 (model2 als "llm").
    Dit maakt het mogelijk om elk model apart te analyseren met dezelfde
    code als voor LLM-vs-strategie experimenten.

    Parameters
    ----------
    model1_name : str
        Korte naam van speler 1 (sleutel in config.MODELS).
    model1_string : str
        Volledige LiteLLM-modelstring van speler 1.
    model2_name : str
        Korte naam van speler 2.
    model2_string : str
        Volledige LiteLLM-modelstring van speler 2.
    game_name : str
        Naam van het spel.
    framing : str
        Framing van de prompt.
    run_id : int
        Volgnummer van de huidige run (1-gebaseerd).
    temperature : float
        Temperatuur voor de LLM-calls (0 = deterministisch, 1 = variabel).
    csv_writer : csv.DictWriter
        Open CSV-writer om resultaten onmiddellijk weg te schrijven.
    dry_run : bool
        Als True, worden geen echte API-calls gedaan.
    """
    # Bij T=0 is het antwoord deterministisch; 1 ronde volstaat.
    total_rounds = 1 if temperature == 0 else config.ROUNDS[game_name]

    # Aparte geschiedenis voor elke speler, elk vanuit hun eigen perspectief.
    # history_p1: llm_action = actie van p1, opponent_action = actie van p2
    # history_p2: llm_action = actie van p2, opponent_action = actie van p1
    history_p1 = []
    history_p2 = []

    for round_num in range(1, total_rounds + 1):
        result = play_round_llm_vs_llm(
            model1_string=model1_string,
            model2_string=model2_string,
            game_name=game_name,
            framing=framing,
            history_p1=history_p1,
            history_p2=history_p2,
            round_num=round_num,
            total_rounds=total_rounds,
            temperature=temperature,
            dry_run=dry_run,
        )

        # Rij 1: perspectief van speler 1 (model1 als "llm", model2 als tegenstander)
        csv_writer.writerow({
            "model":             model1_name,
            "game":              game_name,
            "opponent_strategy": "LLM",           # geen vaste strategie
            "framing":           framing,
            "run_id":            run_id,
            "round":             round_num,
            "llm_action":        result["action_p1"],
            "opponent_action":   result["action_p2"],
            "llm_payoff":        result["payoff_p1"],
            "opponent_payoff":   result["payoff_p2"],
            "raw_response":      result["raw_p1"],
            "temperature":       temperature,
            "opponent_model":    model2_name,
            "perspective":       "player1",
        })

        # Rij 2: perspectief van speler 2 (model2 als "llm", model1 als tegenstander)
        csv_writer.writerow({
            "model":             model2_name,
            "game":              game_name,
            "opponent_strategy": "LLM",
            "framing":           framing,
            "run_id":            run_id,
            "round":             round_num,
            "llm_action":        result["action_p2"],
            "opponent_action":   result["action_p1"],
            "llm_payoff":        result["payoff_p2"],
            "opponent_payoff":   result["payoff_p1"],
            "raw_response":      result["raw_p2"],
            "temperature":       temperature,
            "opponent_model":    model1_name,
            "perspective":       "player2",
        })

        # Geschiedenis bijwerken voor de volgende ronde (elk vanuit eigen perspectief)
        history_p1.append({
            "round":           round_num,
            "llm_action":      result["action_p1"],
            "opponent_action": result["action_p2"],
            "llm_payoff":      result["payoff_p1"],
            "opponent_payoff": result["payoff_p2"],
        })
        history_p2.append({
            "round":           round_num,
            "llm_action":      result["action_p2"],
            "opponent_action": result["action_p1"],
            "llm_payoff":      result["payoff_p2"],
            "opponent_payoff": result["payoff_p1"],
        })


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def main():
    """Parst CLI-argumenten, stelt paren samen en start de experimentlus."""
    parser = argparse.ArgumentParser(
        description="Run LLM-vs-LLM game theory experimenten.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
voorbeelden:
  # Één specifiek paar
  python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat

  # Alle paren uit een lijst van modellen
  python run_llm_vs_llm.py --models gpt-4o-mini deepseek-chat claude-haiku

  # Specifiek spel, zonder API-calls
  python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat \\
      --games prisoners_dilemma --dry-run
        """,
    )

    # --- Modelkeuze: ofwel --player1/--player2, ofwel --models ---
    # De twee opties zijn wederzijds uitsluitend om verwarring te vermijden.
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument(
        "--player1", metavar="MODEL",
        help="Eerste model (bv. gpt-4o-mini). Gebruik samen met --player2.",
    )
    model_group.add_argument(
        "--models", nargs="+", metavar="MODEL",
        help="Lijst van 2+ modellen. Alle unieke paren worden gerund.",
    )
    parser.add_argument(
        "--player2", metavar="MODEL",
        help="Tweede model (bv. deepseek-chat). Verplicht bij --player1.",
    )

    # --- Overige opties ---
    parser.add_argument(
        "--games", nargs="+", default=None,
        help="Spellen om te testen. Default: alle.",
    )
    parser.add_argument(
        "--framings", nargs="+", default=None,
        help="Framings (neutral, competitive). Default: beide.",
    )
    parser.add_argument(
        "--runs", type=int, default=None,
        help="Aantal runs per conditie. Default: config.RUNS_ITERATIVE.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Toon wat uitgevoerd zou worden zonder echte API-calls.",
    )

    args = parser.parse_args()

    # --- Validatie van modelkeuze ---
    if args.player1 and not args.player2:
        parser.error("--player1 vereist ook --player2.")
    if args.player2 and not args.player1:
        parser.error("--player2 vereist ook --player1.")

    # Stel de lijst van te testen paren samen
    if args.models:
        if len(args.models) < 2:
            parser.error("--models vereist minimaal 2 modellen.")
        # combinations() geeft unieke paren zonder herhaling: (A,B) maar niet (B,A)
        pairs = list(combinations(args.models, 2))
    else:
        pairs = [(args.player1, args.player2)]

    # Selectie van spellen, framings en runs op basis van CLI-argumenten
    games    = args.games    or list(GAME_MODULES.keys())
    framings = args.framings or config.FRAMINGS
    n_runs   = args.runs     or config.RUNS_ITERATIVE

    # --- Validatie van spellen en modellen ---
    for g in games:
        if g not in GAME_MODULES:
            sys.exit(f"Onbekend spel: {g}. Kies uit {list(GAME_MODULES.keys())}")
    all_models_in_pairs = {m for pair in pairs for m in pair}
    for m in all_models_in_pairs:
        if m not in config.MODELS:
            sys.exit(f"Onbekend model: {m}. Kies uit {list(config.MODELS.keys())}")

    # --- Output-bestand aanmaken met timestamp ---
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(config.RESULTS_DIR, f"results_llmvsllm_{timestamp}.csv")

    # Kolommen: compatibel met run_experiment.py + extra kolommen voor LLM-vs-LLM
    fieldnames = [
        "model", "game", "opponent_strategy", "framing", "run_id", "round",
        "llm_action", "opponent_action", "llm_payoff", "opponent_payoff",
        "raw_response", "temperature",
        # Extra kolommen specifiek voor LLM-vs-LLM analyse
        "opponent_model", "perspective",
    ]

    temperatures = config.TEMPERATURES

    # Schatting: 2 API-calls per ronde (één per speler)
    # T=0: 1 ronde per spel; T=1: config.ROUNDS[g] rondes per spel
    total_calls = sum(
        len(pairs) * len(framings) * n_runs
        * (1 if t == 0 else config.ROUNDS[g]) * 2
        for t in temperatures
        for g in games
    )
    print(f"Geschat aantal API-calls: ~{total_calls}")
    print(f"Temperaturen: {temperatures}")
    print(f"Paren: {[f'{m1} vs {m2}' for m1, m2 in pairs]}")
    print(f"Resultaten worden weggeschreven naar: {output_path}")
    print(f"Dry-run modus: {args.dry_run}")
    print()

    # --- Hoofdloop ---
    # We loopen over elke conditie (paar x spel x framing x temperatuur) en spelen n_runs keer.
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        conditions = list(product(pairs, games, framings, temperatures))
        for ((model1_name, model2_name), game_name, framing, temperature) in tqdm(
            conditions, desc="Condities", unit="cond"
        ):
            model1_string = config.MODELS[model1_name]
            model2_string = config.MODELS[model2_name]

            for run_id in range(1, n_runs + 1):
                try:
                    play_run_llm_vs_llm(
                        model1_name=model1_name,
                        model1_string=model1_string,
                        model2_name=model2_name,
                        model2_string=model2_string,
                        game_name=game_name,
                        framing=framing,
                        run_id=run_id,
                        temperature=temperature,
                        csv_writer=writer,
                        dry_run=args.dry_run,
                    )
                    f.flush()  # forceer wegschrijven naar disk na elke run
                except Exception as e:
                    print(
                        f"\n[ERROR] {model1_name} vs {model2_name} / "
                        f"{game_name} / {framing} / T={temperature} / run {run_id}: {e}"
                    )
                    print("Doorgaan met volgende run...\n")

    print(f"\nKlaar! Resultaten staan in: {output_path}")


if __name__ == "__main__":
    main()
