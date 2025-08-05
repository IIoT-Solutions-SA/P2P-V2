"""CRUD operations for User model."""

from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.models.enums import UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations specific to User model."""
    
    async def get_by_email(
        self,
        db: AsyncSession,
        *,
        email: str,
        include_deleted: bool = False
    ) -> Optional[User]:
        """Get user by email address."""
        return await self.get_by_field(
            db,
            field_name="email",
            field_value=email,
            include_deleted=include_deleted
        )
    
    async def get_by_supertokens_id(
        self,
        db: AsyncSession,
        *,
        supertokens_user_id: str
    ) -> Optional[User]:
        """Get user by SuperTokens user ID."""
        return await self.get_by_field(
            db,
            field_name="supertokens_user_id",
            field_value=supertokens_user_id
        )
    
    async def get_by_organization(
        self,
        db: AsyncSession,
        *,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        include_deleted: bool = False
    ) -> List[User]:
        """Get all users in an organization with optional filtering."""
        query = select(User).where(User.organization_id == organization_id)
        
        # Apply filters
        if not include_deleted:
            query = query.where(User.is_deleted == False)
        
        if role:
            query = query.where(User.role == role)
        
        if status:
            query = query.where(User.status == status)
        
        # Order by created_at desc
        query = query.order_by(User.created_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_admins_by_organization(
        self,
        db: AsyncSession,
        *,
        organization_id: UUID,
        include_deleted: bool = False
    ) -> List[User]:
        """Get all admin users in an organization."""
        return await self.get_by_organization(
            db,
            organization_id=organization_id,
            role=UserRole.ADMIN,
            include_deleted=include_deleted
        )
    
    async def count_by_organization(
        self,
        db: AsyncSession,
        *,
        organization_id: UUID,
        include_deleted: bool = False
    ) -> int:
        """Count users in an organization."""
        return await self.count(
            db,
            include_deleted=include_deleted,
            filters={"organization_id": organization_id}
        )
    
    async def activate(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> Optional[User]:
        """Activate a user account."""
        user = await self.get(db, id=user_id)
        if user:
            return await self.update(
                db,
                db_obj=user,
                obj_in={"status": UserStatus.ACTIVE}
            )
        return None
    
    async def deactivate(
        self,
        db: AsyncSession,
        *,
        user_id: UUID
    ) -> Optional[User]:
        """Deactivate a user account."""
        user = await self.get(db, id=user_id)
        if user:
            return await self.update(
                db,
                db_obj=user,
                obj_in={"status": UserStatus.INACTIVE}
            )
        return None
    
    async def change_role(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        new_role: UserRole
    ) -> Optional[User]:
        """Change a user's role."""
        user = await self.get(db, id=user_id)
        if user:
            return await self.update(
                db,
                db_obj=user,
                obj_in={"role": new_role}
            )
        return None
    
    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name or email."""
        search_query = select(User).where(
            and_(
                User.is_deleted == False,
                or_(
                    User.email.ilike(f"%{query}%"),
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%")
                )
            )
        )
        
        if organization_id:
            search_query = search_query.where(User.organization_id == organization_id)
        
        search_query = search_query.offset(skip).limit(limit)
        
        result = await db.execute(search_query)
        return result.scalars().all()


# Create a singleton instance
user = CRUDUser(User)