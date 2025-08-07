# Local Storage Architecture

## Overview
This document defines the local file storage architecture for the P2P Sandbox application, designed to handle media uploads, exports, and attachments during development. The architecture is designed to easily migrate to AWS S3 or Azure Blob Storage in production.

---

## Directory Structure

### Complete File System Layout
```
p2p-backend-app/
├── uploads/                           # All user-uploaded content
│   ├── use-cases/                    # Use case related files
│   │   └── {organization_id}/        # Organization isolation
│   │       └── {use_case_id}/        # Use case specific
│   │           ├── images/
│   │           │   ├── original/     # Original uploaded images
│   │           │   ├── thumbnails/   # Generated thumbnails
│   │           │   └── optimized/    # Web-optimized versions
│   │           ├── documents/        # PDFs, Word docs, etc.
│   │           ├── videos/            # Video files
│   │           └── presentations/    # PowerPoint, etc.
│   │
│   ├── messages/                      # Message attachments
│   │   └── attachments/
│   │       └── {conversation_id}/
│   │           └── {message_id}/
│   │               ├── files/        # General attachments
│   │               └── images/       # Image attachments
│   │
│   ├── profiles/                      # User profile data
│   │   └── avatars/
│   │       └── {user_id}/
│   │           ├── original/         # Original avatar
│   │           └── sizes/            # Multiple sizes
│   │               ├── small/        # 50x50
│   │               ├── medium/       # 150x150
│   │               └── large/        # 300x300
│   │
│   └── temp/                          # Temporary upload storage
│       └── {session_id}/              # Session-based temp files
│           └── {timestamp}/           # Auto-cleanup after 24h
│
├── exports/                           # Generated export files
│   ├── use-cases/
│   │   └── {timestamp}/
│   │       ├── pdf/                  # PDF exports
│   │       ├── excel/                # Excel exports
│   │       └── csv/                  # CSV exports
│   │
│   └── reports/                       # System reports
│       └── {organization_id}/
│           └── {report_type}/
│               └── {timestamp}/
│
├── static/                            # Static assets
│   ├── media/                         # Public media files
│   │   ├── defaults/                 # Default images
│   │   │   ├── avatar.png           # Default user avatar
│   │   │   └── placeholder.jpg      # Placeholder image
│   │   └── system/                   # System images
│   │       └── logos/                # Company logos
│   │
│   └── templates/                     # Document templates
│       ├── exports/                  # Export templates
│       │   ├── use-case-pdf.html    # PDF template
│       │   └── use-case-excel.xlsx  # Excel template
│       └── emails/                   # Email templates
│
└── logs/                              # File operation logs
    └── storage/
        ├── uploads.log               # Upload activity
        ├── deletions.log             # Deletion activity
        └── errors.log                # Error logs
```

---

## Storage Service Implementation

### Base Storage Interface
```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO, Dict, Any
import aiofiles
import uuid
from datetime import datetime

class StorageInterface(ABC):
    """Abstract base class for storage implementations"""
    
    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file and return its path/URL"""
        pass
    
    @abstractmethod
    async def download(self, path: str) -> BinaryIO:
        """Download a file"""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file"""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get a URL for the file"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str) -> List[str]:
        """List files with a given prefix"""
        pass
```

### Local Storage Implementation
```python
import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, BinaryIO, Dict, Any, List
import aiofiles
import aiofiles.os
from fastapi import HTTPException
from fastapi.responses import FileResponse

class LocalStorage(StorageInterface):
    """Local file system storage implementation"""
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create required directories
        self._create_directory_structure()
    
    def _create_directory_structure(self):
        """Create the complete directory structure"""
        directories = [
            "use-cases",
            "messages/attachments",
            "profiles/avatars",
            "temp",
            "../exports/use-cases",
            "../exports/reports",
            "../static/media/defaults",
            "../static/media/system",
            "../static/templates/exports",
            "../static/templates/emails",
            "../logs/storage"
        ]
        
        for dir_path in directories:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
    
    async def upload(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file to local storage"""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        async with aiofiles.open(full_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Save metadata if provided
        if metadata:
            metadata_path = full_path.with_suffix('.meta.json')
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata))
        
        # Log upload
        await self._log_operation('upload', str(path), metadata)
        
        return str(path)
    
    async def download(self, path: str) -> Path:
        """Get file path for download"""
        full_path = self.base_path / path
        
        if not await self.exists(path):
            raise HTTPException(404, "File not found")
        
        return full_path
    
    async def delete(self, path: str) -> bool:
        """Delete a file from local storage"""
        full_path = self.base_path / path
        
        try:
            if full_path.is_file():
                await aiofiles.os.remove(full_path)
                
                # Remove metadata if exists
                metadata_path = full_path.with_suffix('.meta.json')
                if metadata_path.exists():
                    await aiofiles.os.remove(metadata_path)
                
                # Log deletion
                await self._log_operation('delete', str(path))
                return True
            return False
        except Exception as e:
            await self._log_error('delete', str(path), str(e))
            return False
    
    async def exists(self, path: str) -> bool:
        """Check if file exists"""
        full_path = self.base_path / path
        return full_path.exists()
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get URL for file (local returns path)"""
        # In local mode, return a path that can be served by FastAPI
        return f"/media/{path}"
    
    async def list_files(self, prefix: str) -> List[str]:
        """List files with given prefix"""
        prefix_path = self.base_path / prefix
        
        if not prefix_path.exists():
            return []
        
        files = []
        for file_path in prefix_path.rglob('*'):
            if file_path.is_file() and not file_path.name.endswith('.meta.json'):
                relative_path = file_path.relative_to(self.base_path)
                files.append(str(relative_path))
        
        return files
    
    async def _log_operation(
        self,
        operation: str,
        path: str,
        metadata: Optional[Dict] = None
    ):
        """Log storage operations"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "path": path,
            "metadata": metadata
        }
        
        log_file = self.base_path / f"../logs/storage/{operation}s.log"
        async with aiofiles.open(log_file, 'a') as f:
            await f.write(json.dumps(log_entry) + '\n')
    
    async def _log_error(self, operation: str, path: str, error: str):
        """Log storage errors"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "path": path,
            "error": error
        }
        
        log_file = self.base_path / "../logs/storage/errors.log"
        async with aiofiles.open(log_file, 'a') as f:
            await f.write(json.dumps(log_entry) + '\n')
```

---

## File Upload Service

### Media Upload Handler
```python
from fastapi import UploadFile, HTTPException
from PIL import Image
from typing import Dict, List, Optional, Tuple
import magic
import hashlib
from pathlib import Path

class MediaUploadService:
    """Service for handling media uploads with validation and processing"""
    
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
    
    def __init__(self, storage: StorageInterface):
        self.storage = storage
    
    async def upload_image(
        self,
        file: UploadFile,
        entity_type: str,  # 'use-case', 'profile', etc.
        entity_id: str,
        organization_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Upload and process an image"""
        
        # Validate file
        await self._validate_file(file, 'image')
        
        # Generate paths
        paths = self._generate_paths(
            entity_type,
            entity_id,
            organization_id,
            file.filename
        )
        
        # Read file content
        content = await file.read()
        
        # Save original
        original_path = await self.storage.upload(
            io.BytesIO(content),
            paths['original'],
            {'content_type': file.content_type}
        )
        
        # Process image sizes
        processed_paths = {}
        image = Image.open(io.BytesIO(content))
        
        for size_name, dimensions in self.IMAGE_SIZES.items():
            processed_image = self._resize_image(image, dimensions)
            
            # Save to buffer
            buffer = io.BytesIO()
            processed_image.save(buffer, format=image.format)
            buffer.seek(0)
            
            # Upload processed image
            size_path = paths['base'] / size_name / paths['filename']
            processed_paths[size_name] = await self.storage.upload(
                buffer,
                str(size_path)
            )
        
        return {
            'original': original_path,
            **processed_paths,
            'content_type': file.content_type,
            'size': len(content)
        }
    
    async def upload_document(
        self,
        file: UploadFile,
        entity_type: str,
        entity_id: str,
        organization_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Upload a document"""
        
        # Validate file
        await self._validate_file(file, 'document')
        
        # Generate path
        paths = self._generate_paths(
            entity_type,
            entity_id,
            organization_id,
            file.filename
        )
        
        # Upload file
        content = await file.read()
        path = await self.storage.upload(
            io.BytesIO(content),
            paths['original'],
            {
                'content_type': file.content_type,
                'original_name': file.filename
            }
        )
        
        return {
            'path': path,
            'content_type': file.content_type,
            'size': len(content),
            'filename': file.filename
        }
    
    async def _validate_file(self, file: UploadFile, file_type: str):
        """Validate file type and size"""
        
        # Check file type
        if file_type == 'image':
            allowed_types = self.ALLOWED_IMAGES
            max_size = self.MAX_IMAGE_SIZE
        elif file_type == 'document':
            allowed_types = self.ALLOWED_DOCUMENTS
            max_size = self.MAX_DOCUMENT_SIZE
        elif file_type == 'video':
            allowed_types = self.ALLOWED_VIDEOS
            max_size = self.MAX_VIDEO_SIZE
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        
        # Verify MIME type
        if file.content_type not in allowed_types:
            raise HTTPException(
                400,
                f"File type {file.content_type} not allowed"
            )
        
        # Check file extension
        ext = Path(file.filename).suffix.lower()
        valid_extensions = [e for exts in allowed_types.values() for e in exts]
        if ext not in valid_extensions:
            raise HTTPException(
                400,
                f"File extension {ext} not allowed"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset
        
        if size > max_size:
            raise HTTPException(
                400,
                f"File too large. Max size: {max_size // (1024*1024)}MB"
            )
        
        # Verify actual content type (security check)
        content = await file.read(1024)  # Read first KB
        file.file.seek(0)  # Reset
        
        detected_type = magic.from_buffer(content, mime=True)
        if detected_type != file.content_type:
            # Allow some flexibility for similar types
            if not self._are_types_compatible(detected_type, file.content_type):
                raise HTTPException(
                    400,
                    "File content does not match declared type"
                )
    
    def _generate_paths(
        self,
        entity_type: str,
        entity_id: str,
        organization_id: Optional[str],
        filename: str
    ) -> Dict[str, Path]:
        """Generate storage paths"""
        
        # Generate unique filename
        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{ext}"
        
        # Build path structure
        if entity_type == 'use-case':
            base = Path('use-cases') / organization_id / entity_id / 'images'
        elif entity_type == 'profile':
            base = Path('profiles/avatars') / entity_id
        elif entity_type == 'message':
            base = Path('messages/attachments') / entity_id
        else:
            base = Path('temp') / entity_id
        
        return {
            'base': base,
            'filename': unique_name,
            'original': base / 'original' / unique_name
        }
    
    def _resize_image(
        self,
        image: Image.Image,
        size: Tuple[int, int]
    ) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        
        # Calculate aspect ratio
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Create new image with exact size (add padding if needed)
        new_image = Image.new('RGB', size, (255, 255, 255))
        
        # Paste resized image centered
        x = (size[0] - image.width) // 2
        y = (size[1] - image.height) // 2
        new_image.paste(image, (x, y))
        
        return new_image
    
    def _are_types_compatible(self, detected: str, declared: str) -> bool:
        """Check if MIME types are compatible"""
        compatible_pairs = [
            ('image/jpeg', 'image/jpg'),
            ('application/zip', 'application/x-zip-compressed')
        ]
        
        for pair in compatible_pairs:
            if (detected, declared) == pair or (declared, detected) == pair:
                return True
        
        return detected == declared
```

---

## File Serving

### Static File Server
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import mimetypes

class FileServer:
    """Service for serving files with proper headers and caching"""
    
    def __init__(self, app: FastAPI, storage: LocalStorage):
        self.app = app
        self.storage = storage
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup file serving routes"""
        
        # Serve static files
        self.app.mount(
            "/static",
            StaticFiles(directory="static"),
            name="static"
        )
        
        # Serve uploaded media files
        @self.app.get("/media/{path:path}")
        async def serve_media(path: str):
            """Serve uploaded media files"""
            
            # Security: Prevent path traversal
            if '..' in path or path.startswith('/'):
                raise HTTPException(403, "Invalid path")
            
            # Get file path
            file_path = await self.storage.download(path)
            
            if not file_path.exists():
                raise HTTPException(404, "File not found")
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Return file with proper headers
            return FileResponse(
                file_path,
                media_type=content_type,
                headers={
                    'Cache-Control': 'public, max-age=3600',
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'SAMEORIGIN'
                }
            )
        
        @self.app.get("/download/{path:path}")
        async def download_file(path: str):
            """Force download of a file"""
            
            # Security check
            if '..' in path or path.startswith('/'):
                raise HTTPException(403, "Invalid path")
            
            file_path = await self.storage.download(path)
            
            if not file_path.exists():
                raise HTTPException(404, "File not found")
            
            # Force download with Content-Disposition
            return FileResponse(
                file_path,
                media_type='application/octet-stream',
                headers={
                    'Content-Disposition': f'attachment; filename="{file_path.name}"'
                }
            )
```

---

## Cleanup Service

### Temporary File Cleanup
```python
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import shutil

class CleanupService:
    """Service for cleaning up temporary and old files"""
    
    def __init__(self, storage: LocalStorage):
        self.storage = storage
        self.running = False
    
    async def start(self):
        """Start cleanup service"""
        self.running = True
        
        # Schedule cleanup tasks
        asyncio.create_task(self._cleanup_temp_files())
        asyncio.create_task(self._cleanup_old_exports())
        asyncio.create_task(self._cleanup_orphaned_files())
    
    async def stop(self):
        """Stop cleanup service"""
        self.running = False
    
    async def _cleanup_temp_files(self):
        """Clean up temporary files older than 24 hours"""
        while self.running:
            try:
                temp_dir = Path('uploads/temp')
                cutoff_time = datetime.now() - timedelta(hours=24)
                
                for session_dir in temp_dir.iterdir():
                    if session_dir.is_dir():
                        # Check directory age
                        mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
                        if mtime < cutoff_time:
                            shutil.rmtree(session_dir)
                            await self._log_cleanup('temp', str(session_dir))
                
            except Exception as e:
                logging.error(f"Temp cleanup error: {e}")
            
            # Run every hour
            await asyncio.sleep(3600)
    
    async def _cleanup_old_exports(self):
        """Clean up export files older than 7 days"""
        while self.running:
            try:
                exports_dir = Path('exports')
                cutoff_time = datetime.now() - timedelta(days=7)
                
                for export_file in exports_dir.rglob('*'):
                    if export_file.is_file():
                        mtime = datetime.fromtimestamp(export_file.stat().st_mtime)
                        if mtime < cutoff_time:
                            export_file.unlink()
                            await self._log_cleanup('export', str(export_file))
                
            except Exception as e:
                logging.error(f"Export cleanup error: {e}")
            
            # Run daily
            await asyncio.sleep(86400)
    
    async def _cleanup_orphaned_files(self):
        """Clean up files not referenced in database"""
        while self.running:
            try:
                # This would check database references
                # Implementation depends on database structure
                pass
                
            except Exception as e:
                logging.error(f"Orphan cleanup error: {e}")
            
            # Run weekly
            await asyncio.sleep(604800)
    
    async def _log_cleanup(self, cleanup_type: str, path: str):
        """Log cleanup operations"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": cleanup_type,
            "path": path
        }
        
        log_file = Path('logs/storage/cleanup.log')
        async with aiofiles.open(log_file, 'a') as f:
            await f.write(json.dumps(log_entry) + '\n')
```

---

## Migration to Cloud Storage

### AWS S3 Implementation (Future)
```python
import boto3
from botocore.exceptions import ClientError
import asyncio

class S3Storage(StorageInterface):
    """AWS S3 storage implementation"""
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        self.bucket_name = bucket_name
        self.region = region
        self.client = boto3.client('s3', region_name=region)
    
    async def upload(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload file to S3"""
        try:
            # Prepare metadata
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = {
                    k: str(v) for k, v in metadata.items()
                }
            
            # Upload to S3
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.upload_fileobj,
                file,
                self.bucket_name,
                path,
                extra_args
            )
            
            return f"s3://{self.bucket_name}/{path}"
            
        except ClientError as e:
            raise HTTPException(500, f"S3 upload failed: {e}")
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Generate presigned URL"""
        try:
            url = await asyncio.get_event_loop().run_in_executor(
                None,
                self.client.generate_presigned_url,
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': path},
                ExpiresIn=expires_in
            )
            return url
            
        except ClientError as e:
            raise HTTPException(500, f"URL generation failed: {e}")
```

### Storage Factory
```python
import os
from typing import Optional

class StorageFactory:
    """Factory for creating storage instances based on configuration"""
    
    @staticmethod
    def create_storage(storage_type: Optional[str] = None) -> StorageInterface:
        """Create storage instance based on type or environment"""
        
        if not storage_type:
            storage_type = os.getenv('STORAGE_TYPE', 'local')
        
        if storage_type == 'local':
            return LocalStorage(
                base_path=os.getenv('LOCAL_STORAGE_PATH', 'uploads')
            )
        
        elif storage_type == 's3':
            return S3Storage(
                bucket_name=os.getenv('S3_BUCKET_NAME'),
                region=os.getenv('AWS_REGION', 'us-east-1')
            )
        
        elif storage_type == 'azure':
            return AzureStorage(
                container_name=os.getenv('AZURE_CONTAINER_NAME'),
                account_name=os.getenv('AZURE_ACCOUNT_NAME')
            )
        
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")

# Usage in application
storage = StorageFactory.create_storage()
```

---

## Configuration

### Environment Variables
```bash
# .env file for local development

# Storage Configuration
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=uploads

# File Upload Limits
MAX_UPLOAD_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,doc,docx,xls,xlsx

# Cleanup Settings
TEMP_FILE_TTL=86400  # 24 hours in seconds
EXPORT_FILE_TTL=604800  # 7 days in seconds

# Future Cloud Storage (commented out for local)
# STORAGE_TYPE=s3
# S3_BUCKET_NAME=p2p-sandbox-uploads
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=xxx
# AWS_SECRET_ACCESS_KEY=xxx
```

### Application Configuration
```python
from pydantic import BaseSettings
from typing import List

class StorageSettings(BaseSettings):
    """Storage configuration settings"""
    
    # Storage type
    storage_type: str = "local"
    local_storage_path: str = "uploads"
    
    # File upload settings
    max_upload_size: int = 52428800  # 50MB
    allowed_image_extensions: List[str] = [
        ".jpg", ".jpeg", ".png", ".gif", ".webp"
    ]
    allowed_document_extensions: List[str] = [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
    ]
    
    # Image processing
    thumbnail_size: tuple = (300, 200)
    medium_size: tuple = (800, 600)
    large_size: tuple = (1920, 1080)
    image_quality: int = 85
    
    # Cleanup settings
    temp_file_ttl: int = 86400  # 24 hours
    export_file_ttl: int = 604800  # 7 days
    
    # Security
    enable_virus_scan: bool = False
    max_filename_length: int = 255
    sanitize_filenames: bool = True
    
    class Config:
        env_file = ".env"
        env_prefix = "STORAGE_"

storage_settings = StorageSettings()
```

---

## Security Considerations

### 1. Path Traversal Prevention
```python
def sanitize_path(path: str) -> str:
    """Sanitize file path to prevent traversal attacks"""
    # Remove any parent directory references
    path = path.replace('../', '').replace('..\\', '')
    
    # Remove leading slashes
    path = path.lstrip('/')
    
    # Ensure path doesn't start with system directories
    forbidden_starts = ['/etc', '/var', '/usr', 'C:\\']
    for forbidden in forbidden_starts:
        if path.startswith(forbidden):
            raise ValueError("Invalid path")
    
    return path
```

### 2. Filename Sanitization
```python
import re
import unicodedata

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Normalize unicode
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove non-ASCII characters
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Replace spaces and special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\s+', '-', filename)
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}{ext}".lower()
```

### 3. File Type Validation
```python
import magic

def validate_file_type(file_path: Path, expected_type: str) -> bool:
    """Validate file type using magic numbers"""
    mime = magic.Magic(mime=True)
    detected_type = mime.from_file(str(file_path))
    
    # Check if detected type matches expected
    type_mappings = {
        'image/jpeg': ['image/jpeg', 'image/jpg'],
        'application/pdf': ['application/pdf', 'application/x-pdf']
    }
    
    valid_types = type_mappings.get(expected_type, [expected_type])
    return detected_type in valid_types
```

---

## Monitoring & Metrics

### Storage Metrics
```python
class StorageMetrics:
    """Track storage usage and performance"""
    
    def __init__(self):
        self.upload_count = 0
        self.download_count = 0
        self.total_size = 0
        self.errors = []
    
    async def track_upload(self, size: int, duration: float):
        """Track upload metrics"""
        self.upload_count += 1
        self.total_size += size
        
        # Log metrics
        metrics = {
            "type": "upload",
            "size": size,
            "duration": duration,
            "throughput": size / duration if duration > 0 else 0
        }
        await self._log_metrics(metrics)
    
    async def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        upload_dir = Path('uploads')
        
        total_files = 0
        total_size = 0
        
        for file_path in upload_dir.rglob('*'):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
        
        return {
            "total_files": total_files,
            "total_size_mb": total_size / (1024 * 1024),
            "upload_count": self.upload_count,
            "download_count": self.download_count,
            "error_count": len(self.errors)
        }
```

---

## Testing

### Storage Tests
```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
async def storage():
    """Create temporary storage for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(base_path=tmpdir)
        yield storage

async def test_upload_download(storage):
    """Test file upload and download"""
    # Create test file
    content = b"Test content"
    file = io.BytesIO(content)
    
    # Upload
    path = await storage.upload(file, "test/file.txt")
    assert path == "test/file.txt"
    
    # Download
    downloaded = await storage.download(path)
    assert downloaded.read_bytes() == content

async def test_delete(storage):
    """Test file deletion"""
    # Upload file
    file = io.BytesIO(b"Test")
    path = await storage.upload(file, "test/delete.txt")
    
    # Verify exists
    assert await storage.exists(path)
    
    # Delete
    result = await storage.delete(path)
    assert result is True
    
    # Verify deleted
    assert not await storage.exists(path)

async def test_image_processing():
    """Test image resizing"""
    service = MediaUploadService(LocalStorage())
    
    # Create test image
    image = Image.new('RGB', (1000, 800), color='red')
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    
    # Process image
    resized = service._resize_image(image, (300, 200))
    
    assert resized.size == (300, 200)
```

---

## Deployment Considerations

### 1. Directory Permissions
```bash
# Set appropriate permissions
chmod 755 uploads/
chmod 755 exports/
chmod 755 static/

# Ensure write permissions for application user
chown -R app:app uploads/
chown -R app:app exports/
chown -R app:app logs/
```

### 2. Backup Strategy
```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups/p2p-storage"
DATE=$(date +%Y%m%d)

# Create backup
tar -czf "$BACKUP_DIR/uploads-$DATE.tar.gz" uploads/
tar -czf "$BACKUP_DIR/exports-$DATE.tar.gz" exports/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### 3. Migration Script
```python
async def migrate_to_s3():
    """Migrate local files to S3"""
    local = LocalStorage()
    s3 = S3Storage(bucket_name="p2p-sandbox")
    
    # Get all local files
    files = await local.list_files("")
    
    for file_path in files:
        # Download from local
        local_file = await local.download(file_path)
        
        # Upload to S3
        with open(local_file, 'rb') as f:
            await s3.upload(f, file_path)
        
        print(f"Migrated: {file_path}")
```

---

## Conclusion

This local storage architecture provides:
1. **Simple Development**: No cloud dependencies
2. **Easy Testing**: Direct file system access
3. **Cost Effective**: No cloud storage costs
4. **Migration Ready**: Clean abstraction for future cloud migration
5. **Security**: Path traversal prevention, file validation
6. **Performance**: Local file access, image optimization
7. **Maintenance**: Automatic cleanup, structured logging

The architecture is designed to seamlessly transition to cloud storage (AWS S3, Azure Blob) when moving to production, requiring minimal code changes through the storage interface abstraction.