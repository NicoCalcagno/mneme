"""
Health check and monitoring models
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field

from api.models.enums import HealthStatus


class ComponentHealth(BaseModel):
    """Health status of an individual component"""
    name: str = Field(..., description="Component name")
    status: HealthStatus = Field(..., description="Component health status")
    message: Optional[str] = Field(None, description="Status message or error details")
    response_time_ms: Optional[float] = Field(None, description="Component response time")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "vector_store",
                "status": "healthy",
                "message": "Connected to Qdrant",
                "response_time_ms": 12.34,
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: HealthStatus = Field(..., description="Overall application health status")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    timestamp: str = Field(..., description="Current server timestamp")

    # Component-specific health
    vector_store_connected: bool = Field(..., description="Vector store connection status")
    llm_provider: str = Field(..., description="Current LLM provider")
    vector_store_documents: Optional[int] = Field(
        None,
        description="Number of documents in vector store"
    )

    # Detailed checks
    checks: Optional[Dict[str, bool]] = Field(
        None,
        description="Individual component health checks"
    )
    components: Optional[list[ComponentHealth]] = Field(
        None,
        description="Detailed component health information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "uptime_seconds": 3600.5,
                "timestamp": "2024-10-21T10:30:00Z",
                "vector_store_connected": True,
                "llm_provider": "openai",
                "vector_store_documents": 387,
                "checks": {
                    "vector_store": True,
                    "llm_client": True,
                    "embeddings": True,
                },
                "components": [
                    {
                        "name": "vector_store",
                        "status": "healthy",
                        "message": "Connected to Qdrant",
                        "response_time_ms": 12.34,
                    }
                ],
            }
        }


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    requests_total: int = Field(..., description="Total number of requests")
    requests_per_minute: float = Field(..., description="Average requests per minute")
    average_response_time_ms: float = Field(..., description="Average response time")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0-1)")

    # Resource usage
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")

    # Vector store metrics
    vector_store_queries: Optional[int] = Field(None, description="Total vector store queries")
    average_retrieval_time_ms: Optional[float] = Field(
        None,
        description="Average retrieval time"
    )

    # LLM metrics
    llm_requests: Optional[int] = Field(None, description="Total LLM requests")
    total_tokens_used: Optional[int] = Field(None, description="Total tokens used")
    average_llm_response_time_ms: Optional[float] = Field(
        None,
        description="Average LLM response time"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "requests_total": 1234,
                "requests_per_minute": 20.5,
                "average_response_time_ms": 456.78,
                "error_rate": 0.02,
                "memory_usage_mb": 512.34,
                "cpu_usage_percent": 25.6,
                "vector_store_queries": 890,
                "average_retrieval_time_ms": 123.45,
                "llm_requests": 445,
                "total_tokens_used": 125000,
                "average_llm_response_time_ms": 789.12,
            }
        }


class ReadinessResponse(BaseModel):
    """Simple readiness probe response"""
    ready: bool = Field(..., description="Application readiness status")

    class Config:
        json_schema_extra = {
            "example": {
                "ready": True,
            }
        }


class LivenessResponse(BaseModel):
    """Simple liveness probe response"""
    alive: bool = Field(..., description="Application liveness status")

    class Config:
        json_schema_extra = {
            "example": {
                "alive": True,
            }
        }