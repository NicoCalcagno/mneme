"""
Embeddings Generator using Datapizza AI

Generates embeddings for text chunks using:
- OpenAI embeddings via datapizza-ai-embedders-openai
- Support for batch processing
"""

from typing import List, Optional
from loguru import logger

from config.settings import Settings
from ingestion.chunker import TextChunk

# Datapizza AI imports
from datapizza.embedders.openai import OpenAIEmbedder


class EmbeddingsGenerator:
    """
    Generate embeddings for text chunks using Datapizza AI.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize embeddings generator with settings.

        Args:
            settings: Settings object (will create if not provided)
        """
        self.settings = settings or Settings()

        # Get embedding configuration from settings
        self.provider = self.settings.embedding_provider
        self.model = self.settings.embedding_model
        self.dimensions = self.settings.embedding_dimensions
        self.batch_size = self.settings.embedding_batch_size

        # Initialize embedder based on provider
        if self.provider == "openai":
            self.embedder = self._init_openai_embedder()
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

        logger.info(
            f"Initialized EmbeddingsGenerator: provider={self.provider}, "
            f"model={self.model}, dimensions={self.dimensions}"
        )

    def _init_openai_embedder(self) -> OpenAIEmbedder:
        """
        Initialize OpenAI embedder using Datapizza AI.

        Returns:
            OpenAIEmbedder instance
        """
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        embedder = OpenAIEmbedder(
            api_key=self.settings.openai_api_key,
            model_name=self.model,
        )

        logger.info(f"Initialized OpenAI embedder: {self.model}")
        return embedder

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.embedder.embed(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []

        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]

            try:
                # Use embed() which accepts list[str] and returns list[list[float]]
                batch_embeddings = self.embedder.embed(batch)
                embeddings.extend(batch_embeddings)

                logger.debug(
                    f"Generated embeddings for batch {i // self.batch_size + 1} "
                    f"({len(batch)} texts)"
                )
            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch: {e}")
                raise

        return embeddings

    def embed_chunks(self, chunks: List[TextChunk]) -> List[tuple[TextChunk, List[float]]]:
        """
        Generate embeddings for text chunks.

        Args:
            chunks: List of TextChunk objects

        Returns:
            List of tuples (chunk, embedding)
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks...")

        # Extract text from chunks
        texts = [chunk.content for chunk in chunks]

        # Generate embeddings in batches
        embeddings = self.embed_batch(texts)

        # Pair chunks with their embeddings
        result = list(zip(chunks, embeddings))

        logger.info(f"Generated {len(embeddings)} embeddings")
        return result
