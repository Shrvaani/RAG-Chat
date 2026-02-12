# MCP Servers Deployment Guide

## Overview

This project includes **3 separate MCP (Model Context Protocol) servers** as required by the assignment:

1. **Web Search MCP Server** (Port 8001)
2. **Vector Database MCP Server** (Port 8002)
3. **Document Processing MCP Server** (Port 8003)

## Local Development

### Running All MCP Servers Locally

```bash
# Terminal 1: Web Search MCP Server
cd backend/mcp/servers
python web_search_server.py

# Terminal 2: Vector DB MCP Server
python vector_db_server.py

# Terminal 3: Document Processing MCP Server
python document_processor_server.py

# Terminal 4: Main FastAPI App
cd ../../..
uvicorn main:app --reload
```

### Testing MCP Servers

```bash
# Test Web Search MCP
curl http://localhost:8001/health
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "max_results": 3}'

# Test Vector DB MCP
curl http://localhost:8002/health
curl -X POST http://localhost:8002/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello world"]}'

# Test Document Processing MCP
curl http://localhost:8003/health
curl -X POST http://localhost:8003/upload \
  -F "file=@sample.pdf"
```

## Deploying to Render (Free Tier)

### Prerequisites

1. Create a [Render account](https://render.com) (free)
2. Push your code to GitHub
3. Have your API keys ready (Pinecone, HuggingFace, etc.)

### Deployment Steps

#### 1. Deploy Web Search MCP Server

1. Go to Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `web-search-mcp`
   - **Region:** Oregon (Free)
   - **Branch:** main
   - **Root Directory:** `mcp_servers`
   - **Build Command:** `pip install -r requirements.txt && pip install -r ../requirements.txt`
   - **Start Command:** `python web_search_server.py`
   - **Instance Type:** Free
4. Add Environment Variables:
   - `PYTHON_VERSION`: 3.11.0
   - `WEB_SEARCH_PROVIDER`: duckduckgo
   - `PORT`: 8001
5. Click **Create Web Service**
6. Copy the deployed URL (e.g., `https://web-search-mcp.onrender.com`)

#### 2. Deploy Vector DB MCP Server

1. Render Dashboard → **New** → **Web Service**
2. Configure:
   - **Name:** `vector-db-mcp`
   - **Root Directory:** `mcp_servers`
   - **Build Command:** `pip install -r requirements.txt && pip install -r ../requirements.txt`
   - **Start Command:** `python vector_db_server.py`
3. Add Environment Variables:
   - `PYTHON_VERSION`: 3.11.0
   - `PINECONE_API_KEY`: [your-key]
   - `PINECONE_ENVIRONMENT`: gcp-starter
   - `PINECONE_INDEX_NAME`: rag-documents
   - `PORT`: 8002
4. Deploy and copy URL

#### 3. Deploy Document Processing MCP Server

1. Render Dashboard → **New** → **Web Service**
2. Configure:
   - **Name:** `doc-processor-mcp`
   - **Root Directory:** `mcp_servers`
   - **Build Command:** `pip install -r requirements.txt && pip install -r ../requirements.txt`
   - **Start Command:** `python document_processor_server.py`
3. Add Environment Variables:
   - `PYTHON_VERSION`: 3.11.0
   - `UPLOAD_DIR`: /tmp/uploads
   - `PORT`: 8003
4. Deploy and copy URL

#### 4. Deploy Main FastAPI Application

1. Render Dashboard → **New** → **Web Service**
2. Configure:
   - **Name:** `rag-api`
   - **Root Directory:** `.` (root)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - All your API keys
   - **MCP Server URLs:**
     - `MCP_WEB_SEARCH_HOST`: web-search-mcp.onrender.com
     - `MCP_VECTOR_DB_HOST`: vector-db-mcp.onrender.com
     - `MCP_DOC_PROCESSOR_HOST`: doc-processor-mcp.onrender.com
4. Deploy

## Environment Variables for Main App

Update your `.env` file with deployed MCP server URLs:

```env
# MCP Server URLs (Render deployment)
MCP_WEB_SEARCH_HOST=web-search-mcp.onrender.com
MCP_WEB_SEARCH_PORT=443
MCP_VECTOR_DB_HOST=vector-db-mcp.onrender.com
MCP_VECTOR_DB_PORT=443
MCP_DOC_PROCESSOR_HOST=doc-processor-mcp.onrender.com
MCP_DOC_PROCESSOR_PORT=443
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Main FastAPI App                      │
│                  (rag-api.onrender.com)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ MCP Client (HTTP)
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Web Search   │ │  Vector DB   │ │  Document    │
│ MCP Server   │ │  MCP Server  │ │  Processing  │
│              │ │              │ │  MCP Server  │
│ Port 8001    │ │ Port 8002    │ │ Port 8003    │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Cost Breakdown (Free Tier)

- **Web Search MCP:** Free (Render free tier)
- **Vector DB MCP:** Free (Render free tier)
- **Document Processing MCP:** Free (Render free tier)
- **Main API:** Free (Render free tier)
- **Total:** $0/month ✅

**Note:** Render free tier services spin down after 15 minutes of inactivity. First request after spin-down may take 30-60 seconds.

## Testing Deployed MCP Servers

```bash
# Test deployed servers
curl https://web-search-mcp.onrender.com/health
curl https://vector-db-mcp.onrender.com/health
curl https://doc-processor-mcp.onrender.com/health
```

## Troubleshooting

### MCP Server Not Responding
- Check Render logs for errors
- Verify environment variables are set
- Ensure build completed successfully

### Connection Timeout
- Free tier services sleep after inactivity
- Wait 30-60 seconds for cold start
- Consider upgrading to paid tier for always-on

### CORS Issues
- Add CORS middleware to MCP servers if needed
- Configure allowed origins in main app

## Next Steps

1. Deploy all 4 services to Render
2. Update main app with MCP server URLs
3. Test end-to-end workflow
4. Deploy frontend (Phase 7)
