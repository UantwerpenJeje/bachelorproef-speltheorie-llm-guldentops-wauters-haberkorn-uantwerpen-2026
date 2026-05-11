"""
run_experiment.py
=================
Orchestrator voor alle iteratieve game-theory experimenten.

Deze module loopt door alle combinaties van:
    model x spel x tegenstander x framing x run x ronde
en schrijft elk resultaat onmiddellijk weg naar een CSV-bestand,
zodat geen data verloren gaat als het experiment crasht.

Gebruik:
    python run_experiment.py                  # alle modellen, alle spellen
    python run_experiment.py --models gpt-4o-mini deepseek-chat
    python run_experiment.py --games prisoners_dilemma
    python run_experiment.py --dry-run        # toon wat het zou doen, zonder API-calls
"""

import argparse
import csv
import os
import random
import sys
from datetime import datetime
from itertools import product

from tqdm import tqdm

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, 'config_files'))

import config
from llm_client import call_llm
from prompts import build_prompt, parse_action
from strategies import STRATEGY_FUNCS
from games import prisoners_dilemma, chicken_game, stag_hunt

# Mapping van spelnaam (zoals in config.py) naar de bijhorende module
GAME_MODULES = {
    "prisoners_dilemma": prisoners_dilemma,
    "chicken_game":      chicken_game,
    "stag_hunt":         stag_hunt,
}


# ---------------------------------------------------------------------------
# Eén ronde spelen
# ---------------------------------------------------------------------------
def play_round(
    model_name: str,
    model_string: str,
    game_name: str,
    framing: str,
    history: list,
    round_num: int,
    total_rounds: int,
    opponent_strategy_name: str,
    temperature: float,
    dry_run: bool = False,
) -> dict:
    """Speelt één ronde en geeft de resultaten terug als een dict."""
    game_module = GAME_MODULES[game_name]
    strategy_func = STRATEGY_FUNCS[opponent_strategy_name]

    # 1. Tegenstander beslist (deterministisch o.b.v. de geschiedenis)
    opponent_action = strategy_func(history)

    # 2. LLM beslist via API-call
    prompt = build_prompt(game_name, framing, history, round_num, total_rounds)

    if dry_run:
        # Geen echte API-call, alleen tonen dat we hier zouden zijn
        llm_action = "C"  # dummy
        raw_response = "[DRY RUN]"
    else:
        raw_response = call_llm(
            model=model_string,
            prompt=prompt,
            temperature=temperature,
        )
        try:
            llm_action = parse_action(raw_response, game_name, framing)
        except ValueError as e:
            # Het LLM heeft iets onverwachts geantwoord. Loggen, niet crashen.
            print(f"  [parse error] {e}")
            llm_action = "PARSE_ERROR"

    # 3. Payoffs berekenen
    if llm_action in ("C", "D"):
        llm_payoff, opponent_payoff = game_module.get_payoff(llm_action, opponent_action)
    else:
        llm_payoff, opponent_payoff = 0, 0  # bij parse error, geen punten

    return {
        "round":            round_num,
        "llm_action":       llm_action,
        "opponent_action":  opponent_action,
        "llm_payoff":       llm_payoff,
        "opponent_payoff":  opponent_payoff,
        "raw_response":     raw_response,
    }


# ---------------------------------------------------------------------------
# Eén volledige run (= meerdere rondes binnen één spel-conditie)
# ---------------------------------------------------------------------------
def play_run(
    model_name: str,
    model_string: str,
    game_name: str,
    framing: str,
    opponent_strategy_name: str,
    run_id: int,
    temperature: float,
    csv_writer,
    dry_run: bool = False,
) -> None:
    """Speelt een volledige run (X rondes) en schrijft elke ronde weg."""
    # Bij T=0 is het antwoord deterministisch; 1 ronde volstaat.
    total_rounds = 1 if temperature == 0 else config.ROUNDS[game_name]
    history = []

    for round_num in range(1, total_rounds + 1):
        result = play_round(
            model_name=model_name,
            model_string=model_string,
            game_name=game_name,
            framing=framing,
            history=history,
            round_num=round_num,
            total_rounds=total_rounds,
            opponent_strategy_name=opponent_strategy_name,
            temperature=temperature,
            dry_run=dry_run,
        )

        # Schrijf onmiddellijk weg naar CSV (lijn per lijn) zodat we niets verliezen
        csv_writer.writerow({
            "model":             model_name,
            "game":              game_name,
            "opponent_strategy": opponent_strategy_name,
            "framing":            framing,
            "run_id":            run_id,
            "round":             result["round"],
            "llm_action":        result["llm_action"],
            "opponent_action":   result["opponent_action"],
            "llm_payoff":        result["llm_payoff"],
            "opponent_payoff":   result["opponent_payoff"],
            "raw_response":      result["raw_response"],
            "temperature":       temperature,
        })

        # Voeg toe aan geschiedenis voor de volgende ronde
        history.append({
            "round":           result["round"],
            "llm_action":      result["llm_action"],
            "opponent_action": result["opponent_action"],
            "llm_payoff":      result["llm_payoff"],
            "opponent_payoff": result["opponent_payoff"],
        })


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Run LLM game theory experiments.")
    parser.add_argument(
        "--models", nargs="+", default=None,
        help="Modellen om te testen (bv. gpt-4o-mini deepseek-chat). Default: alle."
    )
    parser.add_argument(
        "--games", nargs="+", default=None,
        help="Spellen om te testen. Default: alle iteratieve spellen."
    )
    parser.add_argument(
        "--strategies", nargs="+", default=None,
        help="Tegenstanderstrategieën. Default: alle."
    )
    parser.add_argument(
        "--framings", nargs="+", default=None,
        help="Framings (neutral, competitive). Default: beide."
    )
    parser.add_argument(
        "--runs", type=int, default=None,
        help="Aantal runs per conditie. Default: config.RUNS_ITERATIVE."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print wat zou uitgevoerd worden zonder API-calls te doen."
    )
    args = parser.parse_args()

    # Reproduceerbaarheid voor de Random-strategie
    random.seed(config.RANDOM_SEED)

    # Selectie van modellen, spellen, etc. op basis van CLI-argumenten
    models     = args.models     or list(config.MODELS.keys())
    games      = args.games      or list(GAME_MODULES.keys())
    strategies = args.strategies or config.OPPONENT_STRATEGIES
    framings   = args.framings   or config.FRAMINGS
    n_runs     = args.runs       or config.RUNS_ITERATIVE

    # Validatie
    for m in models:
        if m not in config.MODELS:
            sys.exit(f"Onbekend model: {m}. Kies uit {list(config.MODELS.keys())}")
    for g in games:
        if g not in GAME_MODULES:
            sys.exit(f"Onbekend spel: {g}. Kies uit {list(GAME_MODULES.keys())}")

    # Output-bestand met timestamp zodat oude resultaten niet overschreven worden
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(config.RESULTS_DIR, f"results_{timestamp}.csv")

    fieldnames = [
        "model", "game", "opponent_strategy", "framing", "run_id", "round",
        "llm_action", "opponent_action", "llm_payoff", "opponent_payoff",
        "raw_response", "temperature",
    ]

    temperatures = config.TEMPERATURES

    # Totaal aantal LLM-calls inschatten
    # T=0: 1 ronde per spel; T=1: config.ROUNDS[g] rondes per spel
    total_calls = sum(
        len(models) * len(strategies) * len(framings) * n_runs
        * (1 if t == 0 else config.ROUNDS[g])
        for t in temperatures
        for g in games
    )
    print(f"Geschat aantal API-calls: ~{total_calls}")
    print(f"Temperaturen: {temperatures}")
    print(f"Resultaten worden weggeschreven naar: {output_path}")
    print(f"Dry-run modus: {args.dry_run}")
    print()

    # Hoofdloop. We loopen over elke conditie en spelen n_runs keer.
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # tqdm geeft een visuele voortgangsbalk
        conditions = list(product(models, games, strategies, framings, temperatures))
        for (model_name, game_name, strategy, framing, temperature) in tqdm(
            conditions, desc="Conditions", unit="cond"
        ):
            model_string = config.MODELS[model_name]
            for run_id in range(1, n_runs + 1):
                try:
                    play_run(
                        model_name=model_name,
                        model_string=model_string,
                        game_name=game_name,
                        framing=framing,
                        opponent_strategy_name=strategy,
                        run_id=run_id,
                        temperature=temperature,
                        csv_writer=writer,
                        dry_run=args.dry_run,
                    )
                    f.flush()  # forceer wegschrijven naar disk
                except Exception as e:
                    print(f"\n[ERROR] {model_name} / {game_name} / {strategy} / "
                          f"{framing} / T={temperature} / run {run_id}: {e}")
                    print("Doorgaan met volgende run...\n")

    print(f"\nKlaar! Resultaten staan in: {output_path}")


if __name__ == "__main__":
    main()
