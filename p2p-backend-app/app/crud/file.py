"""CRUD operations for file metadata management."""

from typing import Optional, List, Dict, Any
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlmodel import SQLModel

from app.crud.base import CRUDBase
from app.models.file import FileMetadata
from app.core.logging import get_logger

logger = get_logger(__name__)


class CRUDFile(CRUDBase[FileMetadata, dict, dict]):
    """CRUD operations for file metadata."""
    
    async def create_file_record(
        self,
        db: AsyncSession,
        *,
        file_info: Dict[str, Any],
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> FileMetadata:
        """Create a new file metadata record.
        
        Args:
            db: Database session
            file_info: File information from storage service
            user_id: ID of user who uploaded the file
            organization_id: ID of organization the file belongs to
            
        Returns:
            Created file metadata record
        """
        file_data = {
            "file_id": file_info["file_id"],
            "original_filename": file_info["original_filename"],
            "content_type": file_info["content_type"],
            "file_size": file_info["file_size"],
            "content_hash": file_info["content_hash"],
            "storage_type": file_info["storage_type"],
            "storage_path": file_info["storage_path"],
            "category": file_info["category"],
            "user_id": user_id,
            "organization_id": organization_id,
            "extra_metadata": json.dumps({
                "uploaded_at": file_info["uploaded_at"],
                "file_url": file_info["file_url"]
            })
        }
        
        return await self.create(db, obj_in=file_data)
    
    async def get_by_file_id(
        self, 
        db: AsyncSession, 
        file_id: str
    ) -> Optional[FileMetadata]:
        """Get file metadata by file ID."""
        result = await db.execute(
            select(FileMetadata).where(
                and_(
                    FileMetadata.file_id == file_id,
                    FileMetadata.is_active == True
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_files(
        self,
        db: AsyncSession,
        user_id: str,
        *,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[FileMetadata]:
        """Get files uploaded by a specific user.
        
        Args:
            db: Database session
            user_id: ID of the user
            category: Optional category filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of file metadata records
        """
        query = select(FileMetadata).where(
            and_(
                FileMetadata.user_id == user_id,
                FileMetadata.is_active == True
            )
        )
        
        if category:
            query = query.where(FileMetadata.category == category)
        
        query = query.order_by(desc(FileMetadata.created_at))
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_organization_files(
        self,
        db: AsyncSession,
        organization_id: str,
        *,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[FileMetadata]:
        """Get files belonging to an organization.
        
        Args:
            db: Database session
            organization_id: ID of the organization
            category: Optional category filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of file metadata records
        """
        query = select(FileMetadata).where(
            and_(
                FileMetadata.organization_id == organization_id,
                FileMetadata.is_active == True
            )
        )
        
        if category:
            query = query.where(FileMetadata.category == category)
        
        query = query.order_by(desc(FileMetadata.created_at))
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def count_user_files(
        self,
        db: AsyncSession,
        user_id: str,
        *,
        category: Optional[str] = None
    ) -> int:
        """Count files uploaded by a user."""
        query = select(func.count(FileMetadata.id)).where(
            and_(
                FileMetadata.user_id == user_id,
                FileMetadata.is_active == True
            )
        )
        
        if category:
            query = query.where(FileMetadata.category == category)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def count_organization_files(
        self,
        db: AsyncSession,
        organization_id: str,
        *,
        category: Optional[str] = None
    ) -> int:
        """Count files belonging to an organization."""
        query = select(func.count(FileMetadata.id)).where(
            and_(
                FileMetadata.organization_id == organization_id,
                FileMetadata.is_active == True
            )
        )
        
        if category:
            query = query.where(FileMetadata.category == category)
        
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def get_file_storage_stats(
        self,
        db: AsyncSession,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get storage statistics for files.
        
        Args:
            db: Database session
            organization_id: Optional organization filter
            
        Returns:
            Dictionary with storage statistics
        """
        base_query = select(FileMetadata).where(FileMetadata.is_active == True)
        
        if organization_id:
            base_query = base_query.where(FileMetadata.organization_id == organization_id)
        
        # Total files and size
        total_query = select(
            func.count(FileMetadata.id).label('total_files'),
            func.sum(FileMetadata.file_size).label('total_size')
        ).where(FileMetadata.is_active == True)
        
        if organization_id:
            total_query = total_query.where(FileMetadata.organization_id == organization_id)
        
        total_result = await db.execute(total_query)
        total_stats = total_result.first()
        
        # Files by category
        category_query = select(
            FileMetadata.category,
            func.count(FileMetadata.id).label('count'),
            func.sum(FileMetadata.file_size).label('size')
        ).where(FileMetadata.is_active == True)
        
        if organization_id:
            category_query = category_query.where(FileMetadata.organization_id == organization_id)
        
        category_query = category_query.group_by(FileMetadata.category)
        category_result = await db.execute(category_query)
        category_stats = category_result.all()
        
        return {
            'total_files': total_stats.total_files or 0,
            'total_size_bytes': total_stats.total_size or 0,
            'total_size_mb': round((total_stats.total_size or 0) / (1024 * 1024), 2),
            'by_category': [
                {
                    'category': row.category,
                    'file_count': row.count,
                    'size_bytes': row.size or 0,
                    'size_mb': round((row.size or 0) / (1024 * 1024), 2)
                }
                for row in category_stats
            ]
        }
    
    async def soft_delete_file(
        self,
        db: AsyncSession,
        file_id: str,
        user_id: Optional[str] = None
    ) -> Optional[FileMetadata]:
        """Soft delete a file by marking it as inactive.
        
        Args:
            db: Database session
            file_id: ID of the file to delete
            user_id: Optional user ID for permission checking
            
        Returns:
            Updated file metadata record if found
        """
        query = select(FileMetadata).where(
            and_(
                FileMetadata.file_id == file_id,
                FileMetadata.is_active == True
            )
        )
        
        # Add user permission check if user_id provided
        if user_id:
            query = query.where(FileMetadata.user_id == user_id)
        
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if file_record:
            file_record.is_active = False
            db.add(file_record)
            await db.commit()
            await db.refresh(file_record)
            
            logger.info(f"File soft deleted: {file_id} by user {user_id}")
        
        return file_record
    
    async def update_file_access(
        self,
        db: AsyncSession,
        file_id: str,
        is_public: bool,
        user_id: Optional[str] = None
    ) -> Optional[FileMetadata]:
        """Update file access permissions.
        
        Args:
            db: Database session
            file_id: ID of the file to update
            is_public: New public access setting
            user_id: Optional user ID for permission checking
            
        Returns:
            Updated file metadata record if found
        """
        query = select(FileMetadata).where(
            and_(
                FileMetadata.file_id == file_id,
                FileMetadata.is_active == True
            )
        )
        
        # Add user permission check if user_id provided
        if user_id:
            query = query.where(FileMetadata.user_id == user_id)
        
        result = await db.execute(query)
        file_record = result.scalar_one_or_none()
        
        if file_record:
            file_record.is_public = is_public
            db.add(file_record)
            await db.commit()
            await db.refresh(file_record)
            
            logger.info(f"File access updated: {file_id} public={is_public} by user {user_id}")
        
        return file_record


# Create CRUD instance
file_crud = CRUDFile(FileMetadata)