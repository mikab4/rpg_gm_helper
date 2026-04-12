from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enums import EntityType


class LegacyEntityTypeExample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_id: UUID
    entity_name: str
    campaign_id: UUID
    campaign_name: str


class LegacyEntityTypeIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legacy_type: str
    count: int
    example_entities: list[LegacyEntityTypeExample]


class EntityTypeCompatibilityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_issues: bool
    issue_count: int
    issues: list[LegacyEntityTypeIssue]


class EntityTypeMigrationMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legacy_type: str
    target_type: EntityType


class EntityTypeMigrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mappings: list[EntityTypeMigrationMapping]


class EntityTypeMigrationResultItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    legacy_type: str
    target_type: str
    updated_count: int


class EntityTypeMigrationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    updated_count: int
    updated_types: list[EntityTypeMigrationResultItem]
