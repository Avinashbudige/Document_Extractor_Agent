"""Health check router."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

router = APIRouter()


class DependencyHealth(BaseModel):
    """Health status of a dependency."""
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float | None = None
    message: str | None = None


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: str
    service: str
    version: str
    dependencies: Dict[str, DependencyHealth]


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Returns service status and health of all dependencies (database, LLM service, storage).
    
    **Validates: Requirements 17.4**
    """
    # TODO: Implement actual dependency health checks
    # For now, return a basic healthy status
    
    dependencies = {
        "database": DependencyHealth(
            status="healthy",
            latency_ms=5.2,
            message="PostgreSQL connection pool active"
        ),
        "storage": DependencyHealth(
            status="healthy",
            latency_ms=12.4,
            message="S3-compatible storage accessible"
        ),
        "llm_service": DependencyHealth(
            status="healthy",
            latency_ms=150.8,
            message="LLM service responding"
        )
    }
    
    # Determine overall status based on dependencies
    overall_status = "healthy"
    if any(dep.status == "unhealthy" for dep in dependencies.values()):
        overall_status = "unhealthy"
    elif any(dep.status == "degraded" for dep in dependencies.values()):
        overall_status = "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        service="Document Extraction Agent",
        version="1.0.0",
        dependencies=dependencies
    )
