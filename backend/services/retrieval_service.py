"""
retrieval_service.py — FAISS similarity retrieval.

Responsibilities
----------------
Retrieve the top-k most semantically similar transcript chunks for a
given question from a pre-built FAISS vector store.

This is a pure, stateless function — no caching, no side effects.
"""

from typing import List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.utils.exceptions import VectorStoreError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def retrieve_relevant_chunks(
    question: str,
    vector_store: FAISS,
    k: int,
) -> List[Document]:
    """
    Run a similarity search over *vector_store* and return the top-*k*
    most relevant transcript chunks.

    Parameters
    ----------
    question     : The user's natural-language question.
    vector_store : Pre-built FAISS vector store from vector_store_service.
    k            : Number of chunks to retrieve.

    Returns
    -------
    list[Document]
        Retrieved transcript chunks, ordered by descending similarity.

    Raises
    ------
    VectorStoreError
        If the similarity search fails (e.g. corrupt index).
    """
    logger.debug("Retrieving top-%d chunks for question: '%s'", k, question[:80])

    try:
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k},
        )
        docs: List[Document] = retriever.invoke(question)
    except Exception as exc:
        logger.error("Similarity search failed: %s", exc)
        raise VectorStoreError(
            f"Retrieval failed during similarity search: {exc}"
        )

    logger.debug("Retrieved %d chunks.", len(docs))
    return docs
