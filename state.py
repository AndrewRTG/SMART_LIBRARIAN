from dataclasses import dataclass


@dataclass
class ConversationState:
    """
    Memoria conversației curente.
    """

    current_book_title: str | None = None
    current_book_summary: str | None = None
    current_recommendation_reason: str | None = None

    def reset(self) -> None:
        """
        Șterge contextul conversației.
        """

        self.current_book_title = None
        self.current_book_summary = None
        self.current_recommendation_reason = None

    def set_recommended_book(
        self,
        title: str,
        summary: str,
        reason: str,
    ) -> None:
        """
        Salvează o carte obținută prin recomandarea RAG.
        """

        self.current_book_title = title
        self.current_book_summary = summary
        self.current_recommendation_reason = reason

    def set_direct_book(
        self,
        title: str,
        summary: str,
    ) -> None:
        """
        Salvează o carte solicitată direct după titlu.
        """

        self.current_book_title = title
        self.current_book_summary = summary
        self.current_recommendation_reason = None

    def has_current_book(self) -> bool:
        """
        Verifică dacă există o carte curentă.
        """

        return (
            self.current_book_title is not None
            and self.current_book_summary is not None
        )