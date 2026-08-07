import os

from agents import (
    set_default_openai_key,
    set_tracing_disabled,
)
from dotenv import load_dotenv


MODEL_NAME = "gpt-5.6-luna"
IMAGE_AGENT_MODEL = MODEL_NAME
IMAGE_MODEL_NAME = "gpt-image-1"


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

    set_default_openai_key(
        api_key,
        use_for_tracing=False,
    )

    # Dezactivează tracing-ul global pentru aplicație.
    set_tracing_disabled(True)