from agents import Runner

from app_agents.follow_up_agent import create_follow_up_agent
from app_agents.intent_agent import create_intent_agent
from app_agents.recommendation_agent import (
    create_recommendation_agent,
)
from app_agents.summary_agent import create_summary_agent
from repositories.book_repository import get_book_by_exact_title
from models import BookRecommendation, IntentDecision
from state import ConversationState
from utils.rag_helpers import (
    build_rag_context,
    validate_recommended_title,
)
from services.image_generation_service import (
    ImageGenerationService,
)
from vector_store import retrieve_books


class SmartLibrarianService:
    """
    Coordonează fluxul Smart Librarian.
    """

    def __init__(self) -> None:
        self.state = ConversationState()

        self.intent_agent = create_intent_agent()
        self.follow_up_agent = create_follow_up_agent()
        self.recommendation_agent = create_recommendation_agent()
        self.summary_agent = create_summary_agent()
        self.image_generation_service = ImageGenerationService()

    def reset(self) -> None:
        """
        Resetează memoria conversației.
        """

        self.state.reset()


    async def _handle_image_generation(
        self,
        user_question: str,
        requested_title: str,
    ) -> str:
        """
        Generează o imagine pentru un titlu explicit
        sau pentru cartea curentă.
        """

        clean_title = requested_title.strip()

        if clean_title:
            book = get_book_by_exact_title(
                clean_title
            )

            if book is None:
                return (
                    f"Titlul exact „{clean_title}” "
                    "nu există în baza locală."
                )

            exact_title = book["title"]
            summary = book["full_summary"]

            # Cartea menționată explicit devine cartea curentă.
            self.state.set_direct_book(
                title=exact_title,
                summary=summary,
            )

        else:
            if not self.state.has_current_book():
                return (
                    "Nu există încă o carte curentă. "
                    "Numește titlul exact al unei cărți sau "
                    "cere mai întâi o recomandare."
                )

            exact_title = self.state.current_book_title
            summary = self.state.current_book_summary

        if exact_title is None or summary is None:
            raise RuntimeError(
                "Nu am putut determina cartea pentru imagine."
            )

        print(
            f"\n[IMAGE] Generez imaginea pentru "
            f"„{exact_title}”...",
            flush=True,
        )

        image_path = (
            await self.image_generation_service.generate_book_image(
                title=exact_title,
                summary=summary,
                user_request=user_question,
            )
        )

        return (
            f"Imaginea pentru „{exact_title}” a fost generată.\n"
            f"Fișier salvat la:\n{image_path.resolve()}"
        )

    async def process_message(self, user_question: str) -> str:
        """
        Procesează un mesaj și returnează răspunsul final.
        """

        intent_decision = await self._classify_intent(
            user_question
        )

        if intent_decision.intent == "follow_up":
            return await self._handle_follow_up(
                user_question
            )

        if intent_decision.intent == "exact_title_summary":
            return await self._handle_exact_title(
                intent_decision.title
            )

        if intent_decision.intent == "image_generation":
             return await self._handle_image_generation(
                 user_question=user_question,
                 requested_title=intent_decision.title,
              )

        if intent_decision.intent == "other":
            return (
                "Te pot ajuta cu recomandări de cărți în funcție "
                "de teme și preferințe sau cu rezumatele "
                "titlurilor disponibile."
            )

        

        return await self._handle_new_recommendation(
            user_question
        )

    async def _classify_intent(
        self,
        user_question: str,
    ) -> IntentDecision:
        """
        Clasifică mesajul utilizatorului.
        """

        current_context = (
            self.state.current_book_title
            if self.state.current_book_title is not None
            else "Nu există încă o carte curentă."
        )

        router_prompt = f"""
Mesajul utilizatorului:
{user_question}

Contextul conversației:
Cartea curentă: {current_context}

Clasifică mesajul utilizatorului ținând cont de context.
"""

        result = await Runner.run(
            self.intent_agent,
            router_prompt,
        )

        decision = result.final_output

        if not isinstance(decision, IntentDecision):
            raise TypeError(
                "Intent agent nu a returnat un IntentDecision valid."
            )

        return decision

    async def _handle_follow_up(
        self,
        user_question: str,
    ) -> str:
        """
        Răspunde la o întrebare despre cartea curentă.
        """

        if not self.state.has_current_book():
            return (
                "Nu avem încă o carte despre care să discutăm. "
                "Cere-mi o recomandare sau numește un titlu exact."
            )

        reason_context = (
            self.state.current_recommendation_reason
            if self.state.current_recommendation_reason is not None
            else (
                "Cartea nu a fost aleasă printr-o recomandare. "
                "Utilizatorul a cerut direct informații despre titlu."
            )
        )

        follow_up_prompt = f"""
Întrebarea utilizatorului:
{user_question}

Cartea curentă:
{self.state.current_book_title}

Rezumatul exact disponibil:
{self.state.current_book_summary}

Motivul recomandării:
{reason_context}

Răspunde numai la întrebarea utilizatorului.

Reguli:
- Vorbește exclusiv despre cartea curentă.
- Nu recomanda altă carte.
- Nu folosi informații dintr-o carte discutată anterior.
- Nu începe răspunsul cu „Îți recomand”.
- Nu repeta întregul rezumat decât dacă este solicitat.
- Dacă nu a fost recomandată, nu inventa un motiv.
"""

        result = await Runner.run(
            self.follow_up_agent,
            follow_up_prompt,
        )

        return str(result.final_output)

    async def _handle_exact_title(
            self,
            title: str,
        ) -> str:
            """
            Apelează tool-ul pentru un titlu solicitat direct.
            """

            requested_title = title.strip()

            if not requested_title:
                return "Nu am putut identifica titlul exact al cărții."

            book = get_book_by_exact_title(
                requested_title
            )

            if book is None:
                return (
                    f"Titlul exact „{requested_title}” "
                    "nu există în baza locală."
                )

            exact_title = book["title"]

            summary_text = await self._get_summary(
                exact_title
            )

            self.state.set_direct_book(
                title=exact_title,
                summary=summary_text,
            )

            return summary_text

    async def _handle_new_recommendation(
        self,
        user_question: str,
    ) -> str:
        """
        Rulează fluxul RAG, recomandarea și tool calling.
        """

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

        result = await Runner.run(
            self.recommendation_agent,
            recommendation_prompt,
        )

        recommendation = result.final_output

        if not isinstance(
            recommendation,
            BookRecommendation,
        ):
            raise TypeError(
                "Recommendation agent nu a returnat "
                "un BookRecommendation valid."
            )

        exact_title = validate_recommended_title(
            recommended_title=recommendation.title,
            retrieved_books=retrieved_books,
        )

        summary_text = await self._get_summary(
            exact_title
        )

        self.state.set_recommended_book(
            title=exact_title,
            summary=summary_text,
            reason=recommendation.reason,
        )

        return (
            f"Îți recomand „{exact_title}”.\n\n"
            f"Motivul recomandării:\n"
            f"{recommendation.reason}\n\n"
            f"Rezumat complet:\n"
            f"{summary_text}"
        )

    async def _get_summary(
        self,
        exact_title: str,
    ) -> str:
        """
        Apelează summary agent și tool-ul local.
        """

        result = await Runner.run(
            self.summary_agent,
            (
                "Apelează get_summary_by_title exact o dată "
                "pentru acest titlu exact: "
                f"{exact_title}"
            ),
        )

        return str(result.final_output)