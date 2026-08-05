from agents import Agent, ModelSettings

from config import MODEL_NAME
from models import IntentDecision


def create_intent_agent() -> Agent:
    """
    Creează agentul care clasifică intenția utilizatorului.
    """

    return Agent(
        name="Smart Librarian Intent Router",
        instructions=(
            "Clasifică mesajul utilizatorului într-una dintre "
            "următoarele categorii:\n\n"

            "1. new_recommendation:\n"
            "- utilizatorul cere o recomandare nouă;\n"
            "- descrie teme, genuri sau preferințe;\n"
            "- cere o altă carte.\n\n"

            "2. follow_up:\n"
            "- utilizatorul cere explicații despre cartea curentă;\n"
            "- folosește formulări precum «de ce?», "
            "«de ce ai ales asta?», «spune-mi mai multe»;\n"
            "- nu solicită o carte nouă.\n\n"

            "3. exact_title_summary:\n"
            "- utilizatorul cere informații sau rezumat pentru "
            "un titlu numit explicit;\n"
            "- exemple: «Ce este 1984?», "
            "«Dă-mi rezumatul pentru The Hobbit».\n\n"

            "4. other:\n"
            "- mesajul nu are legătură cu recomandarea "
            "sau rezumatul unei cărți.\n\n"

            "Pentru exact_title_summary, pune titlul în câmpul title. "
            "Pentru celelalte categorii, title trebuie să fie șir gol.\n\n"

            "Reguli de prioritate:\n"
            "- Dacă utilizatorul întreabă de ce a fost aleasă sau "
            "recomandată o carte, clasifică drept follow_up, chiar "
            "dacă menționează titlul.\n"
            "- exact_title_summary se folosește când utilizatorul "
            "cere informații sau rezumat despre un titlu.\n"
            "- Formulări precum «de ce ai ales Harry Potter?» sunt "
            "follow_up.\n\n"

            "Reguli pentru referințe conversaționale:\n"
            "- Dacă există o carte curentă, expresii precum "
            "«această carte», «cartea», «ea», "
            "«despre ce este vorba?», «care este tema principală?» "
            "și «cine este personajul principal?» sunt follow_up.\n"
            "- Nu clasifica drept other un mesaj care folosește "
            "o referință la cartea curentă."
        ),
        model=MODEL_NAME,
        model_settings=ModelSettings(
            max_tokens=150,
        ),
        output_type=IntentDecision,
    )