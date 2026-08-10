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
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Annotated
from datetime import datetime
from app.core.input_validation import check_safe_text, check_safe_tag

from app.core.database import get_db
from app.core.config import settings
from app.core.email_domains import get_email_domain, is_blocked_domain
from app.services.database_service import UserService
from app.models.mongo_models import Organization, User as MongoUser
from app.models.pg_models import User as PGUser

router = APIRouter()


@router.post("/session-activity", status_code=204)
async def record_session_activity(
    _session: SessionContainer = Depends(verify_session()),
):
    """Record genuine browser activity through the global session policy hook."""
    return None


class UpdateProfileRequest(BaseModel):
    firstName: Optional[Annotated[str, Field(max_length=50)]] = None
    lastName: Optional[Annotated[str, Field(max_length=50)]] = None
    title: Optional[Annotated[str, Field(max_length=100)]] = None
    location: Optional[Annotated[str, Field(max_length=100)]] = None
    expertiseTags: Optional[Annotated[List[str], Field(max_length=10)]] = None

    @field_validator('firstName', 'lastName')
    @classmethod
    def validate_names(cls, v):
        if not v:
            return v
        v_safe = check_safe_text(v)
        import re
        if not re.match(r"^[a-zA-Z\u0600-\u06FF\s\-']+$", v_safe):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return v_safe

    @field_validator('title', 'location')
    @classmethod
    def validate_safe_strings(cls, v):
        return check_safe_text(v) if v is not None else v

    @field_validator('expertiseTags')
    @classmethod
    def validate_safe_tags(cls, v):
        if v is not None:
            for item in v:
                check_safe_tag(item)
        return v

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
            company_name = ((mongo_profile.company if mongo_profile else None) or "").strip() or domain.split('.')[0].replace('-', ' ').title()
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
            "profilePictureUrl": user.profile_picture_url,  # Profile picture from PostgreSQL (camelCase for frontend)
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
        import logging
        logging.getLogger(__name__).error(f"Error fetching user profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching your profile. Please try again."
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
        import logging
        logging.getLogger(__name__).error(f"Error updating user profile: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating your profile. Please try again."
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
    Blocks personal email domains and enforces organization domain matching.
    SuperTokens, PostgreSQL, and MongoDB are only updated after all validation passes.
    """
    try:
        import logging
        logger = logging.getLogger(__name__)

        # ── Step 1: Look up current user ─────────────────────────────────────
        supertokens_user_id = session.get_user_id()
        user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_email = email_data.newEmail.strip().lower()

        # ── Step 2: Block personal / free email domains ──────────────────────
        new_domain = get_email_domain(new_email)
        if not new_domain:
            raise HTTPException(status_code=400, detail="Invalid email address")

        if is_blocked_domain(new_domain, settings.BLOCKED_EMAIL_DOMAINS):
            raise HTTPException(
                status_code=403,
                detail="Personal email addresses are not allowed. Please use your company email."
            )

        # ── Step 3: Enforce organization domain matching ─────────────────────
        current_domain = get_email_domain(user.email)
        mongo_profile = await MongoUser.find_one(MongoUser.email == user.email)

        # Determine the required domain from the organization, or fall back to current email domain
        required_domain = None
        if mongo_profile and mongo_profile.organization_id:
            org = await Organization.find_one(Organization.id == mongo_profile.organization_id)
            if org and org.domain:
                required_domain = org.domain.strip().lower()

        # If no org domain found, use the current email domain as the required domain
        if not required_domain:
            required_domain = current_domain

        if required_domain and new_domain != required_domain:
            raise HTTPException(
                status_code=403,
                detail=f"New email must match your organization domain (@{required_domain})."
            )

        # ── Step 4: Verify current password ──────────────────────────────────
        sign_in_result = await sign_in("public", user.email, email_data.password)
        if not isinstance(sign_in_result, SignInOkResult):
            raise HTTPException(status_code=400, detail="Invalid password")

        # ── Step 5: All validation passed — update all three stores ──────────
        old_email = user.email
        recipe_user_id = sign_in_result.user.id

        # 5a. Update email in SuperTokens
        update_result = await update_email_or_password(
            recipe_user_id=RecipeUserId(recipe_user_id),
            email=new_email
        )

        if isinstance(update_result, EmailAlreadyExistsError):
            raise HTTPException(status_code=400, detail="Email already exists")
        elif not isinstance(update_result, UpdateEmailOrPasswordOkResult):
            raise HTTPException(status_code=400, detail="Failed to update email")

        # 5b. Update email in PostgreSQL
        user.email = new_email
        await db.commit()

        # 5c. Update email in MongoDB using the OLD email to find the profile
        if mongo_profile:
            mongo_profile.email = new_email
            mongo_profile.updated_at = datetime.utcnow()
            await mongo_profile.save()
        else:
            # Profile might not have been fetched if we skipped the org lookup path
            mongo_fallback = await MongoUser.find_one(MongoUser.email == old_email)
            if mongo_fallback:
                mongo_fallback.email = new_email
                mongo_fallback.updated_at = datetime.utcnow()
                await mongo_fallback.save()

        logger.info(f"Email updated from {old_email} to {new_email} for user {supertokens_user_id}")
        return {"status": "OK", "message": "Email updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error updating email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating your email. Please try again."
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
        import logging
        logging.getLogger(__name__).error(f"Error updating password: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating your password. Please try again."
        )

@router.get("/users/directory")
async def get_people_directory(
    session: SessionContainer = Depends(verify_session()),
    db: AsyncSession = Depends(get_db)
):
    """Return the authenticated PeerLink-wide collaborator directory.

    Unlike ``/users/organization``, this endpoint is intentionally not scoped to
    the current organization. It exposes only profile fields already intended
    for the shared People workspace and leaves organization administration to
    the dedicated organization route.
    """
    try:
        supertokens_user_id = session.get_user_id()
        current_user = await UserService.get_user_by_supertokens_id(db, supertokens_user_id)
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        current_profile = await MongoUser.find_one(MongoUser.email == current_user.email)
        current_organization_id = current_profile.organization_id if current_profile else None
        directory_profiles = await MongoUser.find_all().to_list()
        users_list = []
        for profile in directory_profiles:
            pg_user = await UserService.get_user_by_email_pg(db, profile.email)
            if pg_user and not pg_user.is_active:
                continue

            profile_name = profile.name or ""
            name_parts = profile_name.split()
            users_list.append({
                "id": str(pg_user.id) if pg_user else str(profile.id),
                "email": profile.email,
                "firstName": name_parts[0] if name_parts else "",
                "lastName": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                "name": profile_name,
                "role": profile.role,
                "title": profile.title or "Manufacturing professional",
                "company": profile.company or "",
                "location": profile.location or "",
                "industrySector": profile.industry_sector or "",
                "expertiseTags": profile.expertise_tags or [],
                "isActive": pg_user.is_active if pg_user else True,
                "createdAt": pg_user.created_at if pg_user else profile.created_at,
                "profilePictureUrl": profile.profile_picture_url,
                "isCurrentOrganization": bool(
                    profile.organization_id
                    and current_organization_id == profile.organization_id
                ),
            })

        return {"users": users_list, "total": len(users_list)}
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching people directory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="The People directory could not be loaded. Please try again.")


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
        import logging
        logging.getLogger(__name__).error(f"Error fetching organization members: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching organization members. Please try again."
        )