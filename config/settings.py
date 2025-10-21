"""
Application settings using Pydantic Settings
"""

from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # OBSIDIAN CONFIGURATION
    # =========================================================================
    obsidian_vault_path: str = Field(
        default="/vault",
        description="Path to Obsidian vault"
    )
    obsidian_file_extensions: str = Field(
        default=".md,.markdown",
        description="Comma-separated file extensions"
    )
    obsidian_exclude_folders: str = Field(
        default=".obsidian,.trash,templates",
        description="Comma-separated folders to exclude"
    )

    # =========================================================================
    # LLM PROVIDER CONFIGURATION
    # =========================================================================
    llm_provider: Literal["openai", "anthropic", "google", "mistral"] = Field(
        default="openai",
        description="LLM provider to use"
    )
    llm_model: str = Field(
        default="gpt-4o",
        description="LLM model name"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature"
    )
    llm_max_tokens: int = Field(
        default=2000,
        gt=0,
        description="Maximum tokens for LLM response"
    )

    # =========================================================================
    # API KEYS
    # =========================================================================
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key"
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key"
    )

    # =========================================================================
    # EMBEDDINGS CONFIGURATION
    # =========================================================================
    embedding_provider: Literal["openai", "local"] = Field(
        default="openai",
        description="Embedding provider"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name"
    )
    embedding_dimensions: int = Field(
        default=1536,
        gt=0,
        description="Embedding dimensions"
    )
    embedding_batch_size: int = Field(
        default=100,
        gt=0,
        description="Batch size for embeddings"
    )

    # =========================================================================
    # VECTOR STORE CONFIGURATION
    # =========================================================================
    vector_store_type: Literal["qdrant", "chroma"] = Field(
        default="qdrant",
        description="Vector store type"
    )
    vector_store_collection: str = Field(
        default="mneme_knowledge",
        description="Collection/index name"
    )

    # Qdrant configuration
    qdrant_url: str = Field(
        default="",
        description="Qdrant server URL (leave empty for local)"
    )
    qdrant_api_key: str = Field(
        default="",
        description="Qdrant API key"
    )
    qdrant_path: str = Field(
        default="./data/qdrant",
        description="Local Qdrant storage path"
    )
    qdrant_prefer_grpc: bool = Field(
        default=False,
        description="Use gRPC instead of HTTP"
    )

    # =========================================================================
    # CHUNKING CONFIGURATION
    # =========================================================================
    chunk_size: int = Field(
        default=1000,
        gt=0,
        description="Text chunk size"
    )
    chunk_overlap: int = Field(
        default=200,
        ge=0,
        description="Chunk overlap size"
    )
    chunking_strategy: Literal["recursive", "fixed", "semantic"] = Field(
        default="recursive",
        description="Chunking strategy"
    )

    # =========================================================================
    # RETRIEVAL CONFIGURATION
    # =========================================================================
    retrieval_top_k: int = Field(
        default=5,
        gt=0,
        description="Number of chunks to retrieve"
    )
    retrieval_min_score: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum relevance score"
    )

    # =========================================================================
    # AGENT CONFIGURATION
    # =========================================================================
    max_conversation_history: int = Field(
        default=10,
        ge=0,
        description="Maximum conversation history to keep"
    )
    enable_citations: bool = Field(
        default=True,
        description="Include source citations in responses"
    )
    citation_format: Literal["inline", "footnote", "none"] = Field(
        default="inline",
        description="Citation format style"
    )

    # =========================================================================
    # API SERVER CONFIGURATION
    # =========================================================================
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host"
    )
    api_port: int = Field(
        default=8000,
        gt=0,
        lt=65536,
        description="API server port"
    )
    api_reload: bool = Field(
        default=True,
        description="Enable auto-reload in development"
    )
    api_workers: int = Field(
        default=1,
        gt=0,
        description="Number of API workers"
    )
    api_prefix: str = Field(
        default="/api/v1",
        description="API route prefix"
    )
    enable_docs: bool = Field(
        default=True,
        description="Enable API documentation"
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from environment"""
        cors_str = self.cors_origins_str
        if cors_str == "*":
            return ["*"]
        return [origin.strip() for origin in cors_str.split(",") if origin.strip()]

    cors_origins_str: str = Field(
        default="*",
        alias="CORS_ORIGINS",
        description="Comma-separated CORS origins"
    )

    # =========================================================================
    # OBSERVABILITY
    # =========================================================================
    enable_tracing: bool = Field(
        default=False,
        description="Enable OpenTelemetry tracing"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: str = Field(
        default="./data/logs/mneme.log",
        description="Log file path"
    )

    # =========================================================================
    # INGESTION CONFIGURATION
    # =========================================================================
    incremental_ingestion: bool = Field(
        default=True,
        description="Use incremental ingestion"
    )
    checksum_algorithm: Literal["md5", "sha256"] = Field(
        default="md5",
        description="Checksum algorithm for file tracking"
    )
    ingestion_db_path: str = Field(
        default="./data/ingestion.db",
        description="Ingestion tracking database path"
    )
    max_file_size_mb: int = Field(
        default=10,
        gt=0,
        description="Maximum file size in MB"
    )
    ingestion_workers: int = Field(
        default=4,
        gt=0,
        description="Number of ingestion workers"
    )

    # =========================================================================
    # DEVELOPMENT & TESTING
    # =========================================================================
    environment: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
