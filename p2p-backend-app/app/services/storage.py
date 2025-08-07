"""Local storage service for file management."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO, Dict, Any, List
import aiofiles
import aiofiles.os
import json
import logging
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import FileResponse
import os
import shutil

logger = logging.getLogger(__name__)


class StorageInterface(ABC):
    """Abstract base class for storage implementations."""
    
    @abstractmethod
    async def upload(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file and return its path/URL."""
        pass
    
    @abstractmethod
    async def download(self, path: str) -> Path:
        """Download a file."""
        pass
    
    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file."""
        pass
    
    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        pass
    
    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get a URL for the file."""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str) -> List[str]:
        """List files with a given prefix."""
        pass


class LocalStorage(StorageInterface):
    """Local file system storage implementation."""
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create required directories
        self._create_directory_structure()
    
    def _create_directory_structure(self):
        """Create the complete directory structure."""
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
            
        logger.info(f"Created storage directory structure at {self.base_path}")
    
    async def upload(
        self,
        file: BinaryIO,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upload a file to local storage."""
        try:
            full_path = self.base_path / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            async with aiofiles.open(full_path, 'wb') as f:
                content = file.read() if hasattr(file, 'read') else file
                if isinstance(content, bytes):
                    await f.write(content)
                else:
                    await f.write(await content)
            
            # Save metadata if provided
            if metadata:
                metadata_path = full_path.with_suffix('.meta.json')
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata, default=str))
            
            # Log upload
            await self._log_operation('upload', str(path), metadata)
            
            logger.info(f"Uploaded file to {path}")
            return str(path)
            
        except Exception as e:
            logger.error(f"Failed to upload file to {path}: {e}")
            raise
    
    async def download(self, path: str) -> Path:
        """Get file path for download."""
        full_path = self.base_path / path
        
        if not await self.exists(path):
            raise HTTPException(404, "File not found")
        
        return full_path
    
    async def delete(self, path: str) -> bool:
        """Delete a file from local storage."""
        try:
            full_path = self.base_path / path
            
            if full_path.is_file():
                await aiofiles.os.remove(full_path)
                
                # Remove metadata if exists
                metadata_path = full_path.with_suffix('.meta.json')
                if metadata_path.exists():
                    await aiofiles.os.remove(metadata_path)
                
                # Log deletion
                await self._log_operation('delete', str(path))
                
                logger.info(f"Deleted file {path}")
                return True
                
            return False
            
        except Exception as e:
            await self._log_error('delete', str(path), str(e))
            return False
    
    async def exists(self, path: str) -> bool:
        """Check if file exists."""
        full_path = self.base_path / path
        return full_path.exists()
    
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get URL for file (local returns path)."""
        # In local mode, return a path that can be served by FastAPI
        return f"/media/{path}"
    
    async def list_files(self, prefix: str) -> List[str]:
        """List files with given prefix."""
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
        """Log storage operations."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "path": path,
                "metadata": metadata
            }
            
            log_dir = self.base_path / "../logs/storage"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{operation}s.log"
            
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(log_entry, default=str) + '\n')
        except Exception as e:
            logger.warning(f"Failed to log operation: {e}")
    
    async def _log_error(self, operation: str, path: str, error: str):
        """Log storage errors."""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "operation": operation,
                "path": path,
                "error": error
            }
            
            log_dir = self.base_path / "../logs/storage"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "errors.log"
            
            async with aiofiles.open(log_file, 'a') as f:
                await f.write(json.dumps(log_entry, default=str) + '\n')
        except Exception as e:
            logger.warning(f"Failed to log error: {e}")
    
    def cleanup_path(self, path: str) -> str:
        """Sanitize file path to prevent traversal attacks."""
        # Remove any parent directory references
        path = path.replace('../', '').replace('..\\', '')
        
        # Remove leading slashes
        path = path.lstrip('/').lstrip('\\')
        
        # Ensure path doesn't start with system directories
        forbidden_starts = ['/etc', '/var', '/usr', 'C:\\', 'C:/']
        for forbidden in forbidden_starts:
            if path.startswith(forbidden):
                raise ValueError(f"Invalid path: {path}")
        
        return path


# Storage factory
class StorageFactory:
    """Factory for creating storage instances based on configuration."""
    
    _instance: Optional[StorageInterface] = None
    
    @classmethod
    def get_storage(cls, storage_type: Optional[str] = None) -> StorageInterface:
        """Get or create storage instance."""
        if cls._instance is None:
            if not storage_type:
                storage_type = os.getenv('STORAGE_TYPE', 'local')
            
            if storage_type == 'local':
                cls._instance = LocalStorage(
                    base_path=os.getenv('LOCAL_STORAGE_PATH', 'uploads')
                )
            # Future: Add S3Storage, AzureStorage here
            else:
                raise ValueError(f"Unknown storage type: {storage_type}")
        
        return cls._instance


# Dependency for FastAPI
def get_storage() -> StorageInterface:
    """FastAPI dependency to get storage instance."""
    return StorageFactory.get_storage()