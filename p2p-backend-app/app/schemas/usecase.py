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
    components: Optional[List[dict]] = None  # {layer, components: List[str], specifications}
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


