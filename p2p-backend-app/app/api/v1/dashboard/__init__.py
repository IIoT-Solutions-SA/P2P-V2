"""Dashboard API endpoints."""

from fastapi import APIRouter
from .dashboard import router as dashboard_api_router

dashboard_router = APIRouter()

# Include the dashboard router
dashboard_router.include_router(dashboard_api_router)