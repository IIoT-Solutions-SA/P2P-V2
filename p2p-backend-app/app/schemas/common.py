from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float
    checks: Dict[str, str]

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime
    path: str
    
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Any = None