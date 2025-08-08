"""Background tasks API endpoints."""

from fastapi import APIRouter
from .background_tasks import router as tasks_api_router

tasks_router = APIRouter()

# Include the tasks router
tasks_router.include_router(tasks_api_router)