"""Users API endpoints."""

from fastapi import APIRouter

users_router = APIRouter()


@users_router.get("/me")
async def get_current_user():
    """Get current user - to be implemented."""
    return {"message": "Current user endpoint - Phase 3"}


@users_router.get("/{user_id}")
async def get_user(user_id: str):
    """Get user by ID - to be implemented."""
    return {"message": f"User {user_id} endpoint - Phase 3"}


@users_router.put("/{user_id}")
async def update_user(user_id: str):
    """Update user - to be implemented."""
    return {"message": f"Update user {user_id} endpoint - Phase 3"}