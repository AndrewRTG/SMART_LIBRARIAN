from agents import Agent, ModelSettings

from config import IMAGE_AGENT_MODEL


def create_image_generation_agent() -> Agent:
    """
    Creează agentul care construiește promptul vizual.
    """

    return Agent(
        name="Smart Librarian Image Prompt Agent",
        instructions=(
            "Ești un agent specializat în construirea prompturilor "
            "pentru generarea imaginilor inspirate de cărți.\n\n"

            "Primești titlul cărții, rezumatul și cerința "
            "utilizatorului.\n\n"

            "Returnează numai promptul vizual final, fără JSON, "
            "fără Markdown, fără explicații și fără introduceri.\n\n"

            "Promptul trebuie să aibă între 80 și 140 de cuvinte "
            "și să descrie:\n"
            "- subiectul principal;\n"
            "- decorul;\n"
            "- atmosfera;\n"
            "- iluminarea;\n"
            "- paleta vizuală;\n"
            "- perspectiva și compoziția;\n"
            "- stilul vizual cerut.\n\n"

            "Respectă modificările utilizatorului. "
            "Când cere o altă imagine, propune o compoziție "
            "substanțial diferită.\n\n"

            "Imaginea trebuie să fie originală. "
            "Nu copia o copertă existentă. "
            "Nu include titlul cărții, numele autorului, "
            "logo-uri, watermark-uri sau text lizibil."

        ),
        model=IMAGE_AGENT_MODEL,
        model_settings=ModelSettings(
            max_tokens=1200,
        ),
    )