"""Dashboard API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_session, get_mongo_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.dashboard import (
    DashboardStatistics, QuickStats, TimeRange, ActivityFeedResponse,
    TrendingContentResponse
)
from app.services.dashboard import DashboardService
from app.services.activity_feed import ActivityFeedService
from app.services.trending import TrendingService, TrendingAlgorithm

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


@router.get("/activity", response_model=ActivityFeedResponse)
async def get_activity_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    activity_types: Optional[str] = Query(None, description="Comma-separated list of activity types to filter"),
    hours_back: int = Query(168, ge=1, le=8760, description="Hours back to fetch activities (max 1 year)"),
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get organization activity feed."""
    try:
        # Parse activity types filter
        activity_types_list = None
        if activity_types:
            activity_types_list = [t.strip() for t in activity_types.split(',')]
        
        return await ActivityFeedService.get_activity_feed(
            db=db,
            mongo_db=mongo_db,
            organization_id=current_user.organization_id,
            activity_types=activity_types_list,
            page=page,
            page_size=page_size,
            hours_back=hours_back
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch activity feed: {str(e)}"
        )


@router.get("/activity/user", response_model=ActivityFeedResponse)
async def get_user_activity_feed(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user-specific activity feed."""
    try:
        return await ActivityFeedService.get_user_activity_feed(
            db=db,
            mongo_db=mongo_db,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user activity feed: {str(e)}"
        )


@router.get("/trending", response_model=TrendingContentResponse)
async def get_trending_content(
    content_types: Optional[str] = Query(None, description="Comma-separated list of content types"),
    time_window: TimeRange = Query(TimeRange.WEEK),
    algorithm: TrendingAlgorithm = Query(TrendingAlgorithm.HOT),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get trending content across all types."""
    try:
        # Parse content types filter
        content_types_list = None
        if content_types:
            content_types_list = [t.strip() for t in content_types.split(',')]
        
        return await TrendingService.get_trending_content(
            db=db,
            mongo_db=mongo_db,
            organization_id=current_user.organization_id,
            content_types=content_types_list,
            time_window=time_window,
            algorithm=algorithm,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending content: {str(e)}"
        )


@router.get("/trending/{category}")
async def get_trending_by_category(
    category: str,
    content_type: str = Query("use_case"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_session),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get trending content by category."""
    try:
        return await TrendingService.get_trending_by_category(
            db=db,
            mongo_db=mongo_db,
            organization_id=current_user.organization_id,
            category=category,
            content_type=content_type,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending content by category: {str(e)}"
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
                "dashboard_api": "operational",
                "activity_feed": "operational",
                "trending_service": "operational"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Dashboard service unhealthy: {str(e)}"
        )