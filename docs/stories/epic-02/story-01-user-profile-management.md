# Story 1: User Profile Management System

## Story Details
**Epic**: Epic 2 - Core MVP Features  
**Story Points**: 8  
**Priority**: Critical (Foundation for all other features)  
**Dependencies**: Epic 1 Stories 1-5 (Repository, Frontend, Backend, Database, Authentication)

## User Story
**As a** SME professional (Factory Owner, Plant Engineer, Operations Manager)  
**I want** to create and manage a detailed profile showcasing my industry expertise and background  
**So that** other users can understand my qualifications and credibility when engaging with my content

## Acceptance Criteria
- [ ] User can complete profile during initial onboarding after registration
- [ ] Profile includes all required fields: name, role, industry sector, location, expertise tags
- [ ] Profile supports optional fields: company name, experience years, bio, contact preferences
- [ ] Users can upload and crop profile pictures (JPG, PNG, max 5MB)
- [ ] Company logo upload support for business owners
- [ ] Arabic and English language preference setting affects entire platform
- [ ] Profile displays verification status with appropriate badges
- [ ] Users can set profile visibility (public, verified users only, private)
- [ ] Profile shows user's forum activity summary and reputation score
- [ ] Profile editing preserves data and shows real-time validation

## Technical Specifications

### 1. Database Schema Updates

#### Update app/models/mongo_models.py
```python
from beanie import Document, Indexed, before_event, Replace, Insert
from pydantic import Field, EmailStr, validator
from datetime import datetime
from typing import Optional, List, Dict
import pymongo

class UserProfile(Document):
    # Basic Information
    user_id: Indexed(str, unique=True)  # Reference to SuperTokens user
    email: EmailStr
    name: str
    display_name: Optional[str] = None
    
    # Professional Information
    role: str  # factory_owner, plant_engineer, operations_manager, consultant, other
    industry_sector: str  # manufacturing, automotive, textiles, food_processing, etc.
    company_name: Optional[str] = None
    company_size: Optional[str] = None  # small, medium, large, enterprise
    experience_years: Optional[int] = None
    location: Dict[str, str]  # {"city": "Riyadh", "region": "Riyadh Province", "country": "Saudi Arabia"}
    
    # Expertise and Skills
    expertise_tags: List[str] = Field(default_factory=list, max_items=10)
    specializations: List[str] = Field(default_factory=list, max_items=5)
    certifications: List[Dict[str, str]] = Field(default_factory=list)  # [{"name": "Six Sigma", "year": "2020"}]
    
    # Profile Content
    bio: Optional[str] = Field(None, max_length=500)
    achievements: List[str] = Field(default_factory=list, max_items=5)
    interests: List[str] = Field(default_factory=list, max_items=8)
    
    # Media
    profile_picture_url: Optional[str] = None
    company_logo_url: Optional[str] = None
    
    # Platform Settings
    language_preference: str = "en"  # en, ar
    timezone: str = "Asia/Riyadh"
    notification_preferences: Dict[str, bool] = Field(default_factory=lambda: {
        "forum_replies": True,
        "private_messages": True,
        "weekly_digest": True,
        "verification_updates": True
    })
    
    # Privacy and Verification
    profile_visibility: str = "public"  # public, verified_only, private
    verification_status: str = "pending"  # pending, verified, rejected
    verification_submitted_at: Optional[datetime] = None
    verification_documents: List[Dict[str, str]] = Field(default_factory=list)
    
    # Platform Engagement
    reputation_score: int = 0
    forum_posts_count: int = 0
    forum_replies_count: int = 0
    best_answers_count: int = 0
    profile_views: int = 0
    
    # Metadata
    profile_completion_percentage: int = 0
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('expertise_tags')
    def validate_expertise_tags(cls, v):
        # Predefined list of valid expertise tags
        valid_tags = [
            "lean_manufacturing", "six_sigma", "quality_control", "automation",
            "plc_programming", "industrial_iot", "maintenance", "safety",
            "supply_chain", "inventory_management", "cost_reduction", "energy_efficiency",
            "digital_transformation", "erp_systems", "data_analytics", "ai_ml",
            "robotics", "3d_printing", "sustainability", "regulatory_compliance"
        ]
        for tag in v:
            if tag not in valid_tags:
                raise ValueError(f"Invalid expertise tag: {tag}")
        return v
    
    @before_event([Replace, Insert])
    def calculate_completion_percentage(self):
        """Calculate profile completion percentage"""
        total_fields = 15  # Core fields that count toward completion
        completed_fields = 0
        
        # Required fields
        if self.name: completed_fields += 1
        if self.role: completed_fields += 1
        if self.industry_sector: completed_fields += 1
        if self.location.get('city'): completed_fields += 1
        
        # Important optional fields
        if self.company_name: completed_fields += 1
        if self.experience_years: completed_fields += 1
        if self.bio: completed_fields += 1
        if self.expertise_tags: completed_fields += 1
        if self.specializations: completed_fields += 1
        if self.profile_picture_url: completed_fields += 1
        if self.achievements: completed_fields += 1
        if self.certifications: completed_fields += 1
        if self.interests: completed_fields += 1
        if self.company_logo_url and self.role == "factory_owner": completed_fields += 1
        if self.notification_preferences: completed_fields += 1
        
        self.profile_completion_percentage = int((completed_fields / total_fields) * 100)
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "user_profiles"
        indexes = [
            [("user_id", pymongo.ASCENDING)],
            [("email", pymongo.ASCENDING)],
            [("industry_sector", pymongo.ASCENDING)],
            [("location.city", pymongo.ASCENDING)],
            [("expertise_tags", pymongo.ASCENDING)],
            [("verification_status", pymongo.ASCENDING)],
            [("reputation_score", pymongo.DESCENDING)],
            [("created_at", pymongo.DESCENDING)]
        ]
```

### 2. API Endpoints

#### app/api/v1/endpoints/profiles.py
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from typing import Optional, List
from app.schemas.profiles import (
    UserProfileResponse, UserProfileUpdate, UserProfileCreate,
    ProfileSearchRequest, ProfileSearchResponse
)
from app.services.profile_service import ProfileService
from app.services.file_service import FileService
from app.core.logging import logger

router = APIRouter()

@router.post("/", response_model=UserProfileResponse)
async def create_profile(
    profile_data: UserProfileCreate,
    session: SessionContainer = Depends(verify_session())
):
    """Create user profile after initial registration"""
    user_id = session.get_user_id()
    
    try:
        profile = await ProfileService.create_profile(user_id, profile_data)
        return UserProfileResponse.from_profile(profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Profile creation failed: {e}")
        raise HTTPException(status_code=500, detail="Profile creation failed")

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(session: SessionContainer = Depends(verify_session())):
    """Get current user's profile"""
    user_id = session.get_user_id()
    
    profile = await ProfileService.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return UserProfileResponse.from_profile(profile)

@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    session: SessionContainer = Depends(verify_session())
):
    """Update current user's profile"""
    user_id = session.get_user_id()
    
    try:
        profile = await ProfileService.update_profile(user_id, profile_data)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return UserProfileResponse.from_profile(profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    session: SessionContainer = Depends(verify_session())
):
    """Upload and update profile picture"""
    user_id = session.get_user_id()
    
    # Validate file type and size
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if file.size > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    try:
        # Upload file and get URL
        file_url = await FileService.upload_profile_picture(user_id, file)
        
        # Update profile with new picture URL
        await ProfileService.update_profile_picture(user_id, file_url)
        
        return {"message": "Profile picture updated successfully", "url": file_url}
    except Exception as e:
        logger.error(f"Profile picture upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@router.post("/me/company-logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    session: SessionContainer = Depends(verify_session())
):
    """Upload and update company logo"""
    user_id = session.get_user_id()
    
    # Check if user is authorized to upload company logo
    profile = await ProfileService.get_profile_by_user_id(user_id)
    if not profile or profile.role not in ["factory_owner", "consultant"]:
        raise HTTPException(status_code=403, detail="Not authorized to upload company logo")
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        file_url = await FileService.upload_company_logo(user_id, file)
        await ProfileService.update_company_logo(user_id, file_url)
        
        return {"message": "Company logo updated successfully", "url": file_url}
    except Exception as e:
        logger.error(f"Company logo upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """Get public profile of any user"""
    profile = await ProfileService.get_public_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return UserProfileResponse.from_profile(profile)

@router.post("/search", response_model=ProfileSearchResponse)
async def search_profiles(
    search_request: ProfileSearchRequest,
    session: SessionContainer = Depends(verify_session())
):
    """Search user profiles with filters"""
    try:
        results = await ProfileService.search_profiles(search_request)
        return results
    except Exception as e:
        logger.error(f"Profile search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.post("/me/verify")
async def submit_verification_request(
    documents: List[UploadFile] = File(...),
    session: SessionContainer = Depends(verify_session())
):
    """Submit verification request with supporting documents"""
    user_id = session.get_user_id()
    
    if len(documents) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 documents allowed")
    
    try:
        verification_id = await ProfileService.submit_verification(user_id, documents)
        return {"message": "Verification request submitted", "verification_id": verification_id}
    except Exception as e:
        logger.error(f"Verification submission failed: {e}")
        raise HTTPException(status_code=500, detail="Verification submission failed")
```

### 3. Pydantic Schemas

#### app/schemas/profiles.py
```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict
from datetime import datetime

class UserProfileBase(BaseModel):
    name: str
    display_name: Optional[str] = None
    role: str
    industry_sector: str
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    experience_years: Optional[int] = None
    location: Dict[str, str]
    bio: Optional[str] = None
    language_preference: str = "en"
    timezone: str = "Asia/Riyadh"
    profile_visibility: str = "public"

class UserProfileCreate(UserProfileBase):
    expertise_tags: List[str] = []
    specializations: List[str] = []
    achievements: List[str] = []
    interests: List[str] = []
    certifications: List[Dict[str, str]] = []
    notification_preferences: Dict[str, bool] = {}

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[str] = None
    industry_sector: Optional[str] = None
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    experience_years: Optional[int] = None
    location: Optional[Dict[str, str]] = None
    bio: Optional[str] = None
    expertise_tags: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    certifications: Optional[List[Dict[str, str]]] = None
    notification_preferences: Optional[Dict[str, bool]] = None
    language_preference: Optional[str] = None
    timezone: Optional[str] = None
    profile_visibility: Optional[str] = None

class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    name: str
    display_name: Optional[str]
    role: str
    industry_sector: str
    company_name: Optional[str]
    location: Dict[str, str]
    expertise_tags: List[str]
    specializations: List[str]
    bio: Optional[str]
    profile_picture_url: Optional[str]
    company_logo_url: Optional[str]
    verification_status: str
    reputation_score: int
    profile_completion_percentage: int
    forum_activity: Dict[str, int]
    created_at: datetime
    last_activity_at: datetime
    
    @classmethod
    def from_profile(cls, profile):
        return cls(
            user_id=profile.user_id,
            email=profile.email,
            name=profile.name,
            display_name=profile.display_name,
            role=profile.role,
            industry_sector=profile.industry_sector,
            company_name=profile.company_name,
            location=profile.location,
            expertise_tags=profile.expertise_tags,
            specializations=profile.specializations,
            bio=profile.bio,
            profile_picture_url=profile.profile_picture_url,
            company_logo_url=profile.company_logo_url,
            verification_status=profile.verification_status,
            reputation_score=profile.reputation_score,
            profile_completion_percentage=profile.profile_completion_percentage,
            forum_activity={
                "posts": profile.forum_posts_count,
                "replies": profile.forum_replies_count,
                "best_answers": profile.best_answers_count
            },
            created_at=profile.created_at,
            last_activity_at=profile.last_activity_at
        )

class ProfileSearchRequest(BaseModel):
    query: Optional[str] = None
    industry_sector: Optional[str] = None
    location_city: Optional[str] = None
    expertise_tags: Optional[List[str]] = None
    role: Optional[str] = None
    verification_status: Optional[str] = None
    min_reputation: Optional[int] = None
    limit: int = 20
    offset: int = 0

class ProfileSearchResponse(BaseModel):
    profiles: List[UserProfileResponse]
    total_count: int
    has_more: bool
```

### 4. Service Layer

#### app/services/profile_service.py
```python
from typing import Optional, List
from app.models.mongo_models import UserProfile
from app.schemas.profiles import UserProfileCreate, UserProfileUpdate, ProfileSearchRequest, ProfileSearchResponse
from app.core.logging import logger
from datetime import datetime

class ProfileService:
    @staticmethod
    async def create_profile(user_id: str, profile_data: UserProfileCreate) -> UserProfile:
        """Create a new user profile"""
        # Check if profile already exists
        existing = await UserProfile.find_one(UserProfile.user_id == user_id)
        if existing:
            raise ValueError("Profile already exists for this user")
        
        profile = UserProfile(
            user_id=user_id,
            **profile_data.dict()
        )
        
        await profile.create()
        logger.info(f"Profile created for user: {user_id}")
        return profile
    
    @staticmethod
    async def get_profile_by_user_id(user_id: str) -> Optional[UserProfile]:
        """Get profile by user ID"""
        return await UserProfile.find_one(UserProfile.user_id == user_id)
    
    @staticmethod
    async def update_profile(user_id: str, update_data: UserProfileUpdate) -> Optional[UserProfile]:
        """Update user profile"""
        profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not profile:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)
        
        profile.updated_at = datetime.utcnow()
        await profile.save()
        
        logger.info(f"Profile updated for user: {user_id}")
        return profile
    
    @staticmethod
    async def get_public_profile(user_id: str) -> Optional[UserProfile]:
        """Get public profile (respects visibility settings)"""
        profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        
        if not profile or profile.profile_visibility == "private":
            return None
        
        # Increment profile views
        profile.profile_views += 1
        await profile.save()
        
        return profile
    
    @staticmethod
    async def search_profiles(search_request: ProfileSearchRequest) -> ProfileSearchResponse:
        """Search profiles with filters"""
        query_filters = []
        
        # Text search
        if search_request.query:
            query_filters.append({
                "$or": [
                    {"name": {"$regex": search_request.query, "$options": "i"}},
                    {"company_name": {"$regex": search_request.query, "$options": "i"}},
                    {"bio": {"$regex": search_request.query, "$options": "i"}}
                ]
            })
        
        # Filter by industry
        if search_request.industry_sector:
            query_filters.append({"industry_sector": search_request.industry_sector})
        
        # Filter by location
        if search_request.location_city:
            query_filters.append({"location.city": search_request.location_city})
        
        # Filter by expertise tags
        if search_request.expertise_tags:
            query_filters.append({"expertise_tags": {"$in": search_request.expertise_tags}})
        
        # Filter by role
        if search_request.role:
            query_filters.append({"role": search_request.role})
        
        # Filter by verification status
        if search_request.verification_status:
            query_filters.append({"verification_status": search_request.verification_status})
        
        # Filter by minimum reputation
        if search_request.min_reputation:
            query_filters.append({"reputation_score": {"$gte": search_request.min_reputation}})
        
        # Only show public profiles
        query_filters.append({"profile_visibility": "public"})
        
        # Build final query
        final_query = {"$and": query_filters} if query_filters else {}
        
        # Execute search
        profiles = await UserProfile.find(final_query).sort(
            [("reputation_score", -1), ("created_at", -1)]
        ).skip(search_request.offset).limit(search_request.limit).to_list()
        
        total_count = await UserProfile.find(final_query).count()
        
        return ProfileSearchResponse(
            profiles=[profile for profile in profiles],
            total_count=total_count,
            has_more=total_count > (search_request.offset + search_request.limit)
        )
    
    @staticmethod
    async def update_profile_picture(user_id: str, file_url: str) -> bool:
        """Update profile picture URL"""
        profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not profile:
            return False
        
        profile.profile_picture_url = file_url
        profile.updated_at = datetime.utcnow()
        await profile.save()
        return True
    
    @staticmethod
    async def update_company_logo(user_id: str, file_url: str) -> bool:
        """Update company logo URL"""
        profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if not profile:
            return False
        
        profile.company_logo_url = file_url
        profile.updated_at = datetime.utcnow()
        await profile.save()
        return True
```

### 5. Frontend Components

#### Create frontend/src/components/Profile/ProfileForm.tsx
```typescript
import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  role: z.string().min(1, 'Role is required'),
  industry_sector: z.string().min(1, 'Industry sector is required'),
  company_name: z.string().optional(),
  location: z.object({
    city: z.string().min(1, 'City is required'),
    region: z.string().min(1, 'Region is required'),
    country: z.string().default('Saudi Arabia')
  }),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  experience_years: z.number().min(0).max(50).optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

interface ProfileFormProps {
  initialData?: Partial<ProfileFormData>;
  onSubmit: (data: ProfileFormData) => Promise<void>;
  isLoading?: boolean;
}

export default function ProfileForm({ initialData, onSubmit, isLoading }: ProfileFormProps) {
  const { t } = useTranslation();
  const [expertiseTags, setExpertiseTags] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState('');

  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: '',
      role: '',
      industry_sector: '',
      company_name: '',
      location: {
        city: '',
        region: '',
        country: 'Saudi Arabia'
      },
      bio: '',
      experience_years: undefined,
      ...initialData
    }
  });

  const roles = [
    { value: 'factory_owner', label: t('profile.roles.factory_owner') },
    { value: 'plant_engineer', label: t('profile.roles.plant_engineer') },
    { value: 'operations_manager', label: t('profile.roles.operations_manager') },
    { value: 'consultant', label: t('profile.roles.consultant') },
    { value: 'other', label: t('profile.roles.other') }
  ];

  const industrySectors = [
    { value: 'manufacturing', label: t('profile.industries.manufacturing') },
    { value: 'automotive', label: t('profile.industries.automotive') },
    { value: 'textiles', label: t('profile.industries.textiles') },
    { value: 'food_processing', label: t('profile.industries.food_processing') },
    { value: 'chemicals', label: t('profile.industries.chemicals') },
    { value: 'electronics', label: t('profile.industries.electronics') }
  ];

  const availableTags = [
    'lean_manufacturing', 'six_sigma', 'quality_control', 'automation',
    'plc_programming', 'industrial_iot', 'maintenance', 'safety',
    'supply_chain', 'inventory_management', 'cost_reduction', 'energy_efficiency'
  ];

  const addExpertiseTag = (tag: string) => {
    if (tag && !expertiseTags.includes(tag) && expertiseTags.length < 10) {
      setExpertiseTags([...expertiseTags, tag]);
      setCurrentTag('');
    }
  };

  const removeExpertiseTag = (tagToRemove: string) => {
    setExpertiseTags(expertiseTags.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = async (data: ProfileFormData) => {
    try {
      await onSubmit({
        ...data,
        expertise_tags: expertiseTags
      });
    } catch (error) {
      console.error('Profile submission error:', error);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>{t('profile.title')}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('profile.sections.basic_info')}</h3>
            
            <div>
              <Label htmlFor="name">{t('profile.fields.name')}</Label>
              <Input
                id="name"
                {...form.register('name')}
                placeholder={t('profile.placeholders.name')}
              />
              {form.formState.errors.name && (
                <p className="text-sm text-red-600">{form.formState.errors.name.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="role">{t('profile.fields.role')}</Label>
              <Select onValueChange={(value) => form.setValue('role', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('profile.placeholders.role')} />
                </SelectTrigger>
                <SelectContent>
                  {roles.map((role) => (
                    <SelectItem key={role.value} value={role.value}>
                      {role.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="industry_sector">{t('profile.fields.industry')}</Label>
              <Select onValueChange={(value) => form.setValue('industry_sector', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('profile.placeholders.industry')} />
                </SelectTrigger>
                <SelectContent>
                  {industrySectors.map((sector) => (
                    <SelectItem key={sector.value} value={sector.value}>
                      {sector.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Company Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('profile.sections.company_info')}</h3>
            
            <div>
              <Label htmlFor="company_name">{t('profile.fields.company_name')}</Label>
              <Input
                id="company_name"
                {...form.register('company_name')}
                placeholder={t('profile.placeholders.company_name')}
              />
            </div>

            <div>
              <Label htmlFor="experience_years">{t('profile.fields.experience')}</Label>
              <Input
                id="experience_years"
                type="number"
                min="0"
                max="50"
                {...form.register('experience_years', { valueAsNumber: true })}
                placeholder={t('profile.placeholders.experience')}
              />
            </div>
          </div>

          {/* Location */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('profile.sections.location')}</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="city">{t('profile.fields.city')}</Label>
                <Input
                  id="city"
                  {...form.register('location.city')}
                  placeholder={t('profile.placeholders.city')}
                />
              </div>
              <div>
                <Label htmlFor="region">{t('profile.fields.region')}</Label>
                <Input
                  id="region"
                  {...form.register('location.region')}
                  placeholder={t('profile.placeholders.region')}
                />
              </div>
            </div>
          </div>

          {/* Expertise Tags */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('profile.sections.expertise')}</h3>
            
            <div>
              <Label>{t('profile.fields.expertise_tags')}</Label>
              <div className="flex flex-wrap gap-2 mb-2">
                {expertiseTags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                    {t(`profile.tags.${tag}`)}
                    <X
                      className="h-3 w-3 cursor-pointer"
                      onClick={() => removeExpertiseTag(tag)}
                    />
                  </Badge>
                ))}
              </div>
              <Select value={currentTag} onValueChange={setCurrentTag}>
                <SelectTrigger>
                  <SelectValue placeholder={t('profile.placeholders.add_expertise')} />
                </SelectTrigger>
                <SelectContent>
                  {availableTags
                    .filter(tag => !expertiseTags.includes(tag))
                    .map((tag) => (
                    <SelectItem key={tag} value={tag}>
                      {t(`profile.tags.${tag}`)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {currentTag && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2"
                  onClick={() => addExpertiseTag(currentTag)}
                >
                  {t('profile.actions.add_tag')}
                </Button>
              )}
            </div>
          </div>

          {/* Bio */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">{t('profile.sections.about')}</h3>
            
            <div>
              <Label htmlFor="bio">{t('profile.fields.bio')}</Label>
              <Textarea
                id="bio"
                {...form.register('bio')}
                placeholder={t('profile.placeholders.bio')}
                rows={4}
                maxLength={500}
              />
              <p className="text-sm text-gray-500 mt-1">
                {form.watch('bio')?.length || 0}/500
              </p>
            </div>
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? t('common.loading') : t('profile.actions.save')}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
```

## Implementation Steps

1. **Database Schema Setup**
   ```bash
   # Update MongoDB models with UserProfile schema
   # Run database initialization to create indexes
   ```

2. **Backend API Implementation**
   ```bash
   # Implement ProfileService and API endpoints
   # Add file upload service for profile pictures
   # Set up image processing for resizing/optimization
   ```

3. **Frontend Components**
   ```bash
   # Create profile form components
   # Implement profile view and editing pages
   # Add image upload functionality with preview
   ```

4. **Integration Testing**
   - Test profile creation flow end-to-end
   - Verify file upload and image processing
   - Test profile search and filtering
   - Validate data persistence and updates

## Testing Checklist
- [ ] User can create profile with all required fields
- [ ] Profile completion percentage calculates correctly
- [ ] Image upload works for profile pictures and company logos
- [ ] Profile visibility settings are respected
- [ ] Search functionality returns relevant results
- [ ] Arabic/English language switching affects profile content
- [ ] Form validation works for all input fields
- [ ] Profile editing preserves existing data
- [ ] Verification request submission works

## Dependencies
- Epic 1 Stories 1-5 must be completed
- File storage service (AWS S3) configured
- Image processing service available

## Notes
- Implement comprehensive input validation
- Ensure profile data privacy and security
- Plan for future verification workflow integration
- Consider performance optimization for search functionality