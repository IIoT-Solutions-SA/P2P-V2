"""Database connection and session management."""

from typing import AsyncGenerator
import asyncpg
from pymongo import AsyncMongoClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# PostgreSQL with SQLAlchemy + AsyncPG
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=20,  # Number of connections to maintain in the pool
    max_overflow=10,  # Maximum overflow connections allowed
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# MongoDB with PyMongo Async
mongo_client: AsyncMongoClient | None = None
mongodb = None  # Will be an AsyncDatabase instance


async def init_db():
    """Initialize database connections during app startup."""
    global mongo_client, mongodb
    
    try:
        # Initialize MongoDB connection
        mongo_client = AsyncMongoClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10,
            maxIdleTimeMS=60000,  # Close idle connections after 1 minute
            serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
        )
        
        # Verify MongoDB connection
        await mongo_client.admin.command('ping')
        mongodb = mongo_client[settings.MONGODB_DB_NAME]
        logger.info("MongoDB connection established successfully")
        
        # Test PostgreSQL connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda x: x.execute("SELECT 1"))
        logger.info("PostgreSQL connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")
        raise


async def close_db():
    """Close database connections during app shutdown."""
    global mongo_client
    
    try:
        # Close MongoDB connection
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB connection closed")
        
        # Close PostgreSQL connections
        await engine.dispose()
        logger.info("PostgreSQL connection pool closed")
        
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Dependency to get PostgreSQL session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async SQLAlchemy session.
    Ensures the session is properly closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Dependency to get MongoDB database
async def get_mongodb():
    """
    Dependency to get MongoDB database instance.
    Raises exception if not initialized.
    """
    if mongodb is None:
        raise RuntimeError("MongoDB is not initialized")
    return mongodb


# Dependency to get raw AsyncPG connection (for advanced use cases)
async def get_asyncpg_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Get a raw asyncpg connection for advanced PostgreSQL operations.
    Use this for operations that need PostgreSQL-specific features.
    """
    conn = await asyncpg.connect(
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    try:
        yield conn
    finally:
        await conn.close()


# Health check functions
async def check_postgres_health() -> dict:
    """Check PostgreSQL connection health."""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            result.scalar()
        return {"status": "healthy", "database": "postgresql"}
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return {"status": "unhealthy", "database": "postgresql", "error": str(e)}


async def check_mongodb_health() -> dict:
    """Check MongoDB connection health."""
    try:
        if mongo_client:
            await mongo_client.admin.command('ping')
            return {"status": "healthy", "database": "mongodb"}
        else:
            return {"status": "unhealthy", "database": "mongodb", "error": "Not initialized"}
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return {"status": "unhealthy", "database": "mongodb", "error": str(e)}