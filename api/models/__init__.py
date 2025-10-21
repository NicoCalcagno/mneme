"""
Pydantic models for API requests and responses
"""

# Enums
from api.models.enums import (
    MessageRole,
    IngestionStatus,
    HealthStatus,
)

# Common models
from api.models.common import (
    ErrorResponse,
    Source,
)

# Chat models
from api.models.chat import (
    Message,
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    ConversationListResponse,
    ConversationDetail,
)

# Ingestion models
from api.models.ingestion import (
    IngestionRequest,
    IngestionResponse,
    IngestionStatusResponse,
    IngestionJobDetail,
)

# Health models
from api.models.health import (
    ComponentHealth,
    HealthResponse,
    MetricsResponse,
    ReadinessResponse,
    LivenessResponse,
)

__all__ = [
    # Enums
    "MessageRole",
    "IngestionStatus",
    "HealthStatus",
    # Common
    "ErrorResponse",
    "Source",
    # Chat
    "Message",
    "ChatRequest",
    "ChatResponse",
    "ConversationSummary",
    "ConversationListResponse",
    "ConversationDetail",
    # Ingestion
    "IngestionRequest",
    "IngestionResponse",
    "IngestionStatusResponse",
    "IngestionJobDetail",
    # Health
    "ComponentHealth",
    "HealthResponse",
    "MetricsResponse",
    "ReadinessResponse",
    "LivenessResponse",
]