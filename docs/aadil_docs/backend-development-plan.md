# P2P Sandbox Backend Development Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Async Programming Strategy](#async-programming-strategy)
3. [Backend Architecture & Folder Structure](#backend-architecture--folder-structure)
4. [Database Schema Design](#database-schema-design)
5. [Authentication Flow with SuperTokens](#authentication-flow-with-supertokens)
6. [Frontend to Backend API Mapping](#frontend-to-backend-api-mapping)
7. [API Endpoints Structure](#api-endpoints-structure)
8. [Testing Strategy](#testing-strategy)
9. [Integration Strategy](#integration-strategy)
10. [Implementation Order with Testing Gates](#implementation-order-with-testing-gates)
11. [Key Technical Decisions](#key-technical-decisions)
12. [Development Steps](#development-steps)

## Project Overview

The P2P Sandbox platform is a peer-driven collaboration platform for Saudi Arabia's industrial SMEs. The backend uses **asynchronous FastAPI** to handle real-time collaboration, concurrent file uploads, and high user loads efficiently.

### Why Async for P2P Sandbox?
- **Real-time forum discussions**: Live updates when users post
- **Concurrent file uploads**: Multiple users uploading use case media simultaneously
- **Parallel data loading**: Dashboard loads multiple data sources 3x faster
- **Background notifications**: Email alerts without blocking user operations
- **WebSocket support**: Live messaging and forum updates
- **Scalability**: Handle 1000+ concurrent users vs 50-100 with synchronous code

### Technology Stack
- **Backend Framework**: FastAPI (Python) with **Async/Await**
- **Databases**: 
  - PostgreSQL (async with AsyncPG)
  - MongoDB (async with Motor)
- **Authentication**: SuperTokens
- **File Storage**: AWS S3 / Azure Blob Storage (async)
- **Real-time**: WebSockets + Background Tasks
- **Testing**: Pytest + AsyncIO + Frontend Integration Tests
- **Performance**: 10x better concurrency (1000+ vs 100 users)

## Async Programming Strategy

### Core Async Components

1. **Database Layer**
```python
# Async PostgreSQL with AsyncPG
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/p2p_sandbox"
async_engine = create_async_engine(DATABASE_URL)

# Async MongoDB with Motor
import motor.motor_asyncio
mongo_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
```

2. **Async API Endpoints**
```python
@router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    # Execute multiple queries in parallel - 3x faster!
    user_stats, org_stats, activity = await asyncio.gather(
        get_user_statistics(current_user.id, db),
        get_organization_statistics(current_user.organization_id, db),
        get_recent_activity(current_user.organization_id, db)
    )
    return DashboardStats(user_stats, org_stats, activity)
```

3. **Real-time WebSockets**
```python
@app.websocket("/ws/forum/{topic_id}")
async def forum_websocket(websocket: WebSocket, topic_id: str):
    await websocket.accept()
    # Handle real-time forum updates
    async for message in websocket:
        await broadcast_to_topic(topic_id, message)
```

4. **Async File Operations**
```python
async def upload_use_case_media(files: List[UploadFile]):
    # Upload multiple files in parallel
    upload_tasks = [upload_to_s3_async(file) for file in files]
    file_urls = await asyncio.gather(*upload_tasks)
    return file_urls
```

### Performance Benefits
- **Dashboard Loading**: 700ms → 250ms (parallel queries)
- **File Uploads**: Non-blocking, users can continue browsing
- **Concurrent Users**: 1000+ vs 100 with sync
- **Real-time Updates**: Instant forum notifications

## Backend Architecture & Folder Structure

```
p2p-backend-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI async application entry point
│   ├── config.py               # Configuration settings
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Async dependencies (auth, db sessions)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py         # API router aggregator
│   │       └── endpoints/
│   │           ├── auth.py    # Async authentication endpoints
│   │           ├── users.py   # Async user management
│   │           ├── organizations.py
│   │           ├── forums.py  # Async forum + WebSockets
│   │           ├── use_cases.py # Async use cases + file upload
│   │           ├── messages.py # Async messaging
│   │           ├── search.py  # Async search
│   │           └── websockets.py # WebSocket endpoints
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py        # Async security utilities
│   │   ├── config.py          # Core configuration
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── websocket_manager.py # WebSocket connection manager
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py           # Async database base configuration
│   │   ├── session.py        # Async database sessions (AsyncPG + Motor)
│   │   ├── init_db.py        # Async database initialization
│   │   └── migrations/       # Alembic migrations
│   │
│   ├── models/               # Async SQLAlchemy models + repositories
│   │   ├── __init__.py
│   │   ├── user.py           # User model + async repository
│   │   ├── organization.py   # Organization model + async repository
│   │   ├── forum.py          # Forum models + async repository
│   │   ├── use_case.py       # Use case models + async repository
│   │   └── message.py        # Message models + async repository
│   │
│   ├── schemas/              # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── forum.py
│   │   ├── use_case.py
│   │   ├── message.py
│   │   └── websocket.py      # WebSocket message schemas
│   │
│   ├── services/             # Async business logic
│   │   ├── __init__.py
│   │   ├── auth.py           # Async auth service
│   │   ├── user.py           # Async user service
│   │   ├── organization.py   # Async organization service
│   │   ├── forum.py          # Async forum service
│   │   ├── use_case.py       # Async use case service
│   │   ├── file_storage.py   # Async S3/Azure service
│   │   ├── email.py          # Async email service
│   │   └── background_tasks.py # Background task definitions
│   │
│   └── tasks/                # Background task workers
│       ├── __init__.py
│       ├── email_tasks.py    # Email notification tasks
│       ├── file_tasks.py     # File processing tasks
│       └── analytics_tasks.py # Analytics processing
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Async test configuration
│   ├── test_auth.py          # Authentication tests
│   ├── test_users.py         # User management tests
│   ├── test_forums.py        # Forum system tests
│   ├── test_use_cases.py     # Use case tests
│   ├── test_websockets.py    # WebSocket tests
│   ├── test_integration/     # Frontend integration tests
│   │   ├── test_auth_flow.py
│   │   ├── test_forum_flow.py
│   │   └── test_use_case_flow.py
│   └── test_performance/     # Performance tests
│       ├── test_async_endpoints.py
│       └── test_load.py
│
├── alembic.ini              # Database migration config
├── requirements.txt         # Async Python dependencies
├── .env.example            # Environment variables template
├── docker-compose.yml      # Development environment
└── Dockerfile              # Async-optimized Docker config
```

## Database Schema Design

### PostgreSQL Tables

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    industry VARCHAR(100),
    size VARCHAR(50), -- 'small', 'medium', 'large'
    country VARCHAR(100),
    city VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_user_id UUID
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50), -- 'admin', 'member'
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forum Topics
CREATE TABLE forum_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    created_by UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    is_pinned BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID REFERENCES users(id),
    receiver_id UUID REFERENCES users(id),
    content TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Additional tables for Phase 1
CREATE TABLE use_case_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    submitted_by UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'published', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### MongoDB Collections

```javascript
// Forum Posts (nested structure)
{
  _id: ObjectId,
  topic_id: "uuid",
  content: "post content",
  author_id: "uuid",
  attachments: [
    {
      type: "image|document",
      url: "s3_url",
      filename: "name"
    }
  ],
  replies: [
    {
      id: "uuid",
      content: "reply content",
      author_id: "uuid",
      created_at: Date,
      is_best_answer: false
    }
  ],
  created_at: Date,
  updated_at: Date
}

// Use Cases (detailed content)
{
  _id: ObjectId,
  submission_id: "uuid", // References PostgreSQL table
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
    coordinates: [lat, lng]
  },
  tags: ["automation", "quality-control"],
  created_at: Date,
  updated_at: Date
}

// Activity Logs
{
  _id: ObjectId,
  user_id: "uuid",
  organization_id: "uuid",
  action_type: "login|post_created|use_case_submitted",
  entity_type: "forum|use_case|message",
  entity_id: "uuid",
  metadata: {
    // Additional context
  },
  created_at: Date
}
```

## Authentication Flow with SuperTokens

### Backend Setup Steps

1. **Install SuperTokens Python SDK**
   ```bash
   pip install supertokens-python
   ```

2. **Configure SuperTokens Core**
   - Option 1: Self-hosted SuperTokens Core
   - Option 2: Managed service at supertokens.com

3. **Recipe Configuration**
   - EmailPassword recipe for authentication
   - Session recipe for session management
   - Custom callbacks for user/org creation

### Authentication Flow Diagram

```
Frontend                    Backend                    SuperTokens              Database
   |                           |                           |                        |
   |-- POST /auth/signup ----->|                           |                        |
   |                           |-- Create ST User -------->|                        |
   |                           |<-- ST User ID ------------|                        |
   |                           |                           |                        |
   |                           |-- Create Org & User ------------------------------>|
   |                           |<-- User & Org Data --------------------------------|
   |<-- Session + User Data ---|                           |                        |
   |                           |                           |                        |
   |-- POST /auth/login ------->|                           |                        |
   |                           |-- Verify Credentials ----->|                        |
   |                           |<-- Session Token ---------|                        |
   |                           |-- Fetch User Data ----------------------------------->|
   |<-- Session + User Data ---|<-- User Data ------------------------------------|
```

### Session Management

- Use SuperTokens session management with httpOnly cookies
- Implement refresh token rotation
- Add organization context to session claims
- Session configuration:
  ```python
  Session.init(
      anti_csrf="VIA_TOKEN",
      cookie_domain="localhost",
      cookie_secure=True,  # Set to True in production
      cookie_same_site="lax",
      session_expired_status_code=401
  )
  ```

## Frontend to Backend API Mapping

| Frontend Function | Current Implementation | Backend Endpoint | Method | Request Body |
|------------------|----------------------|------------------|---------|--------------|
| `login()` | Mock user validation | `/api/v1/auth/login` | POST | `{email, password}` |
| `signup()` | Mock user creation | `/api/v1/auth/signup` | POST | `{email, password, firstName, lastName, organizationName, industry, size, country, city}` |
| `logout()` | Clear localStorage | `/api/v1/auth/logout` | POST | - |
| `updateUser()` | Update localStorage | `/api/v1/users/me` | PATCH | `{firstName?, lastName?, ...}` |
| Dashboard data | Static JSON | `/api/v1/dashboard/stats` | GET | - |
| Forum topics | Not implemented | `/api/v1/forums/topics` | GET | - |
| Use cases list | Static JSON file | `/api/v1/use-cases` | GET | `?industry=&technology=&city=` |
| Submit use case | Not implemented | `/api/v1/use-cases` | POST | `{title, industry, technology[], problemStatement, solution, outcomes, vendorInfo, location}` |
| User management | Mock data | `/api/v1/users` | GET | - |

## API Endpoints Structure

### Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.p2psandbox.sa/api/v1
```

### Authentication Endpoints
```
POST   /auth/signup              # Organization + admin user creation
POST   /auth/login               # Email/password login
POST   /auth/logout              # Session logout
POST   /auth/refresh             # Refresh session token
POST   /auth/verify-email        # Email verification
POST   /auth/reset-password      # Request password reset
POST   /auth/reset-password/confirm # Confirm password reset
```

### User Management
```
GET    /users/me                 # Current user profile
PATCH  /users/me                 # Update current user profile
GET    /users                    # List organization users (admin only)
POST   /users/invite             # Invite team member (admin only)
GET    /users/{id}               # Get specific user profile
PATCH  /users/{id}               # Update user (admin only)
DELETE /users/{id}               # Deactivate user (admin only)
```

### Organization Management
```
GET    /organizations/current    # Current organization details
PATCH  /organizations/current    # Update organization (admin only)
GET    /organizations/members    # List all members
GET    /organizations/stats      # Organization statistics
```

### Forum System
```
GET    /forums/topics            # List topics (paginated)
POST   /forums/topics            # Create new topic
GET    /forums/topics/{id}       # Get topic with posts
PATCH  /forums/topics/{id}       # Update topic (author/admin)
DELETE /forums/topics/{id}       # Delete topic (author/admin)
POST   /forums/topics/{id}/pin   # Pin/unpin topic (admin)

GET    /forums/topics/{id}/posts # Get posts for topic
POST   /forums/topics/{id}/posts # Add post to topic
GET    /forums/posts/{id}        # Get specific post
PATCH  /forums/posts/{id}        # Update post (author only)
DELETE /forums/posts/{id}        # Delete post (author/admin)

POST   /forums/posts/{id}/reply  # Reply to post
PATCH  /forums/replies/{id}      # Update reply
DELETE /forums/replies/{id}      # Delete reply
PATCH  /forums/replies/{id}/best # Mark as best answer
```

### Use Case Management
```
GET    /use-cases                # List with filters
POST   /use-cases                # Submit new use case
GET    /use-cases/{id}           # Get use case details
PATCH  /use-cases/{id}           # Update use case
DELETE /use-cases/{id}           # Delete use case
POST   /use-cases/{id}/publish   # Publish draft
POST   /use-cases/{id}/media     # Upload media files
DELETE /use-cases/{id}/media/{mediaId} # Delete media
```

### Messaging System
```
GET    /messages                 # List conversations
POST   /messages                 # Send new message
GET    /messages/{user_id}       # Get conversation with user
PATCH  /messages/{id}/read       # Mark message as read
DELETE /messages/{id}            # Delete message
```

### Search & Discovery
```
GET    /search                   # Global search
GET    /search/users             # Search users
GET    /search/use-cases         # Search use cases
GET    /search/forums            # Search forum content
```

### Dashboard & Analytics
```
GET    /dashboard/stats          # Activity statistics
GET    /dashboard/activity       # Recent activities
GET    /dashboard/trending       # Trending topics & use cases
```

## Integration Strategy

### 1. API Client Setup (Frontend)

Create a centralized API service:

```typescript
// frontend/src/services/api.ts
import axios from 'axios';
import Session from 'supertokens-auth-react/recipe/session';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for SuperTokens cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add SuperTokens interceptor
Session.addAxiosInterceptors(api);

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Session expired, SuperTokens will handle refresh
    } else if (error.response?.status === 403) {
      // Forbidden - redirect to appropriate page
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. Environment Configuration

Frontend `.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_SUPERTOKENS_URL=http://localhost:3567
VITE_SUPERTOKENS_APP_NAME=P2PSandbox
```

Backend `.env`:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost/p2p_sandbox
MONGODB_URL=mongodb://localhost:27017/p2p_sandbox

# SuperTokens
SUPERTOKENS_CONNECTION_URI=http://localhost:3567
SUPERTOKENS_API_KEY=your-api-key

# Security
SECRET_KEY=your-secret-key
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# AWS/Azure for file storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=p2p-sandbox-media

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password
```

### 3. Update AuthContext

Replace mock implementation with API calls:

```typescript
// frontend/src/contexts/AuthContext.tsx
import api from '@/services/api';

const login = async (credentials: LoginCredentials): Promise<void> => {
  try {
    const response = await api.post('/auth/login', credentials);
    const { user, organization } = response.data;
    
    setAuthState({
      user,
      organization,
      isAuthenticated: true,
      isLoading: false
    });
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Login failed');
  }
};

const signup = async (data: SignupData): Promise<void> => {
  try {
    const response = await api.post('/auth/signup', data);
    const { user, organization } = response.data;
    
    setAuthState({
      user,
      organization,
      isAuthenticated: true,
      isLoading: false
    });
  } catch (error) {
    throw new Error(error.response?.data?.message || 'Signup failed');
  }
};
```

### 4. CORS Configuration (Backend)

```python
# backend/app/core/config.py
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"

# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Error Handling

Standardized error response format:

```python
# backend/app/core/exceptions.py
from fastapi import HTTPException
from typing import Any, Dict

class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "message": message,
                "error_code": error_code,
                "details": details or {}
            }
        )
```

## Implementation Order

### Phase 1 - Foundation (Week 1)
1. Set up FastAPI project structure
2. Configure PostgreSQL and MongoDB connections
3. Implement basic models for User and Organization
4. Create Pydantic schemas
5. Set up Alembic for migrations
6. Configure logging and error handling
7. Implement health check endpoint

### Phase 2 - Authentication (Week 1-2)
1. Integrate SuperTokens
2. Implement signup endpoint with org creation
3. Implement login endpoint
4. Add session management
5. Create protected route decorators
6. Implement password reset flow
7. Test with frontend login/signup pages

### Phase 3 - User Management (Week 2)
1. User profile endpoints
2. Organization member management
3. User invitation system
4. Role-based access control
5. Update frontend UserManagement page

### Phase 4 - Core Features (Week 3-4)
1. Forum system:
   - Topic CRUD operations
   - Post and reply functionality
   - Best answer feature
2. Use case submission:
   - CRUD operations
   - Media upload to S3/Azure
   - Location picker integration
3. Dashboard statistics API

### Phase 5 - Advanced Features (Week 4-5)
1. Messaging system
2. Search functionality:
   - Elasticsearch integration (optional)
   - Full-text search in PostgreSQL
3. Activity tracking
4. Real-time updates with WebSockets

### Phase 6 - Integration & Polish (Week 5-6)
1. Update all frontend API calls
2. Comprehensive error handling
3. Performance optimization:
   - Database query optimization
   - Caching with Redis
   - API response compression
4. Security audit
5. API documentation with OpenAPI
6. Docker containerization

## Key Technical Decisions

### Dependencies to Install

```txt
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
motor==3.3.2
supertokens-python==0.17.0
pydantic==2.5.0
pydantic-settings==2.1.0
alembic==1.12.1
python-multipart==0.0.6
boto3==1.29.7
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.25.2
redis==5.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
```

### Development Tools

1. **Code Quality**
   - Black for code formatting
   - Flake8 for linting
   - MyPy for type checking
   - Pre-commit hooks

2. **Testing**
   - Pytest for unit tests
   - Pytest-asyncio for async tests
   - Httpx for API testing
   - Factory Boy for test data

3. **Documentation**
   - OpenAPI/Swagger (built-in with FastAPI)
   - Redoc for API documentation
   - Docstrings for code documentation

### Security Considerations

1. **Input Validation**
   - Use Pydantic models for all inputs
   - Validate file uploads (type, size)
   - Sanitize user-generated content

2. **Authentication & Authorization**
   - SuperTokens for session management
   - Role-based access control
   - API key for service-to-service

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS in production
   - Implement rate limiting
   - SQL injection prevention with ORM

4. **Monitoring & Logging**
   - Structured logging with JSON
   - Error tracking with Sentry
   - Performance monitoring
   - Audit logs for sensitive actions

## Development Steps

### Step 1: Initial Setup
```bash
cd p2p-backend-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Database Setup
```bash
# PostgreSQL
createdb p2p_sandbox

# Run migrations
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Step 3: Environment Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Step 4: Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

### Step 5: Frontend Integration
1. Update frontend environment variables
2. Replace mock API calls with real endpoints
3. Test authentication flow
4. Implement remaining features

## Testing Strategy

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Focus on business logic

### Integration Tests
- Test API endpoints
- Use test database
- Verify request/response contracts

### End-to-End Tests
- Test complete user flows
- Frontend + Backend integration
- Use Cypress or Playwright

### Performance Tests
- Load testing with Locust
- Database query optimization
- API response time monitoring

## Deployment Considerations

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist
- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] Database backups configured
- [ ] Monitoring and alerts set up
- [ ] Rate limiting implemented
- [ ] Security headers configured
- [ ] API documentation updated
- [ ] Load balancing configured
- [ ] CI/CD pipeline set up
- [ ] Rollback strategy defined

## Monitoring and Maintenance

### Key Metrics to Track
1. API response times
2. Error rates
3. Database query performance
4. User activity patterns
5. Resource utilization

### Regular Maintenance Tasks
1. Database optimization
2. Log rotation
3. Security updates
4. Performance tuning
5. Backup verification

## Additional Resources

### Documentation Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SuperTokens Documentation](https://supertokens.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Motor (Async MongoDB) Documentation](https://motor.readthedocs.io/)

### Best Practices
- Follow REST API conventions
- Use semantic versioning
- Document all endpoints
- Write comprehensive tests
- Monitor production closely

---

This documentation serves as the complete guide for building the P2P Sandbox backend and integrating it with the existing frontend. Follow the implementation order and refer to specific sections as needed during development.