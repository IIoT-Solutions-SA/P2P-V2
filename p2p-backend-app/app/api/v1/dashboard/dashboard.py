"""Dashboard API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_session, get_mongo_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.dashboard import (
    DashboardStatistics, QuickStats, TimeRange
)
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatistics)
async def get_dashboard_statistics(
    time_range: TimeRange = Query(TimeRange.MONTH),
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive dashboard statistics."""
    try:
        stats = await DashboardService.get_dashboard_statistics(
            db=db,
            mongo_db=mongo_db,
            organization_id=current_user.organization_id,
            time_range=time_range
        )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch dashboard statistics: {str(e)}"
        )


@router.get("/quick-stats", response_model=QuickStats)
async def get_quick_stats(
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get quick statistics for dashboard header."""
    try:
        stats = await DashboardService.get_quick_stats(
            db=db,
            mongo_db=mongo_db,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch quick statistics: {str(e)}"
        )


@router.get("/health")
async def get_dashboard_health(
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Check dashboard service health."""
    try:
        # Test database connections
        db.exec("SELECT 1")
        await mongo_db.command("ismaster")
        
        return {
            "status": "healthy",
            "services": {
                "postgresql": "connected",
                "mongodb": "connected",
                "dashboard_api": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Dashboard service unhealthy: {str(e)}"
        )