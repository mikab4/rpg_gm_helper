from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, json_document

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.relationship import Relationship
    from app.models.source_document import SourceDocument


class Entity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint("id", "campaign_id", name="uq_entity_id_campaign"),
        ForeignKeyConstraint(
            ["source_document_id", "campaign_id"],
            ["source_documents.id", "source_documents.campaign_id"],
            ondelete="RESTRICT",
            name="fk_entities_source_document_campaign",
        ),
        Index("ix_entities_campaign_id", "campaign_id"),
        Index("ix_entities_source_document_id_campaign_id", "source_document_id", "campaign_id"),
    )

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        json_document,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    source_document_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        nullable=True,
    )
    provenance_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_data: Mapped[dict[str, object]] = mapped_column(
        json_document,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="entities")
    source_document: Mapped["SourceDocument | None"] = relationship(
        back_populates="entities",
        overlaps="campaign,entities",
    )
    outgoing_relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="source_entity",
        foreign_keys="Relationship.source_entity_id",
    )
    incoming_relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="target_entity",
        foreign_keys="Relationship.target_entity_id",
    )
