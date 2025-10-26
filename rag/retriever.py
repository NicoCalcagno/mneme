"""
Retriever for semantic search in vector store

Retrieves relevant chunks from vector store based on query.
"""

from typing import List, Dict, Optional, Any
from loguru import logger

from config.settings import Settings
from ingestion.embedder import EmbeddingsGenerator
from ingestion.vectorstore import VectorStore


class Retriever:
    """
    Retrieve relevant document chunks from vector store.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize retriever.

        Args:
            settings: Settings object (will create if not provided)
        """
        self.settings = settings or Settings()

        # Initialize components
        self.embedder = EmbeddingsGenerator(self.settings)
        self.vector_store = VectorStore(self.settings)

        # Get retrieval parameters
        self.top_k = self.settings.retrieval_top_k
        self.min_score = self.settings.retrieval_min_score

        logger.info(
            f"Initialized Retriever: top_k={self.top_k}, min_score={self.min_score}"
        )

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User query
            top_k: Number of results to return (uses settings if not provided)
            min_score: Minimum similarity score (uses settings if not provided)

        Returns:
            List of relevant chunks with scores
        """
        # Use defaults from settings if not provided
        if top_k is None:
            top_k = self.top_k
        if min_score is None:
            min_score = self.min_score

        logger.info(f"Retrieving documents for query: {query[:50]}...")

        try:
            # Generate embedding for query
            query_embedding = self.embedder.embed_text(query)

            # Search vector store
            results = self.vector_store.search(
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=min_score,
            )

            logger.info(f"Retrieved {len(results)} relevant chunks")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            raise

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved results into context string for LLM.

        Args:
            results: List of retrieval results

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant information found in your notes."

        context_parts = []

        for i, result in enumerate(results, 1):
            content = result["content"]
            metadata = result.get("metadata", {})

            # Get title from metadata
            title = metadata.get("title", "Unknown")
            file_path = metadata.get("file_path", "")

            # Format chunk
            chunk_text = f"[Document {i}: {title}]\n{content}"

            # Add tags if available
            tags = metadata.get("tags", [])
            if tags:
                chunk_text += f"\nTags: {', '.join(tags)}"

            context_parts.append(chunk_text)

        context = "\n\n---\n\n".join(context_parts)
        return context

    def get_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source information from results for citations.

        Args:
            results: List of retrieval results

        Returns:
            List of source dictionaries
        """
        sources = []

        for result in results:
            metadata = result.get("metadata", {})

            source = {
                "file_path": metadata.get("file_path", "unknown"),
                "chunk_id": result.get("chunk_id", "unknown"),
                "score": result.get("score", 0.0),
                "content": result.get("content", "")[:200] + "...",  # Preview
                "metadata": {
                    "title": metadata.get("title"),
                    "tags": metadata.get("tags", []),
                    "created_at": metadata.get("created_at"),
                },
            }

            sources.append(source)

        return sources
