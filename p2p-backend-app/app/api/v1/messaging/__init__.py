"""Messaging API endpoints."""

from fastapi import APIRouter
from .messages import router as messages_router

messaging_router = APIRouter()

# Include the messages router
messaging_router.include_router(messages_router)