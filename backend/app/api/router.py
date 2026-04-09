from fastapi import APIRouter

from app.api.routes.campaigns import router as campaigns_router
from app.api.routes.entities import router as entities_router
from app.api.routes.health import router as health_router
from app.api.routes.owners import router as owners_router
from app.api.routes.relationships import router as relationships_router

api_router = APIRouter()
api_router.include_router(campaigns_router, tags=["campaigns"])
api_router.include_router(entities_router, tags=["entities"])
api_router.include_router(health_router, tags=["health"])
api_router.include_router(owners_router, tags=["owners"])
api_router.include_router(relationships_router, tags=["relationships"])
