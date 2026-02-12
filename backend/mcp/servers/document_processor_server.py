"""
Document Processing MCP Server

Exposes document processing functionality via Model Context Protocol.

Run from project root: python -m backend.mcp.servers.document_processor_server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from backend.services.document_processor import DocumentProcessor
from backend.services.chunking_service import ChunkingService
import uvicorn

app = FastAPI(
    title="Document Processing MCP Server",
    description="MCP server for document processing operations",
    version="1.0.0"
)

# Initialize services
processor = DocumentProcessor()
chunker = ChunkingService()


class ChunkRequest(BaseModel):
    """Chunking request schema."""
    content: str
    metadata: Dict


class ChunkResponse(BaseModel):
    """Chunking response schema."""
    chunks: List[Dict]
    total: int
    statistics: Dict


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Document Processing MCP Server",
        "version": "1.0.0",
        "protocol": "MCP",
        "capabilities": ["upload", "extract", "chunk"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "document_processing",
        "supported_formats": [".txt", ".md", ".pdf"]
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    
    Args:
        file: Uploaded file
        
    Returns:
        Processed document with metadata
    """
    try:
        content = await file.read()
        result = await processor.process_upload(content, file.filename)
        
        return {
            "status": "success",
            "doc_id": result['metadata']['doc_id'],
            "filename": result['metadata']['filename'],
            "file_type": result['metadata']['file_type'],
            "content_length": len(result['content']),
            "metadata": result['metadata']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chunk", response_model=ChunkResponse)
async def chunk_document(request: ChunkRequest):
    """
    Chunk document content.
    
    Args:
        request: Chunking request with content and metadata
        
    Returns:
        Document chunks
    """
    try:
        chunks = chunker.chunk_document(
            content=request.content,
            metadata=request.metadata
        )
        
        stats = chunker.get_chunk_statistics(chunks)
        
        return ChunkResponse(
            chunks=chunks,
            total=len(chunks),
            statistics=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process")
async def process_and_chunk(file: UploadFile = File(...)):
    """
    Upload, process, and chunk a document in one step.
    
    Args:
        file: Uploaded file
        
    Returns:
        Processed chunks
    """
    try:
        # Upload and extract
        content = await file.read()
        result = await processor.process_upload(content, file.filename)
        
        # Chunk
        chunks = chunker.chunk_document(
            content=result['content'],
            metadata=result['metadata']
        )
        
        stats = chunker.get_chunk_statistics(chunks)
        
        return {
            "status": "success",
            "doc_id": result['metadata']['doc_id'],
            "filename": result['metadata']['filename'],
            "chunks": chunks,
            "total_chunks": len(chunks),
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete document files."""
    try:
        # Find and delete document
        # This would need to be implemented based on your storage
        return {"status": "success", "doc_id": doc_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/resources")
async def list_resources():
    """List available MCP resources."""
    return {
        "resources": [
            {
                "uri": "document://upload",
                "name": "Document Upload",
                "description": "Upload and extract text from documents",
                "mimeType": "multipart/form-data"
            },
            {
                "uri": "document://chunk",
                "name": "Document Chunking",
                "description": "Chunk documents into semantic segments",
                "mimeType": "application/json"
            },
            {
                "uri": "document://process",
                "name": "Full Processing",
                "description": "Upload, extract, and chunk in one step",
                "mimeType": "multipart/form-data"
            }
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
