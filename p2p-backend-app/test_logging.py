"""Test script to verify logging configuration."""

import asyncio
import logging
import sys
sys.path.insert(0, '.')

from app.core.logging import setup_logging, get_logger, request_id_context
from app.utils.logging import log_function_call, log_database_operation, log_business_event


# Setup logging
setup_logging()

# Get loggers
logger = get_logger(__name__)
app_logger = get_logger("app.test")


@log_function_call()
def test_sync_function(x: int, y: int) -> int:
    """Test synchronous function with logging."""
    result = x + y
    logger.info(f"Calculated sum: {result}")
    return result


@log_function_call()
async def test_async_function(name: str) -> str:
    """Test asynchronous function with logging."""
    await asyncio.sleep(0.1)
    greeting = f"Hello, {name}!"
    logger.info(f"Generated greeting: {greeting}")
    return greeting


async def test_logging_features():
    """Test various logging features."""
    # Test basic logging
    logger.info("Starting logging tests")
    logger.debug("Debug message - should appear in development")
    logger.warning("Warning message")
    
    # Test with request context
    request_id_context.set("test-request-123")
    logger.info("Message with request ID")
    
    # Test function decorators
    result = test_sync_function(5, 3)
    logger.info(f"Sync function result: {result}")
    
    greeting = await test_async_function("P2P Sandbox")
    logger.info(f"Async function result: {greeting}")
    
    # Test database operation logging
    log_database_operation("INSERT", "users", user_id="123", rows_affected=1)
    
    # Test business event logging
    log_business_event("user_created", "user", "123", organization_id="456")
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.error("Caught test error", exc_info=True)
    
    # Clear context
    request_id_context.set(None)
    
    logger.info("Logging tests completed")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_logging_features())