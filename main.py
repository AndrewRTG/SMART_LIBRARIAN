import asyncio
import os
from typing import Any, Literal

from agents import (
    Agent,
    ModelSettings,
    Runner,
    set_default_openai_key,
)
from dotenv import load_dotenv
from pydantic import BaseModel

from book_summaries import (
    book_summaries_dict,
    get_summary_by_title,
)
from vector_store import retrieve_books


class BookRecommendation(BaseModel):
    """
    Structura recomandării returnate de agent.
    """

    title: str
    reason: str


class IntentDecision(BaseModel):
    """
    Clasifică mesajul utilizatorului înainte de executarea fluxului.
    """

    intent: Literal[
        "new_recommendation",
        "follow_up",
        "exact_title_summary",
        "other",
    ]

    # Trebuie să fie titlu exact sau șir gol.
    title: str


def configure_openai() -> None:
    """
    Încarcă cheia API din fișierul .env.
    """

    load_dotenv()

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită în fișierul .env."
        )

    set_default_openai_key(api_key)


def build_rag_context(
    retrieved_books: list[dict[str, Any]],
) -> str:
    """
    Transformă rezultatele ChromaDB într-un context pentru agent.
    """

    context_parts = []

    for book in retrieved_books:
        context_parts.append(
            f"Titlu exact: {book['title']}\n"
            f"Conținut: {book['document']}"
        )

    return "\n\n".join(context_parts)


def validate_recommended_title(
    recommended_title: str,
    retrieved_books: list[dict[str, Any]],
) -> str:
    """
    Verifică dacă titlul recomandat provine din rezultatele ChromaDB.

    Returnează forma exactă a titlului din metadata ChromaDB.
    """

    normalized_recommendation = recommended_title.strip().lower()

    for book in retrieved_books:
        exact_title = book["title"]

        if exact_title.lower() == normalized_recommendation:
            return exact_title

    available_titles = [
        book["title"]
        for book in retrieved_books
    ]

    raise ValueError(
        "Agentul a recomandat un titlu care nu provine din retriever. "
        f"Titluri permise: {available_titles}"
    )


async def main() -> None:
    """
    Rulează Smart Librarian cu RAG, memorie și tool calling.
    """

    configure_openai()

    

    intent_agent = Agent(
        name="Smart Librarian Intent Router",
        instructions=(
            "Clasifică mesajul utilizatorului într-una dintre următoarele categorii:\n"
            "\n"
            "1. new_recommendation:\n"
            "- utilizatorul cere o recomandare nouă;\n"
            "- descrie teme, genuri sau preferințe;\n"
            "- cere o altă carte.\n"
            "\n"
            "2. follow_up:\n"
            "- utilizatorul cere explicații despre ultima recomandare;\n"
            "- folosește formulări precum «de ce?», «de ce ai ales asta?», "
            "«spune-mi mai multe despre ea?»;\n"
            "- nu solicită o carte nouă.\n"
            "\n"
            "3. exact_title_summary:\n"
            "- utilizatorul cere informații sau rezumat pentru un titlu numit explicit;\n"
            "- exemple: «Ce este 1984?», «Dă-mi rezumatul pentru The Hobbit».\n"
            "\n"
            "4. other:\n"
            "- mesajul nu are legătură cu recomandarea sau rezumatul unei cărți.\n"
            "\n"
            "Pentru exact_title_summary, pune titlul în câmpul title. "
            "Pentru celelalte categorii, title trebuie să fie șir gol.\n"
            "Reguli de prioritate:\n"
            "- Dacă utilizatorul întreabă de ce a fost aleasă sau recomandată o carte, "
            "clasifică mesajul drept follow_up, chiar dacă menționează explicit titlul.\n"
            "- exact_title_summary se folosește numai când utilizatorul cere informații "
            "despre carte sau rezumatul ei, nu când cere motivul recomandării.\n"
            "- Formulări precum «de ce ai ales Harry Potter?» sau "
            "«de ce mi-ai recomanda această carte?» sunt follow_up.\n"
            "Reguli pentru referințe conversaționale:\n"
            "- Dacă există o carte curentă în context, expresii precum "
            "«această carte», «cartea», «ea», «despre ce este vorba?», "
            "«care este tema principală?», «cine este personajul principal?» "
            "și «spune-mi mai multe» sunt follow_up.\n"
            "- Dacă utilizatorul întreabă de ce a fost aleasă sau recomandată "
            "cartea curentă, clasifică drept follow_up.\n"
            "- exact_title_summary se folosește când utilizatorul numește un titlu "
            "și cere informații sau rezumat despre acel titlu.\n"
            "- Nu clasifica un mesaj drept other doar pentru că folosește pronume "
            "sau expresii precum «această carte», dacă există o carte curentă."
        ),
        model="gpt-5.6-luna",
        model_settings=ModelSettings(
            max_tokens=150,
        ),
        output_type=IntentDecision,
    )



    follow_up_agent = Agent(
    name="Smart Librarian Follow-up Agent",
    instructions=(
        "Răspunde strict la întrebarea utilizatorului despre cartea curentă. "
        "Nu recomanda o altă carte. "
        "Nu începe răspunsul cu «Îți recomand». "
        "Nu repeta rezumatul complet decât dacă utilizatorul îl cere explicit. "
        "Folosește numai contextul furnizat de aplicație. "
        "Răspunde în limba utilizatorului."
    ),
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        max_tokens=300,
    ),
)



    recommendation_agent = Agent(
        name="Smart Librarian Recommendation Agent",
        instructions=(
            "Ești un bibliotecar AI. "
            "Primești întrebarea utilizatorului și câteva cărți găsite "
            "printr-o căutare semantică în ChromaDB. "
            "Alege exact o singură carte dintre rezultatele primite. "
            "Nu inventa alte titluri. "
            "Copiază titlul exact așa cum apare în context. "
            "Explică pe scurt de ce se potrivește intereselor utilizatorului. "
            "Răspunde în limba utilizatorului."
        ),
        model="gpt-5.6-luna",
        model_settings=ModelSettings(
            max_tokens=400,
        ),
        output_type=BookRecommendation,
    )

    summary_agent = Agent(
        name="Book Summary Tool Agent",
        instructions=(
            "Trebuie să apelezi get_summary_by_title exact o dată, "
            "folosind titlul exact primit. "
            "Nu genera rezumatul din propriile cunoștințe."
        ),
        model="gpt-5.6-luna",
        model_settings=ModelSettings(
            max_tokens=800,
            tool_choice="get_summary_by_title",
        ),
        tools=[get_summary_by_title],
        tool_use_behavior="stop_on_first_tool",
    )


    print("=" * 60)
    print("Smart Librarian – RAG + Tool Calling")
    print("Scrie 'exit' pentru închidere.")
    print("Scrie 'reset' pentru resetarea memoriei.")
    print("=" * 60)

    current_book_title: str | None = None
    current_book_summary: str | None = None
    current_recommendation_reason: str | None = None

    while True:
        user_question = input("\nTu: ").strip()

        if user_question.lower() in {"exit", "quit", "stop"}:
            print("\nAgent: La revedere!")
            break

        if user_question.lower() == "reset":
            current_book_title = None
            current_book_summary = None
            current_recommendation_reason = None

            print("\nAgent: Memoria conversației a fost resetată.")
            continue

        if not user_question:
            print("\nAgent: Te rog să introduci o întrebare.")
            continue

        try:
            # ---------------------------------------------------------
            # 1. Clasificăm intenția înainte de RAG sau tool calling.
            # ---------------------------------------------------------
            current_context = (
                current_book_title
                if current_book_title is not None
                else "Nu există încă o carte curentă."
            )

            router_prompt = f"""
            Mesajul utilizatorului:
            {user_question}

            Contextul conversației:
            Cartea curentă: {current_context}

            Clasifică mesajul utilizatorului ținând cont de context.
            """

            intent_result = await Runner.run(
                intent_agent,
                router_prompt,
            )

            intent_decision: IntentDecision = intent_result.final_output


            # Pentru debugging temporar:
            # print(f"[DEBUG] Intent: {intent_decision.intent}")
            # print(f"[DEBUG] Titlu: {intent_decision.title}")

            # ---------------------------------------------------------
            # 2. Follow-up despre ultima recomandare.
            # Nu rulăm ChromaDB și nu apelăm din nou tool-ul.
            # ---------------------------------------------------------
            if intent_decision.intent == "follow_up":
                if current_book_title is None or current_book_summary is None:
                    print(
                        "\nAgent: Nu avem încă o carte despre care să discutăm. "
                        "Cere-mi o recomandare sau numește un titlu exact."
                    )
                    continue

                reason_context = (
                    current_recommendation_reason
                    if current_recommendation_reason is not None
                    else (
                        "Cartea nu a fost aleasă printr-o recomandare. "
                        "Utilizatorul a cerut direct informații despre acest titlu."
                    )
                )

                follow_up_prompt = f"""
            Întrebarea utilizatorului:
            {user_question}

            Cartea curentă:
            {current_book_title}

            Rezumatul exact disponibil:
            {current_book_summary}

            Motivul recomandării:
            {reason_context}

            Răspunde numai la întrebarea utilizatorului.

            Reguli:
            - Vorbește exclusiv despre cartea curentă.
            - Nu recomanda altă carte.
            - Nu folosi informații dintr-o carte discutată anterior.
            - Nu începe răspunsul cu „Îți recomand”.
            - Nu repeta întregul rezumat decât dacă utilizatorul cere acest lucru.
            - Dacă această carte nu a fost recomandată, nu inventa un motiv pentru alegerea ei.
            """

                follow_up_result = await Runner.run(
                    follow_up_agent,
                    follow_up_prompt,
                )

                print(f"\nAgent: {follow_up_result.final_output}")
                continue


            # ---------------------------------------------------------
            # 3. Cerere directă pentru un titlu exact.
            # Apelăm tool-ul, fără căutare semantică.
            # ---------------------------------------------------------
            if intent_decision.intent == "exact_title_summary":
                exact_title = intent_decision.title.strip()

                if not exact_title:
                    print(
                        "\nAgent: Nu am putut identifica titlul exact al cărții."
                    )
                    continue

                # Potrivire exactă. Nu corectăm typo-uri și nu căutăm aproximativ.
                if exact_title not in book_summaries_dict:
                    print(
                        f"\nAgent: Titlul exact „{exact_title}” "
                        "nu există în baza locală."
                    )
                    continue

                summary_result = await Runner.run(
                    summary_agent,
                    (
                        "Apelează get_summary_by_title exact o dată "
                        "folosind acest titlu exact: "
                        f"{exact_title}"
                    ),
                )

                summary_text = str(summary_result.final_output)

                current_book_title = exact_title
                current_book_summary = summary_text
                current_recommendation_reason = None

                print(f"\nAgent:\n{summary_text}")
                continue

            # ---------------------------------------------------------
            # 4. Mesaj fără legătură cu proiectul.
            # ---------------------------------------------------------
            if intent_decision.intent == "other":
                print(
                    "\nAgent: Te pot ajuta cu recomandări de cărți "
                    "în funcție de teme și preferințe sau cu "
                    "rezumatele titlurilor disponibile."
                )
                continue

            # ---------------------------------------------------------
            # 5. Recomandare nouă:
            # RAG -> recomandare GPT -> tool pentru rezumat.
            # ---------------------------------------------------------
            retrieved_books = retrieve_books(
                query=user_question,
                number_of_results=3,
            )

            rag_context = build_rag_context(
                retrieved_books
            )

            recommendation_prompt = f"""
Întrebarea utilizatorului:
{user_question}

Cărți returnate de retrieverul ChromaDB:
{rag_context}

Alege cea mai potrivită carte numai dintre rezultatele de mai sus.
Copiază titlul exact așa cum apare în context.
"""

            recommendation_result = await Runner.run(
                recommendation_agent,
                recommendation_prompt,
            )

            recommendation: BookRecommendation = (
                recommendation_result.final_output
            )

            exact_title = validate_recommended_title(
                recommended_title=recommendation.title,
                retrieved_books=retrieved_books,
            )

            # ---------------------------------------------------------
            # 6. Tool calling automat după recomandare.
            # ---------------------------------------------------------
            summary_result = await Runner.run(
                summary_agent,
                (
                    "Apelează get_summary_by_title exact o dată "
                    "pentru acest titlu exact: "
                    f"{exact_title}"
                ),
            )

            summary_text = str(
                summary_result.final_output
            )

            current_book_title = exact_title
            current_book_summary = summary_text
            current_recommendation_reason = recommendation.reason

            # ---------------------------------------------------------
            # 8. Afișăm rezultatul complet numai pentru recomandări noi.
            # ---------------------------------------------------------
            print(
                f"\nAgent: Îți recomand "
                f"„{exact_title}”."
            )

            print(
                f"\nMotivul recomandării:\n"
                f"{recommendation.reason}"
            )

            print(
                f"\nRezumat complet:\n"
                f"{summary_text}"
            )

        except Exception as error:
            print("\nAgent: A apărut o eroare.")
            print(f"Tip eroare: {type(error).__name__}")
            print(f"Mesaj: {error}")


if __name__ == "__main__":
    asyncio.run(main())