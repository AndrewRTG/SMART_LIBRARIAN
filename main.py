import os

from agents import Agent, ModelSettings, Runner, set_default_openai_key
from dotenv import load_dotenv


def configure_openai() -> None:
    """Încarcă și configurează cheia OpenAI."""

    load_dotenv()

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită în fișierul .env."
        )

    set_default_openai_key(api_key)


def main() -> None:
    """Creează și rulează primul agent."""

    configure_openai()

    agent = Agent(
        name="Smart Librarian Assistant",
        instructions=(
            "You are a helpful assistant. "
            "Answer clearly and briefly in the same language as the user."
        ),
        model="gpt-5.6-luna",
        model_settings=ModelSettings(
            max_tokens=200
        ),
    )


    while True:
        user_question = input("Tu: ").strip()

        if user_question.lower() in {"exit", "quit", "stop"}:
            print("\nAgent: La revedere!")
            break

        if not user_question:
            print("Te rog să introduci o întrebare.")
            continue

        result = Runner.run_sync(
            agent,
            user_question,
        )

        print(f"\nAgent: {result.final_output}")


if __name__ == "__main__":
    main()