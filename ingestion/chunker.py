"""
Text Chunking Module

Splits text into chunks for embeddings with support for:
- Page-level chunking (keeps entire documents)
- Recursive chunking (respects markdown structure)
- Fixed-size chunking
- Semantic chunking (sentence-aware)
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from loguru import logger

from config.settings import Settings


@dataclass
class TextChunk:
    """Represents a text chunk with metadata"""

    content: str
    chunk_id: str
    start_char: int
    end_char: int
    metadata: Dict
    token_count: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert chunk to dictionary"""
        return {
            "content": self.content,
            "chunk_id": self.chunk_id,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "token_count": self.token_count,
            "metadata": self.metadata,
        }


class TextChunker:
    """
    Split text into chunks for embeddings.

    Strategies:
    - page: Keep entire document as one chunk
    - recursive: Split by structure (paragraphs → sentences → words)
    - fixed: Fixed-size chunks with overlap
    - semantic: Split at sentence boundaries
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize chunker with settings from environment.

        Args:
            settings: Settings object (will create if not provided)
        """
        self.settings = settings or Settings()

        # Get chunking parameters from settings
        self.chunk_size = self.settings.chunk_size
        self.chunk_overlap = self.settings.chunk_overlap
        self.strategy = self.settings.chunking_strategy

        # Separators for recursive splitting (in order of preference)
        self.separators = [
            "\n\n\n",  # Multiple blank lines
            "\n\n",    # Paragraph breaks
            "\n",      # Single newlines
            ". ",      # Sentences
            "! ",      # Exclamations
            "? ",      # Questions
            "; ",      # Semicolons
            ", ",      # Commas
            " ",       # Spaces
            "",        # Characters
        ]

        logger.info(
            f"Initialized TextChunker: strategy={self.strategy}, "
            f"chunk_size={self.chunk_size}, overlap={self.chunk_overlap}"
        )

    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        note_id: Optional[str] = None,
    ) -> List[TextChunk]:
        """
        Split text into chunks based on configured strategy.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            note_id: Unique identifier for the note

        Returns:
            List of TextChunk objects
        """
        if metadata is None:
            metadata = {}

        if note_id is None:
            note_id = "unknown"

        if self.strategy == "page":
            return self._page_chunk(text, metadata, note_id)
        elif self.strategy == "recursive":
            return self._recursive_chunk(text, metadata, note_id)
        elif self.strategy == "fixed":
            return self._fixed_chunk(text, metadata, note_id)
        elif self.strategy == "semantic":
            return self._semantic_chunk(text, metadata, note_id)
        else:
            logger.warning(f"Unknown strategy '{self.strategy}', using page")
            return self._page_chunk(text, metadata, note_id)

    def _page_chunk(
        self,
        text: str,
        metadata: Dict,
        note_id: str,
    ) -> List[TextChunk]:
        """
        Keep the entire document as a single chunk.

        Best for:
        - Small notes that fit within context window
        - Maintaining full document context
        - Preserving document structure
        """
        text = text.strip()

        if not text:
            return []

        chunk = TextChunk(
            content=text,
            chunk_id=f"{note_id}_page",
            start_char=0,
            end_char=len(text),
            metadata={
                **metadata,
                "chunk_index": 0,
                "total_chunks": 1,
                "chunking_strategy": "page",
            },
            token_count=self._estimate_tokens(text),
        )

        logger.debug(f"Created page chunk: {note_id} ({len(text)} chars)")
        return [chunk]

    def _recursive_chunk(
        self,
        text: str,
        metadata: Dict,
        note_id: str,
    ) -> List[TextChunk]:
        """
        Recursively split text using separators in order of preference.
        Preserves document structure better than fixed chunking.
        """
        chunks = []
        current_chunks = [text]

        for separator in self.separators:
            next_chunks = []

            for chunk in current_chunks:
                if len(chunk) <= self.chunk_size:
                    next_chunks.append(chunk)
                else:
                    # Split by separator
                    splits = chunk.split(separator)
                    merged = []
                    current = ""

                    for i, split in enumerate(splits):
                        # Add separator back (except for last split)
                        if i < len(splits) - 1:
                            split = split + separator

                        if len(current) + len(split) <= self.chunk_size:
                            current += split
                        else:
                            if current:
                                merged.append(current)
                            current = split

                    if current:
                        merged.append(current)

                    next_chunks.extend(merged)

            current_chunks = next_chunks

            # If all chunks are small enough, we're done
            if all(len(c) <= self.chunk_size for c in current_chunks):
                break

        # Create TextChunk objects
        position = 0
        for i, chunk_text in enumerate(current_chunks):
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue

            # Find actual position in original text
            start_char = text.find(chunk_text, position)
            if start_char == -1:
                start_char = position
            end_char = start_char + len(chunk_text)

            chunk = TextChunk(
                content=chunk_text,
                chunk_id=f"{note_id}_chunk_{i}",
                start_char=start_char,
                end_char=end_char,
                metadata={
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(current_chunks),
                    "chunking_strategy": "recursive",
                },
                token_count=self._estimate_tokens(chunk_text),
            )
            chunks.append(chunk)

            position = end_char

        logger.debug(f"Created {len(chunks)} chunks (recursive)")
        return chunks

    def _fixed_chunk(
        self,
        text: str,
        metadata: Dict,
        note_id: str,
    ) -> List[TextChunk]:
        """
        Split text into fixed-size chunks with overlap.
        """
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size

            # Find a good break point (space or punctuation)
            if end < len(text):
                # Look back for a good break point
                for i in range(min(50, end - start)):
                    if text[end - i] in " .!?\n":
                        end = end - i + 1
                        break

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk = TextChunk(
                    content=chunk_text,
                    chunk_id=f"{note_id}_chunk_{chunk_index}",
                    start_char=start,
                    end_char=end,
                    metadata={
                        **metadata,
                        "chunk_index": chunk_index,
                        "chunking_strategy": "fixed",
                    },
                    token_count=self._estimate_tokens(chunk_text),
                )
                chunks.append(chunk)
                chunk_index += 1

            # Move start with overlap
            start = end - self.chunk_overlap

            # Avoid infinite loop
            if start >= len(text):
                break

        logger.debug(f"Created {len(chunks)} chunks (fixed)")
        return chunks

    def _semantic_chunk(
        self,
        text: str,
        metadata: Dict,
        note_id: str,
    ) -> List[TextChunk]:
        """
        Split text into chunks at sentence boundaries.
        """
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunk_text = current_chunk.strip()
                    chunk = TextChunk(
                        content=chunk_text,
                        chunk_id=f"{note_id}_chunk_{chunk_index}",
                        start_char=current_start,
                        end_char=current_start + len(chunk_text),
                        metadata={
                            **metadata,
                            "chunk_index": chunk_index,
                            "chunking_strategy": "semantic",
                        },
                        token_count=self._estimate_tokens(chunk_text),
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                current_chunk = sentence + " "
                current_start = current_start + len(chunk_text) + 1

        # Add last chunk
        if current_chunk:
            chunk_text = current_chunk.strip()
            chunk = TextChunk(
                content=chunk_text,
                chunk_id=f"{note_id}_chunk_{chunk_index}",
                start_char=current_start,
                end_char=current_start + len(chunk_text),
                metadata={
                    **metadata,
                    "chunk_index": chunk_index,
                    "chunking_strategy": "semantic",
                },
                token_count=self._estimate_tokens(chunk_text),
            )
            chunks.append(chunk)

        logger.debug(f"Created {len(chunks)} chunks (semantic)")
        return chunks

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Uses simple heuristic: ~4 characters per token
        """
        return len(text) // 4

    def chunk_note(
        self,
        note_content: str,
        note_metadata: Dict,
        note_id: str,
    ) -> List[TextChunk]:
        """
        Chunk a complete note with its metadata.

        Args:
            note_content: Content of the note
            note_metadata: Metadata from the note
            note_id: Unique identifier for the note

        Returns:
            List of TextChunk objects
        """
        return self.chunk_text(
            text=note_content,
            metadata=note_metadata,
            note_id=note_id,
        )
