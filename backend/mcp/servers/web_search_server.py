"""
Web Search MCP Server

Exposes web search functionality via Model Context Protocol.

Run from project root: python -m backend.mcp.servers.web_search_server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.services.web_search import WebSearchService
import uvicorn

app = FastAPI(
    title="Web Search MCP Server",
    description="MCP server for web search operations",
    version="1.0.0"
)

# Initialize web search service
web_search = WebSearchService()


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    """Search response schema."""
    results: List[Dict]
    total: int
    provider: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Web Search MCP Server",
        "version": "1.0.0",
        "protocol": "MCP",
        "capabilities": ["web_search"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "web_search",
        "provider": web_search.provider
    }


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Perform web search.
    
    Args:
        request: Search request with query and max_results
        
    Returns:
        Search results
    """
    try:
        results = await web_search.search(
            query=request.query,
            max_results=request.max_results
        )
        
        return SearchResponse(
            results=results,
            total=len(results),
            provider=web_search.provider
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/resources")
async def list_resources():
    """List available MCP resources."""
    return {
        "resources": [
            {
                "uri": "search://web",
                "name": "Web Search",
                "description": "Search the web using DuckDuckGo or Tavily",
                "mimeType": "application/json"
            }
        ]
    }


@app.post("/mcp/resources/search")
async def get_resource(request: SearchRequest):
    """Get resource via MCP protocol."""
    return await search(request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
