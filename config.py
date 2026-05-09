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
#   - xAI:       "xai/grok-3-mini-beta"

MODELS = {
    "gpt-4o-mini":      "gpt-4o-mini",
    "claude-haiku":     "anthropic/claude-haiku-4-5",
    "gemini-flash":     "gemini/gemini-2.0-flash",
    "deepseek-chat":    "deepseek/deepseek-chat",
    "llama-3.1-8b":     "groq/llama-3.1-8b-instant",
    # TODO: verifieer de exacte LiteLLM-string voor xAI Grok vóór productierun
    "grok":             "xai/grok-3-mini-beta",
}

# ---------------------------------------------------------------------------
# Experimentparameters
# ---------------------------------------------------------------------------

# Twee temperatuurcondities:
#   T=0 — deterministisch; bij iteratieve spellen volstaat 1 ronde (het antwoord
#          verandert niet, dus extra rondes voegen geen informatie toe).
#   T=1 — maximaal variabel; het volledige aantal rondes wordt gespeeld.
TEMPERATURES = [0, 1]

# Aantal runs per conditie (1 conditie = 1 model x 1 spel x 1 tegenstander x 1 framing)
RUNS_ITERATIVE = 1         # voor PD, Chicken, Stag Hunt
RUNS_ONE_SHOT  = 1         # voor Dictator, Beauty Contest

# Aantal rondes binnen één run
ROUNDS = {
    "prisoners_dilemma": 10,
    "chicken_game":      10,
    "stag_hunt":         10,
}

# Tegenstanderstrategieën (geïmplementeerd in strategies.py)
OPPONENT_STRATEGIES = ["AC", "AD", "TfT", "Random"]
# LLM-vs-LLM wordt apart afgehandeld in run_experiment.py

# Beauty Contest parameters
BEAUTY_CONTEST_PLAYERS = 5   # totaal aantal spelers (1 LLM + 4 willekeurige)
BEAUTY_CONTEST_ROUNDS  = 20  # aantal rondes per run

# Framings (geïmplementeerd in prompts.py)
FRAMINGS = ["neutral", "competitive"]

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
RESULTS_DIR = "results"
RANDOM_SEED = 42  # voor reproduceerbaarheid van de Random-strategie
