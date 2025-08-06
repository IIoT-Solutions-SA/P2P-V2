"""CRUD operations for User Invitations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.invitation import UserInvitation
from app.models.enums import InvitationStatus, UserRole
from app.schemas.invitation import InvitationCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


class CRUDInvitation(CRUDBase[UserInvitation, InvitationCreate, dict]):
    """CRUD operations for user invitations."""

    async def create_invitation(
        self,
        db: AsyncSession,
        *,
        email: str,
        organization_id: UUID,
        invited_by: UUID,
        token: str,
        invitation_data: Dict[str, Any]
    ) -> UserInvitation:
        """Create a new invitation."""
        invitation = UserInvitation.create_invitation(
            email=email,
            organization_id=organization_id,
            invited_by=invited_by,
            token=token,
            **invitation_data
        )
        
        db.add(invitation)
        await db.commit()
        await db.refresh(invitation)
        
        logger.info(f"Created invitation for {email} to organization {organization_id}")
        return invitation

    async def get_by_token(
        self, 
        db: AsyncSession, 
        token: str
    ) -> Optional[UserInvitation]:
        """Get invitation by token."""
        result = await db.execute(
            select(UserInvitation).where(
                and_(
                    UserInvitation.token == token,
                    UserInvitation.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email_and_org(
        self,
        db: AsyncSession,
        email: str,
        organization_id: UUID,
        status: Optional[InvitationStatus] = None
    ) -> Optional[UserInvitation]:
        """Get invitation by email and organization."""
        query = select(UserInvitation).where(
            and_(
                UserInvitation.email == email,
                UserInvitation.organization_id == organization_id,
                UserInvitation.is_deleted == False
            )
        )
        
        if status:
            query = query.where(UserInvitation.status == status)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_for_email(
        self,
        db: AsyncSession,
        email: str
    ) -> List[UserInvitation]:
        """Get all pending invitations for an email address."""
        result = await db.execute(
            select(UserInvitation).where(
                and_(
                    UserInvitation.email == email,
                    UserInvitation.status == InvitationStatus.PENDING,
                    UserInvitation.expires_at > datetime.utcnow(),
                    UserInvitation.is_deleted == False
                )
            ).order_by(desc(UserInvitation.created_at))
        )
        return result.scalars().all()

    async def get_organization_invitations(
        self,
        db: AsyncSession,
        organization_id: UUID,
        *,
        status: Optional[InvitationStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[UserInvitation]:
        """Get invitations for an organization."""
        query = select(UserInvitation).where(
            and_(
                UserInvitation.organization_id == organization_id,
                UserInvitation.is_deleted == False
            )
        )
        
        if status:
            query = query.where(UserInvitation.status == status)
        
        query = query.order_by(desc(UserInvitation.created_at))
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def count_organization_invitations(
        self,
        db: AsyncSession,
        organization_id: UUID,
        status: Optional[InvitationStatus] = None
    ) -> int:
        """Count invitations for an organization."""
        query = select(func.count(UserInvitation.id)).where(
            and_(
                UserInvitation.organization_id == organization_id,
                UserInvitation.is_deleted == False
            )
        )
        
        if status:
            query = query.where(UserInvitation.status == status)
        
        result = await db.execute(query)
        return result.scalar() or 0

    async def get_invitation_stats(
        self,
        db: AsyncSession,
        organization_id: UUID
    ) -> Dict[str, Any]:
        """Get invitation statistics for an organization."""
        # Get counts by status
        stats_query = select(
            UserInvitation.status,
            func.count(UserInvitation.id).label('count')
        ).where(
            and_(
                UserInvitation.organization_id == organization_id,
                UserInvitation.is_deleted == False
            )
        ).group_by(UserInvitation.status)
        
        result = await db.execute(stats_query)
        status_counts = {row.status: row.count for row in result.all()}
        
        # Calculate totals
        total_sent = sum(status_counts.values())
        accepted = status_counts.get(InvitationStatus.ACCEPTED, 0)
        pending = status_counts.get(InvitationStatus.PENDING, 0)
        expired = status_counts.get(InvitationStatus.EXPIRED, 0)
        cancelled = status_counts.get(InvitationStatus.CANCELLED, 0)
        
        # Calculate acceptance rate
        acceptance_rate = (accepted / total_sent * 100) if total_sent > 0 else 0
        
        # Get recent invitations
        recent = await self.get_organization_invitations(
            db, organization_id, limit=10
        )
        
        return {
            "total_sent": total_sent,
            "pending": pending,
            "accepted": accepted,
            "expired": expired,
            "cancelled": cancelled,
            "acceptance_rate": round(acceptance_rate, 2),
            "recent_invitations": recent
        }

    async def mark_as_accepted(
        self,
        db: AsyncSession,
        invitation_id: UUID,
        accepted_by_user_id: UUID
    ) -> Optional[UserInvitation]:
        """Mark invitation as accepted."""
        invitation = await self.get(db, id=invitation_id)
        if invitation:
            invitation.mark_as_accepted(accepted_by_user_id)
            db.add(invitation)
            await db.commit()
            await db.refresh(invitation)
            
            logger.info(f"Invitation {invitation_id} accepted by user {accepted_by_user_id}")
        
        return invitation

    async def cancel_invitation(
        self,
        db: AsyncSession,
        invitation_id: UUID,
        cancelled_by: UUID
    ) -> Optional[UserInvitation]:
        """Cancel an invitation."""
        invitation = await self.get(db, id=invitation_id)
        if invitation and invitation.status == InvitationStatus.PENDING:
            invitation.status = InvitationStatus.CANCELLED
            db.add(invitation)
            await db.commit()
            await db.refresh(invitation)
            
            logger.info(f"Invitation {invitation_id} cancelled by user {cancelled_by}")
        
        return invitation

    async def expire_old_invitations(
        self,
        db: AsyncSession,
        organization_id: Optional[UUID] = None
    ) -> int:
        """Expire old invitations and return count of expired invitations."""
        query = select(UserInvitation).where(
            and_(
                UserInvitation.status == InvitationStatus.PENDING,
                UserInvitation.expires_at <= datetime.utcnow(),
                UserInvitation.is_deleted == False
            )
        )
        
        if organization_id:
            query = query.where(UserInvitation.organization_id == organization_id)
        
        result = await db.execute(query)
        expired_invitations = result.scalars().all()
        
        count = 0
        for invitation in expired_invitations:
            invitation.mark_as_expired()
            db.add(invitation)
            count += 1
        
        if count > 0:
            await db.commit()
            logger.info(f"Expired {count} old invitations")
        
        return count

    async def check_duplicate_invitation(
        self,
        db: AsyncSession,
        email: str,
        organization_id: UUID
    ) -> Optional[UserInvitation]:
        """Check if there's already a pending invitation for this email/org."""
        return await self.get_by_email_and_org(
            db, email, organization_id, InvitationStatus.PENDING
        )

    async def resend_invitation(
        self,
        db: AsyncSession,
        invitation_id: UUID,
        new_expiry_days: int = 7
    ) -> Optional[UserInvitation]:
        """Resend an invitation by extending its expiry."""
        invitation = await self.get(db, id=invitation_id)
        if invitation and invitation.status in [InvitationStatus.PENDING, InvitationStatus.EXPIRED]:
            invitation.status = InvitationStatus.PENDING
            invitation.expires_at = datetime.utcnow() + timedelta(days=new_expiry_days)
            db.add(invitation)
            await db.commit()
            await db.refresh(invitation)
            
            logger.info(f"Resent invitation {invitation_id} with new expiry")
        
        return invitation

    async def get_user_invitations(
        self,
        db: AsyncSession,
        invited_by: UUID,
        *,
        skip: int = 0,
        limit: int = 20
    ) -> List[UserInvitation]:
        """Get invitations sent by a specific user."""
        result = await db.execute(
            select(UserInvitation).where(
                and_(
                    UserInvitation.invited_by == invited_by,
                    UserInvitation.is_deleted == False
                )
            ).order_by(desc(UserInvitation.created_at))
            .offset(skip).limit(limit)
        )
        return result.scalars().all()


# Create singleton instance
invitation = CRUDInvitation(UserInvitation)