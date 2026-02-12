"""API routes for conversation management."""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetail,
    ConversationListResponse,
    Message
)
from backend.services.conversation_manager import ConversationManager
from typing import List

router = APIRouter(prefix="/conversations", tags=["conversations"])

# Initialize conversation manager
conversation_manager = ConversationManager()


@router.post("/", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreate):
    """Create a new conversation."""
    conversation_id = conversation_manager.create_conversation(request.title)
    conversation = conversation_manager.get_conversation(conversation_id)
    
    return ConversationResponse(
        conversation_id=conversation['conversation_id'],
        title=conversation['title'],
        created_at=conversation['created_at'],
        updated_at=conversation['updated_at'],
        message_count=len(conversation['messages'])
    )


@router.get("/", response_model=ConversationListResponse)
async def list_conversations():
    """List all conversations."""
    conversations = conversation_manager.list_conversations()
    
    return ConversationListResponse(
        conversations=[ConversationResponse(**c) for c in conversations],
        total=len(conversations)
    )


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """Get conversation details with messages."""
    conversation = conversation_manager.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationDetail(
        conversation_id=conversation['conversation_id'],
        title=conversation['title'],
        created_at=conversation['created_at'],
        updated_at=conversation['updated_at'],
        messages=[Message(**m) for m in conversation['messages']]
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    deleted = conversation_manager.delete_conversation(conversation_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"message": f"Conversation {conversation_id} deleted successfully"}
