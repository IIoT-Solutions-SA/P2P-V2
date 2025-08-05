"""CRUD operations for Organization model."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.organization import Organization
from app.models.enums import OrganizationStatus, IndustryType
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    """CRUD operations specific to Organization model."""
    
    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        include_deleted: bool = False
    ) -> Optional[Organization]:
        """Get organization by name."""
        return await self.get_by_field(
            db,
            field_name="name",
            field_value=name,
            include_deleted=include_deleted
        )
    
    async def get_by_registration_number(
        self,
        db: AsyncSession,
        *,
        registration_number: str
    ) -> Optional[Organization]:
        """Get organization by registration number."""
        return await self.get_by_field(
            db,
            field_name="registration_number",
            field_value=registration_number
        )
    
    async def get_by_tax_id(
        self,
        db: AsyncSession,
        *,
        tax_id: str
    ) -> Optional[Organization]:
        """Get organization by tax ID."""
        return await self.get_by_field(
            db,
            field_name="tax_id",
            field_value=tax_id
        )
    
    async def get_by_industry(
        self,
        db: AsyncSession,
        *,
        industry_type: IndustryType,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Organization]:
        """Get organizations by industry type."""
        query = select(Organization).where(
            Organization.industry_type == industry_type
        )
        
        if not include_deleted:
            query = query.where(Organization.is_deleted == False)
        
        query = query.order_by(Organization.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Get all active organizations."""
        query = select(Organization).where(
            Organization.is_deleted == False,
            Organization.status.in_([
                OrganizationStatus.ACTIVE,
                OrganizationStatus.TRIAL
            ])
        )
        
        query = query.order_by(Organization.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def activate(
        self,
        db: AsyncSession,
        *,
        org_id: UUID
    ) -> Optional[Organization]:
        """Activate an organization."""
        org = await self.get(db, id=org_id)
        if org:
            return await self.update(
                db,
                db_obj=org,
                obj_in={"status": OrganizationStatus.ACTIVE}
            )
        return None
    
    async def suspend(
        self,
        db: AsyncSession,
        *,
        org_id: UUID
    ) -> Optional[Organization]:
        """Suspend an organization."""
        org = await self.get(db, id=org_id)
        if org:
            return await self.update(
                db,
                db_obj=org,
                obj_in={"status": OrganizationStatus.SUSPENDED}
            )
        return None
    
    async def search(
        self,
        db: AsyncSession,
        *,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Organization]:
        """Search organizations by name or email."""
        search_query = select(Organization).where(
            Organization.is_deleted == False,
            or_(
                Organization.name.ilike(f"%{query}%"),
                Organization.name_arabic.ilike(f"%{query}%"),
                Organization.email.ilike(f"%{query}%")
            )
        )
        
        search_query = search_query.offset(skip).limit(limit)
        
        result = await db.execute(search_query)
        return result.scalars().all()
    
    async def update_subscription(
        self,
        db: AsyncSession,
        *,
        org_id: UUID,
        subscription_tier: str,
        max_users: Optional[int] = None,
        max_use_cases: Optional[int] = None,
        max_storage_gb: Optional[int] = None
    ) -> Optional[Organization]:
        """Update organization subscription details."""
        org = await self.get(db, id=org_id)
        if not org:
            return None
        
        update_data = {"subscription_tier": subscription_tier}
        
        if max_users is not None:
            update_data["max_users"] = max_users
        if max_use_cases is not None:
            update_data["max_use_cases"] = max_use_cases
        if max_storage_gb is not None:
            update_data["max_storage_gb"] = max_storage_gb
        
        return await self.update(db, db_obj=org, obj_in=update_data)


# Create a singleton instance
organization = CRUDOrganization(Organization)