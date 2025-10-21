"""
Common models shared across different endpoints
"""

from typing import Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid request parameters",
                "detail": "Field 'message' is required",
                "request_id": "req_abc123",
            }
        }


class Source(BaseModel):
    """Source document reference from vector store"""
    file_path: str = Field(..., description="Path to the source file")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    content: str = Field(..., description="Chunk content")
    metadata: Optional[dict] = Field(None, description="Additional metadata from the source")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "notes/programming/python_basics.md",
                "chunk_id": "chunk_001",
                "score": 0.92,
                "content": "Python is a high-level programming language...",
                "metadata": {
                    "created_at": "2024-01-15",
                    "tags": ["python", "programming"],
                    "title": "Python Basics",
                },
            }
        }