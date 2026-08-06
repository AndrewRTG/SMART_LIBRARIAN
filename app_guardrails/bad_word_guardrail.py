import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    TResponseInputItem,
    input_guardrail,
)


BAD_WORDS_FILE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "bad_words.json"
)

# Fișierul de mai sus este sursa unică pentru lista de termeni blocați.
# Păstrăm calea într-o constantă ca să fie ușor de modificat și de testat.


def normalize_text(text: str) -> str:
    """
    Normalizează textul pentru o verificare consistentă.

    Transformă textul în lowercase și elimină diacriticele.
    Asta face căutarea mai robustă: „proastă", „PROASTĂ" și
    „proasta" ajung la aceeași formă internă.
    """

    # casefold() e mai puternic decât lower() pentru comparații textuale.
    lowercase_text = text.casefold()

    # Separăm literele de semnele diacritice, apoi le eliminăm.
    decomposed_text = unicodedata.normalize(
        "NFKD",
        lowercase_text,
    )

    return "".join(
        character
        for character in decomposed_text
        if not unicodedata.combining(character)
    )


@lru_cache(maxsize=1)
def load_bad_words() -> set[str]:
    """
    Citește lista termenilor blocați din JSON.

    Lista este încărcată o singură dată și păstrată în memorie,
    ca să nu citim fișierul la fiecare mesaj primit.
    """

    # Dacă fișierul nu există, preferăm o eroare clară încă de la pornire.
    if not BAD_WORDS_FILE_PATH.exists():
        raise FileNotFoundError(
            "Fișierul cu termeni blocați nu există: "
            f"{BAD_WORDS_FILE_PATH}"
        )

    # JSON-ul trebuie să conțină o listă simplă de stringuri.
    with BAD_WORDS_FILE_PATH.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        bad_words = json.load(file)

    if not isinstance(bad_words, list):
        raise ValueError(
            "bad_words.json trebuie să conțină o listă."
        )

    normalized_words: set[str] = set()

    for word in bad_words:
        # Nu acceptăm valori goale sau tipuri neașteptate.
        if not isinstance(word, str) or not word.strip():
            raise ValueError(
                "Fiecare termen din bad_words.json "
                "trebuie să fie un text valid."
            )

        # Salvează forma normalizată ca să comparăm mereu în același mod.
        normalized_words.add(
            normalize_text(word.strip())
        )

    return normalized_words


def find_bad_words(text: str) -> list[str]:
    """
    Returnează termenii nepotriviți găsiți în text.

    Verificarea caută cuvinte complete, nu fragmente aflate
    în interiorul altor cuvinte.
    """

    # Înainte de căutare, aducem mesajul utilizatorului în aceeași formă.
    normalized_text = normalize_text(text)
    detected_words: list[str] = []

    # Parcurgem fiecare termen interzis și verificăm dacă apare ca token separat.
    for bad_word in load_bad_words():
        pattern = (
            rf"(?<!\w)"
            rf"{re.escape(bad_word)}"
            rf"(?!\w)"
        )

        if re.search(pattern, normalized_text):
            detected_words.append(bad_word)

    return sorted(detected_words)


def convert_input_to_text(
    agent_input: str | list[TResponseInputItem],
) -> str:
    """
    Transformă inputul agentului într-un singur text.

    Uneori guardrail-ul primește un string simplu, alteori primește o listă
    de itemi de conversație. Funcția uniformizează ambele cazuri.
    """

    if isinstance(agent_input, str):
        return agent_input

    # Convertim fiecare element la text și îl lipim într-un singur mesaj.
    return " ".join(
        str(item)
        for item in agent_input
    )


@input_guardrail(
    name="bad_word_guardrail",
    run_in_parallel=False,
)
async def bad_word_guardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    """
    Oprește execuția dacă mesajul conține termeni nepotriviți.

    Dacă nu găsește nimic, mesajul trece mai departe către agent.
    Dacă găsește cel puțin un termen interzis, guardrail-ul ridică tripwire.
    """

    # 1) Convertim orice format de input într-un text simplu.
    input_text = convert_input_to_text(input)

    # 2) Căutăm termenii blocați în textul normalizat.
    detected_words = find_bad_words(input_text)

    # 3) Raportăm rezultatul către runtime-ul agentului.
    return GuardrailFunctionOutput(
        output_info={
            "detected_words": detected_words,
        },
        tripwire_triggered=bool(detected_words),
    )