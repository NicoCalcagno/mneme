"""
Chat-related models for conversation endpoints
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from api.models.enums import MessageRole
from api.models.common import Source


class Message(BaseModel):
    """Single message in a conversation"""
    role: MessageRole = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional message metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What did I write about machine learning?",
                "timestamp": "2024-10-21T10:30:00Z",
                "metadata": {"source": "web_ui"},
            }
        }


class ChatRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User message to send to the chatbot"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for maintaining context across messages"
    )
    include_sources: bool = Field(
        True,
        description="Whether to include source documents in the response"
    )
    max_sources: int = Field(
        5,
        ge=1,
        le=20,
        description="Maximum number of source documents to return"
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Temperature override for this request (higher = more creative)"
    )
    stream: bool = Field(
        False,
        description="Enable streaming response (not yet implemented)"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate and clean the message"""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty or only whitespace")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Summarize my notes about Python programming",
                "conversation_id": "conv_123abc",
                "include_sources": True,
                "max_sources": 5,
                "temperature": 0.7,
                "stream": False,
            }
        }


class ChatResponse(BaseModel):
    """Response model for a chat message"""
    conversation_id: str = Field(..., description="Conversation ID")
    message: str = Field(..., description="Assistant's response message")
    sources: Optional[List[Source]] = Field(
        None,
        description="Source documents used to generate the response"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response metadata (model, temperature, etc.)"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="Processing time in milliseconds"
    )
    tokens_used: Optional[int] = Field(
        None,
        description="Total tokens used in this request"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_123abc",
                "message": "Based on your notes, Python is a versatile programming language that emphasizes readability and simplicity...",
                "sources": [
                    {
                        "file_path": "notes/programming/python_basics.md",
                        "chunk_id": "chunk_001",
                        "score": 0.92,
                        "content": "Python is a high-level programming language...",
                    }
                ],
                "metadata": {
                    "model": "gpt-4o",
                    "temperature": 0.7,
                },
                "processing_time_ms": 1234.56,
                "tokens_used": 450,
            }
        }


class ConversationSummary(BaseModel):
    """Summary of a conversation"""
    id: str = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages in conversation")
    last_message: Optional[str] = Field(None, description="Preview of last message")
    title: Optional[str] = Field(None, description="Auto-generated or user-defined title")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "conv_123abc",
                "created_at": "2024-10-21T10:00:00Z",
                "updated_at": "2024-10-21T10:30:00Z",
                "message_count": 5,
                "last_message": "What about Python?",
                "title": "Python Programming Discussion",
            }
        }


class ConversationListResponse(BaseModel):
    """Response model for listing conversations"""
    conversations: List[ConversationSummary] = Field(
        ...,
        description="List of conversation summaries"
    )
    total: int = Field(..., description="Total number of conversations")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "conversations": [
                    {
                        "id": "conv_123",
                        "created_at": "2024-10-21T10:00:00Z",
                        "updated_at": "2024-10-21T10:30:00Z",
                        "message_count": 5,
                        "last_message": "What about Python?",
                        "title": "Python Discussion",
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
            }
        }


class ConversationDetail(BaseModel):
    """Detailed view of a conversation including all messages"""
    id: str = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    messages: List[Message] = Field(..., description="All messages in the conversation")
    title: Optional[str] = Field(None, description="Conversation title")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional conversation metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "conv_123abc",
                "created_at": "2024-10-21T10:00:00Z",
                "updated_at": "2024-10-21T10:30:00Z",
                "messages": [
                    {
                        "role": "user",
                        "content": "What is Python?",
                        "timestamp": "2024-10-21T10:00:00Z",
                    },
                    {
                        "role": "assistant",
                        "content": "Python is a high-level programming language...",
                        "timestamp": "2024-10-21T10:00:05Z",
                    },
                ],
                "title": "Python Discussion",
            }
        }