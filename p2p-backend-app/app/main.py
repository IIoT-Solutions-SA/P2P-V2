"""
P2P Sandbox Backend API
FastAPI application with async support for industrial SME collaboration platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.errors import ServerErrorMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app.db.session import init_db, close_db, check_postgres_health, check_mongodb_health
from app.schemas.health import HealthCheckResponse
from app.core.logging import setup_logging, get_logger
from app.middleware.logging import LoggingMiddleware, UserContextMiddleware
# Temporarily disable SuperTokens due to version compatibility
# from app.core.supertokens import init_supertokens, get_supertokens_middleware
# from supertokens_python import get_all_cors_headers
from datetime import datetime

# Configure structured logging
setup_logging()
logger = get_logger(__name__)

# Temporarily disable SuperTokens initialization
# init_supertokens()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting up P2P Sandbox Backend...")
    try:
        await init_db()
        logger.info("Database connections initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down P2P Sandbox Backend...")
    await close_db()
    logger.info("Database connections closed successfully")


# Create FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for P2P Sandbox platform - Empowering Saudi industrial SMEs through peer collaboration",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Add logging middleware (should be first to catch all requests)
app.add_middleware(LoggingMiddleware, service_name=settings.PROJECT_NAME)
app.add_middleware(UserContextMiddleware)

# Temporarily disable SuperTokens middleware
# app.add_middleware(get_supertokens_middleware())

# Add server error middleware
app.add_middleware(ServerErrorMiddleware, handler=general_exception_handler)

# Configure CORS
# Get CORS origins from settings
cors_origins = settings.cors_origins
if not cors_origins and settings.DEBUG:
    cors_origins = ["http://localhost:5173", "http://localhost:3000"]

logger.info(f"CORS Origins configured: {cors_origins}")

# Temporarily disable SuperTokens CORS headers
# supertokens_cors_headers = get_all_cors_headers()
supertokens_cors_headers = []  # Empty list for now

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization"] + supertokens_cors_headers,
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include API router  
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to P2P Sandbox API",
        "version": settings.VERSION,
        "status": "Container setup complete! 🎉"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint with database status"""
    # Record check timestamp
    check_timestamp = datetime.utcnow()
    
    # Run health checks in parallel
    postgres_health = await check_postgres_health()
    mongodb_health = await check_mongodb_health()
    
    # Determine overall status
    all_healthy = (
        postgres_health["status"] == "healthy" and 
        mongodb_health["status"] == "healthy"
    )
    
    return HealthCheckResponse(
        status="healthy" if all_healthy else "degraded",
        service="p2p-backend",
        timestamp=check_timestamp.isoformat() + "Z",
        version=settings.VERSION,
        checks={
            "api": {
                "status": "healthy",
                "response_time_ms": 1
            },
            "postgresql": postgres_health,
            "mongodb": mongodb_health,
        }
    )


# This allows us to run the app directly with python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)