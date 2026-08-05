import os

from agents import set_default_openai_key
from dotenv import load_dotenv


MODEL_NAME = "gpt-5.6-luna"


def configure_openai() -> None:
    """
    Încarcă cheia API și configurează OpenAI Agents SDK.
    """

    load_dotenv()

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită în fișierul .env."
        )

    set_default_openai_key(api_key)