import asyncio
import os

from agents import (
    Agent,
    ModelSettings,
    Runner,
    set_default_openai_key,
)
from dotenv import load_dotenv
from book_summaries import get_summary_by_title


def configure_openai() -> None:
    """Încarcă cheia API."""

    load_dotenv()

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită în fișierul .env."
        )

    set_default_openai_key(api_key)


async def main() -> None:

    configure_openai()

    agent = Agent(
        name="Smart Librarian Assistant",
        instructions=(
        "You are a book assistant. "
        "For every request about a book or its summary, "
        "use the get_summary_by_title tool. "
        "Never generate or rewrite the summary yourself."
        ),
        model="gpt-5.6-luna",
        model_settings=ModelSettings(
            max_tokens=800,
            tool_choice="get_summary_by_title",
        ),
        tools=[get_summary_by_title],
        tool_use_behavior="stop_on_first_tool",
    )

    previous_response_id = None

    print("=" * 50)
    print("Smart Librarian Assistant")
    print("Agentul păstrează contextul conversației.")
    print("Scrie 'exit' pentru închidere.")
    print("Scrie 'reset' pentru a șterge memoria conversației.")
    print("=" * 50)

    while True:
        user_question = input("\nTu: ").strip()

        if user_question.lower() in {"exit", "quit", "stop"}:
            print("\nAgent: La revedere!")
            break

        if user_question.lower() == "reset":
            previous_response_id = None
            print("\nAgent: Memoria conversației a fost resetată.")
            continue

        if not user_question:
            print("\nAgent: Te rog să introduci o întrebare.")
            continue

        try:
            if previous_response_id is None:
                result = await Runner.run(
                    agent,
                    user_question,
                )

            else:
                result = await Runner.run(
                    agent,
                    user_question,
                    previous_response_id=previous_response_id,
                )

            previous_response_id = result.last_response_id

            print(f"\nAgent: {result.final_output}")

        except Exception as error:
            print("\nAgent: A apărut o eroare.")
            print(f"Tip eroare: {type(error).__name__}")
            print(f"Mesaj: {error}")


if __name__ == "__main__":
    asyncio.run(main())