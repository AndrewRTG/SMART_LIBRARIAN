from typing import Literal

from pydantic import BaseModel


class BookRecommendation(BaseModel):
    """
    Recomandarea structurată produsă de recommendation agent.
    """

    title: str
    reason: str


class IntentDecision(BaseModel):
    """
    Rezultatul clasificării mesajului utilizatorului.
    """

    intent: Literal[
        "new_recommendation",
        "follow_up",
        "exact_title_summary",
        "other",
    ]

    title: str