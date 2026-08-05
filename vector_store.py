import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils.embedding_functions import (
    OpenAIEmbeddingFunction,
)
from dotenv import load_dotenv

from repositories.book_repository import get_all_books


CHROMA_DB_PATH = (
    Path(__file__).resolve().parent
    / "chroma_db"
)

COLLECTION_NAME = "smart_librarian_books"
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding_function() -> OpenAIEmbeddingFunction:
    """
    Creează funcția OpenAI folosită pentru embeddings.
    """

    load_dotenv()

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită."
        )

    return OpenAIEmbeddingFunction(
        api_key_env_var="ENDAVA_OPENAI_API_KEY",
        model_name=EMBEDDING_MODEL,
    )


def get_book_collection():
    """
    Creează sau deschide colecția ChromaDB.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_DB_PATH)
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
    )


def initialize_vector_store():
    """
    Încarcă în ChromaDB titlurile, temele și rezumatele scurte.
    """

    collection = get_book_collection()
    books = get_all_books()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []

    for book in books:
        title = book["title"]
        themes = ", ".join(book["themes"])

        document = (
            f"Title: {title}\n"
            f"Themes: {themes}\n"
            f"Short summary: {book['short_summary']}"
        )

        ids.append(title)
        documents.append(document)
        metadatas.append(
            {
                "title": title,
            }
        )

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(
        "Vector store inițializat cu succes. "
        f"Număr de cărți: {collection.count()}"
    )

    return collection


def retrieve_books(
    query: str,
    number_of_results: int = 3,
) -> list[dict[str, Any]]:
    """
    Caută semantic cărți după temă sau context.
    """

    clean_query = query.strip()

    if not clean_query:
        raise ValueError(
            "Întrebarea pentru retriever nu poate fi goală."
        )

    collection = get_book_collection()

    if collection.count() == 0:
        raise RuntimeError(
            "Colecția ChromaDB este goală. "
            "Rulează mai întâi vector_store.py."
        )

    result_limit = min(
        number_of_results,
        collection.count(),
    )

    results = collection.query(
        query_texts=[clean_query],
        n_results=result_limit,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    retrieved_books: list[dict[str, Any]] = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        retrieved_books.append(
            {
                "title": metadata["title"],
                "document": document,
                "distance": distance,
            }
        )

    return retrieved_books


if __name__ == "__main__":
    collection = initialize_vector_store()

    test_query = "Vreau o carte despre prietenie și magie."

    test_results = retrieve_books(
        query=test_query,
        number_of_results=3,
    )

    print(f"\nCăutare semantică: {test_query}")
    print("-" * 60)

    for index, book in enumerate(
        test_results,
        start=1,
    ):
        print(
            f"{index}. {book['title']} "
            f"| distanță: {book['distance']:.4f}"
        )