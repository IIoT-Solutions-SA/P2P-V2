"""Messaging API endpoints."""

from fastapi import APIRouter

messaging_router = APIRouter()


@messaging_router.get("/conversations")
async def list_conversations():
    """List conversations - to be implemented."""
    return {"message": "List conversations endpoint - Phase 6"}


@messaging_router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    """Get conversation by ID - to be implemented."""
    return {"message": f"Conversation {conv_id} endpoint - Phase 6"}


@messaging_router.post("/messages")
async def send_message():
    """Send message - to be implemented."""
    return {"message": "Send message endpoint - Phase 6"}