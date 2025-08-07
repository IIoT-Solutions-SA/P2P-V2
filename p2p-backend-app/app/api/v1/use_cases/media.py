"""Media upload endpoints for Use Cases."""

from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.rbac import get_current_user as get_current_active_user
from app.db.mongodb import get_mongodb
from app.models.user import User
from app.services.storage import get_storage, StorageInterface
from app.services.media import get_media_service
from app.schemas.use_case import MediaUpload

router = APIRouter()


@router.post("/{use_case_id}/media", response_model=MediaUpload, status_code=status.HTTP_201_CREATED)
async def upload_media(
    use_case_id: str,
    file: UploadFile = File(..., description="Media file to upload"),
    caption: Optional[str] = Form(None, description="Optional caption for the media"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    storage: StorageInterface = Depends(get_storage),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload media (image, document, or video) for a use case.
    
    **Supported file types:**
    - Images: JPEG, PNG, GIF, WebP (max 10MB)
    - Documents: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX (max 50MB)
    - Videos: MP4, MPEG, MOV, AVI (max 500MB)
    
    **Features:**
    - Automatic image resizing and thumbnail generation
    - File type validation and security scanning
    - Organized storage by organization and use case
    - Metadata tracking and logging
    
    **Returns:**
    - media_id: Unique identifier for the uploaded media
    - url: URL to access the original file
    - thumbnail_url: URL to access thumbnail (images only)
    - type: Media type (image/document/video)
    - size: File size in bytes
    - filename: Original filename
    """
    # Verify use case exists and user has permission
    use_case = await db.use_cases.find_one({
        'id': use_case_id,
        'organization_id': str(current_user.organization_id)
    })
    
    if not use_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found"
        )
    
    # Check if user is owner or admin
    if (str(current_user.id) != use_case['published_by']['user_id'] and 
        current_user.role != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to upload media to this use case"
        )
    
    # Upload media
    media_service = get_media_service(storage, db)
    
    try:
        media_upload = await media_service.upload_media(
            file=file,
            entity_type='use-case',
            entity_id=use_case_id,
            organization_id=str(current_user.organization_id),
            caption=caption
        )
        
        return media_upload
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload media: {str(e)}"
        )


@router.delete("/{use_case_id}/media/{media_id}")
async def delete_media(
    use_case_id: str,
    media_id: str,
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    storage: StorageInterface = Depends(get_storage),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a media file from a use case.
    
    **Permissions:**
    - Only the use case owner or an admin can delete media
    
    **Actions:**
    - Removes the file from storage
    - Removes thumbnail if it exists
    - Updates the use case media array
    - Logs the deletion operation
    """
    # Verify use case exists and user has permission
    use_case = await db.use_cases.find_one({
        'id': use_case_id,
        'organization_id': str(current_user.organization_id)
    })
    
    if not use_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found"
        )
    
    # Check if user is owner or admin
    if (str(current_user.id) != use_case['published_by']['user_id'] and 
        current_user.role != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete media from this use case"
        )
    
    # Delete media
    media_service = get_media_service(storage, db)
    
    success = await media_service.delete_media(
        media_id=media_id,
        entity_type='use-case',
        entity_id=use_case_id,
        user_id=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    return {
        "message": "Media deleted successfully",
        "media_id": media_id
    }


@router.patch("/{use_case_id}/media/{media_id}")
async def update_media_caption(
    use_case_id: str,
    media_id: str,
    caption: str = Form(..., description="New caption for the media"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the caption of a media file.
    
    **Permissions:**
    - Only the use case owner or an admin can update media
    """
    # Verify use case exists and user has permission
    use_case = await db.use_cases.find_one({
        'id': use_case_id,
        'organization_id': str(current_user.organization_id)
    })
    
    if not use_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found"
        )
    
    # Check if user is owner or admin
    if (str(current_user.id) != use_case['published_by']['user_id'] and 
        current_user.role != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update media in this use case"
        )
    
    # Update media caption
    result = await db.use_cases.update_one(
        {
            'id': use_case_id,
            'media.id': media_id
        },
        {
            '$set': {
                'media.$.caption': caption
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    return {
        "message": "Media caption updated successfully",
        "media_id": media_id,
        "caption": caption
    }


@router.patch("/{use_case_id}/media/{media_id}/order")
async def reorder_media(
    use_case_id: str,
    media_id: str,
    new_order: int = Form(..., description="New order position (0-based)"),
    db: AsyncIOMotorDatabase = Depends(get_mongodb),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reorder media within a use case.
    
    **Permissions:**
    - Only the use case owner or an admin can reorder media
    
    **Parameters:**
    - new_order: 0-based index for the new position
    """
    # Verify use case exists and user has permission
    use_case = await db.use_cases.find_one({
        'id': use_case_id,
        'organization_id': str(current_user.organization_id)
    })
    
    if not use_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Use case not found"
        )
    
    # Check if user is owner or admin
    if (str(current_user.id) != use_case['published_by']['user_id'] and 
        current_user.role != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reorder media in this use case"
        )
    
    # Validate new_order
    media_list = use_case.get('media', [])
    if new_order < 0 or new_order >= len(media_list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order position"
        )
    
    # Find current position
    current_order = None
    for i, media in enumerate(media_list):
        if media['id'] == media_id:
            current_order = i
            break
    
    if current_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Reorder media array
    media_item = media_list.pop(current_order)
    media_list.insert(new_order, media_item)
    
    # Update order values
    for i, media in enumerate(media_list):
        media['order'] = i
    
    # Update use case
    await db.use_cases.update_one(
        {'id': use_case_id},
        {'$set': {'media': media_list}}
    )
    
    return {
        "message": "Media reordered successfully",
        "media_id": media_id,
        "old_order": current_order,
        "new_order": new_order
    }