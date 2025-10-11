"""
Health check endpoint
"""

from fastapi import APIRouter

from api.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for load balancer / monitoring
    """
    return HealthResponse(status="healthy", version="0.1.0")
