"""
Vector Database MCP Server

Exposes vector database operations via Model Context Protocol.

Run from project root: python -m backend.mcp.servers.vector_db_server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.services.vector_store import VectorStore
from backend.services.embedding_service import EmbeddingService
import uvicorn

app = FastAPI(
    title="Vector Database MCP Server",
    description="MCP server for vector database operations",
    version="1.0.0"
)

# Initialize services
embedding_service = EmbeddingService()
vector_store = None  # Will be initialized when needed


class EmbedRequest(BaseModel):
    """Embedding request schema."""
    texts: List[str]


class EmbedResponse(BaseModel):
    """Embedding response schema."""
    embeddings: List[List[float]]
    dimension: int


class UpsertRequest(BaseModel):
    """Upsert request schema."""
    chunks: List[Dict]


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str
    top_k: int = 10
    filter: Optional[Dict] = None


class SearchResponse(BaseModel):
    """Search response schema."""
    results: List[Dict]
    total: int


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Vector Database MCP Server",
        "version": "1.0.0",
        "protocol": "MCP",
        "capabilities": ["embeddings", "vector_search", "upsert", "delete"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_info = embedding_service.get_model_info()
    return {
        "status": "healthy",
        "service": "vector_database",
        "embedding_model": model_info['model_name'],
        "dimension": model_info['dimension']
    }


@app.post("/embed", response_model=EmbedResponse)
async def create_embeddings(request: EmbedRequest):
    """
    Generate embeddings for texts.
    
    Args:
        request: Embedding request with texts
        
    Returns:
        Embeddings
    """
    try:
        embeddings = embedding_service.embed_batch(request.texts)
        
        return EmbedResponse(
            embeddings=embeddings,
            dimension=embedding_service.dimension
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert")
async def upsert_chunks(request: UpsertRequest):
    """
    Upsert chunks to vector database.
    
    Args:
        request: Upsert request with chunks
        
    Returns:
        Success message
    """
    try:
        global vector_store
        if not vector_store:
            vector_store = VectorStore()
        
        await vector_store.upsert_chunks(request.chunks)
        
        return {
            "status": "success",
            "chunks_upserted": len(request.chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_vectors(request: SearchRequest):
    """
    Search vector database.
    
    Args:
        request: Search request
        
    Returns:
        Search results
    """
    try:
        global vector_store
        if not vector_store:
            vector_store = VectorStore()
        
        results = await vector_store.similarity_search(
            query=request.query,
            top_k=request.top_k,
            filter=request.filter
        )
        
        return SearchResponse(
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document from vector database."""
    try:
        global vector_store
        if not vector_store:
            vector_store = VectorStore()
        
        await vector_store.delete_document(doc_id)
        
        return {"status": "success", "doc_id": doc_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/resources")
async def list_resources():
    """List available MCP resources."""
    return {
        "resources": [
            {
                "uri": "vector://embeddings",
                "name": "Embeddings",
                "description": "Generate text embeddings",
                "mimeType": "application/json"
            },
            {
                "uri": "vector://search",
                "name": "Vector Search",
                "description": "Search vector database",
                "mimeType": "application/json"
            },
            {
                "uri": "vector://upsert",
                "name": "Upsert Vectors",
                "description": "Add/update vectors in database",
                "mimeType": "application/json"
            }
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
