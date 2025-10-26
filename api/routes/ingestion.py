"""
Ingestion endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from loguru import logger

from api.models.ingestion import (
    IngestionRequest,
    IngestionResponse,
    IngestionStatusResponse,
    IngestionStatus,
)
from api.models.common import ErrorResponse
from api.dependencies import get_settings
from config.settings import Settings
from ingestion import IngestionPipeline

router = APIRouter(prefix="/ingest", tags=["ingestion"])


async def run_ingestion_task(request: IngestionRequest, settings: Settings):
    """
    Background task for running ingestion.

    Args:
        request: IngestionRequest parameters
        settings: Application settings
    """
    logger.info("Starting background ingestion task")

    try:
        # Initialize ingestion pipeline
        pipeline = IngestionPipeline(settings)

        # Run ingestion
        stats = pipeline.ingest_vault(
            vault_path=request.vault_path,
            incremental=request.incremental,
            force=request.force,
            dry_run=request.dry_run,
        )

        logger.info(f"Background ingestion completed: {stats}")
    except Exception as e:
        logger.error(f"Background ingestion failed: {e}", exc_info=True)

    logger.info("Background ingestion task completed")


@router.post(
    "",
    response_model=IngestionResponse,
    summary="Trigger Ingestion",
    description="Manually trigger ingestion of Obsidian notes into the vector store",
    responses={
        200: {"description": "Ingestion started successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def trigger_ingestion(
        request: IngestionRequest,
        background_tasks: BackgroundTasks,
        settings: Settings = Depends(get_settings),
) -> IngestionResponse:
    """
    Trigger ingestion of Obsidian notes.

    This endpoint can run in two modes:
    - Synchronous (dry_run=True): Returns immediately with simulation results
    - Asynchronous (dry_run=False): Starts background task and returns immediately

    Args:
        request: IngestionRequest with ingestion parameters
        background_tasks: FastAPI background tasks

    Returns:
        IngestionResponse with ingestion status
    """
    try:
        vault_path = request.vault_path or settings.obsidian_vault_path

        logger.info(
            f"Ingestion triggered - vault: {vault_path}, "
            f"incremental: {request.incremental}, force: {request.force}, "
            f"dry_run: {request.dry_run}"
        )

        if request.dry_run:
            # Simulate ingestion
            return IngestionResponse(
                status=IngestionStatus.COMPLETED,
                message="Dry run completed successfully (simulation)",
                files_processed=0,
                files_skipped=0,
                total_chunks=0,
                processing_time_s=0.0,
            )

        # Start background ingestion task
        background_tasks.add_task(run_ingestion_task, request, settings)

        return IngestionResponse(
            status=IngestionStatus.IN_PROGRESS,
            message="Ingestion started in background",
        )

    except Exception as e:
        logger.error(f"Error triggering ingestion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering ingestion: {str(e)}",
        )


@router.get(
    "/status",
    summary="Get Ingestion Status",
    description="Get the current status of ingestion process",
)
async def get_ingestion_status() -> dict:
    """
    Get current ingestion status.

    Returns:
        Ingestion status information
    """
    # TODO: Implement ingestion status tracking
    logger.info("Getting ingestion status")

    return {
        "status": "idle",
        "last_run": None,
        "next_run": None,
    }