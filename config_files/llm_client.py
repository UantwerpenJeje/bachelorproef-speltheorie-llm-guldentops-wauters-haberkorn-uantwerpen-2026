"""
llm_client.py
=============
Eén functie om met alle 5 LLM-providers te praten via LiteLLM.

LiteLLM vertaalt elke API-call naar het juiste formaat per provider,
zodat we ons geen zorgen hoeven te maken over de verschillen tussen
OpenAI, Anthropic, Gemini, DeepSeek en Groq.

Gebruik:
    from llm_client import call_llm
    answer = call_llm("gpt-4o-mini", "Hallo, hoe gaat het?")
"""

import os
import time
from dotenv import load_dotenv
from litellm import completion

# API-sleutels uit .env-bestand laden (zie .env.example)
load_dotenv()

# Maximaal aantal pogingen bij netwerk- of rate limit fouten
MAX_RETRIES = 3
RETRY_DELAY_SEC = 5


def call_llm(
    model: str,
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 200,
    system_prompt: str = None,
) -> str:
    """
    Verstuurt een prompt naar het opgegeven model en geeft het antwoord terug.

    Parameters
    ----------
    model : str
        LiteLLM-modelstring, bv. "gpt-4o-mini" of "anthropic/claude-haiku-4-5".
    prompt : str
        De gebruikersprompt (de eigenlijke vraag).
    temperature : float
        Variatie in de output (0 = deterministisch, 1 = maximaal variabel).
    max_tokens : int
        Maximaal aantal tokens dat het model mag genereren. 200 is ruim
        voldoende voor één-letter antwoorden zoals 'A' of 'B'.
    system_prompt : str, optional
        Optionele system prompt om het gedrag van het model te kaderen.

    Returns
    -------
    str
        Het tekstantwoord van het model, zonder leading/trailing whitespace.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Retry-loop voor het geval een API tijdelijk traag is of we tegen een
    # rate limit aanlopen.
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                print(f"  [warning] {model}: {e} -- retrying in {RETRY_DELAY_SEC}s...")
                time.sleep(RETRY_DELAY_SEC)

    # Alle pogingen hebben gefaald
    raise RuntimeError(
        f"Failed to call {model} after {MAX_RETRIES} attempts. Last error: {last_error}"
    )
