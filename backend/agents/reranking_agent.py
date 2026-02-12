"""Re-ranking Agent - Re-ranks retrieved documents by relevance."""

from typing import List, Dict
from backend.agents.state import AgentState
from backend.services.embedding_service import EmbeddingService


class RerankingAgent:
    """
    Re-ranks retrieved documents to improve relevance.
    
    Uses embedding similarity for re-ranking.
    """
    
    def __init__(self):
        """Initialize re-ranking agent."""
        self.embedding_service = EmbeddingService()
    
    async def rerank(self, state: AgentState) -> AgentState:
        """
        Re-rank retrieved documents and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with re-ranked chunks
        """
        query = state["query"]
        chunks = state.get("retrieved_chunks", [])
        
        # Add processing step
        state["processing_steps"].append("reranking")
        
        if not chunks:
            print("⚠️  No chunks to re-rank")
            state["reranked_chunks"] = []
            return state
        
        print(f"🔄 Re-ranking {len(chunks)} chunks...")
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Calculate relevance scores
        scored_chunks = []
        for chunk in chunks:
            # Get chunk embedding
            chunk_embedding = self.embedding_service.embed_text(chunk['content'])
            
            # Calculate similarity
            similarity = self.embedding_service.similarity(
                query_embedding,
                chunk_embedding
            )
            
            # Combine with existing score (if any)
            existing_score = chunk.get('score', 0.5)
            final_score = (similarity * 0.6) + (existing_score * 0.4)
            
            scored_chunks.append({
                **chunk,
                'rerank_score': final_score,
                'similarity': similarity
            })
        
        # Sort by re-rank score
        scored_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # Take top results
        from backend.config import settings
        top_chunks = scored_chunks[:settings.reranking_top_k]
        
        state["reranked_chunks"] = top_chunks
        
        print(f"   ✅ Re-ranked to top {len(top_chunks)} chunks")
        if top_chunks:
            print(f"   Top score: {top_chunks[0]['rerank_score']:.4f}")
        
        return state
