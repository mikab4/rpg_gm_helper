from app.enums import HealthStatus
from app.schemas.health import HealthResponse


def test_health_response_uses_health_status_enum() -> None:
    health_response = HealthResponse(status="ok")

    assert health_response.status is HealthStatus.OK
