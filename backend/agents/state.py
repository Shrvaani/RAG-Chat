"""Agent state definition for LangGraph multi-agent system."""

from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Shared state for all agents in the RAG system.
    
    This state is passed between agents and updated as the workflow progresses.
    """
    # User input
    query: str
    conversation_id: Optional[str]
    
    # Messages (for LLM interactions)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Query analysis
    query_type: Optional[str]  # "factual", "analytical", "conversational"
    needs_web_search: bool
    search_keywords: List[str]
    
    # Retrieved documents
    retrieved_chunks: List[Dict]  # From vector/hybrid search
    web_results: List[Dict]  # From web search (if needed)
    
    # Re-ranked results
    reranked_chunks: List[Dict]
    
    # Generation
    generated_response: Optional[str]
    
    # Citations
    citations: List[Dict]
    final_response: Optional[str]
    
    # Metadata
    processing_steps: List[str]  # Track which agents have run
    error: Optional[str]


class QueryAnalysisResult(TypedDict):
    """Result from query analysis agent."""
    query_type: str
    needs_web_search: bool
    search_keywords: List[str]
    reasoning: str


class RetrievalResult(TypedDict):
    """Result from retrieval agent."""
    chunks: List[Dict]
    source: str  # "vector_db", "hybrid", "web"
    total_found: int


class RerankingResult(TypedDict):
    """Result from re-ranking agent."""
    reranked_chunks: List[Dict]
    scores: List[float]
    method: str  # "relevance", "cross_encoder"


class GenerationResult(TypedDict):
    """Result from generation agent."""
    response: str
    sources_used: List[str]
    confidence: float


class CitationResult(TypedDict):
    """Result from citation agent."""
    final_response: str
    citations: List[Dict]
    citation_format: str  # "inline", "footnote"
