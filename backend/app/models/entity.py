from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, json_document

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.relationship import Relationship
    from app.models.source_document import SourceDocument


class Entity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "entities"

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", json_document, default=dict)
    source_document_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        ForeignKey("source_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    provenance_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_data: Mapped[dict[str, object]] = mapped_column(json_document, default=dict)

    campaign: Mapped["Campaign"] = relationship(back_populates="entities")
    source_document: Mapped["SourceDocument | None"] = relationship(back_populates="entities")
    outgoing_relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="source_entity",
        foreign_keys="Relationship.source_entity_id",
    )
    incoming_relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="target_entity",
        foreign_keys="Relationship.target_entity_id",
    )
