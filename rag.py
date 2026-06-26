"""
rag.py — Core RAG pipeline for the YouTube RAG Chatbot (Streamlit prototype).

Pipeline stages
---------------
1. Transcript ingestion  : YouTubeTranscriptApi
2. Text splitting        : RecursiveCharacterTextSplitter
3. Embedding generation  : HuggingFace all-MiniLM-L6-v2 (singleton)
4. Vector store          : FAISS
5. Retrieval             : similarity search (top-k = 4)
6. Augmentation          : ChatPromptTemplate (System + Human)
7. Generation            : Groq Cloud via ChatGroq (llama-3.1-8b-instant)

Environment variables (loaded from backend/.env or OS environment)
------------------------------------------------------------------
  GROQ_API_KEY    — Required. Groq Cloud API key (get at console.groq.com).
  MODEL_NAME      — Optional. Groq model ID. Default: llama-3.1-8b-instant.

NOTE: This file powers the Streamlit prototype (app.py).
      The production FastAPI backend lives in backend/ and has its own
      service-oriented architecture (backend/services/llm_service.py).
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Tuple

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
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
LLM_MODEL_NAME       = os.getenv("MODEL_NAME", os.getenv("LLM_MODEL_NAME", "llama-3.1-8b-instant"))
GROQ_API_KEY         = os.getenv("GROQ_API_KEY", "")
CHUNK_SIZE           = 1000
CHUNK_OVERLAP        = 200
RETRIEVER_K          = 4   # number of chunks to retrieve per question


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
_embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME, google_api_key=GROQ_API_KEY)


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
    Fetch the YouTube transcript for *video_id*, split it into chunks,
    embed each chunk with HuggingFace all-MiniLM-L6-v2, and return a
    FAISS vector store.

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
    TranscriptsDisabled
        If the video owner has disabled captions entirely.
    NoTranscriptFound
        If no English transcript is available for this video.
    ValueError
        Propagated from the transcript API for completely invalid IDs.
    """

    # ── Stage 1a : Transcript ingestion ──────────────────────────────────
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.fetch(video_id, languages=["en"])

    # Flatten snippet objects into a single plain-text string
    transcript = " ".join(chunk.text for chunk in transcript_list)

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
    answer using the Groq Cloud API (ChatGroq).

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
        If GROQ_API_KEY is not set in the environment.
    RuntimeError
        If the Groq API returns an empty or unexpected response.
    Exception
        Propagated for network errors, rate limits, or API failures.
    """

    # ── Validate API key ──────────────────────────────────────────────────
    # Re-read from environment on every call so .env changes take effect immediately.
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key in ("your_groq_api_key_here", ""):
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to backend/.env or set the GROQ_API_KEY environment variable. "
            "Get a free key at https://console.groq.com"
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

    # Build System + Human message list (better instruction-following than
    # a single PromptTemplate on chat-tuned models like LLaMA 3 and Gemma).
    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=_HUMAN_TEMPLATE.format(
            context=context_text,
            question=question,
        )),
    ]

    # ── Stage 7 : Generation via Groq ─────────────────────────────────────
    llm = ChatGroq(
        model=LLM_MODEL_NAME,
        api_key=api_key,
        temperature=0.0,
        max_tokens=1024,
    )
    response = llm.invoke(messages)

    answer: str = getattr(response, "content", "").strip()
    if not answer:
        raise RuntimeError(
            "Groq returned an empty response. "
            "Try rephrasing the question or switching models."
        )

    return answer, retrieved_docs