from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, dashboard, forum

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(forum.router, prefix="/forum", tags=["forum"])
# Removed custom supertokens_auth router - using standard SuperTokens middleware