from agents import Agent, ModelSettings

from config import MODEL_NAME


def create_follow_up_agent() -> Agent:
    """
    Creează agentul care răspunde despre cartea curentă.
    """

    return Agent(
        name="Smart Librarian Follow-up Agent",
        instructions=(
            "Răspunde strict la întrebarea utilizatorului despre "
            "cartea curentă. "
            "Nu recomanda o altă carte. "
            "Nu începe răspunsul cu «Îți recomand». "
            "Nu repeta rezumatul complet decât dacă utilizatorul "
            "îl cere explicit. "
            "Folosește numai contextul furnizat de aplicație. "
            "Răspunde în limba utilizatorului."
        ),
        model=MODEL_NAME,
        model_settings=ModelSettings(
            max_tokens=300,
        ),
    )