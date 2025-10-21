"""
FastAPI dependencies for dependency injection
"""

from functools import lru_cache
from typing import Optional
from config.settings import Settings


# Placeholder imports - will be implemented in later phases
# from rag.agent import RAGAgent
# from ingestion.vectorstore import VectorStore


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings (cached).

    Returns:
        Settings instance
    """
    return Settings()


def get_vector_store():
    """
    Get vector store instance (dependency injection).

    Returns:
        VectorStore instance
    """
    # TODO: Implement in Phase 5
    # settings = get_settings()
    # return VectorStore(settings)
    return None


def get_rag_agent():
    """
    Get RAG agent instance (dependency injection).

    Returns:
        RAGAgent instance
    """
    # TODO: Implement in Phase 7
    # settings = get_settings()
    # vector_store = get_vector_store()
    # return RAGAgent(settings, vector_store)
    return None