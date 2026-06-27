"""
transcript_service.py — YouTube transcript fetching and text splitting.

Responsibilities
----------------
1. Parse / validate YouTube URLs and extract bare video IDs.
2. Fetch the transcript via the Supadata Transcript API (cloud-friendly,
   works on Render and other cloud providers without IP-blocking issues).
3. Split the raw transcript text into overlapping chunks (LangChain Documents).

Why Supadata instead of youtube-transcript-api?
-----------------------------------------------
The open-source ``youtube-transcript-api`` library scrapes YouTube directly and
is frequently blocked by YouTube when running on cloud provider IP ranges
(Render, Railway, Heroku, etc.).  Supadata is a managed API that routes
transcript requests through its own infrastructure, eliminating the IP-blocking
problem and providing a stable, versioned REST contract.

All exceptions are converted to domain-specific errors from utils.exceptions
so that route handlers never need to import Supadata API internals.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import List

import httpx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from backend.config import settings
from backend.utils.exceptions import (
    InvalidVideoURLError,
    TranscriptDisabledError,
    TranscriptNotFoundError,
    SupadataAPIError,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Supadata REST endpoint for YouTube transcripts
_SUPADATA_URL = "https://api.supadata.ai/v1/transcript"

# Default HTTP timeout for Supadata requests (seconds)
_REQUEST_TIMEOUT = 30.0


# ── URL / ID helpers ───────────────────────────────────────────────────────────

def extract_video_id(url_or_id: str) -> str:
    """
    Parse a YouTube URL or bare video ID and return the 11-character video ID.

    Accepted formats
    ----------------
    * ``https://www.youtube.com/watch?v=Gfr50f6ZBvo``
    * ``https://www.youtube.com/watch?v=Gfr50f6ZBvo&t=30s``
    * ``https://youtu.be/Gfr50f6ZBvo``
    * ``Gfr50f6ZBvo``  (bare ID)

    Raises
    ------
    InvalidVideoURLError
        If the input cannot be resolved to a valid YouTube video ID.
    """
    raw = url_or_id.strip()

    # ── Bare ID (no http prefix) ──────────────────────────────────────────
    if not raw.startswith("http"):
        if _is_valid_video_id(raw):
            logger.debug("Input treated as bare video ID: %s", raw)
            return raw
        raise InvalidVideoURLError(
            f"'{raw}' is not a valid YouTube video ID. "
            "A video ID is 11 alphanumeric characters (e.g. Gfr50f6ZBvo)."
        )

    parsed = urlparse(raw)

    # ── https://youtu.be/<id> ─────────────────────────────────────────────
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/").split("/")[0]
        if _is_valid_video_id(video_id):
            logger.debug("Extracted video ID '%s' from short URL.", video_id)
            return video_id
        raise InvalidVideoURLError(
            f"Could not extract a valid video ID from the shortened URL: {raw!r}"
        )

    # ── https://www.youtube.com/watch?v=<id> ─────────────────────────────
    if parsed.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        qs = parse_qs(parsed.query)
        if "v" in qs:
            video_id = qs["v"][0]
            if _is_valid_video_id(video_id):
                logger.debug("Extracted video ID '%s' from standard URL.", video_id)
                return video_id
        raise InvalidVideoURLError(
            f"Could not find a valid 'v=' parameter in the YouTube URL: {raw!r}. "
            "Expected format: https://www.youtube.com/watch?v=<video_id>"
        )

    raise InvalidVideoURLError(
        f"Unrecognised YouTube URL format: {raw!r}. "
        "Supported: youtube.com/watch?v=<id>, youtu.be/<id>, or bare ID."
    )


def _is_valid_video_id(video_id: str) -> bool:
    """Return True if *video_id* matches YouTube's 11-char ID pattern."""
    return bool(re.fullmatch(r"[A-Za-z0-9_\-]{11}", video_id))


# ── Transcript fetching + splitting ────────────────────────────────────────────

def get_transcript(video_url: str) -> str:
    """
    Fetch the plain-text transcript for a YouTube video via Supadata API.

    Parameters
    ----------
    video_url : str
        Full YouTube URL or bare video ID.

    Returns
    -------
    str
        Plain transcript text (all segments joined).

    Raises
    ------
    InvalidVideoURLError
        If the URL/ID is not a valid YouTube video reference.
    TranscriptNotFoundError
        If Supadata cannot find a transcript for the video (404).
    TranscriptDisabledError
        If the video has transcripts/captions explicitly disabled.
    SupadataAPIError
        If the Supadata API is unreachable, times out, or returns an
        unexpected error.
    """
    # Build the canonical YouTube URL that Supadata expects
    video_id = extract_video_id(video_url)
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    logger.info("Fetching transcript via Supadata for video_id='%s'", video_id)

    try:
        response = httpx.get(
            _SUPADATA_URL,
            params={"url": canonical_url},
            headers={"x-api-key": settings.SUPADATA_API_KEY},
            timeout=_REQUEST_TIMEOUT,
        )
    except httpx.TimeoutException as exc:
        logger.error(
            "Supadata request timed out for video_id='%s': %s", video_id, exc
        )
        raise SupadataAPIError(
            f"The request to Supadata timed out after {_REQUEST_TIMEOUT:.0f}s "
            f"while fetching the transcript for video '{video_id}'. "
            "Please try again."
        ) from exc
    except httpx.RequestError as exc:
        logger.error(
            "Network error reaching Supadata for video_id='%s': %s", video_id, exc
        )
        raise SupadataAPIError(
            f"Could not reach the Supadata API (network error): {exc}. "
            "Check your internet connection and try again."
        ) from exc

    # ── Handle HTTP error responses ───────────────────────────────────────
    if response.status_code == 404:
        logger.warning(
            "Supadata returned 404 for video_id='%s' — no transcript available.",
            video_id,
        )
        raise TranscriptNotFoundError(
            f"No transcript was found for video '{video_id}'. "
            "The video may not have captions, or it may be private/unavailable."
        )

    if response.status_code == 400:
        logger.warning(
            "Supadata returned 400 for video_id='%s' — invalid request: %s",
            video_id,
            response.text,
        )
        raise InvalidVideoURLError(
            f"Supadata rejected the video URL as invalid for video '{video_id}'. "
            "Ensure the video is public and the URL is correct."
        )

    if response.status_code == 401 or response.status_code == 403:
        logger.error(
            "Supadata API key rejected (HTTP %d) for video_id='%s'.",
            response.status_code,
            video_id,
        )
        raise SupadataAPIError(
            "The Supadata API key is invalid or unauthorised. "
            "Check SUPADATA_API_KEY in your .env file. "
            "Get a new key at https://dash.supadata.ai"
        )

    if not response.is_success:
        logger.error(
            "Supadata returned HTTP %d for video_id='%s': %s",
            response.status_code,
            video_id,
            response.text[:200],
        )
        raise SupadataAPIError(
            f"Supadata API returned an error (HTTP {response.status_code}) "
            f"for video '{video_id}'. Please try again later."
        )

    # ── Parse JSON response ───────────────────────────────────────────────
    try:
        data = response.json()
    except Exception as exc:
        logger.error(
            "Failed to parse Supadata JSON response for video_id='%s': %s",
            video_id,
            exc,
        )
        raise SupadataAPIError(
            f"Supadata returned an unreadable response for video '{video_id}'. "
            "Please try again."
        ) from exc

    # Supadata returns { "content": [ {"text": "..."}, ... ] } or { "content": "..." }
    raw_content = data.get("content", "")
    if isinstance(raw_content, list):
        parts = [item.get("text", "") if isinstance(item, dict) else str(item) for item in raw_content]
        transcript_text = " ".join(parts)
    else:
        transcript_text = str(raw_content)

    if not transcript_text or not transcript_text.strip():
        logger.warning(
            "Supadata returned an empty transcript for video_id='%s'.", video_id
        )
        raise TranscriptNotFoundError(
            f"Supadata returned an empty transcript for video '{video_id}'. "
            "The video may not have readable captions."
        )

    logger.info(
        "Transcript fetched via Supadata for video_id='%s' (%d characters).",
        video_id,
        len(transcript_text),
    )
    return transcript_text


def fetch_and_split_transcript(
    video_id: str,
    chunk_size: int,
    chunk_overlap: int,
) -> List[Document]:
    """
    Fetch the transcript for *video_id* via Supadata and split it into
    overlapping LangChain Document chunks.

    Parameters
    ----------
    video_id     : Bare 11-character YouTube video ID.
    chunk_size   : Maximum characters per chunk.
    chunk_overlap: Character overlap between adjacent chunks.

    Returns
    -------
    list[Document]
        Non-empty list of text chunks ready for embedding.

    Raises
    ------
    TranscriptNotFoundError
        If no transcript is available for the video.
    TranscriptDisabledError
        If the video owner has disabled captions entirely.
    InvalidVideoURLError
        If the Supadata API rejects the video as invalid.
    SupadataAPIError
        If the Supadata API is unreachable or returns an unexpected error.
    """
    # Re-build canonical URL from the bare ID so get_transcript can use it
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    full_text = get_transcript(canonical_url)

    # Split into overlapping chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks: List[Document] = splitter.create_documents([full_text])
    logger.info(
        "Transcript split into %d chunks (size=%d, overlap=%d).",
        len(chunks),
        chunk_size,
        chunk_overlap,
    )

    return chunks
