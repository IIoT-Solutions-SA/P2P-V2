from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, field_validator

from app.core.input_validation import check_safe_text, check_safe_tag, check_safe_title, ALLOWED_USECASE_CATEGORIES, ALLOWED_USECASE_CATEGORIES_STR

class TeamMember(BaseModel):
    role: Annotated[str, Field(min_length=2, max_length=100)]
    name: Annotated[str, Field(min_length=2, max_length=100)]
    title: Annotated[str, Field(min_length=2, max_length=100)]

    @field_validator('role', 'name', 'title')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v)

class ProjectPhase(BaseModel):
    phase: Annotated[str, Field(min_length=2, max_length=100)]
    duration: Annotated[str, Field(min_length=2, max_length=100)]
    objectives: Annotated[List[Annotated[str, Field(max_length=500)]], Field(max_length=10)]
    keyActivities: Annotated[List[Annotated[str, Field(max_length=500)]], Field(max_length=10)]
    budget: Optional[Annotated[str, Field(max_length=100)]] = None

    @field_validator('phase', 'duration', 'budget')
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('objectives', 'keyActivities')
    @classmethod
    def validate_safe_string_lists(cls, v):
        if v is not None:
            for item in v:
                check_safe_text(item)
        return v


class QuantitativeResult(BaseModel):
    metric: Annotated[str, Field(min_length=5, max_length=200)]
    baseline: Annotated[str, Field(min_length=1, max_length=200)]
    current: Annotated[str, Field(min_length=1, max_length=200)]
    improvement: Annotated[str, Field(min_length=2, max_length=200)]

    @field_validator('metric', 'baseline', 'current', 'improvement')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v)


class ChallengeSolution(BaseModel):
    challenge: Annotated[str, Field(min_length=10, max_length=300)]
    description: Annotated[str, Field(min_length=20, max_length=1000)]
    solution: Annotated[str, Field(min_length=20, max_length=1000)]
    outcome: Annotated[str, Field(min_length=10, max_length=500)]

    @field_validator('challenge')
    @classmethod
    def validate_safe_challenge(cls, v):
        return check_safe_text(v)

    @field_validator('description', 'solution', 'outcome')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True)


class ArchitectureComponent(BaseModel):
    layer: Annotated[str, Field(min_length=2, max_length=100)]
    components: Annotated[List[Annotated[str, Field(max_length=200)]], Field(max_length=20)]
    specifications: Optional[Annotated[str, Field(max_length=1000)]] = None

    @field_validator('layer', 'specifications')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v

    @field_validator('components')
    @classmethod
    def validate_components(cls, v):
        if v is not None:
            for item in v:
                check_safe_text(item)
        return v


class TechnicalArchitecture(BaseModel):
    system_overview: Optional[Annotated[str, Field(max_length=5000)]] = None
    architecture_components: Optional[List[ArchitectureComponent]] = None
    security_measures: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    scalability_design: Optional[List[Annotated[str, Field(max_length=500)]]] = None

    @field_validator('system_overview')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v


class FutureRoadmapItem(BaseModel):
    timeline: Annotated[str, Field(min_length=2, max_length=100)]
    initiative: Annotated[str, Field(min_length=5, max_length=300)]
    description: Optional[Annotated[str, Field(max_length=1000)]] = None
    expected_benefit: Optional[Annotated[str, Field(max_length=500)]] = None

    @field_validator('timeline', 'initiative')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'expected_benefit')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v


class LessonLearned(BaseModel):
    category: Annotated[str, Field(min_length=2, max_length=100)]
    lesson: Annotated[str, Field(min_length=5, max_length=500)]
    description: Optional[Annotated[str, Field(max_length=1000)]] = None
    recommendation: Optional[Annotated[str, Field(max_length=1000)]] = None

    @field_validator('category', 'lesson')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'recommendation')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v


class UseCaseCreate(BaseModel):
    # Basic Information
    title: Annotated[str, Field(min_length=10, max_length=100)]
    subtitle: Annotated[str, Field(min_length=10, max_length=150)]
    description: Annotated[str, Field(min_length=50, max_length=5000)]  # Executive summary
    category: str
    factoryName: Annotated[str, Field(min_length=2, max_length=80)]

    # Location
    city: Annotated[str, Field(min_length=2, max_length=50)]
    latitude: Annotated[float, Field(ge=-90, le=90)]
    longitude: Annotated[float, Field(ge=-180, le=180)]

    # Business Challenge
    industryContext: Annotated[str, Field(min_length=50, max_length=5000)]
    specificProblems: Annotated[List[Annotated[str, Field(min_length=10, max_length=500)]], Field(min_length=2, max_length=5)]
    financialLoss: Annotated[str, Field(min_length=5, max_length=500)]

    # Solution Overview
    selectionCriteria: Annotated[List[Annotated[str, Field(min_length=10, max_length=500)]], Field(min_length=2, max_length=5)]
    selectedVendor: Annotated[str, Field(min_length=2, max_length=120)]
    technologyComponents: Annotated[List[Annotated[str, Field(min_length=20, max_length=500)]], Field(min_length=1, max_length=15)]

    # Implementation
    implementationTime: Annotated[str, Field(min_length=3, max_length=120)]
    totalBudget: Annotated[str, Field(min_length=3, max_length=120)]
    methodology: Annotated[str, Field(min_length=20, max_length=5000)]

    # Results
    quantitativeResults: Annotated[List[QuantitativeResult], Field(min_length=2, max_length=4)]
    roiPercentage: Optional[Annotated[str, Field(max_length=100)]] = None
    annualSavings: Optional[Annotated[str, Field(max_length=100)]] = None

    # Challenges & Solutions
    challengesSolutions: Annotated[List[ChallengeSolution], Field(min_length=1, max_length=4)]

    # Contact & Media
    contactPerson: Optional[Annotated[str, Field(max_length=120)]] = None
    contactTitle: Optional[Annotated[str, Field(max_length=120)]] = None
    images: Annotated[List[str], Field(max_length=5)] = Field(default_factory=list)

    # Optional extended sections (may be added in the form later)
    technical_architecture: Optional[TechnicalArchitecture] = None
    future_roadmap: Optional[List[FutureRoadmapItem]] = None
    lessons_learned: Optional[List[LessonLearned]] = None

    # Additional optional fields to mirror UseCaseDetail
    industryTags: Optional[Annotated[List[str], Field(max_length=10)]] = None
    technologyTags: Optional[Annotated[List[str], Field(max_length=10)]] = None
    vendorProcess: Optional[Annotated[str, Field(max_length=2000)]] = None
    vendorSelectionReasons: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    projectTeamInternal: Optional[List[TeamMember]] = None
    projectTeamVendor: Optional[List[TeamMember]] = None
    phases: Optional[List[ProjectPhase]] = None
    qualitativeImpacts: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    roiTotalInvestment: Optional[Annotated[str, Field(max_length=100)]] = None
    roiThreeYearRoi: Optional[Annotated[str, Field(max_length=100)]] = None

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v not in ALLOWED_USECASE_CATEGORIES:
            raise ValueError(f"Please select a valid category from: {ALLOWED_USECASE_CATEGORIES_STR}")
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        return check_safe_title(v) if v is not None else v

    @field_validator(
        'subtitle', 'factoryName', 'city', 
        'financialLoss', 'selectedVendor',
        'implementationTime', 'totalBudget',
        'roiPercentage', 'annualSavings', 'contactPerson', 'contactTitle',
        'roiTotalInvestment', 'roiThreeYearRoi'
    )
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'industryContext', 'methodology', 'vendorProcess')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v

    @field_validator(
        'specificProblems', 'selectionCriteria', 'technologyComponents',
        'vendorSelectionReasons', 'qualitativeImpacts'
    )
    @classmethod
    def validate_safe_string_lists(cls, v):
        if v is not None:
            for item in v:
                check_safe_text(item)
        return v

    @field_validator('industryTags', 'technologyTags')
    @classmethod
    def validate_safe_tags(cls, v):
        if v is not None:
            for item in v:
                check_safe_tag(item)
        return v


# ===== DRAFT SCHEMAS =====

class DraftQuantitativeResult(BaseModel):
    """Relaxed quantitative result for partial draft saves."""
    metric: Optional[Annotated[str, Field(max_length=200)]] = None
    baseline: Optional[Annotated[str, Field(max_length=200)]] = None
    current: Optional[Annotated[str, Field(max_length=200)]] = None
    improvement: Optional[Annotated[str, Field(max_length=200)]] = None

    @field_validator('metric', 'baseline', 'current', 'improvement')
    @classmethod
    def validate_safe_text(cls, v):
        return check_safe_text(v) if v is not None else v


class DraftChallengeSolution(BaseModel):
    """Relaxed challenge/solution item for partial draft saves."""
    challenge: Optional[Annotated[str, Field(max_length=300)]] = None
    description: Optional[Annotated[str, Field(max_length=1000)]] = None
    solution: Optional[Annotated[str, Field(max_length=1000)]] = None
    outcome: Optional[Annotated[str, Field(max_length=500)]] = None

    @field_validator('challenge')
    @classmethod
    def validate_safe_challenge(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'solution', 'outcome')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v


class UseCaseDraftCreate(BaseModel):
    """Schema for creating/updating use case drafts - all fields Optional for partial saves"""
    # Draft ID for updates (if updating existing draft)
    draftId: Optional[str] = None

    # Wizard step tracking
    currentStep: Optional[int] = 1

    # Basic Information
    title: Optional[Annotated[str, Field(max_length=100)]] = None
    subtitle: Optional[Annotated[str, Field(max_length=150)]] = None
    description: Optional[Annotated[str, Field(max_length=5000)]] = None
    category: Optional[str] = None
    factoryName: Optional[Annotated[str, Field(max_length=80)]] = None

    # Location
    city: Optional[Annotated[str, Field(max_length=50)]] = None
    latitude: Optional[Annotated[float, Field(ge=-90, le=90)]] = None
    longitude: Optional[Annotated[float, Field(ge=-180, le=180)]] = None

    # Business Challenge
    industryContext: Optional[Annotated[str, Field(max_length=5000)]] = None
    specificProblems: Optional[Annotated[List[Annotated[str, Field(max_length=500)]], Field(max_length=5)]] = None
    financialLoss: Optional[Annotated[str, Field(max_length=500)]] = None

    # Solution Overview
    selectionCriteria: Optional[Annotated[List[Annotated[str, Field(max_length=500)]], Field(max_length=5)]] = None
    selectedVendor: Optional[Annotated[str, Field(max_length=120)]] = None
    technologyComponents: Optional[Annotated[List[Annotated[str, Field(max_length=500)]], Field(max_length=15)]] = None

    # Implementation
    implementationTime: Optional[Annotated[str, Field(max_length=120)]] = None
    totalBudget: Optional[Annotated[str, Field(max_length=120)]] = None
    methodology: Optional[Annotated[str, Field(max_length=5000)]] = None

    # Results
    quantitativeResults: Optional[Annotated[List[DraftQuantitativeResult], Field(max_length=4)]] = None
    roiPercentage: Optional[Annotated[str, Field(max_length=100)]] = None
    annualSavings: Optional[Annotated[str, Field(max_length=100)]] = None

    # Challenges & Solutions
    challengesSolutions: Optional[Annotated[List[DraftChallengeSolution], Field(max_length=4)]] = None

    # Contact & Media
    contactPerson: Optional[Annotated[str, Field(max_length=120)]] = None
    contactTitle: Optional[Annotated[str, Field(max_length=120)]] = None
    images: Optional[Annotated[List[str], Field(max_length=5)]] = None

    # Extended sections
    technical_architecture: Optional[TechnicalArchitecture] = None
    future_roadmap: Optional[List[FutureRoadmapItem]] = None
    lessons_learned: Optional[List[LessonLearned]] = None

    # Additional fields
    industryTags: Optional[Annotated[List[str], Field(max_length=10)]] = None
    technologyTags: Optional[Annotated[List[str], Field(max_length=10)]] = None
    vendorProcess: Optional[Annotated[str, Field(max_length=2000)]] = None
    vendorSelectionReasons: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    projectTeamInternal: Optional[List[TeamMember]] = None
    projectTeamVendor: Optional[List[TeamMember]] = None
    phases: Optional[List[ProjectPhase]] = None
    qualitativeImpacts: Optional[List[Annotated[str, Field(max_length=500)]]] = None
    roiTotalInvestment: Optional[Annotated[str, Field(max_length=100)]] = None
    roiThreeYearRoi: Optional[Annotated[str, Field(max_length=100)]] = None

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None and v not in ALLOWED_USECASE_CATEGORIES:
            raise ValueError(f"Please select a valid category from: {ALLOWED_USECASE_CATEGORIES_STR}")
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        return check_safe_title(v) if v is not None else v

    @field_validator(
        'subtitle', 'factoryName', 'city', 
        'financialLoss', 'selectedVendor',
        'implementationTime', 'totalBudget',
        'roiPercentage', 'annualSavings', 'contactPerson', 'contactTitle',
        'roiTotalInvestment', 'roiThreeYearRoi'
    )
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('description', 'industryContext', 'methodology', 'vendorProcess')
    @classmethod
    def validate_safe_descriptions(cls, v):
        return check_safe_text(v, allow_urls=True) if v is not None else v

    @field_validator(
        'specificProblems', 'selectionCriteria', 'technologyComponents',
        'vendorSelectionReasons', 'qualitativeImpacts'
    )
    @classmethod
    def validate_safe_string_lists(cls, v):
        if v is not None:
            for item in v:
                check_safe_text(item)
        return v

    @field_validator('industryTags', 'technologyTags')
    @classmethod
    def validate_safe_tags(cls, v):
        if v is not None:
            for item in v:
                check_safe_tag(item)
        return v


class UseCaseDraftResponse(BaseModel):
    """Full draft response with metadata"""
    id: str
    user_id: str
    current_step: int

    # All UseCase fields (Optional)
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    factoryName: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    industryContext: Optional[str] = None
    specificProblems: Optional[List[str]] = None
    financialLoss: Optional[str] = None
    selectionCriteria: Optional[List[str]] = None
    selectedVendor: Optional[str] = None
    technologyComponents: Optional[List[str]] = None
    implementationTime: Optional[str] = None
    totalBudget: Optional[str] = None
    methodology: Optional[str] = None
    quantitativeResults: Optional[List[dict]] = None
    roiPercentage: Optional[str] = None
    annualSavings: Optional[str] = None
    challengesSolutions: Optional[List[dict]] = None
    contactPerson: Optional[str] = None
    contactTitle: Optional[str] = None
    images: Optional[List[str]] = None
    technical_architecture: Optional[dict] = None
    future_roadmap: Optional[List[dict]] = None
    lessons_learned: Optional[List[dict]] = None
    industryTags: Optional[List[str]] = None
    technologyTags: Optional[List[str]] = None
    vendorProcess: Optional[str] = None
    vendorSelectionReasons: Optional[List[str]] = None
    projectTeamInternal: Optional[List[TeamMember]] = None
    projectTeamVendor: Optional[List[TeamMember]] = None
    phases: Optional[List[ProjectPhase]] = None
    qualitativeImpacts: Optional[List[str]] = None
    roiTotalInvestment: Optional[str] = None
    roiThreeYearRoi: Optional[str] = None

    # Metadata
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UseCaseDraftListItem(BaseModel):
    """Lightweight draft info for list view"""
    id: str
    title: Optional[str] = None
    category: Optional[str] = None
    current_step: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UseCaseDraftPublishValidation(BaseModel):
    """Validation result for publishing a draft"""
    is_valid: bool
    missing_fields: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    can_publish: bool
    draft_preview: Optional[dict] = None
