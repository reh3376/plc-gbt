#!/usr/bin/env python3
"""
PLC-GPT Enterprise Application
Phase 3 Days 6-7: Enterprise Features Integration

This is the main application file that integrates all enterprise components:
- JWT Authentication & RBAC
- Redis Caching & Rate Limiting
- Comprehensive Monitoring
- Enterprise API Endpoints
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import enterprise components
from config.enterprise_settings import EnterpriseSettings
from auth.jwt_manager import get_jwt_manager
from auth.rbac import get_rbac_manager
from cache.redis_cache import get_cache
from middleware.rate_limiter import get_rate_limiter
from middleware.auth_middleware import AuthenticationMiddleware
from middleware.monitoring_middleware import MonitoringMiddleware
from monitoring.enterprise_monitoring import get_monitoring
from api.enterprise_api import enterprise_router

# Setup logging early for import error handling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import N8N Workflow Engine Integration (Phase 1.3 - OpenAPI Schema MCP Compliant)
try:
    from api.workflow_engine.fastapi_router import (
        router as workflow_router,
        startup_workflow_engine,
        shutdown_workflow_engine
    )
    WORKFLOW_ENGINE_AVAILABLE = True
    logger.info("✅ N8N Workflow Engine integration available")
except ImportError as e:
    WORKFLOW_ENGINE_AVAILABLE = False
    workflow_import_error = str(e)
    logger.warning(f"⚠️ N8N Workflow Engine not available: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting PLC-GPT Enterprise Application")
    
    # Initialize enterprise components
    settings = EnterpriseSettings()
    
    try:
        # Initialize JWT Manager
        jwt_manager = get_jwt_manager()
        logger.info("✅ JWT Manager initialized")
        
        # Initialize RBAC Manager
        rbac_manager = get_rbac_manager()
        logger.info("✅ RBAC Manager initialized")
        
        # Initialize Redis Cache
        cache = get_cache()
        cache_health = cache.health_check()
        if cache_health['status'] == 'healthy':
            logger.info("✅ Redis Cache connected and healthy")
        else:
            logger.warning(f"⚠️ Redis Cache health check failed: {cache_health}")
        
        # Initialize Rate Limiter
        rate_limiter = get_rate_limiter()
        logger.info("✅ Rate Limiter initialized")
        
        # Initialize Monitoring
        monitoring = get_monitoring()
        monitoring.start_monitoring()
        logger.info("✅ Enterprise Monitoring started")
        
        # Register alert handlers
        def log_alert_handler(alert):
            logger.warning(f"ALERT: {alert.name} - {alert.message}")
        
        monitoring.register_alert_handler("log_handler", log_alert_handler)
        
        # Initialize N8N Workflow Engine (Phase 1.3 - OpenAPI Schema MCP Integration)
        if WORKFLOW_ENGINE_AVAILABLE:
            try:
                await startup_workflow_engine()
                logger.info("✅ N8N Workflow Engine initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize N8N Workflow Engine: {e}")
                # Continue without workflow engine if initialization fails
        else:
            logger.warning(f"⚠️ N8N Workflow Engine not available: {workflow_import_error}")
        
        logger.info("🚀 All enterprise components initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize enterprise components: {e}")
        raise
    
    finally:
        # Cleanup
        logger.info("Shutting down PLC-GPT Enterprise Application")
        
        try:
            monitoring = get_monitoring()
            monitoring.stop_monitoring()
            logger.info("✅ Monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
        
        # Shutdown N8N Workflow Engine
        if WORKFLOW_ENGINE_AVAILABLE:
            try:
                await shutdown_workflow_engine()
                logger.info("✅ N8N Workflow Engine shutdown completed")
            except Exception as e:
                logger.error(f"Error stopping N8N Workflow Engine: {e}")


# Create FastAPI application
app = FastAPI(
    title="PLC-GPT Enterprise",
    description="Enterprise-grade PLC data processing and analysis platform",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add enterprise middleware
app.add_middleware(MonitoringMiddleware)
app.add_middleware(AuthenticationMiddleware)

# Add rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    rate_limiter = get_rate_limiter()
    return await rate_limiter(request, call_next)


# Include enterprise router
app.include_router(enterprise_router)

# Include N8N Workflow Engine router (Phase 1.3 - OpenAPI Schema MCP Integration)
if WORKFLOW_ENGINE_AVAILABLE:
    app.include_router(workflow_router)
    logger.info("✅ N8N Workflow Engine API endpoints integrated")
else:
    logger.warning(f"⚠️ N8N Workflow Engine API not available: {workflow_import_error}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    try:
        from monitoring.enterprise_monitoring import comprehensive_health_check
        health_data = comprehensive_health_check()
        
        # Add N8N Workflow Engine health status
        if WORKFLOW_ENGINE_AVAILABLE:
            try:
                # Import here to avoid circular dependency
                from api.workflow_engine.fastapi_router import get_workflow_engine
                engine = await get_workflow_engine()
                workflow_health = await engine.get_engine_health()
                health_data['workflow_engine'] = {
                    'status': workflow_health.get('engine_status', 'unknown'),
                    'database_healthy': workflow_health.get('database_healthy', False),
                    'redis_healthy': workflow_health.get('redis_healthy', False),
                    'n8n_framework_available': workflow_health.get('n8n_framework_available', False),
                    'total_workflows': workflow_health.get('total_workflows', 0),
                    'version': workflow_health.get('version', 'unknown')
                }
            except Exception as e:
                health_data['workflow_engine'] = {
                    'status': 'error',
                    'error': str(e)
                }
        else:
            health_data['workflow_engine'] = {
                'status': 'unavailable',
                'reason': 'N8N Workflow Engine not imported'
            }
        
        # Determine overall status
        overall_status = "healthy"
        if health_data['redis']['status'] != 'healthy':
            overall_status = "degraded"
        if health_data['database']['status'] != 'healthy':
            overall_status = "unhealthy"
        if WORKFLOW_ENGINE_AVAILABLE and health_data['workflow_engine']['status'] not in ['healthy', 'degraded']:
            overall_status = "degraded"
        
        health_data['overall_status'] = overall_status
        
        return health_data
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )


# Metrics endpoint for Prometheus
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    try:
        monitoring = get_monitoring()
        metrics = monitoring.get_metrics()
        
        from fastapi.responses import Response
        return Response(
            content=metrics,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get metrics: {e}"}
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information."""
    try:
        settings = EnterpriseSettings()
        monitoring = get_monitoring()
        performance_metrics = monitoring.get_performance_metrics()
        
        # Build features list dynamically based on available components
        features = [
            "JWT Authentication",
            "Role-Based Access Control (RBAC)",
            "Redis Caching",
            "Rate Limiting",
            "Comprehensive Monitoring",
            "Enterprise APIs"
        ]
        
        # Add N8N Workflow Engine features if available
        if WORKFLOW_ENGINE_AVAILABLE:
            features.extend([
                "N8N Workflow Engine Integration",
                "Industrial Automation Workflows",
                "Real-time Workflow Execution",
                "OpenAPI Schema MCP Compliance",
                "Workflow Performance Monitoring"
            ])
        
        return {
            "application": "PLC-GPT Enterprise",
            "version": "3.0.0",
            "status": "operational",
            "features": features,
            "environment": settings.ENVIRONMENT,
            "performance": {
                "cpu_usage": f"{performance_metrics['cpu_usage_percent']:.1f}%",
                "memory_usage": f"{performance_metrics['memory_usage_percent']:.1f}%",
                "cache_hit_rate": f"{performance_metrics['cache_hit_rate']:.1f}%"
            },
            "documentation": "/docs",
            "health_check": "/health",
            "metrics": "/metrics",
            "workflow_engine_status": "/api/v1/workflows/engine/health" if WORKFLOW_ENGINE_AVAILABLE else None
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "application": "PLC-GPT Enterprise",
                "status": "error",
                "error": str(e)
            }
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    monitoring = get_monitoring()
    monitoring.record_error("not_found", "api")
    
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource '{request.url.path}' was not found",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    monitoring = get_monitoring()
    monitoring.record_error("internal_server_error", "api")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "status_code": 500
        }
    )


# Startup message
@app.on_event("startup")
async def startup_message():
    """Display startup message."""
    # Build dynamic startup message based on available components
    workflow_status = "✅ OPERATIONAL" if WORKFLOW_ENGINE_AVAILABLE else "⚠️  NOT AVAILABLE"
    workflow_docs = "║  🔧 Workflow API:  http://localhost:8000/api/v1/workflows/engine/health     ║" if WORKFLOW_ENGINE_AVAILABLE else "║  🔧 Workflow API:  Not Available (Import Error)                           ║"
    
    logger.info(f"""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                           PLC-GPT Enterprise v3.0.0                         ║
    ║              Phase 1.3: N8N Workflow Engine Integration Complete            ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║  🔐 JWT Authentication & Authorization                                       ║
    ║  👥 Role-Based Access Control (RBAC)                                        ║
    ║  🚀 Redis Caching & Performance Optimization                                ║
    ║  🛡️  Rate Limiting & DDoS Protection                                        ║
    ║  📊 Comprehensive Monitoring & Observability                                ║
    ║  🌐 Enterprise-grade API Endpoints                                          ║
    ║  🔄 N8N Workflow Engine Integration: {workflow_status}                      ║
    ║  🏭 Industrial Automation Workflows                                         ║
    ║  📋 OpenAPI Schema MCP Compliance                                           ║
    ╠══════════════════════════════════════════════════════════════════════════════╣
    ║  📚 Documentation: http://localhost:8000/docs                               ║
    ║  🏥 Health Check:  http://localhost:8000/health                             ║
    ║  📈 Metrics:       http://localhost:8000/metrics                            ║
    {workflow_docs}
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    settings = EnterpriseSettings()
    
    # Run the application
    uvicorn.run(
        "enterprise_app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
        access_log=True
    ) 