import boto3
import uuid
import logging
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    """Service for handling AWS S3 file uploads and management"""

    def __init__(self):
        """Initialize S3 client with AWS credentials"""
        try:
            if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
                logger.warning("AWS credentials not configured - S3 uploads will fail")
                self.s3_client = None
            else:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            self.s3_client = None

    def _check_s3_client(self):
        """Check if S3 client is properly initialized"""
        if not self.s3_client:
            raise HTTPException(500, "S3 service not configured. Please check AWS credentials.")

    async def upload_profile_picture(self, user_id: str, file_content: bytes,
                                   filename: str, content_type: str) -> str:
        """
        Upload profile picture to S3 and return CDN URL

        Args:
            user_id: UUID of the user
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            str: CDN URL of uploaded image
        """
        self._check_s3_client()

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if content_type not in allowed_types:
            raise HTTPException(400, f"Invalid file type. Allowed: {', '.join(allowed_types)}")

        # Generate unique S3 key
        file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
        s3_key = f"profile-pictures/{user_id}/{uuid.uuid4()}.{file_extension}"

        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.S3_PROFILE_PICTURES_BUCKET,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                CacheControl="max-age=31536000",  # 1 year cache
                # ACL removed - bucket access controlled via bucket policy
                Metadata={
                    'user_id': user_id,
                    'original_filename': filename,
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'file_type': 'profile_picture'
                }
            )

            # Generate URL
            return self._generate_url(s3_key)

        except ClientError as e:
            logger.error(f"Failed to upload profile picture to S3: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")

    async def upload_forum_attachment(self, post_id: str, user_id: str, file_content: bytes,
                                    filename: str, content_type: str) -> tuple[str, str]:
        """
        Upload forum attachment to S3

        Args:
            post_id: ID of the forum post
            user_id: ID of the uploading user
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            tuple: (file_url, s3_key)
        """
        self._check_s3_client()

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'video/mp4', 'video/webm']
        if content_type not in allowed_types:
            raise HTTPException(400, f"Invalid file type. Allowed: images and videos")

        # Generate unique S3 key
        file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
        s3_key = f"forum-attachments/{post_id}/{uuid.uuid4()}.{file_extension}"

        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.S3_FORUM_MEDIA_BUCKET,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                CacheControl="max-age=86400",  # 1 day cache
                # ACL removed - bucket has public access configured via bucket policy
                Metadata={
                    'post_id': post_id,
                    'user_id': user_id,
                    'original_filename': filename,
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'file_type': 'forum_attachment'
                }
            )

            return self._generate_url(s3_key), s3_key

        except ClientError as e:
            logger.error(f"Failed to upload forum attachment to S3: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")

    async def upload_usecase_media(self, usecase_id: str, user_id: str, file_content: bytes,
                                 filename: str, content_type: str) -> tuple[str, str]:
        """
        Upload use case media (images/videos) to S3

        Args:
            usecase_id: ID of the use case
            user_id: ID of the uploading user
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            tuple: (file_url, s3_key)
        """
        self._check_s3_client()

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/webm']
        if content_type not in allowed_types:
            raise HTTPException(400, f"Invalid file type. Allowed: images and videos")

        # Generate unique S3 key based on file type
        file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
        media_type = 'videos' if content_type.startswith('video/') else 'images'
        s3_key = f"usecase-{media_type}/{usecase_id}/{uuid.uuid4()}.{file_extension}"

        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.S3_USECASE_MEDIA_BUCKET,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                CacheControl="max-age=31536000",  # 1 year cache
                # ACL removed - bucket has public access configured via bucket policy
                Metadata={
                    'usecase_id': usecase_id,
                    'user_id': user_id,
                    'original_filename': filename,
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'file_type': 'usecase_media',
                    'media_type': media_type
                }
            )

            return self._generate_url(s3_key), s3_key

        except ClientError as e:
            logger.error(f"Failed to upload use case media to S3: {e}")
            raise HTTPException(500, f"Upload failed: {str(e)}")

    async def delete_file(self, s3_url: str, bucket: str):
        """
        Delete file from S3 using its URL

        Args:
            s3_url: URL of the file to delete
            bucket: S3 bucket name
        """
        if not self.s3_client:
            logger.warning("S3 client not configured - cannot delete file")
            return

        try:
            # Extract S3 key from URL
            s3_key = self._extract_s3_key_from_url(s3_url)

            self.s3_client.delete_object(
                Bucket=bucket,
                Key=s3_key
            )

            logger.info(f"Successfully deleted file: {s3_key}")

        except ClientError as e:
            logger.warning(f"Failed to delete from S3: {e}")
            # Don't fail the request if file deletion fails

    def _generate_url(self, s3_key: str) -> str:
        """Generate CDN URL or direct S3 URL for a file"""
        if settings.CLOUDFRONT_DOMAIN:
            return f"https://{settings.CLOUDFRONT_DOMAIN}/{s3_key}"
        else:
            # Fallback to direct S3 URL for development
            bucket = self._get_bucket_from_key(s3_key)
            return f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

    def _get_bucket_from_key(self, s3_key: str) -> str:
        """Determine which bucket to use based on S3 key prefix"""
        if s3_key.startswith('profile-pictures/'):
            return settings.S3_PROFILE_PICTURES_BUCKET
        elif s3_key.startswith('forum-attachments/'):
            return settings.S3_FORUM_MEDIA_BUCKET
        elif s3_key.startswith('usecase-'):
            return settings.S3_USECASE_MEDIA_BUCKET
        else:
            return settings.S3_PROFILE_PICTURES_BUCKET  # Default

    def _extract_s3_key_from_url(self, url: str) -> str:
        """Extract S3 key from CDN or S3 URL"""
        if settings.CLOUDFRONT_DOMAIN and settings.CLOUDFRONT_DOMAIN in url:
            # CloudFront URL: https://d123.cloudfront.net/profile-pictures/user/file.jpg
            return url.split(settings.CLOUDFRONT_DOMAIN + '/')[-1]
        else:
            # Direct S3 URL: https://bucket.s3.region.amazonaws.com/key
            return url.split('.amazonaws.com/')[-1]

    def get_file_info(self, s3_url: str) -> Optional[dict]:
        """
        Get metadata information about a file in S3

        Args:
            s3_url: URL of the file

        Returns:
            dict: File metadata or None if not found
        """
        if not self.s3_client:
            return None

        try:
            s3_key = self._extract_s3_key_from_url(s3_url)
            bucket = self._get_bucket_from_key(s3_key)

            response = self.s3_client.head_object(Bucket=bucket, Key=s3_key)

            return {
                'key': s3_key,
                'size': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'metadata': response.get('Metadata', {})
            }

        except ClientError:
            return None

    def generate_presigned_url(self, s3_url: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for a private S3 object

        Args:
            s3_url: The S3 URL of the object
            expiration: URL expiration time in seconds (default 1 hour)

        Returns:
            str: Presigned URL or original URL if generation fails
        """
        if not self.s3_client:
            return s3_url

        try:
            s3_key = self._extract_s3_key_from_url(s3_url)
            bucket = self._get_bucket_from_key(s3_key)

            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return presigned_url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return s3_url

# Global instance
s3_service = S3Service()