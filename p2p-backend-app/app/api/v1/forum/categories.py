"""Forum category endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_current_user as get_current_active_user, get_current_admin_user as require_admin
from app.core.rbac import require_organization_access
from app.db.session import get_db
from app.models.user import User
from app.services.forum import ForumService
from app.schemas.forum import (
    ForumCategoryResponse,
    ForumCategoryCreate,
    ForumCategoryUpdate
)

router = APIRouter()


@router.get("/", response_model=List[ForumCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all active forum categories.
    
    Categories are returned sorted by sort_order and then by name.
    Only active categories are included in the response.
    """
    # Ensure user has access to their organization's forum
    await require_organization_access(db, current_user, current_user.organization_id)
    
    return await ForumService.get_categories(db)


@router.post("/", response_model=ForumCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_data: ForumCategoryCreate,
    current_user: User = Depends(require_admin)
):
    """
    Create a new forum category (admin only).
    
    **Required Fields:**
    - `name`: Category name (1-100 characters)
    - `category_type`: Category type from predefined list
    
    **Optional Fields:**
    - `description`: Category description (max 500 characters)
    - `color_class`: CSS color class for UI styling
    - `is_active`: Whether category is active (default: true)
    - `sort_order`: Display order (default: 0)
    """
    return await ForumService.create_category(
        db,
        category_data=category_data,
        creator_id=current_user.id
    )