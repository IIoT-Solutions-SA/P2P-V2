from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.emailpassword.asyncio import update_email_or_password, sign_in
from supertokens_python.recipe.emailpassword.interfaces import (
    SignInOkResult,
    UpdateEmailOrPasswordOkResult,
    EmailAlreadyExistsError
)
from supertokens_python.types import RecipeUserId
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.services.database_service import UserService
from app.models.mongo_models import Organization, User as MongoUser
from app.models.pg_models import User as PGUser

router = APIRouter()

class UpdateProfileRequest(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    expertiseTags: Optional[List[str]] = None

class UpdateEmailRequest(BaseModel):
    newEmail: EmailStr
    password: str  # Current password for verification

class UpdatePasswordRequest(BaseModel):
    currentPassword: str
    newPassword: str

@router.get("/me")
async def get_current_user(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user profile.
    Requires valid SuperTokens session.
    """
    try:
        # Get SuperTokens user ID from session
        supertokens_user_id = session.get_user_id()
        
        # Find user in our database by supertokens_id
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User profile not found. Please contact support."
            )
        
        # Resolve organization from Mongo profile if available; fallback to domain inference
        mongo_profile = await MongoUser.find_one(MongoUser.email == user.email)
        organization = None
        if mongo_profile and mongo_profile.organization_id:
            org = await Organization.find_one(Organization.id == mongo_profile.organization_id)
            if org:
                organization = {
                    "id": str(org.id),
                    "name": org.name,
                    "domain": org.domain,
                    "industry": org.industry_sector,
                    "size": org.size,
                    "country": org.country,
                    "city": org.city,
                    "isActive": org.is_active,
                    "createdAt": org.created_at,
                    "adminUserId": str(user.id)
                }
        if organization is None:
            domain = user.email.split('@')[1]
            company_name = domain.split('.')[0].replace('-', ' ').title()
            organization = {
                "id": f"org-{user.id}",
                "name": company_name,
                "domain": domain,
                "industry": "Technology",
                "size": "medium",
                "country": "Saudi Arabia",
                "city": "Riyadh",
                "isActive": True,
                "createdAt": user.created_at,
                "adminUserId": str(user.id)
            }
        
        # Format user response
        user_response = {
            "id": str(user.id),
            "mongo_id": str(mongo_profile.id) if mongo_profile else None,  # Add mongo_id for authorization checks
            "email": user.email,
            "firstName": user.name.split(' ')[0] if user.name else "",
            "lastName": " ".join(user.name.split(' ')[1:]) if len(user.name.split(' ')) > 1 else "",
            "role": user.role,
            "title": mongo_profile.title if mongo_profile and hasattr(mongo_profile, 'title') else "Team Member",
            "company": organization["name"],  # Use organization name as company
            "location": mongo_profile.location if mongo_profile and hasattr(mongo_profile, 'location') else "",
            "industrySector": organization["industry"],  # Use organization's industry
            "expertiseTags": mongo_profile.expertise_tags if mongo_profile and hasattr(mongo_profile, 'expertise_tags') else [],
            "organizationId": organization["id"],  
            "isActive": user.is_active,
            "lastLogin": user.updated_at,  # Using updated_at as proxy for last login
            "createdAt": user.created_at
        }
        
        return {
            "user": user_response,
            "organization": organization
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching user profile: {str(e)}"
        )

@router.put("/profile")
async def update_profile(
    profile_data: UpdateProfileRequest,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    Requires valid SuperTokens session.
    """
    try:
        # Get SuperTokens user ID from session
        supertokens_user_id = session.get_user_id()
        
        # Find user in our database by supertokens_id
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User profile not found."
            )
        
        # Update PostgreSQL user if name fields are provided
        if profile_data.firstName or profile_data.lastName:
            full_name = f"{profile_data.firstName or user.name.split(' ')[0]} {profile_data.lastName or ' '.join(user.name.split(' ')[1:]) if len(user.name.split(' ')) > 1 else ''}".strip()
            user.name = full_name
            await db.commit()
            await db.refresh(user)
        
        # Update MongoDB profile
        mongo_profile = await MongoUser.find_one(MongoUser.email == user.email)
        
        if mongo_profile:
            # Update existing profile
            if profile_data.firstName or profile_data.lastName:
                mongo_profile.name = f"{profile_data.firstName or mongo_profile.name.split(' ')[0]} {profile_data.lastName or ' '.join(mongo_profile.name.split(' ')[1:]) if len(mongo_profile.name.split(' ')) > 1 else ''}".strip()
            
            if profile_data.title is not None:
                mongo_profile.title = profile_data.title
            if profile_data.location is not None:
                mongo_profile.location = profile_data.location
            if profile_data.expertiseTags is not None:
                mongo_profile.expertise_tags = profile_data.expertiseTags
            
            mongo_profile.updated_at = datetime.utcnow()
            await mongo_profile.save()
        else:
            # Create new MongoDB profile if it doesn't exist
            mongo_profile = MongoUser(
                email=user.email,
                name=user.name,
                title=profile_data.title or "Team Member",
                location=profile_data.location,
                expertise_tags=profile_data.expertiseTags or [],
                role=user.role,
                verified=user.is_verified
            )
            await mongo_profile.insert()
        
        # Return updated profile using the same format as get_current_user
        return await get_current_user(session, db)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user profile: {str(e)}"
        )

@router.put("/email")
async def update_email(
    email_data: UpdateEmailRequest,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's email address.
    Requires current password for verification.
    """
    try:
        # Get current user
        supertokens_user_id = session.get_user_id()
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        sign_in_result = await sign_in("public", user.email, email_data.password)
        if not isinstance(sign_in_result, SignInOkResult):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Store old email before updating
        old_email = user.email
        
        # Get the recipe_user_id from the sign in result for the update
        recipe_user_id = sign_in_result.user.id
        
        # Update email in SuperTokens
        update_result = await update_email_or_password(
            recipe_user_id=RecipeUserId(recipe_user_id),
            email=email_data.newEmail
        )
        
        # Check if update was successful
        if isinstance(update_result, EmailAlreadyExistsError):
            raise HTTPException(status_code=400, detail="Email already exists")
        elif not isinstance(update_result, UpdateEmailOrPasswordOkResult):
            raise HTTPException(status_code=400, detail="Failed to update email")
        
        # Update email in PostgreSQL
        user.email = email_data.newEmail
        await db.commit()
        
        # Update email in MongoDB using the OLD email to find the profile
        mongo_profile = await MongoUser.find_one(MongoUser.email == old_email)
        if mongo_profile:
            mongo_profile.email = email_data.newEmail
            await mongo_profile.save()
        
        return {"status": "OK", "message": "Email updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating email: {str(e)}"
        )

@router.put("/password")
async def update_password(
    password_data: UpdatePasswordRequest,
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's password.
    Requires current password for verification.
    """
    try:
        # Get current user
        supertokens_user_id = session.get_user_id()
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        sign_in_result = await sign_in("public", user.email, password_data.currentPassword)
        if not isinstance(sign_in_result, SignInOkResult):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Get the recipe_user_id from the sign in result for the update
        recipe_user_id = sign_in_result.user.id
        
        # Update password in SuperTokens
        update_result = await update_email_or_password(
            recipe_user_id=RecipeUserId(recipe_user_id),
            password=password_data.newPassword
        )
        
        if not isinstance(update_result, UpdateEmailOrPasswordOkResult):
            raise HTTPException(status_code=400, detail="Failed to update password")
        
        return {"status": "OK", "message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating password: {str(e)}"
        )

@router.get("/users/organization")
async def get_organization_members(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all members of the current user's organization.
    Requires valid SuperTokens session.
    """
    try:
        # Get current user
        supertokens_user_id = session.get_user_id()
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get current user's MongoDB profile to find organization
        mongo_profile = await MongoUser.find_one(MongoUser.email == user.email)
        
        if not mongo_profile or not mongo_profile.organization_id:
            # If no organization, return just the current user
            return {
                "users": [{
                    "id": str(user.id),
                    "email": user.email,
                    "firstName": user.name.split(' ')[0] if user.name else "",
                    "lastName": " ".join(user.name.split(' ')[1:]) if len(user.name.split(' ')) > 1 else "",
                    "name": user.name,
                    "role": user.role,
                    "title": mongo_profile.title if mongo_profile and hasattr(mongo_profile, 'title') else "Team Member",
                    "company": mongo_profile.company if mongo_profile and hasattr(mongo_profile, 'company') else "",
                    "location": mongo_profile.location if mongo_profile and hasattr(mongo_profile, 'location') else "",
                    "industrySector": mongo_profile.industry_sector if mongo_profile and hasattr(mongo_profile, 'industry_sector') else "",
                    "expertiseTags": mongo_profile.expertise_tags if mongo_profile and hasattr(mongo_profile, 'expertise_tags') else [],
                    "isActive": user.is_active,
                    "createdAt": user.created_at
                }]
            }
        
        # Find all MongoDB users in the same organization
        org_members = await MongoUser.find(MongoUser.organization_id == mongo_profile.organization_id).to_list()
        
        # Build the response with all organization members
        users_list = []
        for member in org_members:
            # Try to find the corresponding PostgreSQL user
            pg_user = await UserService.get_user_by_email_pg(db, member.email)
            
            users_list.append({
                "id": str(pg_user.id) if pg_user else str(member.id),
                "email": member.email,
                "firstName": member.name.split(' ')[0] if member.name else "",
                "lastName": " ".join(member.name.split(' ')[1:]) if len(member.name.split(' ')) > 1 else "",
                "name": member.name,
                "role": member.role,
                "title": member.title if hasattr(member, 'title') else "Team Member",
                "company": member.company if hasattr(member, 'company') else "",
                "location": member.location if hasattr(member, 'location') else "",
                "industrySector": member.industry_sector if hasattr(member, 'industry_sector') else "",
                "expertiseTags": member.expertise_tags if hasattr(member, 'expertise_tags') else [],
                "isActive": pg_user.is_active if pg_user else True,
                "createdAt": pg_user.created_at if pg_user else member.created_at
            })
        
        return {"users": users_list}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching organization members: {str(e)}"
        )