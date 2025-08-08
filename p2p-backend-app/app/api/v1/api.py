"""Main API router that combines all endpoint routers."""

from datetime import datetime
from fastapi import APIRouter

# Auth router for organization-based signup and session management
from app.api.v1.auth import auth_router
from app.api.v1.users import users_router
from app.api.v1.organizations import organizations_router
from app.api.v1.forum import forum_router
from app.api.v1.use_cases import router as use_cases_router
from app.api.v1.messaging import messaging_router
from app.api.v1.notifications import notifications_router
from app.api.v1.dashboard import dashboard_router
from app.api.v1.files import router as files_router
from app.api.v1.media import router as media_router
from app.api.v1.invitations import router as invitations_router
# from app.api.v1.test_auth import router as test_auth_router
# from app.api.v1.test_rbac import router as test_rbac_router
# from app.api.v1.password_reset import router as password_reset_router
# from app.api.v1.email_verification import router as email_verification_router
# from app.api.v1.test_email_verification import router as test_email_verification_router
# from app.api.v1.test_auth_suite import router as test_auth_suite_router
from app.core.config import settings
from app.db.session import check_postgres_health, check_mongodb_health
from app.schemas.health import HealthCheckResponse

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(files_router, prefix="/files", tags=["files"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
api_router.include_router(invitations_router, prefix="/invitations", tags=["invitations"])
api_router.include_router(forum_router, prefix="/forum", tags=["forum"])
api_router.include_router(use_cases_router, prefix="/use-cases", tags=["use-cases"])
api_router.include_router(messaging_router, prefix="/messaging", tags=["messaging"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(dashboard_router, tags=["dashboard"])
# api_router.include_router(test_auth_router, prefix="/test-auth", tags=["testing"])
# api_router.include_router(test_rbac_router, prefix="/test-rbac", tags=["rbac-testing"])
# api_router.include_router(password_reset_router, prefix="/password-reset", tags=["password-reset"])
# api_router.include_router(email_verification_router, prefix="/email-verification", tags=["email-verification"])
# api_router.include_router(test_email_verification_router, prefix="/test-email-verification", tags=["email-verification-testing"])
# api_router.include_router(test_auth_suite_router, prefix="/test-auth-suite", tags=["auth-suite-testing"])


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