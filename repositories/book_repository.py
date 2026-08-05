import json
from functools import lru_cache
from pathlib import Path
from typing import Any


BOOKS_FILE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "books.json"
)


@lru_cache(maxsize=1)
def load_books() -> list[dict[str, Any]]:
    """
    Citește și validează cărțile din fișierul JSON.

    Rezultatul este păstrat în memorie după prima citire.
    """

    if not BOOKS_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Fișierul cu cărți nu există: {BOOKS_FILE_PATH}"
        )

    with BOOKS_FILE_PATH.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        books = json.load(file)

    if not isinstance(books, list):
        raise ValueError(
            "Fișierul books.json trebuie să conțină o listă."
        )

    if len(books) < 10:
        raise ValueError(
            "Fișierul books.json trebuie să conțină minimum 10 cărți."
        )

    required_fields = {
        "title",
        "short_summary",
        "full_summary",
        "themes",
    }

    seen_titles: set[str] = set()

    for book in books:
        if not isinstance(book, dict):
            raise ValueError(
                "Fiecare carte trebuie să fie un obiect JSON."
            )

        missing_fields = required_fields - book.keys()

        if missing_fields:
            raise ValueError(
                f"Cartea este incompletă. "
                f"Câmpuri lipsă: {missing_fields}"
            )

        title = book["title"]

        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                "Fiecare carte trebuie să aibă un titlu valid."
            )

        normalized_title = title.strip().casefold()

        if normalized_title in seen_titles:
            raise ValueError(
                f"Titlu duplicat în books.json: {title}"
            )

        seen_titles.add(normalized_title)

        if not isinstance(book["themes"], list):
            raise ValueError(
                f"Temele pentru „{title}” trebuie să fie o listă."
            )

    return books


def get_all_books() -> list[dict[str, Any]]:
    """
    Returnează toate cărțile disponibile.
    """

    return load_books()


def get_book_by_exact_title(
    title: str,
) -> dict[str, Any] | None:
    """
    Caută titlul complet, fără potrivire aproximativă.

    Literele mari și mici sunt ignorate, dar titlul trebuie
    să fie complet. Nu sunt corectate greșelile de scriere.
    """

    normalized_title = title.strip().casefold()

    for book in load_books():
        if book["title"].casefold() == normalized_title:
            return book

    return None


def get_available_titles() -> list[str]:
    """
    Returnează lista titlurilor disponibile.
    """

    return [
        book["title"]
        for book in load_books()
    ]