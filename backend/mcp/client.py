"""
Updated MCP Client to connect to separate MCP servers.
"""

import httpx
from typing import List, Dict, Optional
from backend.config import settings


class MCPClient:
    """
    MCP Client for connecting to separate MCP servers.
    
    Connects to:
    - Web Search MCP Server (port 8001)
    - Vector Database MCP Server (port 8002)
    - Document Processing MCP Server (port 8003)
    """
    
    def __init__(self):
        """Initialize MCP client with server URLs."""
        self.web_search_url = f"http://{settings.mcp_web_search_host}:{settings.mcp_web_search_port}"
        self.vector_db_url = f"http://{settings.mcp_vector_db_host}:{settings.mcp_vector_db_port}"
        self.doc_processor_url = f"http://{settings.mcp_doc_processor_host}:{settings.mcp_doc_processor_port}"
        
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using Web Search MCP Server.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            response = await self.client.post(
                f"{self.web_search_url}/search",
                json={"query": query, "max_results": max_results}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Web search MCP error: {e}")
            return []
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Vector DB MCP Server.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        try:
            response = await self.client.post(
                f"{self.vector_db_url}/embed",
                json={"texts": texts}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])
        except Exception as e:
            print(f"Embedding MCP error: {e}")
            return []
    
    async def vector_search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search vector database using Vector DB MCP Server.
        
        Args:
            query: Search query
            top_k: Number of results
            filter: Optional metadata filter
            
        Returns:
            Search results
        """
        try:
            response = await self.client.post(
                f"{self.vector_db_url}/search",
                json={"query": query, "top_k": top_k, "filter": filter}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Vector search MCP error: {e}")
            return []
    
    async def upsert_vectors(self, chunks: List[Dict]) -> bool:
        """
        Upsert vectors using Vector DB MCP Server.
        
        Args:
            chunks: List of chunks with embeddings
            
        Returns:
            Success status
        """
        try:
            response = await self.client.post(
                f"{self.vector_db_url}/upsert",
                json={"chunks": chunks}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Upsert MCP error: {e}")
            return False
    
    async def process_document(self, file_content: bytes, filename: str) -> Dict:
        """
        Process document using Document Processing MCP Server.
        
        Args:
            file_content: File content bytes
            filename: Original filename
            
        Returns:
            Processing result with chunks
        """
        try:
            files = {"file": (filename, file_content)}
            response = await self.client.post(
                f"{self.doc_processor_url}/process",
                files=files
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Document processing MCP error: {e}")
            return {}
    
    async def health_check(self) -> Dict:
        """
        Check health of all MCP servers.
        
        Returns:
            Dictionary with service status
        """
        health = {}
        
        # Check web search
        try:
            response = await self.client.get(f"{self.web_search_url}/health")
            health['web_search'] = response.json() if response.status_code == 200 else {'status': 'unhealthy'}
        except:
            health['web_search'] = {'status': 'unreachable'}
        
        # Check vector DB
        try:
            response = await self.client.get(f"{self.vector_db_url}/health")
            health['vector_db'] = response.json() if response.status_code == 200 else {'status': 'unhealthy'}
        except:
            health['vector_db'] = {'status': 'unreachable'}
        
        # Check document processor
        try:
            response = await self.client.get(f"{self.doc_processor_url}/health")
            health['doc_processor'] = response.json() if response.status_code == 200 else {'status': 'unhealthy'}
        except:
            health['doc_processor'] = {'status': 'unreachable'}
        
        return health
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        client = MCPClient()
        
        # Test health check
        health = await client.health_check()
        print(f"MCP Servers Health: {health}")
        
        await client.close()
    
    asyncio.run(test())
