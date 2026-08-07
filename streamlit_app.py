import asyncio
import re
from pathlib import Path

import streamlit as st

from agents import InputGuardrailTripwireTriggered
from app_tools.image_tools import open_image_file
from components.book_card import clean_book_summary, render_book_card
from config import configure_openai
from services.librarian_service import SmartLibrarianService
from components.image_card import render_image_card


st.set_page_config(
    page_title="Smart Librarian",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    css_path = (
        Path(__file__).parent
        / "styles"
        / "main.css"
    )

    css = css_path.read_text(
        encoding="utf-8"
    )

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def initialize_app_state() -> None:
    """
    Inițializează obiectele care trebuie păstrate între rerun-uri.
    """

    if "openai_configured" not in st.session_state:
        configure_openai()
        st.session_state.openai_configured = True

    if "librarian" not in st.session_state:
        st.session_state.librarian = SmartLibrarianService()

    if "messages" not in st.session_state:
        st.session_state.messages = []



def run_async(coroutine):
    """
    Rulează o operație async din aplicația Streamlit.
    """

    return asyncio.run(coroutine)


def remove_redundant_book_summary(
    response: str,
    title: str,
    summary: str,
) -> str:
    """
    Elimină din mesajul assistant-ului blocul brut de rezumat
    atunci când aceeași informație este afișată în book card.
    """

    cleaned_response = response.strip()
    cleaned_summary = clean_book_summary(
        title=title,
        summary=summary,
    )

    escaped_title = re.escape(title.strip())
    escaped_summary = re.escape(cleaned_summary)
    patterns = (
        rf"\n*Rezumat\s+complet:\s*Titlul\s+cărții:\s*[\"']?{escaped_title}[\"']?\s*Rezumatul\s+complet:\s*{escaped_summary}",
        rf"\n*Titlul\s+cărții:\s*[\"']?{escaped_title}[\"']?\s*Rezumatul\s+complet:\s*{escaped_summary}",
        rf"\n*Rezumatul?\s+complet:\s*{escaped_summary}",
    )

    for pattern in patterns:
        cleaned_response = re.sub(
            pattern,
            "",
            cleaned_response,
            flags=re.IGNORECASE,
        )

    return cleaned_response.strip()


def extract_generated_image_payload(
    response: str,
    librarian: SmartLibrarianService,
) -> dict[str, str] | None:
    """
    Extrage metadatele imaginii generate din răspunsul text
    al backend-ului, pentru a afișa Image Card în UI.
    """

    lines = [
        line.strip()
        for line in response.splitlines()
        if line.strip()
    ]

    path_candidate: str | None = None

    for index, line in enumerate(lines):
        inline_match = re.search(
            r"Fișier\s+salvat\s+la:\s*(.+)$",
            line,
            flags=re.IGNORECASE,
        )

        if inline_match:
            path_candidate = inline_match.group(1).strip()
            break

        if re.fullmatch(
            r"Fișier\s+salvat\s+la:\s*",
            line,
            flags=re.IGNORECASE,
        ):
            if index + 1 < len(lines):
                path_candidate = lines[index + 1].strip()
                break

    if not path_candidate:
        return None

    image_path = Path(path_candidate.strip('"'))

    if not image_path.exists():
        return None

    title_match = re.search(
        r"Imaginea\s+pentru\s+[„\"]?(.+?)[”\"]?\s+a\s+fost\s+generată",
        response,
        flags=re.IGNORECASE,
    )

    image_title = (
        title_match.group(1).strip()
        if title_match
        else librarian.state.current_book_title
    )

    image_summary = librarian.state.current_book_summary

    if not image_title or not image_summary:
        return None

    return {
        "title": image_title,
        "summary": image_summary,
        "path": str(image_path),
    }



def render_chat_history() -> None:
    """
    Afișează conversația și componentele asociate.
    """

    for index, message in enumerate(
        st.session_state["messages"]
    ):
        role = message["role"]
        content = message["content"]

        with st.chat_message(role):
            st.markdown(content)

            book = message.get("book")

            if book:
                visualize_clicked = render_book_card(
                    title=book["title"],
                    summary=book["summary"],
                    key_suffix=str(index),
                )

                if visualize_clicked:
                    st.session_state[
                        "pending_visualization"
                    ] = {
                        "title": book["title"],
                        "summary": book["summary"],
                        "user_request": (
                            "Generează o imagine originală "
                            f"inspirată de cartea {book['title']}."
                        ),
                    }

                    st.rerun()

            image = message.get("image")

            if image:
                image_card_rendered = render_image_card(
                    title=image["title"],
                    image_path=image["path"],
                    key_suffix=str(index),
                )

                if image_card_rendered:
                    if st.button(
                        "Open image",
                        key=f"open_image_{index}",
                        use_container_width=True,
                    ):
                        open_image_file(
                            Path(image["path"])
                        )

                    if st.button(
                        "Generate another variation  ✦",
                        key=f"regenerate_image_{index}",
                        use_container_width=True,
                    ):
                        image_summary = image.get(
                            "summary"
                        )

                        if not image_summary:
                            image_summary = st.session_state[
                                "librarian"
                            ].state.current_book_summary

                        if not image_summary:
                            st.session_state["messages"].append(
                                {
                                    "role": "assistant",
                                    "content": (
                                        "Nu mai am rezumatul necesar pentru "
                                        "a genera o nouă variație. "
                                        "Cere din nou detaliile cărții sau "
                                        "selectează cartea încă o dată."
                                    ),
                                }
                            )
                            st.rerun()

                        st.session_state[
                            "pending_visualization"
                        ] = {
                            "title": image["title"],
                            "summary": image_summary,
                            "user_request": (
                                "Generează o altă variantă vizuală "
                                "originală pentru aceeași carte. "
                                "Folosește o compoziție clar diferită, "
                                "o perspectivă diferită și o atmosferă "
                                "vizuală diferită de varianta precedentă."
                            ),
                        }

                        st.rerun()
    
                




def render_ai_loader(
    placeholder,
    title: str = "Smart Librarian is thinking",
    subtitle: str = "Exploring the library for you",
) -> None:
    """
    Afișează un loader temporar premium.
    """

    loader_html = f"""
<div class="ai-thinking">
    <div class="ai-thinking-icon">
        ✦
    </div>

    <div class="ai-thinking-content">
        <div class="ai-thinking-title">
            {title}

            <span class="ai-thinking-dots">
                <span></span>
                <span></span>
                <span></span>
            </span>
        </div>

        <div class="ai-thinking-subtitle">
            {subtitle}
        </div>
    </div>
</div>
"""

    with placeholder.container():
        st.html(loader_html)





def clean_response_for_book_card(
    response: str,
    book_title: str,
) -> str:
    """
    Elimină blocul de rezumat din mesajul conversațional
    atunci când rezumatul este afișat separat în Book Card.
    """

    marker = "Rezumat complet:"

    if marker not in response:
        return response.strip()

    conversational_part = response.split(
        marker,
        1,
    )[0].strip()

    if conversational_part:
        return conversational_part

    return f'Am găsit „{book_title}”.'



def process_user_message(
    user_message: str,
) -> None:
    """
    Procesează mesajul utilizatorului și afișează
    feedback vizual în timpul operației AI.
    """

    st.session_state["messages"].append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Mesajul nou nu era în istoricul randat la începutul
    # acestui rerun, așa că îl afișăm imediat.
    with st.chat_message("user"):
        st.markdown(user_message)

    loader_placeholder = st.empty()

    render_ai_loader(
        loader_placeholder,
        title="Smart Librarian is thinking",
        subtitle="Exploring stories, knowledge and imagination",
    )

    try:
        librarian = st.session_state["librarian"]

        previous_title = (
            librarian.state.current_book_title
        )
        response = run_async(
            librarian.process_message(
                user_message
            )
        )

    except InputGuardrailTripwireTriggered:
        response = (
            "Te rog să folosești un limbaj respectuos. "
            "Mesajul nu a fost procesat."
        )

    except TimeoutError:
        response = (
            "Cererea a durat prea mult. "
            "Te rog să încerci din nou."
        )

    except Exception as error:
        print(
            "[STREAMLIT ERROR] "
            f"{type(error).__name__}: {error}"
        )

        response = (
            "A apărut o problemă în timpul procesării cererii. "
            "Te rog să încerci din nou."
        )

    finally:
        loader_placeholder.empty()

    current_title = (
    librarian.state.current_book_title
    )

    current_summary = (
        librarian.state.current_book_summary
    )



    assistant_message = {
        "role": "assistant",
        "content": response,
    }

    image_payload = extract_generated_image_payload(
        response=response,
        librarian=librarian,
    )

    if image_payload:
        assistant_message["content"] = (
            f'Am creat o interpretare vizuală pentru '
            f'„{image_payload["title"]}”.'
        )
        assistant_message["image"] = image_payload

    if (
        current_title
        and current_summary
        and current_title != previous_title
        and not image_payload
    ):
        assistant_message["content"] = remove_redundant_book_summary(
            response=response,
            title=current_title,
            summary=current_summary,
        )
        assistant_message["book"] = {
            "title": current_title,
            "summary": current_summary,
        }

    st.session_state["messages"].append(
    assistant_message
    )



def process_pending_visualization() -> None:
    """
    Procesează o cerere pornită din butonul
    Visualize this book.
    """

    pending = st.session_state.pop(
        "pending_visualization",
        None,
    )

    if not pending:
        return

    title = pending["title"]
    summary = pending["summary"]
    user_request = pending.get(
        "user_request",
        (
            "Generează o imagine originală "
            f"inspirată de cartea {title}."
        ),
    )

    loader_placeholder = st.empty()

    render_ai_loader(
        loader_placeholder,
        title=f'Imagining “{title}”',
        subtitle="Creating your visual interpretation",
    )

    try:
        librarian = st.session_state["librarian"]

        image_path = run_async(
            librarian.image_generation_service.generate_book_image(
                title=title,
                summary=summary,
                user_request=user_request,
            )
        )

        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": (
                    f'Am creat o interpretare vizuală '
                    f'pentru „{title}”.'
                ),
                "image": {
                    "title": title,
                    "summary": summary,
                    "path": str(image_path),
                },
            }
        )

    except Exception as error:
        print(
            "[IMAGE STREAMLIT ERROR] "
            f"{type(error).__name__}: {error}"
        )

        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": (
                    "Imaginea nu a putut fi generată acum. "
                    "Te rog să încerci din nou."
                ),
            }
        )

    finally:
        loader_placeholder.empty()

    st.rerun()



def render_hero() -> None:
    st.html(
        """
<section class="smart-hero">

    <div class="smart-logo">
        <svg
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M4 5.5C4 4.67 4.67 4 5.5 4H10
                   C11.1 4 12 4.9 12 6V20
                   C12 18.9 11.1 18 10 18H5.5
                   C4.67 18 4 17.33 4 16.5V5.5Z"
                stroke="#C7C9FF"
                stroke-width="1.5"
            />

            <path
                d="M20 5.5C20 4.67 19.33 4 18.5 4H14
                   C12.9 4 12 4.9 12 6V20
                   C12 18.9 12.9 18 14 18H18.5
                   C19.33 18 20 17.33 20 16.5V5.5Z"
                stroke="#8EEAFF"
                stroke-width="1.5"
            />

            <path
                d="M17.5 1.8L18.1 3.4L19.7 4
                   L18.1 4.6L17.5 6.2
                   L16.9 4.6L15.3 4
                   L16.9 3.4L17.5 1.8Z"
                fill="#E8BC70"
            />
        </svg>
    </div>

    <h1 class="smart-title">
        Smart Librarian
    </h1>

    <p class="smart-subtitle">
        Your AI-powered gateway to stories,
        knowledge and imagination.
    </p>

    <div class="smart-kicker">
        Discover books · Explore stories · Visualize imagination
    </div>

</section>
        """
    )


def render_empty_state() -> str | None:
    st.html(
        """
<div class="empty-state">
    <div class="empty-state-title">
        What would you like to discover?
    </div>

    <div class="empty-state-description">
        Explore a title, find your next book,
        or bring a story to life.
    </div>
</div>
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Find a book  ·  Tell me about Dune",
            key="quick_find_dune",
            use_container_width=True,
        ):
            return "Tell me about Dune"

        if st.button(
            "Recommend something  ·  Philosophical sci-fi",
            key="quick_recommend_scifi",
            use_container_width=True,
        ):
            return "Recommend me a philosophical sci-fi book"

    with col2:
        if st.button(
            "Visualize a story  ·  The Hobbit",
            key="quick_visualize_hobbit",
            use_container_width=True,
        ):
            return "Generate an image inspired by The Hobbit"

        if st.button(
            "Search by title  ·  Search for 1984",
            key="quick_search_1984",
            use_container_width=True,
        ):
            return "Search for 1984"

    return None

load_css()

initialize_app_state()

render_hero()

process_pending_visualization()

if not st.session_state["messages"]:
    quick_prompt = render_empty_state()
else:
    quick_prompt = None

render_chat_history()

prompt = st.chat_input(
    "Ask your librarian about a book..."
)

if quick_prompt:
    process_user_message(quick_prompt)

    st.rerun()

elif prompt:
    process_user_message(prompt)

    st.rerun()