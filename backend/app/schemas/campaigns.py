from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.types import NonBlankString, OptionalNonBlankString


class CampaignCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner_id: UUID
    name: NonBlankString
    description: OptionalNonBlankString = None


class CampaignUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: OptionalNonBlankString = None
    description: OptionalNonBlankString = None

    @model_validator(mode="after")
    def validate_campaign_update_fields(self) -> "CampaignUpdate":
        no_campaign_name_update = self.name is None
        no_description_update = (
            self.description is None and "description" not in self.model_fields_set
        )

        if no_campaign_name_update and no_description_update:
            raise ValueError("At least one campaign field must be provided.")

        return self


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
