import base64
import html
from pathlib import Path

import streamlit as st


def render_image_card(
    title: str,
    image_path: str | Path,
    key_suffix: str,
) -> bool:
    """
    Afișează imaginea generată într-un card premium.

    Returnează True dacă utilizatorul cere
    o nouă variantă.
    """

    path = Path(image_path)

    if not path.exists():
        st.error(
            "Imaginea generată nu mai este disponibilă."
        )
        return False

    safe_title = html.escape(title)
    encoded_image = base64.b64encode(
        path.read_bytes()
    ).decode("ascii")
    image_extension = path.suffix.lower().lstrip(".") or "png"

    with st.container(
        key=f"image_card_{key_suffix}",
    ):
        st.html(
            f"""
<div class="generated-image-header">
    <div class="generated-image-badge">
        <span class="generated-image-dot"></span>
        AI generated
    </div>

    <div class="generated-image-heading">
        Visual interpretation
    </div>
</div>
            """
        )

        st.html(
            f"""
<div class="generated-image-frame">
    <img
        src="data:image/{image_extension};base64,{encoded_image}"
        alt="Visual interpretation inspired by {safe_title}"
    />
</div>
            """
        )

        st.html(
            f"""
<div class="generated-image-footer">

    <div class="generated-image-inspired">
        Inspired by
        <span>“{safe_title}”</span>
    </div>

    <div class="generated-image-meta">
        An original AI-generated interpretation
        of the story.
    </div>

</div>
            """
        )

        return True