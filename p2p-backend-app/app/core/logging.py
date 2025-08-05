"""Structured logging configuration for P2P Sandbox backend."""

import logging
import sys
from typing import Any, Dict, Optional
import json
from datetime import datetime
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

from app.core.config import settings


# Context variables for request tracking
request_id_context: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_context: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
organization_id_context: ContextVar[Optional[str]] = ContextVar("organization_id", default=None)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that adds contextual information."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Add service info
        log_record["service"] = settings.PROJECT_NAME
        log_record["version"] = settings.VERSION
        log_record["environment"] = settings.ENVIRONMENT
        
        # Add context from context vars
        if request_id := request_id_context.get():
            log_record["request_id"] = request_id
        
        if user_id := user_id_context.get():
            log_record["user_id"] = user_id
            
        if org_id := organization_id_context.get():
            log_record["organization_id"] = org_id
        
        # Add error details if exception
        if record.exc_info:
            log_record["error_type"] = record.exc_info[0].__name__
            log_record["error_message"] = str(record.exc_info[1])
        
        # Remove internal fields
        log_record.pop("message", None)
        log_record.pop("msg", None)


class HealthCheckFilter(logging.Filter):
    """Filter to reduce noise from health check endpoints."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out health check logs unless they're errors."""
        if record.levelno >= logging.ERROR:
            return True
            
        # Check if this is a health check request
        message = record.getMessage()
        if "/health" in message or "/api/v1/health" in message:
            return False
            
        return True


def setup_logging() -> None:
    """Configure structured logging for the application."""
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter for production, readable format for development
    if settings.ENVIRONMENT == "production":
        formatter = CustomJsonFormatter(
            "%(levelname)s %(name)s %(funcName)s %(lineno)d %(message)s"
        )
    else:
        # Human-readable format for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    
    # Add health check filter
    console_handler.addFilter(HealthCheckFilter())
    
    # Configure root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Configure specific loggers
    loggers_config = {
        "uvicorn": settings.LOG_LEVEL.upper(),
        "uvicorn.error": settings.LOG_LEVEL.upper(),
        "uvicorn.access": "WARNING" if settings.ENVIRONMENT == "production" else "INFO",
        "sqlalchemy.engine": "WARNING",
        "sqlalchemy.pool": "WARNING",
        "asyncpg": "WARNING",
        "motor": "WARNING",
        "supertokens": "INFO",
        "app": settings.LOG_LEVEL.upper(),
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = True
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "environment": settings.ENVIRONMENT,
            "json_logs": settings.ENVIRONMENT == "production"
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)