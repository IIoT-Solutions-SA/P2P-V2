"""File upload and management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
from pathlib import Path

from app.db.session import get_db
# Temporarily disable RBAC due to SuperTokens compatibility
# from app.core.rbac import (
#     get_current_user,
#     get_current_admin_user,
#     require_admin
# )
from app.models.user import User
from app.models.file import (
    FileUploadResponse,
    FileInfoResponse,
    FileListResponse,
    FileUploadRequest
)
from app.services.file_storage import file_storage_service
from app.crud.file import file_crud
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# Temporary mock dependencies for testing file upload without auth
async def get_mock_user():
    """Mock user for testing file upload"""
    # This is temporary until we fix SuperTokens compatibility
    from uuid import uuid4
    from app.models.user import User
    from app.models.enums import UserRole
    
    # Create a mock user for testing (with null foreign keys to avoid DB constraints)
    mock_user = User(
        id=uuid4(),
        email="test@example.com", 
        first_name="Test",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
        organization_id=None  # Null to avoid foreign key constraint
    )
    return mock_user


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=201,
    summary="Upload a file",
    description="Upload a file to the system with automatic validation and storage"
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    category: str = Form(default="general", description="File category (profile_pictures, documents, etc.)"),
    is_public: bool = Form(default=False, description="Whether file should be publicly accessible"),
    current_user: User = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to the system.
    
    The file will be validated for security, stored in the configured storage backend,
    and a metadata record will be created in the database.
    
    **Categories:**
    - `profile_pictures`: User profile pictures
    - `organization_logos`: Organization logos
    - `documents`: General documents (PDF, DOC, etc.)
    - `forum_attachments`: Files attached to forum posts
    - `use_case_media`: Media for use case submissions
    - `general`: General file uploads
    
    **File Restrictions:**
    - Images: JPG, PNG, GIF, WebP (max 10MB)
    - Documents: PDF, DOC, DOCX, TXT (max 50MB)
    - Archives: ZIP, TAR, GZ (max 100MB)
    - Default max size: 25MB
    """
    try:
        # Upload file using storage service
        file_info = await file_storage_service.upload_file(
            file=file,
            category=category,
            user_id=current_user.id
        )
        
        # Create database record (temporarily using None for foreign keys)
        file_record = await file_crud.create_file_record(
            db,
            file_info=file_info,
            user_id=None,  # Temporarily None to avoid FK constraint in testing
            organization_id=None  # Temporarily None to avoid FK constraint in testing
        )
        file_record.is_public = is_public
        await db.commit()
        await db.refresh(file_record)
        
        # Return response
        return FileUploadResponse(
            file_id=file_record.file_id,
            original_filename=file_record.original_filename,
            content_type=file_record.content_type,
            file_size=file_record.file_size,
            category=file_record.category,
            file_url=file_storage_service.get_file_url(file_record.storage_path),
            uploaded_at=file_record.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")


@router.get(
    "/{file_path:path}",
    summary="Download a file",
    description="Download a file by its storage path"
)
async def download_file(
    file_path: str,
    current_user: Optional[User] = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a file from storage.
    
    Files are served directly from the storage backend. Access control is enforced
    based on the file's public setting and user permissions.
    """
    # For local storage, we need to extract file_id from path
    # Path format: category/YYYY/MM/file_id
    try:
        file_id = Path(file_path).name
        file_record = await file_crud.get_by_file_id(db, file_id)
    except:
        file_record = None
    
    if not file_record or not file_record.is_active:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check access permissions
    if not file_record.is_public:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Allow access if user owns the file or is admin or in same organization
        if (current_user.id != file_record.user_id and 
            not current_user.is_admin and
            current_user.organization_id != file_record.organization_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists in storage
    if not file_storage_service.file_exists(file_path):
        logger.warning(f"File not found in storage: {file_path}")
        raise HTTPException(status_code=404, detail="File not found in storage")
    
    # For local storage, serve file directly
    if file_storage_service.storage_type == "local":
        full_path = Path(file_storage_service.storage.base_path) / file_path
        
        return FileResponse(
            path=full_path,
            filename=file_record.original_filename,
            media_type=file_record.content_type
        )
    
    # TODO: For S3/cloud storage, generate and redirect to presigned URL
    raise HTTPException(status_code=501, detail="Cloud storage download not yet implemented")


@router.get(
    "/info/{file_id}",
    response_model=FileInfoResponse,
    summary="Get file information",
    description="Get detailed information about a file"
)
async def get_file_info(
    file_id: str,
    current_user: User = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed information about a file."""
    file_record = await file_crud.get_by_file_id(db, file_id)
    if not file_record or not file_record.is_active:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check access permissions
    if not file_record.is_public:
        if (current_user.id != file_record.user_id and 
            not current_user.is_admin and
            current_user.organization_id != file_record.organization_id):
            raise HTTPException(status_code=403, detail="Access denied")
    
    return FileInfoResponse(
        file_id=file_record.file_id,
        original_filename=file_record.original_filename,
        content_type=file_record.content_type,
        file_size=file_record.file_size,
        category=file_record.category,
        file_url=file_storage_service.get_file_url(file_record.storage_path),
        storage_type=file_record.storage_type,
        is_public=file_record.is_public,
        uploaded_at=file_record.created_at,
        user_id=file_record.user_id,
        organization_id=file_record.organization_id
    )


@router.delete(
    "/{file_id}",
    summary="Delete a file",
    description="Delete a file from storage and database"
)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file from the system.
    
    Users can delete their own files. Admins can delete any file in their organization.
    """
    file_record = await file_crud.get_by_file_id(db, file_id)
    if not file_record or not file_record.is_active:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    if (current_user.id != file_record.user_id and 
        not current_user.is_admin):
        raise HTTPException(status_code=403, detail="Cannot delete this file")
    
    # Admins can only delete files within their organization
    if (current_user.is_admin and 
        current_user.organization_id != file_record.organization_id):
        raise HTTPException(status_code=403, detail="Cannot delete file from other organization")
    
    try:
        # Delete from storage
        await file_storage_service.delete_file(
            file_record.storage_path,
            user_id=current_user.id
        )
        
        # Soft delete from database
        await file_crud.soft_delete_file(db, file_id, current_user.id)
        
        return {"message": "File deleted successfully", "file_id": file_id}
        
    except Exception as e:
        logger.error(f"File deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File deletion failed")


@router.patch(
    "/{file_id}/access",
    response_model=FileInfoResponse,
    summary="Update file access",
    description="Update file public access setting"
)
async def update_file_access(
    file_id: str,
    is_public: bool,
    current_user: User = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """Update file access permissions.
    
    Users can update access for their own files. Admins can update access for any file
    in their organization.
    """
    file_record = await file_crud.get_by_file_id(db, file_id)
    if not file_record or not file_record.is_active:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    if (current_user.id != file_record.user_id and 
        not current_user.is_admin):
        raise HTTPException(status_code=403, detail="Cannot modify this file")
    
    # Admins can only modify files within their organization
    if (current_user.is_admin and 
        current_user.organization_id != file_record.organization_id):
        raise HTTPException(status_code=403, detail="Cannot modify file from other organization")
    
    # Update access
    updated_record = await file_crud.update_file_access(
        db, file_id, is_public, current_user.id
    )
    
    if not updated_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileInfoResponse(
        file_id=updated_record.file_id,
        original_filename=updated_record.original_filename,
        content_type=updated_record.content_type,
        file_size=updated_record.file_size,
        category=updated_record.category,
        file_url=file_storage_service.get_file_url(updated_record.storage_path),
        storage_type=updated_record.storage_type,
        is_public=updated_record.is_public,
        uploaded_at=updated_record.created_at,
        user_id=updated_record.user_id,
        organization_id=updated_record.organization_id
    )


@router.get(
    "/",
    response_model=FileListResponse,
    summary="List files",
    description="List files with optional filtering"
)
async def list_files(
    category: Optional[str] = Query(None, description="Filter by category"),
    user_id: Optional[str] = Query(None, description="Filter by user (admin only)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """List files with optional filtering.
    
    Regular users see their own files. Admins can see all files in their organization
    or filter by specific user.
    """
    skip = (page - 1) * page_size
    
    # Determine which files to show
    if user_id and current_user.is_admin:
        # Admin viewing specific user's files
        files = await file_crud.get_user_files(
            db, user_id, category=category, skip=skip, limit=page_size
        )
        total = await file_crud.count_user_files(db, user_id, category=category)
    elif current_user.is_admin:
        # Admin viewing organization files
        files = await file_crud.get_organization_files(
            db, current_user.organization_id, category=category, skip=skip, limit=page_size
        )
        total = await file_crud.count_organization_files(
            db, current_user.organization_id, category=category
        )
    else:
        # Regular user viewing their own files
        files = await file_crud.get_user_files(
            db, current_user.id, category=category, skip=skip, limit=page_size
        )
        total = await file_crud.count_user_files(db, current_user.id, category=category)
    
    # Convert to response format
    file_responses = [
        FileInfoResponse(
            file_id=file.file_id,
            original_filename=file.original_filename,
            content_type=file.content_type,
            file_size=file.file_size,
            category=file.category,
            file_url=file_storage_service.get_file_url(file.storage_path),
            storage_type=file.storage_type,
            is_public=file.is_public,
            uploaded_at=file.created_at,
            user_id=file.user_id,
            organization_id=file.organization_id
        )
        for file in files
    ]
    
    total_pages = (total + page_size - 1) // page_size
    
    return FileListResponse(
        files=file_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/stats/storage",
    summary="Get storage statistics",
    description="Get file storage usage statistics"
)
async def get_storage_stats(
    current_user: User = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db)
):
    """Get storage usage statistics.
    
    Regular users see their own usage. Admins see organization-wide usage.
    """
    if current_user.is_admin:
        # Admin sees organization stats
        stats = await file_crud.get_file_storage_stats(db, current_user.organization_id)
    else:
        # Regular user sees personal stats
        user_files = await file_crud.get_user_files(db, current_user.id, limit=1000)
        total_size = sum(file.file_size for file in user_files)
        
        # Group by category
        category_stats = {}
        for file in user_files:
            if file.category not in category_stats:
                category_stats[file.category] = {'count': 0, 'size': 0}
            category_stats[file.category]['count'] += 1
            category_stats[file.category]['size'] += file.file_size
        
        stats = {
            'total_files': len(user_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_category': [
                {
                    'category': category,
                    'file_count': data['count'],
                    'size_bytes': data['size'],
                    'size_mb': round(data['size'] / (1024 * 1024), 2)
                }
                for category, data in category_stats.items()
            ]
        }
    
    return stats