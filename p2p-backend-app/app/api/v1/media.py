"""Media file serving endpoints."""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from starlette.requests import Request
import mimetypes
import logging

from app.services.storage import get_storage, StorageInterface

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{file_path:path}")
async def serve_media_file(
    file_path: str,
    request: Request,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Serve uploaded media files.
    
    **Features:**
    - Serves files with proper MIME types
    - Security checks to prevent path traversal
    - Proper caching headers
    - Support for range requests (partial content)
    
    **Security:**
    - Path sanitization to prevent directory traversal
    - Access control (files are served based on storage permissions)
    - Content-Type validation
    """
    # Security: Prevent path traversal
    if '..' in file_path or file_path.startswith('/'):
        raise HTTPException(403, "Invalid file path")
    
    try:
        # Get file path from storage
        local_path = await storage.download(file_path)
        
        if not local_path.exists():
            raise HTTPException(404, "File not found")
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(local_path))
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Get file stats
        stat_result = local_path.stat()
        
        # Check if client requests a range
        range_header = request.headers.get('range')
        
        # Prepare headers
        headers = {
            'Cache-Control': 'public, max-age=3600',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'SAMEORIGIN',
            'Accept-Ranges': 'bytes',
            'Content-Length': str(stat_result.st_size)
        }
        
        # Handle range requests for large files (videos, etc.)
        if range_header and content_type.startswith(('video/', 'audio/')):
            return _handle_range_request(local_path, range_header, content_type, stat_result.st_size)
        
        # Return full file
        return FileResponse(
            local_path,
            media_type=content_type,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        raise HTTPException(500, "Internal server error")


@router.get("/download/{file_path:path}")
async def download_media_file(
    file_path: str,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Force download of a media file with Content-Disposition header.
    
    **Use cases:**
    - Download documents and files
    - Force download instead of inline viewing
    - Preserve original filename
    """
    # Security: Prevent path traversal
    if '..' in file_path or file_path.startswith('/'):
        raise HTTPException(403, "Invalid file path")
    
    try:
        # Get file path from storage
        local_path = await storage.download(file_path)
        
        if not local_path.exists():
            raise HTTPException(404, "File not found")
        
        # Force download with Content-Disposition
        return FileResponse(
            local_path,
            media_type='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{local_path.name}"',
                'X-Content-Type-Options': 'nosniff'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_path}: {e}")
        raise HTTPException(500, "Internal server error")


def _handle_range_request(file_path: Path, range_header: str, content_type: str, file_size: int):
    """Handle HTTP range requests for large files."""
    try:
        # Parse range header (e.g., "bytes=0-1023")
        range_match = range_header.replace('bytes=', '').split('-')
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Validate range
        if start >= file_size or end >= file_size or start > end:
            raise HTTPException(416, "Range not satisfiable")
        
        # Calculate content length
        content_length = end - start + 1
        
        # Read file chunk
        with open(file_path, 'rb') as f:
            f.seek(start)
            content = f.read(content_length)
        
        # Return partial content response
        from fastapi import Response
        
        return Response(
            content=content,
            status_code=206,  # Partial Content
            headers={
                'Content-Type': content_type,
                'Content-Length': str(content_length),
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes'
            }
        )
        
    except ValueError:
        raise HTTPException(400, "Invalid range header")
    except Exception as e:
        logger.error(f"Error handling range request: {e}")
        raise HTTPException(500, "Internal server error")