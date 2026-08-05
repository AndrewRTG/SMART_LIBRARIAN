from agents import Agent, ModelSettings

from app_tools.book_tools import get_summary_by_title
from config import MODEL_NAME


def create_summary_agent() -> Agent:
    """
    Creează agentul care apelează tool-ul pentru rezumat.
    """

    return Agent(
        name="Book Summary Tool Agent",
        instructions=(
            "Apelează get_summary_by_title exact o dată, "
            "folosind titlul exact primit. "
            "Nu genera rezumatul din propriile cunoștințe."
        ),
        model=MODEL_NAME,
        model_settings=ModelSettings(
            max_tokens=800,
            tool_choice="get_summary_by_title",
        ),
        tools=[get_summary_by_title],
        tool_use_behavior="stop_on_first_tool",
    )