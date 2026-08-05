from agents import function_tool

from repositories.book_repository import (
    get_available_titles,
    get_book_by_exact_title,
)


@function_tool
def get_summary_by_title(title: str) -> str:
    """
    Returnează rezumatul complet pentru un titlu exact.

    Titlul trebuie să fie complet. Funcția nu efectuează
    căutare aproximativă și nu corectează greșeli de scriere.

    Args:
        title: Titlul complet al cărții căutate.
    """

    print(f"\n[TOOL] get_summary_by_title('{title}')")

    book = get_book_by_exact_title(title)

    if book is None:
        available_titles = ", ".join(
            get_available_titles()
        )

        return (
            f"Nu am găsit titlul exact „{title}”. "
            f"Titlurile disponibile sunt: {available_titles}."
        )

    return (
        f"Titlul cărții: '{book['title']}'\n"
        f"Rezumatul complet: {book['full_summary']}"
    )