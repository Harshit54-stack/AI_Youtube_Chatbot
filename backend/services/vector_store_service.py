"""
vector_store_service.py — Embedding generation and FAISS vector store management.

Responsibilities
----------------
1. Hold the singleton GoogleGenerativeAIEmbeddings model (loaded once at startup).
2. Build FAISS vector stores from Document chunks.
3. Cache built vector stores in a plain dict keyed by video_id so that
   follow-up questions on the same video never re-embed the transcript.

Cache eviction
--------------
Uses a simple dict bounded by VECTOR_STORE_CACHE_SIZE (LRU-style: oldest
entry evicted when the limit is reached). This avoids the unhashable-list
problem of functools.lru_cache while giving the same semantics.
"""

from collections import OrderedDict
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

from backend.utils.exceptions import VectorStoreError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# ── Singletons ─────────────────────────────────────────────────────────────────
_embeddings: GoogleGenerativeAIEmbeddings | None = None

# Ordered dict acts as an LRU cache: video_id → FAISS
_store_cache: OrderedDict[str, FAISS] = OrderedDict()
_cache_max_size: int = 20


def initialise_embeddings(model_name: str, cache_size: int = 20) -> None:
    """
    Load the Google Generative AI embedding model into memory.

    Call this exactly once from the FastAPI lifespan context manager
    before the server starts serving requests. Subsequent calls are no-ops.

    Parameters
    ----------
    model_name : str
        Google Generative AI model identifier.
        e.g. 'models/gemini-embedding-2'
    cache_size : int
        Maximum number of video vector stores to keep in memory.
    """
    global _embeddings, _cache_max_size

    if _embeddings is not None:
        logger.debug("Embedding model already initialised — skipping.")
        return

    logger.info("Loading Google Generative AI embedding model: '%s' …", model_name)
    from backend.config import settings
    _embeddings = GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    _cache_max_size = cache_size
    logger.info("Embedding model loaded. Vector store cache size: %d.", cache_size)


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return the singleton embedding model; raise if not yet initialised."""
    if _embeddings is None:
        raise VectorStoreError(
            "Embedding model not initialised. "
            "Call initialise_embeddings() during application startup."
        )
    return _embeddings


def get_or_build_vector_store(
    video_id: str,
    chunks: List[Document],
) -> FAISS:
    """
    Return the cached FAISS vector store for *video_id*.

    On cache hit  → returns the stored index instantly (no re-embedding).
    On cache miss → embeds *chunks*, stores the index, and returns it.

    The cache is bounded by ``_cache_max_size``. When full, the oldest
    entry (LRU) is evicted to make room for the new one.

    Parameters
    ----------
    video_id : str
        Bare 11-character YouTube video ID (used as cache key).
    chunks : list[Document]
        Transcript chunks from transcript_service. Used only on cache miss.

    Returns
    -------
    FAISS
        Ready-to-query FAISS vector store.

    Raises
    ------
    VectorStoreError
        If embedding or FAISS indexing fails.
    """
    # ── Cache hit ──────────────────────────────────────────────────────────
    if video_id in _store_cache:
        _store_cache.move_to_end(video_id)   # mark as recently used
        logger.info("Vector store cache HIT for video_id='%s'.", video_id)
        return _store_cache[video_id]

    # ── Cache miss: build the vector store ────────────────────────────────
    logger.info(
        "Vector store cache MISS for video_id='%s'. Building index from %d chunks…",
        video_id,
        len(chunks),
    )
    try:
        vector_store = FAISS.from_documents(chunks, _get_embeddings())
    except Exception as exc:
        logger.error("FAISS build failed for video_id='%s': %s", video_id, exc)
        raise VectorStoreError(
            f"Failed to build vector store for video '{video_id}': {exc}"
        ) from exc

    # ── Evict oldest entry if cache is full ───────────────────────────────
    if len(_store_cache) >= _cache_max_size:
        evicted_id, _ = _store_cache.popitem(last=False)
        logger.debug("Cache full — evicted video_id='%s'.", evicted_id)

    _store_cache[video_id] = vector_store
    logger.info("FAISS index cached for video_id='%s'.", video_id)
    return vector_store
