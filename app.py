from config import configure_openai
from services.librarian_service import SmartLibrarianService
from agents import InputGuardrailTripwireTriggered


async def main() -> None:
    """
    Pornește interfața CLI Smart Librarian.
    """

    configure_openai()

    librarian = SmartLibrarianService()

    print("=" * 60)
    print("Smart Librarian – RAG + Tool Calling")
    print("Scrie 'exit' pentru închidere.")
    print("Scrie 'reset' pentru resetarea memoriei.")
    print("=" * 60)

    while True:
        user_question = input("\nTu: ").strip()

        if user_question.lower() in {
            "exit",
            "quit",
            "stop",
        }:
            print("\nAgent: La revedere!")
            break

        if user_question.lower() == "reset":
            librarian.reset()
            print(
                "\nAgent: Memoria conversației "
                "a fost resetată."
            )
            continue

        if not user_question:
            print(
                "\nAgent: Te rog să introduci "
                "o întrebare."
            )
            continue

        try:
            response = await librarian.process_message(
                user_question
            )

            print(f"\nAgent: {response}")

        except InputGuardrailTripwireTriggered:
            print(
                "\nAgent: Te rog să folosești un limbaj "
                "respectuos. Mesajul nu a fost procesat."
            )

        except TimeoutError:
            print(
                "\nAgent: Cererea a durat prea mult. "
                "Te rog să încerci din nou."
            )

        except Exception as error:
            print("\nAgent: A apărut o eroare.")
            print(
                f"Tip eroare: "
                f"{type(error).__name__}"
            )
            print(f"Mesaj: {error}")