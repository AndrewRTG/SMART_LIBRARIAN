import asyncio
from pathlib import Path

from agents import Runner

from app_agents.image_generation_agent import (
    create_image_generation_agent,
)
from app_tools.image_tools import (
    generate_book_image_file,
)



class ImageGenerationService:
    """
    Construiește promptul și generează imaginea.
    """

    def __init__(self) -> None:
        self.agent = create_image_generation_agent()

    async def generate_book_image(
        self,
        title: str,
        summary: str,
        user_request: str,
    ) -> Path:
        """
        Generează o imagine pentru carte.
        """

        agent_input = f"""
Titlul exact al cărții:
{title}

Rezumatul cărții:
{summary}

Cerința utilizatorului:
{user_request}

Construiește un prompt vizual complet și original.
"""

        plan_result = await asyncio.wait_for(
            Runner.run(
                self.agent,
                agent_input,
                max_turns=2,
            ),
            timeout=60,
        )

        visual_prompt = plan_result.final_output

        if not isinstance(visual_prompt, str):
            raise TypeError(
                "Agentul de imagini nu a returnat un prompt text valid."
            )

        visual_prompt = visual_prompt.strip()

        if not visual_prompt:
            raise RuntimeError(
                "Agentul de imagini a returnat un prompt gol."
            )

        print(
            "\n[IMAGE] Prompt vizual generat:",
            flush=True,
        )
        print(
            visual_prompt,
            flush=True,
        )

        generated_path = await asyncio.wait_for(
            generate_book_image_file(
                title=title,
                prompt=visual_prompt,
            ),
            timeout=180,
        )

        image_path = Path(generated_path)

        if not image_path.exists():
            raise RuntimeError(
                "Imaginea nu a fost salvată la calea așteptată: "
                f"{image_path}"
            )

        return image_path