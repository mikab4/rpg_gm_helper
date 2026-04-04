from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Numeric,
    Text,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, json_document

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.entity import Entity
    from app.models.source_document import SourceDocument


class Relationship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "entity_relationships"
    __table_args__ = (
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_entity_relationships_confidence_between_0_and_1",
        ),
        ForeignKeyConstraint(
            ["source_entity_id", "campaign_id"],
            ["entities.id", "entities.campaign_id"],
            ondelete="CASCADE",
            name="fk_entity_relationships_source_entity_campaign",
        ),
        ForeignKeyConstraint(
            ["target_entity_id", "campaign_id"],
            ["entities.id", "entities.campaign_id"],
            ondelete="CASCADE",
            name="fk_entity_relationships_target_entity_campaign",
        ),
        ForeignKeyConstraint(
            ["source_document_id", "campaign_id"],
            ["source_documents.id", "source_documents.campaign_id"],
            ondelete="RESTRICT",
            name="fk_entity_relationships_source_document_campaign",
        ),
        Index("ix_entity_relationships_campaign_id", "campaign_id"),
        Index(
            "ix_entity_relationships_source_entity_id_campaign_id",
            "source_entity_id",
            "campaign_id",
        ),
        Index(
            "ix_entity_relationships_target_entity_id_campaign_id",
            "target_entity_id",
            "campaign_id",
        ),
        Index(
            "ix_entity_relationships_source_document_id_campaign_id",
            "source_document_id",
            "campaign_id",
        ),
    )

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_entity_id: Mapped[UUID] = mapped_column(
        Uuid(),
        nullable=False,
    )
    target_entity_id: Mapped[UUID] = mapped_column(
        Uuid(),
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
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

    campaign: Mapped["Campaign"] = relationship(back_populates="relationships", lazy="select")
    source_entity: Mapped["Entity"] = relationship(
        back_populates="outgoing_relationships",
        foreign_keys=[source_entity_id],
        lazy="select",
    )
    target_entity: Mapped["Entity"] = relationship(
        back_populates="incoming_relationships",
        foreign_keys=[target_entity_id],
        lazy="select",
    )
    source_document: Mapped["SourceDocument | None"] = relationship(
        back_populates="relationships",
        lazy="select",
        overlaps="campaign,relationships",
    )
