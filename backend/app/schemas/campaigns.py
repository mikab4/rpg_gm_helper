from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CampaignCreate(BaseModel):
    owner_id: UUID
    name: str
    description: str | None = None


class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
