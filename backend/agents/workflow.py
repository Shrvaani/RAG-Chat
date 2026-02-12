"""LangGraph workflow orchestrating the multi-agent RAG system."""

from langgraph.graph import StateGraph, END
from backend.agents.state import AgentState
from backend.agents.query_analysis_agent import QueryAnalysisAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.reranking_agent import RerankingAgent
from backend.agents.generation_agent import GenerationAgent
from backend.agents.citation_agent import CitationAgent
from backend.services.hybrid_search import HybridSearch
from typing import Dict


class RAGWorkflow:
    """
    LangGraph workflow for multi-agent RAG system.
    
    Workflow:
    1. Query Analysis → 2. Retrieval → 3. Re-ranking → 4. Generation → 5. Citation
    """
    
    def __init__(self, hybrid_search: HybridSearch):
        """
        Initialize RAG workflow.
        
        Args:
            hybrid_search: Hybrid search service instance
        """
        # Initialize agents
        self.query_agent = QueryAnalysisAgent()
        self.retrieval_agent = RetrievalAgent(hybrid_search)
        self.reranking_agent = RerankingAgent()
        self.generation_agent = GenerationAgent()
        self.citation_agent = CitationAgent()
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("query_analysis", self.query_agent.analyze)
        workflow.add_node("retrieval", self.retrieval_agent.retrieve)
        workflow.add_node("reranking", self.reranking_agent.rerank)
        workflow.add_node("generation", self.generation_agent.generate)
        workflow.add_node("citation", self.citation_agent.add_citations)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("query_analysis")
        
        workflow.add_edge("query_analysis", "retrieval")
        workflow.add_edge("retrieval", "reranking")
        workflow.add_edge("reranking", "generation")
        workflow.add_edge("generation", "citation")
        workflow.add_edge("citation", END)
        
        # Compile graph
        return workflow.compile()
    
    async def run(self, query: str, conversation_id: str = None) -> Dict:
        """
        Run the RAG workflow.
        
        Args:
            query: User query
            conversation_id: Optional conversation ID
            
        Returns:
            Final state with response and citations
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting RAG Workflow")
        print(f"Query: {query}")
        print(f"{'='*60}\n")
        
        # Initialize state
        initial_state = AgentState(
            query=query,
            conversation_id=conversation_id,
            messages=[],
            query_type=None,
            needs_web_search=False,
            search_keywords=[],
            retrieved_chunks=[],
            web_results=[],
            reranked_chunks=[],
            generated_response=None,
            citations=[],
            final_response=None,
            processing_steps=[],
            error=None
        )
        
        try:
            # Run workflow
            final_state = await self.graph.ainvoke(initial_state)
            
            print(f"\n{'='*60}")
            print(f"✅ Workflow Complete")
            print(f"Processing steps: {' → '.join(final_state['processing_steps'])}")
            print(f"{'='*60}\n")
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ Workflow error: {e}")
            initial_state["error"] = str(e)
            return initial_state
    
    def get_workflow_diagram(self) -> str:
        """Get ASCII diagram of the workflow."""
        return """
RAG Workflow:

┌─────────────────┐
│ Query Analysis  │  Analyze query type, extract keywords
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Retrieval     │  Hybrid search + optional web search
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Re-ranking    │  Re-score by relevance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Generation    │  LLM generates response
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Citation     │  Add source references
└────────┬────────┘
         │
         ▼
       [END]
"""


# Example usage
if __name__ == "__main__":
    import asyncio
    from backend.services.vector_store import VectorStore
    from backend.services.hybrid_search import HybridSearch
    
    async def test_workflow():
        """Test the RAG workflow."""
        
        # Note: This requires Pinecone API key
        # For testing without API key, use mock vector store
        
        print("RAG Workflow Diagram:")
        print(RAGWorkflow(None).get_workflow_diagram())
    
    asyncio.run(test_workflow())
