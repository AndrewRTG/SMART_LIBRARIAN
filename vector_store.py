import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

from book_summaries import book_summaries_dict


# Folderul în care ChromaDB va salva baza vectorială.
CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"

# Numele colecției din ChromaDB.
COLLECTION_NAME = "smart_librarian_books"

# Modelul folosit pentru generarea embeddings.
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding_function() -> OpenAIEmbeddingFunction:
    """
    Creează funcția de embeddings folosită de ChromaDB.
    """

    load_dotenv()

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită în fișierul .env."
        )

    return OpenAIEmbeddingFunction(
        api_key_env_var="ENDAVA_OPENAI_API_KEY",
        model_name=EMBEDDING_MODEL,
    )


def get_book_collection() -> Collection:
    """
    Creează sau deschide colecția de cărți din ChromaDB.
    """

    chroma_client = chromadb.PersistentClient(
        path=str(CHROMA_DB_PATH)
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=get_embedding_function(),
    )

    return collection


def initialize_vector_store() -> Collection:
    """
    Încarcă titlurile și rezumatele cărților în ChromaDB.

    Metoda upsert permite rularea repetată a scriptului fără
    să creeze duplicate.
    """

    collection = get_book_collection()

    titles = list(book_summaries_dict.keys())

    documents = [
        (
            f"Title: {title}\n"
            f"Summary and themes: {book_summaries_dict[title]}"
        )
        for title in titles
    ]

    metadatas = [
        {
            "title": title,
        }
        for title in titles
    ]

    collection.upsert(
        ids=titles,
        documents=documents,
        metadatas=metadatas,
    )

    print(
        f"Vector store inițializat cu succes. "
        f"Număr de cărți: {collection.count()}"
    )

    return collection


def retrieve_books(
    query: str,
    number_of_results: int = 3,
) -> list[dict[str, Any]]:
    """
    Caută semantic cărți după temă, interes sau context.

    Args:
        query: Interesul sau tema descrisă de utilizator.
        number_of_results: Numărul maxim de cărți returnate.

    Returns:
        O listă de cărți găsite în ChromaDB.
    """

    clean_query = query.strip()

    if not clean_query:
        raise ValueError("Întrebarea pentru retriever nu poate fi goală.")

    collection = get_book_collection()

    collection_size = collection.count()

    if collection_size == 0:
        raise RuntimeError(
            "Colecția ChromaDB este goală. "
            "Rulează mai întâi initialize_vector_store()."
        )

    result_limit = min(number_of_results, collection_size)

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

    metadatas = results["metadatas"][0]
    documents = results["documents"][0]
    distances = results["distances"][0]

    for metadata, document, distance in zip(
        metadatas,
        documents,
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


def print_retrieved_books(
    query: str,
    books: list[dict[str, Any]],
) -> None:
    """
    Afișează rezultatele retrieverului într-un format ușor de citit.
    """

    print(f"\nCăutare semantică: {query}")
    print("-" * 60)

    for index, book in enumerate(books, start=1):
        print(
            f"{index}. {book['title']} "
            f"| distanță: {book['distance']:.4f}"
        )


if __name__ == "__main__":
    initialize_vector_store()

    test_query = "Vreau o carte despre prietenie și magie."

    test_results = retrieve_books(
        query=test_query,
        number_of_results=3,
    )

    print_retrieved_books(
        query=test_query,
        books=test_results,
    )