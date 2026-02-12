# MCP Folder Structure

## ✅ Reorganized Structure

All MCP-related files are now organized in `backend/mcp/`:

```
backend/mcp/
├── __init__.py
├── client.py                    # MCP Client (connects to servers)
├── DEPLOYMENT.md                # Deployment guide
├── test_mcp_servers.py          # Test all servers
├── servers/                     # MCP Server implementations
│   ├── web_search_server.py     # Web Search MCP (Port 8001)
│   ├── vector_db_server.py      # Vector DB MCP (Port 8002)
│   ├── document_processor_server.py  # Doc Processing MCP (Port 8003)
│   └── requirements.txt         # Server dependencies
└── deploy/                      # Deployment configurations
    ├── render_web_search.yaml
    ├── render_vector_db.yaml
    └── render_doc_processor.yaml
```

## Quick Start

### Run MCP Servers Locally

```bash
# From project root
cd backend/mcp/servers

# Terminal 1
python web_search_server.py

# Terminal 2
python vector_db_server.py

# Terminal 3
python document_processor_server.py
```

### Test MCP Servers

```bash
# From project root
python backend/mcp/test_mcp_servers.py
```

### Deploy to Render

See `backend/mcp/DEPLOYMENT.md` for complete guide.

## Files Overview

| File | Purpose |
|------|---------|
| `client.py` | HTTP client to connect to MCP servers |
| `servers/web_search_server.py` | Web search service (DuckDuckGo/Tavily) |
| `servers/vector_db_server.py` | Vector DB operations (Pinecone + embeddings) |
| `servers/document_processor_server.py` | Document upload, extract, chunk |
| `deploy/*.yaml` | Render deployment configs |
| `DEPLOYMENT.md` | Complete deployment guide |
| `test_mcp_servers.py` | Test suite for all servers |

All paths have been updated to reflect the new structure! ✅
