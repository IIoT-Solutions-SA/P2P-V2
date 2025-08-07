# Use Cases Module Design

## Overview
Comprehensive design document for the Use Cases module (Phase 5), detailing MongoDB schemas, API specifications, and implementation approach.

---

## MongoDB Schema Design

### Main UseCase Collection

```javascript
{
  "_id": ObjectId("..."),
  "id": "uuid-v4",  // For API responses
  "organization_id": "uuid-v4",
  
  // Basic Information
  "title": "AI-Powered Quality Inspection System Reduces Defects by 85%",
  "company": "Advanced Manufacturing Co.",
  "industry": "Electronics Manufacturing",
  "category": "quality",  // Enum: automation|quality|maintenance|efficiency|innovation|sustainability
  
  // Detailed Content
  "description": "Implementation of computer vision and machine learning...",
  "challenge": "High defect rates in PCB manufacturing leading to...",
  "solution": "Deployed custom AI model trained on 100,000 images...",
  "implementation": {
    "timeline": "6 months",
    "phases": [
      {
        "phase": 1,
        "title": "Assessment & Planning",
        "duration": "1 month",
        "description": "Initial analysis of current processes..."
      }
    ],
    "team_size": 8,
    "budget_range": "$100K-$500K"
  },
  
  // Results & Metrics
  "results": {
    "metrics": [
      {
        "name": "Defect Reduction",
        "value": "85%",
        "baseline": "12%",
        "current": "1.8%",
        "improvement_percentage": 85
      },
      {
        "name": "Cost Savings",
        "value": "$2.3M",
        "period": "annually",
        "breakdown": {
          "labor": "$800K",
          "materials": "$1.2M",
          "rework": "$300K"
        }
      },
      {
        "name": "Efficiency",
        "value": "40% faster",
        "details": "Inspection time reduced from 5min to 3min per unit"
      }
    ],
    "roi": {
      "percentage": 230,
      "payback_period": "8 months",
      "total_investment": "$450K",
      "annual_return": "$2.3M"
    },
    "timeframe": "Results achieved within 6 months"
  },
  
  // Technologies & Tools
  "technologies": [
    "Computer Vision",
    "TensorFlow",
    "Python",
    "Edge Computing",
    "IoT Sensors"
  ],
  "vendors": [
    {
      "name": "NVIDIA",
      "product": "Jetson Edge AI",
      "category": "Hardware"
    },
    {
      "name": "Custom Development",
      "product": "In-house AI Model",
      "category": "Software"
    }
  ],
  
  // Media & Attachments
  "media": [
    {
      "id": "uuid-v4",
      "type": "image",  // image|video|document|presentation
      "filename": "defect-detection-dashboard.jpg",
      "path": "uploads/use-cases/{org_id}/{use_case_id}/images/original/{filename}",
      "thumbnail_path": "uploads/use-cases/{org_id}/{use_case_id}/images/thumbnails/{filename}",
      "size": 2048576,  // bytes
      "mime_type": "image/jpeg",
      "caption": "Real-time defect detection dashboard",
      "order": 1,
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ],
  
  // Location
  "location": {
    "city": "Riyadh",
    "region": "Central Region",
    "country": "Saudi Arabia",
    "coordinates": {
      "lat": 24.7136,
      "lng": 46.6753
    }
  },
  
  // Publishing & Status
  "status": "published",  // draft|published|archived|under_review
  "visibility": "public",  // public|organization|private
  "published_by": {
    "user_id": "uuid-v4",
    "name": "Sarah Al-Mahmoud",
    "title": "Quality Engineering Director",
    "email": "sarah@company.com"  // Hidden in public API
  },
  
  // Engagement Metrics
  "metrics": {
    "views": 1247,
    "unique_views": 892,
    "likes": 89,
    "saves": 156,
    "shares": 45,
    "inquiries": 12,
    "avg_time_on_page": 245  // seconds
  },
  
  // Verification & Features
  "verification": {
    "verified": true,
    "verified_by": "admin-uuid",
    "verified_at": "2024-01-20T14:00:00Z",
    "verification_notes": "ROI metrics independently verified"
  },
  "featured": {
    "is_featured": true,
    "featured_until": "2024-12-31T23:59:59Z",
    "featured_by": "admin-uuid"
  },
  
  // Tags & Categorization
  "tags": [
    "AI",
    "Computer Vision",
    "Quality Control",
    "Automation",
    "ROI",
    "Best Practice"
  ],
  
  // Related Content
  "related_use_cases": [
    "uuid-1",
    "uuid-2"
  ],
  
  // Timestamps
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "published_at": "2024-01-15T10:30:00Z",
  "deleted_at": null  // Soft delete
}
```

### Supporting Collections

#### UseCaseDraft Collection
```javascript
{
  "_id": ObjectId,
  "use_case_id": "uuid-v4",
  "user_id": "uuid-v4",
  "organization_id": "uuid-v4",
  "draft_data": { /* Partial UseCase schema */ },
  "current_step": 2,  // Multi-step form progress
  "total_steps": 5,
  "last_saved": "2024-01-10T09:00:00Z",
  "expires_at": "2024-02-10T09:00:00Z"  // Auto-cleanup after 30 days
}
```

#### UseCaseView Collection (for analytics)
```javascript
{
  "_id": ObjectId,
  "use_case_id": "uuid-v4",
  "viewer_id": "uuid-v4",  // null for anonymous
  "organization_id": "uuid-v4",
  "session_id": "session-uuid",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "referrer": "https://p2p.sa/forum",
  "time_on_page": 245,  // seconds
  "actions": ["viewed", "liked", "saved"],
  "viewed_at": "2024-01-15T10:30:00Z"
}
```

---

## API Specifications

### 1. Create Use Case
**POST** `/api/v1/use-cases`

```json
// Request Body
{
  "title": "AI-Powered Quality Inspection System",
  "company": "Advanced Manufacturing Co.",
  "industry": "Electronics Manufacturing",
  "category": "quality",
  "description": "Implementation details...",
  "challenge": "Problem statement...",
  "solution": "Solution approach...",
  "implementation": {
    "timeline": "6 months",
    "phases": [...],
    "team_size": 8,
    "budget_range": "$100K-$500K"
  },
  "results": {
    "metrics": [...],
    "roi": {...},
    "timeframe": "6 months"
  },
  "technologies": ["AI", "IoT"],
  "location": {
    "city": "Riyadh",
    "region": "Central Region"
  },
  "status": "draft",
  "tags": ["AI", "Quality Control"]
}

// Response (201 Created)
{
  "id": "uuid-v4",
  "title": "AI-Powered Quality Inspection System",
  "status": "draft",
  "created_at": "2024-01-10T09:00:00Z",
  "message": "Use case created successfully"
}
```

### 2. Browse Use Cases
**GET** `/api/v1/use-cases`

Query Parameters:
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `category` (string): Filter by category
- `industry` (string): Filter by industry
- `technologies` (array): Filter by technologies
- `verified` (boolean): Show only verified cases
- `featured` (boolean): Show only featured cases
- `sort_by` (string): date|views|likes|roi (default: date)
- `order` (string): asc|desc (default: desc)
- `search` (string): Full-text search query

```json
// Response (200 OK)
{
  "data": [
    {
      "id": "uuid-v4",
      "title": "AI-Powered Quality Inspection System",
      "company": "Advanced Manufacturing Co.",
      "industry": "Electronics Manufacturing",
      "category": "quality",
      "description": "Brief description...",
      "results": {
        "key_metric": "85% defect reduction",
        "roi": "230%"
      },
      "thumbnail": "/media/use-cases/.../thumbnail.jpg",
      "tags": ["AI", "Quality Control"],
      "verified": true,
      "featured": true,
      "views": 1247,
      "likes": 89,
      "published_by": {
        "name": "Sarah Al-Mahmoud",
        "title": "Quality Engineering Director"
      },
      "published_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 89,
    "total_pages": 5
  },
  "filters_applied": {
    "category": "quality",
    "verified": true
  }
}
```

### 3. Get Use Case Details
**GET** `/api/v1/use-cases/{id}`

```json
// Response (200 OK)
{
  // Full UseCase object (excluding sensitive fields)
  "id": "uuid-v4",
  "title": "...",
  // ... all public fields ...
  "related_use_cases": [
    {
      "id": "uuid-1",
      "title": "Similar Implementation at Another Factory",
      "category": "quality",
      "roi": "180%"
    }
  ]
}
```

### 4. Update Use Case
**PATCH** `/api/v1/use-cases/{id}`

```json
// Request Body (partial update)
{
  "description": "Updated description...",
  "results": {
    "metrics": [...]
  },
  "status": "published"
}

// Response (200 OK)
{
  "id": "uuid-v4",
  "message": "Use case updated successfully",
  "updated_fields": ["description", "results", "status"]
}
```

### 5. Delete Use Case
**DELETE** `/api/v1/use-cases/{id}`

```json
// Response (200 OK)
{
  "message": "Use case deleted successfully",
  "deleted_at": "2024-01-20T10:00:00Z"
}
```

### 6. Upload Media
**POST** `/api/v1/use-cases/{id}/media`

Multipart form data:
- `file`: Binary file data
- `type`: image|video|document
- `caption`: Optional description

```json
// Response (201 Created)
{
  "media_id": "uuid-v4",
  "url": "/media/use-cases/.../filename.jpg",
  "thumbnail_url": "/media/use-cases/.../thumbnail.jpg",
  "type": "image",
  "size": 2048576,
  "message": "Media uploaded successfully"
}
```

### 7. Search Use Cases
**GET** `/api/v1/use-cases/search`

Query Parameters:
- `q` (string): Search query
- `fields` (array): Fields to search in (title, description, solution, tags)
- All browse filters also apply

```json
// Response (200 OK)
{
  "data": [...],
  "search_metadata": {
    "query": "AI quality inspection",
    "total_results": 15,
    "search_time_ms": 45
  }
}
```

### 8. Export Use Cases
**GET** `/api/v1/use-cases/export`

Query Parameters:
- `format`: pdf|excel|csv
- `ids` (array): Specific use case IDs to export
- Inherits browse filters

```json
// Response (200 OK)
{
  "export_url": "/exports/use-cases-2024-01-20.pdf",
  "expires_at": "2024-01-21T00:00:00Z",
  "format": "pdf",
  "total_items": 15
}
```

### 9. Save Draft
**POST** `/api/v1/use-cases/drafts`

```json
// Request Body
{
  "use_case_id": "uuid-v4",  // null for new draft
  "draft_data": {
    // Partial use case data
  },
  "current_step": 2
}

// Response (200 OK)
{
  "draft_id": "uuid-v4",
  "use_case_id": "uuid-v4",
  "saved_at": "2024-01-10T09:00:00Z",
  "expires_at": "2024-02-10T09:00:00Z"
}
```

### 10. Like/Unlike Use Case
**POST** `/api/v1/use-cases/{id}/like`

```json
// Response (200 OK)
{
  "liked": true,
  "total_likes": 90
}
```

---

## Implementation Details

### MongoDB Connection
```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, TEXT
import os

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None
    
    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(
            os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
            maxPoolSize=10,
            minPoolSize=2
        )
        cls.database = cls.client["p2p_sandbox"]
        
        # Create indexes
        await cls.create_indexes()
    
    @classmethod
    async def create_indexes(cls):
        use_cases = cls.database.use_cases
        
        # Text search index
        await use_cases.create_index([
            ("title", TEXT),
            ("description", TEXT),
            ("solution", TEXT),
            ("tags", TEXT)
        ])
        
        # Query optimization indexes
        await use_cases.create_index([("organization_id", ASCENDING)])
        await use_cases.create_index([("status", ASCENDING)])
        await use_cases.create_index([("category", ASCENDING)])
        await use_cases.create_index([("created_at", -1)])
        await use_cases.create_index([("metrics.views", -1)])
        
        # Compound indexes for common queries
        await use_cases.create_index([
            ("status", ASCENDING),
            ("organization_id", ASCENDING),
            ("created_at", -1)
        ])
```

### Service Layer
```python
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class UseCaseService:
    @staticmethod
    async def create_use_case(
        data: Dict[str, Any],
        user_id: UUID,
        organization_id: UUID
    ) -> str:
        """Create a new use case"""
        use_case = {
            **data,
            "id": str(uuid4()),
            "organization_id": str(organization_id),
            "published_by": {
                "user_id": str(user_id),
                # Add user details
            },
            "metrics": {
                "views": 0,
                "likes": 0,
                "saves": 0
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await MongoDB.database.use_cases.insert_one(use_case)
        return use_case["id"]
    
    @staticmethod
    async def browse_use_cases(
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Browse use cases with filters and pagination"""
        query = {"status": "published"}
        
        # Apply filters
        if filters.get("category"):
            query["category"] = filters["category"]
        if filters.get("verified"):
            query["verification.verified"] = True
        
        # Execute query with pagination
        skip = (page - 1) * page_size
        cursor = MongoDB.database.use_cases.find(query)
        cursor = cursor.skip(skip).limit(page_size)
        
        # Sort
        sort_field = filters.get("sort_by", "created_at")
        sort_order = -1 if filters.get("order", "desc") == "desc" else 1
        cursor = cursor.sort(sort_field, sort_order)
        
        # Get results
        use_cases = await cursor.to_list(length=page_size)
        total = await MongoDB.database.use_cases.count_documents(query)
        
        return {
            "data": use_cases,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
```

---

## Media Handling

### Local Storage Implementation
```python
from pathlib import Path
from PIL import Image
import aiofiles
import hashlib

class MediaService:
    UPLOAD_DIR = Path("uploads/use-cases")
    ALLOWED_IMAGES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ALLOWED_DOCS = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    THUMBNAIL_SIZE = (300, 200)
    
    @classmethod
    async def upload_media(
        cls,
        file: UploadFile,
        use_case_id: str,
        organization_id: str,
        media_type: str
    ) -> Dict[str, str]:
        """Upload and process media file"""
        # Validate file
        if file.size > cls.MAX_FILE_SIZE:
            raise ValueError("File too large")
        
        # Create directory structure
        upload_path = cls.UPLOAD_DIR / organization_id / use_case_id / media_type
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        ext = Path(file.filename).suffix
        file_hash = hashlib.md5(file.file.read()).hexdigest()
        filename = f"{file_hash}{ext}"
        file_path = upload_path / "original" / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(await file.read())
        
        # Generate thumbnail for images
        thumbnail_path = None
        if media_type == "image" and ext.lower() in cls.ALLOWED_IMAGES:
            thumbnail_path = await cls.generate_thumbnail(
                file_path,
                upload_path / "thumbnails" / filename
            )
        
        return {
            "path": str(file_path.relative_to(Path("uploads"))),
            "thumbnail_path": str(thumbnail_path.relative_to(Path("uploads"))) if thumbnail_path else None,
            "filename": file.filename,
            "size": file.size,
            "mime_type": file.content_type
        }
    
    @staticmethod
    async def generate_thumbnail(input_path: Path, output_path: Path) -> Path:
        """Generate thumbnail for image"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with Image.open(input_path) as img:
            img.thumbnail(MediaService.THUMBNAIL_SIZE)
            img.save(output_path, optimize=True, quality=85)
        
        return output_path
```

---

## Search Implementation

### Full-Text Search
```python
class SearchService:
    @staticmethod
    async def search_use_cases(
        query: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict]:
        """Full-text search across use cases"""
        search_query = {
            "$text": {"$search": query},
            "status": "published"
        }
        
        # Add additional filters
        if filters:
            search_query.update(filters)
        
        # Execute search with relevance score
        cursor = MongoDB.database.use_cases.find(
            search_query,
            {"score": {"$meta": "textScore"}}
        )
        
        # Sort by relevance
        cursor = cursor.sort([("score", {"$meta": "textScore"})])
        
        results = await cursor.to_list(length=100)
        return results
```

---

## Categories & Enums

```python
from enum import Enum

class UseCaseCategory(str, Enum):
    AUTOMATION = "automation"
    QUALITY = "quality"
    MAINTENANCE = "maintenance"
    EFFICIENCY = "efficiency"
    INNOVATION = "innovation"
    SUSTAINABILITY = "sustainability"

class UseCaseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    PRESENTATION = "presentation"
```

---

## Security Considerations

1. **File Upload Security**
   - Validate MIME types
   - Check file extensions
   - Scan for malware (future)
   - Limit file sizes
   - Generate new filenames

2. **Access Control**
   - Organization-scoped access
   - Owner-only editing
   - Admin moderation rights
   - Public/private visibility

3. **Data Protection**
   - Hide contact emails in public API
   - Sanitize HTML content
   - Rate limit submissions
   - Validate all inputs

---

## Performance Optimizations

1. **Database**
   - Create compound indexes
   - Use projection for list views
   - Implement pagination
   - Cache frequent queries

2. **Media**
   - Generate multiple thumbnail sizes
   - Lazy load images
   - Compress uploads
   - CDN preparation

3. **Search**
   - Text indexes for full-text search
   - Aggregate pipeline optimization
   - Search result caching
   - Relevance scoring

---

## Testing Strategy

1. **Unit Tests**
   - Schema validation
   - Service methods
   - Media processing
   - Search algorithms

2. **Integration Tests**
   - API endpoints
   - File uploads
   - MongoDB queries
   - Access control

3. **Performance Tests**
   - Large dataset queries
   - Concurrent uploads
   - Search performance
   - Image processing

---

## Future Enhancements

1. **AI Integration**
   - Auto-tagging with NLP
   - Similar use case recommendations
   - Content summarization
   - Trend analysis

2. **Advanced Features**
   - Version history
   - Collaborative editing
   - Use case templates
   - Impact tracking

3. **Analytics**
   - Detailed view analytics
   - Engagement metrics
   - ROI calculator
   - Benchmark comparisons