"""Conversation manager for handling chat history."""

from typing import List, Dict, Optional
import json
from pathlib import Path
from datetime import datetime
import uuid
from backend.config import settings


class ConversationManager:
    """Manages conversation history and persistence."""
    
    def __init__(self):
        """Initialize conversation manager."""
        self.conversations_dir = Path(settings.conversations_dir)
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
    
    def create_conversation(self, title: Optional[str] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            title: Optional conversation title
            
        Returns:
            Conversation ID
        """
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        conversation = {
            'conversation_id': conversation_id,
            'title': title or f"Conversation {conversation_id[:8]}",
            'created_at': timestamp,
            'updated_at': timestamp,
            'messages': []
        }
        
        self._save_conversation(conversation_id, conversation)
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        citations: Optional[List[Dict]] = None
    ):
        """
        Add message to conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ("user" or "assistant")
            content: Message content
            citations: Optional citations
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'citations': citations or []
        }
        
        conversation['messages'].append(message)
        conversation['updated_at'] = datetime.utcnow().isoformat()
        
        self._save_conversation(conversation_id, conversation)
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation data or None
        """
        file_path = self.conversations_dir / f"{conversation_id}.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def list_conversations(self) -> List[Dict]:
        """
        List all conversations.
        
        Returns:
            List of conversation summaries
        """
        conversations = []
        
        for file_path in self.conversations_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    conv = json.load(f)
                    conversations.append({
                        'conversation_id': conv['conversation_id'],
                        'title': conv['title'],
                        'created_at': conv['created_at'],
                        'updated_at': conv['updated_at'],
                        'message_count': len(conv['messages'])
                    })
            except Exception as e:
                print(f"Error loading conversation {file_path}: {e}")
        
        # Sort by updated_at (most recent first)
        conversations.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.conversations_dir / f"{conversation_id}.json"
        
        if not file_path.exists():
            return False
        
        file_path.unlink()
        return True
    
    def _save_conversation(self, conversation_id: str, conversation: Dict):
        """Save conversation to file."""
        file_path = self.conversations_dir / f"{conversation_id}.json"
        
        with open(file_path, 'w') as f:
            json.dump(conversation, f, indent=2)
