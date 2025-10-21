"""
Chat endpoints
"""

import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from api.models.chat import ChatRequest, ChatResponse, ConversationListResponse
from api.models.common import Source, ErrorResponse
from api.dependencies import get_settings, get_rag_agent
from config.settings import Settings

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Send Chat Message",
    description="Send a message to the chatbot and receive a response based on your Obsidian notes",
    responses={
        200: {"description": "Successful response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def chat(
        request: ChatRequest,
        settings: Settings = Depends(get_settings),
        agent=Depends(get_rag_agent),
) -> ChatResponse:
    """
    Process a chat message and return an AI-generated response.

    The agent will:
    1. Retrieve relevant chunks from your Obsidian notes
    2. Use the retrieved context to generate a response
    3. Return the response with source citations (if enabled)

    Args:
        request: ChatRequest with message and optional parameters

    Returns:
        ChatResponse with assistant message and sources
    """
    start_time = time.time()

    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or f"conv_{uuid.uuid4().hex[:12]}"

        logger.info(
            f"Processing chat request - conversation_id: {conversation_id}, "
            f"message_length: {len(request.message)}"
        )

        # TODO: Call RAG agent with the message
        # For now, return a placeholder response

        # Placeholder response
        assistant_message = (
            "This is a placeholder response. "
            "The RAG agent integration will be implemented in the next phase."
        )

        sources = []
        if request.include_sources:
            # Placeholder sources
            sources = [
                Source(
                    file_path="notes/example.md",
                    chunk_id="chunk_001",
                    score=0.95,
                    content="This is example content from your notes.",
                    metadata={"tags": ["example"]},
                )
            ]

        processing_time = (time.time() - start_time) * 1000

        logger.info(
            f"Chat request completed - conversation_id: {conversation_id}, "
            f"processing_time_ms: {processing_time:.2f}"
        )

        return ChatResponse(
            conversation_id=conversation_id,
            message=assistant_message,
            sources=sources if request.include_sources else None,
            processing_time_ms=processing_time,
            metadata={
                "model": settings.llm_model,
                "temperature": request.temperature or settings.llm_temperature,
            },
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}",
        )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List Conversations",
    description="Get a list of all conversation sessions",
)
async def list_conversations() -> ConversationListResponse:
    """
    List all conversation sessions.

    Returns:
        ConversationListResponse with list of conversations
    """
    # TODO: Implement conversation persistence
    logger.info("Listing conversations")

    return ConversationListResponse(
        conversations=[],
        total=0,
    )


@router.delete(
    "/conversations/{conversation_id}",
    summary="Delete Conversation",
    description="Delete a specific conversation session",
)
async def delete_conversation(conversation_id: str) -> dict:
    """
    Delete a conversation session.

    Args:
        conversation_id: ID of the conversation to delete

    Returns:
        Success message
    """
    # TODO: Implement conversation deletion
    logger.info(f"Deleting conversation: {conversation_id}")

    return {"message": f"Conversation {conversation_id} deleted successfully"}


@router.get(
    "/conversations/{conversation_id}",
    summary="Get Conversation",
    description="Get details of a specific conversation",
)
async def get_conversation(conversation_id: str) -> dict:
    """
    Get conversation details.

    Args:
        conversation_id: ID of the conversation

    Returns:
        Conversation details
    """
    # TODO: Implement conversation retrieval
    logger.info(f"Getting conversation: {conversation_id}")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Conversation {conversation_id} not found",
    )