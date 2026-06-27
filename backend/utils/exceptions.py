"""
exceptions.py — Custom exception hierarchy for the RAG Chatbot backend.

Every exception maps to a specific HTTP status code so that the FastAPI
exception handlers in main.py can return consistent, structured JSON errors
without any try/except clutter in the route handlers.

Exception Tree
--------------
RAGBaseError (500)
├── InvalidVideoURLError    (422) — bad URL or video ID format
├── TranscriptDisabledError (422) — video owner disabled captions
├── TranscriptNotFoundError (404) — no transcript found for the video
├── SupadataAPIError        (502) — Supadata API unreachable or returned an error
├── VectorStoreError        (500) — FAISS build or retrieval failure
├── LLMConnectionError      (503) — cannot reach the Google Gemini API
│   ├── network error
│   ├── invalid API key
│   └── timeout
└── LLMGenerationError      (500) — Gemini returned an error response
    ├── rate limit exceeded
    ├── model not found
    ├── context window exceeded
    └── empty response
"""


class RAGBaseError(Exception):
    """
    Root of the custom exception tree.
    All domain errors inherit from this so callers can catch broadly
    with ``except RAGBaseError`` when needed.
    """
    http_status: int = 500
    error_code:  str = "INTERNAL_ERROR"

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


# ── Input / URL errors ─────────────────────────────────────────────────────────

class InvalidVideoURLError(RAGBaseError):
    """
    Raised when the supplied string is not a recognisable YouTube URL or
    a valid 11-character video ID.

    HTTP 422 Unprocessable Entity — the client sent a bad value.
    """
    http_status = 422
    error_code  = "INVALID_VIDEO_URL"


# ── Transcript errors ──────────────────────────────────────────────────────────

class TranscriptDisabledError(RAGBaseError):
    """
    Raised when the video owner has disabled captions entirely.

    HTTP 422 — the video exists but cannot be processed by this app.
    """
    http_status = 422
    error_code  = "TRANSCRIPT_DISABLED"


class TranscriptNotFoundError(RAGBaseError):
    """
    Raised when no transcript is available for the video via Supadata.

    HTTP 404 — the resource (transcript) was not found.
    """
    http_status = 404
    error_code  = "TRANSCRIPT_NOT_FOUND"


class SupadataAPIError(RAGBaseError):
    """
    Raised when the Supadata Transcript API is unreachable or returns an
    unexpected error (non-404 / non-400 failure).

    Covers:
    - Network errors (no internet, DNS failure, connection refused)
    - HTTP timeout (the request exceeded the configured timeout)
    - Supadata service errors (5xx responses)
    - Unexpected API response format

    HTTP 502 Bad Gateway — the upstream transcript service failed.
    """
    http_status = 502
    error_code  = "SUPADATA_API_ERROR"


# ── Vector store errors ────────────────────────────────────────────────────────

class VectorStoreError(RAGBaseError):
    """
    Raised when FAISS fails to build or query the vector index.

    HTTP 500 — unexpected server-side failure.
    """
    http_status = 500
    error_code  = "VECTOR_STORE_ERROR"


# ── LLM errors ─────────────────────────────────────────────────────────────────

class LLMConnectionError(RAGBaseError):
    """
    Raised when the backend cannot reach the Google Gemini API.

    Covers:
    - Network errors (no internet, DNS failure)
    - Invalid or expired API key (401 Unauthorized)
    - HTTP timeout (the request exceeded LLM_TIMEOUT seconds)
    - Gemini service unavailable (503)

    HTTP 503 Service Unavailable — the upstream LLM service is unreachable.
    """
    http_status = 503
    error_code  = "LLM_CONNECTION_ERROR"


class LLMGenerationError(RAGBaseError):
    """
    Raised when the Gemini API is reachable but cannot generate a response.

    Covers:
    - Rate limit exceeded (429 Too Many Requests)
    - Model not found or not available
    - Context window exceeded (prompt too long)
    - Empty response returned by the LLM
    - Any other Gemini API error during generation

    HTTP 500 — the LLM failed to produce a usable response.
    """
    http_status = 500
    error_code  = "LLM_GENERATION_ERROR"
