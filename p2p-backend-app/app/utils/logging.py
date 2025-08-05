"""Logging utilities for the application."""

import logging
from typing import Any, Dict, Optional
from functools import wraps
import time
import asyncio

from app.core.logging import get_logger, user_id_context, organization_id_context


def log_function_call(logger: Optional[logging.Logger] = None):
    """Decorator to log function calls with timing."""
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            logger.debug(f"Calling {func_name}", extra={"function": func_name, "args": args, "kwargs": kwargs})
            
            try:
                result = func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.debug(
                    f"Function {func_name} completed",
                    extra={"function": func_name, "duration_ms": duration_ms}
                )
                
                return result
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.error(
                    f"Function {func_name} failed",
                    extra={"function": func_name, "duration_ms": duration_ms, "error": str(e)},
                    exc_info=True
                )
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            logger.debug(f"Calling async {func_name}", extra={"function": func_name})
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.debug(
                    f"Async function {func_name} completed",
                    extra={"function": func_name, "duration_ms": duration_ms}
                )
                
                return result
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                
                logger.error(
                    f"Async function {func_name} failed",
                    extra={"function": func_name, "duration_ms": duration_ms, "error": str(e)},
                    exc_info=True
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def log_database_operation(operation: str, table: str, **kwargs):
    """Log database operations with context."""
    logger = get_logger("app.db")
    
    extra = {
        "operation": operation,
        "table": table,
        **kwargs
    }
    
    # Add user context if available
    if user_id := user_id_context.get():
        extra["user_id"] = user_id
    
    if org_id := organization_id_context.get():
        extra["organization_id"] = org_id
    
    logger.info(f"Database operation: {operation} on {table}", extra=extra)


def log_api_error(endpoint: str, error: Exception, status_code: int, **kwargs):
    """Log API errors with context."""
    logger = get_logger("app.api")
    
    extra = {
        "endpoint": endpoint,
        "status_code": status_code,
        "error_type": type(error).__name__,
        "error_message": str(error),
        **kwargs
    }
    
    logger.error(f"API error at {endpoint}", extra=extra, exc_info=True)


def log_authentication_event(event_type: str, user_email: Optional[str] = None, success: bool = True, **kwargs):
    """Log authentication-related events."""
    logger = get_logger("app.auth")
    
    extra = {
        "event_type": event_type,
        "success": success,
        **kwargs
    }
    
    if user_email:
        extra["user_email"] = user_email
    
    level = logging.INFO if success else logging.WARNING
    message = f"Authentication event: {event_type} {'succeeded' if success else 'failed'}"
    
    logger.log(level, message, extra=extra)


def log_business_event(event_type: str, entity_type: str, entity_id: str, **kwargs):
    """Log business domain events."""
    logger = get_logger("app.business")
    
    extra = {
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        **kwargs
    }
    
    # Add user context
    if user_id := user_id_context.get():
        extra["user_id"] = user_id
    
    if org_id := organization_id_context.get():
        extra["organization_id"] = org_id
    
    logger.info(f"Business event: {event_type} for {entity_type}", extra=extra)