# Speltheoretisch gedrag van Large Language Models

Code horend bij de bachelorproef *"Het speltheoretisch gedrag van Large Language Models: een vergelijking met rationele en menselijke beslissers"* (Universiteit Antwerpen, Faculteit Bedrijfswetenschappen en Economie, academiejaar 2025-2026).

**Auteurs:** Stef Guldentops, Milan Wauters, Jérémie Haberkorn
**Promotor:** Prof. dr. David Martens
**Begeleider:** Wannes Van den Bulck

## Wat doet deze code?

Deze code voert geautomatiseerde experimenten uit waarin verschillende Large Language Models (LLMs) iteratieve speltheoretische spellen spelen tegen vaste tegenstanderstrategieën. Het doel is hun keuzes te vergelijken met:
1. de rationele oplossing volgens de speltheorie (Nash-evenwicht)
2. empirisch waargenomen menselijk gedrag uit de literatuur

### Onderzochte spellen (iteratief)
- **Prisoner's Dilemma** (50 rondes per run)
- **Chicken Game** (20 rondes per run)
- **Stag Hunt** (20 rondes per run)

> Eenmalige spellen (Dictator Game, Ultimatum Game, Beauty Contest) komen in een aparte module.

### Onderzochte modellen
| Model | Provider | LiteLLM-string |
|-------|----------|----------------|
| GPT-4o-mini | OpenAI (VS) | `gpt-4o-mini` |
| Claude Haiku 4.5 | Anthropic (VS) | `anthropic/claude-haiku-4-5` |
| Gemini 2.0 Flash | Google (VS) | `gemini/gemini-2.0-flash` |
| DeepSeek-V3 | DeepSeek (China) | `deepseek/deepseek-chat` |
| Llama 3.1 8B | Meta via Groq | `groq/llama-3.1-8b-instant` |

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
├── prompts.py                 ← prompt-templates per spel × framing
├── games/
│   ├── prisoners_dilemma.py   ← payoff-matrix
│   ├── chicken_game.py        ← payoff-matrix
│   └── stag_hunt.py           ← payoff-matrix
├── run_experiment.py          ← hoofdscript dat alles orkestreert
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

### Het volledige experiment
```bash
python run_experiment.py
```
Dit voert ~10 000 LLM-calls uit. Reken op enkele uren afhankelijk van je rate limits.

### Output
Elke run schrijft een tijdgestempeld CSV-bestand in `results/`:
```
results/results_YYYYMMDD_HHMMSS.csv
```

Kolommen:
| kolom | omschrijving |
|-------|--------------|
| `model` | naam van het LLM |
| `game` | spelnaam |
| `opponent_strategy` | tegenstanderstrategie |
| `framing` | `neutral` of `competitive` |
| `run_id` | nummer van de run binnen deze conditie |
| `round` | rondenummer |
| `llm_action` | `C` (coöpereren) of `D` (defectie) |
| `opponent_action` | actie van de tegenstander |
| `llm_payoff` | payoff voor het LLM in deze ronde |
| `opponent_payoff` | payoff voor de tegenstander |
| `raw_response` | de volledige tekst van het LLM (voor debugging) |
| `temperature` | gebruikte temperatuur (0.7) |

## Methodologische keuzes

### Temperatuur
We gebruiken `temperature=0.7` (niet 0). Bij T=0 zou een deterministisch tegenstandermodel (AC, AD, TfT) altijd dezelfde geschiedenis genereren, en zouden de 10 runs identiek zijn. Bij T=0.7 ontstaat realistische variatie tussen runs, wat toelaat om gemiddelden en standaardafwijkingen te berekenen.

### Geheugen
Voor elke iteratieve ronde wordt de volledige speelgeschiedenis (alle voorgaande rondes met acties en payoffs) in de prompt geïnjecteerd. Het LLM kan dus patronen herkennen in het gedrag van de tegenstander.

### Aantal runs
- Iteratieve spellen: **10 runs** per conditie (= per combinatie model × spel × tegenstander × framing).
- Per spel × tegenstander × framing levert dit 10 datapunten op om gemiddelden en standaarddeviaties te berekenen.

### Universele actiecodering
Intern werken we met `C` (cooperate) en `D` (defect) labels voor alle spellen, zodat strategieën zoals Tit-for-Tat herbruikbaar zijn over alle spellen heen. De vertaling naar spel-specifieke termen (Stag/Hare, Stop/Go, etc.) gebeurt in `prompts.py`.

## Reproduceerbaarheid

- `random.seed(42)` wordt gezet voor de Random-strategie.
- Elk LLM-antwoord wordt onmiddellijk weggeschreven naar CSV (per ronde, niet per run), zodat een crash of rate limit nooit data verliest.
- Foutieve API-calls worden tot 3x opnieuw geprobeerd voor het experiment doorgaat.

## Licentie

MIT (zie `LICENSE` indien aanwezig).
