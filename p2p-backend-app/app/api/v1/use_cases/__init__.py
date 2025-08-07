"""Use Cases API endpoints."""

from fastapi import APIRouter
from .use_cases import router as use_cases_router
from .media import router as media_router

# Create main router and include sub-routers
router = APIRouter()
router.include_router(use_cases_router)
router.include_router(media_router)

__all__ = ["router"]