"""
rag.py — RAGService: single orchestration facade for the full pipeline.

This class is the only thing that route handlers in main.py talk to.
It wires together the four service modules in the correct order and
returns a clean, typed result ready for Pydantic serialisation.

Pipeline
--------
1. transcript_service  : extract_video_id → fetch_and_split_transcript
2. vector_store_service: get_or_build_vector_store
3. retrieval_service   : retrieve_relevant_chunks
4. llm_service         : generate_answer  (Google Gemini)
"""

from typing import Tuple, List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.config import settings
from backend.services.transcript_service import (
    extract_video_id,
    fetch_and_split_transcript,
)
from backend.services.vector_store_service import get_or_build_vector_store
from backend.services.retrieval_service import retrieve_relevant_chunks
from backend.services.llm_service import generate_answer
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Stateless orchestrator for the Retrieval-Augmented Generation pipeline.

    All heavy work is delegated to the service modules. This class only
    sequences calls and passes data between them — no business logic lives here.

    Usage
    -----
    ::

        rag = RAGService()
        answer, video_id, docs = rag.ask(video_url, question)
    """

    def ask(
        self,
        video_url: str,
        question: str,
    ) -> Tuple[str, str, List[Document]]:
        """
        Run the full RAG pipeline for one question about one video.

        Parameters
        ----------
        video_url : str
            Full YouTube URL or bare video ID supplied by the client.
        question  : str
            The user's natural-language question.

        Returns
        -------
        answer : str
            LLM-generated answer grounded in the transcript.
        video_id : str
            Resolved 11-character YouTube video ID.
        retrieved_docs : list[Document]
            Transcript chunks used as context (for the sources field).

        Raises
        ------
        InvalidVideoURLError
            Bad URL / video ID.
        TranscriptDisabledError
            Video captions are disabled.
        TranscriptNotFoundError
            No English transcript available.
        VectorStoreError
            FAISS build or retrieval failure.
        LLMConnectionError
            Cannot reach the Google Gemini API.
        LLMGenerationError
            Gemini API returned an error.
        """
        # ── Stage 1 : Resolve video ID ────────────────────────────────────
        video_id = extract_video_id(video_url)
        logger.info(
            "RAGService.ask | video_id='%s' | model='%s' | question='%s'",
            video_id,
            settings.LLM_MODEL_NAME,
            question[:80],
        )

        # ── Stage 2 : Fetch transcript + split into chunks ─────────────────
        chunks = fetch_and_split_transcript(
            video_id=video_id,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        # ── Stage 3 : Build / retrieve cached FAISS vector store ──────────
        vector_store: FAISS = get_or_build_vector_store(
            video_id=video_id,
            chunks=chunks,
        )

        # ── Stage 4 : Retrieve top-k relevant chunks ───────────────────────
        retrieved_docs: List[Document] = retrieve_relevant_chunks(
            question=question,
            vector_store=vector_store,
            k=settings.RETRIEVER_K,
        )

        # ── Stage 5 : Generate answer via Google Gemini ───────────────────
        answer = generate_answer(
            question=question,
            retrieved_docs=retrieved_docs,
            model_name=settings.LLM_MODEL_NAME,
            api_key=settings.GOOGLE_API_KEY,   # ← CHANGED: was GROQ_API_KEY
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
        )

        logger.info(
            "RAGService.ask complete | video_id='%s' | answer_chars=%d",
            video_id,
            len(answer),
        )

        return answer, video_id, retrieved_docs


# Module-level singleton — imported by main.py
rag_service = RAGService()
