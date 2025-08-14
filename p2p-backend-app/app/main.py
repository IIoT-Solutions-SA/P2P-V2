from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from supertokens_python.framework.fastapi import get_middleware
# from supertokens_python.recipe import emailpassword  # Imported in custom endpoints
# from supertokens_python.recipe import session  # Imported in custom endpoints
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.database import db_manager
from app.core.supertokens import init_supertokens

# Setup logging
logger = setup_logging()

# Initialize SuperTokens 
init_supertokens()
logger.info("SuperTokens initialized")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME}")
    
    # Initialize databases
    await db_manager.init_postgres()
    await db_manager.init_mongodb()
    logger.info("Database connections initialized")
    
    yield
    # Shutdown
    logger.info("Shutting down")
    await db_manager.close_connections()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# DEBUG: Request logging middleware removed

# SuperTokens middleware (MUST BE FIRST - handles auth endpoints)
app.add_middleware(get_middleware())

# CORS middleware (AFTER SuperTokens - adds headers to all responses)
if settings.BACKEND_CORS_ORIGINS:
    from supertokens_python import get_all_cors_headers
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,  # Use settings instead of hardcoded
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"] + get_all_cors_headers(),
    )

# Include routers  
app.include_router(api_router, prefix=settings.API_V1_STR)

# Removed catch-all route to test if it interferes with SuperTokens middleware
# SuperTokens middleware should handle /auth/* routes automatically

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "environment": "development"
    }

# DEBUG: Catch-all OPTIONS handler removed