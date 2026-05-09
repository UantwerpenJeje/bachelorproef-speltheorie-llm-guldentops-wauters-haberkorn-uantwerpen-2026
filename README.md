# Speltheoretisch gedrag van Large Language Models

Code horend bij de bachelorproef *"Het speltheoretisch gedrag van Large Language Models: een vergelijking met rationele en menselijke beslissers"* (Universiteit Antwerpen, Faculteit Bedrijfswetenschappen en Economie, academiejaar 2025-2026).

**Auteurs:** Stef Guldentops, Milan Wauters, Jérémie Haberkorn
**Promotor:** Prof. dr. David Martens
**Begeleider:** Wannes Van den Bulck

## Wat doet deze code?

Deze code voert geautomatiseerde experimenten uit waarin verschillende Large Language Models (LLMs) iteratieve speltheoretische spellen spelen tegen vaste tegenstanderstrategieën. Het doel is hun keuzes te vergelijken met:
1. de rationele oplossing volgens de speltheorie (Nash-evenwicht)
2. empirisch waargenomen menselijk gedrag uit de literatuur

### Onderzochte spellen

**Iteratief** (LLM vs vaste strategie — `run_experiment.py`)
- **Prisoner's Dilemma** (1 ronde bij T=0 / 10 rondes bij T=1)
- **Chicken Game** (1 ronde bij T=0 / 10 rondes bij T=1)
- **Stag Hunt** (1 ronde bij T=0 / 10 rondes bij T=1)

**Eenmalig / one-shot** (`run_oneshot.py`)
- **Dictator Game** — LLM verdeelt 100€; Nash = 0€, mensen ≈ 28€ (1 call per run, beide temperaturen)
- **Beauty Contest** — kies een getal 0–100; winnaar = dichtst bij 2/3 × gemiddelde; Nash = 0 (1 ronde bij T=0 / 20 rondes bij T=1)

**LLM vs LLM** (`run_llm_vs_llm.py`)
- Alle iteratieve spellen, maar de tegenstander is een tweede LLM in plaats van een vaste strategie

### Onderzochte modellen
| Model | Provider | LiteLLM-string |
|-------|----------|----------------|
| GPT-4o-mini | OpenAI (VS) | `gpt-4o-mini` |
| Claude Haiku 4.5 | Anthropic (VS) | `anthropic/claude-haiku-4-5` |
| Gemini 2.0 Flash | Google (VS) | `gemini/gemini-2.0-flash` |
| DeepSeek-V3 | DeepSeek (China) | `deepseek/deepseek-chat` |
| Llama 3.1 8B | Meta via Groq | `groq/llama-3.1-8b-instant` |
| Grok-3 Mini Beta | xAI (VS) | `xai/grok-3-mini-beta` |

### Tegenstanderstrategieën
- **AC** – Always Cooperate
- **AD** – Always Defect
- **TfT** – Tit-for-Tat
- **Random** – willekeurige keuze (50/50)

### Framings
- **neutral** – spel wordt beschreven zonder geladen termen, acties zijn `A` / `B`
- **competitive** – expliciete nadruk op winnen en eigen scoremaximalisatie

## Projectstructuur

```
.
├── README.md                  ← dit bestand
├── requirements.txt           ← Python-dependencies
├── .env.example               ← model voor API-sleutels
├── .gitignore                 ← bestanden die niet gepushed worden (incl. .env!)
├── config.py                  ← centrale configuratie (modellen, runs, etc.)
├── llm_client.py              ← uniforme wrapper rond alle LLM-API's (LiteLLM)
├── strategies.py              ← AC, AD, TfT, Random
├── prompts.py                 ← prompt-templates per spel × framing + parse-functies
├── games/
│   ├── prisoners_dilemma.py   ← payoff-matrix (iteratief)
│   ├── chicken_game.py        ← payoff-matrix (iteratief)
│   ├── stag_hunt.py           ← payoff-matrix (iteratief)
│   ├── dictator_game.py       ← payoff-functie (one-shot)
│   └── beauty_contest.py      ← hulpfuncties (iteratief met feedback)
├── run_experiment.py          ← LLM vs vaste strategie (iteratief)
├── run_llm_vs_llm.py          ← LLM vs LLM (iteratief)
├── run_oneshot.py             ← Dictator, Beauty Contest
└── results/                   ← gegenereerde CSV-bestanden
```

## Installatie

### 1. Clone de repository
```bash
git clone https://github.com/<jouw-username>/<repo-naam>.git
cd <repo-naam>
```

### 2. Maak een virtual environment aan
```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate       # Windows
```

### 3. Installeer dependencies
```bash
pip install -r requirements.txt
```

### 4. Configureer API-sleutels
Kopieer `.env.example` naar `.env` en vul je eigen sleutels in:
```bash
cp .env.example .env
# Open .env in een editor en vul de keys in
```

> **Belangrijk:** `.env` staat in `.gitignore` en wordt **nooit** mee gepushed naar GitHub. Verifieer dit altijd voor je `git push` doet.

## Gebruik

### Dry-run (geen API-calls, om de pipeline te testen)
```bash
python run_experiment.py --dry-run
```

### Een klein experiment (voor een eerste test)
```bash
python run_experiment.py \
    --models gpt-4o-mini \
    --games prisoners_dilemma \
    --strategies AC AD \
    --framings neutral \
    --runs 2
```

### Het volledige iteratieve experiment
```bash
python run_experiment.py
```
Dit voert ~1 584 LLM-calls uit (T=0: 6×3×4×2×1×1 = 144; T=1: 6×3×4×2×1×10 = 1 440).

### LLM vs LLM (iteratief)
```bash
# Één specifiek paar (bv. VS vs China)
python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat

# Alle paren uit een lijst van modellen
python run_llm_vs_llm.py --models gpt-4o-mini deepseek-chat claude-haiku

# Dry-run
python run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat --dry-run
```

### One-shot spellen (Dictator, Beauty Contest)
```bash
# Beide one-shot spellen
python run_oneshot.py --models gpt-4o-mini deepseek-chat

# Enkel het Dictator Game
python run_oneshot.py --models gpt-4o-mini --games dictator_game

# Beauty Contest met meer spelers en meer rondes
python run_oneshot.py --models gpt-4o-mini --games beauty_contest \
    --num-players 7 --num-rounds 8

# Dry-run (geen API-calls)
python run_oneshot.py --models gpt-4o-mini --dry-run
```

### Output
Elke run schrijft tijdgestempelde CSV-bestanden in `results/`:
```
results/results_YYYYMMDD_HHMMSS.csv              ← iteratief (LLM vs strategie)
results/results_llmvsllm_YYYYMMDD_HHMMSS.csv     ← LLM vs LLM
results/results_oneshot_dictator_YYYYMMDD_HHMMSS.csv
results/results_oneshot_beauty_YYYYMMDD_HHMMSS.csv
```

**Kolommen — iteratief (`run_experiment.py`):**
| kolom | omschrijving |
|-------|--------------|
| `model` | naam van het LLM |
| `game` | spelnaam |
| `opponent_strategy` | tegenstanderstrategie (AC / AD / TfT / Random / LLM) |
| `framing` | `neutral` of `competitive` |
| `run_id` | nummer van de run binnen deze conditie |
| `round` | rondenummer |
| `llm_action` | `C` (coöpereren) of `D` (defectie) |
| `opponent_action` | actie van de tegenstander |
| `llm_payoff` | payoff voor het LLM in deze ronde |
| `opponent_payoff` | payoff voor de tegenstander |
| `raw_response` | de volledige tekst van het LLM (voor debugging) |
| `temperature` | gebruikte temperatuur (0.7) |

Extra kolommen in `run_llm_vs_llm.py`: `opponent_model`, `perspective` (player1/player2).

**Kolommen — Dictator Game:**
`model`, `game`, `framing`, `run_id`, `amount_shared`, `amount_kept`, `payoff_dictator`, `payoff_receiver`, `raw_response`, `temperature`

**Kolommen — Beauty Contest:**
`model`, `game`, `framing`, `run_id`, `round`, `llm_number`, `random_numbers`, `mean`, `target`, `winner_number`, `llm_won`, `payoff`, `raw_response`, `temperature`, `num_players`, `num_rounds`

## Resultaten en grafieken

Voer `python analyze_results.py` uit om alle analyses en grafieken te genereren. Alle PNG-bestanden worden opgeslagen in `results/`.

### plot1_coop_per_game.png — Coöperatie-rate per model per spel
Toont het percentage rondes waarin elk LLM de coöperatieve actie kiest, gemiddeld over alle tegenstanders en framings. De rode stippellijn is het Nash-evenwicht, de groene stippellijn het menselijk gemiddelde. Hoe hoger de balk, hoe coöperatiever het model.

### plot2_coop_temperature.png — Temperatuurvergelijking T=0 vs T=1
Vergelijkt de coöperatie-rate bij T=0 (deterministisch, 1 ronde) en T=1 (variabel, 10 rondes) per model per spel. Blauwe balken zijn T=0, oranje balken T=1. Een groot verschil tussen T=0 en T=1 betekent dat temperatuur het gedrag sterk beïnvloedt.

### plot3_beauty_contest.png — Beauty Contest: gekozen getal per ronde
Links (T=0): barplot van het gekozen getal per model in de enkele ronde. Rechts (T=1): lijnplot van het gemiddeld gekozen getal per ronde over 20 rondes. De stippellijnen tonen level-k denkniveaus (level 0 = 50, level 1 = 33, level 2 = 22, Nash = 0) en het menselijk gemiddelde (36). Convergentie naar 0 over de rondes wijst op strategisch leren.

### plot4_dictator_game.png — Dictator Game: gemiddeld afgestaan bedrag
Barplot van hoeveel elk model weggeeft van de 100 euro. Nash-evenwicht is 0 euro (rode lijn), menselijk gemiddelde is 28 euro (groene lijn). Modellen die boven de groene lijn zitten zijn genereuzer dan mensen.

### plot5_framing_effect.png — Framing-effect: neutral vs competitive
Toont het verschil in coöperatie-rate tussen neutrale en competitieve framing per model per spel. Groene balken = hogere coöperatie bij neutrale framing. Rode balken = hogere coöperatie bij competitieve framing. Een grote balk betekent dat het model gevoelig is voor hoe de situatie wordt beschreven.

### plot6_llmvsllm_heatmaps.png — LLM vs LLM coöperatie-heatmaps
Heatmaps per spel en temperatuur. Rijen = het model, kolommen = de tegenstander. De kleur toont de coöperatie-rate: donkergroen = altijd coöpereren, donkerrood = altijd defecteren. Bij T=0 is het altijd 0 of 1 omdat er maar 1 ronde is.

### plot7_coop_per_opponent.png — Coöperatie-rate per tegenstander-strategie
Gegroepeerde barplot per spel met de tegenstander (AC, AD, TfT, Random) op de x-as en een balk per model. Toont of LLM's hun gedrag aanpassen aan de strategie van de tegenstander. Een model dat meer coöpereert tegen AC dan tegen AD past zich aan.

### plot8_payoff_evolution.png — Payoff-evolutie over rondes (T=1)
Lijnplot van de gemiddelde payoff per ronde per model per spel, alleen bij T=1. Toont of modellen leren en betere resultaten behalen naarmate het spel vordert. Een stijgende lijn wijst op leergedrag.

## Methodologische keuzes

### Temperatuur
We draaien elk experiment onder **twee temperatuurcondities**:

| Conditie | Temperatuur | Rondes (iteratief) | Rondes (Beauty Contest) | Doel |
|----------|-------------|-------------------|------------------------|------|
| T=0 | 0 (deterministisch) | 1 | 1 | Meet de standaardkeuze van het LLM zonder stochastische variatie |
| T=1 | 1 (maximaal variabel) | 10 | 20 | Meet aanpassing aan de tegenstander en variatie over rondes heen |

Bij T=0 geeft het LLM bij elke call hetzelfde antwoord; bijbijgevolg voegen extra rondes geen informatie toe en volstaat 1 ronde. Bij T=1 kan het LLM zijn strategie aanpassen op basis van de spelgeschiedenis en ontstaat de variatie die nodig is om gedragspatronen te bestuderen.

### Geheugen
Voor elke iteratieve ronde wordt de volledige speelgeschiedenis (alle voorgaande rondes met acties en payoffs) in de prompt geïnjecteerd. Het LLM kan dus patronen herkennen in het gedrag van de tegenstander.

### Aantal runs
- Iteratieve spellen: **1 run** per conditie (= per combinatie model × spel × tegenstander × framing).
- One-shot spellen: **1 run** per conditie.

### Universele actiecodering
Intern werken we met `C` (cooperate) en `D` (defect) labels voor alle spellen, zodat strategieën zoals Tit-for-Tat herbruikbaar zijn over alle spellen heen. De vertaling naar spel-specifieke termen (Stag/Hare, Stop/Go, etc.) gebeurt in `prompts.py`.

## Reproduceerbaarheid

- `random.seed(42)` wordt gezet voor de Random-strategie.
- Elk LLM-antwoord wordt onmiddellijk weggeschreven naar CSV (per ronde, niet per run), zodat een crash of rate limit nooit data verliest.
- Foutieve API-calls worden tot 3x opnieuw geprobeerd voor het experiment doorgaat.

## Licentie

MIT (zie `LICENSE` indien aanwezig).
