"""
Ingestion CLI Command

Orchestrates the complete ingestion pipeline:
1. Parse Obsidian vault
2. Chunk documents
3. Generate embeddings
4. Store in vector database
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from loguru import logger

from config.settings import Settings
from ingestion.parser import ObsidianParser
from ingestion.chunker import TextChunker
from ingestion.embedder import EmbeddingsGenerator
from ingestion.vectorstore import VectorStore


class IngestionPipeline:
    """
    Complete ingestion pipeline for Obsidian notes.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize ingestion pipeline.

        Args:
            settings: Settings object (will create if not provided)
        """
        self.settings = settings or Settings()

        # Initialize components
        self.parser = ObsidianParser()
        self.chunker = TextChunker(self.settings)
        self.embedder = EmbeddingsGenerator(self.settings)
        self.vector_store = VectorStore(self.settings)

        logger.info("Ingestion pipeline initialized")

    def ingest_vault(
        self,
        vault_path: Optional[str] = None,
        incremental: bool = False,
        force: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """
        Run complete ingestion pipeline on Obsidian vault.

        Args:
            vault_path: Path to vault (uses settings if not provided)
            incremental: Only process changed files
            force: Force reprocessing of all files
            dry_run: Don't actually store in vector database

        Returns:
            Statistics dictionary
        """
        # Use vault path from settings if not provided
        if vault_path is None:
            vault_path = self.settings.obsidian_vault_path

        vault_path = Path(vault_path)

        logger.info(f"Starting ingestion: {vault_path}")
        logger.info(f"Incremental: {incremental}, Force: {force}, Dry run: {dry_run}")

        stats = {
            "notes_parsed": 0,
            "notes_skipped": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "vectors_stored": 0,
        }

        try:
            # Step 1: Parse vault
            logger.info("Step 1/4: Parsing Obsidian vault...")

            file_extensions = self.settings.obsidian_file_extensions.split(",")
            exclude_folders = self.settings.obsidian_exclude_folders.split(",")

            notes = self.parser.parse_vault(
                vault_path=vault_path,
                file_extensions=file_extensions,
                exclude_folders=exclude_folders,
            )

            stats["notes_parsed"] = len(notes)
            logger.info(f"Parsed {len(notes)} notes")

            if not notes:
                logger.warning("No notes found to process")
                return stats

            # Step 2: Chunk documents
            logger.info("Step 2/4: Chunking documents...")

            all_chunks = []
            for note in notes:
                # Get enriched metadata
                metadata = self.parser.get_note_metadata(note)

                # Chunk the note
                chunks = self.chunker.chunk_note(
                    note_content=note.content,
                    note_metadata=metadata,
                    note_id=str(note.file_path),
                )

                all_chunks.extend(chunks)

            stats["chunks_created"] = len(all_chunks)
            logger.info(f"Created {len(all_chunks)} chunks")

            # Step 3: Generate embeddings
            logger.info("Step 3/4: Generating embeddings...")

            chunk_embedding_pairs = self.embedder.embed_chunks(all_chunks)

            stats["embeddings_generated"] = len(chunk_embedding_pairs)
            logger.info(f"Generated {len(chunk_embedding_pairs)} embeddings")

            # Step 4: Store in vector database
            if not dry_run:
                logger.info("Step 4/4: Storing in vector database...")

                chunks = [pair[0] for pair in chunk_embedding_pairs]
                embeddings = [pair[1] for pair in chunk_embedding_pairs]

                vectors_stored = self.vector_store.upsert_chunks(chunks, embeddings)

                stats["vectors_stored"] = vectors_stored
                logger.info(f"Stored {vectors_stored} vectors")
            else:
                logger.info("Step 4/4: Skipping storage (dry run)")

            # Final stats
            logger.info("=" * 60)
            logger.info("Ingestion completed successfully!")
            logger.info(f"  Notes parsed:       {stats['notes_parsed']}")
            logger.info(f"  Chunks created:     {stats['chunks_created']}")
            logger.info(f"  Embeddings generated: {stats['embeddings_generated']}")
            if not dry_run:
                logger.info(f"  Vectors stored:     {stats['vectors_stored']}")
            logger.info("=" * 60)

            return stats

        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            raise


def main():
    """
    CLI entry point for ingestion command.
    """
    parser = argparse.ArgumentParser(
        description="Ingest Obsidian vault into vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest vault from settings
  mneme-ingest

  # Ingest specific vault
  mneme-ingest --vault-path /path/to/vault

  # Dry run (don't store in database)
  mneme-ingest --dry-run

  # Force reprocessing
  mneme-ingest --force
        """,
    )

    parser.add_argument(
        "--vault-path",
        type=str,
        help="Path to Obsidian vault (overrides OBSIDIAN_VAULT_PATH from .env)",
    )

    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only process files that have changed (not implemented yet)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocessing of all files",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and chunk but don't store in vector database",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=args.log_level,
    )

    try:
        # Initialize pipeline
        pipeline = IngestionPipeline()

        # Run ingestion
        stats = pipeline.ingest_vault(
            vault_path=args.vault_path,
            incremental=args.incremental,
            force=args.force,
            dry_run=args.dry_run,
        )

        logger.info("Ingestion complete! ✅")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("Ingestion interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
