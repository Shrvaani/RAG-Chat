"""Retrieval Agent - Retrieves relevant documents using hybrid search."""

from typing import List, Dict
from backend.agents.state import AgentState
from backend.services.hybrid_search import HybridSearch
from backend.services.web_search import WebSearchService


class RetrievalAgent:
    """
    Retrieves relevant documents from:
    1. Vector database (hybrid search)
    2. Web search (if needed)
    """
    
    def __init__(self, hybrid_search: HybridSearch):
        """
        Initialize retrieval agent.
        
        Args:
            hybrid_search: Hybrid search service instance
        """
        self.hybrid_search = hybrid_search
        self.web_search = WebSearchService()
    
    async def retrieve(self, state: AgentState) -> AgentState:
        """
        Retrieve relevant documents and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with retrieved chunks
        """
        query = state["query"]
        needs_web = state.get("needs_web_search", False)
        
        # Add processing step
        state["processing_steps"].append("retrieval")
        
        # Retrieve from vector database
        print(f"🔍 Retrieving from vector database...")
        vector_results = await self.hybrid_search.hybrid_search(
            query=query,
            top_k=settings.retrieval_top_k,
            dense_weight=0.7,
            sparse_weight=0.3
        )
        
        state["retrieved_chunks"] = vector_results
        print(f"   Found {len(vector_results)} chunks from vector DB")
        
        # Retrieve from web if needed
        if needs_web:
            print(f"🌐 Retrieving from web...")
            web_results = await self.web_search.search(
                query=query,
                max_results=5
            )
            state["web_results"] = web_results
            print(f"   Found {len(web_results)} web results")
        else:
            state["web_results"] = []
        
        return state


# Import settings
from backend.config import settings
