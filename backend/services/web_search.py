"""
Free Web Search Integration - DuckDuckGo & Tavily

This module provides free web search capabilities without requiring paid API keys.
"""

from typing import List, Dict, Optional
from duckduckgo_search import DDGS
from backend.config import settings


class WebSearchService:
    """Free web search using DuckDuckGo or Tavily."""
    
    def __init__(self):
        self.provider = settings.web_search_provider
        
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform web search using configured provider.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        if self.provider == "duckduckgo":
            return await self._duckduckgo_search(query, max_results)
        elif self.provider == "tavily":
            return await self._tavily_search(query, max_results)
        else:
            raise ValueError(f"Unknown search provider: {self.provider}")
    
    async def _duckduckgo_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Search using DuckDuckGo (FREE - No API key needed).
        
        Uses duckduckgo-search library which doesn't require authentication.
        """
        results = []
        
        try:
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                
                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', ''),
                        'source': 'duckduckgo'
                    })
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            
        return results
    
    async def _tavily_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Search using Tavily API (FREE tier: 1000 requests/month).
        
        Requires TAVILY_API_KEY in environment variables.
        Sign up at: https://tavily.com
        """
        if not settings.tavily_api_key:
            raise ValueError("Tavily API key not configured")
        
        try:
            # Import only if using Tavily
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=settings.tavily_api_key)
            response = client.search(query, max_results=max_results)
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('content', ''),
                    'source': 'tavily'
                })
                
            return results
            
        except Exception as e:
            print(f"Tavily search error: {e}")
            return []


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        search = WebSearchService()
        results = await search.search("What is RAG in AI?", max_results=3)
        
        print(f"Found {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
    
    asyncio.run(test_search())
