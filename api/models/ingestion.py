"""
Ingestion-related models for indexing operations
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from api.models.enums import IngestionStatus


class IngestionRequest(BaseModel):
    """Request model for triggering ingestion"""
    vault_path: Optional[str] = Field(
        None,
        description="Override the default vault path from settings"
    )
    incremental: bool = Field(
        True,
        description="Only process files that have changed since last ingestion"
    )
    force: bool = Field(
        False,
        description="Force re-indexing of all files, ignoring incremental flag"
    )
    dry_run: bool = Field(
        False,
        description="Simulate ingestion without actually indexing (for testing)"
    )
    file_patterns: Optional[List[str]] = Field(
        None,
        description="Optional file patterns to filter (e.g., ['*.md', 'notes/**/*.md'])"
    )

    @field_validator("force")
    @classmethod
    def validate_force_incremental(cls, v: bool, info) -> bool:
        """Ensure force and incremental are not both True"""
        if v and info.data.get("incremental", False):
            raise ValueError("Cannot use both 'force' and 'incremental' flags together")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "vault_path": "/path/to/vault",
                "incremental": True,
                "force": False,
                "dry_run": False,
                "file_patterns": ["*.md"],
            }
        }


class IngestionResponse(BaseModel):
    """Response model for ingestion operations"""
    status: IngestionStatus = Field(..., description="Current status of the ingestion")
    message: str = Field(..., description="Human-readable status message")
    files_processed: Optional[int] = Field(
        None,
        description="Number of files successfully processed"
    )
    files_skipped: Optional[int] = Field(
        None,
        description="Number of files skipped (not changed or excluded)"
    )
    files_failed: Optional[int] = Field(
        None,
        description="Number of files that failed to process"
    )
    total_chunks: Optional[int] = Field(
        None,
        description="Total number of chunks generated and stored"
    )
    processing_time_s: Optional[float] = Field(
        None,
        description="Total processing time in seconds"
    )
    errors: Optional[List[str]] = Field(
        None,
        description="List of error messages if any files failed"
    )
    job_id: Optional[str] = Field(
        None,
        description="Job ID for tracking asynchronous ingestion"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "message": "Ingestion completed successfully",
                "files_processed": 42,
                "files_skipped": 5,
                "files_failed": 0,
                "total_chunks": 387,
                "processing_time_s": 12.34,
                "errors": None,
                "job_id": "job_abc123",
            }
        }


class IngestionStatusResponse(BaseModel):
    """Response model for checking ingestion status"""
    current_status: IngestionStatus = Field(..., description="Current ingestion status")
    last_run_at: Optional[str] = Field(None, description="Timestamp of last ingestion")
    last_run_status: Optional[IngestionStatus] = Field(None, description="Status of last run")
    last_run_summary: Optional[str] = Field(None, description="Summary of last run")
    next_scheduled_run: Optional[str] = Field(None, description="Next scheduled run (if configured)")
    total_documents: Optional[int] = Field(None, description="Total documents in vector store")
    vault_path: Optional[str] = Field(None, description="Current vault path being indexed")

    class Config:
        json_schema_extra = {
            "example": {
                "current_status": "idle",
                "last_run_at": "2024-10-21T09:00:00Z",
                "last_run_status": "completed",
                "last_run_summary": "42 files processed, 387 chunks created",
                "next_scheduled_run": None,
                "total_documents": 387,
                "vault_path": "/path/to/vault",
            }
        }


class IngestionJobDetail(BaseModel):
    """Detailed information about a specific ingestion job"""
    job_id: str = Field(..., description="Unique job identifier")
    status: IngestionStatus = Field(..., description="Current job status")
    started_at: str = Field(..., description="Job start timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")
    progress_percentage: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Progress percentage (0-100)"
    )
    current_file: Optional[str] = Field(None, description="Currently processing file")
    files_processed: int = Field(0, description="Files processed so far")
    total_files: Optional[int] = Field(None, description="Total files to process")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_abc123",
                "status": "in_progress",
                "started_at": "2024-10-21T10:00:00Z",
                "completed_at": None,
                "progress_percentage": 45.5,
                "current_file": "notes/programming/python_basics.md",
                "files_processed": 19,
                "total_files": 42,
                "errors": [],
            }
        }