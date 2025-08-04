from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import AsyncGenerator, Optional
from app.core.config import settings
from app.core.logging import logger
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

# PostgreSQL Setup
Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.pg_engine = None
        self.pg_session_factory = None
        self.mongo_client = None
        self.mongo_db = None
        
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def init_postgres(self):
        """Initialize PostgreSQL connection with retry logic"""
        try:
            self.pg_engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.DEBUG,
                pool_size=20,
                max_overflow=40,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            self.pg_session_factory = async_sessionmaker(
                self.pg_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.pg_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("PostgreSQL connection established")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def init_mongodb(self):
        """Initialize MongoDB connection with retry logic"""
        try:
            self.mongo_client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=20,
                minPoolSize=5
            )
            
            self.mongo_db = self.mongo_client.p2p_sandbox
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            
            # Initialize Beanie with document models
            from app.models.mongo_models import User, ForumPost, UseCase, ForumReply
            await init_beanie(
                database=self.mongo_db,
                document_models=[User, ForumPost, ForumReply, UseCase]
            )
            
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    async def close_connections(self):
        """Close all database connections"""
        if self.pg_engine:
            await self.pg_engine.dispose()
        if self.mongo_client:
            self.mongo_client.close()

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for PostgreSQL sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.pg_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()