# Story 1: Use Case Submission Tool

## Story Details
**Epic**: Epic 3 - Use Case Submission and Knowledge Management  
**Story Points**: 8  
**Priority**: High  
**Dependencies**: Epic 1 (Project Foundation), Story 1 (User Profiles)

## User Story
**As a** Factory Owner, Plant Engineer, or Operations Manager  
**I want** to submit detailed use cases of industrial challenges and solutions  
**So that** I can share my experience with the community and help peers facing similar issues

## Acceptance Criteria
- [ ] Multi-step form for structured use case submission with rich text editing
- [ ] Categorization system for industry, problem type, and solution category
- [ ] File attachment support for images, documents, and videos
- [ ] Draft saving functionality to prevent data loss during submission
- [ ] Use case preview before final submission
- [ ] Approval workflow for submitted use cases with admin review
- [ ] Email notifications for submission status updates
- [ ] Template system for common use case types
- [ ] Arabic/English language support for all content
- [ ] Mobile-optimized submission interface

## Technical Specifications

### 1. Use Case Data Model

```python
# app/models/mongo_models.py
class UseCase(Document):
    # Basic Information
    title: str
    description: str
    language: str = "en"
    
    # Categorization
    industry_sector: str  # manufacturing, chemical, food_processing, etc.
    problem_category: str  # efficiency, safety, quality, maintenance, etc.
    solution_type: str  # process_improvement, technology, training, etc.
    
    # Content Structure
    problem_statement: str
    solution_description: str
    implementation_details: str
    results_achieved: str
    lessons_learned: Optional[str] = None
    
    # Metadata
    company_size: str  # startup, small, medium, large, enterprise
    implementation_cost: str  # low, medium, high, very_high
    implementation_time: str  # days, weeks, months, years
    complexity_level: str  # beginner, intermediate, advanced, expert
    
    # Tags and Keywords
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    # Attachments
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    # [{"type": "image", "url": "...", "filename": "...", "description": "..."}]
    
    # Author Information
    author_id: str
    author_name: str
    author_company: Optional[str] = None
    author_position: Optional[str] = None
    is_anonymous: bool = False
    
    # Status and Workflow
    status: str = "draft"  # draft, submitted, under_review, approved, rejected, published
    submission_notes: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # Engagement Metrics
    view_count: int = 0
    like_count: int = 0
    bookmark_count: int = 0
    comment_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    class Settings:
        name = "use_cases"
        indexes = [
            [("author_id", pymongo.ASCENDING)],
            [("status", pymongo.ASCENDING)],
            [("industry_sector", pymongo.ASCENDING)],
            [("problem_category", pymongo.ASCENDING)],
            [("tags", pymongo.ASCENDING)],
            [("created_at", pymongo.DESCENDING)],
            [("view_count", pymongo.DESCENDING)],
            # Full-text search index
            [("title", pymongo.TEXT), ("description", pymongo.TEXT), 
             ("problem_statement", pymongo.TEXT), ("solution_description", pymongo.TEXT)]
        ]

# Use Case Template System
class UseCaseTemplate(Document):
    name: str
    description: str
    industry_sector: str
    template_fields: Dict[str, Any] = Field(default_factory=dict)
    # {"problem_statement": {"label": "...", "placeholder": "...", "required": true}}
    
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "use_case_templates"
```

### 2. API Endpoints

```python
# app/api/v1/endpoints/use_cases.py
@router.post("/", response_model=UseCaseResponse)
async def create_use_case(
    use_case_data: UseCaseCreateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Create a new use case submission"""
    user_id = session.get_user_id()
    
    try:
        use_case = await UseCaseService.create_use_case(user_id, use_case_data)
        return await UseCaseService.get_use_case_response(use_case.id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{use_case_id}", response_model=UseCaseResponse)
async def update_use_case(
    use_case_id: str,
    use_case_data: UseCaseUpdateRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Update a use case (draft or submitted)"""
    user_id = session.get_user_id()
    
    try:
        use_case = await UseCaseService.update_use_case(use_case_id, user_id, use_case_data)
        return await UseCaseService.get_use_case_response(use_case.id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/{use_case_id}/submit")
async def submit_use_case(
    use_case_id: str,
    session: SessionContainer = Depends(verify_session())
):
    """Submit use case for review"""
    user_id = session.get_user_id()
    
    try:
        await UseCaseService.submit_for_review(use_case_id, user_id)
        return {"message": "Use case submitted for review successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates", response_model=List[UseCaseTemplateResponse])
async def get_use_case_templates(
    industry_sector: Optional[str] = Query(None)
):
    """Get available use case templates"""
    templates = await UseCaseService.get_templates(industry_sector)
    return templates

@router.post("/upload-attachment")
async def upload_use_case_attachment(
    file: UploadFile = File(...),
    use_case_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    session: SessionContainer = Depends(verify_session())
):
    """Upload attachment for use case"""
    user_id = session.get_user_id()
    
    try:
        file_service = FileService()
        attachment = await file_service.upload_use_case_attachment(
            user_id, file, use_case_id, description
        )
        return {"message": "File uploaded successfully", "attachment": attachment}
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
```

### 3. Use Case Service Implementation

```python
# app/services/use_case_service.py
class UseCaseService:
    @staticmethod
    async def create_use_case(user_id: str, use_case_data: UseCaseCreateRequest) -> UseCase:
        """Create new use case draft"""
        # Get user profile for author info
        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not user_profile:
            raise ValueError("User profile not found")
        
        # Create use case
        use_case = UseCase(
            title=use_case_data.title,
            description=use_case_data.description,
            language=use_case_data.language,
            industry_sector=use_case_data.industry_sector,
            problem_category=use_case_data.problem_category,
            solution_type=use_case_data.solution_type,
            problem_statement=use_case_data.problem_statement,
            solution_description=use_case_data.solution_description,
            implementation_details=use_case_data.implementation_details,
            results_achieved=use_case_data.results_achieved,
            lessons_learned=use_case_data.lessons_learned,
            company_size=use_case_data.company_size,
            implementation_cost=use_case_data.implementation_cost,
            implementation_time=use_case_data.implementation_time,
            complexity_level=use_case_data.complexity_level,
            tags=use_case_data.tags,
            keywords=use_case_data.keywords,
            author_id=user_id,
            author_name=user_profile.name,
            author_company=user_profile.company_name,
            author_position=user_profile.job_title,
            is_anonymous=use_case_data.is_anonymous,
            status="draft"
        )
        
        await use_case.create()
        logger.info(f"Use case created: {use_case.id} by user {user_id}")
        return use_case
    
    @staticmethod
    async def submit_for_review(use_case_id: str, user_id: str):
        """Submit use case for admin review"""
        use_case = await UseCase.find_one(
            UseCase.id == use_case_id,
            UseCase.author_id == user_id
        )
        if not use_case:
            raise ValueError("Use case not found or access denied")
        
        if use_case.status not in ["draft", "rejected"]:
            raise ValueError("Use case cannot be submitted in current status")
        
        # Validate required fields
        await UseCaseService._validate_use_case_completion(use_case)
        
        # Update status
        use_case.status = "submitted"
        use_case.updated_at = datetime.utcnow()
        await use_case.save()
        
        # Notify admins
        await NotificationService.notify_admins_new_use_case(use_case.id)
        
        # Notify author
        await NotificationService.send_use_case_submitted_confirmation(
            user_id, use_case.title
        )
        
        logger.info(f"Use case submitted for review: {use_case_id}")
    
    @staticmethod
    async def get_templates(industry_sector: Optional[str] = None) -> List[UseCaseTemplate]:
        """Get use case templates"""
        query = {"is_active": True}
        if industry_sector:
            query["industry_sector"] = industry_sector
        
        templates = await UseCaseTemplate.find(query).to_list()
        return templates
    
    @staticmethod
    async def _validate_use_case_completion(use_case: UseCase):
        """Validate use case has all required fields for submission"""
        required_fields = [
            "title", "description", "problem_statement", 
            "solution_description", "implementation_details", "results_achieved"
        ]
        
        for field in required_fields:
            value = getattr(use_case, field)
            if not value or len(value.strip()) < 10:
                raise ValueError(f"Field '{field}' is required and must be at least 10 characters")
        
        if not use_case.tags or len(use_case.tags) < 2:
            raise ValueError("At least 2 tags are required")
        
        if not use_case.industry_sector:
            raise ValueError("Industry sector is required")
```

### 4. Frontend Use Case Submission Form

```typescript
// UseCaseSubmissionForm.tsx
export default function UseCaseSubmissionForm() {
  const { t } = useTranslation();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<UseCaseFormData>({});
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(false);
  const [attachments, setAttachments] = useState<Attachment[]>([]);

  const steps = [
    { id: 1, name: t('usecase.steps.basic_info'), component: BasicInfoStep },
    { id: 2, name: t('usecase.steps.problem_solution'), component: ProblemSolutionStep },
    { id: 3, name: t('usecase.steps.implementation'), component: ImplementationStep },
    { id: 4, name: t('usecase.steps.results'), component: ResultsStep },
    { id: 5, name: t('usecase.steps.review'), component: ReviewStep }
  ];

  useEffect(() => {
    fetchTemplates();
    // Auto-save draft every 30 seconds
    const interval = setInterval(saveDraft, 30000);
    return () => clearInterval(interval);
  }, [formData]);

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/api/v1/use-cases/templates');
      setTemplates(response.data);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const saveDraft = async () => {
    if (formData.title?.trim()) {
      try {
        const response = await api.post('/api/v1/use-cases', {
          ...formData,
          status: 'draft'
        });
        setFormData(prev => ({ ...prev, id: response.data.id }));
      } catch (error) {
        console.error('Draft save failed:', error);
      }
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Create or update use case
      let useCaseId = formData.id;
      if (!useCaseId) {
        const response = await api.post('/api/v1/use-cases', formData);
        useCaseId = response.data.id;
      } else {
        await api.put(`/api/v1/use-cases/${useCaseId}`, formData);
      }

      // Submit for review
      await api.post(`/api/v1/use-cases/${useCaseId}/submit`);
      
      toast.success(t('usecase.submitted_successfully'));
      router.push('/dashboard?tab=use-cases');
    } catch (error) {
      toast.error(t('usecase.submission_failed'));
    } finally {
      setLoading(false);
    }
  };

  const CurrentStepComponent = steps[currentStep - 1].component;

  return (
    <div className="max-w-4xl mx-auto py-8">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`flex items-center ${
                index < steps.length - 1 ? 'flex-1' : ''
              }`}
            >
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                  currentStep >= step.id
                    ? 'bg-blue-600 border-blue-600 text-white'
                    : 'border-gray-300 text-gray-500'
                }`}
              >
                {currentStep > step.id ? (
                  <Check className="h-5 w-5" />
                ) : (
                  step.id
                )}
              </div>
              <span
                className={`ml-2 text-sm font-medium ${
                  currentStep >= step.id ? 'text-blue-600' : 'text-gray-500'
                }`}
              >
                {step.name}
              </span>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-4 ${
                    currentStep > step.id ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Content */}
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStep - 1].name}</CardTitle>
        </CardHeader>
        <CardContent>
          <CurrentStepComponent
            formData={formData}
            setFormData={setFormData}
            templates={templates}
            attachments={attachments}
            setAttachments={setAttachments}
          />
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
          >
            {t('common.previous')}
          </Button>
          
          {currentStep < steps.length ? (
            <Button
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!isStepValid(currentStep, formData)}
            >
              {t('common.next')}
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={loading || !isFormComplete(formData)}
            >
              {loading ? t('usecase.submitting') : t('usecase.submit')}
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
```

## Implementation Steps

1. **Database Schema**
   - Create UseCase and UseCaseTemplate models
   - Set up indexes for efficient querying and search
   - Implement full-text search capabilities

2. **Backend Services**
   - UseCaseService for CRUD operations
   - File upload service for attachments
   - Validation and approval workflow

3. **Frontend Components**
   - Multi-step submission form with rich text editing
   - Template selection and auto-filling
   - Draft auto-saving functionality

4. **Admin Interface**
   - Use case review and approval dashboard
   - Quality control and moderation tools
   - Analytics for submission metrics

## Testing Checklist
- [ ] Multi-step form navigation works correctly
- [ ] Draft auto-saving prevents data loss
- [ ] File attachments upload and display properly
- [ ] Template system auto-fills form fields
- [ ] Validation prevents incomplete submissions
- [ ] Admin approval workflow functions correctly
- [ ] Email notifications sent for status changes
- [ ] Arabic/English content displays properly
- [ ] Mobile interface is responsive and usable
- [ ] Search indexing works for submitted use cases

## Performance Considerations
- [ ] File upload optimization for large attachments
- [ ] Form data persistence across browser sessions
- [ ] Efficient querying for template and category data
- [ ] Pagination for admin review dashboard
- [ ] Search performance for large use case database

## Dependencies
- Epic 1 (Project Foundation) completed
- User Profile Management operational
- File upload service configured
- Email notification service active

## Notes
- Implement content quality scoring for use case reviews
- Consider machine learning for automatic categorization
- Plan for integration with external industry databases
- Design for scalability as use case volume grows
- Ensure compliance with intellectual property guidelines