# Story 6: User Verification System

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 7  
**Priority**: High  
**Dependencies**: Story 1 (User Profile Management)

## User Story
**As a** platform administrator  
**I want** to verify the authenticity and credentials of SME users  
**So that** the platform maintains credibility and trust among professional users

**As a** platform user  
**I want** to see verified badges on user profiles and posts  
**So that** I can trust the expertise and credibility of content contributors

## Acceptance Criteria
- [ ] Users can submit verification requests with supporting documents
- [ ] Admin interface for reviewing and approving verification requests
- [ ] Verified badge displays prominently on user profiles and forum posts
- [ ] Verification requirements clearly documented and accessible
- [ ] Email notifications for verification status updates
- [ ] Verified users receive enhanced platform privileges
- [ ] Verification status affects search result rankings
- [ ] Multiple verification levels (Basic, Expert, Company)
- [ ] Verification expiry and renewal system
- [ ] Appeal process for rejected verification requests

## Technical Specifications

### 1. Verification Data Models

```python
# app/models/mongo_models.py
class VerificationRequest(Document):
    user_id: str
    request_type: str  # basic, expert, company
    status: str = "pending"  # pending, approved, rejected, expired
    
    # Submitted Information
    submitted_documents: List[Dict[str, str]] = Field(default_factory=list)
    # [{"type": "id_card", "url": "...", "filename": "..."}]
    
    verification_data: Dict[str, str] = Field(default_factory=dict)
    # {"company_name": "...", "position": "...", "experience_years": "..."}
    
    # Admin Review
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Verification Details
    verification_level: Optional[str] = None  # basic, expert, company
    verified_fields: List[str] = Field(default_factory=list)
    # ["identity", "company", "expertise", "education"]
    
    expires_at: Optional[datetime] = None
    
    # Metadata
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "verification_requests"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("status", pymongo.ASCENDING)],
            [("submitted_at", pymongo.DESCENDING)],
            [("reviewed_by", pymongo.ASCENDING)]
        ]

# Update UserProfile model
class UserProfile(Document):
    # ... existing fields ...
    
    # Enhanced Verification
    verification_status: str = "unverified"  # unverified, pending, verified, expired
    verification_level: Optional[str] = None  # basic, expert, company
    verification_badges: List[str] = Field(default_factory=list)
    # ["identity_verified", "company_verified", "expert_certified"]
    
    verified_at: Optional[datetime] = None
    verification_expires_at: Optional[datetime] = None
    
    # Verification Metadata
    verification_score: int = 0  # 0-100 credibility score
    verification_notes: Optional[str] = None
```

### 2. Admin Verification Interface

```python
# app/api/v1/endpoints/admin/verification.py
@router.get("/verification-requests", response_model=List[VerificationRequestResponse])
async def get_verification_requests(
    status: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin_session: SessionContainer = Depends(verify_admin_session())
):
    \"\"\"Get verification requests for admin review\"\"\"
    try:
        requests = await VerificationService.get_verification_requests(
            status=status,
            request_type=request_type,
            page=page,
            limit=limit
        )
        return requests
    except Exception as e:
        logger.error(f"Failed to fetch verification requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to load requests")

@router.post("/verification-requests/{request_id}/approve")
async def approve_verification(
    request_id: str,
    approval_data: VerificationApprovalRequest,
    admin_session: SessionContainer = Depends(verify_admin_session())
):
    \"\"\"Approve a verification request\"\"\"
    admin_id = admin_session.get_user_id()
    
    try:
        result = await VerificationService.approve_verification(
            request_id, admin_id, approval_data
        )
        return {"message": "Verification approved successfully", "result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verification-requests/{request_id}/reject")
async def reject_verification(
    request_id: str,
    rejection_data: VerificationRejectionRequest,
    admin_session: SessionContainer = Depends(verify_admin_session())
):
    \"\"\"Reject a verification request\"\"\"
    admin_id = admin_session.get_user_id()
    
    try:
        await VerificationService.reject_verification(
            request_id, admin_id, rejection_data
        )
        return {"message": "Verification rejected"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 3. User Verification Endpoints

```python
# app/api/v1/endpoints/verification.py
@router.post("/submit", response_model=VerificationSubmissionResponse)
async def submit_verification_request(
    verification_data: VerificationSubmissionRequest,
    session: SessionContainer = Depends(verify_session())
):
    \"\"\"Submit verification request\"\"\"
    user_id = session.get_user_id()
    
    try:
        request = await VerificationService.submit_verification_request(
            user_id, verification_data
        )
        return VerificationSubmissionResponse.from_request(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status", response_model=VerificationStatusResponse)
async def get_verification_status(
    session: SessionContainer = Depends(verify_session())
):
    \"\"\"Get user's verification status\"\"\"
    user_id = session.get_user_id()
    
    try:
        status = await VerificationService.get_user_verification_status(user_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get verification status: {e}")
        raise HTTPException(status_code=500, detail="Failed to load status")

@router.post("/upload-document")
async def upload_verification_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    session: SessionContainer = Depends(verify_session())
):
    \"\"\"Upload verification document\"\"\"
    user_id = session.get_user_id()
    
    try:
        file_service = FileService()
        document = await file_service.upload_verification_document(
            user_id, file, document_type
        )
        return {"message": "Document uploaded successfully", "document": document}
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
```

### 4. Verification Service Implementation

```python
# app/services/verification_service.py
class VerificationService:
    @staticmethod
    async def submit_verification_request(
        user_id: str, 
        verification_data: VerificationSubmissionRequest
    ) -> VerificationRequest:
        \"\"\"Submit new verification request\"\"\"
        # Check for existing pending request
        existing = await VerificationRequest.find_one(
            VerificationRequest.user_id == user_id,
            VerificationRequest.status == "pending"
        )
        if existing:
            raise ValueError("Verification request already pending")
        
        # Create verification request
        request = VerificationRequest(
            user_id=user_id,
            request_type=verification_data.request_type,
            verification_data=verification_data.verification_data.dict(),
            submitted_documents=verification_data.documents,
            status="pending"
        )
        
        await request.create()
        
        # Update user profile status
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if user_profile:
            user_profile.verification_status = "pending"
            await user_profile.save()
        
        # Notify admins of new verification request
        await NotificationService.notify_admins_new_verification(request.id)
        
        logger.info(f"Verification request submitted: {request.id}")
        return request
    
    @staticmethod
    async def approve_verification(
        request_id: str,
        admin_id: str,
        approval_data: VerificationApprovalRequest
    ):
        \"\"\"Approve verification request\"\"\"
        request = await VerificationRequest.find_one(
            VerificationRequest.id == request_id
        )
        if not request:
            raise ValueError("Verification request not found")
        
        if request.status != "pending":
            raise ValueError("Request is not in pending status")
        
        # Update verification request
        request.status = "approved"
        request.reviewed_by = admin_id
        request.reviewed_at = datetime.utcnow()
        request.review_notes = approval_data.notes
        request.verification_level = approval_data.verification_level
        request.verified_fields = approval_data.verified_fields
        
        # Set expiration (2 years from now)
        request.expires_at = datetime.utcnow() + timedelta(days=730)
        
        await request.save()
        
        # Update user profile
        user_profile = await UserProfile.find_one(
            UserProfile.user_id == request.user_id
        )
        if user_profile:
            user_profile.verification_status = "verified"
            user_profile.verification_level = approval_data.verification_level
            user_profile.verification_badges = approval_data.verified_fields
            user_profile.verified_at = datetime.utcnow()
            user_profile.verification_expires_at = request.expires_at
            user_profile.verification_score = approval_data.verification_score
            
            # Update reputation
            user_profile.reputation_score += 50  # Verification bonus
            
            await user_profile.save()
        
        # Send approval notification
        await NotificationService.send_verification_approval(
            request.user_id, approval_data.verification_level
        )
        
        logger.info(f"Verification approved: {request_id} by admin {admin_id}")
        return True
    
    @staticmethod
    async def get_verification_requirements() -> Dict[str, Any]:
        \"\"\"Get verification requirements and guidelines\"\"\"
        return {
            "basic": {
                "description": "Basic identity verification",
                "required_documents": ["government_id", "proof_of_employment"],
                "benefits": ["Verified badge", "Higher search ranking", "Forum privileges"],
                "processing_time": "3-5 business days"
            },
            "expert": {
                "description": "Professional expertise verification",
                "required_documents": [
                    "government_id", "proof_of_employment", 
                    "professional_certifications", "work_portfolio"
                ],
                "benefits": [
                    "Expert badge", "Answer highlighting", "Mentorship opportunities",
                    "Early access to features"
                ],
                "processing_time": "5-7 business days"
            },
            "company": {
                "description": "Company official verification",
                "required_documents": [
                    "company_registration", "official_authorization",
                    "business_license", "tax_certificate"
                ],
                "benefits": [
                    "Company badge", "Official announcements", "Company page access",
                    "Recruitment posting rights"
                ],
                "processing_time": "7-10 business days"
            }
        }
```

### 5. Frontend Verification Components

```typescript
// VerificationForm.tsx
export default function VerificationForm() {
  const { t } = useTranslation();
  const [verificationType, setVerificationType] = useState('basic');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);

  const verificationTypes = [
    {
      id: 'basic',
      name: t('verification.types.basic.name'),
      description: t('verification.types.basic.description'),
      required: ['government_id', 'proof_of_employment'],
      badge: 'Verified',
      color: 'blue'
    },
    {
      id: 'expert',
      name: t('verification.types.expert.name'),
      description: t('verification.types.expert.description'),
      required: ['government_id', 'certifications', 'portfolio'],
      badge: 'Expert',
      color: 'purple'
    },
    {
      id: 'company',
      name: t('verification.types.company.name'),
      description: t('verification.types.company.description'),
      required: ['company_registration', 'authorization', 'license'],
      badge: 'Official',
      color: 'green'
    }
  ];

  const handleSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const submissionData = {
        request_type: verificationType,
        verification_data: data,
        documents: documents
      };

      await api.post('/api/v1/verification/submit', submissionData);
      
      // Show success message and redirect
      toast.success(t('verification.submitted_successfully'));
      router.push('/profile?tab=verification');
    } catch (error) {
      toast.error(t('verification.submission_failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>{t('verification.title')}</CardTitle>
        <CardDescription>
          {t('verification.description')}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Verification Type Selection */}
        <div className="space-y-4 mb-8">
          <h3 className="text-lg font-semibold">{t('verification.select_type')}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {verificationTypes.map((type) => (
              <Card 
                key={type.id}
                className={`cursor-pointer border-2 ${
                  verificationType === type.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200'
                }`}
                onClick={() => setVerificationType(type.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{type.name}</h4>
                    <Badge className={`bg-${type.color}-100 text-${type.color}-800`}>
                      {type.badge}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{type.description}</p>
                  <div>
                    <p className="text-xs font-medium text-gray-500 mb-1">
                      {t('verification.required_documents')}:
                    </p>
                    <ul className="text-xs text-gray-600">
                      {type.required.map((doc) => (
                        <li key={doc}>• {t(`verification.documents.${doc}`)}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Document Upload */}
        <VerificationDocumentUpload
          verificationType={verificationType}
          documents={documents}
          onDocumentsChange={setDocuments}
        />

        {/* Submit Button */}
        <div className="mt-8">
          <Button 
            onClick={handleSubmit} 
            disabled={loading || documents.length === 0}
            className="w-full"
          >
            {loading ? t('verification.submitting') : t('verification.submit')}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

## Implementation Steps

1. **Database Schema**
   - Create VerificationRequest model
   - Update UserProfile with verification fields
   - Set up indexes for efficient querying

2. **Admin Interface**
   - Build verification request review dashboard
   - Implement approval/rejection workflows
   - Add document viewer and verification tools

3. **User Interface**
   - Verification request form with document upload
   - Verification status tracking page
   - Verification badge display components

4. **Background Services**
   - Document processing and validation
   - Expiration monitoring and renewal reminders
   - Notification system for status updates

## Testing Checklist
- [ ] Users can submit verification requests
- [ ] Document upload works securely
- [ ] Admin can review and approve/reject requests
- [ ] Verification badges display correctly
- [ ] Email notifications sent for status changes
- [ ] Verification expiry system functions
- [ ] Appeal process for rejections works
- [ ] Different verification levels display properly
- [ ] Search rankings affected by verification status

## Dependencies
- Story 1 (User Profile Management) completed
- File upload service configured
- Admin authentication system implemented
- Email notification service operational

## Notes
- Implement fraud detection for document verification
- Consider integration with third-party verification services
- Plan for manual verification workflows
- Ensure compliance with data privacy regulations
- Design scalable verification process for growth