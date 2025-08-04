from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db, db_manager
from datetime import datetime
import psutil

router = APIRouter()

async def check_postgres(db: AsyncSession) -> str:
    """Check PostgreSQL database connectivity"""
    try:
        await db.execute(text("SELECT 1"))
        return "healthy"
    except Exception:
        return "unhealthy"

async def check_mongodb() -> str:
    """Check MongoDB database connectivity"""
    try:
        await db_manager.mongo_client.admin.command('ping')
        return "healthy"
    except Exception:
        return "unhealthy"

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check the health status of the API and databases"""
    pg_status = await check_postgres(db)
    mongo_status = await check_mongodb()
    
    overall_status = "healthy" if pg_status == "healthy" and mongo_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime": psutil.boot_time(),
        "checks": {
            "api": "healthy",
            "postgresql": pg_status,
            "mongodb": mongo_status
        }
    }