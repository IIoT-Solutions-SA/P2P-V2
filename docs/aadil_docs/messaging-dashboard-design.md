# Messaging & Dashboard Design

## Overview
Comprehensive design document for the Messaging and Dashboard modules (Phase 6), detailing PostgreSQL schemas, API specifications, and performance optimization strategies.

---

## Part 1: Messaging System

### PostgreSQL Schema Design

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    sender_id UUID NOT NULL REFERENCES users(id),
    recipient_id UUID NOT NULL REFERENCES users(id),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    
    -- Content
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text', -- text|file|image|system
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    deleted_by UUID REFERENCES users(id),
    
    -- Metadata
    metadata JSONB, -- For attachments, reactions, etc.
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_conversation (conversation_id, created_at DESC),
    INDEX idx_sender (sender_id, created_at DESC),
    INDEX idx_recipient (recipient_id, is_read, created_at DESC),
    INDEX idx_organization (organization_id)
);

-- Optimized compound index for unread messages query
CREATE INDEX idx_unread_messages ON messages(recipient_id, is_read, conversation_id) 
WHERE is_read = FALSE AND is_deleted = FALSE;
```

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id),
    
    -- Participants (2 for direct messages)
    participant1_id UUID NOT NULL REFERENCES users(id),
    participant2_id UUID NOT NULL REFERENCES users(id),
    
    -- Last message cache (denormalized for performance)
    last_message_id UUID REFERENCES messages(id),
    last_message_content TEXT,
    last_message_at TIMESTAMP,
    last_message_sender_id UUID,
    
    -- Unread counts (denormalized)
    participant1_unread_count INT DEFAULT 0,
    participant2_unread_count INT DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    archived_by_participant1 BOOLEAN DEFAULT FALSE,
    archived_by_participant2 BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint for participant pairs
    CONSTRAINT unique_participants UNIQUE (participant1_id, participant2_id),
    
    -- Indexes
    INDEX idx_participant1 (participant1_id, last_message_at DESC),
    INDEX idx_participant2 (participant2_id, last_message_at DESC),
    INDEX idx_organization (organization_id)
);
```

#### Message Attachments Table
```sql
CREATE TABLE message_attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    
    -- File information
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL, -- Local storage path
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- Thumbnail for images
    thumbnail_path TEXT,
    
    -- Metadata
    width INT, -- For images
    height INT, -- For images
    duration INT, -- For videos/audio in seconds
    
    -- Timestamps
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_message (message_id)
);
```

### Messaging API Specifications

#### 1. Send Message
**POST** `/api/v1/messages`

```json
// Request
{
  "recipient_id": "uuid",
  "content": "Hello, I have a question about your use case...",
  "attachments": ["file_id_1", "file_id_2"] // Optional, from pre-upload
}

// Response (201)
{
  "id": "message-uuid",
  "conversation_id": "conv-uuid",
  "content": "Hello, I have a question...",
  "sender": {
    "id": "uuid",
    "name": "Ahmed Ali",
    "avatar": "/media/avatars/..."
  },
  "created_at": "2024-01-20T10:30:00Z"
}
```

#### 2. Get Conversations
**GET** `/api/v1/messages/conversations`

Query Parameters:
- `page` (int): Page number
- `page_size` (int): Items per page (max 50)
- `archived` (boolean): Include archived conversations

```json
// Response (200)
{
  "conversations": [
    {
      "id": "conv-uuid",
      "participant": {
        "id": "user-uuid",
        "name": "Sarah Ahmed",
        "title": "Production Manager",
        "avatar": "/media/avatars/...",
        "organization": "Tech Industries"
      },
      "last_message": {
        "content": "Thanks for the information!",
        "sender_id": "user-uuid",
        "created_at": "2024-01-20T10:30:00Z",
        "is_read": false
      },
      "unread_count": 3,
      "created_at": "2024-01-15T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

#### 3. Get Conversation Messages
**GET** `/api/v1/messages/conversations/{conversation_id}`

Query Parameters:
- `page` (int): Page number
- `page_size` (int): Messages per page
- `before` (timestamp): Get messages before this time

```json
// Response (200)
{
  "conversation": {
    "id": "conv-uuid",
    "participant": {...}
  },
  "messages": [
    {
      "id": "msg-uuid",
      "content": "Hello!",
      "sender_id": "user-uuid",
      "is_mine": true,
      "is_read": true,
      "attachments": [],
      "created_at": "2024-01-20T10:30:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 4. Mark Messages as Read
**PATCH** `/api/v1/messages/conversations/{conversation_id}/read`

```json
// Response (200)
{
  "marked_read": 5,
  "unread_count": 0
}
```

#### 5. Delete Message
**DELETE** `/api/v1/messages/{message_id}`

```json
// Response (200)
{
  "message": "Message deleted successfully",
  "deleted_at": "2024-01-20T10:30:00Z"
}
```

---

## Part 2: Dashboard System

### Dashboard Statistics Structure

#### Organization Statistics
```python
@dataclass
class OrganizationStats:
    total_users: int
    active_users_30d: int
    new_users_this_month: int
    user_growth_percentage: float
    departments: List[Dict[str, int]]
    user_roles_distribution: Dict[str, int]
```

#### Forum Statistics
```python
@dataclass
class ForumStats:
    total_topics: int
    total_posts: int
    topics_this_week: int
    posts_this_week: int
    active_contributors: int
    engagement_rate: float
    popular_categories: List[Dict[str, Any]]
    trending_topics: List[Dict[str, Any]]
    best_answers_count: int
    avg_response_time: float  # hours
```

#### Use Cases Statistics
```python
@dataclass
class UseCaseStats:
    total_submissions: int
    verified_cases: int
    draft_cases: int
    total_views: int
    avg_roi: float
    top_categories: List[Dict[str, int]]
    submissions_this_month: int
    avg_implementation_time: str
    total_cost_savings: str
```

#### Messaging Statistics
```python
@dataclass
class MessagingStats:
    total_conversations: int
    active_conversations_7d: int
    messages_sent_today: int
    avg_response_time: float  # minutes
    unread_messages: int
```

### Dashboard API Specifications

#### 1. Get Dashboard Statistics
**GET** `/api/v1/dashboard/stats`

Query Parameters:
- `period` (string): day|week|month|year|all
- `compare` (boolean): Include comparison with previous period

```json
// Response (200)
{
  "period": "month",
  "organization": {
    "total_users": 156,
    "active_users_30d": 98,
    "new_users_this_month": 12,
    "user_growth_percentage": 8.3,
    "departments": [
      {"name": "Production", "count": 45},
      {"name": "Quality", "count": 32}
    ]
  },
  "forum": {
    "total_topics": 234,
    "total_posts": 1567,
    "topics_this_week": 15,
    "engagement_rate": 62.5,
    "trending_topics": [
      {
        "id": "uuid",
        "title": "New Safety Protocols",
        "views": 234,
        "replies": 45
      }
    ]
  },
  "use_cases": {
    "total_submissions": 89,
    "verified_cases": 67,
    "total_views": 15234,
    "avg_roi": 185.5,
    "top_categories": [
      {"name": "Quality Control", "count": 24},
      {"name": "Automation", "count": 18}
    ]
  },
  "messaging": {
    "total_conversations": 324,
    "active_conversations_7d": 45,
    "messages_sent_today": 89,
    "unread_messages": 12
  },
  "comparison": {
    "users_change": "+8.3%",
    "topics_change": "+12.5%",
    "messages_change": "+22.1%"
  }
}
```

#### 2. Get Activity Feed
**GET** `/api/v1/dashboard/activity`

Query Parameters:
- `page` (int): Page number
- `page_size` (int): Items per page
- `types` (array): Filter by activity types

```json
// Response (200)
{
  "activities": [
    {
      "id": "activity-uuid",
      "type": "forum_topic_created",
      "title": "New topic: Safety Protocol Updates",
      "description": "Ahmed created a new forum topic",
      "actor": {
        "id": "user-uuid",
        "name": "Ahmed Ali",
        "avatar": "/media/avatars/..."
      },
      "target": {
        "type": "forum_topic",
        "id": "topic-uuid",
        "title": "Safety Protocol Updates"
      },
      "timestamp": "2024-01-20T10:30:00Z"
    },
    {
      "type": "use_case_published",
      "title": "New use case: AI Quality Inspection",
      "description": "Sarah published a new use case",
      "actor": {...},
      "target": {...},
      "timestamp": "2024-01-20T09:15:00Z"
    }
  ],
  "pagination": {...}
}
```

#### 3. Get Trending Content
**GET** `/api/v1/dashboard/trending`

Query Parameters:
- `period` (string): day|week|month
- `category` (string): all|forum|use_cases
- `limit` (int): Number of items (max 20)

```json
// Response (200)
{
  "period": "week",
  "trending": {
    "forum_topics": [
      {
        "id": "topic-uuid",
        "title": "Implementing ISO 9001",
        "views": 456,
        "replies": 34,
        "trend_score": 89.5
      }
    ],
    "use_cases": [
      {
        "id": "uc-uuid",
        "title": "AI-Powered Quality Control",
        "views": 1234,
        "likes": 89,
        "trend_score": 94.2
      }
    ],
    "search_terms": [
      {"term": "automation", "count": 234},
      {"term": "quality control", "count": 189}
    ]
  }
}
```

---

## Performance Optimization Strategies

### 1. Database Optimization

#### Query Optimization
```python
# Use database views for complex aggregations
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT 
    o.id as organization_id,
    COUNT(DISTINCT u.id) as total_users,
    COUNT(DISTINCT CASE WHEN u.last_active > NOW() - INTERVAL '30 days' THEN u.id END) as active_users_30d,
    COUNT(DISTINCT ft.id) as total_topics,
    COUNT(DISTINCT fp.id) as total_posts
FROM organizations o
LEFT JOIN users u ON u.organization_id = o.id
LEFT JOIN forum_topics ft ON ft.organization_id = o.id
LEFT JOIN forum_posts fp ON fp.organization_id = o.id
GROUP BY o.id;

# Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;
```

#### Index Strategy
```sql
-- Composite indexes for common queries
CREATE INDEX idx_messages_unread ON messages(recipient_id, is_read, created_at DESC) 
WHERE is_read = FALSE;

CREATE INDEX idx_conversations_active ON conversations(participant1_id, last_message_at DESC) 
WHERE is_active = TRUE;

-- Partial indexes for performance
CREATE INDEX idx_messages_recent ON messages(created_at DESC) 
WHERE created_at > NOW() - INTERVAL '7 days';
```

### 2. Caching Strategy

#### In-Memory Caching
```python
from functools import lru_cache
from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta

class CacheService:
    _cache: Dict[str, Any] = {}
    _timestamps: Dict[str, datetime] = {}
    
    @classmethod
    async def get_or_set(
        cls,
        key: str,
        factory,
        ttl: int = 300  # 5 minutes default
    ):
        """Get from cache or compute and cache"""
        now = datetime.utcnow()
        
        # Check if cached and not expired
        if key in cls._cache:
            if now - cls._timestamps[key] < timedelta(seconds=ttl):
                return cls._cache[key]
        
        # Compute and cache
        value = await factory()
        cls._cache[key] = value
        cls._timestamps[key] = now
        
        return value
    
    @classmethod
    def invalidate(cls, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            keys_to_delete = [k for k in cls._cache if pattern in k]
            for key in keys_to_delete:
                del cls._cache[key]
                del cls._timestamps[key]
        else:
            cls._cache.clear()
            cls._timestamps.clear()

# Usage in service
class DashboardService:
    @staticmethod
    async def get_stats(organization_id: UUID, period: str = "month"):
        cache_key = f"dashboard_stats:{organization_id}:{period}"
        
        return await CacheService.get_or_set(
            cache_key,
            lambda: DashboardService._compute_stats(organization_id, period),
            ttl=600  # 10 minutes
        )
```

### 3. Query Batching
```python
class MessageService:
    @staticmethod
    async def get_conversations_optimized(user_id: UUID, page: int = 1):
        """Get conversations with batched queries"""
        # Single query with joins instead of N+1
        query = """
            SELECT 
                c.*,
                u.id as participant_id,
                u.first_name,
                u.last_name,
                u.title,
                u.avatar_url,
                o.name as organization_name,
                CASE 
                    WHEN c.participant1_id = $1 THEN c.participant2_unread_count
                    ELSE c.participant1_unread_count
                END as unread_count
            FROM conversations c
            JOIN users u ON (
                CASE 
                    WHEN c.participant1_id = $1 THEN c.participant2_id
                    ELSE c.participant1_id
                END = u.id
            )
            JOIN organizations o ON u.organization_id = o.id
            WHERE c.participant1_id = $1 OR c.participant2_id = $1
            ORDER BY c.last_message_at DESC
            LIMIT $2 OFFSET $3
        """
        
        limit = 20
        offset = (page - 1) * limit
        
        return await db.fetch_all(query, user_id, limit, offset)
```

---

## Background Tasks

### Task Queue Implementation
```python
import asyncio
from typing import Callable, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class Task:
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    created_at: datetime = None

class SimpleTaskQueue:
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.workers = []
        self.running = False
        
    async def enqueue(self, func: Callable, *args, **kwargs):
        """Add task to queue"""
        task = Task(
            id=str(uuid4()),
            func=func,
            args=args,
            kwargs=kwargs,
            created_at=datetime.utcnow()
        )
        await self.queue.put((task.priority, task))
        return task.id
    
    async def worker(self):
        """Worker coroutine"""
        while self.running:
            try:
                priority, task = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                # Execute task
                try:
                    if asyncio.iscoroutinefunction(task.func):
                        await task.func(*task.args, **task.kwargs)
                    else:
                        task.func(*task.args, **task.kwargs)
                except Exception as e:
                    logging.error(f"Task {task.id} failed: {e}")
                    
            except asyncio.TimeoutError:
                continue
    
    async def start(self, num_workers: int = 3):
        """Start task queue workers"""
        self.running = True
        self.workers = [
            asyncio.create_task(self.worker()) 
            for _ in range(num_workers)
        ]
    
    async def stop(self):
        """Stop task queue"""
        self.running = False
        await asyncio.gather(*self.workers)

# Usage
task_queue = SimpleTaskQueue()

# In application startup
async def startup():
    await task_queue.start(num_workers=3)

# Enqueue tasks
await task_queue.enqueue(send_email_notification, user_id, message)
await task_queue.enqueue(update_statistics_cache, organization_id)
```

### Scheduled Jobs
```python
import asyncio
from datetime import datetime, timedelta
from typing import List, Callable

class ScheduledJob:
    def __init__(self, func: Callable, interval: timedelta, name: str):
        self.func = func
        self.interval = interval
        self.name = name
        self.last_run = None
        self.next_run = datetime.utcnow()
    
    async def run(self):
        """Execute the job"""
        try:
            await self.func()
            self.last_run = datetime.utcnow()
            self.next_run = self.last_run + self.interval
        except Exception as e:
            logging.error(f"Scheduled job {self.name} failed: {e}")

class Scheduler:
    def __init__(self):
        self.jobs: List[ScheduledJob] = []
        self.running = False
    
    def add_job(self, func: Callable, interval: timedelta, name: str):
        """Add a scheduled job"""
        job = ScheduledJob(func, interval, name)
        self.jobs.append(job)
    
    async def run(self):
        """Main scheduler loop"""
        self.running = True
        while self.running:
            now = datetime.utcnow()
            
            # Check each job
            for job in self.jobs:
                if now >= job.next_run:
                    asyncio.create_task(job.run())
            
            # Sleep for a short interval
            await asyncio.sleep(10)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False

# Define scheduled jobs
scheduler = Scheduler()

# Refresh dashboard cache every 5 minutes
scheduler.add_job(
    refresh_dashboard_cache,
    timedelta(minutes=5),
    "refresh_dashboard"
)

# Clean up old exports every hour
scheduler.add_job(
    cleanup_old_exports,
    timedelta(hours=1),
    "cleanup_exports"
)

# Update trending content every 30 minutes
scheduler.add_job(
    update_trending_content,
    timedelta(minutes=30),
    "update_trending"
)
```

---

## Security Considerations

### 1. Message Security
- Validate conversation participants
- Prevent cross-organization messaging
- Sanitize message content (XSS prevention)
- Rate limit message sending
- Encrypt sensitive content (future)

### 2. File Upload Security
- Validate file types and sizes
- Scan for malware (future)
- Generate unique filenames
- Restrict path traversal
- Implement download permissions

### 3. Dashboard Access Control
- Organization-scoped statistics only
- Role-based dashboard views
- Audit log for admin actions
- Rate limit API calls
- Cache invalidation on permission changes

---

## Testing Strategy

### 1. Unit Tests
```python
import pytest
from unittest.mock import AsyncMock

async def test_send_message():
    """Test message sending"""
    service = MessageService()
    mock_db = AsyncMock()
    
    message_data = {
        "recipient_id": "user-uuid",
        "content": "Test message"
    }
    
    result = await service.send_message(
        mock_db,
        sender_id="sender-uuid",
        **message_data
    )
    
    assert result.content == "Test message"
    assert mock_db.execute.called

async def test_dashboard_stats_caching():
    """Test dashboard statistics caching"""
    service = DashboardService()
    
    # First call should compute
    stats1 = await service.get_stats("org-uuid")
    
    # Second call should use cache
    stats2 = await service.get_stats("org-uuid")
    
    assert stats1 == stats2
```

### 2. Integration Tests
```python
async def test_conversation_flow():
    """Test complete conversation flow"""
    async with test_db() as db:
        # Create users
        user1 = await create_test_user(db)
        user2 = await create_test_user(db)
        
        # Send message
        message = await MessageService.send_message(
            db,
            sender_id=user1.id,
            recipient_id=user2.id,
            content="Hello"
        )
        
        # Get conversations for user2
        convs = await MessageService.get_conversations(db, user2.id)
        
        assert len(convs) == 1
        assert convs[0].unread_count == 1
        
        # Mark as read
        await MessageService.mark_read(
            db,
            conversation_id=convs[0].id,
            user_id=user2.id
        )
        
        # Verify unread count
        convs = await MessageService.get_conversations(db, user2.id)
        assert convs[0].unread_count == 0
```

### 3. Performance Tests
```python
import time

async def test_dashboard_performance():
    """Test dashboard stats performance"""
    start = time.time()
    
    stats = await DashboardService.get_stats("org-uuid")
    
    elapsed = time.time() - start
    
    # Should be under 200ms
    assert elapsed < 0.2
    assert stats is not None
```

---

## Monitoring & Metrics

### Key Metrics to Track
1. **Messaging**
   - Messages sent per day
   - Average response time
   - Unread message age
   - Conversation activity

2. **Dashboard**
   - API response times
   - Cache hit rates
   - Query execution times
   - Concurrent users

3. **Performance**
   - Database connection pool usage
   - Memory usage
   - Task queue length
   - Background job execution times

### Logging Strategy
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    @staticmethod
    def log_api_request(
        endpoint: str,
        method: str,
        user_id: str,
        response_time: float,
        status_code: int
    ):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "api_request",
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "response_time_ms": response_time * 1000,
            "status_code": status_code
        }
        logging.info(json.dumps(log_data))
```

---

## Future Enhancements

1. **Messaging**
   - Group conversations
   - Message reactions
   - Voice/video calls
   - End-to-end encryption
   - Message search

2. **Dashboard**
   - Custom dashboards
   - Real-time updates (WebSockets)
   - Advanced analytics
   - Export capabilities
   - AI insights

3. **Performance**
   - Redis caching
   - Read replicas
   - Message queue (RabbitMQ/Celery)
   - CDN for attachments
   - Database sharding