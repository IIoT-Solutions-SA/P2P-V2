# Story 4: Database Configuration and Connections

## Story Details
**Epic**: Epic 1 - Project Foundation & Development Environment  
**Story Points**: 5  
**Priority**: High  
**Dependencies**: Story 3 (Backend API Setup)

## User Story
**As a** developer  
**I want** properly configured databases with connection pooling  
**So that** I can store and retrieve application data efficiently

## Acceptance Criteria
- [ ] PostgreSQL container configured with initial database and user
- [ ] MongoDB container configured with authentication
- [ ] Database connection pooling implemented for both databases
- [ ] Alembic migration system configured for PostgreSQL
- [ ] Initial database schemas created
- [ ] Basic CRUD operations tested for both databases
- [ ] Database health checks integrated into API
- [ ] Development seed data scripts created
- [ ] Connection retry logic implemented

## Technical Specifications

### 1. Database Dependencies

Update backend/requirements.txt:
```
# Existing dependencies...

# Database
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
motor==3.3.2
beanie==1.24.0
```

### 2. Database Configuration

#### app/core/database.py
```python
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
            from app.models.mongo_models import User, ForumPost, UseCase
            await init_beanie(
                database=self.mongo_db,
                document_models=[User, ForumPost, UseCase]
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
```

### 3. PostgreSQL Models

#### app/models/pg_models.py
```python
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

class UserSession(Base, TimestampMixin):
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
```

### 4. MongoDB Models

#### app/models/mongo_models.py
```python
from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict
import pymongo

class User(Document):
    email: Indexed(EmailStr, unique=True)
    name: str
    role: str = "user"
    industry_sector: Optional[str] = None
    location: Optional[str] = None
    expertise_tags: List[str] = Field(default_factory=list)
    verified: bool = False
    language_preference: str = "en"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            [("email", pymongo.ASCENDING)],
            [("expertise_tags", pymongo.ASCENDING)]
        ]

class ForumPost(Document):
    author_id: str
    title: str
    content: str
    category: str
    tags: List[str] = Field(default_factory=list)
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    best_answer_id: Optional[str] = None
    status: str = "open"  # open, resolved, closed
    view_count: int = 0
    reply_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_posts"
        indexes = [
            [("category", pymongo.ASCENDING)],
            [("tags", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]

class ForumReply(Document):
    post_id: str
    author_id: str
    content: str
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    upvotes: int = 0
    is_best_answer: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "forum_replies"
        indexes = [
            [("post_id", pymongo.ASCENDING)],
            [("created_at", pymongo.ASCENDING)]
        ]

class UseCase(Document):
    submitted_by: str
    title: str
    problem_statement: str
    solution_description: str
    vendor_info: Optional[Dict[str, str]] = None
    cost_estimate: Optional[str] = None
    impact_metrics: Dict[str, str] = Field(default_factory=dict)
    industry_tags: List[str] = Field(default_factory=list)
    region: str
    location: Dict[str, float]  # {"lat": 24.7136, "lng": 46.6753}
    bookmarks: List[str] = Field(default_factory=list)
    published: bool = False
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "use_cases"
        indexes = [
            [("industry_tags", pymongo.ASCENDING)],
            [("region", pymongo.ASCENDING)],
            [("location", pymongo.GEO2D)]
        ]
```

### 5. Alembic Configuration

#### alembic.ini
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://p2p_user:changeme@localhost:5432/p2p_sandbox

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 88

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### alembic/env.py
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.database import Base
from app.models.pg_models import *  # Import all models
from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 6. Database Services

#### app/services/database_service.py
```python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.pg_models import User as PGUser
from app.models.mongo_models import User as MongoUser, ForumPost, UseCase
from uuid import UUID
from datetime import datetime

class UserService:
    @staticmethod
    async def create_user_pg(db: AsyncSession, email: str, name: str) -> PGUser:
        """Create user in PostgreSQL"""
        user = PGUser(email=email, name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def create_user_mongo(email: str, name: str, **kwargs) -> MongoUser:
        """Create user in MongoDB"""
        user = MongoUser(email=email, name=name, **kwargs)
        await user.create()
        return user
    
    @staticmethod
    async def get_user_by_email_pg(db: AsyncSession, email: str) -> Optional[PGUser]:
        """Get user by email from PostgreSQL"""
        result = await db.execute(select(PGUser).where(PGUser.email == email))
        return result.scalar_one_or_none()

class ForumService:
    @staticmethod
    async def create_post(
        author_id: str,
        title: str,
        content: str,
        category: str,
        tags: List[str] = None
    ) -> ForumPost:
        """Create a new forum post"""
        post = ForumPost(
            author_id=author_id,
            title=title,
            content=content,
            category=category,
            tags=tags or []
        )
        await post.create()
        return post
    
    @staticmethod
    async def get_posts_by_category(category: str, limit: int = 20) -> List[ForumPost]:
        """Get posts by category"""
        posts = await ForumPost.find(
            ForumPost.category == category
        ).sort(-ForumPost.created_at).limit(limit).to_list()
        return posts

class UseCaseService:
    @staticmethod
    async def create_use_case(data: dict) -> UseCase:
        """Create a new use case"""
        use_case = UseCase(**data)
        await use_case.create()
        return use_case
    
    @staticmethod
    async def get_use_cases_by_region(region: str) -> List[UseCase]:
        """Get use cases by region"""
        use_cases = await UseCase.find(
            UseCase.region == region,
            UseCase.published == True
        ).to_list()
        return use_cases
```

### 7. Database Initialization Scripts

#### backend/scripts/init_db.py
```python
import asyncio
from app.core.database import db_manager, Base
from app.core.config import settings
from app.models.pg_models import *
from app.models.mongo_models import *
from app.core.logging import logger

async def init_databases():
    """Initialize both databases"""
    try:
        # Initialize PostgreSQL
        await db_manager.init_postgres()
        logger.info("PostgreSQL initialized successfully")
        
        # Initialize MongoDB
        await db_manager.init_mongodb()
        logger.info("MongoDB initialized successfully")
        
        # Create indexes
        await create_indexes()
        
        logger.info("All databases initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await db_manager.close_connections()

async def create_indexes():
    """Create additional indexes"""
    # MongoDB indexes are created automatically by Beanie
    logger.info("Indexes created successfully")

if __name__ == "__main__":
    asyncio.run(init_databases())
```

#### backend/scripts/seed_db.py
```python
import asyncio
from app.core.database import db_manager
from app.services.database_service import UserService, ForumService, UseCaseService
from app.core.logging import logger
import random

async def seed_data():
    """Seed development data"""
    await db_manager.init_postgres()
    await db_manager.init_mongodb()
    
    try:
        # Create test users
        test_users = [
            {"email": "ahmed@example.com", "name": "Ahmed Al-Faisal", "role": "factory_owner"},
            {"email": "mariam@example.com", "name": "Mariam Al-Zahrani", "role": "engineer"},
            {"email": "youssef@example.com", "name": "Youssef Al-Qahtani", "role": "manager"}
        ]
        
        created_users = []
        for user_data in test_users:
            user = await UserService.create_user_mongo(**user_data)
            created_users.append(user)
            logger.info(f"Created user: {user.name}")
        
        # Create test forum posts
        categories = ["technical", "business", "training", "general"]
        for i in range(10):
            post = await ForumService.create_post(
                author_id=str(random.choice(created_users).id),
                title=f"Test Post {i+1}",
                content=f"This is test content for post {i+1}",
                category=random.choice(categories),
                tags=["test", "development"]
            )
            logger.info(f"Created post: {post.title}")
        
        # Create test use cases
        regions = ["Riyadh", "Jeddah", "Dammam"]
        for i in range(5):
            use_case = await UseCaseService.create_use_case({
                "submitted_by": str(random.choice(created_users).id),
                "title": f"Digital Transformation Case {i+1}",
                "problem_statement": "Legacy systems causing inefficiencies",
                "solution_description": "Implementation of modern ERP system",
                "region": random.choice(regions),
                "location": {"lat": 24.7136, "lng": 46.6753},
                "industry_tags": ["manufacturing", "4IR"],
                "published": True
            })
            logger.info(f"Created use case: {use_case.title}")
        
        logger.info("Seed data created successfully")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise
    finally:
        await db_manager.close_connections()

if __name__ == "__main__":
    asyncio.run(seed_data())
```

### 8. Update Health Check

Update app/api/v1/endpoints/health.py:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db, db_manager
from app.schemas.common import HealthResponse
from datetime import datetime
import psutil

router = APIRouter()

async def check_postgres(db: AsyncSession) -> str:
    try:
        await db.execute(text("SELECT 1"))
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_mongodb() -> str:
    try:
        await db_manager.mongo_client.admin.command('ping')
        return "healthy"
    except Exception:
        return "unhealthy"

@router.get("/", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check the health status of the API and databases"""
    pg_status = await check_postgres(db)
    mongo_status = await check_mongodb()
    
    return HealthResponse(
        status="healthy" if pg_status == "healthy" and mongo_status == "healthy" else "degraded",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime=psutil.boot_time(),
        checks={
            "api": "healthy",
            "postgresql": pg_status,
            "mongodb": mongo_status
        }
    )
```

## Implementation Steps

1. **Install Database Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Initialize Alembic**
   ```bash
   alembic init alembic
   # Replace alembic.ini and env.py with provided configurations
   ```

3. **Create Initial Migration**
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

4. **Initialize Databases**
   ```bash
   python scripts/init_db.py
   ```

5. **Seed Development Data**
   ```bash
   python scripts/seed_db.py
   ```

## Testing Checklist
- [ ] PostgreSQL connection successful
- [ ] MongoDB connection successful
- [ ] Alembic migrations run without errors
- [ ] CRUD operations work for both databases
- [ ] Connection pooling functioning
- [ ] Retry logic works when database is down
- [ ] Health checks report correct status
- [ ] Seed data created successfully

## Docker Commands (Preview for Story 6)
```bash
# PostgreSQL
docker run -d \
  --name p2p-postgres \
  -e POSTGRES_DB=p2p_sandbox \
  -e POSTGRES_USER=p2p_user \
  -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 \
  postgres:16-alpine

# MongoDB
docker run -d \
  --name p2p-mongodb \
  -e MONGO_INITDB_ROOT_USERNAME=p2p_user \
  -e MONGO_INITDB_ROOT_PASSWORD=changeme \
  -e MONGO_INITDB_DATABASE=p2p_sandbox \
  -p 27017:27017 \
  mongo:7
```

## Dependencies
- Story 3 must be completed (Backend API setup)
- Docker must be installed for database containers

## Notes
- Always use connection pooling for production
- Implement proper indexing strategies
- Regular backups should be configured
- Monitor connection pool usage