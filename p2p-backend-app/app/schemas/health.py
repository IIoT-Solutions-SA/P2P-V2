"""Health check schemas for API responses."""

from typing import Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    """Health status of a single component."""
    status: Literal["healthy", "unhealthy", "degraded"]
    response_time_ms: int = Field(..., ge=0)
    message: str | None = None
    details: Dict[str, Any] | None = None


class HealthCheckResponse(BaseModel):
    """Complete health check response."""
    status: Literal["healthy", "unhealthy", "degraded"]
    service: str
    timestamp: str
    checks: Dict[str, ComponentHealth | Dict[str, Any]]
    version: str | None = None
    uptime_seconds: int | None = None