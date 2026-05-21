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

De grafieken worden gegenereerd via `python scripts/analyze_results.py` en opgeslagen als PNG in `results/`.

### plot1_coop_per_game.png — Coöperatie-rate per model per spel
Percentage C-keuzes per model, gemiddeld over alle tegenstanders (AC, AD, TfT, Random), beide framings en beide temperaturen.

Let op: dit gemiddelde kan grote verschillen maskeren. Een model dat 100% C speelt tegen AC maar 0% tegen AD scoort gemiddeld hetzelfde als een model dat altijd 50% C kiest — terwijl het gedrag fundamenteel anders is. Plot7 geeft de uitsplitsing per tegenstander.

- **Error bars** = standaarddeviatie over alle condities (tegenstander × framing × temperatuur); ze tonen spreiding *tussen* condities, niet statistische onzekerheid.
- **Referentielijnen:** rood = Nash-evenwicht, groen = menselijk gemiddelde uit de literatuur.
- **Prisoner's Dilemma:** Nash = 0%, menselijk gemiddelde = 68%.
- **Chicken Game:** Nash mixed ≈ 50%, menselijk gemiddelde = 50%.
- **Stag Hunt:** twee Nash-evenwichten — (C,C) bovenste rode lijn, (D,D) onderste; menselijk gemiddelde = 60% Hert.

### plot2_coop_temperature.png — T=0 vs T=1 vergelijking
Vergelijkt coöperatie-rate bij T=0 (blauw) en T=1 (oranje) per model per spel.

T=0 en T=1 zijn niet één-op-één vergelijkbaar: bij T=0 is er één deterministische ronde, bij T=1 zijn er 10 rondes met geheugen. Verschillen tussen beide balken kunnen dus zowel door de temperatuurinstelling zelf komen als door het iteratieve karakter — die twee effecten zijn hier niet van elkaar los te trekken.

Error bars bij T=1 = standaarddeviatie over tegenstander × framing.

### plot3_beauty_contest.png — Beauty Contest: gekozen getal per ronde
Het LLM speelt hier niet tegen rationele spelers maar tegen gesimuleerde random spelers (uniform 0–100). Het gemiddelde van die spelers is ≈ 50, dus het optimale antwoord is ≈ 33 (= 2/3 × 50) — niet 0. Nash = 0 geldt alleen als alle spelers rationeel redeneren.

- **Links (T=0):** 4 van 6 modellen kiezen precies 33 (level-1-redenering). Llama kiest 46,5 (nauwelijks strategisch), Grok kiest 10 (te ver doorgedacht voor random tegenstanders).
- **Rechts (T=1):** de meeste modellen schommelen tussen 15 en 40 over 20 rondes, zonder duidelijke convergentie richting 0 — wat eigenlijk rationeel is in deze opzet.
- **Referentielijnen:** Level 0 = 50, Level 1 ≈ 33, Level 2 ≈ 22, Nash = 0, menselijk gemiddelde ronde 1 = 36.

### plot4_dictator_game.png — Dictator Game: gemiddeld afgestaan bedrag
Hoeveel elk model weggeeft van 100 euro, gemiddeld over beide framings. Nash = 0 euro (rode lijn), menselijk gemiddelde = 28 euro (groene lijn).

Bij T=0 geeft GPT-4o-mini 75 euro weg — bijna drie keer het menselijk gemiddelde. De andere modellen geven allemaal 25 euro. Bij T=1 normaliseren alle modellen naar 25 euro. De hoge waarde van GPT-4o-mini bij T=0 is waarschijnlijk een artefact van deterministische decoding. Alle modellen zitten dicht bij het menselijk gemiddelde en ver van het Nash-evenwicht van 0.

### plot5_framing_effect.png — Framing-effect: neutral vs competitive
Verschil in coöperatie-rate: (neutraal) − (competitief).

- **Positief (groen):** model coöpereert meer bij neutrale framing.
- **Negatief (rood):** model coöpereert meer bij competitieve framing.

Claude Haiku en GPT-4o-mini zijn het sterkst framing-gevoelig bij Prisoner's Dilemma en Chicken Game (Δ > 0,6). DeepSeek reageert het minst op de framing. Bij Stag Hunt hebben Llama en Grok een negatief effect: zij coöpereren meer bij competitieve framing, wat tegen de verwachting in gaat.

### plot6_llmvsllm_heatmaps.png — LLM vs LLM coöperatie-heatmaps
Elke cel = coöperatie-rate van het model in de rij tegen het model in de kolom.

- **T=0 (boven):** 1 ronde, dus binaire waarden (0,00 of 1,00) — de standaardkeuze van elk model.
- **T=1 (onder):** gemiddelde over 10 rondes; het model kan zich aanpassen aan de tegenstander.
- **Kleurschaal:** donkergroen = altijd C, donkerrood = altijd D, geel = gemengd.
- De diagonaal is ingevuld — elk model speelt tegen een tweede instantie van zichzelf.

### plot7_coop_per_opponent.png — Coöperatie-rate per tegenstander-strategie
Per tegenstander (AC, AD, TfT, Random) hoe vaak elk model C kiest, gemiddeld over framings en temperaturen.

Een model dat zich aanpast zou meer C moeten spelen tegen AC (veilig om samen te werken) en minder C tegen AD (samenwerken wordt uitgebuit). Een model dat tegen beide even vaak C speelt, past zich dus niet aan de tegenstander aan.

Bij Stag Hunt loopt de logica anders: tegen AC is C optimaal, tegen AD is D optimaal. Claude Haiku en Gemini Flash halen 100% C tegen AC bij Stag Hunt — dat is de optimale respons.

### plot8_payoff_evolution.png — Payoff-evolutie over rondes (T=1)
Gemiddelde payoff per ronde bij T=1, over alle tegenstanders en framings. De hoge volatiliteit komt doordat de payoffs sterk verschillen per tegenstander: AC levert hoge payoffs, AD lage.

Elk datapunt is gebaseerd op 1 enkele run per conditie, dus er is geen statistische smoothing. Een stijgende trend zou op leergedrag wijzen; in de praktijk is die trend niet zichtbaar.

## Methodologische keuzes

### Temperatuur
Elk experiment wordt uitgevoerd onder twee temperatuurcondities:

| Conditie | Temperatuur | Rondes (iteratief) | Rondes (Beauty Contest) | Doel |
|----------|-------------|-------------------|------------------------|------|
| T=0 | 0 (deterministisch) | 1 | 1 | Standaardkeuze van het LLM zonder willekeur |
| T=1 | 1 (maximaal variabel) | 10 | 20 | Aanpassing aan tegenstander en variatie over rondes |

Bij T=0 is het antwoord deterministisch; extra rondes voegen dan niets toe. Bij T=1 kan het model zijn strategie bijsturen op basis van de spelgeschiedenis.

### Geheugen
Per iteratieve ronde wordt de volledige speelgeschiedenis (alle vorige acties en payoffs) in de prompt gezet. Het model heeft dus zicht op wat de tegenstander deed en kan zijn gedrag daarop afstemmen.

### Aantal runs
Zowel voor iteratieve als one-shot spellen: **1 run** per conditie (combinatie van model × spel × tegenstander × framing).

### Universele actiecodering
Intern gebruiken we `C` en `D` voor alle spellen zodat strategieën zoals Tit-for-Tat herbruikbaar zijn. De vertaling naar spel-specifieke bewoordingen (Stag/Hare, Stop/Go, …) zit in `prompts.py`.

### Beperkingen

- **1 run per conditie** — geen betrouwbaarheidsintervallen of statistische tests mogelijk. De resultaten zijn één realisatie van het experiment.
- **"Cooperation Rate" heeft per spel een andere betekenis.** Bij Prisoner's Dilemma is C samenwerken; bij Stag Hunt is C de risicovolle keuze (Hert). Zie de sectie "Actielabels per spel" hierboven.
- **Beauty Contest: random tegenstanders.** Nash = 0 is hier niet het optimale antwoord; level-1-redenering (≈ 33) is dat wel.
- **Temperatuur en iteratie zijn niet los te trekken.** T=0 heeft 1 ronde, T=1 heeft 10. Verschillen kunnen zowel door de temperatuurinstelling als door het iteratieve leerproces komen.

## Reproduceerbaarheid

- `random.seed(42)` voor de Random-strategie.
- Resultaten worden per ronde naar CSV geschreven, niet pas aan het einde van een run — een crash of rate limit verliest dus maximaal één ronde data.
- Mislukte API-calls worden tot 3x opnieuw geprobeerd.

## Licentie

MIT (zie `LICENSE` indien aanwezig).
