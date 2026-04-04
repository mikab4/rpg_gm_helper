from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, json_document

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.entity import Entity
    from app.models.source_document import SourceDocument


class Relationship(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "entity_relationships"

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_entity_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_entity_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        ForeignKey("source_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    provenance_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_data: Mapped[dict[str, object]] = mapped_column(json_document, default=dict)

    campaign: Mapped["Campaign"] = relationship(back_populates="relationships")
    source_entity: Mapped["Entity"] = relationship(
        back_populates="outgoing_relationships",
        foreign_keys=[source_entity_id],
    )
    target_entity: Mapped["Entity"] = relationship(
        back_populates="incoming_relationships",
        foreign_keys=[target_entity_id],
    )
    source_document: Mapped["SourceDocument | None"] = relationship(back_populates="relationships")
