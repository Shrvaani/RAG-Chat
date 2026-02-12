"""API routes for query processing."""

from fastapi import APIRouter, HTTPException
from backend.models.schemas import QueryRequest, QueryResponse, Citation
from backend.agents.workflow import RAGWorkflow
from backend.services.conversation_manager import ConversationManager
from backend.services.hybrid_search import HybridSearch
from backend.services.vector_store import VectorStore
import time
from datetime import datetime

router = APIRouter(prefix="/query", tags=["query"])

# Initialize services
conversation_manager = ConversationManager()


@router.post("/", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query using the RAG system.
    
    This endpoint:
    1. Analyzes the query
    2. Retrieves relevant documents
    3. Re-ranks results
    4. Generates response
    5. Adds citations
    """
    start_time = time.time()
    
    try:
        # Create or get conversation
        if not request.conversation_id:
            conversation_id = conversation_manager.create_conversation()
        else:
            conversation_id = request.conversation_id
        
        # Add user message
        conversation_manager.add_message(
            conversation_id,
            role="user",
            content=request.query
        )
        
        # Initialize workflow
        try:
            vector_store = VectorStore()
            hybrid_search = HybridSearch(vector_store)
            workflow = RAGWorkflow(hybrid_search)
            
            # Run workflow
            result = await workflow.run(request.query, conversation_id)
            
            # Extract response from final state
            # Note: The key is 'final_response' or 'generated_response'
            response_text = result.get("final_response") or result.get("generated_response", "No response generated.")
            citations_list = result.get("citations", [])
            
        except Exception as e:
            print(f"Workflow error: {e}")
            # Fallback if workflow fails
            response_text = f"I encountered an error processing your query: {str(e)}"
            citations_list = []

        # Add assistant message
        conversation_manager.add_message(
            conversation_id,
            role="assistant",
            content=response_text,
            citations=citations_list
        )
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            response=response_text,
            citations=[Citation(**c) for c in citations_list],
            conversation_id=conversation_id,
            processing_time=processing_time,
            metadata={
                "status": "success",
                "note": "Full workflow requires Pinecone configuration"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
