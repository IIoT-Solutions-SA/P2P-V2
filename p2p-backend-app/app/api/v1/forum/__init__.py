"""Forum API endpoints."""

from fastapi import APIRouter

forum_router = APIRouter()


@forum_router.get("/topics")
async def list_topics():
    """List forum topics - to be implemented."""
    return {"message": "List topics endpoint - Phase 4"}


@forum_router.get("/topics/{topic_id}")
async def get_topic(topic_id: str):
    """Get topic by ID - to be implemented."""
    return {"message": f"Topic {topic_id} endpoint - Phase 4"}


@forum_router.post("/topics")
async def create_topic():
    """Create forum topic - to be implemented."""
    return {"message": "Create topic endpoint - Phase 4"}