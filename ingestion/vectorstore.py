"""
Vector Store Integration using Datapizza AI

Manages storage and retrieval of embeddings in Qdrant using:
- datapizza-ai-vectorstores-qdrant for Qdrant integration
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from loguru import logger
import hashlib

from config.settings import Settings
from ingestion.chunker import TextChunk

# Datapizza AI imports
from datapizza.vectorstores.qdrant import QdrantVectorstore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct


class VectorStore:
    """
    Manage embeddings storage and retrieval in Qdrant.
    Uses Datapizza AI's QdrantVectorStore.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize vector store with settings.

        Args:
            settings: Settings object (will create if not provided)
        """
        self.settings = settings or Settings()

        # Get vector store configuration
        self.collection_name = self.settings.vector_store_collection
        self.dimensions = self.settings.embedding_dimensions

        # Initialize Qdrant client and vector store
        self.client = self._init_qdrant_client()
        self.vector_store = self._init_vector_store()

        # Ensure collection exists
        self._ensure_collection()

        logger.info(
            f"Initialized VectorStore: collection={self.collection_name}, "
            f"dimensions={self.dimensions}"
        )

    def _init_qdrant_client(self) -> QdrantClient:
        """
        Initialize Qdrant client based on configuration.

        Returns:
            QdrantClient instance
        """
        # Check if using cloud or local
        if self.settings.qdrant_url:
            # Qdrant Cloud
            logger.info(f"Connecting to Qdrant Cloud: {self.settings.qdrant_url}")
            client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
                prefer_grpc=self.settings.qdrant_prefer_grpc,
            )
        else:
            # Local Qdrant
            qdrant_path = Path(self.settings.qdrant_path)
            qdrant_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Using local Qdrant: {qdrant_path}")
            client = QdrantClient(path=str(qdrant_path))

        return client

    def _init_vector_store(self) -> QdrantVectorstore:
        """
        Initialize Datapizza AI's QdrantVectorstore.

        Returns:
            QdrantVectorstore instance
        """
        # Use host or location based on settings
        if self.settings.qdrant_url:
            # Remote Qdrant
            vector_store = QdrantVectorstore(
                host=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
            )
        else:
            # Local Qdrant
            vector_store = QdrantVectorstore(
                location=self.settings.qdrant_path,
            )

        return vector_store

    def _ensure_collection(self):
        """
        Ensure collection exists, create if not.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimensions,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Collection created: {self.collection_name}")
            else:
                logger.info(f"Collection exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")
            raise

    def upsert_chunks(
        self,
        chunks: List[TextChunk],
        embeddings: List[List[float]],
    ) -> int:
        """
        Insert or update chunks with their embeddings in the vector store.

        Args:
            chunks: List of TextChunk objects
            embeddings: List of embedding vectors

        Returns:
            Number of chunks upserted
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        logger.info(f"Upserting {len(chunks)} chunks to vector store...")

        points = []
        for chunk, embedding in zip(chunks, embeddings):
            # Create point with chunk data
            # Generate positive integer ID from chunk_id using MD5 hash
            chunk_hash = int(hashlib.md5(chunk.chunk_id.encode()).hexdigest()[:15], 16)

            point = PointStruct(
                id=chunk_hash,  # Use positive hash as numeric ID
                vector=embedding,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "token_count": chunk.token_count,
                    **chunk.metadata,  # Include all metadata
                },
            )
            points.append(point)

        try:
            # Upsert points in batches
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
                logger.debug(f"Upserted batch {i // batch_size + 1}/{(len(points) + batch_size - 1) // batch_size}")

            logger.info(f"Successfully upserted {len(chunks)} chunks")
            return len(chunks)

        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            raise

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of matching chunks with scores
        """
        try:
            # Use score threshold from settings if not provided
            if score_threshold is None:
                score_threshold = self.settings.retrieval_min_score

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "id": result.id,
                        "score": result.score,
                        "chunk_id": result.payload.get("chunk_id"),
                        "content": result.payload.get("content"),
                        "metadata": {
                            k: v
                            for k, v in result.payload.items()
                            if k not in ["chunk_id", "content"]
                        },
                    }
                )

            logger.debug(f"Found {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search vector store: {e}")
            raise

    def delete_by_filter(self, filter_dict: Dict[str, Any]) -> bool:
        """
        Delete chunks matching a filter.

        Args:
            filter_dict: Filter criteria

        Returns:
            True if successful
        """
        try:
            # Note: Implementation depends on Qdrant filter syntax
            # This is a placeholder - adjust based on actual usage
            logger.info(f"Deleting chunks with filter: {filter_dict}")
            # self.client.delete(collection_name=self.collection_name, ...)
            return True

        except Exception as e:
            logger.error(f"Failed to delete chunks: {e}")
            raise

    def count(self) -> int:
        """
        Count total number of vectors in collection.

        Returns:
            Number of vectors
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count

        except Exception as e:
            logger.error(f"Failed to count vectors: {e}")
            return 0

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Collection metadata
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            return {
                "name": collection.name,
                "points_count": collection.points_count,
                "vectors_count": collection.vectors_count,
                "status": collection.status,
            }

        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
