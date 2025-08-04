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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    print("Starting up P2P Sandbox Backend...")
    # TODO: Initialize database connections
    # TODO: Initialize Redis connection
    # TODO: Initialize MongoDB connection
    yield
    # Shutdown
    print("Shutting down P2P Sandbox Backend...")
    # TODO: Close database connections
    # TODO: Close Redis connection
    # TODO: Close MongoDB connection


# Create FastAPI instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for P2P Sandbox platform - Empowering Saudi industrial SMEs through peer collaboration",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Add server error middleware
app.add_middleware(ServerErrorMiddleware, handler=general_exception_handler)

# Configure CORS
# Parse CORS origins - ensure we have defaults for development
cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
if not cors_origins and settings.ENVIRONMENT == "development":
    cors_origins = ["http://localhost:5173", "http://localhost:3000"]

print(f"CORS Origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "version": "0.1.0",
        "status": "Container setup complete! 🎉"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "p2p-backend",
        "checks": {
            "api": "operational",
            # We'll add database checks later
        }
    }


# This allows us to run the app directly with python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)