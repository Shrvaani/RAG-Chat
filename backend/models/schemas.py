"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# Document Schemas
class DocumentUploadResponse(BaseModel):
    """Response for document upload."""
    doc_id: str
    filename: str
    file_type: str
    chunks_created: int
    upload_timestamp: str
    message: str = "Document uploaded successfully"


class DocumentInfo(BaseModel):
    """Document information."""
    doc_id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Response for listing documents."""
    documents: List[DocumentInfo]
    total: int


# Query Schemas
class QueryRequest(BaseModel):
    """Request for querying the RAG system."""
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to retrieve")


class Citation(BaseModel):
    """Citation information."""
    id: int
    type: str  # "document" or "web"
    filename: Optional[str] = None
    page: Optional[int] = None
    title: Optional[str] = None
    url: Optional[str] = None
    content_preview: Optional[str] = None


class QueryResponse(BaseModel):
    """Response for query."""
    query: str
    response: str
    citations: List[Citation]
    conversation_id: str
    processing_time: float
    metadata: Dict = Field(default_factory=dict)


# Conversation Schemas
class Message(BaseModel):
    """Chat message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    citations: Optional[List[Citation]] = None


class ConversationCreate(BaseModel):
    """Create new conversation."""
    title: Optional[str] = Field(None, max_length=200)


class ConversationResponse(BaseModel):
    """Conversation information."""
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationDetail(BaseModel):
    """Detailed conversation with messages."""
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message]


class ConversationListResponse(BaseModel):
    """List of conversations."""
    conversations: List[ConversationResponse]
    total: int


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    services: Dict[str, str]
    timestamp: str


# Error Schema
class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: str
