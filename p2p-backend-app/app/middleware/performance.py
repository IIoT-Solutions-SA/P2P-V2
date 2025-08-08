"""Performance monitoring middleware."""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from app.services.performance import performance_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance."""
    
    def __init__(self, app, slow_request_threshold: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # milliseconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance."""
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            # Record metrics
            performance_service.record_api_call(response_time_ms)
            
            # Log slow requests
            if response_time_ms > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} - "
                    f"{response_time_ms:.2f}ms"
                )
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            # Record error
            performance_service.record_error()
            
            # Calculate response time even for errors
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            performance_service.record_api_call(response_time_ms)
            
            raise e


class DatabaseMonitoringMiddleware:
    """Middleware to monitor database queries."""
    
    def __init__(self):
        self.query_count = 0
    
    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Called before a database query is executed."""
        context._query_start_time = time.time()
        performance_service.record_db_query()
        self.query_count += 1
    
    def after_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        """Called after a database query is executed."""
        if hasattr(context, '_query_start_time'):
            execution_time = time.time() - context._query_start_time
            
            # Log slow queries
            if execution_time > 0.5:  # 500ms threshold
                logger.warning(
                    f"Slow query detected: {execution_time:.3f}s - "
                    f"{statement[:100]}..."
                )
    
    def get_query_count(self) -> int:
        """Get total query count."""
        return self.query_count
    
    def reset_query_count(self) -> None:
        """Reset query count."""
        self.query_count = 0


# Global database monitoring instance
db_monitor = DatabaseMonitoringMiddleware()