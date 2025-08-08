"""Messaging API endpoints."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.rbac import get_current_user as get_current_active_user
from app.models.user import User
from app.models.message import (
    MessageCreate, MessageUpdate, MessageResponse,
    ConversationCreate, ConversationResponse,
    ConversationListResponse, MessageListResponse,
    UnreadCountResponse, MessageSearchRequest
)
from app.services.messaging import MessagingService
from app.core.exceptions import NotFoundException, ForbiddenException

router = APIRouter(prefix="/messages", tags=["messaging"])


@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a new message to another user."""
    try:
        message = await MessagingService.send_message(
            db=db,
            sender_id=current_user.id,
            message_data=message_data,
            organization_id=current_user.organization_id
        )
        return message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    archived: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's conversations."""
    return await MessagingService.get_conversations(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        page=page,
        page_size=page_size,
        archived=archived
    )


@router.get("/conversations/{conversation_id}", response_model=MessageListResponse)
async def get_messages(
    conversation_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages in a conversation."""
    try:
        return await MessagingService.get_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            page=page,
            page_size=page_size
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.patch("/{message_id}/read", response_model=MessageResponse)
async def mark_message_as_read(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a message as read."""
    try:
        return await MessagingService.mark_as_read(
            db=db,
            message_id=message_id,
            user_id=current_user.id
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put("/{message_id}", response_model=MessageResponse)
async def edit_message(
    message_id: UUID,
    update_data: MessageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Edit a message."""
    try:
        return await MessagingService.edit_message(
            db=db,
            message_id=message_id,
            user_id=current_user.id,
            update_data=update_data
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/{message_id}")
async def delete_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a message."""
    try:
        return await MessagingService.delete_message(
            db=db,
            message_id=message_id,
            user_id=current_user.id
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/unread/count", response_model=UnreadCountResponse)
async def get_unread_counts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get unread message counts."""
    return await MessagingService.get_unread_counts(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id
    )


@router.post("/search", response_model=List[MessageResponse])
async def search_messages(
    search_params: MessageSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search messages."""
    return await MessagingService.search_messages(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        search_params=search_params
    )


@router.post("/{message_id}/reactions")
async def add_reaction(
    message_id: UUID,
    reaction: str = Query(..., min_length=1, max_length=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add or remove a reaction to a message."""
    try:
        return await MessagingService.add_reaction(
            db=db,
            message_id=message_id,
            user_id=current_user.id,
            reaction=reaction
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/conversations/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: UUID,
    archive: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Archive or unarchive a conversation."""
    try:
        return await MessagingService.archive_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            archive=archive
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post("/conversations/{conversation_id}/mark-all-read")
async def mark_all_as_read(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark all messages in a conversation as read."""
    try:
        # Get all messages to mark them as read
        await MessagingService.get_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=current_user.id,
            page=1,
            page_size=1000  # Get all messages
        )
        return {"message": "All messages marked as read"}
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )