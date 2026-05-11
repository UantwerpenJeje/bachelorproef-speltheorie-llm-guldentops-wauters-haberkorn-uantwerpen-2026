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

**Iteratief** (LLM vs vaste strategie — `scripts/run_experiment.py`)
- **Prisoner's Dilemma** (1 ronde bij T=0 / 10 rondes bij T=1)
- **Chicken Game** (1 ronde bij T=0 / 10 rondes bij T=1)
- **Stag Hunt** (1 ronde bij T=0 / 10 rondes bij T=1)

**Eenmalig / one-shot** (`scripts/run_oneshot.py`)
- **Dictator Game** — LLM verdeelt 100€; Nash = 0€, mensen ≈ 28€ (1 ronde per run, beide temperaturen)
- **Beauty Contest** — kies een getal 0–100; winnaar = dichtst bij 2/3 × gemiddelde; Nash = 0 (1 ronde bij T=0 / 20 rondes bij T=1)

**LLM vs LLM** (`scripts/run_llm_vs_llm.py`)
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

### Actielabels per spel

In de code gebruiken we universeel `C` en `D` als actielabels zodat strategieën zoals Tit-for-Tat herbruikbaar zijn over alle spellen heen. Maar C/D betekent per spel iets anders:

| Spel | C (cooperate) | D (defect) | Waarom deze mapping? |
|------|--------------|------------|---------------------|
| Prisoner's Dilemma | Zwijgen (samenwerken) | Verraden | Klassiek: C = coöperatie, D = verraad |
| Chicken Game | Stoppen (veilig) | Doorrijden (agressief) | C = toegeven, D = escaleren |
| Stag Hunt | Hert jagen (risicovol maar belonend) | Haas jagen (veilig) | C = risicovolle samenwerking, D = veilige solo-keuze. Let op: "defect" is hier GEEN verraad maar de veilige optie |

> **Belangrijk voor Stag Hunt:** "Cooperation Rate" is hier het percentage dat Hert kiest (de risicovolle maar potentieel meer belonende keuze). "Defect" is het percentage dat voor Haas kiest (de veilige keuze). Dit is een wezenlijk verschil met het Prisoner's Dilemma, waar D echt verraad inhoudt.

De y-as "Cooperation Rate" in alle grafieken betekent dus: het percentage keer dat het model C kiest — wat per spel verschilt in betekenis.

### Framings
- **neutral** – spel wordt beschreven zonder geladen termen, acties zijn `A` / `B`
- **competitive** – expliciete nadruk op winnen en eigen scoremaximalisatie

## Projectstructuur

```
.
├── README.md
├── .gitignore
├── .env.example               ← model voor API-sleutels
├── games/
│   ├── __init__.py             ← package initializer
│   ├── prisoners_dilemma.py    ← payoff-matrix
│   ├── chicken_game.py         ← payoff-matrix
│   ├── stag_hunt.py            ← payoff-matrix
│   ├── dictator_game.py        ← payoff-functie (one-shot)
│   └── beauty_contest.py       ← hulpfuncties (iteratief met feedback)
├── scripts/
│   ├── run_experiment.py       ← LLM vs vaste strategie (iteratief)
│   ├── run_llm_vs_llm.py      ← LLM vs LLM (iteratief)
│   ├── run_oneshot.py          ← Dictator, Beauty Contest
│   └── analyze_results.py      ← analyse en grafieken genereren
├── config_files/
│   ├── config.py               ← centrale configuratie (modellen, runs, etc.)
│   ├── llm_client.py           ← uniforme wrapper rond alle LLM-API's (LiteLLM)
│   ├── prompts.py              ← prompt-templates per spel × framing
│   ├── strategies.py           ← AC, AD, TfT, Random
│   └── requirements.txt        ← Python-dependencies
└── results/
    ├── *.csv                   ← ruwe resultaten
    └── *.png                   ← gegenereerde grafieken
```

## Installatie

### 1. Clone de repository
```bash
git clone https://github.com/UantwerpenJeje/bachelorproef-speltheorie-llm-guldentops-wauters-haberkorn-uantwerpen-2026.git
cd bachelorproef-speltheorie-llm-guldentops-wauters-haberkorn-uantwerpen-2026
```

### 2. Maak een virtual environment aan
```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate       # Windows
```

### 3. Installeer dependencies
```bash
pip install -r config_files/requirements.txt
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
python scripts/run_experiment.py --dry-run
```

### Een klein experiment (voor een eerste test)
```bash
python scripts/run_experiment.py \
    --models gpt-4o-mini \
    --games prisoners_dilemma \
    --strategies AC AD \
    --framings neutral \
    --runs 2
```

### Het volledige iteratieve experiment
```bash
python scripts/run_experiment.py
```
Dit voert ~1 584 LLM-calls uit (T=0: 6×3×4×2×1×1 = 144; T=1: 6×3×4×2×1×10 = 1 440).

### LLM vs LLM (iteratief)
```bash
# Één specifiek paar (bv. VS vs China)
python scripts/run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat

# Alle paren uit een lijst van modellen
python scripts/run_llm_vs_llm.py --models gpt-4o-mini deepseek-chat claude-haiku

# Dry-run
python scripts/run_llm_vs_llm.py --player1 gpt-4o-mini --player2 deepseek-chat --dry-run
```

### One-shot spellen (Dictator, Beauty Contest)
```bash
# Beide one-shot spellen
python scripts/run_oneshot.py --models gpt-4o-mini deepseek-chat

# Enkel het Dictator Game
python scripts/run_oneshot.py --models gpt-4o-mini --games dictator_game

# Beauty Contest met meer spelers en meer rondes
python scripts/run_oneshot.py --models gpt-4o-mini --games beauty_contest \
    --num-players 7 --num-rounds 8

# Dry-run (geen API-calls)
python scripts/run_oneshot.py --models gpt-4o-mini --dry-run
```

### Output
Elke run schrijft tijdgestempelde CSV-bestanden in `results/`:
```
results/results_YYYYMMDD_HHMMSS.csv              ← iteratief (LLM vs strategie)
results/results_llmvsllm_YYYYMMDD_HHMMSS.csv     ← LLM vs LLM
results/results_oneshot_dictator_YYYYMMDD_HHMMSS.csv
results/results_oneshot_beauty_YYYYMMDD_HHMMSS.csv
```

**Kolommen — iteratief (`scripts/run_experiment.py`):**
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

Extra kolommen in `scripts/run_llm_vs_llm.py`: `opponent_model`, `perspective` (player1/player2).

**Kolommen — Dictator Game:**
`model`, `game`, `framing`, `run_id`, `amount_shared`, `amount_kept`, `payoff_dictator`, `payoff_receiver`, `raw_response`, `temperature`

**Kolommen — Beauty Contest:**
`model`, `game`, `framing`, `run_id`, `round`, `llm_number`, `random_numbers`, `mean`, `target`, `winner_number`, `llm_won`, `payoff`, `raw_response`, `temperature`, `num_players`, `num_rounds`

## Resultaten en grafieken

Voer `python scripts/analyze_results.py` uit om alle analyses en grafieken te genereren. Alle PNG-bestanden worden opgeslagen in `results/`.

### plot1_coop_per_game.png — Coöperatie-rate per model per spel
Toont het percentage C-keuzes per model, gemiddeld over **alle** tegenstanders (AC, AD, TfT, Random) én beide framings (neutral + competitive) én beide temperaturen (T=0 en T=1).

Dit gemiddelde maskeert mogelijk grote verschillen: een model dat 100% C speelt tegen AC en 0% tegen AD scoort gemiddeld 50%, net als een model dat altijd 50% C speelt. Zie plot7 voor de uitsplitsing per tegenstander.

- **Error bars** = standaarddeviatie over alle condities (tegenstander × framing × temperatuur), niet over meerdere runs. Ze tonen de spreiding van gedrag *tussen* condities, niet de onzekerheid van een schatting.
- **Referentielijnen:** rood = Nash-evenwicht (rationele voorspelling), groen = menselijk gemiddelde uit de literatuur.
- **Prisoner's Dilemma:** Nash = 0% coöperatie (altijd verraden); menselijk gemiddelde = 68%.
- **Chicken Game:** Nash mixed ≈ 50% stoppen; menselijk gemiddelde = 50%.
- **Stag Hunt:** twee Nash-evenwichten — (C,C) = beide Hert (rode stippellijn boven) en (D,D) = beide Haas (rode stippellijn onder); menselijk gemiddelde = 60% Hert.

### plot2_coop_temperature.png — T=0 vs T=1 vergelijking
Vergelijkt de coöperatie-rate bij T=0 (blauw) en T=1 (oranje) per model per spel.

> **Belangrijk:** T=0 en T=1 zijn niet direct vergelijkbaar. Bij T=0 is er slechts 1 ronde (deterministisch; het model geeft altijd hetzelfde antwoord). Bij T=1 zijn er 10 rondes met geheugen (iteratief; het model kan leren van vorige rondes). Een verschil tussen beide balken kan komen door: (a) de temperatuurinstelling zelf (meer willekeur), (b) het iteratieve karakter (leren van de tegenstander), of (c) beide. Deze effecten zijn in dit experiment niet los te trekken.

Error bars bij T=1 tonen de standaarddeviatie over de condities (tegenstander × framing).

### plot3_beauty_contest.png — Beauty Contest: gekozen getal per ronde
> **Belangrijke context:** het LLM speelt *niet* tegen andere rationele spelers, maar tegen gesimuleerde random spelers die elke ronde een willekeurig getal kiezen (uniform 0–100). Het verwachte gemiddelde van deze spelers is ≈ 50. Daardoor is het optimale antwoord *niet* 0 (het Nash-evenwicht), maar ≈ 33 (= 2/3 × 50). Het Nash-evenwicht van 0 geldt alleen als *alle* spelers rationeel redeneren, wat hier niet het geval is.

- **Links (T=0):** barplot van het gekozen getal per model in de enkele deterministisch ronde. 4 van 6 modellen kiezen 33 — exact level-1-redenering (optimaal tegen random spelers). Llama kiest 46,5 (bijna level-0, nauwelijks strategisch). Grok kiest 10 (overmatig strategisch, suboptimaal tegen random spelers).
- **Rechts (T=1):** lijnplot van het gemiddeld gekozen getal per ronde over 20 rondes. De meeste modellen fluctueren tussen 15 en 40, zonder duidelijke convergentie naar 0 — wat rationeel is, want tegen random spelers is convergeren naar 0 niet optimaal.
- **Referentielijnen:** Level 0 = 50 (geen strategisch denken), Level 1 ≈ 33 (één stap: 2/3 × 50), Level 2 ≈ 22 (twee stappen: (2/3)² × 50), Nash = 0 (oneindig iteratief redeneren), menselijk gemiddelde ronde 1 = 36.

### plot4_dictator_game.png — Dictator Game: gemiddeld afgestaan bedrag
Barplot van hoeveel elk model weggeeft van de 100 euro, gemiddeld over beide framings. Nash-evenwicht = 0 euro (rode lijn): een rationele egoist houdt alles. Menselijk gemiddelde = 28 euro (groene lijn).

Opvallend: bij T=0 geeft GPT-4o-mini 75 euro weg — bijna drie keer zoveel als het menselijk gemiddelde. Alle andere modellen geven 25 euro. Bij T=1 normaliseren alle modellen naar 25 euro (inclusief GPT-4o-mini). De hoge waarde van GPT-4o-mini bij T=0 is mogelijk een artefact van de deterministische decoding. Alle modellen zitten dicht bij het menselijk gemiddelde van 28 euro en ver van het rationele Nash-evenwicht van 0.

### plot5_framing_effect.png — Framing-effect: neutral vs competitive
Toont het *verschil* in coöperatie-rate: (neutraal) minus (competitief).

- **Positieve waarde (groene balk):** het model coöpereert meer bij neutrale framing.
- **Negatieve waarde (rode balk):** het model coöpereert meer bij competitieve framing.

Claude Haiku en GPT-4o-mini zijn het meest framing-gevoelig bij Prisoner's Dilemma en Chicken Game (Δ > 0,6): zij wisselen dramatisch van strategie afhankelijk van hoe de vraag wordt gesteld. Gemini Flash is ook sterk framing-gevoelig bij Chicken Game (Δ > 0,8). DeepSeek is het minst framing-gevoelig over alle spellen heen. Bij Stag Hunt zijn Llama en Grok de enige modellen met een negatief framing-effect (rode balken): zij coöpereren meer bij competitieve framing, wat contra-intuïtief is.

### plot6_llmvsllm_heatmaps.png — LLM vs LLM coöperatie-heatmaps
Elke cel toont de coöperatie-rate (percentage C-keuzes) van het model in de **rij** wanneer het speelt tegen het model in de **kolom**.

- **Bovenste rij (T=0):** slechts 1 ronde, dus waarden zijn binair (0,00 = D gekozen, 1,00 = C gekozen). Dit toont de "standaardkeuze" van elk model ongeacht de tegenstander.
- **Onderste rij (T=1):** gemiddelde over 10 rondes met geheugen. Hier kan het model zich aanpassen aan de tegenstander; waarden tussen 0 en 1 tonen hoe vaak het model coöpereert over die 10 rondes.
- **Kleurschaal:** donkergroen = altijd coöpereren (1,0), donkerrood = altijd defecteren (0,0), geel = gemengd (≈ 0,5).
- De diagonaal (model vs zichzelf) is gevuld — het model speelt tegen een tweede instantie van zichzelf.

### plot7_coop_per_opponent.png — Coöperatie-rate per tegenstander-strategie
Toont per tegenstander (AC, AD, TfT, Random) hoe vaak elk model C kiest, gemiddeld over framings en temperaturen.

Wat we verwachten van een "slim" model: meer C tegen AC (de tegenstander coöpereert altijd, dus samenwerking is veilig), minder C tegen AD (de tegenstander defecteert altijd, dus coöperatie wordt uitgebuit). Een model dat even vaak C speelt tegen AC als tegen AD past zich niet aan.

Bij Stag Hunt zijn de patronen anders: tegen AC (= Always Stag) is C optimaal, tegen AD (= Always Hare) is D optimaal. Sommige modellen — zoals Claude Haiku en Gemini Flash — bereiken 100% C tegen AC bij Stag Hunt, wat optimaal is.

### plot8_payoff_evolution.png — Payoff-evolutie over rondes (T=1)
Lijnplot van de gemiddelde payoff per ronde, alleen bij T=1 (10 rondes met geheugen). Het gemiddelde is over alle tegenstanders (AC, AD, TfT, Random) én beide framings. Dit verklaart de hoge volatiliteit: de ene tegenstander levert hoge payoffs (AC), de andere lage (AD), en het gemiddelde fluctueert sterk.

Er is slechts 1 run per conditie, dus elk datapunt is gebaseerd op 1 enkele ronde tegen 1 tegenstander — er is geen statistische smoothing. Een stijgende trend zou wijzen op leergedrag; in de praktijk is er geen duidelijke trend zichtbaar, wat suggereert dat de modellen niet systematisch leren over de rondes.

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

### Beperkingen van de huidige opzet

- **Één run per conditie.** We kunnen geen betrouwbaarheidsintervallen of statistische tests berekenen. De resultaten tonen één enkele realisatie van het experiment, niet een verwachte waarde.
- **"Cooperation Rate" verschilt per spel in betekenis.** Bij Prisoner's Dilemma is C = samenwerken; bij Stag Hunt is C = de risicovolle keuze (Hert). Zie de sectie "Actielabels per spel" voor de volledige vertaaltabel.
- **Beauty Contest: random tegenstanders, geen rationele agenten.** Het Nash-evenwicht van 0 is daardoor niet het optimale antwoord in dit experiment; 33 (level-1-redenering) is dat wel.
- **Temperatuur en iteratie zijn verweven.** T=0 heeft 1 ronde en T=1 heeft 10 rondes; gemeten verschillen kunnen zowel door de temperatuurinstelling als door het iteratieve karakter (leren van de tegenstander) komen.

## Reproduceerbaarheid

- `random.seed(42)` wordt gezet voor de Random-strategie.
- Elk LLM-antwoord wordt onmiddellijk weggeschreven naar CSV (per ronde, niet per run), zodat een crash of rate limit nooit data verliest.
- Foutieve API-calls worden tot 3x opnieuw geprobeerd voor het experiment doorgaat.

## Licentie

MIT (zie `LICENSE` indien aanwezig).
