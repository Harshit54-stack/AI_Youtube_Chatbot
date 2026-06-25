"""
transcript_service.py — YouTube transcript fetching and text splitting.

Responsibilities
----------------
1. Parse / validate YouTube URLs and extract bare video IDs.
2. Fetch the English transcript via YouTubeTranscriptApi.
3. Split the raw transcript text into overlapping chunks (LangChain Documents).

All exceptions are converted to domain-specific errors from utils.exceptions
so that route handlers never need to import YouTube API internals.
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import List

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from backend.utils.exceptions import (
    InvalidVideoURLError,
    TranscriptDisabledError,
    TranscriptNotFoundError,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)


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

def fetch_and_split_transcript(
    video_id: str,
    chunk_size: int,
    chunk_overlap: int,
) -> List[Document]:
    """
    Fetch the English transcript for *video_id* and split it into
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
    TranscriptDisabledError
        If the video owner has disabled captions entirely.
    TranscriptNotFoundError
        If no English transcript is available.
    InvalidVideoURLError
        If the transcript API rejects the video ID as invalid.
    """
    logger.info("Fetching transcript for video_id='%s'", video_id)

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id, languages=["en"])
    except TranscriptsDisabled:
        logger.warning("Transcripts disabled for video_id='%s'", video_id)
        raise TranscriptDisabledError(
            f"The video '{video_id}' has transcripts/captions disabled. "
            "This app requires an English transcript to answer questions."
        )
    except NoTranscriptFound:
        logger.warning("No English transcript for video_id='%s'", video_id)
        raise TranscriptNotFoundError(
            f"No English transcript was found for video '{video_id}'. "
            "Try a video that has English captions enabled."
        )
    except Exception as exc:
        logger.error("Transcript fetch failed for video_id='%s': %s", video_id, exc)
        raise InvalidVideoURLError(
            f"Could not fetch transcript for video '{video_id}': {exc}. "
            "Ensure the video is public and the ID is correct."
        )

    # Flatten snippet objects → single plain-text string
    full_text = " ".join(snippet.text for snippet in transcript_list)
    logger.info(
        "Transcript fetched for video_id='%s' (%d characters).",
        video_id,
        len(full_text),
    )

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
