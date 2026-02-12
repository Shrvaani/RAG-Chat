"""Query Analysis Agent - Analyzes user queries and determines search strategy."""

from typing import Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEndpoint
from backend.config import settings
from backend.agents.state import AgentState, QueryAnalysisResult
import json


class QueryAnalysisAgent:
    """
    Analyzes user queries to determine:
    1. Query type (factual, analytical, conversational)
    2. Whether web search is needed
    3. Key search keywords
    """
    
    def __init__(self):
        """Initialize query analysis agent."""
        self.llm = None
        if settings.huggingface_api_key:
            self.llm = HuggingFaceEndpoint(
                repo_id=settings.hf_model_name,
                huggingfacehub_api_token=settings.huggingface_api_key,
                temperature=0.1,
                max_new_tokens=512
            )
    
    async def analyze(self, state: AgentState) -> AgentState:
        """
        Analyze the query and update state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with query analysis
        """
        query = state["query"]
        
        # Add processing step
        state["processing_steps"].append("query_analysis")
        
        if self.llm:
            # Use LLM for sophisticated analysis
            result = await self._llm_analysis(query)
        else:
            # Fallback to rule-based analysis
            result = self._rule_based_analysis(query)
        
        # Update state
        state["query_type"] = result["query_type"]
        state["needs_web_search"] = result["needs_web_search"]
        state["search_keywords"] = result["search_keywords"]
        
        print(f"📊 Query Analysis:")
        print(f"   Type: {result['query_type']}")
        print(f"   Web search needed: {result['needs_web_search']}")
        print(f"   Keywords: {result['search_keywords']}")
        
        return state
    
    async def _llm_analysis(self, query: str) -> QueryAnalysisResult:
        """Use LLM for query analysis."""
        
        system_prompt = """You are a query analysis expert. Analyze the user's query and provide:
1. Query type: "factual" (seeking specific facts), "analytical" (requiring reasoning), or "conversational" (general chat)
2. Whether web search is needed (true if query requires current information not in documents)
3. Key search keywords (3-5 important terms)

Respond in JSON format:
{
    "query_type": "factual|analytical|conversational",
    "needs_web_search": true|false,
    "search_keywords": ["keyword1", "keyword2", ...],
    "reasoning": "brief explanation"
}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Query: {query}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            result = json.loads(response)
            
            return QueryAnalysisResult(
                query_type=result.get("query_type", "factual"),
                needs_web_search=result.get("needs_web_search", False),
                search_keywords=result.get("search_keywords", []),
                reasoning=result.get("reasoning", "")
            )
        except Exception as e:
            print(f"⚠️  LLM analysis failed: {e}, using fallback")
            return self._rule_based_analysis(query)
    
    def _rule_based_analysis(self, query: str) -> QueryAnalysisResult:
        """Fallback rule-based analysis."""
        
        query_lower = query.lower()
        
        # Determine query type
        question_words = ["what", "why", "how", "when", "where", "who"]
        conversational_words = ["hello", "hi", "thanks", "thank you"]
        
        if any(word in query_lower for word in conversational_words):
            query_type = "conversational"
        elif any(query_lower.startswith(word) for word in question_words):
            if "why" in query_lower or "how" in query_lower:
                query_type = "analytical"
            else:
                query_type = "factual"
        else:
            query_type = "factual"
        
        # Determine if web search is needed
        current_info_indicators = [
            "latest", "recent", "current", "today", "now",
            "2024", "2025", "2026", "this year"
        ]
        needs_web_search = any(word in query_lower for word in current_info_indicators)
        
        # Extract keywords (simple: remove common words)
        stop_words = {
            "what", "is", "the", "a", "an", "in", "on", "at", "to", "for",
            "of", "and", "or", "but", "with", "from", "by", "about"
        }
        
        words = query_lower.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2][:5]
        
        return QueryAnalysisResult(
            query_type=query_type,
            needs_web_search=needs_web_search,
            search_keywords=keywords,
            reasoning="Rule-based analysis"
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        agent = QueryAnalysisAgent()
        
        state = AgentState(
            query="What is Retrieval-Augmented Generation?",
            conversation_id=None,
            messages=[],
            needs_web_search=False,
            search_keywords=[],
            retrieved_chunks=[],
            web_results=[],
            reranked_chunks=[],
            generated_response=None,
            citations=[],
            final_response=None,
            processing_steps=[],
            error=None,
            query_type=None
        )
        
        result = await agent.analyze(state)
        print(f"\nResult: {result['query_type']}")
    
    asyncio.run(test())
