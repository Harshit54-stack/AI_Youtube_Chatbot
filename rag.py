"""
rag.py — Core RAG pipeline for the YouTube RAG Chatbot (Streamlit prototype).

Pipeline stages
---------------
1. Transcript ingestion  : Supadata Transcript API (cloud-friendly, no IP-blocking)
2. Text splitting        : RecursiveCharacterTextSplitter
3. Embedding generation  : Google Generative AI Embeddings (gemini-embedding-2)
4. Vector store          : FAISS
5. Retrieval             : similarity search (top-k = 4)
6. Augmentation          : ChatPromptTemplate (System + Human)
7. Generation            : Google Gemini via ChatGoogleGenerativeAI

Environment variables (loaded from backend/.env or OS environment)
------------------------------------------------------------------
  GOOGLE_API_KEY    — Required. Google AI Studio API key.
  SUPADATA_API_KEY  — Required. Supadata API key (get at dash.supadata.ai).
  LLM_MODEL_NAME    — Optional. Gemini model ID. Default: gemini-2.5-flash.

NOTE: This file powers the Streamlit prototype (app.py).
      The production FastAPI backend lives in backend/ and has its own
      service-oriented architecture (backend/services/transcript_service.py).
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Tuple

import httpx
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document


# ── Environment variable loading ───────────────────────────────────────────────
# Try backend/.env first (where the real config lives), then project root .env.
_BACKEND_ENV = Path(__file__).parent / "backend" / ".env"
_ROOT_ENV    = Path(__file__).parent / ".env"

# Always reload with override=True so the latest .env values are always used.
if _BACKEND_ENV.exists():
    load_dotenv(dotenv_path=_BACKEND_ENV, override=True)
elif _ROOT_ENV.exists():
    load_dotenv(dotenv_path=_ROOT_ENV, override=True)


# ── Constants ──────────────────────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = "models/gemini-embedding-2"
LLM_MODEL_NAME       = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")
GOOGLE_API_KEY       = os.getenv("GOOGLE_API_KEY", "")
SUPADATA_API_KEY     = os.getenv("SUPADATA_API_KEY", "")
CHUNK_SIZE           = 1000
CHUNK_OVERLAP        = 200
RETRIEVER_K          = 4   # number of chunks to retrieve per question

# Supadata REST endpoint
_SUPADATA_URL        = "https://api.supadata.ai/v1/transcript"


# ── Prompt Engineering ─────────────────────────────────────────────────────────
# System prompt defines a strict, factual persona that prevents hallucinations.
# Human turn injects the retrieved transcript context and the user's question.

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

_HUMAN_TEMPLATE = """TRANSCRIPT CONTEXT
==================
{context}

==================
QUESTION: {question}

Provide a clear, accurate answer based solely on the transcript above."""


# ── Singleton embedding model ──────────────────────────────────────────────────
# Loaded once at module import time — reused across all build_vector_store() calls.
_embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME, google_api_key=GOOGLE_API_KEY)


# ── URL / ID helpers ───────────────────────────────────────────────────────────

def extract_video_id(url_or_id: str) -> str:
    """
    Accept any of the following and return the bare 11-character video ID:

    * Bare ID           : ``Gfr50f6ZBvo``
    * Standard URL      : ``https://www.youtube.com/watch?v=Gfr50f6ZBvo``
    * Shortened URL     : ``https://youtu.be/Gfr50f6ZBvo``
    * URL with extras   : ``https://www.youtube.com/watch?v=Gfr50f6ZBvo&t=30s``

    Raises
    ------
    ValueError
        If the input does not look like a valid YouTube URL or video ID.
    """
    raw = url_or_id.strip()

    # If there is no "http" prefix treat the whole string as a bare ID.
    if not raw.startswith("http"):
        if _is_valid_video_id(raw):
            return raw
        raise ValueError(
            f"'{raw}' is not a valid YouTube video ID. "
            "A video ID is typically 11 alphanumeric characters (e.g. Gfr50f6ZBvo)."
        )

    parsed = urlparse(raw)

    # ── https://youtu.be/<id> ──────────────────────────────────────────────
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.lstrip("/").split("/")[0]
        if _is_valid_video_id(video_id):
            return video_id
        raise ValueError(f"Could not extract a valid video ID from the shortened URL: {raw!r}")

    # ── https://www.youtube.com/watch?v=<id> ──────────────────────────────
    if parsed.netloc in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        qs = parse_qs(parsed.query)
        if "v" in qs:
            video_id = qs["v"][0]
            if _is_valid_video_id(video_id):
                return video_id
        raise ValueError(
            f"Could not find a 'v=' parameter in the YouTube URL: {raw!r}\n"
            "Expected format: https://www.youtube.com/watch?v=<video_id>"
        )

    raise ValueError(
        f"Unrecognised YouTube URL format: {raw!r}\n"
        "Supported formats:\n"
        "  • https://www.youtube.com/watch?v=<id>\n"
        "  • https://youtu.be/<id>\n"
        "  • Bare video ID (e.g. Gfr50f6ZBvo)"
    )


def _is_valid_video_id(video_id: str) -> bool:
    """Return True if *video_id* looks like a YouTube video ID (11 chars, alphanumeric + - _)."""
    return bool(re.fullmatch(r"[A-Za-z0-9_\-]{11}", video_id))


# ── Stage 1-4 : Build vector store ─────────────────────────────────────────────

def build_vector_store(video_id: str) -> FAISS:
    """
    Fetch the YouTube transcript for *video_id* via Supadata API, split it
    into chunks, embed each chunk with Google Generative AI Embeddings, and
    return a FAISS vector store.

    Parameters
    ----------
    video_id : str
        Bare 11-character YouTube video ID (not a URL).

    Returns
    -------
    FAISS
        An in-memory FAISS vector store ready for similarity search.

    Raises
    ------
    ValueError
        If SUPADATA_API_KEY is not set or the video URL is invalid.
    RuntimeError
        If Supadata returns an error or an empty transcript.
    """
    if not SUPADATA_API_KEY or SUPADATA_API_KEY in ("your_supadata_api_key_here", ""):
        raise ValueError(
            "SUPADATA_API_KEY is not set. "
            "Add it to backend/.env or set the SUPADATA_API_KEY environment variable. "
            "Get a free key at https://dash.supadata.ai"
        )

    # ── Stage 1a : Transcript ingestion via Supadata ──────────────────────
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    response = httpx.get(
        _SUPADATA_URL,
        params={"url": canonical_url},
        headers={"x-api-key": SUPADATA_API_KEY},
        timeout=30.0,
    )

    if response.status_code == 404:
        raise RuntimeError(
            f"No transcript found for video '{video_id}'. "
            "The video may not have captions or may be private."
        )
    if not response.is_success:
        raise RuntimeError(
            f"Supadata API error (HTTP {response.status_code}) for video '{video_id}'. "
            "Please try again later."
        )

    data = response.json()
    raw_content = data.get("content", "")
    if isinstance(raw_content, list):
        parts = [item.get("text", "") if isinstance(item, dict) else str(item) for item in raw_content]
        transcript = " ".join(parts).strip()
    else:
        transcript = str(raw_content).strip()

    if not transcript:
        raise RuntimeError(
            f"Supadata returned an empty transcript for video '{video_id}'."
        )

    # ── Stage 1b : Text splitting ─────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks: List[Document] = splitter.create_documents([transcript])

    # ── Stage 1c & 1d : Embedding + FAISS indexing ───────────────────────
    # Reuse the module-level singleton embedding model (already loaded).
    vector_store = FAISS.from_documents(chunks, _embeddings)

    return vector_store


# ── Stage 5-7 : Retrieval → Augmentation → Generation ─────────────────────────

def get_answer(
    question: str,
    vector_store: FAISS,
) -> Tuple[str, List[Document]]:
    """
    Retrieve the most relevant transcript chunks and generate a grounded
    answer using the Google Gemini API.

    Parameters
    ----------
    question     : The user's natural-language question.
    vector_store : A FAISS vector store returned by build_vector_store().

    Returns
    -------
    answer : str
        The LLM-generated answer as a plain string.
    retrieved_docs : list[Document]
        The transcript chunks used as context (for display in the UI).

    Raises
    ------
    EnvironmentError
        If GOOGLE_API_KEY is not set in the environment.
    RuntimeError
        If the Gemini API returns an empty or unexpected response.
    Exception
        Propagated for network errors, rate limits, or API failures.
    """

    # ── Validate API key ──────────────────────────────────────────────────
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key or api_key in ("your_google_api_key_here", ""):
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. "
            "Add it to backend/.env or set the GOOGLE_API_KEY environment variable. "
            "Get a free key at https://aistudio.google.com/app/apikey"
        )

    # ── Stage 5 : Retrieval ───────────────────────────────────────────────
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_K},
    )
    retrieved_docs: List[Document] = retriever.invoke(question)

    # ── Stage 6 : Augmentation ────────────────────────────────────────────
    # Build a numbered context block from retrieved chunks.
    if retrieved_docs:
        context_parts = [
            f"[Chunk {i}]\n{doc.page_content.strip()}"
            for i, doc in enumerate(retrieved_docs, start=1)
        ]
        context_text = "\n\n".join(context_parts)
    else:
        context_text = "[No transcript context was retrieved for this question.]"

    # Build System + Human message list.
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=_HUMAN_TEMPLATE.format(
            context=context_text,
            question=question,
        )),
    ]

    # ── Stage 7 : Generation via Google Gemini ────────────────────────────
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=api_key,
        temperature=0.0,
        max_tokens=1024,
    )
    response = llm.invoke(messages)

    answer: str = getattr(response, "content", "").strip()
    if not answer:
        raise RuntimeError(
            "Gemini returned an empty response. "
            "Try rephrasing the question or switching models."
        )

    return answer, retrieved_docs