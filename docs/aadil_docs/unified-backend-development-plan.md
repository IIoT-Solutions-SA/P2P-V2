# P2P Sandbox Unified Backend Development Plan

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Container-First Development Approach](#container-first-development-approach)
4. [Backend Architecture & Project Structure](#backend-architecture--project-structure)
5. [Database Design with SQLModel](#database-design-with-sqlmodel)
6. [API Design & Endpoints](#api-design--endpoints)
7. [Authentication with SuperTokens](#authentication-with-supertokens)
8. [Async Programming Implementation](#async-programming-implementation)
9. [Development Workflow](#development-workflow)
10. [Implementation Roadmap](#implementation-roadmap)
11. [Testing Strategy](#testing-strategy)
12. [Production Deployment](#production-deployment)

## Project Overview

The P2P Sandbox platform is a peer-driven collaboration platform for Saudi Arabia's industrial SMEs, built with modern async architecture for real-time features and high performance.

### Key Features
- **Real-time Forum Discussions**: Live updates via WebSockets
- **Use Case Management**: Structured knowledge sharing with media
- **Private Messaging**: Secure peer-to-peer communication
- **File Storage**: Document and media sharing
- **Activity Dashboards**: Real-time analytics and insights

### Performance Goals
- Handle 1000+ concurrent users
- Sub-second API response times
- Real-time updates under 100ms latency
- 99.9% uptime reliability

## Technology Stack

### Core Technologies
- **Language**: Python 3.11+
- **Framework**: FastAPI with full async/await
- **ORM**: SQLModel (SQLAlchemy + Pydantic combined)
- **Databases**: 
  - PostgreSQL (primary data, async with AsyncPG)
  - MongoDB (document storage, async with Motor)
  - Redis (caching & sessions)
- **Authentication**: SuperTokens
- **File Storage**: AWS S3 / Azure Blob Storage
- **Real-time**: WebSockets
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest with async support

### Key Dependencies
```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
motor==3.3.2
redis[hiredis]==5.0.1
supertokens-python==0.17.0
pydantic==2.5.0
pydantic-settings==2.1.0
alembic==1.12.1
python-multipart==0.0.6
boto3==1.29.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
ruff==0.1.9
mypy==1.8.0
```

## Container-First Development Approach

### Philosophy
Everything runs in containers from day one - no local installations required. This ensures:
- Consistent environments across all developers
- Easy onboarding (< 15 minutes to full setup)
- Production parity from development
- Isolated testing environments

### Docker Compose Services Architecture
```yaml
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: ./p2p-backend-app
      dockerfile: Dockerfile.dev
    container_name: p2p-backend
    volumes:
      - ./p2p-backend-app:/app
      - /app/__pycache__
    ports:
      - "8000:8000"
      - "5678:5678"  # Debugger port
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - MONGODB_URL=mongodb://mongodb:27017/${MONGO_DB}
      - REDIS_URL=redis://redis:6379
      - SUPERTOKENS_CONNECTION_URI=http://supertokens:3567
    depends_on:
      postgres:
        condition: service_healthy
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - p2p-network

  # PostgreSQL with health checks
  postgres:
    image: postgres:15-alpine
    container_name: p2p-postgres
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - p2p-network

  # MongoDB
  mongodb:
    image: mongo:7
    container_name: p2p-mongodb
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - p2p-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: p2p-redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - p2p-network

  # SuperTokens
  supertokens:
    image: registry.supertokens.io/supertokens/supertokens-postgresql:7.0
    container_name: p2p-supertokens
    environment:
      - POSTGRESQL_CONNECTION_URI=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/supertokens
    ports:
      - "3567:3567"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - p2p-network

volumes:
  postgres_data:
  mongo_data:
  redis_data:

networks:
  p2p-network:
    driver: bridge
```

### Development Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
```

## Backend Architecture & Project Structure

```
p2p-backend-app/
├── docker-compose.yml          # Container orchestration
├── docker-compose.test.yml     # Test environment
├── Dockerfile                  # Production build
├── Dockerfile.dev              # Development build
├── .env.example                # Environment template
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── alembic.ini                 # Database migrations config
├── pytest.ini                  # Test configuration
├── mypy.ini                    # Type checking config
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Settings management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Common dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py         # API router aggregator
│   │       └── endpoints/
│   │           ├── auth.py    # Authentication endpoints
│   │           ├── users.py   # User management
│   │           ├── organizations.py
│   │           ├── forums.py  # Forum + WebSockets
│   │           ├── use_cases.py
│   │           ├── messages.py
│   │           ├── dashboard.py
│   │           └── search.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Core settings
│   │   ├── security.py        # Security utilities
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── websocket.py       # WebSocket manager
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py           # SQLModel base setup
│   │   ├── session.py        # Async sessions
│   │   └── init_db.py        # Database initialization
│   │
│   ├── models/               # SQLModel definitions
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── forum.py
│   │   ├── use_case.py
│   │   └── message.py
│   │
│   ├── schemas/              # Additional schemas
│   │   ├── __init__.py
│   │   ├── common.py         # Common responses
│   │   ├── auth.py           # Auth-specific
│   │   └── websocket.py      # WebSocket messages
│   │
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── forum.py
│   │   ├── use_case.py
│   │   ├── file_storage.py
│   │   └── email.py
│   │
│   └── tasks/                # Background tasks
│       ├── __init__.py
│       ├── email_tasks.py
│       └── file_tasks.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Test fixtures
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
│
├── alembic/
│   ├── versions/             # Migration files
│   └── env.py               # Migration environment
│
└── scripts/
    ├── init_db.py           # Database setup
    ├── seed_data.py         # Development data
    └── create_superuser.py  # Admin creation
```

## Database Design with SQLModel

### SQLModel Benefits
- Single model definition serves as both ORM model and API schema
- Full type hints and IDE support
- Automatic validation
- Seamless FastAPI integration

### Core Models

```python
# app/models/base.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# app/models/organization.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from .base import TimestampMixin

class OrganizationBase(SQLModel):
    name: str = Field(max_length=255)
    domain: str = Field(max_length=255, unique=True)
    industry: Optional[str] = Field(max_length=100, default=None)
    size: Optional[str] = Field(max_length=50, default=None)
    country: Optional[str] = Field(max_length=100, default=None)
    city: Optional[str] = Field(max_length=100, default=None)
    is_active: bool = True

class Organization(OrganizationBase, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    admin_user_id: Optional[UUID] = None
    
    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    forum_topics: List["ForumTopic"] = Relationship(back_populates="organization")

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    user_count: Optional[int] = 0

# app/models/user.py
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from .base import TimestampMixin

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    first_name: Optional[str] = Field(max_length=100, default=None)
    last_name: Optional[str] = Field(max_length=100, default=None)
    role: str = Field(default="member", max_length=50)
    is_active: bool = True
    is_verified: bool = False

class User(UserBase, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: Optional[UUID] = Field(foreign_key="organization.id")
    hashed_password: str
    last_login: Optional[datetime] = None
    
    # Relationships
    organization: Optional[Organization] = Relationship(back_populates="users")
    forum_topics: List["ForumTopic"] = Relationship(back_populates="author")

class UserCreate(UserBase):
    password: str
    organization_name: Optional[str] = None

class UserRead(UserBase):
    id: UUID
    organization_id: Optional[UUID]
    created_at: datetime

class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
```

### MongoDB Collections
```javascript
// Forum Posts
{
  _id: ObjectId,
  topic_id: "uuid",
  content: "rich text content",
  author_id: "uuid",
  attachments: [
    {
      type: "image|document",
      url: "s3_url",
      filename: "name",
      size: 1024
    }
  ],
  replies: [
    {
      id: "uuid",
      content: "reply content",
      author_id: "uuid",
      created_at: Date,
      is_best_answer: false,
      upvotes: ["user_id1", "user_id2"]
    }
  ],
  created_at: Date,
  updated_at: Date
}

// Use Cases
{
  _id: ObjectId,
  submission_id: "uuid",
  title: "Use case title",
  organization_id: "uuid",
  submitted_by: "uuid",
  industry: "Manufacturing",
  technology: ["AI", "IoT"],
  problem_statement: "detailed description",
  solution: "detailed solution",
  outcomes: {
    cost_savings: "20%",
    efficiency_gain: "30%",
    roi_timeline: "6 months"
  },
  vendor_info: {
    name: "Vendor Name",
    contact: "contact info"
  },
  media: [
    {
      type: "image|video",
      url: "s3_url",
      caption: "description"
    }
  ],
  location: {
    city: "Riyadh",
    coordinates: [24.7136, 46.6753]
  },
  tags: ["automation", "quality-control"],
  views: 0,
  created_at: Date,
  updated_at: Date
}
```

## API Design & Endpoints

### API Structure
```
Base URL: http://localhost:8000/api/v1

Authentication:
POST   /auth/signup              # Create organization + admin user
POST   /auth/login               # Email/password login
POST   /auth/logout              # End session
POST   /auth/refresh             # Refresh token
POST   /auth/verify-email        # Verify email
POST   /auth/reset-password      # Request reset

Users:
GET    /users/me                 # Current user profile
PATCH  /users/me                 # Update profile
GET    /users                    # List org users (admin)
POST   /users/invite             # Invite member (admin)
GET    /users/{id}               # Get user details
PATCH  /users/{id}               # Update user (admin)
DELETE /users/{id}               # Deactivate (admin)

Organizations:
GET    /organizations/current    # Current org details
PATCH  /organizations/current    # Update org (admin)
GET    /organizations/members    # List members
GET    /organizations/stats      # Statistics

Forums:
GET    /forums/topics            # List topics (paginated)
POST   /forums/topics            # Create topic
GET    /forums/topics/{id}       # Get topic + posts
PATCH  /forums/topics/{id}       # Update topic
DELETE /forums/topics/{id}       # Delete topic
POST   /forums/topics/{id}/pin   # Pin/unpin (admin)

WebSocket /ws/forum/{topic_id}   # Real-time updates

Use Cases:
GET    /use-cases                # List with filters
POST   /use-cases                # Submit new
GET    /use-cases/{id}           # Get details
PATCH  /use-cases/{id}           # Update
DELETE /use-cases/{id}           # Delete
POST   /use-cases/{id}/publish   # Publish draft
POST   /use-cases/{id}/media     # Upload media

Messages:
GET    /messages                 # List conversations
POST   /messages                 # Send message
GET    /messages/{user_id}       # Get conversation
PATCH  /messages/{id}/read       # Mark as read

Dashboard:
GET    /dashboard/stats          # Statistics
GET    /dashboard/activity       # Recent activity
GET    /dashboard/trending       # Trending content

Search:
GET    /search                   # Global search
GET    /search/users             # Search users
GET    /search/use-cases         # Search use cases
GET    /search/forums            # Search forums
```

### Example Endpoint Implementation
```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.api import deps
from app.models.user import User, UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter()

@router.get("/me", response_model=UserRead)
async def get_current_user(
    current_user: User = Depends(deps.get_current_user)
) -> UserRead:
    """Get current user profile"""
    return UserRead.model_validate(current_user)

@router.patch("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
    session: AsyncSession = Depends(deps.get_session)
) -> UserRead:
    """Update current user profile"""
    user_service = UserService(session)
    updated_user = await user_service.update(current_user.id, user_update)
    return UserRead.model_validate(updated_user)

@router.get("/", response_model=List[UserRead])
async def list_organization_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin_user),
    session: AsyncSession = Depends(deps.get_session)
) -> List[UserRead]:
    """List all users in organization (admin only)"""
    user_service = UserService(session)
    users = await user_service.get_by_organization(
        current_user.organization_id, 
        skip=skip, 
        limit=limit
    )
    return [UserRead.model_validate(user) for user in users]
```

## Authentication with SuperTokens

### SuperTokens Integration
```python
# app/core/auth.py
import supertokens_python
from supertokens_python import init, InputAppInfo
from supertokens_python.recipe import emailpassword, session
from supertokens_python.recipe.emailpassword import EmailPasswordRecipe
from supertokens_python.recipe.session import SessionRecipe
from app.core.config import settings

def init_supertokens():
    init(
        app_info=InputAppInfo(
            app_name="P2P Sandbox",
            api_domain=settings.API_DOMAIN,
            website_domain=settings.WEBSITE_DOMAIN,
            api_base_path="/auth",
            website_base_path="/auth"
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.SUPERTOKENS_CONNECTION_URI,
            api_key=settings.SUPERTOKENS_API_KEY
        ),
        framework='fastapi',
        recipe_list=[
            emailpassword.init(),
            session.init(
                anti_csrf="VIA_TOKEN",
                cookie_secure=not settings.DEBUG,
                cookie_same_site="lax",
                session_expired_status_code=401
            )
        ]
    )
```

### Custom Auth Flow
```python
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.user import UserCreate
from app.models.organization import OrganizationCreate
from app.services.auth import AuthService

router = APIRouter()

@router.post("/signup")
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create organization and admin user"""
    auth_service = AuthService(session)
    
    # Create organization first
    org = await auth_service.create_organization(
        OrganizationCreate(
            name=user_data.organization_name,
            domain=user_data.email.split("@")[1]
        )
    )
    
    # Create admin user
    user = await auth_service.create_user(
        user_data,
        organization_id=org.id,
        role="admin"
    )
    
    # Create SuperTokens user
    st_user = await auth_service.create_supertokens_user(
        email=user.email,
        password=user_data.password
    )
    
    return {
        "user": UserRead.model_validate(user),
        "organization": OrganizationRead.model_validate(org)
    }
```

## Async Programming Implementation

### Database Session Management
```python
# app/db/session.py
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from typing import AsyncGenerator
from app.core.config import settings

# PostgreSQL with SQLModel
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# MongoDB
mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# Redis
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Dependencies
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_mongo_db():
    return mongo_db

async def get_redis():
    return redis_client
```

### Parallel Query Execution
```python
# app/services/dashboard.py
import asyncio
from typing import Dict, Any
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class DashboardService:
    def __init__(self, session: AsyncSession, mongo_db, redis):
        self.session = session
        self.mongo_db = mongo_db
        self.redis = redis
    
    async def get_dashboard_stats(self, user_id: UUID) -> Dict[str, Any]:
        """Get dashboard statistics with parallel queries"""
        # Execute multiple queries in parallel
        results = await asyncio.gather(
            self._get_user_stats(user_id),
            self._get_forum_stats(user_id),
            self._get_use_case_stats(user_id),
            self._get_recent_activity(user_id),
            return_exceptions=True
        )
        
        return {
            "user_stats": results[0],
            "forum_stats": results[1],
            "use_case_stats": results[2],
            "recent_activity": results[3]
        }
    
    async def _get_user_stats(self, user_id: UUID):
        # PostgreSQL query
        stmt = select(User).where(User.id == user_id)
        result = await self.session.exec(stmt)
        user = result.first()
        
        return {
            "total_posts": await self._count_user_posts(user_id),
            "best_answers": await self._count_best_answers(user_id),
            "reputation": user.reputation if user else 0
        }
    
    async def _count_user_posts(self, user_id: UUID):
        # MongoDB aggregation
        pipeline = [
            {"$match": {"author_id": str(user_id)}},
            {"$count": "total"}
        ]
        result = await self.mongo_db.forum_posts.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0
```

### WebSocket Implementation
```python
# app/core/websocket.py
from typing import Dict, Set
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, topic_id: str):
        await websocket.accept()
        if topic_id not in self.active_connections:
            self.active_connections[topic_id] = set()
        self.active_connections[topic_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, topic_id: str):
        if topic_id in self.active_connections:
            self.active_connections[topic_id].discard(websocket)
            if not self.active_connections[topic_id]:
                del self.active_connections[topic_id]
    
    async def broadcast_to_topic(self, topic_id: str, message: dict):
        if topic_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[topic_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for connection in dead_connections:
                self.disconnect(connection, topic_id)

manager = ConnectionManager()

# app/api/v1/endpoints/forums.py
@router.websocket("/ws/forum/{topic_id}")
async def forum_websocket(
    websocket: WebSocket, 
    topic_id: str,
    current_user: User = Depends(get_current_user_ws)
):
    await manager.connect(websocket, topic_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process message (save to database, etc.)
            message = await process_forum_message(data, current_user, topic_id)
            
            # Broadcast to all connected clients
            await manager.broadcast_to_topic(topic_id, {
                "type": "new_message",
                "message": message
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic_id)
```

## Development Workflow

### Initial Setup
```bash
# 1. Clone repository
git clone https://github.com/your-org/p2p-v2.git
cd p2p-v2

# 2. Setup environment
cp .env.example .env
# Edit .env with your values

# 3. Start all services
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Create superuser (optional)
docker-compose exec backend python scripts/create_superuser.py

# 6. Seed development data (optional)
docker-compose exec backend python scripts/seed_data.py
```

### Daily Development Commands
```bash
# Start services
docker-compose up

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest

# Run specific test
docker-compose exec backend pytest tests/test_auth.py -v

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Add new field"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Format code
docker-compose exec backend black .
docker-compose exec backend ruff . --fix

# Type checking
docker-compose exec backend mypy .

# Access database
docker-compose exec postgres psql -U postgres -d p2p_sandbox

# Python shell with async support
docker-compose exec backend python -m asyncio
```

### Development Best Practices
1. **Always use containers** - Never install services locally
2. **Write tests first** - TDD approach for reliability
3. **Use type hints** - Full typing for better IDE support
4. **Format on save** - Configure IDE to run Black
5. **Commit often** - Small, focused commits
6. **Document APIs** - OpenAPI schemas for all endpoints

## Implementation Roadmap

### Phase 0: Container Foundation (Day 1)
- [x] Docker Compose setup with all services
- [x] Development Dockerfiles
- [x] Environment configuration
- [x] Health checks for all services
- [ ] Documentation

### Phase 0.5: Frontend Integration Setup (Day 2-3) 🆕
- [ ] Install frontend dependencies (axios, supertokens-auth-react, react-query)
- [ ] Create API service layer with TypeScript
- [ ] Update frontend environment configuration
- [ ] Create shared types between frontend and backend
- [ ] Update AuthContext to use real API calls
- [ ] Add CORS testing between frontend and backend
- [ ] Create API integration documentation

### Phase 1: Backend Foundation (Week 1)
- [ ] FastAPI project structure
- [ ] SQLModel models implementation
- [ ] Async database connections
- [ ] Alembic migrations setup
- [ ] Basic CRUD operations
- [ ] Health check endpoints
- [ ] Logging configuration

### Phase 2: Authentication (Week 1-2)
- [ ] SuperTokens integration
- [ ] Signup with organization creation
- [ ] Login/logout endpoints
- [ ] Session management
- [ ] Password reset flow
- [ ] Email verification
- [ ] Role-based access control

### Phase 3: User Management (Week 2)
- [ ] User profile endpoints
- [ ] Organization management
- [ ] User invitation system
- [ ] Member listing and search
- [ ] Profile picture upload
- [ ] Activity tracking

### Phase 4: Forum System (Week 3)
- [ ] Forum topic CRUD
- [ ] Post creation with rich text
- [ ] Reply system with threading
- [ ] File attachments
- [ ] Best answer feature
- [ ] WebSocket real-time updates
- [ ] Forum search

### Phase 5: Use Cases (Week 4)
- [ ] Use case submission
- [ ] Media upload to S3
- [ ] Location picker integration
- [ ] Use case browsing
- [ ] Filtering and search
- [ ] Analytics tracking
- [ ] Export functionality

### Phase 6: Messaging & Dashboard (Week 5)
- [ ] Private messaging system
- [ ] Message notifications
- [ ] Dashboard statistics
- [ ] Activity feed
- [ ] Trending content
- [ ] Performance optimization

### Phase 7: Testing & Deployment (Week 6)
- [ ] Unit test coverage > 80%
- [ ] Integration tests
- [ ] E2E tests with frontend
- [ ] Performance testing
- [ ] Security audit
- [ ] Production deployment
- [ ] Monitoring setup

## Testing Strategy

### Test Structure
```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/            # API endpoint tests
│   ├── test_auth_api.py
│   ├── test_user_api.py
│   └── test_forum_api.py
├── e2e/                    # Full flow tests
│   ├── test_signup_flow.py
│   └── test_forum_flow.py
└── conftest.py            # Shared fixtures
```

### Test Configuration
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from app.main import app
from app.db.session import async_engine

@pytest.fixture
async def async_session():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with AsyncSession(async_engine) as session:
        yield session
    
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Example test
async def test_create_user(async_client: AsyncClient, async_session: AsyncSession):
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "securepass123",
            "first_name": "Test",
            "last_name": "User",
            "organization_name": "Test Org"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
```

### Running Tests
```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/unit/test_models.py -v

# Run tests matching pattern
docker-compose exec backend pytest -k "test_create" -v

# Run tests in parallel
docker-compose exec backend pytest -n auto
```

## Production Deployment

### Production Dockerfile
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python packages
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Update PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: ${DOCKER_REGISTRY}/p2p-backend:${VERSION}
    restart: always
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  postgres:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/conf.d:/etc/nginx/conf.d
    depends_on:
      - backend
```

### Deployment Checklist
- [ ] Environment variables secured in secrets manager
- [ ] HTTPS certificates configured
- [ ] Database backups automated
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Error tracking (Sentry)
- [ ] Log aggregation (ELK stack)
- [ ] Rate limiting configured
- [ ] CDN for static assets
- [ ] Load balancer health checks
- [ ] Rollback strategy documented
- [ ] Disaster recovery plan

## Performance Optimization

### Database Optimization
1. **Connection Pooling**: Configure optimal pool sizes
2. **Indexes**: Add indexes for frequently queried fields
3. **Query Optimization**: Use select_related/prefetch_related
4. **Caching**: Redis for frequently accessed data

### API Optimization
1. **Response Compression**: Enable gzip
2. **Pagination**: Limit default page sizes
3. **Field Selection**: Allow clients to specify fields
4. **Batch Operations**: Support bulk creates/updates

### Monitoring Metrics
- API response times (p50, p95, p99)
- Database query times
- Cache hit rates
- WebSocket connection counts
- Background task queue lengths
- Error rates by endpoint

## Security Best Practices

### API Security
1. **Authentication**: All endpoints require auth except public ones
2. **Authorization**: Role-based access control
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: SQLModel automatic validation
5. **SQL Injection**: Protected by ORM
6. **XSS Prevention**: Sanitize user content

### Infrastructure Security
1. **HTTPS Only**: Force SSL in production
2. **Secrets Management**: Use environment variables
3. **Container Security**: Run as non-root user
4. **Network Isolation**: Use Docker networks
5. **Regular Updates**: Keep dependencies current
6. **Security Scanning**: Scan images for vulnerabilities

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
```bash
# Check if database is running
docker-compose ps
docker-compose logs postgres

# Test connection
docker-compose exec postgres pg_isready
```

2. **Port Conflicts**
```bash
# Check what's using the port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Change port in docker-compose.yml
```

3. **Migration Errors**
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

4. **Performance Issues**
```bash
# Check container resources
docker stats

# Increase limits in docker-compose.yml
```

## Frontend-Backend Integration Guide

### Frontend Dependencies Update
Add these dependencies to `p2p-frontend-app/package.json`:
```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "supertokens-auth-react": "^0.35.0",
    "supertokens-web-js": "^0.8.0",
    "@tanstack/react-query": "^5.0.0",
    "socket.io-client": "^4.5.0"
  }
}
```

### API Service Layer Structure
```
p2p-frontend-app/src/
├── services/
│   ├── api.ts              # Axios instance with interceptors
│   ├── auth.service.ts     # Authentication API calls
│   ├── user.service.ts     # User management API
│   ├── forum.service.ts    # Forum API calls
│   └── usecase.service.ts  # Use case API calls
├── hooks/
│   ├── useApi.ts          # Generic API hook
│   ├── useAuth.ts         # Auth-specific hooks
│   └── useWebSocket.ts    # WebSocket hook
└── types/
    ├── api.types.ts       # API response types
    └── shared.types.ts    # Shared with backend
```

### Type Alignment Strategy
1. **Shared Types Package**: Create a shared TypeScript definitions
2. **UUID Handling**: Frontend uses string type for UUID compatibility
3. **Date Handling**: Use ISO strings in API, convert to Date objects in frontend
4. **Enum Alignment**: Ensure all enums match between frontend and backend

### Frontend Environment Configuration
```env
# .env.development
VITE_API_URL=http://localhost:8000/api/v1
VITE_SUPERTOKENS_URL=http://localhost:3567
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
VITE_APP_NAME=P2P Sandbox
```

### CORS Configuration for Development
Ensure backend allows frontend origin:
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative port
]
```

### Integration Testing Checklist
- [ ] Frontend can reach backend health endpoint
- [ ] Authentication flow works end-to-end
- [ ] API error responses are handled properly
- [ ] File uploads work with presigned URLs
- [ ] WebSocket connections establish correctly
- [ ] Session refresh works seamlessly

## Conclusion

This unified backend development plan provides:
- Complete container-first development environment
- Modern async architecture with SQLModel
- Comprehensive API design
- Frontend-backend integration strategy
- Clear implementation roadmap
- Testing and deployment strategies

Follow this plan to build a scalable, maintainable backend for the P2P Sandbox platform with seamless frontend integration.