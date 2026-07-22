from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from datetime import datetime
from typing import List, Optional
from pathlib import Path
import logging
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.services.s3_service import SAFE_CONTENT_TYPE_EXTENSIONS, s3_service
from app.models.pg_models import User, UserMedia
from app.models.mongo_models import User as MongoUser, ForumPost, ForumReply, UseCase
from sqlalchemy import select
from bson import ObjectId
from app.core.upload_validation import validate_upload_file

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB for images
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB for videos
ALLOWED_PROFILE_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_FORUM_ATTACHMENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4", "video/webm"}
ALLOWED_USECASE_MEDIA_TYPES = {"image/jpeg", "image/png", "image/webp", "video/mp4", "video/webm"}
LOCAL_FORUM_MEDIA_ROOT = Path("/app/uploads/forum")
LOCAL_USECASE_MEDIA_ROOT = Path("/app/uploads/usecases")


def _save_local_forum_attachment(target_id: str, content: bytes, mime_type: str) -> tuple[str, str]:
    """Development fallback when the configured object-storage credentials are unavailable."""
    extension = SAFE_CONTENT_TYPE_EXTENSIONS[mime_type]
    generated_name = f"{uuid.uuid4()}.{extension}"
    target_dir = LOCAL_FORUM_MEDIA_ROOT / target_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / generated_name
    target_path.write_bytes(content)
    key = f"local/{target_id}/{generated_name}"
    return f"/api/v1/media/forum-files/{target_id}/{generated_name}", key


def _save_local_usecase_media(usecase_id: str, content: bytes, mime_type: str) -> tuple[str, str]:
    """Persist development use-case media when object storage is not in use."""
    extension = SAFE_CONTENT_TYPE_EXTENSIONS[mime_type]
    generated_name = f"{uuid.uuid4()}.{extension}"
    target_dir = LOCAL_USECASE_MEDIA_ROOT / usecase_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / generated_name
    target_path.write_bytes(content)
    key = f"local/{usecase_id}/{generated_name}"
    return f"/api/v1/media/usecase-files/{usecase_id}/{generated_name}", key


@router.get("/forum-files/{target_id}/{filename}")
async def get_local_forum_attachment(target_id: str, filename: str):
    if settings.ENVIRONMENT.lower() == "production":
        raise HTTPException(404, "Not found")
    if not ObjectId.is_valid(target_id) or Path(filename).name != filename:
        raise HTTPException(400, "Invalid media path")
    path = LOCAL_FORUM_MEDIA_ROOT / target_id / filename
    if not path.is_file():
        raise HTTPException(404, "Attachment not found")
    return FileResponse(path)


@router.get("/usecase-files/{usecase_id}/{filename}")
async def get_local_usecase_media(usecase_id: str, filename: str):
    if settings.ENVIRONMENT.lower() == "production":
        raise HTTPException(404, "Not found")
    if not ObjectId.is_valid(usecase_id) or Path(filename).name != filename:
        raise HTTPException(400, "Invalid media path")
    path = LOCAL_USECASE_MEDIA_ROOT / usecase_id / filename
    if not path.is_file():
        raise HTTPException(404, "Media not found")
    return FileResponse(path)


@router.post("/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload profile picture for the current user

    Supports: JPEG, PNG, WebP
    Max size: 5MB
    """
    try:
        # Validate actual file bytes before trusting user-controlled metadata
        validated_file = await validate_upload_file(
            file,
            allowed_mime_types=ALLOWED_PROFILE_IMAGE_TYPES,
            max_size=MAX_FILE_SIZE,
            purpose="profile picture",
        )

        # Get user from session
        supertokens_user_id = session.get_user_id()
        result = await db.execute(
            select(User).where(User.supertokens_id == supertokens_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        file_content = validated_file.content

        # Delete old profile picture if exists
        if user.profile_picture_url:
            await s3_service.delete_file(
                user.profile_picture_url,
                s3_service._get_bucket_from_key("profile-pictures/")
            )

            # Delete old media record
            old_media = await db.execute(
                select(UserMedia).where(
                    UserMedia.user_id == user.id,
                    UserMedia.file_type == "profile_picture"
                )
            )
            old_media_record = old_media.scalar_one_or_none()
            if old_media_record:
                await db.delete(old_media_record)

        # Upload new profile picture
        cdn_url = await s3_service.upload_profile_picture(
            user_id=str(user.id),
            file_content=file_content,
            filename=validated_file.safe_filename,
            content_type=validated_file.mime_type
        )

        # Update PostgreSQL user record
        user.profile_picture_url = cdn_url
        user.updated_at = datetime.utcnow()

        # Create media tracking record
        media_record = UserMedia(
            user_id=user.id,
            file_type="profile_picture",
            original_filename=validated_file.original_filename,
            s3_key=s3_service._extract_s3_key_from_url(cdn_url),
            s3_url=cdn_url,
            file_size=len(file_content),
            mime_type=validated_file.mime_type,
            context_id=str(user.id)
        )
        db.add(media_record)
        await db.commit()

        # Update MongoDB user profile too
        mongo_user = await MongoUser.find_one(MongoUser.email == user.email)
        if mongo_user:
            mongo_user.profile_picture_url = cdn_url
            mongo_user.updated_at = datetime.utcnow()
            await mongo_user.save()

        return {
            "success": True,
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": cdn_url,
            "file_size": len(file_content)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading profile picture: {e}")
        raise HTTPException(500, "Internal server error during upload")

@router.post("/forum-attachment")
async def upload_forum_attachment(
    file: UploadFile = File(...),
    post_id: Optional[str] = Form(None),
    reply_id: Optional[str] = Form(None),
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Upload an image or video to a forum post or reply.

    Exactly one of ``post_id`` or ``reply_id`` must be supplied. Images may be
    up to 5 MB and videos up to 50 MB.
    """
    try:
        # Validate actual file bytes before trusting user-controlled metadata
        preliminary_allowed_video_types = {"video/mp4", "video/webm"}
        preliminary_max_size = MAX_VIDEO_SIZE if file.content_type in preliminary_allowed_video_types else MAX_FILE_SIZE
        validated_file = await validate_upload_file(
            file,
            allowed_mime_types=ALLOWED_FORUM_ATTACHMENT_TYPES,
            max_size=preliminary_max_size,
            purpose="forum attachment",
        )

        # Enforce final size limit using the verified MIME type
        max_size = MAX_VIDEO_SIZE if validated_file.mime_type.startswith("video/") else MAX_FILE_SIZE
        if len(validated_file.content) > max_size:
            max_mb = max_size // (1024 * 1024)
            raise HTTPException(400, f"File too large. Maximum size is {max_mb}MB for this file type.")

        # Get user from session
        supertokens_user_id = session.get_user_id()
        result = await db.execute(
            select(User).where(User.supertokens_id == supertokens_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == user.email)
        if not mongo_user:
            raise HTTPException(404, "User profile not found")

        if bool(post_id) == bool(reply_id):
            raise HTTPException(400, "Supply exactly one of post_id or reply_id")

        target_id = post_id or reply_id
        target = None
        try:
            if post_id:
                target = await ForumPost.find_one(ForumPost.id == ObjectId(post_id))
            else:
                target = await ForumReply.find_one(ForumReply.id == ObjectId(reply_id))
        except Exception:
            raise HTTPException(400, "Invalid forum post or reply ID")

        if not target:
            raise HTTPException(404, "Forum post or reply not found")
        if target.author_id != str(mongo_user.id) and user.role != "admin":
            raise HTTPException(403, "Only the author can upload attachments")
        if len(target.attachments or []) >= 5:
            raise HTTPException(400, "A forum post or reply can have at most 5 attachments")

        file_content = validated_file.content

        # Keep development media persistent in the bind-mounted app directory; production
        # continues to use OCI Object Storage and fails closed if that service is unavailable.
        if settings.ENVIRONMENT.lower() != "production":
            file_url, s3_key = _save_local_forum_attachment(target_id, file_content, validated_file.mime_type)
        else:
            file_url, s3_key = await s3_service.upload_forum_attachment(
                post_id=target_id,
                user_id=str(user.id),
                file_content=file_content,
                filename=validated_file.safe_filename,
                content_type=validated_file.mime_type
            )

        # Create media tracking record
        media_record = UserMedia(
            user_id=user.id,
            file_type="forum_attachment",
            original_filename=validated_file.original_filename,
            s3_key=s3_key,
            s3_url=file_url,
            file_size=len(file_content),
            mime_type=validated_file.mime_type,
            context_id=target_id
        )
        db.add(media_record)
        await db.commit()

        attachment_data = {
            "url": file_url,
            "filename": validated_file.original_filename,
            "type": validated_file.mime_type,
            "size": len(file_content)
        }
        target.attachments.append(attachment_data)
        await target.save()
        logger.info(f"Added forum attachment to {target_id}: {validated_file.original_filename}")

        return {
            "success": True,
            "message": "Attachment uploaded successfully",
            "attachment": {
                "url": file_url,
                "filename": validated_file.original_filename,
                "type": validated_file.mime_type,
                "size": len(file_content)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading forum attachment: {e}")
        raise HTTPException(500, "Internal server error during upload")

@router.post("/usecase-media")
async def upload_usecase_media(
    files: List[UploadFile] = File(...),
    usecase_id: str = Form(...),
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload multiple media files (images/videos) for use case

    Supports: Images (JPEG, PNG, WebP) and Videos (MP4, WebM)
    Max size: 5MB for images, 50MB for videos
    Max files: 10 per request
    """
    try:
        if len(files) > 10:
            raise HTTPException(400, "Too many files. Maximum 10 files per request.")

        # Get user from session
        supertokens_user_id = session.get_user_id()
        result = await db.execute(
            select(User).where(User.supertokens_id == supertokens_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        mongo_user = await MongoUser.find_one(MongoUser.email == user.email)
        if not mongo_user:
            raise HTTPException(404, "User profile not found")

        try:
            use_case = await UseCase.find_one(UseCase.id == ObjectId(usecase_id))
        except Exception:
            raise HTTPException(400, "Invalid use case ID")

        if not use_case:
            raise HTTPException(404, "Use case not found")
        if use_case.submitted_by != str(mongo_user.id) and user.role != "admin":
            raise HTTPException(403, "Only the use case owner can upload media")

        uploaded_files = []

        for file in files:
            # Validate actual file bytes before trusting user-controlled metadata
            preliminary_allowed_video_types = {"video/mp4", "video/webm"}
            preliminary_max_size = MAX_VIDEO_SIZE if file.content_type in preliminary_allowed_video_types else MAX_FILE_SIZE
            validated_file = await validate_upload_file(
                file,
                allowed_mime_types=ALLOWED_USECASE_MEDIA_TYPES,
                max_size=preliminary_max_size,
                purpose="use case media",
            )

            # Enforce final size limit using the verified MIME type
            is_video = validated_file.mime_type.startswith('video/')
            max_size = MAX_VIDEO_SIZE if is_video else MAX_FILE_SIZE
            if len(validated_file.content) > max_size:
                max_mb = max_size // (1024 * 1024)
                raise HTTPException(400, f"File {validated_file.original_filename} too large. Maximum size is {max_mb}MB.")

            file_content = validated_file.content

            # Keep development media persistent in the bind-mounted app directory; production
            # continues to use OCI Object Storage and fails closed if that service is unavailable.
            if settings.ENVIRONMENT.lower() != "production":
                file_url, s3_key = _save_local_usecase_media(
                    usecase_id, file_content, validated_file.mime_type
                )
            else:
                file_url, s3_key = await s3_service.upload_usecase_media(
                    usecase_id=usecase_id,
                    user_id=str(user.id),
                    file_content=file_content,
                    filename=validated_file.safe_filename,
                    content_type=validated_file.mime_type
                )

            # Create media tracking record
            media_record = UserMedia(
                user_id=user.id,
                file_type="usecase_media",
                original_filename=validated_file.original_filename,
                s3_key=s3_key,
                s3_url=file_url,
                file_size=len(file_content),
                mime_type=validated_file.mime_type,
                context_id=usecase_id
            )
            db.add(media_record)

            uploaded_files.append({
                "url": file_url,
                "filename": validated_file.original_filename,
                "type": validated_file.mime_type,
                "size": len(file_content),
                "is_video": is_video
            })

        await db.commit()

        # Update MongoDB UseCase to include the media URLs
        try:
            logger.info(f"Attempting to update UseCase {usecase_id} with media")
            if use_case:
                logger.info(f"Found UseCase {usecase_id}. Current images: {len(use_case.images) if use_case.images else 0}")

                # Add new media URLs to the images list
                if not use_case.images:
                    use_case.images = []

                initial_image_count = len(use_case.images)
                for file_info in uploaded_files:
                    if not file_info["is_video"]:  # Only add images, not videos
                        use_case.images.append(file_info["url"])
                        logger.info(f"Added image URL to use case: {file_info['url']}")
                    else:
                        # For videos, add to the videos array with metadata
                        if not use_case.videos:
                            use_case.videos = []
                        use_case.videos.append({
                            "url": file_info["url"],
                            "filename": file_info["filename"],
                            "type": file_info["type"]
                        })
                        logger.info(f"Added video URL to use case: {file_info['url']}")

                await use_case.save()
                logger.info(f"Successfully saved UseCase {usecase_id}. Images: {initial_image_count} -> {len(use_case.images)}")
            else:
                logger.warning(f"UseCase {usecase_id} not found in MongoDB when trying to add media")
        except Exception as e:
            logger.error(f"Error updating MongoDB UseCase {usecase_id} with media: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't fail the whole request if MongoDB update fails

        return {
            "success": True,
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "files": uploaded_files
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading use case media: {e}")
        raise HTTPException(500, "Internal server error during upload")

@router.delete("/{media_id}")
async def delete_media_file(
    media_id: str,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a media file by ID
    Only the owner can delete their media files
    """
    try:
        # Get user from session
        supertokens_user_id = session.get_user_id()
        result = await db.execute(
            select(User).where(User.supertokens_id == supertokens_user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(404, "User not found")

        # Find media record
        media_result = await db.execute(
            select(UserMedia).where(
                UserMedia.id == media_id,
                UserMedia.user_id == user.id
            )
        )
        media_record = media_result.scalar_one_or_none()

        if not media_record:
            raise HTTPException(404, "Media file not found or not owned by user")

        # Delete from S3
        bucket = s3_service._get_bucket_from_key(media_record.s3_key)
        await s3_service.delete_file(media_record.s3_url, bucket)

        # Delete database record
        await db.delete(media_record)

        # If it was a profile picture, update user record
        if media_record.file_type == "profile_picture":
            user.profile_picture_url = None

            # Update MongoDB too
            mongo_user = await MongoUser.find_one(MongoUser.email == user.email)
            if mongo_user:
                mongo_user.profile_picture_url = None
                await mongo_user.save()

        await db.commit()

        return {
            "success": True,
            "message": "Media file deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting media file: {e}")
        raise HTTPException(500, "Internal server error during deletion")

@router.get("/user/{user_id}")
async def get_user_media(
    user_id: str,
    file_type: Optional[str] = None,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get media files for a user
    Users can only access their own media files
    """
    try:
        # Get user from session
        supertokens_user_id = session.get_user_id()
        result = await db.execute(
            select(User).where(User.supertokens_id == supertokens_user_id)
        )
        current_user = result.scalar_one_or_none()

        if not current_user:
            raise HTTPException(404, "User not found")

        # Check if requesting own media or if admin
        if str(current_user.id) != user_id and current_user.role != "admin":
            raise HTTPException(403, "Access denied")

        # Build query
        query = select(UserMedia).where(UserMedia.user_id == user_id)
        if file_type:
            query = query.where(UserMedia.file_type == file_type)

        query = query.order_by(UserMedia.created_at.desc())

        result = await db.execute(query)
        media_files = result.scalars().all()

        return {
            "success": True,
            "media_files": [
                {
                    "id": str(media.id),
                    "file_type": media.file_type,
                    "filename": media.original_filename,
                    "url": media.s3_url,
                    "size": media.file_size,
                    "mime_type": media.mime_type,
                    "context_id": media.context_id,
                    "created_at": media.created_at.isoformat()
                }
                for media in media_files
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user media: {e}")
        raise HTTPException(500, "Internal server error")