from typing import Any


def build_rag_context(
    retrieved_books: list[dict[str, Any]],
) -> str:
    """
    Transformă rezultatele ChromaDB într-un context pentru agent.
    """

    context_parts: list[str] = []

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
    Verifică dacă titlul recomandat există în rezultatele retrieverului.
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
        "Agentul a recomandat un titlu care nu provine "
        "din retriever. "
        f"Titluri permise: {available_titles}"
    )