"""
run_oneshot.py
==============
Orchestrator voor eenmalige (one-shot) game-theory experimenten:
    - Dictator Game  : 1 API-call per run, LLM verdeelt 100 euro.
    - Ultimatum Game : 2 API-calls per run (proposer + responder).
    - Beauty Contest : num_rounds API-calls per run, LLM vs willekeurige spelers.

Per speltype wordt een apart tijdgestempeld CSV-bestand aangemaakt in results/.

Gebruik:
    # Alle spellen, alle modellen
    python run_oneshot.py --models gpt-4o-mini deepseek-chat

    # Enkel Dictator Game
    python run_oneshot.py --models gpt-4o-mini --games dictator_game

    # Ultimatum met een andere responder
    python run_oneshot.py --models gpt-4o-mini --games ultimatum_game \\
        --responder-model deepseek-chat

    # Beauty Contest met aangepaste parameters
    python run_oneshot.py --models gpt-4o-mini --games beauty_contest \\
        --num-players 7 --num-rounds 8

    # Dry-run (geen echte API-calls)
    python run_oneshot.py --models gpt-4o-mini --dry-run
"""

import argparse
import csv
import os
import random
import sys
from datetime import datetime
from itertools import product

from tqdm import tqdm

import config
from llm_client import call_llm
from prompts import (
    build_dictator_prompt,
    build_ultimatum_proposer_prompt,
    build_ultimatum_responder_prompt,
    build_beauty_prompt,
    parse_amount,
    parse_ultimatum_response,
)
from games import dictator_game, ultimatum_game, beauty_contest

# Mapping van CLI-naam naar game-module
ONESHOT_GAMES = {
    "dictator_game":  dictator_game,
    "ultimatum_game": ultimatum_game,
    "beauty_contest": beauty_contest,
}

# CSV-velden per speltype (apart omdat de structuur sterk verschilt)
FIELDNAMES = {
    "dictator_game": [
        "model", "game", "framing", "run_id",
        "amount_shared", "amount_kept", "payoff_dictator", "payoff_receiver",
        "raw_response", "temperature",
    ],
    "ultimatum_game": [
        "proposer_model", "responder_model", "game", "framing", "run_id",
        "offer", "response", "payoff_proposer", "payoff_responder",
        "raw_proposer", "raw_responder", "temperature",
    ],
    "beauty_contest": [
        "model", "game", "framing", "run_id", "round",
        "llm_number", "random_numbers", "mean", "target",
        "winner_number", "llm_won", "payoff",
        "raw_response", "temperature", "num_players", "num_rounds",
    ],
}


# ---------------------------------------------------------------------------
# Dictator Game — één run
# ---------------------------------------------------------------------------

def run_dictator(
    model_name: str,
    model_string: str,
    framing: str,
    run_id: int,
    csv_writer,
    dry_run: bool = False,
) -> None:
    """
    Speelt één run van het Dictator Game: één API-call, geen interactie.

    Parameters
    ----------
    model_name : str
        Korte naam van het model (sleutel in config.MODELS).
    model_string : str
        Volledige LiteLLM-modelstring.
    framing : str
        "neutral" of "competitive".
    run_id : int
        Volgnummer van de huidige run.
    csv_writer : csv.DictWriter
        Open CSV-writer.
    dry_run : bool
        Als True, geen echte API-call.
    """
    prompt = build_dictator_prompt(framing)

    if dry_run:
        raw = "[DRY RUN]"
        amount = 0
    else:
        raw = call_llm(model=model_string, prompt=prompt, temperature=config.TEMPERATURE)
        try:
            amount = parse_amount(raw)
        except ValueError as e:
            print(f"  [parse error dictator] {e}")
            amount = -1  # markeer als fout in de data

    # Payoffs berekenen (bij parse error: gebruik 0 als fallback)
    payoff_dictator, payoff_receiver = dictator_game.get_payoff(max(0, amount))

    csv_writer.writerow({
        "model":           model_name,
        "game":            "dictator_game",
        "framing":         framing,
        "run_id":          run_id,
        "amount_shared":   amount,
        "amount_kept":     100 - amount if amount >= 0 else -1,
        "payoff_dictator": payoff_dictator,
        "payoff_receiver": payoff_receiver,
        "raw_response":    raw,
        "temperature":     config.TEMPERATURE,
    })


# ---------------------------------------------------------------------------
# Ultimatum Game — één run (proposer + responder)
# ---------------------------------------------------------------------------

def run_ultimatum(
    proposer_name: str,
    proposer_string: str,
    responder_name: str,
    responder_string: str,
    framing: str,
    run_id: int,
    csv_writer,
    dry_run: bool = False,
) -> None:
    """
    Speelt één run van het Ultimatum Game: twee API-calls.

    Fase 1 — proposer beslist hoeveel hij aanbiedt (0–100).
    Fase 2 — responder ziet het aanbod en kiest ACCEPT of REJECT.

    Parameters
    ----------
    proposer_name : str
        Korte naam van de proposer.
    proposer_string : str
        Volledige LiteLLM-modelstring van de proposer.
    responder_name : str
        Korte naam van de responder (kan gelijk zijn aan proposer).
    responder_string : str
        Volledige LiteLLM-modelstring van de responder.
    framing : str
        "neutral" of "competitive".
    run_id : int
        Volgnummer van de huidige run.
    csv_writer : csv.DictWriter
        Open CSV-writer.
    dry_run : bool
        Als True, geen echte API-calls.
    """
    # --- Fase 1: proposer beslist ---
    prompt_proposer = build_ultimatum_proposer_prompt(framing)

    if dry_run:
        raw_proposer = "[DRY RUN]"
        offer = 50
    else:
        raw_proposer = call_llm(
            model=proposer_string, prompt=prompt_proposer,
            temperature=config.TEMPERATURE,
        )
        try:
            offer = parse_amount(raw_proposer)
        except ValueError as e:
            print(f"  [parse error proposer] {e}")
            offer = -1

    # --- Fase 2: responder reageert op het aanbod ---
    # De responder ziet enkel het aangeboden bedrag, niet de redenering.
    prompt_responder = build_ultimatum_responder_prompt(framing, max(0, offer))

    if dry_run:
        raw_responder = "[DRY RUN]"
        response = "ACCEPT"
    else:
        raw_responder = call_llm(
            model=responder_string, prompt=prompt_responder,
            temperature=config.TEMPERATURE,
        )
        try:
            response = parse_ultimatum_response(raw_responder)
        except ValueError as e:
            print(f"  [parse error responder] {e}")
            response = "PARSE_ERROR"

    # --- Payoffs berekenen ---
    if offer >= 0 and response in ("ACCEPT", "REJECT"):
        payoff_proposer, payoff_responder = ultimatum_game.get_payoff(offer, response)
    else:
        payoff_proposer, payoff_responder = 0, 0

    csv_writer.writerow({
        "proposer_model":   proposer_name,
        "responder_model":  responder_name,
        "game":             "ultimatum_game",
        "framing":          framing,
        "run_id":           run_id,
        "offer":            offer,
        "response":         response,
        "payoff_proposer":  payoff_proposer,
        "payoff_responder": payoff_responder,
        "raw_proposer":     raw_proposer,
        "raw_responder":    raw_responder,
        "temperature":      config.TEMPERATURE,
    })


# ---------------------------------------------------------------------------
# Beauty Contest — één run (meerdere rondes met feedback)
# ---------------------------------------------------------------------------

def run_beauty(
    model_name: str,
    model_string: str,
    framing: str,
    run_id: int,
    num_players: int,
    num_rounds: int,
    csv_writer,
    dry_run: bool = False,
) -> None:
    """
    Speelt één run van het Beauty Contest over num_rounds rondes.

    Het LLM staat op index 0 in de spelerslijst. De overige (num_players - 1)
    spelers zijn gesimuleerd: zij kiezen elk ronde een willekeurig geheel getal
    tussen 0 en 100. Na elke ronde krijgt het LLM feedback over het gemiddelde
    en het winnende getal.

    Parameters
    ----------
    model_name : str
        Korte naam van het LLM.
    model_string : str
        Volledige LiteLLM-modelstring.
    framing : str
        "neutral" of "competitive".
    run_id : int
        Volgnummer van de huidige run.
    num_players : int
        Totaal aantal spelers (incl. het LLM).
    num_rounds : int
        Aantal rondes in deze run.
    csv_writer : csv.DictWriter
        Open CSV-writer (één rij per ronde).
    dry_run : bool
        Als True, geen echte API-calls.
    """
    history = []        # feedback over vorige rondes
    num_random = num_players - 1  # aantal gesimuleerde random spelers

    for round_num in range(1, num_rounds + 1):
        # 1. Prompt bouwen met geschiedenis van vorige rondes
        prompt = build_beauty_prompt(
            framing=framing,
            history=history,
            round_num=round_num,
            total_rounds=num_rounds,
            num_players=num_players,
        )

        # 2. LLM beslist (staat op index 0 in de spelerslijst)
        if dry_run:
            raw = "[DRY RUN]"
            llm_number = 33  # typische waarde ronde 1 als dummy
        else:
            raw = call_llm(
                model=model_string, prompt=prompt, temperature=config.TEMPERATURE
            )
            try:
                llm_number = parse_amount(raw)
            except ValueError as e:
                print(f"  [parse error beauty r{round_num}] {e}")
                llm_number = -1

        # 3. Willekeurige spelers kiezen hun getal (index 1 t/m num_players-1)
        random_numbers = [random.randint(0, 100) for _ in range(num_random)]

        # 4. Alle getallen samenvoegen (LLM op index 0)
        llm_val = max(0, llm_number)  # bij parse error → 0
        all_numbers = [llm_val] + random_numbers

        # 5. Uitslag berekenen
        mean = sum(all_numbers) / len(all_numbers)
        target = beauty_contest.compute_target(all_numbers)
        winner_idx = beauty_contest.get_winner_index(all_numbers)
        winner_number = all_numbers[winner_idx]
        payoff = beauty_contest.get_payoff(player_idx=0, numbers=all_numbers)

        # 6. Rij wegschrijven
        csv_writer.writerow({
            "model":          model_name,
            "game":           "beauty_contest",
            "framing":        framing,
            "run_id":         run_id,
            "round":          round_num,
            "llm_number":     llm_number,
            "random_numbers": "|".join(str(n) for n in random_numbers),
            "mean":           round(mean, 4),
            "target":         round(target, 4),
            "winner_number":  winner_number,
            "llm_won":        1 if winner_idx == 0 else 0,
            "payoff":         payoff,
            "raw_response":   raw,
            "temperature":    config.TEMPERATURE,
            "num_players":    num_players,
            "num_rounds":     num_rounds,
        })

        # 7. Geschiedenis bijwerken zodat het LLM volgende ronde feedback heeft
        history.append({
            "round":         round_num,
            "mean":          mean,
            "target":        target,
            "winner_number": winner_number,
        })


# ---------------------------------------------------------------------------
# Hoofdfunctie
# ---------------------------------------------------------------------------

def main():
    """Parst CLI-argumenten en orkestreert alle one-shot experimenten."""
    parser = argparse.ArgumentParser(
        description=(
            "Run one-shot game theory experimenten "
            "(Dictator Game, Ultimatum Game, Beauty Contest)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
voorbeelden:
  python run_oneshot.py --models gpt-4o-mini deepseek-chat
  python run_oneshot.py --models gpt-4o-mini --games dictator_game ultimatum_game
  python run_oneshot.py --models gpt-4o-mini --games ultimatum_game \\
      --responder-model deepseek-chat
  python run_oneshot.py --models gpt-4o-mini --games beauty_contest \\
      --num-players 7 --num-rounds 8 --runs 20
  python run_oneshot.py --models gpt-4o-mini --dry-run
        """,
    )

    parser.add_argument(
        "--models", nargs="+", required=True, metavar="MODEL",
        help="Modellen om te testen (bv. gpt-4o-mini deepseek-chat).",
    )
    parser.add_argument(
        "--games", nargs="+", default=None,
        choices=list(ONESHOT_GAMES.keys()),
        metavar="GAME",
        help=(
            "Spellen om te testen: dictator_game, ultimatum_game, beauty_contest. "
            "Default: alle."
        ),
    )
    parser.add_argument(
        "--framings", nargs="+", default=None,
        help="Framings (neutral, competitive). Default: beide.",
    )
    parser.add_argument(
        "--runs", type=int, default=None,
        help="Aantal runs per conditie. Default: config.RUNS_ONE_SHOT (30).",
    )
    # Ultimatum-specifieke optie
    parser.add_argument(
        "--responder-model", default=None, metavar="MODEL",
        dest="responder_model",
        help=(
            "Model dat als responder speelt in het Ultimatum Game. "
            "Default: hetzelfde als --models (zelfspel per model)."
        ),
    )
    # Beauty Contest-specifieke opties
    parser.add_argument(
        "--num-players", type=int, default=None, dest="num_players",
        help=(
            "Totaal aantal spelers in het Beauty Contest (incl. het LLM). "
            "Default: config.BEAUTY_CONTEST_PLAYERS (5)."
        ),
    )
    parser.add_argument(
        "--num-rounds", type=int, default=None, dest="num_rounds",
        help=(
            "Aantal rondes per run in het Beauty Contest. "
            "Default: config.BEAUTY_CONTEST_ROUNDS (5)."
        ),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Toon wat uitgevoerd zou worden zonder echte API-calls.",
    )

    args = parser.parse_args()

    # --- Selectie van parameters op basis van CLI-argumenten ---
    games     = args.games     or list(ONESHOT_GAMES.keys())
    framings  = args.framings  or config.FRAMINGS
    n_runs    = args.runs      or config.RUNS_ONE_SHOT
    n_players = args.num_players or config.BEAUTY_CONTEST_PLAYERS
    n_rounds  = args.num_rounds  or config.BEAUTY_CONTEST_ROUNDS

    # --- Validatie van modelnamen ---
    for m in args.models:
        if m not in config.MODELS:
            sys.exit(f"Onbekend model: {m}. Kies uit {list(config.MODELS.keys())}")
    if args.responder_model and args.responder_model not in config.MODELS:
        sys.exit(
            f"Onbekend responder-model: {args.responder_model}. "
            f"Kies uit {list(config.MODELS.keys())}"
        )

    # --- Reproduceerbaarheid voor willekeurige Beauty Contest-spelers ---
    random.seed(config.RANDOM_SEED)

    # --- Output-bestanden aanmaken (één per speltype) ---
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Bestanden en writers openen vóór de lus zodat de headers er altijd in zitten
    csv_files    = {}
    csv_writers  = {}
    output_paths = {}

    for game_name in games:
        path = os.path.join(
            config.RESULTS_DIR, f"results_oneshot_{game_name}_{timestamp}.csv"
        )
        output_paths[game_name] = path
        fh = open(path, "w", newline="", encoding="utf-8")
        csv_files[game_name]  = fh
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES[game_name])
        writer.writeheader()
        csv_writers[game_name] = writer

    # Schatting van het aantal API-calls
    calls_per_run = {
        "dictator_game":  1,
        "ultimatum_game": 2,
        "beauty_contest": n_rounds,
    }
    total_calls = sum(
        len(args.models) * len(framings) * n_runs * calls_per_run[g]
        for g in games
    )
    print(f"Geschat aantal API-calls: ~{total_calls}")
    print(f"Spellen: {games}")
    print(f"Modellen: {args.models}")
    if "ultimatum_game" in games:
        resp = args.responder_model or "(= zelfde als proposer)"
        print(f"Ultimatum responder: {resp}")
    if "beauty_contest" in games:
        print(f"Beauty Contest: {n_players} spelers, {n_rounds} rondes")
    print(f"Resultaten in: {config.RESULTS_DIR}/")
    print(f"Dry-run modus: {args.dry_run}")
    print()

    # --- Hoofdloop ---
    try:
        conditions = list(product(args.models, games, framings))
        for (model_name, game_name, framing) in tqdm(
            conditions, desc="Condities", unit="cond"
        ):
            model_string = config.MODELS[model_name]
            writer       = csv_writers[game_name]
            fh           = csv_files[game_name]

            for run_id in range(1, n_runs + 1):
                try:
                    if game_name == "dictator_game":
                        run_dictator(
                            model_name=model_name,
                            model_string=model_string,
                            framing=framing,
                            run_id=run_id,
                            csv_writer=writer,
                            dry_run=args.dry_run,
                        )

                    elif game_name == "ultimatum_game":
                        # Responder: apart model indien opgegeven, anders zelfspel
                        resp_name   = args.responder_model or model_name
                        resp_string = config.MODELS[resp_name]
                        run_ultimatum(
                            proposer_name=model_name,
                            proposer_string=model_string,
                            responder_name=resp_name,
                            responder_string=resp_string,
                            framing=framing,
                            run_id=run_id,
                            csv_writer=writer,
                            dry_run=args.dry_run,
                        )

                    elif game_name == "beauty_contest":
                        run_beauty(
                            model_name=model_name,
                            model_string=model_string,
                            framing=framing,
                            run_id=run_id,
                            num_players=n_players,
                            num_rounds=n_rounds,
                            csv_writer=writer,
                            dry_run=args.dry_run,
                        )

                    fh.flush()  # forceer wegschrijven naar disk na elke run

                except Exception as e:
                    print(
                        f"\n[ERROR] {model_name} / {game_name} / "
                        f"{framing} / run {run_id}: {e}"
                    )
                    print("Doorgaan met volgende run...\n")

    finally:
        # Sluit altijd alle bestanden netjes, ook bij een onverwachte fout
        for fh in csv_files.values():
            fh.close()

    print("\nKlaar! Resultaten staan in:")
    for game_name, path in output_paths.items():
        print(f"  {path}")


if __name__ == "__main__":
    main()
