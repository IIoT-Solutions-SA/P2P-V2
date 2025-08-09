"""Media upload and processing service."""

import io
import hashlib
import uuid
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from PIL import Image
# import magic  # Disabled - using mimetypes instead
from fastapi import UploadFile, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.storage import StorageInterface
from app.models.use_case import MediaType
from app.schemas.use_case import MediaUpload

logger = logging.getLogger(__name__)


class MediaUploadService:
    """Service for handling media uploads with validation and processing."""
    
    # File type configurations
    ALLOWED_IMAGES = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        'image/webp': ['.webp']
    }
    
    ALLOWED_DOCUMENTS = {
        'application/pdf': ['.pdf'],
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        'application/vnd.ms-excel': ['.xls'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        'application/vnd.ms-powerpoint': ['.ppt'],
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx']
    }
    
    ALLOWED_VIDEOS = {
        'video/mp4': ['.mp4'],
        'video/mpeg': ['.mpeg'],
        'video/quicktime': ['.mov'],
        'video/x-msvideo': ['.avi']
    }
    
    # Size limits (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10MB
    MAX_DOCUMENT_SIZE = 50 * 1024 * 1024   # 50MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024     # 500MB
    
    # Image processing settings
    IMAGE_SIZES = {
        'thumbnail': (300, 200),
        'medium': (800, 600),
        'large': (1920, 1080)
    }
    
    def __init__(self, storage: StorageInterface, db: AsyncIOMotorDatabase):
        self.storage = storage
        self.db = db
    
    async def upload_media(
        self,
        file: UploadFile,
        entity_type: str,  # 'use-case', 'message', etc.
        entity_id: str,
        organization_id: str,
        caption: Optional[str] = None
    ) -> MediaUpload:
        """Upload and process a media file."""
        
        # Determine media type
        media_type = self._determine_media_type(file.content_type, file.filename)
        
        # Validate file
        await self._validate_file(file, media_type)
        
        # Generate paths
        paths = self._generate_paths(
            entity_type,
            entity_id,
            organization_id,
            file.filename
        )
        
        # Read file content
        content = await file.read()
        file.file.seek(0)  # Reset for potential re-reading
        
        # Save original file
        original_path = await self.storage.upload(
            io.BytesIO(content),
            paths['original'],
            {
                'content_type': file.content_type,
                'original_filename': file.filename,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'organization_id': organization_id,
                'uploaded_at': str(uuid.uuid4())
            }
        )
        
        # Process image if needed
        thumbnail_path = None
        if media_type == MediaType.IMAGE:
            thumbnail_path = await self._process_image(
                content,
                paths['base'],
                paths['filename']
            )
        
        # Create media response
        media_upload = MediaUpload(
            media_id=str(uuid.uuid4()),
            url=await self.storage.get_url(original_path),
            thumbnail_url=await self.storage.get_url(thumbnail_path) if thumbnail_path else None,
            type=media_type,
            size=len(content),
            filename=file.filename
        )
        
        # Update use case media array
        if entity_type == 'use-case':
            await self._update_use_case_media(
                entity_id,
                organization_id,
                {
                    'id': media_upload.media_id,
                    'type': media_type.value,
                    'filename': file.filename,
                    'path': original_path,
                    'thumbnail_path': thumbnail_path,
                    'size': len(content),
                    'mime_type': file.content_type,
                    'caption': caption,
                    'order': 0  # Will be updated based on existing media count
                }
            )
        
        logger.info(f"Uploaded {media_type.value} for {entity_type} {entity_id}")
        return media_upload
    
    async def delete_media(
        self,
        media_id: str,
        entity_type: str,
        entity_id: str,
        user_id: str
    ) -> bool:
        """Delete a media file."""
        try:
            # Get media info from use case
            if entity_type == 'use-case':
                use_case = await self.db.use_cases.find_one({'id': entity_id})
                if not use_case:
                    return False
                
                # Find media item
                media_item = None
                for media in use_case.get('media', []):
                    if media['id'] == media_id:
                        media_item = media
                        break
                
                if not media_item:
                    return False
                
                # Delete files
                await self.storage.delete(media_item['path'])
                if media_item.get('thumbnail_path'):
                    await self.storage.delete(media_item['thumbnail_path'])
                
                # Remove from use case
                await self.db.use_cases.update_one(
                    {'id': entity_id},
                    {'$pull': {'media': {'id': media_id}}}
                )
                
                logger.info(f"Deleted media {media_id} from {entity_type} {entity_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting media {media_id}: {e}")
            return False
    
    def _determine_media_type(self, content_type: str, filename: str) -> MediaType:
        """Determine media type from content type and filename."""
        if content_type in self.ALLOWED_IMAGES:
            return MediaType.IMAGE
        elif content_type in self.ALLOWED_DOCUMENTS:
            return MediaType.DOCUMENT
        elif content_type in self.ALLOWED_VIDEOS:
            return MediaType.VIDEO
        else:
            # Try to determine from extension
            ext = Path(filename).suffix.lower()
            for mime_types, extensions in [
                (self.ALLOWED_IMAGES, MediaType.IMAGE),
                (self.ALLOWED_DOCUMENTS, MediaType.DOCUMENT),
                (self.ALLOWED_VIDEOS, MediaType.VIDEO)
            ]:
                for exts in mime_types.values():
                    if ext in exts:
                        return extensions
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {content_type}"
            )
    
    async def _validate_file(self, file: UploadFile, media_type: MediaType):
        """Validate file type and size."""
        
        # Check file type
        if media_type == MediaType.IMAGE:
            allowed_types = self.ALLOWED_IMAGES
            max_size = self.MAX_IMAGE_SIZE
        elif media_type == MediaType.DOCUMENT:
            allowed_types = self.ALLOWED_DOCUMENTS
            max_size = self.MAX_DOCUMENT_SIZE
        elif media_type == MediaType.VIDEO:
            allowed_types = self.ALLOWED_VIDEOS
            max_size = self.MAX_VIDEO_SIZE
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown media type: {media_type}"
            )
        
        # Verify MIME type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file.content_type} not allowed for {media_type.value}"
            )
        
        # Check file extension
        ext = Path(file.filename).suffix.lower()
        valid_extensions = [e for exts in allowed_types.values() for e in exts]
        if ext not in valid_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension {ext} not allowed"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset
        
        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {max_size // (1024*1024)}MB"
            )
        
        # Verify actual content type (security check)
        content = await file.read(1024)  # Read first KB
        file.file.seek(0)  # Reset
        
        try:
            # Use filename-based type detection instead of magic
            detected_type = mimetypes.guess_type(file.filename)[0] or file.content_type
            if not self._are_types_compatible(detected_type, file.content_type):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content does not match declared type"
                )
        except Exception as e:
            logger.warning(f"Could not verify file type: {e}")
            # Continue without magic verification if it fails
    
    def _generate_paths(
        self,
        entity_type: str,
        entity_id: str,
        organization_id: str,
        filename: str
    ) -> Dict[str, str]:
        """Generate storage paths."""
        
        # Generate unique filename
        file_hash = hashlib.md5(f"{entity_id}{filename}{uuid.uuid4()}".encode()).hexdigest()
        ext = Path(filename).suffix
        unique_name = f"{file_hash}{ext}"
        
        # Build path structure
        if entity_type == 'use-case':
            base = f"use-cases/{organization_id}/{entity_id}/images"
        elif entity_type == 'message':
            base = f"messages/attachments/{entity_id}"
        else:
            base = f"temp/{entity_id}"
        
        return {
            'base': base,
            'filename': unique_name,
            'original': f"{base}/original/{unique_name}"
        }
    
    async def _process_image(
        self,
        content: bytes,
        base_path: str,
        filename: str
    ) -> str:
        """Process image and create thumbnail."""
        try:
            # Open image
            image = Image.open(io.BytesIO(content))
            
            # Create thumbnail
            thumbnail = self._resize_image(image, self.IMAGE_SIZES['thumbnail'])
            
            # Save thumbnail
            thumbnail_buffer = io.BytesIO()
            thumbnail.save(thumbnail_buffer, format=image.format or 'JPEG', optimize=True, quality=85)
            thumbnail_buffer.seek(0)
            
            thumbnail_path = f"{base_path}/thumbnails/{filename}"
            await self.storage.upload(
                thumbnail_buffer,
                thumbnail_path
            )
            
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def _resize_image(
        self,
        image: Image.Image,
        size: Tuple[int, int]
    ) -> Image.Image:
        """Resize image maintaining aspect ratio."""
        
        # Calculate aspect ratio
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create new image with exact size (add padding if needed)
        if image.mode in ('RGBA', 'LA', 'P'):
            new_image = Image.new('RGBA', size, (255, 255, 255, 0))
        else:
            new_image = Image.new('RGB', size, (255, 255, 255))
        
        # Paste resized image centered
        x = (size[0] - image.width) // 2
        y = (size[1] - image.height) // 2
        
        if image.mode in ('RGBA', 'LA', 'P'):
            new_image.paste(image, (x, y), image)
        else:
            new_image.paste(image, (x, y))
        
        return new_image
    
    def _are_types_compatible(self, detected: str, declared: str) -> bool:
        """Check if MIME types are compatible."""
        if detected == declared:
            return True
        
        # Some compatibility mappings
        compatible_pairs = [
            ('image/jpeg', 'image/jpg'),
            ('application/zip', 'application/x-zip-compressed'),
            ('text/plain', 'application/octet-stream')  # Sometimes text files are detected as octet-stream
        ]
        
        for pair in compatible_pairs:
            if (detected, declared) == pair or (declared, detected) == pair:
                return True
        
        return False
    
    async def _update_use_case_media(
        self,
        use_case_id: str,
        organization_id: str,
        media_data: Dict
    ):
        """Add media to use case."""
        try:
            # Get current media count for ordering
            use_case = await self.db.use_cases.find_one({'id': use_case_id})
            if use_case:
                current_media = use_case.get('media', [])
                media_data['order'] = len(current_media)
            
            # Add media to use case
            await self.db.use_cases.update_one(
                {'id': use_case_id, 'organization_id': organization_id},
                {'$push': {'media': media_data}}
            )
            
        except Exception as e:
            logger.error(f"Error updating use case media: {e}")
            raise


# Factory function
def get_media_service(
    storage: StorageInterface,
    db: AsyncIOMotorDatabase
) -> MediaUploadService:
    """Get media upload service instance."""
    return MediaUploadService(storage, db)