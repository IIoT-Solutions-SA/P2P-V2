"""Custom exception handlers for the P2P Sandbox backend."""

from fastapi import Request, HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


class NotFoundException(FastAPIHTTPException):
    """Exception for when a resource is not found."""
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=404, detail=detail)


class ForbiddenException(FastAPIHTTPException):
    """Exception for when access is forbidden."""
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class BadRequestException(FastAPIHTTPException):
    """Exception for bad requests."""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(FastAPIHTTPException):
    """Exception for unauthorized access."""
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "type": "http_error"
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
            "type": "validation_error"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    from app.core.config import settings
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "type": "server_error"
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": "server_error"
        }
    )