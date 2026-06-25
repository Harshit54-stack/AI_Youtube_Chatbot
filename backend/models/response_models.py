"""
response_models.py — Pydantic response schemas for the RAG Chatbot API.

These models serialise all outbound JSON responses.
FastAPI uses them for automatic Swagger UI generation and response validation.
"""

from pydantic import BaseModel, Field


class SourceChunk(BaseModel):
    """
    A single transcript chunk retrieved from the FAISS vector store.
    Included in AskResponse.sources so the client can show provenance.
    """

    chunk_index: int = Field(
        ...,
        title="Chunk Index",
        description="1-based position of this chunk among the retrieved results.",
        examples=[1],
    )
    content: str = Field(
        ...,
        title="Chunk Content",
        description="The raw transcript text used as context for the answer.",
        examples=["In this video we explore the fundamentals of machine learning..."],
    )


class AskResponse(BaseModel):
    """
    Successful response from POST /ask.

    Returns the generated answer together with the source transcript
    chunks that grounded it, enabling frontend citation display.
    """

    video_id: str = Field(
        ...,
        title="Video ID",
        description="The 11-character YouTube video ID resolved from the request.",
        examples=["Gfr50f6ZBvo"],
    )
    question: str = Field(
        ...,
        title="Question",
        description="The original question echoed back for convenience.",
        examples=["What is the main topic of this video?"],
    )
    answer: str = Field(
        ...,
        title="Answer",
        description="The LLM-generated answer grounded in the transcript.",
        examples=["This video covers the fundamentals of retrieval-augmented generation."],
    )
    sources: list[SourceChunk] = Field(
        ...,
        title="Sources",
        description="Transcript chunks that were retrieved and used as context.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "video_id": "Gfr50f6ZBvo",
                    "question": "What is the main topic of this video?",
                    "answer": "This video covers the fundamentals of retrieval-augmented generation (RAG).",
                    "sources": [
                        {"chunk_index": 1, "content": "Today we're going to talk about RAG..."},
                        {"chunk_index": 2, "content": "RAG combines retrieval with generation..."},
                    ],
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """
    Structured JSON error returned by all exception handlers.

    Using a consistent error schema makes frontend error handling trivial —
    always check ``response.error`` and ``response.detail``.
    """

    error: str = Field(
        ...,
        title="Error Code",
        description="Machine-readable error code (snake_case).",
        examples=["INVALID_VIDEO_URL"],
    )
    detail: str = Field(
        ...,
        title="Detail",
        description="Human-readable explanation of what went wrong.",
        examples=["'not-a-video' is not a valid YouTube video ID."],
    )
    status_code: int = Field(
        ...,
        title="HTTP Status Code",
        description="The HTTP status code of this error response.",
        examples=[422],
    )
