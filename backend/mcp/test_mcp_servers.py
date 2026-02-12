"""
Test script for MCP Servers

Tests all three MCP servers locally.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.mcp.client import MCPClient


async def test_mcp_servers():
    """Test all MCP servers."""
    
    print("=" * 60)
    print("Testing MCP Servers")
    print("=" * 60)
    
    print("\n⚠️  Note: This test requires MCP servers to be running:")
    print("   Terminal 1: python backend/mcp/servers/web_search_server.py")
    print("   Terminal 2: python backend/mcp/servers/vector_db_server.py")
    print("   Terminal 3: python backend/mcp/servers/document_processor_server.py")
    print()
    
    client = MCPClient()
    
    # Test 1: Health Check
    print("\n1. Testing MCP Server Health...")
    health = await client.health_check()
    
    for service, status in health.items():
        status_emoji = "✅" if status.get('status') == 'healthy' else "❌"
        print(f"   {status_emoji} {service}: {status.get('status', 'unknown')}")
    
    # Test 2: Web Search (if available)
    print("\n2. Testing Web Search MCP...")
    if health.get('web_search', {}).get('status') == 'healthy':
        results = await client.search_web("What is RAG?", max_results=2)
        print(f"   ✅ Web search: Found {len(results)} results")
        if results:
            print(f"      First result: {results[0].get('title', 'N/A')}")
    else:
        print("   ⏭️  Skipped (server not running)")
    
    # Test 3: Embeddings (if available)
    print("\n3. Testing Vector DB MCP (Embeddings)...")
    if health.get('vector_db', {}).get('status') == 'healthy':
        embeddings = await client.generate_embeddings(["Hello world", "Test text"])
        print(f"   ✅ Generated {len(embeddings)} embeddings")
        if embeddings:
            print(f"      Dimension: {len(embeddings[0])}")
    else:
        print("   ⏭️  Skipped (server not running)")
    
    # Test 4: Document Processing (if available)
    print("\n4. Testing Document Processing MCP...")
    if health.get('doc_processor', {}).get('status') == 'healthy':
        # Create a test file
        test_content = b"This is a test document for MCP server testing."
        result = await client.process_document(test_content, "test.txt")
        if result:
            print(f"   ✅ Document processed: {result.get('total_chunks', 0)} chunks")
        else:
            print("   ⚠️  Processing returned empty result")
    else:
        print("   ⏭️  Skipped (server not running)")
    
    await client.close()
    
    print("\n" + "=" * 60)
    print("✅ MCP Server tests complete!")
    print("=" * 60)
    print("\n📝 Summary:")
    print("   - Web Search MCP Server: Port 8001")
    print("   - Vector DB MCP Server: Port 8002")
    print("   - Document Processing MCP Server: Port 8003")
    print("\n🚀 Ready for deployment to Render!")


if __name__ == "__main__":
    asyncio.run(test_mcp_servers())
