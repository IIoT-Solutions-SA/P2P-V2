"""Main API router that combines all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.auth import auth_router
from app.api.v1.users import users_router
from app.api.v1.organizations import organizations_router
from app.api.v1.forum import forum_router
from app.api.v1.use_cases import use_cases_router
from app.api.v1.messaging import messaging_router
from app.db.session import check_postgres_health, check_mongodb_health

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(forum_router, prefix="/forum", tags=["forum"])
api_router.include_router(use_cases_router, prefix="/use-cases", tags=["use-cases"])
api_router.include_router(messaging_router, prefix="/messaging", tags=["messaging"])


@api_router.get("/health")
async def health_check():
    """API health check endpoint with database status."""
    # Run health checks in parallel
    postgres_health = await check_postgres_health()
    mongodb_health = await check_mongodb_health()
    
    # Determine overall status
    all_healthy = (
        postgres_health["status"] == "healthy" and 
        mongodb_health["status"] == "healthy"
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": "p2p-backend-api-v1",
        "checks": {
            "api": "operational",
            "postgresql": postgres_health,
            "mongodb": mongodb_health,
        }
    }