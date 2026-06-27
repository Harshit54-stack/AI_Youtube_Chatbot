"""
main.py — FastAPI application entry point for the YouTube RAG Chatbot backend.

Responsibilities
----------------
* Define the FastAPI app with lifespan (startup / shutdown hooks).
* Register CORS middleware for React frontend integration.
* Mount all API routes (thin handlers — no business logic).
* Register global exception handlers for every custom domain error.
* Provide structured JSON error responses with consistent shape.

Run locally (from the project root d:/AI_Youtube_Chatbot)
----------------------------------------------------------
    # Option 1 — using the helper script:
    python run.py

    # Option 2 — direct uvicorn:
    uvicorn backend.main:app --reload --port 8000

Swagger UI → http://localhost:8000/docs
ReDoc      → http://localhost:8000/redoc
"""

import uuid
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings, SUPPORTED_GEMINI_MODELS
from backend.models.request_models import AskRequest
from backend.models.response_models import AskResponse, ErrorResponse, SourceChunk
from backend.rag import rag_service
from backend.services.vector_store_service import initialise_embeddings
from backend.utils.exceptions import RAGBaseError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.

    startup  : Load the Google Generative AI embedding model into memory once.
    shutdown : Log graceful shutdown (add cleanup here if needed later).
    """
    # ── Startup ───────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("YouTube RAG Chatbot API — starting up")
    logger.info("Environment : %s", settings.APP_ENV)
    logger.info("LLM Provider: Google Gemini (generativelanguage.googleapis.com)")
    logger.info("LLM Model   : %s", settings.LLM_MODEL_NAME)
    logger.info("LLM Tokens  : max=%d | temp=%.1f | timeout=%ds",
                settings.LLM_MAX_TOKENS, settings.LLM_TEMPERATURE, settings.LLM_TIMEOUT)
    logger.info("Embedding   : %s", settings.EMBEDDING_MODEL_NAME)
    logger.info("CORS origins: %s", settings.CORS_ORIGINS)
    logger.info("=" * 60)

    initialise_embeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        cache_size=settings.VECTOR_STORE_CACHE_SIZE,
    )

    logger.info("Startup complete — ready to serve requests.")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────
    logger.info("YouTube RAG Chatbot API — shutting down.")


# ── FastAPI application ────────────────────────────────────────────────────────

app = FastAPI(
    title="YouTube RAG Chatbot API",
    description=(
        "A production-ready Retrieval-Augmented Generation API that answers "
        "questions about YouTube videos using their transcripts.\n\n"
        "**Stack**: LangChain · FAISS · Google Generative AI Embeddings · Google Gemini · FastAPI\n\n"
        "**LLM Provider**: [Google Gemini](https://ai.google.dev) — state-of-the-art multimodal LLM, "
        "no local GPU required, cloud-deployable.\n\n"
        "**Transcript Provider**: [Supadata](https://supadata.ai) — managed transcript API that works "
        "reliably on cloud platforms (Render, Railway) without YouTube IP-blocking.\n\n"
        "**Usage**: POST `/ask` with a YouTube URL and a question.\n\n"
        "**Models**: Use `GET /models` to list all supported Gemini models."
    ),
    version="3.0.0",
    contact={
        "name": "Harshit Malviya",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
)


# ── CORS middleware ────────────────────────────────────────────────────────────
# Allows the React frontend (running on a different port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Request logging middleware ─────────────────────────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every incoming request with method, path, and response time.
    Attach a unique X-Request-ID header to each response for traceability.
    """
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()

    logger.info(
        "[%s] → %s %s",
        request_id,
        request.method,
        request.url.path,
    )

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "[%s] ← %d  %.1f ms",
        request_id,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Request-ID"] = request_id
    return response


# ── Global exception handlers ──────────────────────────────────────────────────

@app.exception_handler(RAGBaseError)
async def rag_exception_handler(request: Request, exc: RAGBaseError) -> JSONResponse:
    """
    Catch every custom domain exception and return a structured JSON error.

    The ``error_code`` field lets the React frontend switch on the error type
    without parsing the human-readable ``detail`` string.
    """
    logger.warning(
        "Domain error [%s]: %s",
        exc.error_code,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.http_status,
        content=ErrorResponse(
            error=exc.error_code,
            detail=exc.detail,
            status_code=exc.http_status,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected errors — return 500 with a safe message."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            detail="An unexpected error occurred. Please try again later.",
            status_code=500,
        ).model_dump(),
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    summary="Health check",
    description=(
        "Returns the API status, configured LLM provider, model name, and "
        "current environment. Use this for uptime monitoring on Render/Railway."
    ),
    tags=["System"],
)
async def health_check():
    """
    Lightweight health check endpoint.

    Use this to verify the server is running before sending real requests.
    Safe to call from a load balancer or uptime monitor.
    """
    return {
        "status": "ok",
        "api": "YouTube RAG Chatbot",
        "version": "3.0.0",
        "environment": settings.APP_ENV,
        "llm_provider": "Google Gemini",
        "llm_model": settings.LLM_MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
    }


@app.get(
    "/models",
    summary="List supported Gemini models",
    description=(
        "Returns the list of Gemini model IDs supported by this API. "
        "Set `LLM_MODEL_NAME` in your `.env` to switch models at runtime."
    ),
    tags=["System"],
)
async def list_models():
    """
    Return all supported Gemini model IDs with their characteristics.

    The active model (configured via ``LLM_MODEL_NAME``) is flagged in
    the response so clients can show which model is currently in use.
    """
    model_metadata = {
        "gemini-2.5-flash": {
            "params": "N/A", "context_window": "1M",
            "speed": "fast", "quality": "highest",
            "description": "Gemini 2.5 Flash — best balance of speed & quality (default)",
        },
        "gemini-2.5-pro": {
            "params": "N/A", "context_window": "1M",
            "speed": "medium", "quality": "highest",
            "description": "Gemini 2.5 Pro — highest quality, complex reasoning",
        },
        "gemini-2.0-flash": {
            "params": "N/A", "context_window": "1M",
            "speed": "fastest", "quality": "high",
            "description": "Gemini 2.0 Flash — fast, efficient, multimodal",
        },
        "gemini-2.0-flash-lite": {
            "params": "N/A", "context_window": "1M",
            "speed": "fastest", "quality": "good",
            "description": "Gemini 2.0 Flash Lite — lightest 2.0 model",
        },
        "gemini-1.5-flash": {
            "params": "N/A", "context_window": "1M",
            "speed": "fast", "quality": "high",
            "description": "Gemini 1.5 Flash — stable, 1M token context window",
        },
        "gemini-1.5-flash-8b": {
            "params": "8B", "context_window": "1M",
            "speed": "fastest", "quality": "good",
            "description": "Gemini 1.5 Flash 8B — smallest 1.5 model",
        },
        "gemini-1.5-pro": {
            "params": "N/A", "context_window": "2M",
            "speed": "medium", "quality": "highest",
            "description": "Gemini 1.5 Pro — stable pro, 2M token context window",
        },
    }
    return {
        "active_model": settings.LLM_MODEL_NAME,
        "supported_models": [
            {
                "id": model_id,
                "active": model_id == settings.LLM_MODEL_NAME,
                **meta,
            }
            for model_id, meta in model_metadata.items()
            if model_id in SUPPORTED_GEMINI_MODELS
        ],
        "note": (
            "Switch models by setting LLM_MODEL_NAME in your .env file "
            "and restarting the server."
        ),
    }


@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask questions about YouTube videos using their transcripts.",
    description=(
        "Supply a YouTube video URL (or bare video ID) and a natural-language "
        "question. The API fetches the transcript via **Supadata API** (cloud-friendly, "
        "works on Render without YouTube IP-blocking), builds a semantic index, "
        "retrieves the most relevant chunks, and generates a grounded answer "
        "using Google Gemini.\n\n"
        "**Transcript retrieved using Supadata API.**\n\n"
        "The `sources` field in the response contains the exact transcript "
        "excerpts that grounded the answer.\n\n"
        "**Anti-hallucination**: The LLM is strictly instructed to answer only "
        "from the retrieved transcript context."
    ),
    responses={
        200: {"description": "Answer generated successfully", "model": AskResponse},
        404: {"description": "No English transcript found", "model": ErrorResponse},
        422: {
            "description": "Invalid YouTube URL or transcript disabled",
            "model": ErrorResponse,
        },
        500: {"description": "Vector store or LLM error", "model": ErrorResponse},
        503: {"description": "Gemini API unreachable or timed out", "model": ErrorResponse},
    },
    tags=["RAG"],
)
async def ask(request_body: AskRequest) -> AskResponse:
    """
    **POST /ask** — Main RAG endpoint.

    **Request body**:
    ```json
    {
        "video_url": "https://www.youtube.com/watch?v=Gfr50f6ZBvo",
        "question": "What is the main topic of this video?"
    }
    ```

    **Response**:
    ```json
    {
        "video_id": "Gfr50f6ZBvo",
        "question": "What is the main topic of this video?",
        "answer": "This video covers...",
        "sources": [
            {"chunk_index": 1, "content": "...transcript excerpt..."},
            ...
        ]
    }
    ```
    """
    # Route handler is intentionally thin — all logic lives in RAGService
    answer, video_id, retrieved_docs = rag_service.ask(
        video_url=request_body.video_url,
        question=request_body.question,
    )

    return AskResponse(
        video_id=video_id,
        question=request_body.question,
        answer=answer,
        sources=[
            SourceChunk(chunk_index=i + 1, content=doc.page_content)
            for i, doc in enumerate(retrieved_docs)
        ],
    )
