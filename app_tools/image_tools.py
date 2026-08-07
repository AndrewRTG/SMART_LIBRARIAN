import base64
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from openai import AsyncOpenAI

from config import IMAGE_MODEL_NAME


GENERATED_IMAGES_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "generated_images"
)


def create_safe_filename(title: str) -> str:
    """
    Creează un nume de fișier valid pentru imagine.
    """

    safe_title = "".join(
        character if character.isalnum() else "_"
        for character in title
    ).strip("_")

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    return f"{safe_title}_{timestamp}.png"


def open_image_file(image_path: Path) -> None:
    """
    Deschide imaginea în aplicația implicită a sistemului.
    """

    resolved_path = str(image_path.resolve())

    if os.name == "nt":
        os.startfile(resolved_path)  # type: ignore[attr-defined]
        return

    if sys.platform == "darwin":
        subprocess.run(
            ["open", resolved_path],
            check=False,
        )
        return

    subprocess.run(
        ["xdg-open", resolved_path],
        check=False,
    )


async def generate_book_image_file(
    title: str,
    prompt: str,
) -> str:
    """
    Generează și salvează o imagine originală pentru o carte.

    Args:
        title: Titlul exact al cărții.
        prompt: Descrierea vizuală completă a imaginii.
    """

    api_key = os.getenv("ENDAVA_OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "ENDAVA_OPENAI_API_KEY nu a fost găsită."
        )

    client = AsyncOpenAI(
        api_key=api_key,
    )

    try:
        result = await client.images.generate(
            model=IMAGE_MODEL_NAME,
            prompt=prompt,
            size="1024x1024",
            quality="low",
        )
    finally:
        await client.close()

    if not result.data:
        raise RuntimeError(
            "Images API nu a returnat nicio imagine."
        )

    image_base64 = result.data[0].b64_json

    if not image_base64:
        raise RuntimeError(
            "Images API nu a returnat conținut Base64."
        )

    try:
        image_bytes = base64.b64decode(
            image_base64,
            validate=True,
        )
    except ValueError as error:
        raise RuntimeError(
            "Imaginea returnată nu conține Base64 valid."
        ) from error

    GENERATED_IMAGES_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_path = (
        GENERATED_IMAGES_DIRECTORY
        / create_safe_filename(title)
    )

    image_path.write_bytes(image_bytes)

    return image_path.resolve()