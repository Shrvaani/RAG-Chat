# Advanced RAG System - Document Q&A with Multi-Agent Architecture

A sophisticated Retrieval-Augmented Generation (RAG) application that enables users to upload documents, build a knowledge base, and query content using a multi-agent architecture powered by LangGraph.

## 🎯 Features

- **Multi-Agent Architecture**: 6 specialized agents orchestrated by LangGraph
- **Hybrid Search**: Combines dense vector search with sparse BM25 retrieval
- **Conversation Memory**: Context-aware follow-up questions
- **Document Processing**: Support for .txt, .md, and .pdf files
- **Citations**: Automatic source references in answers
- **MCP Integration**: Model Context Protocol for external services
- **Production-Ready**: Pinecone vector database for scalable deployment

## 🏗️ Architecture

### Technology Stack

- **Backend**: FastAPI
- **LLM**: HuggingFace models (Qwen/Claude)
- **Vector Database**: Pinecone
- **Embeddings**: sentence-transformers (open-source)
- **Agent Orchestration**: LangGraph
- **Search**: Hybrid (dense + sparse BM25)

### Multi-Agent System

1. **Query Analysis Agent**: Analyzes intent and expands queries
2. **Retrieval Agent**: Performs hybrid search on knowledge base
3. **Re-ranking Agent**: Re-ranks results using cross-encoder
4. **Generation Agent**: Generates answers using LLM
5. **Citation Agent**: Adds source references
6. **Web Search Agent**: Augments with external knowledge (optional)

## 📦 Installation

### Prerequisites

- Python 3.11 (required for PyTorch compatibility)
- HuggingFace API key
- Pinecone API key
- Brave Search API key (optional, for web search)

### Setup

1. **Clone the repository** (or navigate to project directory)

```bash
cd "/Users/alexander/Documents/tinker/RAG - Document uploader"
```

2. **Create virtual environment** (Python 3.11)

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
HUGGINGFACE_API_KEY=your_hf_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1-aws

# Optional
MCP_BRAVE_SEARCH_API_KEY=your_brave_api_key_here
```

## 🚀 Quick Start

### Phase 1: Foundation (✅ Complete)

- [x] Project structure created
- [x] Dependencies installed
- [x] Configuration management set up
- [x] Virtual environment configured

### Next Steps

Continue with Phase 2: Document Processing Pipeline

## 📁 Project Structure

```
RAG - Document uploader/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Centralized configuration
│   ├── agents/                # Multi-agent system
│   │   └── __init__.py
│   ├── services/              # Core services
│   │   └── __init__.py
│   ├── mcp/                   # MCP integration
│   │   └── __init__.py
│   ├── routes/                # API endpoints
│   │   └── __init__.py
│   └── models/                # Pydantic schemas
│       └── __init__.py
├── data/                      # Data storage (auto-created)
│   ├── uploads/               # Uploaded documents
│   └── conversations/         # Conversation history
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your environment variables (create this)
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

### LLM Configuration
- `HUGGINGFACE_API_KEY`: Your HuggingFace API key
- `HF_MODEL_NAME`: Model to use (default: Qwen/Qwen2.5-72B-Instruct)

### Embedding Configuration
- `EMBEDDING_MODEL`: Embedding model (default: sentence-transformers/all-MiniLM-L6-v2)

### Vector Database
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment (e.g., us-east-1-aws)
- `PINECONE_INDEX_NAME`: Index name (default: rag-documents)

### Application Settings
- `CHUNK_SIZE`: Document chunk size (default: 512)
- `CHUNK_OVERLAP`: Chunk overlap (default: 128)
- `TOP_K_RETRIEVAL`: Number of chunks to retrieve (default: 10)
- `TOP_K_RERANK`: Number of chunks after re-ranking (default: 5)

## 🧪 Testing Phase 1

Test that all packages are installed correctly:

```bash
source venv/bin/activate
python -c "import fastapi; import langchain; import langgraph; import pinecone; import sentence_transformers; print('✅ All packages imported successfully!')"
```

## 📚 Development Phases

- [x] **Phase 1**: Foundation & Configuration
- [ ] **Phase 2**: Document Processing Pipeline
- [ ] **Phase 3**: Vector Database & Embeddings
- [ ] **Phase 4**: Multi-Agent System with LangGraph
- [ ] **Phase 5**: MCP Integration
- [ ] **Phase 6**: API Endpoints & Integration
- [ ] **Phase 7**: Frontend Development
- [ ] **Phase 8**: Testing & Documentation

## 📖 Documentation

- [Implementation Plan](/.gemini/antigravity/brain/3c2f6ad4-1777-4eae-bb46-e72ba753eeb5/implementation_plan.md)
- [Backend Implementation Plan](/.gemini/antigravity/brain/3c2f6ad4-1777-4eae-bb46-e72ba753eeb5/backend_implementation_plan.md)

## 🤝 Contributing

This is a learning/development project. Contributions and suggestions are welcome!

## 📄 License

MIT License

---

**Status**: Phase 1 Complete ✅ | Ready for Phase 2: Document Processing
