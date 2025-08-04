"""Authentication API endpoints."""

from fastapi import APIRouter

auth_router = APIRouter()


@auth_router.post("/login")
async def login():
    """Login endpoint - to be implemented."""
    return {"message": "Login endpoint - Phase 2"}


@auth_router.post("/logout")
async def logout():
    """Logout endpoint - to be implemented."""
    return {"message": "Logout endpoint - Phase 2"}


@auth_router.post("/register")
async def register():
    """Register endpoint - to be implemented."""
    return {"message": "Register endpoint - Phase 2"}