"""
config.py — Centralised configuration for the YouTube RAG Chatbot backend.

All values are read from the .env file (or environment variables).
Import `settings` anywhere in the project — never call os.getenv() directly.

Google Gemini model catalogue (as of June 2026)
------------------------------------------------
Production / recommended:
  gemini-2.5-flash           — Best balance of speed & quality  ← DEFAULT
  gemini-2.5-pro             — Highest quality, complex reasoning
  gemini-2.0-flash           — Fast, efficient, multimodal
  gemini-1.5-flash           — Stable, 1M token context window
  gemini-1.5-pro             — Stable pro, 2M token context window
"""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

# Resolve .env path relative to this file so that uvicorn launched from
# *any* working directory (project root or backend/) finds it correctly.
_ENV_FILE = Path(__file__).parent / ".env"


# ── Supported Gemini models ────────────────────────────────────────────────────
# These are validated at startup to prevent silent misconfigurations.
SUPPORTED_GEMINI_MODELS: List[str] = [
    # Gemini 2.5 (latest generation — recommended)
    "gemini-2.5-flash",           # Best balance of speed & quality ← DEFAULT
    "gemini-2.5-pro",             # Highest quality, complex reasoning
    # Gemini 2.0
    "gemini-2.0-flash",           # Fast, efficient, multimodal
    "gemini-2.0-flash-lite",      # Lightest 2.0 model
    # Gemini 1.5 (stable)
    "gemini-1.5-flash",           # 1M token context window
    "gemini-1.5-flash-8b",        # Smallest 1.5 model
    "gemini-1.5-pro",             # 2M token context window
]


class Settings(BaseSettings):
    """
    Application settings driven entirely by environment variables / .env file.
    Pydantic-settings handles type coercion and validation automatically.

    Priority (highest → lowest):
      1. Actual OS environment variables
      2. backend/.env file
      3. Field defaults defined below
    """

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),      # always resolves to backend/.env
        env_file_encoding="utf-8",
        case_sensitive=False,          # GOOGLE_API_KEY == google_api_key
        extra="ignore",                # silently ignore unknown .env keys
    )

    # ── Google Gemini ──────────────────────────────────────────────────────────
    GOOGLE_API_KEY: str = Field(
        ...,                           # required — no default
        description="Google AI Studio API key. Get one at https://aistudio.google.com/app/apikey",
    )
    LLM_MODEL_NAME: str = Field(
        default="gemini-2.5-flash",    # ← CHANGED: was llama-3.1-8b-instant (Groq)
        description=(
            "Gemini model ID. Recommended options:\n"
            "  gemini-2.5-flash  (best balance — default)\n"
            "  gemini-2.5-pro    (highest quality)\n"
            "  gemini-2.0-flash  (fast & multimodal)\n"
            "  gemini-1.5-flash  (stable, 1M context)"
        ),
    )
    LLM_TEMPERATURE: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature. 0.0 = deterministic, 1.0 = creative.",
    )
    LLM_MAX_TOKENS: int = Field(
        default=1024,
        ge=64,
        le=8192,
        description="Maximum tokens the LLM may generate per response.",
    )
    LLM_TIMEOUT: int = Field(
        default=60,
        ge=10,
        le=300,
        description="Seconds before an LLM call is considered timed out.",
    )
    LLM_MAX_RETRIES: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Number of automatic retries on transient Gemini errors.",
    )

    # ── Embeddings ────────────────────────────────────────────────────────────
    EMBEDDING_MODEL_NAME: str = Field(
        default="models/gemini-embedding-2",
        description="Google Generative AI embedding model.",
    )

    # ── Text splitting ────────────────────────────────────────────────────────
    CHUNK_SIZE: int = Field(
        default=1000,
        ge=100,
        le=8000,
        description="Maximum characters per transcript chunk.",
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        ge=0,
        le=2000,
        description="Character overlap between adjacent chunks.",
    )

    # ── Retrieval ─────────────────────────────────────────────────────────────
    RETRIEVER_K: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Number of transcript chunks to retrieve per question.",
    )

    # ── Vector store cache ────────────────────────────────────────────────────
    VECTOR_STORE_CACHE_SIZE: int = Field(
        default=20,
        ge=1,
        le=500,
        description="Maximum number of video vector stores held in memory.",
    )

    # ── API / Server ──────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description=(
            "Allowed CORS origins. Add your React dev URL. "
            "Use [\"*\"] only in development."
        ),
    )
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging verbosity: DEBUG | INFO | WARNING | ERROR | CRITICAL",
    )
    APP_ENV: str = Field(
        default="development",
        description="Deployment environment: development | staging | production",
    )

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def google_api_key_must_not_be_placeholder(cls, v: str) -> str:
        """Reject the placeholder value so devs get a clear startup error."""
        if not v or v.strip() in ("your_google_api_key_here", ""):
            raise ValueError(
                "GOOGLE_API_KEY is not set. "
                "Add it to backend/.env or set the environment variable. "
                "Get a free key at https://aistudio.google.com/app/apikey"
            )
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def log_level_must_be_valid(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(
                f"LOG_LEVEL must be one of {valid}, got '{v}'."
            )
        return upper

    @field_validator("APP_ENV")
    @classmethod
    def app_env_must_be_valid(cls, v: str) -> str:
        valid = {"development", "staging", "production"}
        lower = v.lower()
        if lower not in valid:
            raise ValueError(
                f"APP_ENV must be one of {valid}, got '{v}'."
            )
        return lower

    # ── Derived helpers (not stored in .env) ─────────────────────────────────

    @property
    def is_production(self) -> bool:
        """True when running in the production environment."""
        return self.APP_ENV == "production"

    @property
    def supported_models(self) -> List[str]:
        """Return the catalogue of known Gemini model IDs."""
        return SUPPORTED_GEMINI_MODELS


# Module-level singleton — import this everywhere; never re-instantiate.
settings = Settings()
