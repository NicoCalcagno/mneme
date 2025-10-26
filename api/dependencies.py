"""
FastAPI dependencies for dependency injection
"""

from functools import lru_cache
from config.settings import Settings
from rag.agent import RAGAgent
from ingestion.vectorstore import VectorStore


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).

    Returns:
        Settings instance
    """
    return Settings()


@lru_cache()
def get_vector_store() -> VectorStore:
    """
    Get vector store instance (dependency injection).

    Returns:
        VectorStore instance
    """
    settings = get_settings()
    return VectorStore(settings)


@lru_cache()
def get_rag_agent() -> RAGAgent:
    """
    Get RAG agent instance (dependency injection).

    Returns:
        RAGAgent instance
    """
    settings = get_settings()
    return RAGAgent(settings)