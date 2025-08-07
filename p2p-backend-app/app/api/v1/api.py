from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    supertokens_auth, # <-- Re-add this import
    dashboard,
    forum,
    usecases
)

api_router = APIRouter()

# --- Re-add the router for your custom endpoints ---
api_router.include_router(supertokens_auth.router, prefix="/auth", tags=["Custom SuperTokens Auth"])

# --- Include your other existing routers ---
api_router.include_router(auth.router, prefix="/auth", tags=["User Profile"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(forum.router, prefix="/forum", tags=["Forum"])
api_router.include_router(usecases.router, prefix="/use-cases", tags=["Use Cases"])
