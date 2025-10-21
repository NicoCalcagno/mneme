"""
FastAPI application entry point
"""

import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config.settings import Settings
from api.routes import chat, health, ingestion
from api.middleware import RequestLoggingMiddleware
from api.models.common import ErrorResponse

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("🧠 Mneme API starting up...")
    settings = Settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector Store: {settings.vector_store_type}")
    logger.info(f"Obsidian Vault: {settings.obsidian_vault_path}")

    # TODO: Initialize vector store connection
    # TODO: Initialize RAG agent
    # TODO: Load any required models

    logger.info("✅ Mneme API ready to serve requests")

    yield

    # Shutdown
    logger.info("🛑 Mneme API shutting down...")
    # TODO: Close vector store connection
    # TODO: Cleanup resources
    logger.info("✅ Mneme API shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app
    """
    settings = Settings()

    app = FastAPI(
        title="Mneme API",
        description="Transform your Obsidian vault into a queryable AI-powered second brain",
        version="0.1.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
        lifespan=lifespan,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Global exception handler for unhandled errors.

        Args:
            request: HTTP request
            exc: Exception that was raised

        Returns:
            JSONResponse with error details
        """
        logger.error("Unhandled exception: {}", repr(exc), exc_info=True)

        error_response = ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc) if settings.debug else None,
            request_id=getattr(request.state, "request_id", None),
        )

        return JSONResponse(
            status_code=500,
            content=error_response.model_dump(),
        )

    # Include routers
    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(chat.router, prefix=settings.api_prefix)
    app.include_router(ingestion.router, prefix=settings.api_prefix)

    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint with API information"""
        return {
            "name": "Mneme API",
            "version": "0.1.0",
            "description": "Transform your Obsidian vault into a queryable AI-powered second brain",
            "docs": f"{settings.api_prefix}/docs" if settings.enable_docs else None,
        }

    return app


# Create app instance
app = create_app()


def main():
    """
    Main entry point for running the API server.
    """
    import uvicorn

    settings = Settings()

    logger.info(f"Starting Mneme API server on {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers if not settings.api_reload else 1,
        log_level="info",
    )


if __name__ == "__main__":
    main()