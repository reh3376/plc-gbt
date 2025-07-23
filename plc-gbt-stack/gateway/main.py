#!/usr/bin/env python3
"""
Gateway API for PLC-GPT Stack
Provides REST API for querying the knowledge graph and vector store
"""

import os
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import n8n-MCP proxy integration
try:
    from .n8n_mcp_proxy import router as n8n_mcp_router, startup_n8n_mcp_proxy, shutdown_n8n_mcp_proxy
    N8N_MCP_AVAILABLE = True
except ImportError as e:
    N8N_MCP_AVAILABLE = False
    n8n_mcp_import_error = str(e)

# Import industrial-automation MCP proxy integration
try:
    from .industrial_automation_mcp_proxy import router as industrial_mcp_router, startup_industrial_mcp_proxy, shutdown_industrial_mcp_proxy
    INDUSTRIAL_MCP_AVAILABLE = True
except ImportError as e:
    INDUSTRIAL_MCP_AVAILABLE = False
    industrial_mcp_import_error = str(e)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger()

# Log n8n-MCP availability after logger is configured
if not N8N_MCP_AVAILABLE:
    logger.warning("n8n-MCP proxy not available", error=n8n_mcp_import_error)

# Log industrial-automation MCP availability
if not INDUSTRIAL_MCP_AVAILABLE:
    logger.warning("Industrial automation MCP proxy not available", error=industrial_mcp_import_error)

# Initialize FastAPI
app = FastAPI(
    title="PLC-GPT Gateway API",
    description="Gateway for PLC knowledge graph, vector search, n8n-MCP, and industrial automation MCP integration",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("GATEWAY_CORS_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include n8n-MCP router if available
if N8N_MCP_AVAILABLE:
    app.include_router(n8n_mcp_router)
    logger.info("n8n-MCP proxy router integrated")
else:
    logger.warning("n8n-MCP proxy not available", error=n8n_mcp_import_error)

# Include industrial automation MCP router if available
if INDUSTRIAL_MCP_AVAILABLE:
    app.include_router(industrial_mcp_router)
    logger.info("Industrial automation MCP proxy router integrated")
else:
    logger.warning("Industrial automation MCP proxy not available", error=industrial_mcp_import_error)

# Add startup and shutdown event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Gateway API starting up")
    
    if N8N_MCP_AVAILABLE:
        try:
            await startup_n8n_mcp_proxy()
            logger.info("n8n-MCP proxy initialized")
        except Exception as e:
            logger.error("Failed to initialize n8n-MCP proxy", error=str(e))
    
    if INDUSTRIAL_MCP_AVAILABLE:
        try:
            await startup_industrial_mcp_proxy()
            logger.info("Industrial automation MCP proxy initialized")
        except Exception as e:
            logger.error("Failed to initialize industrial automation MCP proxy", error=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    logger.info("Gateway API shutting down")
    
    if N8N_MCP_AVAILABLE:
        try:
            await shutdown_n8n_mcp_proxy()
            logger.info("n8n-MCP proxy cleaned up")
        except Exception as e:
            logger.error("Error during n8n-MCP proxy cleanup", error=str(e))
    
    if INDUSTRIAL_MCP_AVAILABLE:
        try:
            await shutdown_industrial_mcp_proxy()
            logger.info("Industrial automation MCP proxy cleaned up")
        except Exception as e:
            logger.error("Error during industrial automation MCP proxy cleanup", error=str(e))

# Security
security = HTTPBearer()
BEARER_TOKEN = os.getenv("GATEWAY_BEARER_TOKEN")


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify bearer token"""
    if credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    return credentials.credentials


# Request/Response models
class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to answer")
    max_results: int = Field(6, description="Maximum number of results to return")
    include_graph: bool = Field(True, description="Include graph context in response")
    include_vectors: bool = Field(True, description="Include vector context in response")


class Citation(BaseModel):
    source: str
    relevance: float
    snippet: str


class QueryResponse(BaseModel):
    question: str
    answer: Optional[str] = None
    graph_context: Optional[Dict] = None
    vector_context: Optional[List[Dict]] = None
    citations: List[Citation] = []
    processing_time_ms: float
    timestamp: datetime


# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "neo4j": "connected",  # TODO: Implement actual health checks
            "qdrant": "connected",
            "openai": "available"
        }
    }


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_knowledge(
    request: QueryRequest,
    token: str = Depends(verify_token)
):
    """
    Query the PLC knowledge graph and vector store
    """
    start_time = datetime.utcnow()
    
    logger.info("query_received", 
                question=request.question,
                max_results=request.max_results)
    
    try:
        # Import query service
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'query'))
        from query_service import QueryService
        
        # Initialize query service
        query_service = QueryService(
            neo4j_uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_user=os.environ.get("NEO4J_USER", "neo4j"),
            neo4j_password=os.environ.get("NEO4J_PASSWORD", "password"),
            qdrant_host=os.environ.get("QDRANT_HOST", "localhost"),
            qdrant_port=int(os.environ.get("QDRANT_PORT", "6333")),
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Execute query using the service
        query_result = await query_service.query(
            question=request.question,
            strategy="hybrid" if request.include_graph and request.include_vectors else (
                "graph" if request.include_graph else "vector"
            ),
            max_results=request.max_results,
            vector_threshold=0.7,
            expand_graph=True
        )
        
        # Convert query result to response format
        response = QueryResponse(
            question=request.question,
            answer=query_result.answer,
            graph_context=query_result.graph_context,
            vector_context=query_result.vector_context,
            citations=[
                Citation(
                    source=citation.get("source", "Unknown"),
                    relevance=citation.get("relevance", 0.0),
                    snippet=citation.get("snippet", "")
                ) for citation in query_result.citations
            ],
            processing_time_ms=query_result.processing_time_ms,
            timestamp=query_result.timestamp
        )
        
        query_service.close()
        
        logger.info("query_completed",
                   question=request.question,
                   processing_time_ms=response.processing_time_ms)
        
        return response
        
    except Exception as e:
        logger.error("query_error", 
                    question=request.question,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/stats")
async def get_stats(token: str = Depends(verify_token)):
    """Get system statistics"""
    return {
        "total_documents": 0,  # TODO: Implement
        "total_nodes": 0,
        "total_embeddings": 0,
        "last_update": datetime.utcnow()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 