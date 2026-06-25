"""
llm_service.py — Production-grade Google Gemini LLM integration for answer generation.

Responsibilities
----------------
1. Build an anti-hallucination prompt from retrieved context + user question.
2. Call the Gemini API via langchain-google-genai ChatGoogleGenerativeAI with timeout & retry logic.
3. Return the answer as a plain string.
4. Map every possible Gemini / network error to a typed domain exception.
5. Support runtime model switching — callers pass model_name explicitly.

Prompt Engineering Philosophy
------------------------------
The prompt is designed to:
  * Ground the LLM in the retrieved transcript chunks ONLY.
  * Explicitly forbid fabrication with a numbered ruleset the model can follow.
  * Detect when the context is empty or insufficient and return a graceful message.
  * Return concise, direct answers — no padding or hallucinated filler.
  * Format the answer as plain prose (no markdown unless the content warrants it).

Supported Gemini models (configure via LLM_MODEL_NAME in .env)
---------------------------------------------------------------
  gemini-2.5-flash    — best balance of speed & quality  ← DEFAULT
  gemini-2.5-pro      — highest quality, complex reasoning
  gemini-2.0-flash    — fast, efficient, multimodal
  gemini-1.5-flash    — stable, 1M token context window
  gemini-1.5-pro      — stable pro, 2M token context window
"""

import time
from typing import List

import httpx
from langchain_google_genai import ChatGoogleGenerativeAI  # ← CHANGED: was ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document

from backend.utils.exceptions import LLMConnectionError, LLMGenerationError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# ── System prompt (constant — defines LLM persona and strict rules) ────────────
_SYSTEM_PROMPT = """You are a precise, factual assistant that answers questions \
exclusively using content from YouTube video transcripts.

STRICT RULES — follow without exception:
1. Answer ONLY from the provided transcript context. Never use outside knowledge.
2. If the context is empty or clearly insufficient, respond with:
   "I cannot answer this question based on the available transcript."
3. If the context partially covers the question, answer what you can and note \
what is missing.
4. Do NOT fabricate names, statistics, dates, quotes, or any facts.
5. Be concise and direct — avoid padding, filler phrases, or unnecessary repetition.
6. Use plain prose. Avoid markdown formatting unless listing multiple items.
7. Never say "based on the context" or "according to the transcript" repeatedly — \
state facts directly.
8. If the question is ambiguous, answer the most reasonable interpretation."""

# ── Human turn template (context + question) ──────────────────────────────────
_HUMAN_TEMPLATE = """TRANSCRIPT CONTEXT
==================
{context}

==================
QUESTION: {question}

Provide a clear, accurate answer based solely on the transcript above."""


def _build_prompt(context: str, question: str) -> List:
    """
    Construct a two-turn ChatPromptTemplate message list.

    Using a system + human structure (instead of a single PromptTemplate)
    improves instruction-following on chat-tuned models like Gemini.
    """
    return [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=_HUMAN_TEMPLATE.format(
            context=context,
            question=question,
        )),
    ]


def _format_context(retrieved_docs: List[Document]) -> str:
    """
    Merge retrieved transcript chunks into a single numbered context block.

    Numbering helps the LLM attribute information to specific chunks and
    makes it easier to notice when chunks are thematically unrelated to
    the question (a signal that the context may be insufficient).
    """
    if not retrieved_docs:
        return "[No transcript context was retrieved for this question.]"

    parts = []
    for i, doc in enumerate(retrieved_docs, start=1):
        parts.append(f"[Chunk {i}]\n{doc.page_content.strip()}")

    return "\n\n".join(parts)


def _classify_error(error_msg: str, exc: Exception) -> None:
    """
    Inspect *error_msg* and raise the most specific domain exception.

    Called inside the main except block of generate_answer so every
    error path raises a typed RAGBaseError (never a bare Exception).
    Handles Gemini-specific error codes and messages.
    """
    msg_lower = error_msg.lower()

    # ── Missing API key ────────────────────────────────────────────────────
    if any(kw in msg_lower for kw in ("api_key_invalid", "api key not valid", "missing api key")):
        raise LLMConnectionError(
            "Google API key is missing or invalid. "
            "Verify GOOGLE_API_KEY in your .env file. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        ) from exc

    # ── Authentication / Authorization errors ─────────────────────────────
    if any(kw in msg_lower for kw in ("unauthorized", "401", "permission_denied", "403")):
        raise LLMConnectionError(
            "Invalid Google API key or insufficient permissions. "
            "Verify GOOGLE_API_KEY in your .env matches https://aistudio.google.com/app/apikey"
        ) from exc

    # ── Quota exceeded ─────────────────────────────────────────────────────
    if any(kw in msg_lower for kw in ("quota_exceeded", "quota exceeded", "resource_exhausted")):
        raise LLMGenerationError(
            "Google Gemini API quota exceeded. "
            "Check your quota at https://aistudio.google.com or wait and retry. "
            "Consider upgrading your Google Cloud quota limits."
        ) from exc

    # ── Rate limiting ──────────────────────────────────────────────────────
    if any(kw in msg_lower for kw in ("rate_limit", "rate limit", "429", "too many")):
        raise LLMGenerationError(
            "Google Gemini API rate limit exceeded. "
            "Wait 60 seconds, then try again. "
            "Consider switching to gemini-2.0-flash for higher rate limits."
        ) from exc

    # ── Context / token limit ──────────────────────────────────────────────
    if any(kw in msg_lower for kw in ("context_length", "max_tokens", "too long", "413", "token")):
        raise LLMGenerationError(
            "The transcript context exceeds the model's context window. "
            "Try a shorter video or switch to gemini-1.5-pro (2M context)."
        ) from exc

    # ── Model not found ────────────────────────────────────────────────────
    if any(kw in msg_lower for kw in ("model_not_found", "does not exist", "404", "not found")):
        raise LLMGenerationError(
            f"Gemini model not found: {error_msg}. "
            "Check LLM_MODEL_NAME in your .env. "
            "Valid models: gemini-2.5-flash, gemini-2.5-pro, gemini-1.5-flash."
        ) from exc

    # ── Service unavailable / overloaded ──────────────────────────────────
    if any(kw in msg_lower for kw in ("503", "502", "overloaded", "unavailable", "service_unavailable")):
        raise LLMConnectionError(
            "Google Gemini API is temporarily unavailable. "
            "This is likely a transient issue — retry in a few seconds."
        ) from exc

    # ── Generic fallback ───────────────────────────────────────────────────
    raise LLMGenerationError(
        f"Google Gemini API returned an unexpected error: {error_msg}"
    ) from exc


def generate_answer(
    question: str,
    retrieved_docs: List[Document],
    model_name: str,
    api_key: str,
    temperature: float = 0.0,
    max_tokens: int = 1024,
    timeout: int = 60,
    max_retries: int = 2,
) -> str:
    """
    Build an anti-hallucination prompt from *retrieved_docs* and call Google Gemini
    to generate a grounded answer.

    Parameters
    ----------
    question       : The user's natural-language question.
    retrieved_docs : Transcript chunks retrieved from FAISS.
    model_name     : Gemini model ID (e.g. 'gemini-2.5-flash').  ← CHANGED
    api_key        : Google API key from settings.               ← CHANGED
    temperature    : Sampling temperature (0.0 = deterministic).
    max_tokens     : Maximum tokens to generate in the response.
    timeout        : HTTP timeout in seconds for the Gemini API call.
    max_retries    : Automatic retries on transient network errors.

    Returns
    -------
    str
        The LLM-generated answer as a plain string.

    Raises
    ------
    LLMConnectionError
        If the Gemini API is unreachable, the key is invalid/missing, or the
        call times out after all retries.
    LLMGenerationError
        If the API returns an error during generation (rate limit, quota exceeded,
        bad model, context too long, etc.).
    """
    # ── Stage 1: Format context ────────────────────────────────────────────
    context_text = _format_context(retrieved_docs)

    logger.info(
        "Generating answer | model='%s' | chunks=%d | context_chars=%d | question='%s'",
        model_name,
        len(retrieved_docs),
        len(context_text),
        question[:80],
    )

    # ── Stage 2: Build chat prompt ─────────────────────────────────────────
    messages = _build_prompt(context=context_text, question=question)

    # ── Stage 3: Initialise ChatGoogleGenerativeAI client ─────────────────
    # ← CHANGED: was ChatGroq(model=..., api_key=..., ...)
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,   # Gemini uses max_output_tokens
            timeout=timeout,
            max_retries=max_retries,
        )
    except Exception as exc:
        logger.error("Failed to initialise ChatGoogleGenerativeAI client: %s", exc)
        raise LLMConnectionError(
            f"Could not initialise the Gemini LLM client: {exc}. "
            "Check GOOGLE_API_KEY and LLM_MODEL_NAME in your .env file."
        ) from exc

    # ── Stage 4: Call Gemini API ───────────────────────────────────────────
    start_time = time.perf_counter()

    try:
        response = llm.invoke(messages)

    except httpx.ConnectError as exc:
        logger.error("Network error connecting to Gemini API: %s", exc)
        raise LLMConnectionError(
            "Cannot reach the Google Gemini API. "
            "Check your internet connection and ensure generativelanguage.googleapis.com is reachable."
        ) from exc

    except httpx.TimeoutException as exc:
        logger.error("Gemini API call timed out after %ds: %s", timeout, exc)
        raise LLMConnectionError(
            f"The Gemini API call timed out after {timeout} seconds. "
            "Try increasing LLM_TIMEOUT in your .env, "
            "or switch to a faster model like gemini-2.0-flash."
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.error("Gemini HTTP error %d: %s", exc.response.status_code, exc)
        _classify_error(str(exc), exc)

    except Exception as exc:
        error_msg = str(exc)
        logger.error("Gemini generation error: %s", error_msg, exc_info=True)
        _classify_error(error_msg, exc)

    # ── Stage 5: Extract and validate response ─────────────────────────────
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    answer: str = getattr(response, "content", "").strip()

    if not answer:
        logger.warning("Gemini returned an empty response for question: '%s'", question[:80])
        raise LLMGenerationError(
            "The LLM returned an empty response. "
            "This may be caused by safety filters or a context issue. "
            "Try rephrasing the question."
        )

    # Log token usage if Gemini included it in the response metadata
    usage = getattr(response, "response_metadata", {}).get("usage_metadata", {})
    if usage:
        logger.info(
            "Gemini response | model='%s' | prompt_tokens=%s | completion_tokens=%s "
            "| total_tokens=%s | latency_ms=%.1f",
            model_name,
            usage.get("prompt_token_count", "?"),
            usage.get("candidates_token_count", "?"),
            usage.get("total_token_count", "?"),
            elapsed_ms,
        )
    else:
        logger.info(
            "Answer generated | model='%s' | chars=%d | latency_ms=%.1f",
            model_name,
            len(answer),
            elapsed_ms,
        )

    return answer
