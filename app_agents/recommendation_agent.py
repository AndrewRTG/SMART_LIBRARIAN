from agents import Agent, ModelSettings

from config import MODEL_NAME
from models import BookRecommendation


def create_recommendation_agent() -> Agent:
    """
    Creează agentul care selectează o carte din rezultatele RAG.
    """

    return Agent(
        name="Smart Librarian Recommendation Agent",
        instructions=(
            "Ești un bibliotecar AI. "
            "Primești întrebarea utilizatorului și câteva cărți "
            "găsite printr-o căutare semantică în ChromaDB. "
            "Alege exact o singură carte dintre rezultatele primite. "
            "Nu inventa alte titluri. "
            "Copiază titlul exact așa cum apare în context. "
            "Explică pe scurt de ce se potrivește intereselor "
            "utilizatorului. "
            "Răspunde în limba utilizatorului."
        ),
        model=MODEL_NAME,
        model_settings=ModelSettings(
            max_tokens=400,
        ),
        output_type=BookRecommendation,
    )