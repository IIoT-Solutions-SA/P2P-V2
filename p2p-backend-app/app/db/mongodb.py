"""MongoDB connection and database management using Motor async driver."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, TEXT
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager using Motor async driver."""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB and initialize database."""
        try:
            # Get MongoDB URL from environment
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            database_name = os.getenv("MONGO_DB_NAME", "p2p_sandbox")
            
            # Create Motor client
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                maxPoolSize=10,
                minPoolSize=2,
                serverSelectionTimeoutMS=5000
            )
            
            # Get database
            cls.database = cls.client[database_name]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB at {mongodb_url}")
            
            # Create indexes
            await cls.create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    async def create_indexes(cls):
        """Create indexes for all collections."""
        try:
            # Use Cases collection indexes
            use_cases = cls.database.use_cases
            
            # Text search index for full-text search
            await use_cases.create_index([
                ("title", TEXT),
                ("description", TEXT),
                ("challenge", TEXT),
                ("solution", TEXT),
                ("tags", TEXT)
            ])
            
            # Single field indexes for filtering
            await use_cases.create_index([("organization_id", ASCENDING)])
            await use_cases.create_index([("status", ASCENDING)])
            await use_cases.create_index([("category", ASCENDING)])
            await use_cases.create_index([("industry", ASCENDING)])
            await use_cases.create_index([("created_at", DESCENDING)])
            await use_cases.create_index([("published_at", DESCENDING)])
            await use_cases.create_index([("metrics.views", DESCENDING)])
            await use_cases.create_index([("metrics.likes", DESCENDING)])
            await use_cases.create_index([("verification.verified", ASCENDING)])
            await use_cases.create_index([("featured.is_featured", ASCENDING)])
            
            # Compound indexes for common queries
            await use_cases.create_index([
                ("status", ASCENDING),
                ("organization_id", ASCENDING),
                ("created_at", DESCENDING)
            ])
            
            await use_cases.create_index([
                ("status", ASCENDING),
                ("category", ASCENDING),
                ("published_at", DESCENDING)
            ])
            
            # Use Case Drafts collection indexes
            drafts = cls.database.use_case_drafts
            await drafts.create_index([("user_id", ASCENDING)])
            await drafts.create_index([("organization_id", ASCENDING)])
            await drafts.create_index([("expires_at", ASCENDING)])  # For TTL cleanup
            
            # Use Case Views collection indexes (for analytics)
            views = cls.database.use_case_views
            await views.create_index([("use_case_id", ASCENDING)])
            await views.create_index([("viewer_id", ASCENDING)])
            await views.create_index([("organization_id", ASCENDING)])
            await views.create_index([("viewed_at", DESCENDING)])
            
            # Compound index for analytics queries
            await views.create_index([
                ("use_case_id", ASCENDING),
                ("viewed_at", DESCENDING)
            ])
            
            # Use Case Likes collection
            likes = cls.database.use_case_likes
            await likes.create_index([("use_case_id", ASCENDING)])
            await likes.create_index([("user_id", ASCENDING)])
            await likes.create_index([
                ("use_case_id", ASCENDING),
                ("user_id", ASCENDING)
            ], unique=True)  # Prevent duplicate likes
            
            # Use Case Saves collection
            saves = cls.database.use_case_saves
            await saves.create_index([("use_case_id", ASCENDING)])
            await saves.create_index([("user_id", ASCENDING)])
            await saves.create_index([
                ("use_case_id", ASCENDING),
                ("user_id", ASCENDING)
            ], unique=True)  # Prevent duplicate saves
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {e}")
            raise
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get the database instance."""
        if not cls.database:
            raise RuntimeError("MongoDB is not connected. Call connect() first.")
        return cls.database
    
    @classmethod
    def get_collection(cls, name: str):
        """Get a collection by name."""
        if not cls.database:
            raise RuntimeError("MongoDB is not connected. Call connect() first.")
        return cls.database[name]


# Dependency for FastAPI
async def get_mongodb() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get MongoDB database instance."""
    return MongoDB.get_database()