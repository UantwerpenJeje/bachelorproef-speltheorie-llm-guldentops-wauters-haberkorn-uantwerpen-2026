"""
config.py
=========
Centrale configuratie van het experiment.
Alle constanten staan hier zodat we ze niet hoeven te zoeken in de code.
"""

# ---------------------------------------------------------------------------
# LLM-modellen
# ---------------------------------------------------------------------------
# We gebruiken LiteLLM, dat een uniforme interface biedt voor alle providers.
# Modelnamen volgen de LiteLLM-conventie:
#   - OpenAI:    "gpt-4o-mini"
#   - Anthropic: "anthropic/claude-haiku-4-5"
#   - Gemini:    "gemini/gemini-2.0-flash"
#   - DeepSeek:  "deepseek/deepseek-chat"
#   - Groq:      "groq/llama-3.1-8b-instant"

MODELS = {
    "gpt-4o-mini":      "gpt-4o-mini",
    "claude-haiku":     "anthropic/claude-haiku-4-5",
    "gemini-flash":     "gemini/gemini-2.0-flash",
    "deepseek-chat":    "deepseek/deepseek-chat",
    "llama-3.1-8b":     "groq/llama-3.1-8b-instant",
}

# ---------------------------------------------------------------------------
# Experimentparameters
# ---------------------------------------------------------------------------

# Temperatuur: 0.7 geeft variatie tussen runs (nodig om gemiddelde + stdev
# te kunnen berekenen). T=0 zou altijd hetzelfde antwoord geven bij
# deterministische tegenstanders (AC, AD, TfT) en runs zouden niets toevoegen.
TEMPERATURE = 0.7

# Aantal runs per conditie (1 conditie = 1 model x 1 spel x 1 tegenstander x 1 framing)
RUNS_ITERATIVE = 10        # voor PD, Chicken, Stag Hunt
RUNS_ONE_SHOT  = 30        # voor Dictator, Ultimatum, Beauty Contest

# Aantal rondes binnen één run
ROUNDS = {
    "prisoners_dilemma": 50,
    "chicken_game":      20,
    "stag_hunt":         20,
}

# Tegenstanderstrategieën (geïmplementeerd in strategies.py)
OPPONENT_STRATEGIES = ["AC", "AD", "TfT", "Random"]
# LLM-vs-LLM wordt apart afgehandeld in run_experiment.py

# Beauty Contest parameters
BEAUTY_CONTEST_PLAYERS = 5   # totaal aantal spelers (1 LLM + 4 willekeurige)
BEAUTY_CONTEST_ROUNDS  = 5   # aantal rondes per run

# Framings (geïmplementeerd in prompts.py)
FRAMINGS = ["neutral", "competitive"]

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
RESULTS_DIR = "results"
RANDOM_SEED = 42  # voor reproduceerbaarheid van de Random-strategie
