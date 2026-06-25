"""
request_models.py — Pydantic request schemas for the RAG Chatbot API.

These models validate and document all inbound request bodies.
FastAPI uses them for automatic Swagger UI generation.
"""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """
    Request body for POST /ask.

    Both full YouTube URLs and bare video IDs are accepted.
    The backend extracts the video ID internally.
    """

    video_url: str = Field(
        ...,
        title="YouTube URL or Video ID",
        description=(
            "Accepts any of the following formats:\n"
            "- Full URL: https://www.youtube.com/watch?v=Gfr50f6ZBvo\n"
            "- Short URL: https://youtu.be/Gfr50f6ZBvo\n"
            "- Bare ID: Gfr50f6ZBvo"
        ),
        examples=["https://www.youtube.com/watch?v=Gfr50f6ZBvo"],
        min_length=1,
    )

    question: str = Field(
        ...,
        title="Question",
        description="Natural-language question to answer from the video transcript.",
        examples=["What is the main topic of this video?"],
        min_length=3,
        max_length=1000,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "video_url": "https://www.youtube.com/watch?v=Gfr50f6ZBvo",
                    "question": "What is the main topic of this video?",
                }
            ]
        }
    }
