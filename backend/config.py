"""Centralized configuration management for the RAG system."""

from pydantic_settings import BaseSettings
from typing import List
import os
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # HuggingFace Configuration
    huggingface_api_key: str = ""  # Optional for Phase 2 testing
    hf_model_name: str = "microsoft/Phi-3-mini-4k-instruct"
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # for all-MiniLM-L6-v2
    
    # Pinecone Configuration
    pinecone_api_key: str = ""  # Optional for Phase 2 testing
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "decodx-finance"
    
    # Web Search Configuration
    web_search_provider: str = "duckduckgo"  # Options: duckduckgo, tavily
    tavily_api_key: str = ""  # Optional, only needed if using Tavily
    
    # MCP Server Configuration
    mcp_web_search_host: str = "localhost"
    mcp_web_search_port: int = 8001
    mcp_vector_db_host: str = "localhost"
    mcp_vector_db_port: int = 8002
    mcp_doc_processor_host: str = "localhost"
    mcp_doc_processor_port: int = 8003
    
    # Data Directories
    upload_dir: str = "./data/uploads"
    conversations_dir: str = "./data/conversations"
    
    # Application Settings
    chunk_size: int = 512
    chunk_overlap: int = 128
    retrieval_top_k: int = 10
    reranking_top_k: int = 5
    top_k_retrieval: int = 10
    top_k_rerank: int = 5
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = '["http://localhost:3000", "http://localhost:8000", "http://localhost:8080", "http://127.0.0.1:8080"]'
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        try:
            return json.loads(self.cors_origins)
        except:
            return ["http://localhost:3000", "http://localhost:8000"]


# Initialize settings
settings = Settings()

# Create necessary directories
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs("./data/conversations", exist_ok=True)

# Print configuration on import (for debugging)
if __name__ != "__main__":
    print("🔧 Configuration loaded:")
    print(f"  📚 LLM Model: {settings.hf_model_name}")
    print(f"  🔍 Embedding Model: {settings.embedding_model}")
    print(f"  💾 Vector DB: Pinecone ({settings.pinecone_index_name})")
    print(f"  📁 Upload Directory: {settings.upload_dir}")
