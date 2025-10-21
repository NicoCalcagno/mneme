"""
Health check endpoints
"""

import time
from datetime import datetime
from fastapi import APIRouter, Depends
from api.models.health import HealthResponse, ReadinessResponse, LivenessResponse
from api.models.enums import HealthStatus
from api.dependencies import get_settings, get_vector_store
from config.settings import Settings

router = APIRouter(tags=["health"])

# Track application start time
START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the application and its dependencies",
)
async def health_check(
        settings: Settings = Depends(get_settings),
        vector_store=Depends(get_vector_store),
) -> HealthResponse:
    """
    Perform health check on the application and its dependencies.

    Returns:
        HealthResponse with status and component health information
    """
    uptime = time.time() - START_TIME

    # Check vector store connection
    vector_store_connected = False
    vector_store_documents = None
    try:
        # Attempt to count documents in vector store
        if hasattr(vector_store, "count"):
            vector_store_documents = vector_store.count()
            vector_store_connected = True
        else:
            vector_store_connected = True
    except Exception:
        vector_store_connected = False

    # Determine overall health status
    checks = {
        "vector_store": vector_store_connected,
    }

    all_healthy = all(checks.values())
    status = HealthStatus.HEALTHY if all_healthy else HealthStatus.DEGRADED

    return HealthResponse(
        status=status,
        version="0.1.0",
        uptime_seconds=uptime,
        timestamp=datetime.utcnow().isoformat() + "Z",
        vector_store_connected=vector_store_connected,
        llm_provider=settings.llm_provider,
        vector_store_documents=vector_store_documents,
        checks=checks,
    )


@router.get(
    "/ready",
    summary="Readiness Check",
    description="Check if the application is ready to accept requests",
)
async def readiness_check() -> dict:
    """
    Kubernetes-style readiness probe.

    Returns:
        Simple status dict
    """
    return {"status": "ready"}


@router.get(
    "/live",
    summary="Liveness Check",
    description="Check if the application is alive",
)
async def liveness_check() -> dict:
    """
    Kubernetes-style liveness probe.

    Returns:
        Simple status dict
    """
    return {"status": "alive"}