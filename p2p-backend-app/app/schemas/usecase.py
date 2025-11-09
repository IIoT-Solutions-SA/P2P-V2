from typing import List, Optional
from pydantic import BaseModel, Field


class QuantitativeResult(BaseModel):
    metric: str
    baseline: str
    current: str
    improvement: str


class ChallengeSolution(BaseModel):
    challenge: str
    description: str
    solution: str
    outcome: str


class TechnicalArchitecture(BaseModel):
    system_overview: Optional[str] = None
    architecture_components: Optional[List[dict]] = None  # {layer, components: List[str], specifications}
    security_measures: Optional[List[str]] = None
    scalability_design: Optional[List[str]] = None


class FutureRoadmapItem(BaseModel):
    timeline: str
    initiative: str
    description: Optional[str] = None
    expected_benefit: Optional[str] = None


class LessonLearned(BaseModel):
    category: str
    lesson: str
    description: Optional[str] = None
    recommendation: Optional[str] = None


class UseCaseCreate(BaseModel):
    # Basic Information
    title: str
    subtitle: str
    description: str  # Executive summary
    category: str
    factoryName: str

    # Location
    city: str
    latitude: float
    longitude: float

    # Business Challenge
    industryContext: str
    specificProblems: List[str]
    financialLoss: str

    # Solution Overview
    selectionCriteria: List[str]
    selectedVendor: str
    technologyComponents: List[str]

    # Implementation
    implementationTime: str
    totalBudget: str
    methodology: str

    # Results
    quantitativeResults: List[QuantitativeResult]
    roiPercentage: Optional[str] = None
    annualSavings: Optional[str] = None

    # Challenges & Solutions
    challengesSolutions: List[ChallengeSolution]

    # Contact & Media
    contactPerson: Optional[str] = None
    contactTitle: Optional[str] = None
    images: List[str] = Field(default_factory=list)

    # Optional extended sections (may be added in the form later)
    technical_architecture: Optional[TechnicalArchitecture] = None
    future_roadmap: Optional[List[FutureRoadmapItem]] = None
    lessons_learned: Optional[List[LessonLearned]] = None

    # Additional optional fields to mirror UseCaseDetail
    industryTags: Optional[List[str]] = None
    technologyTags: Optional[List[str]] = None
    vendorProcess: Optional[str] = None
    vendorSelectionReasons: Optional[List[str]] = None
    projectTeamInternal: Optional[List[dict]] = None  # {role, name, title}
    projectTeamVendor: Optional[List[dict]] = None    # {role, name, title}
    phases: Optional[List[dict]] = None  # {phase, duration, objectives: List[str], keyActivities: List[str], budget}
    qualitativeImpacts: Optional[List[str]] = None
    roiTotalInvestment: Optional[str] = None
    roiThreeYearRoi: Optional[str] = None


# ===== DRAFT SCHEMAS =====

class UseCaseDraftCreate(BaseModel):
    """Schema for creating/updating use case drafts - all fields Optional for partial saves"""
    # Draft ID for updates (if updating existing draft)
    draftId: Optional[str] = None

    # Wizard step tracking
    currentStep: Optional[int] = 1

    # Basic Information
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    factoryName: Optional[str] = None

    # Location
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Business Challenge
    industryContext: Optional[str] = None
    specificProblems: Optional[List[str]] = None
    financialLoss: Optional[str] = None

    # Solution Overview
    selectionCriteria: Optional[List[str]] = None
    selectedVendor: Optional[str] = None
    technologyComponents: Optional[List[str]] = None

    # Implementation
    implementationTime: Optional[str] = None
    totalBudget: Optional[str] = None
    methodology: Optional[str] = None

    # Results
    quantitativeResults: Optional[List[QuantitativeResult]] = None
    roiPercentage: Optional[str] = None
    annualSavings: Optional[str] = None

    # Challenges & Solutions
    challengesSolutions: Optional[List[ChallengeSolution]] = None

    # Contact & Media
    contactPerson: Optional[str] = None
    contactTitle: Optional[str] = None
    images: Optional[List[str]] = None

    # Extended sections
    technical_architecture: Optional[TechnicalArchitecture] = None
    future_roadmap: Optional[List[FutureRoadmapItem]] = None
    lessons_learned: Optional[List[LessonLearned]] = None

    # Additional fields
    industryTags: Optional[List[str]] = None
    technologyTags: Optional[List[str]] = None
    vendorProcess: Optional[str] = None
    vendorSelectionReasons: Optional[List[str]] = None
    projectTeamInternal: Optional[List[dict]] = None
    projectTeamVendor: Optional[List[dict]] = None
    phases: Optional[List[dict]] = None
    qualitativeImpacts: Optional[List[str]] = None
    roiTotalInvestment: Optional[str] = None
    roiThreeYearRoi: Optional[str] = None


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
    projectTeamInternal: Optional[List[dict]] = None
    projectTeamVendor: Optional[List[dict]] = None
    phases: Optional[List[dict]] = None
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


