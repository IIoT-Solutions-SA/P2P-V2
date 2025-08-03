# Asynchronous Programming Implementation Guide

## Why Async for P2P Sandbox

### Performance Benefits
- **10x better concurrency**: Handle 1000+ concurrent users vs 50-100 with sync
- **Non-blocking I/O**: Database queries, file uploads, API calls don't block other operations
- **Real-time capabilities**: WebSockets for live forum updates and messaging
- **Resource efficiency**: Better CPU and memory utilization

### Key Use Cases in P2P Sandbox
1. **Real-time forum discussions** - Live updates when users post
2. **Concurrent file uploads** - Multiple users uploading use case media
3. **Parallel database queries** - Dashboard loading multiple data sources
4. **Background tasks** - Email notifications, data processing
5. **Search operations** - Non-blocking search across large datasets

## Implementation Strategy

### 1. Database Layer (AsyncPG + Motor)

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import motor.motor_asyncio

# PostgreSQL async connection
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/p2p_sandbox"
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# MongoDB async connection
mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
mongo_db = mongo_client.p2p_sandbox

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_mongo_db():
    yield mongo_db
```

### 2. Async Models

```python
# app/models/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: str) -> User:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.organization))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_organization_members(self, org_id: str) -> List[User]:
        result = await self.session.execute(
            select(User).where(User.organization_id == org_id)
        )
        return result.scalars().all()
    
    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
```

### 3. Async API Endpoints

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_db
from app.models.user import UserRepository
from app.core.security import get_current_user

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.id)
    return user

@router.get("/")
async def list_organization_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    user_repo = UserRepository(db)
    users = await user_repo.get_organization_members(current_user.organization_id)
    return users

@router.patch("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    user_repo = UserRepository(db)
    updated_user = await user_repo.update(current_user.id, user_update.dict(exclude_unset=True))
    return updated_user
```

### 4. Async Forum System with Real-time Updates

```python
# app/api/v1/endpoints/forums.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, topic_id: str):
        await websocket.accept()
        if topic_id not in self.active_connections:
            self.active_connections[topic_id] = []
        self.active_connections[topic_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, topic_id: str):
        self.active_connections[topic_id].remove(websocket)
    
    async def broadcast_to_topic(self, topic_id: str, message: str):
        if topic_id in self.active_connections:
            await asyncio.gather(*[
                connection.send_text(message)
                for connection in self.active_connections[topic_id]
            ], return_exceptions=True)

manager = ConnectionManager()

@router.get("/topics")
async def list_forum_topics(
    skip: int = 0,
    limit: int = 20,
    category: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    # Async database query with filtering
    query = select(ForumTopic).offset(skip).limit(limit)
    if category:
        query = query.where(ForumTopic.category == category)
    
    result = await db.execute(query)
    topics = result.scalars().all()
    return topics

@router.post("/topics")
async def create_forum_topic(
    topic: ForumTopicCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    # Create topic in PostgreSQL
    db_topic = ForumTopic(
        title=topic.title,
        category=topic.category,
        created_by=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(db_topic)
    await db.commit()
    await db.refresh(db_topic)
    
    # Notify connected users in real-time
    await manager.broadcast_to_topic(
        "all", 
        json.dumps({"type": "new_topic", "topic": db_topic.dict()})
    )
    
    return db_topic

@router.websocket("/ws/forum/{topic_id}")
async def forum_websocket_endpoint(
    websocket: WebSocket, 
    topic_id: str,
    current_user: User = Depends(get_current_user_ws)  # WebSocket auth
):
    await manager.connect(websocket, topic_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message (save to DB, etc.)
            await process_forum_message(topic_id, message_data, current_user)
            
            # Broadcast to all connected users
            await manager.broadcast_to_topic(topic_id, data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, topic_id)
```

### 5. Async Use Case System with File Upload

```python
# app/api/v1/endpoints/use_cases.py
import aiofiles
import asyncio
from app.services.file_storage import S3Service

@router.post("/")
async def create_use_case(
    use_case: UseCaseCreate,
    files: List[UploadFile] = File([]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    mongo_db = Depends(get_mongo_db)
):
    # Create use case record in PostgreSQL
    db_use_case = UseCaseSubmission(
        title=use_case.title,
        organization_id=current_user.organization_id,
        submitted_by=current_user.id,
        status="draft"
    )
    db.add(db_use_case)
    await db.commit()
    await db.refresh(db_use_case)
    
    # Upload files asynchronously
    file_urls = []
    if files:
        upload_tasks = [
            upload_file_async(file, db_use_case.id) 
            for file in files
        ]
        file_urls = await asyncio.gather(*upload_tasks)
    
    # Store detailed content in MongoDB
    use_case_doc = {
        "submission_id": str(db_use_case.id),
        "title": use_case.title,
        "organization_id": str(current_user.organization_id),
        "submitted_by": str(current_user.id),
        "industry": use_case.industry,
        "technology": use_case.technology,
        "problem_statement": use_case.problem_statement,
        "solution": use_case.solution,
        "outcomes": use_case.outcomes.dict() if use_case.outcomes else {},
        "vendor_info": use_case.vendor_info.dict() if use_case.vendor_info else {},
        "media": [{"type": "image", "url": url} for url in file_urls],
        "location": use_case.location.dict() if use_case.location else {},
        "created_at": datetime.utcnow()
    }
    
    await mongo_db.use_cases.insert_one(use_case_doc)
    
    return db_use_case

async def upload_file_async(file: UploadFile, use_case_id: str) -> str:
    """Upload file to S3 asynchronously"""
    s3_service = S3Service()
    
    # Save file temporarily
    file_path = f"temp/{use_case_id}_{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    # Upload to S3
    s3_key = f"use-cases/{use_case_id}/{file.filename}"
    file_url = await s3_service.upload_file_async(file_path, s3_key)
    
    # Clean up temp file
    await aiofiles.os.remove(file_path)
    
    return file_url
```

### 6. Async Dashboard with Parallel Data Loading

```python
# app/api/v1/endpoints/dashboard.py
@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    mongo_db = Depends(get_mongo_db)
):
    # Execute all dashboard queries in parallel
    stats_tasks = [
        get_user_statistics(current_user.id, db),
        get_organization_statistics(current_user.organization_id, db),
        get_recent_forum_activity(current_user.organization_id, mongo_db),
        get_use_case_statistics(current_user.organization_id, mongo_db),
        get_trending_topics(mongo_db)
    ]
    
    user_stats, org_stats, forum_activity, use_case_stats, trending = await asyncio.gather(*stats_tasks)
    
    return DashboardStats(
        user_stats=user_stats,
        organization_stats=org_stats,
        recent_activity=forum_activity,
        use_case_stats=use_case_stats,
        trending_topics=trending
    )

async def get_user_statistics(user_id: str, db: AsyncSession):
    # Multiple async queries
    posts_count, replies_count, use_cases_count = await asyncio.gather(
        db.scalar(select(func.count(ForumPost.id)).where(ForumPost.author_id == user_id)),
        db.scalar(select(func.count(ForumReply.id)).where(ForumReply.author_id == user_id)),
        db.scalar(select(func.count(UseCaseSubmission.id)).where(UseCaseSubmission.submitted_by == user_id))
    )
    
    return {
        "posts_count": posts_count,
        "replies_count": replies_count,
        "use_cases_count": use_cases_count
    }
```

### 7. Background Tasks

```python
# app/services/background_tasks.py
from fastapi import BackgroundTasks
import asyncio
from app.services.email import EmailService

async def send_notification_email(user_email: str, subject: str, content: str):
    """Send email asynchronously"""
    email_service = EmailService()
    await email_service.send_async(user_email, subject, content)

@router.post("/forums/topics/{topic_id}/posts")
async def create_forum_post(
    topic_id: str,
    post: ForumPostCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    # Create post
    db_post = await create_post_in_db(topic_id, post, current_user, db)
    
    # Send notifications in background
    background_tasks.add_task(
        notify_topic_followers,
        topic_id,
        current_user.id,
        f"New post in {topic_id}"
    )
    
    return db_post

async def notify_topic_followers(topic_id: str, author_id: str, message: str):
    """Notify all topic followers asynchronously"""
    # Get all followers
    followers = await get_topic_followers(topic_id)
    
    # Send emails in parallel
    email_tasks = [
        send_notification_email(
            follower.email,
            "New Forum Activity",
            message
        )
        for follower in followers if follower.id != author_id
    ]
    
    await asyncio.gather(*email_tasks, return_exceptions=True)
```

## Updated Dependencies

```txt
# requirements.txt - Updated for async
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Async Database
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
motor==3.3.2  # Async MongoDB

# Async File Operations
aiofiles==23.2.1
aiohttp==3.9.0

# Background Tasks
celery[redis]==5.3.4  # For heavy background tasks
redis==5.0.1

# Other async utilities
asyncio-mqtt==0.16.1  # If using MQTT for real-time
websockets==12.0
```

## Performance Comparison

### Synchronous vs Asynchronous Performance

```python
# Synchronous approach
def sync_dashboard_load():
    # Each query blocks until complete
    user_stats = get_user_stats()      # 100ms
    org_stats = get_org_stats()        # 150ms  
    activity = get_activity()          # 200ms
    use_cases = get_use_cases()        # 250ms
    # Total: 700ms

# Asynchronous approach  
async def async_dashboard_load():
    # All queries run in parallel
    results = await asyncio.gather(
        get_user_stats_async(),         # 100ms
        get_org_stats_async(),          # 150ms
        get_activity_async(),           # 200ms
        get_use_cases_async()           # 250ms
    )
    # Total: 250ms (time of slowest query)
```

## Testing Async Code

```python
# test_async_endpoints.py
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_forum_creation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/forums/topics",
            json={"title": "Test Topic", "category": "general"}
        )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_concurrent_requests():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Test multiple concurrent requests
        tasks = [
            ac.get("/api/v1/dashboard/stats")
            for _ in range(10)
        ]
        responses = await asyncio.gather(*tasks)
        
    assert all(r.status_code == 200 for r in responses)
```

## Migration Strategy

### Phase 1: Core Async Infrastructure
1. Update database connections to async
2. Convert basic CRUD operations
3. Update authentication layer

### Phase 2: High-Impact Endpoints  
1. Dashboard (parallel data loading)
2. Forum listing (large datasets)
3. Use case search (complex queries)

### Phase 3: Real-time Features
1. WebSocket connections
2. Live forum updates  
3. Real-time messaging

### Phase 4: Background Processing
1. Email notifications
2. File processing
3. Data analytics

This async implementation will dramatically improve the P2P Sandbox's performance and enable real-time collaboration features that are essential for a modern forum and collaboration platform.