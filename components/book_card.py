import html
import re

import streamlit as st


def clean_book_summary(
    title: str,
    summary: str,
) -> str:
    """
    Elimină metadatele redundante din rezumat
    înainte de afișarea în UI.
    """

    cleaned = summary.strip()

    escaped_title = re.escape(title.strip())
    metadata_pattern = re.compile(
        rf"^(?:\s*(?:Titlul cărții:\s*[\"']?{escaped_title}[\"']?|Rezumatul complet:\s*|Rezumat complet:\s*))+",
        re.IGNORECASE,
    )

    cleaned = metadata_pattern.sub("", cleaned).strip(" :-\n\t")

    return cleaned or summary.strip()


def render_book_card(
    title: str,
    summary: str,
    key_suffix: str,
) -> bool:
    """
    Afișează un card premium pentru o carte.

    Returnează True dacă utilizatorul apasă
    butonul de generare a imaginii.
    """

    clean_summary = clean_book_summary(
        title=title,
        summary=summary,
    )

    safe_title = html.escape(title)
    safe_summary = html.escape(clean_summary)

    st.html(
        f"""
<div class="book-card">

    <div class="book-card-top">
        <div class="book-cover-placeholder">
            <svg
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    d="M5 4.5C5 3.67 5.67 3 6.5 3H18
                       C18.55 3 19 3.45 19 4V19
                       C19 19.55 18.55 20 18 20H6.5
                       C5.67 20 5 19.33 5 18.5V4.5Z"
                    stroke="currentColor"
                    stroke-width="1.5"
                />

                <path
                    d="M8 7H16"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                />

                <path
                    d="M8 10H14"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                />
            </svg>
        </div>

        <div class="book-card-heading">
            <div class="book-found-badge">
                <span class="book-found-dot"></span>
                Book found
            </div>

            <h3 class="book-card-title">
                {safe_title}
            </h3>
        </div>
    </div>

    <div class="book-card-divider"></div>

    <div class="book-card-label">
        Summary
    </div>

    <div class="book-card-summary">
        {safe_summary}
    </div>

</div>
        """
    )

    return st.button(
        "Visualize this book  ✦",
        key=f"visualize_book_{key_suffix}",
        use_container_width=True,
    )