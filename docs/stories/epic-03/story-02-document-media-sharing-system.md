# Story 2: Document & Media Sharing System

## Story Details
**Epic**: Epic 3 - Use Case Submission and Knowledge Management  
**Story Points**: 7  
**Priority**: High  
**Dependencies**: Epic 1 (Project Foundation), File Upload Service

## User Story
**As a** platform user (Factory Owner, Plant Engineer, Operations Manager)  
**I want** to securely upload, share, and collaborate on documents and media files  
**So that** I can provide comprehensive documentation for use cases and collaborate effectively with peers

## Acceptance Criteria
- [ ] Support for multiple file types: PDF, DOC, XLS, PPT, images, videos (max 100MB per file)
- [ ] Virus scanning and security validation for all uploaded files
- [ ] File organization with folders, tags, and categorization
- [ ] Access control system: public, private, shared with specific users/groups
- [ ] File versioning and revision history tracking
- [ ] Direct sharing via links with expiration and download limits
- [ ] Preview functionality for common file types (PDF, images)
- [ ] Batch upload capability for multiple files
- [ ] Download analytics and tracking
- [ ] Arabic/English filename and metadata support

## Technical Specifications

### 1. File Management Data Models

```python
# app/models/mongo_models.py
class FileDocument(Document):
    # Basic Information
    filename: str
    original_filename: str
    file_size: int  # bytes
    file_type: str  # pdf, docx, xlsx, jpg, mp4, etc.
    mime_type: str
    file_hash: str  # SHA256 for duplicate detection
    
    # Storage Information
    storage_provider: str = "aws_s3"
    storage_path: str
    storage_bucket: str
    cdn_url: Optional[str] = None
    
    # Metadata
    title: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None  # manual, technical_drawing, report, etc.
    language: str = "en"
    
    # Owner and Access
    owner_id: str
    owner_name: str
    access_level: str = "private"  # public, private, shared, organization
    shared_with: List[Dict[str, str]] = Field(default_factory=list)
    # [{"user_id": "...", "permission": "view|download|edit", "granted_at": "..."}]
    
    # Security
    virus_scan_status: str = "pending"  # pending, clean, infected, failed
    virus_scan_result: Optional[Dict[str, Any]] = None
    is_approved: bool = False
    moderation_notes: Optional[str] = None
    
    # Versioning
    version: int = 1
    parent_file_id: Optional[str] = None  # For file versions
    is_latest_version: bool = True
    
    # Usage Analytics
    download_count: int = 0
    view_count: int = 0
    last_accessed: Optional[datetime] = None
    
    # Timestamps
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    class Settings:
        name = "file_documents"
        indexes = [
            [("owner_id", pymongo.ASCENDING)],
            [("file_hash", pymongo.ASCENDING)],
            [("tags", pymongo.ASCENDING)],
            [("category", pymongo.ASCENDING)],
            [("uploaded_at", pymongo.DESCENDING)],
            [("virus_scan_status", pymongo.ASCENDING)],
            [("access_level", pymongo.ASCENDING)]
        ]

class FileShare(Document):
    file_id: str
    shared_by: str
    shared_with: Optional[str] = None  # None for public links
    share_token: str  # Unique token for public sharing
    
    permissions: List[str] = Field(default_factory=list)  # ["view", "download"]
    password_protected: bool = False
    password_hash: Optional[str] = None
    
    # Limitations
    max_downloads: Optional[int] = None
    download_count: int = 0
    expires_at: Optional[datetime] = None
    
    # Tracking
    access_log: List[Dict[str, Any]] = Field(default_factory=list)
    # [{"timestamp": "...", "ip": "...", "user_agent": "...", "action": "view|download"}]
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    
    class Settings:
        name = "file_shares"
        indexes = [
            [("file_id", pymongo.ASCENDING)],
            [("share_token", pymongo.ASCENDING)],
            [("shared_by", pymongo.ASCENDING)],
            [("expires_at", pymongo.ASCENDING)]
        ]

class FileFolder(Document):
    name: str
    description: Optional[str] = None
    owner_id: str
    parent_folder_id: Optional[str] = None
    
    # Access Control
    access_level: str = "private"
    shared_with: List[Dict[str, str]] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    color: Optional[str] = None  # For UI organization
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "file_folders"
        indexes = [
            [("owner_id", pymongo.ASCENDING)],
            [("parent_folder_id", pymongo.ASCENDING)]
        ]
```

### 2. File Management API Endpoints

```python
# app/api/v1/endpoints/files.py
@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    category: Optional[str] = Form(None),
    folder_id: Optional[str] = Form(None),
    access_level: str = Form("private"),
    session: SessionContainer = Depends(verify_session())
):
    """Upload a new file"""
    user_id = session.get_user_id()
    
    try:
        file_service = FileService()
        file_doc = await file_service.upload_file(
            user_id=user_id,
            file=file,
            title=title,
            description=description,
            tags=tags.split(",") if tags else [],
            category=category,
            folder_id=folder_id,
            access_level=access_level
        )
        
        return FileUploadResponse.from_document(file_doc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@router.get("/", response_model=List[FileResponse])
async def get_user_files(
    folder_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    session: SessionContainer = Depends(verify_session())
):
    """Get user's files with filtering"""
    user_id = session.get_user_id()
    
    files = await FileService.get_user_files(
        user_id=user_id,
        folder_id=folder_id,
        category=category,
        tags=tags,
        limit=limit
    )
    
    return [FileResponse.from_document(f) for f in files]

@router.post("/{file_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    file_id: str,
    share_request: FileShareRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Create shareable link for file"""
    user_id = session.get_user_id()
    
    try:
        share = await FileService.create_share_link(
            file_id, user_id, share_request
        )
        return ShareLinkResponse.from_share(share)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    session: Optional[SessionContainer] = Depends(verify_session(session_required=False))
):
    """Download file with access control"""
    user_id = session.get_user_id() if session else None
    
    try:
        download_url = await FileService.get_download_url(file_id, user_id)
        return RedirectResponse(url=download_url)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/shared/{share_token}")
async def access_shared_file(
    share_token: str,
    password: Optional[str] = Query(None)
):
    """Access file via shared link"""
    try:
        file_info = await FileService.access_shared_file(share_token, password)
        return file_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/folders", response_model=FolderResponse)
async def create_folder(
    folder_data: FolderCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Create new folder"""
    user_id = session.get_user_id()
    
    folder = await FileService.create_folder(user_id, folder_data)
    return FolderResponse.from_document(folder)
```

### 3. File Service Implementation

```python
# app/services/file_service.py
import boto3
from botocore.exceptions import ClientError
import hashlib
import magic
from urllib.parse import quote

class FileService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET
        self.cdn_base_url = settings.AWS_CLOUDFRONT_URL
    
    async def upload_file(
        self,
        user_id: str,
        file: UploadFile,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: List[str] = None,
        category: Optional[str] = None,
        folder_id: Optional[str] = None,
        access_level: str = "private"
    ) -> FileDocument:
        """Upload file to S3 and create database record"""
        
        # Validate file
        await self._validate_file(file)
        
        # Calculate file hash
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check for duplicates
        existing_file = await FileDocument.find_one(
            FileDocument.file_hash == file_hash,
            FileDocument.owner_id == user_id
        )
        if existing_file:
            raise ValueError("File already exists")
        
        # Generate storage path
        file_extension = file.filename.split('.')[-1].lower()
        storage_path = f"files/{user_id}/{file_hash}.{file_extension}"
        
        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=storage_path,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'original_filename': file.filename,
                    'uploaded_by': user_id,
                    'file_hash': file_hash
                }
            )
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise Exception("File upload failed")
        
        # Get user info
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        
        # Create database record
        file_doc = FileDocument(
            filename=f"{file_hash}.{file_extension}",
            original_filename=file.filename,
            file_size=len(file_content),
            file_type=file_extension,
            mime_type=file.content_type,
            file_hash=file_hash,
            storage_path=storage_path,
            storage_bucket=self.bucket_name,
            cdn_url=f"{self.cdn_base_url}/{storage_path}",
            title=title or file.filename,
            description=description,
            tags=tags or [],
            category=category,
            owner_id=user_id,
            owner_name=user_profile.name if user_profile else "Unknown",
            access_level=access_level,
            virus_scan_status="pending"
        )
        
        await file_doc.create()
        
        # Schedule virus scan
        await self._schedule_virus_scan(file_doc.id)
        
        logger.info(f"File uploaded: {file_doc.id} by user {user_id}")
        return file_doc
    
    async def create_share_link(
        self,
        file_id: str,
        user_id: str,
        share_request: FileShareRequest
    ) -> FileShare:
        """Create shareable link for file"""
        
        # Verify file ownership or access
        file_doc = await self._get_accessible_file(file_id, user_id)
        
        # Generate unique share token
        share_token = self._generate_share_token()
        
        # Create share record
        file_share = FileShare(
            file_id=file_id,
            shared_by=user_id,
            shared_with=share_request.shared_with,
            share_token=share_token,
            permissions=share_request.permissions,
            password_protected=bool(share_request.password),
            password_hash=self._hash_password(share_request.password) if share_request.password else None,
            max_downloads=share_request.max_downloads,
            expires_at=share_request.expires_at
        )
        
        await file_share.create()
        
        logger.info(f"Share link created: {share_token} for file {file_id}")
        return file_share
    
    async def get_download_url(self, file_id: str, user_id: Optional[str] = None) -> str:
        """Generate secure download URL"""
        
        # Verify access
        file_doc = await self._get_accessible_file(file_id, user_id)
        
        # Update analytics
        file_doc.download_count += 1
        file_doc.last_accessed = datetime.utcnow()
        await file_doc.save()
        
        # Generate presigned URL for S3
        try:
            download_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': file_doc.storage_bucket,
                    'Key': file_doc.storage_path,
                    'ResponseContentDisposition': f'attachment; filename="{quote(file_doc.original_filename)}"'
                },
                ExpiresIn=3600  # 1 hour
            )
            return download_url
        except ClientError as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise Exception("Download URL generation failed")
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        # Check file size (100MB limit)
        if file.size > 100 * 1024 * 1024:
            raise ValueError("File size exceeds 100MB limit")
        
        # Check file type
        allowed_types = {
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
            'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm',
            'txt', 'csv', 'zip', 'rar', '7z'
        }
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in allowed_types:
            raise ValueError(f"File type '{file_extension}' not allowed")
        
        # Verify MIME type matches extension
        file_content = await file.read()
        detected_mime = magic.from_buffer(file_content, mime=True)
        await file.seek(0)  # Reset file pointer
        
        # Basic MIME type validation
        if not self._is_mime_type_safe(detected_mime):
            raise ValueError("File appears to be malicious or corrupted")
    
    def _generate_share_token(self) -> str:
        """Generate unique share token"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _hash_password(self, password: str) -> str:
        """Hash share link password"""
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

### 4. Frontend File Management Interface

```typescript
// FileManager.tsx
export default function FileManager() {
  const { t } = useTranslation();
  const [files, setFiles] = useState<FileDocument[]>([]);
  const [folders, setFolders] = useState<FileFolder[]>([]);
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFilesDrop,
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: true
  });

  const handleFilesDrop = async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder_id', currentFolder || '');
    
    try {
      const response = await api.post('/api/v1/files/upload', formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
        }
      });
      
      setFiles(prev => [response.data, ...prev]);
      setUploadProgress(prev => {
        const { [file.name]: _, ...rest } = prev;
        return rest;
      });
      
      toast.success(t('files.upload_success'));
    } catch (error) {
      toast.error(t('files.upload_failed'));
    }
  };

  const createShareLink = async (fileId: string) => {
    try {
      const response = await api.post(`/api/v1/files/${fileId}/share`, {
        permissions: ['view', 'download'],
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
      });
      
      const shareUrl = `${window.location.origin}/shared/${response.data.share_token}`;
      navigator.clipboard.writeText(shareUrl);
      toast.success(t('files.share_link_copied'));
    } catch (error) {
      toast.error(t('files.share_failed'));
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive ? t('files.drop_here') : t('files.drag_drop')}
            </p>
            <p className="text-sm text-gray-500">
              {t('files.supported_formats')} • {t('files.max_size')}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* File List */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>{t('files.my_files')}</CardTitle>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Folder className="h-4 w-4 mr-2" />
                {t('files.new_folder')}
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    {t('files.filter')}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem>{t('files.all_files')}</DropdownMenuItem>
                  <DropdownMenuItem>{t('files.documents')}</DropdownMenuItem>
                  <DropdownMenuItem>{t('files.images')}</DropdownMenuItem>
                  <DropdownMenuItem>{t('files.videos')}</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {files.map((file) => (
              <FileItem
                key={file.id}
                file={file}
                selected={selectedFiles.includes(file.id)}
                onSelect={(id) => setSelectedFiles(prev => 
                  prev.includes(id) 
                    ? prev.filter(fId => fId !== id)
                    : [...prev, id]
                )}
                onShare={() => createShareLink(file.id)}
                onDownload={() => downloadFile(file.id)}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

## Implementation Steps

1. **Database Schema**
   - Create FileDocument, FileShare, and FileFolder models
   - Set up indexes for efficient querying
   - Implement file deduplication logic

2. **Storage Infrastructure**
   - Configure AWS S3 bucket with proper permissions
   - Set up CloudFront CDN for file delivery
   - Implement virus scanning service

3. **Backend Services**
   - FileService for upload/download operations
   - Share link generation and access control
   - File organization and folder management

4. **Frontend Components**
   - Drag-and-drop file upload interface
   - File browser with folder navigation
   - Share link creation and management

## Testing Checklist
- [ ] File upload works for all supported types
- [ ] Virus scanning detects and blocks malicious files
- [ ] Access control prevents unauthorized downloads
- [ ] Share links work with expiration and limits
- [ ] File versioning maintains history correctly
- [ ] Folder organization functions properly
- [ ] Mobile interface handles file operations
- [ ] Large file uploads show progress correctly
- [ ] Download analytics track usage accurately

## Performance Considerations
- [ ] S3 presigned URLs for direct uploads
- [ ] CDN caching for frequently accessed files
- [ ] Lazy loading for large file lists
- [ ] Compression for document types
- [ ] Efficient database queries for file metadata

## Dependencies
- AWS S3 and CloudFront configuration
- Virus scanning service (ClamAV or cloud service)
- User authentication and authorization
- Email notification service

## Notes
- Implement file thumbnail generation for images
- Consider integration with document preview services
- Plan for automated file cleanup and archiving
- Ensure GDPR compliance for file deletion
- Design scalable architecture for high file volumes