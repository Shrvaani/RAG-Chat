# How to Run the Complete RAG System

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ installed
- Virtual environment activated
- All dependencies installed

### Step 1: Install Dependencies (if not done)

```bash
# From project root
cd "/Users/alexander/Documents/tinker/RAG - Document uploader"

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys (optional for basic testing)
# - PINECONE_API_KEY (for vector storage)
# - HUGGINGFACE_API_KEY (for LLM)
```

### Step 3: Run the Backend API

```bash
# From project root
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Step 4: Run MCP Servers (Optional - for full functionality)

Open **3 separate terminals** and run from project root:

**Terminal 1 - Web Search MCP:**
```bash
# From project root
python -m backend.mcp.servers.web_search_server
```

**Terminal 2 - Vector DB MCP:**
```bash
# From project root
python -m backend.mcp.servers.vector_db_server
```

**Terminal 3 - Document Processing MCP:**
```bash
# From project root
python -m backend.mcp.servers.document_processor_server
```

### Step 5: Open the Frontend

```bash
# Simply open the HTML file in your browser
open frontend/index.html

# Or use Python's HTTP server
cd frontend
python -m http.server 8080
```

Then visit: **http://localhost:8080**

## 📋 Complete System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)                │
│                   http://localhost:8080                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Main FastAPI Backend                        │
│              http://localhost:8000                       │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Multi-Agent RAG Workflow                 │   │
│  │  Query → Retrieval → Rerank → Generate → Cite   │   │
│  └────────────────┬────────────────────────────────┘   │
└───────────────────┼──────────────────────────────────────┘
                    │ MCP Client
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Web Search   │ │  Vector DB   │ │  Document    │
│ MCP Server   │ │  MCP Server  │ │  Processing  │
│ Port 8001    │ │ Port 8002    │ │  Port 8003   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🎯 Usage

### 1. Upload Documents
- Click "Upload Files" or drag & drop
- Supports: PDF, TXT, MD files
- Documents are processed and chunked automatically

### 2. Ask Questions
- Type your question in the chat input
- Press Enter or click "Send"
- Get AI-powered answers with citations

### 3. Manage Conversations
- Click "New Chat" to start fresh
- View conversation history in sidebar
- Click any conversation to load it

## 🧪 Testing

### Test Backend Only
```bash
# Test Phase 2 (Document Processing)
python test_phase2.py

# Test Phase 3 (Vector DB & Embeddings)
python test_phase3.py

# Test Phase 4 (Multi-Agent System)
python test_phase4.py

# Test Phase 5 & 6 (MCP & API)
python test_phase5_6.py
```

### Test MCP Servers
```bash
# Make sure MCP servers are running first
python backend/mcp/test_mcp_servers.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health/

# Upload document
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@sample_rag_document.pdf"

# Query
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "top_k": 5}'
```

## 🔧 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify virtual environment is activated
- Check all dependencies are installed

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify API_BASE_URL in `frontend/app.js`

### MCP servers not responding
- Make sure all 3 MCP servers are running
- Check ports 8001, 8002, 8003 are available
- Verify MCP server URLs in `.env`

### No responses from queries
- Check if documents are uploaded
- Verify Pinecone API key (if using vector storage)
- Check backend logs for errors

## 📦 Deployment

### Deploy to Render (Free)
See `backend/mcp/DEPLOYMENT.md` for complete guide.

### Quick Deploy
1. Push code to GitHub
2. Create 4 Render services:
   - Main API
   - Web Search MCP
   - Vector DB MCP
   - Document Processing MCP
3. Deploy frontend to Netlify/Vercel

## 🎉 You're All Set!

Your Advanced RAG Document Q&A System is ready to use!

**Default URLs:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Web Search MCP: http://localhost:8001
- Vector DB MCP: http://localhost:8002
- Doc Processing MCP: http://localhost:8003
