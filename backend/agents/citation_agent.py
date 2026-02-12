"""Citation Agent - Adds citations to generated responses."""

from typing import List, Dict
from backend.agents.state import AgentState
import re


class CitationAgent:
    """
    Adds citations to generated responses.
    
    Formats citations inline with [1], [2] notation and provides
    a reference list at the end.
    """
    
    def __init__(self):
        """Initialize citation agent."""
        pass
    
    async def add_citations(self, state: AgentState) -> AgentState:
        """
        Add citations to response and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with citations and final response
        """
        response = state.get("generated_response", "")
        chunks = state.get("reranked_chunks", [])
        web_results = state.get("web_results", [])
        
        # Add processing step
        state["processing_steps"].append("citation")
        
        if not response:
            state["final_response"] = ""
            state["citations"] = []
            return state
        
        print(f"📝 Adding citations...")
        
        # Build citations
        citations = []
        citation_map = {}
        
        # Add document citations
        for i, chunk in enumerate(chunks[:5], 1):
            metadata = chunk.get('metadata', {})
            filename = metadata.get('filename', 'Unknown Document')
            page = metadata.get('page_number')
            
            citation = {
                'id': i,
                'type': 'document',
                'filename': filename,
                'page': page,
                'content_preview': chunk.get('content', '')[:100]
            }
            citations.append(citation)
            citation_map[filename] = i
        
        # Add web citations
        web_start = len(citations) + 1
        for i, result in enumerate(web_results[:3], web_start):
            citation = {
                'id': i,
                'type': 'web',
                'title': result.get('title', 'Web Source'),
                'url': result.get('url', ''),
                'snippet': result.get('snippet', '')[:100]
            }
            citations.append(citation)
        
        # Format final response with citations
        final_response = self._format_with_citations(response, citations)
        
        state["citations"] = citations
        state["final_response"] = final_response
        
        print(f"   ✅ Added {len(citations)} citations")
        
        return state
    
    def _format_with_citations(self, response: str, citations: List[Dict]) -> str:
        """Format response with inline citations and reference list."""
        
        # For now, just append citations at the end
        # In a more sophisticated version, we could parse the response
        # and add inline citations where sources are mentioned
        
        formatted = response + "\n\n"
        
        if citations:
            formatted += "**Sources:**\n\n"
            
            for citation in citations:
                if citation['type'] == 'document':
                    formatted += f"[{citation['id']}] {citation['filename']}"
                    if citation.get('page'):
                        formatted += f", Page {citation['page']}"
                    formatted += "\n"
                elif citation['type'] == 'web':
                    formatted += f"[{citation['id']}] {citation['title']}\n"
                    formatted += f"    {citation['url']}\n"
        
        return formatted
    
    def _add_inline_citations(self, response: str, citation_map: Dict) -> str:
        """
        Add inline citations to response (advanced feature).
        
        This would analyze the response and add [1], [2] markers
        where specific sources are referenced.
        """
        # TODO: Implement sophisticated citation matching
        # For now, return response as-is
        return response
