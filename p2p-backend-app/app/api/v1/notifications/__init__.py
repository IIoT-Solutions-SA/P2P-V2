"""Notifications API endpoints."""

from fastapi import APIRouter
from .notifications import router as notifications_api_router

notifications_router = APIRouter()

# Include the notifications router
notifications_router.include_router(notifications_api_router)