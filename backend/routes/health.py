"""API routes for health checks and system status."""

from fastapi import APIRouter
from backend.models.schemas import HealthResponse
from backend.config import settings
from backend.mcp.client import MCPClient
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

# Initialize MCP client
mcp_client = MCPClient()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and service availability.
    """
    # Check MCP services
    mcp_health = await mcp_client.health_check()
    
    services = {
        "web_search": mcp_health['web_search']['status'],
        "embedding_model": settings.embedding_model,
        "llm_model": settings.hf_model_name if settings.huggingface_api_key else "not_configured"
    }
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        services=services,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"status": "ok", "message": "pong"}
