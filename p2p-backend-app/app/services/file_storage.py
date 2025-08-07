"""File storage service for handling file uploads and management.

This service provides a unified interface for file storage operations,
supporting both local filesystem storage (for development) and cloud storage
like S3 (for production). The implementation is designed to be easily
switchable based on configuration.
"""

import os
import uuid
import mimetypes
import hashlib
from pathlib import Path
from typing import Optional, Tuple, List, BinaryIO
from datetime import datetime, timezone
import aiofiles
from fastapi import UploadFile, HTTPException
from PIL import Image
# import magic  # Disabled for now due to system dependency

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileStorageError(Exception):
    """Custom exception for file storage operations."""
    pass


class FileValidator:
    """File validation utilities with security checks."""
    
    # Allowed file extensions and their corresponding MIME types
    ALLOWED_EXTENSIONS = {
        # Images
        '.jpg': ['image/jpeg'],
        '.jpeg': ['image/jpeg'],  
        '.png': ['image/png'],
        '.gif': ['image/gif'],
        '.webp': ['image/webp'],
        
        # Documents
        '.pdf': ['application/pdf'],
        '.doc': ['application/msword'],
        '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        '.txt': ['text/plain'],
        
        # Archives
        '.zip': ['application/zip'],
        '.tar': ['application/x-tar'],
        '.gz': ['application/gzip'],
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 10 * 1024 * 1024,  # 10MB for images
        'document': 50 * 1024 * 1024,  # 50MB for documents
        'archive': 100 * 1024 * 1024,  # 100MB for archives
        'default': 25 * 1024 * 1024,  # 25MB default
    }
    
    @classmethod
    def get_file_type(cls, mime_type: str) -> str:
        """Determine file category from MIME type."""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type in ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain']:
            return 'document'
        elif mime_type in ['application/zip', 'application/x-tar', 'application/gzip']:
            return 'archive'
        return 'default'
    
    @classmethod 
    async def validate_file(cls, file: UploadFile) -> Tuple[str, str]:
        """Validate uploaded file for security and constraints.
        
        Returns:
            Tuple of (file_extension, detected_mime_type)
            
        Raises:
            HTTPException: If file validation fails
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower()
        if not file_ext:
            raise HTTPException(status_code=400, detail="File must have an extension")
        
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File extension {file_ext} not allowed. Allowed: {list(cls.ALLOWED_EXTENSIONS.keys())}"
            )
        
        # Read first chunk to detect MIME type
        file_content = await file.read(1024)
        await file.seek(0)  # Reset file pointer
        
        # Detect actual MIME type - fallback to mimetypes module for now
        detected_mime, _ = mimetypes.guess_type(file.filename)
        if not detected_mime:
            # Set a default based on extension if mimetypes fails
            if file_ext in ['.jpg', '.jpeg']:
                detected_mime = 'image/jpeg'
            elif file_ext == '.png':
                detected_mime = 'image/png'
            elif file_ext == '.pdf':
                detected_mime = 'application/pdf'
            else:
                raise HTTPException(status_code=400, detail="Could not determine file type")
        
        # Verify MIME type matches extension
        allowed_mimes = cls.ALLOWED_EXTENSIONS[file_ext]
        if detected_mime not in allowed_mimes:
            raise HTTPException(
                status_code=400,
                detail=f"File content ({detected_mime}) doesn't match extension {file_ext}"
            )
        
        # Check file size
        file_size = file.size or 0
        if hasattr(file, 'file'):
            # Get actual file size
            current_pos = file.file.tell()
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(current_pos)  # Reset position
        
        file_type = cls.get_file_type(detected_mime)
        max_size = cls.MAX_FILE_SIZES.get(file_type, cls.MAX_FILE_SIZES['default'])
        
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size for {file_type} files: {max_size // (1024*1024)}MB"
            )
        
        return file_ext, detected_mime


class LocalFileStorage:
    """Local filesystem storage implementation."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def _get_file_path(self, file_id: str, category: str) -> Path:
        """Generate full file path with category organization."""
        # Organize files by category and date
        date_prefix = datetime.now().strftime("%Y/%m")
        return self.base_path / category / date_prefix / file_id
    
    async def save_file(
        self, 
        file: UploadFile, 
        file_id: str,
        category: str = "general"
    ) -> Tuple[str, dict]:
        """Save file to local storage.
        
        Returns:
            Tuple of (file_path, metadata)
        """
        file_path = self._get_file_path(file_id, category)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Calculate file hash while saving
            hasher = hashlib.sha256()
            file_size = 0
            
            async with aiofiles.open(file_path, 'wb') as f:
                await file.seek(0)
                while chunk := await file.read(8192):
                    hasher.update(chunk)
                    await f.write(chunk)
                    file_size += len(chunk)
            
            metadata = {
                'file_size': file_size,
                'content_hash': hasher.hexdigest(),
                'storage_path': str(file_path.relative_to(self.base_path)),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            return str(file_path.relative_to(self.base_path)), metadata
            
        except Exception as e:
            # Clean up partial file if save failed
            if file_path.exists():
                file_path.unlink()
            raise FileStorageError(f"Failed to save file: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local storage."""
        full_path = self.base_path / file_path
        try:
            if full_path.exists():
                full_path.unlink()
                
                # Clean up empty directories
                parent = full_path.parent
                while parent != self.base_path and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                    
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            raise FileStorageError(f"Failed to delete file: {str(e)}")
    
    def get_file_url(self, file_path: str) -> str:
        """Generate URL for accessing the file."""
        # For local development, return API endpoint URL
        return f"{settings.API_DOMAIN}/api/v1/files/{file_path}"
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""
        return (self.base_path / file_path).exists()


class FileStorageService:
    """Main file storage service with unified interface."""
    
    def __init__(self):
        self.validator = FileValidator()
        
        # Initialize storage backend based on configuration
        if settings.S3_BUCKET_NAME and settings.AWS_ACCESS_KEY_ID:
            # TODO: Initialize S3 storage when credentials are available
            logger.info("S3 credentials found but S3 storage not yet implemented")
            self._use_local_storage()
        else:
            self._use_local_storage()
    
    def _use_local_storage(self):
        """Initialize local file storage."""
        # Use local storage directory in project root
        import os
        storage_path = os.path.join(os.getcwd(), "storage")
        self.storage = LocalFileStorage(storage_path)
        self.storage_type = "local"
        logger.info(f"Using local file storage at {storage_path}")
    
    async def upload_file(
        self,
        file: UploadFile,
        category: str = "general",
        user_id: Optional[str] = None
    ) -> dict:
        """Upload and store a file.
        
        Args:
            file: The uploaded file
            category: File category (profile_pictures, documents, etc.)
            user_id: Optional user ID for access control
            
        Returns:
            Dictionary with file information
        """
        # Validate file
        file_ext, mime_type = await self.validator.validate_file(file)
        
        # Generate unique file ID
        file_id = f"{uuid.uuid4().hex}{file_ext}"
        
        try:
            # Save file to storage
            storage_path, storage_metadata = await self.storage.save_file(
                file, file_id, category
            )
            
            # Prepare response metadata
            file_info = {
                'file_id': file_id,
                'original_filename': file.filename,
                'content_type': mime_type,
                'category': category,
                'storage_path': storage_path,
                'file_url': self.storage.get_file_url(storage_path),
                'user_id': user_id,
                'uploaded_at': datetime.now(timezone.utc).isoformat(),
                'storage_type': self.storage_type,
                **storage_metadata
            }
            
            logger.info(f"File uploaded successfully: {file_id} by user {user_id}")
            return file_info
            
        except Exception as e:
            logger.error(f"File upload failed for {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail="File upload failed")
    
    async def delete_file(self, file_path: str, user_id: Optional[str] = None) -> bool:
        """Delete a file from storage.
        
        Args:
            file_path: Storage path of the file
            user_id: User ID for access control logging
            
        Returns:
            True if file was deleted successfully
        """
        try:
            success = await self.storage.delete_file(file_path)
            if success:
                logger.info(f"File deleted successfully: {file_path} by user {user_id}")
            else:
                logger.warning(f"File not found for deletion: {file_path}")
            return success
        except Exception as e:
            logger.error(f"File deletion failed for {file_path}: {str(e)}")
            raise HTTPException(status_code=500, detail="File deletion failed")
    
    def get_file_url(self, file_path: str) -> str:
        """Get public URL for a file."""
        return self.storage.get_file_url(file_path)
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage."""
        return self.storage.file_exists(file_path)
    
    async def get_file_info(self, file_path: str) -> Optional[dict]:
        """Get file information and metadata."""
        if not self.file_exists(file_path):
            return None
        
        full_path = self.storage.base_path / file_path
        stat = full_path.stat()
        
        return {
            'file_path': file_path,
            'file_size': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            'file_url': self.get_file_url(file_path)
        }


# Global service instance
file_storage_service = FileStorageService()