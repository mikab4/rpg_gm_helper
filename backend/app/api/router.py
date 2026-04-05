from fastapi import APIRouter

from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.entities import router as entities_router
from app.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(campaigns_router, tags=["campaigns"])
api_router.include_router(entities_router, tags=["entities"])
api_router.include_router(health_router, tags=["health"])
