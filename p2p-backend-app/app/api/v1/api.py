"""Main API router that combines all endpoint routers."""

from datetime import datetime
from fastapi import APIRouter

from app.api.v1.auth import auth_router
from app.api.v1.users import users_router
from app.api.v1.organizations import organizations_router
from app.api.v1.forum import forum_router
from app.api.v1.use_cases import use_cases_router
from app.api.v1.messaging import messaging_router
from app.api.v1.test_auth import router as test_auth_router
from app.api.v1.test_rbac import router as test_rbac_router
from app.api.v1.password_reset import router as password_reset_router
from app.core.config import settings
from app.db.session import check_postgres_health, check_mongodb_health
from app.schemas.health import HealthCheckResponse

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(forum_router, prefix="/forum", tags=["forum"])
api_router.include_router(use_cases_router, prefix="/use-cases", tags=["use-cases"])
api_router.include_router(messaging_router, prefix="/messaging", tags=["messaging"])
api_router.include_router(test_auth_router, prefix="/test-auth", tags=["testing"])
api_router.include_router(test_rbac_router, prefix="/test-rbac", tags=["rbac-testing"])
api_router.include_router(password_reset_router, prefix="/password-reset", tags=["password-reset"])


@api_router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """API health check endpoint with database status."""
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
        service="p2p-backend-api-v1",
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