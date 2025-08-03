# Story 3: Forum Post Creation and Management

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 8  
**Priority**: High  
**Dependencies**: Story 1 (User Profiles), Story 2 (Forum System)

## User Story
**As a** SME user (Factory Owner, Plant Engineer, Operations Manager)  
**I want** to create detailed forum posts with rich content and media attachments  
**So that** I can share technical problems, solutions, and documentation with my peers effectively

## Acceptance Criteria
- [ ] Rich text editor supports formatting, links, lists, and code blocks
- [ ] Users can upload documents (PDF, DOC, DOCX) up to 10MB each
- [ ] Users can upload images (JPG, PNG, GIF) up to 5MB each with preview
- [ ] Posts support industry-specific tags and automatic categorization suggestions
- [ ] Draft saving functionality preserves content during editing
- [ ] Post editing preserves formatting and allows media updates
- [ ] Post deletion moves content to "deleted" status (soft delete)
- [ ] Media files are virus-scanned before upload acceptance
- [ ] Content preview shows how post will appear before publishing
- [ ] Arabic and English content creation both fully supported

## Technical Specifications

### 1. File Upload Service

#### app/services/file_service.py
```python
import os
import uuid
import hashlib
from typing import Optional, List, Dict
from fastapi import UploadFile, HTTPException
from PIL import Image
import magic
from app.core.config import settings
from app.core.logging import logger
import boto3
from botocore.exceptions import ClientError

class FileService:
    def __init__(self):
        # AWS S3 configuration
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        
        # Allowed file types
        self.allowed_image_types = {'image/jpeg', 'image/png', 'image/gif'}
        self.allowed_document_types = {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        }
        
        # File size limits (bytes)
        self.max_image_size = 5 * 1024 * 1024  # 5MB
        self.max_document_size = 10 * 1024 * 1024  # 10MB
    
    async def upload_forum_attachment(
        self, 
        user_id: str, 
        file: UploadFile,
        post_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Upload file for forum post attachment"""
        
        # Validate file
        await self._validate_file(file)
        
        # Generate unique filename
        file_extension = self._get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Determine file type and path
        file_type = await self._determine_file_type(file)
        if file_type == "image":
            s3_key = f"forum/images/{user_id}/{unique_filename}"
        else:
            s3_key = f"forum/documents/{user_id}/{unique_filename}"
        
        try:
            # Read file content
            file_content = await file.read()
            await file.seek(0)  # Reset file pointer
            
            # Virus scan (implement with ClamAV or cloud service)
            if not await self._virus_scan(file_content):
                raise HTTPException(status_code=400, detail="File failed security scan")
            
            # Process image if needed
            if file_type == "image":
                file_content = await self._process_image(file_content, file.content_type)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'original_filename': file.filename,
                    'post_id': post_id or 'draft'
                }
            )
            
            # Generate signed URL for access
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            
            # Calculate file hash for deduplication
            file_hash = hashlib.md5(file_content).hexdigest()
            
            return {
                "type": file_type,
                "url": file_url,
                "s3_key": s3_key,
                "original_filename": file.filename,
                "size": len(file_content),
                "content_type": file.content_type,
                "hash": file_hash
            }
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")
        except Exception as e:
            logger.error(f"File processing failed: {e}")
            raise HTTPException(status_code=500, detail="File processing failed")
    
    async def delete_forum_attachment(self, s3_key: str, user_id: str) -> bool:
        """Delete forum attachment"""
        try:
            # Verify ownership
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            if response['Metadata'].get('user_id') != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this file")
            
            # Delete from S3
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
            
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            return False
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Check file size
        file_content = await file.read()
        file_size = len(file_content)
        await file.seek(0)  # Reset file pointer
        
        # Determine file type and validate
        mime_type = magic.from_buffer(file_content, mime=True)
        
        if mime_type in self.allowed_image_types:
            if file_size > self.max_image_size:
                raise HTTPException(status_code=400, detail="Image file too large (max 5MB)")
        elif mime_type in self.allowed_document_types:
            if file_size > self.max_document_size:
                raise HTTPException(status_code=400, detail="Document file too large (max 10MB)")
        else:
            raise HTTPException(status_code=400, detail="File type not allowed")
    
    async def _determine_file_type(self, file: UploadFile) -> str:
        """Determine if file is image or document"""
        file_content = await file.read()
        await file.seek(0)
        
        mime_type = magic.from_buffer(file_content, mime=True)
        
        if mime_type in self.allowed_image_types:
            return "image"
        elif mime_type in self.allowed_document_types:
            return "document"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    
    async def _process_image(self, image_data: bytes, content_type: str) -> bytes:
        """Process and optimize image"""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 1920x1920)
            max_size = (1920, 1920)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            output = io.BytesIO()
            format_map = {
                'image/jpeg': 'JPEG',
                'image/png': 'PNG',
                'image/gif': 'GIF'
            }
            
            image.save(output, format=format_map.get(content_type, 'JPEG'), quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            # Return original if processing fails
            return image_data
    
    async def _virus_scan(self, file_content: bytes) -> bool:
        """Virus scan file content (placeholder implementation)"""
        # In production, integrate with ClamAV or cloud antivirus service
        # For now, do basic checks
        
        # Check for suspicious patterns
        suspicious_patterns = [b'<script', b'javascript:', b'vbscript:']
        content_lower = file_content.lower()
        
        for pattern in suspicious_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        if '.' in filename:
            return '.' + filename.rsplit('.', 1)[1].lower()
        return ''
```

### 2. Post Creation API Endpoints

#### app/api/v1/endpoints/posts.py
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from typing import Optional, List
from app.schemas.posts import (
    PostCreateRequest, PostUpdateRequest, PostResponse, PostDraftResponse
)
from app.services.post_service import PostService
from app.services.file_service import FileService
from app.core.logging import logger

router = APIRouter()

@router.post("/", response_model=PostResponse)
async def create_post(
    post_data: PostCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Create a new forum post"""
    user_id = session.get_user_id()
    
    try:
        post = await PostService.create_post(user_id, post_data)
        return await PostService.get_post_response(post.id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Post creation failed: {e}")
        raise HTTPException(status_code=500, detail="Post creation failed")

@router.post("/drafts", response_model=PostDraftResponse)
async def save_draft(
    post_data: PostCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Save post as draft"""
    user_id = session.get_user_id()
    
    try:
        draft = await PostService.save_draft(user_id, post_data)
        return PostDraftResponse.from_post(draft)
    except Exception as e:
        logger.error(f"Draft saving failed: {e}")
        raise HTTPException(status_code=500, detail="Draft saving failed")

@router.get("/drafts", response_model=List[PostDraftResponse])
async def get_my_drafts(session: SessionContainer = Depends(verify_session())):
    """Get user's draft posts"""
    user_id = session.get_user_id()
    
    try:
        drafts = await PostService.get_user_drafts(user_id)
        return [PostDraftResponse.from_post(draft) for draft in drafts]
    except Exception as e:
        logger.error(f"Drafts fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load drafts")

@router.post("/upload-attachment")
async def upload_attachment(
    file: UploadFile = File(...),
    post_id: Optional[str] = Form(None),
    session: SessionContainer = Depends(verify_session())
):
    """Upload file attachment for post"""
    user_id = session.get_user_id()
    
    try:
        file_service = FileService()
        attachment = await file_service.upload_forum_attachment(user_id, file, post_id)
        return {"message": "File uploaded successfully", "attachment": attachment}
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    """Get a specific post"""
    user_id = session.get_user_id() if session else None
    
    try:
        post_response = await PostService.get_post_response(post_id, user_id)
        
        # Increment view count if not the author
        if user_id != post_response.author.id:
            await PostService.increment_view_count(post_id)
        
        return post_response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Post fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to load post")

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_data: PostUpdateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Update an existing post"""
    user_id = session.get_user_id()
    
    try:
        post = await PostService.update_post(post_id, user_id, post_data)
        return await PostService.get_post_response(post.id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Post update failed: {e}")
        raise HTTPException(status_code=500, detail="Post update failed")

@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Delete a post (soft delete)"""
    user_id = session.get_user_id()
    
    try:
        await PostService.delete_post(post_id, user_id)
        return {"message": "Post deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Post deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Post deletion failed")

@router.post("/{post_id}/upvote")
async def upvote_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Upvote a post"""
    user_id = session.get_user_id()
    
    try:
        result = await PostService.toggle_upvote(post_id, user_id)
        return {"message": "Vote recorded", "upvoted": result}
    except Exception as e:
        logger.error(f"Upvote failed: {e}")
        raise HTTPException(status_code=500, detail="Vote failed")

@router.post("/{post_id}/bookmark")
async def bookmark_post(
    post_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Bookmark a post"""
    user_id = session.get_user_id()
    
    try:
        result = await PostService.toggle_bookmark(post_id, user_id)
        return {"message": "Bookmark updated", "bookmarked": result}
    except Exception as e:
        logger.error(f"Bookmark failed: {e}")
        raise HTTPException(status_code=500, detail="Bookmark failed")
```

### 3. Post Schemas

#### app/schemas/posts.py
```python
from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime

class PostAttachment(BaseModel):
    type: str  # image, document
    url: str
    original_filename: str
    size: int
    content_type: str

class PostCreateRequest(BaseModel):
    title: str
    content: str
    category_id: str
    tags: List[str] = []
    content_type: str = "discussion"  # discussion, question, tutorial
    language: str = "en"
    attachments: List[PostAttachment] = []
    
    @validator('title')
    def validate_title(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Title must be at least 5 characters')
        if len(v) > 200:
            raise ValueError('Title must be less than 200 characters')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 20:
            raise ValueError('Content must be at least 20 characters')
        if len(v) > 50000:
            raise ValueError('Content must be less than 50,000 characters')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 5:
            raise ValueError('Maximum 5 tags allowed')
        return [tag.lower().strip() for tag in v if tag.strip()]

class PostUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[PostAttachment]] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if len(v.strip()) < 5:
                raise ValueError('Title must be at least 5 characters')
            if len(v) > 200:
                raise ValueError('Title must be less than 200 characters')
            return v.strip()
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            if len(v.strip()) < 20:
                raise ValueError('Content must be at least 20 characters')
            if len(v) > 50000:
                raise ValueError('Content must be less than 50,000 characters')
        return v

class PostAuthor(BaseModel):
    id: str
    name: str
    avatar: Optional[str]
    verification_status: str
    reputation_score: int
    role: str

class PostCategory(BaseModel):
    id: str
    name: str
    slug: str
    color: str

class PostResponse(BaseModel):
    id: str
    title: str
    slug: str
    content: str
    author: PostAuthor
    category: PostCategory
    tags: List[str]
    language: str
    content_type: str
    attachments: List[PostAttachment]
    
    # Engagement metrics
    view_count: int
    reply_count: int
    upvote_count: int
    bookmark_count: int
    
    # User interactions (if authenticated)
    user_upvoted: bool = False
    user_bookmarked: bool = False
    
    # Status
    status: str
    is_pinned: bool
    is_featured: bool
    has_best_answer: bool
    best_answer_id: Optional[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_reply_at: Optional[datetime]

class PostDraftResponse(BaseModel):
    id: str
    title: str
    content: str
    category_id: Optional[str]
    tags: List[str]
    attachments: List[PostAttachment]
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def from_post(cls, post):
        return cls(
            id=str(post.id),
            title=post.title,
            content=post.content,
            category_id=post.category_id,
            tags=post.tags,
            attachments=post.attachments,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
```

### 4. Post Service Implementation

#### app/services/post_service.py
```python
from typing import Optional, List
from datetime import datetime
from app.models.mongo_models import ForumPost, ForumCategory, UserProfile
from app.schemas.posts import PostCreateRequest, PostUpdateRequest, PostResponse, PostAuthor, PostCategory
from app.core.logging import logger

class PostService:
    @staticmethod
    async def create_post(user_id: str, post_data: PostCreateRequest) -> ForumPost:
        """Create a new forum post"""
        # Get user profile
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not user_profile:
            raise ValueError("User profile not found")
        
        # Get category
        category = await ForumCategory.find_one(ForumCategory.id == post_data.category_id)
        if not category:
            raise ValueError("Category not found")
        
        # Check if category requires verification
        if category.requires_verification and user_profile.verification_status != "verified":
            raise ValueError("This category requires verified users")
        
        # Create post
        post = ForumPost(
            title=post_data.title,
            content=post_data.content,
            author_id=user_id,
            author_name=user_profile.name,
            author_avatar=user_profile.profile_picture_url,
            author_verification_status=user_profile.verification_status,
            category_id=post_data.category_id,
            category_name=category.name,
            tags=post_data.tags,
            language=post_data.language,
            content_type=post_data.content_type,
            attachments=[att.dict() for att in post_data.attachments],
            status="published"
        )
        
        await post.create()
        
        # Update category statistics
        await PostService._update_category_stats(post_data.category_id)
        
        # Update user statistics
        user_profile.forum_posts_count += 1
        user_profile.last_activity_at = datetime.utcnow()
        await user_profile.save()
        
        logger.info(f"Post created: {post.id} by user {user_id}")
        return post
    
    @staticmethod
    async def save_draft(user_id: str, post_data: PostCreateRequest) -> ForumPost:
        """Save post as draft"""
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not user_profile:
            raise ValueError("User profile not found")
        
        # Create draft post
        draft = ForumPost(
            title=post_data.title,
            content=post_data.content,
            author_id=user_id,
            author_name=user_profile.name,
            author_avatar=user_profile.profile_picture_url,
            author_verification_status=user_profile.verification_status,
            category_id=post_data.category_id,
            category_name="",  # Will be set when published
            tags=post_data.tags,
            language=post_data.language,
            content_type=post_data.content_type,
            attachments=[att.dict() for att in post_data.attachments],
            status="draft"
        )
        
        await draft.create()
        logger.info(f"Draft saved: {draft.id} by user {user_id}")
        return draft
    
    @staticmethod
    async def get_user_drafts(user_id: str) -> List[ForumPost]:
        """Get user's draft posts"""
        drafts = await ForumPost.find(
            ForumPost.author_id == user_id,
            ForumPost.status == "draft"
        ).sort([("updated_at", -1)]).to_list()
        
        return drafts
    
    @staticmethod
    async def get_post_response(post_id: str, user_id: Optional[str] = None) -> PostResponse:
        """Get post with full details for response"""
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if not post or post.status == "deleted":
            raise ValueError("Post not found")
        
        # Get author profile for additional details
        author_profile = await UserProfile.find_one(UserProfile.user_id == post.author_id)
        
        author = PostAuthor(
            id=post.author_id,
            name=post.author_name,
            avatar=post.author_avatar,
            verification_status=post.author_verification_status,
            reputation_score=author_profile.reputation_score if author_profile else 0,
            role=author_profile.role if author_profile else "user"
        )
        
        # Get category details
        category = await ForumCategory.find_one(ForumCategory.id == post.category_id)
        category_info = PostCategory(
            id=post.category_id,
            name=post.category_name,
            slug=category.slug if category else "",
            color=category.color if category else "#6B7280"
        )
        
        # Check user interactions if authenticated
        user_upvoted = False
        user_bookmarked = False
        
        if user_id:
            # Check if user has upvoted (implement user votes tracking)
            # user_upvoted = await PostVote.find_one(...)
            # user_bookmarked = await PostBookmark.find_one(...)
            pass
        
        return PostResponse(
            id=str(post.id),
            title=post.title,
            slug=post.slug,
            content=post.content,
            author=author,
            category=category_info,
            tags=post.tags,
            language=post.language,
            content_type=post.content_type,
            attachments=post.attachments,
            view_count=post.view_count,
            reply_count=post.reply_count,
            upvote_count=post.upvote_count,
            bookmark_count=post.bookmark_count,
            user_upvoted=user_upvoted,
            user_bookmarked=user_bookmarked,
            status=post.status,
            is_pinned=post.is_pinned,
            is_featured=post.is_featured,
            has_best_answer=post.has_best_answer,
            best_answer_id=post.best_answer_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
            last_reply_at=post.last_reply_at
        )
    
    @staticmethod
    async def update_post(post_id: str, user_id: str, update_data: PostUpdateRequest) -> ForumPost:
        """Update an existing post"""
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if not post:
            raise ValueError("Post not found")
        
        if post.author_id != user_id:
            raise PermissionError("Not authorized to edit this post")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if key == "category_id" and value:
                # Update category name as well
                category = await ForumCategory.find_one(ForumCategory.id == value)
                if category:
                    post.category_id = value
                    post.category_name = category.name
            else:
                setattr(post, key, value)
        
        post.updated_at = datetime.utcnow()
        await post.save()
        
        logger.info(f"Post updated: {post_id} by user {user_id}")
        return post
    
    @staticmethod
    async def delete_post(post_id: str, user_id: str):
        """Delete a post (soft delete)"""
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if not post:
            raise ValueError("Post not found")
        
        if post.author_id != user_id:
            raise PermissionError("Not authorized to delete this post")
        
        post.status = "deleted"
        post.updated_at = datetime.utcnow()
        await post.save()
        
        # Update category statistics
        await PostService._update_category_stats(post.category_id)
        
        logger.info(f"Post deleted: {post_id} by user {user_id}")
    
    @staticmethod
    async def increment_view_count(post_id: str):
        """Increment post view count"""
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if post:
            post.view_count += 1
            await post.save()
    
    @staticmethod
    async def toggle_upvote(post_id: str, user_id: str) -> bool:
        """Toggle upvote for a post"""
        # Implement user voting system (requires additional model)
        # For now, just increment/decrement upvote count
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if not post:
            raise ValueError("Post not found")
        
        # In a real implementation, check if user already voted
        # and toggle accordingly
        post.upvote_count += 1
        await post.save()
        return True
    
    @staticmethod
    async def toggle_bookmark(post_id: str, user_id: str) -> bool:
        """Toggle bookmark for a post"""
        # Implement user bookmark system
        # For now, just increment bookmark count
        post = await ForumPost.find_one(ForumPost.id == post_id)
        if not post:
            raise ValueError("Post not found")
        
        post.bookmark_count += 1
        await post.save()
        return True
    
    @staticmethod
    async def _update_category_stats(category_id: str):
        """Update category post count and last activity"""
        category = await ForumCategory.find_one(ForumCategory.id == category_id)
        if not category:
            return
        
        # Count active posts in category
        post_count = await ForumPost.find(
            ForumPost.category_id == category_id,
            ForumPost.status == "published"
        ).count()
        
        # Get latest post
        latest_post = await ForumPost.find(
            ForumPost.category_id == category_id,
            ForumPost.status == "published"
        ).sort([("created_at", -1)]).first_or_none()
        
        category.post_count = post_count
        category.last_activity_at = datetime.utcnow()
        if latest_post:
            category.last_post_id = str(latest_post.id)
        
        await category.save()
```

### 5. Frontend Rich Text Editor Component

#### Create frontend/src/components/Forum/PostEditor.tsx
```typescript
import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Upload, X, FileText, Image as ImageIcon } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

const postSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters').max(200),
  content: z.string().min(20, 'Content must be at least 20 characters'),
  category_id: z.string().min(1, 'Category is required'),
  content_type: z.string().default('discussion'),
  language: z.string().default('en'),
});

type PostFormData = z.infer<typeof postSchema>;

interface Attachment {
  type: string;
  url: string;
  original_filename: string;
  size: number;
  content_type: string;
}

interface PostEditorProps {
  onSubmit: (data: PostFormData & { tags: string[], attachments: Attachment[] }) => Promise<void>;
  onSaveDraft: (data: PostFormData & { tags: string[], attachments: Attachment[] }) => Promise<void>;
  initialData?: Partial<PostFormData>;
  categories: Array<{ id: string; name: string; slug: string }>;
  isLoading?: boolean;
}

export default function PostEditor({ 
  onSubmit, 
  onSaveDraft, 
  initialData, 
  categories, 
  isLoading 
}: PostEditorProps) {
  const { t } = useTranslation();
  const [content, setContent] = useState(initialData?.content || '');
  const [tags, setTags] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [uploadingFiles, setUploadingFiles] = useState<string[]>([]);

  const form = useForm<PostFormData>({
    resolver: zodResolver(postSchema),
    defaultValues: {
      title: '',
      content: '',
      category_id: '',
      content_type: 'discussion',
      language: 'en',
      ...initialData
    }
  });

  const quillModules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      ['link', 'blockquote', 'code-block'],
      [{ 'align': [] }],
      ['clean']
    ],
  };

  const quillFormats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'indent', 'link', 'blockquote', 
    'code-block', 'align'
  ];

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploadingFiles(prev => [...prev, ...acceptedFiles.map(f => f.name)]);

    for (const file of acceptedFiles) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/v1/posts/upload-attachment', {
          method: 'POST',
          body: formData,
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const result = await response.json();
        setAttachments(prev => [...prev, result.attachment]);
      } catch (error) {
        console.error('File upload failed:', error);
        // Show error toast
      } finally {
        setUploadingFiles(prev => prev.filter(name => name !== file.name));
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const addTag = () => {
    if (currentTag && !tags.includes(currentTag) && tags.length < 5) {
      setTags([...tags, currentTag]);
      setCurrentTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = async (data: PostFormData) => {
    const submitData = {
      ...data,
      content,
      tags,
      attachments
    };

    try {
      await onSubmit(submitData);
    } catch (error) {
      console.error('Post submission failed:', error);
    }
  };

  const handleSaveDraft = async () => {
    const data = form.getValues();
    const draftData = {
      ...data,
      content,
      tags,
      attachments
    };

    try {
      await onSaveDraft(draftData);
    } catch (error) {
      console.error('Draft saving failed:', error);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>{t('forum.post.create_title')}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
          {/* Title */}
          <div>
            <Label htmlFor="title">{t('forum.post.title')}</Label>
            <Input
              id="title"
              {...form.register('title')}
              placeholder={t('forum.post.title_placeholder')}
              className="text-lg"
            />
            {form.formState.errors.title && (
              <p className="text-sm text-red-600 mt-1">
                {form.formState.errors.title.message}
              </p>
            )}
          </div>

          {/* Category and Type */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="category">{t('forum.post.category')}</Label>
              <Select onValueChange={(value) => form.setValue('category_id', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('forum.post.select_category')} />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {form.formState.errors.category_id && (
                <p className="text-sm text-red-600 mt-1">
                  {form.formState.errors.category_id.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="content_type">{t('forum.post.type')}</Label>
              <Select onValueChange={(value) => form.setValue('content_type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('forum.post.select_type')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="discussion">{t('forum.post.types.discussion')}</SelectItem>
                  <SelectItem value="question">{t('forum.post.types.question')}</SelectItem>
                  <SelectItem value="tutorial">{t('forum.post.types.tutorial')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Tags */}
          <div>
            <Label>{t('forum.post.tags')}</Label>
            <div className="flex flex-wrap gap-2 mb-2">
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  <X
                    className="h-3 w-3 cursor-pointer"
                    onClick={() => removeTag(tag)}
                  />
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={currentTag}
                onChange={(e) => setCurrentTag(e.target.value)}
                placeholder={t('forum.post.add_tag')}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              />
              <Button type="button" onClick={addTag} variant="outline">
                {t('forum.post.add')}
              </Button>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {tags.length}/5 {t('forum.post.tags_limit')}
            </p>
          </div>

          {/* Content Editor */}
          <div>
            <Label>{t('forum.post.content')}</Label>
            <div className="mt-2">
              <ReactQuill
                theme="snow"
                value={content}
                onChange={setContent}
                modules={quillModules}
                formats={quillFormats}
                placeholder={t('forum.post.content_placeholder')}
                style={{ height: '300px', marginBottom: '50px' }}
              />
            </div>
            {form.formState.errors.content && (
              <p className="text-sm text-red-600 mt-1">
                {form.formState.errors.content.message}
              </p>
            )}
          </div>

          {/* File Upload */}
          <div>
            <Label>{t('forum.post.attachments')}</Label>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600">
                {isDragActive
                  ? t('forum.post.drop_files')
                  : t('forum.post.drag_drop_files')
                }
              </p>
              <p className="text-xs text-gray-500 mt-2">
                {t('forum.post.supported_formats')}
              </p>
            </div>

            {/* Attachment List */}
            {attachments.length > 0 && (
              <div className="mt-4 space-y-2">
                {attachments.map((attachment, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {attachment.type === 'image' ? (
                        <ImageIcon className="h-5 w-5 text-blue-500" />
                      ) : (
                        <FileText className="h-5 w-5 text-gray-500" />
                      )}
                      <div>
                        <p className="text-sm font-medium">{attachment.original_filename}</p>
                        <p className="text-xs text-gray-500">
                          {(attachment.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeAttachment(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Uploading Files */}
            {uploadingFiles.length > 0 && (
              <div className="mt-4 space-y-2">
                {uploadingFiles.map((filename) => (
                  <div key={filename} className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                    <p className="text-sm">{t('forum.post.uploading')} {filename}...</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={handleSaveDraft}
              disabled={isLoading}
            >
              {t('forum.post.save_draft')}
            </Button>
            
            <Button type="submit" disabled={isLoading || !content.trim()}>
              {isLoading ? t('common.publishing') : t('forum.post.publish')}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

## Implementation Steps

1. **File Upload Infrastructure**
   ```bash
   # Set up AWS S3 bucket with proper permissions
   # Configure file processing and virus scanning
   # Implement image optimization pipeline
   ```

2. **Database Updates**
   ```bash
   # Apply ForumPost schema updates
   # Create file attachment tracking
   # Set up indexes for performance
   ```

3. **Backend Implementation**
   ```bash
   # Implement PostService and FileService
   # Create API endpoints for post CRUD operations
   # Add file upload and processing logic
   ```

4. **Frontend Rich Editor**
   ```bash
   # Integrate ReactQuill for rich text editing
   # Implement drag-and-drop file upload
   # Add preview and draft saving functionality
   ```

## Testing Checklist
- [ ] Rich text editor saves formatting correctly
- [ ] File upload works for images and documents
- [ ] Virus scanning prevents malicious uploads
- [ ] Draft auto-saving preserves content
- [ ] Post editing maintains formatting
- [ ] File size limits are enforced
- [ ] Arabic text input and display work properly
- [ ] Category and tag selection function
- [ ] Post deletion (soft delete) works
- [ ] Mobile responsiveness verified

## Security Considerations
- [ ] All uploaded files are virus scanned
- [ ] File size and type restrictions enforced
- [ ] Input sanitization prevents XSS attacks
- [ ] User permissions validated for all operations
- [ ] Secure file storage with access controls

## Dependencies
- Story 1 (User Profile Management) completed
- Story 2 (Forum System) completed
- AWS S3 or equivalent file storage configured
- Image processing service available

## Notes
- Implement comprehensive content moderation
- Consider file deduplication to save storage costs
- Plan for content versioning and edit history
- Optimize for mobile content creation experience