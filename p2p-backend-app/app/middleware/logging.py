"""Logging middleware for request tracking."""

import uuid
import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import request_id_context, user_id_context, organization_id_context


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and tracking."""
    
    def __init__(self, app: ASGIApp, service_name: str = "p2p-backend"):
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add logging context."""
        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set request ID in context
        request_id_context.set(request_id)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
                exc_info=True
            )
            
            raise
        
        finally:
            # Clear context
            request_id_context.set(None)
            user_id_context.set(None)
            organization_id_context.set(None)


class UserContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract user context from authenticated requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract user information from request and set context."""
        # This will be implemented when we add authentication
        # For now, just pass through
        
        # Example of how it will work:
        # if hasattr(request.state, "user"):
        #     user_id_context.set(str(request.state.user.id))
        #     organization_id_context.set(str(request.state.user.organization_id))
        
        response = await call_next(request)
        return response