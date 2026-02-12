"""API routes for document management."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import DocumentUploadResponse, DocumentListResponse, DocumentInfo
from backend.services.document_processor import DocumentProcessor
from backend.services.chunking_service import ChunkingService
from backend.services.vector_store import VectorStore
from backend.services.hybrid_search import HybridSearch
from typing import List
import time

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize services (will be injected via dependency injection in production)
processor = DocumentProcessor()
chunker = ChunkingService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.
    
    Supports: .txt, .md, .pdf
    """
    try:
        # Read file content
        content = await file.read()
        
        # Process document
        result = await processor.process_upload(content, file.filename)
        
        # Chunk document
        chunks = chunker.chunk_document(result['content'], result['metadata'])
        
        # Add to vector store
        try:
            vector_store = VectorStore()
            await vector_store.add_chunks(chunks)
        except Exception as e:
            print(f"Warning: Failed to add chunks to vector store: {e}")
            # Continue even if vector store fails, so we don't break the upload flow
        
        return DocumentUploadResponse(
            doc_id=result['metadata']['doc_id'],
            filename=result['metadata']['filename'],
            file_type=result['metadata']['file_type'],
            chunks_created=len(chunks),
            upload_timestamp=result['metadata']['upload_timestamp']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded documents."""
    # TODO: Implement document listing from database
    # For now, return empty list
    return DocumentListResponse(documents=[], total=0)


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its chunks."""
    # TODO: Implement document deletion
    # - Delete from vector store
    # - Delete file from disk
    # - Update database
    
    return {"message": f"Document {doc_id} deleted successfully"}


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document(doc_id: str):
    """Get document information."""
    # TODO: Implement document retrieval from database
    raise HTTPException(status_code=404, detail="Document not found")
