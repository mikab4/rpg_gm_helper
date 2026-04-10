from fastapi import APIRouter

from app.enums import HealthStatus
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(status=HealthStatus.OK)
