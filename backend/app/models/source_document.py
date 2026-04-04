from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, json_document

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.entity import Entity
    from app.models.extraction import ExtractionJob
    from app.models.relationship import Relationship
    from app.models.session_note import SessionNote


class SourceDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "source_documents"

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_note_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        ForeignKey("session_notes.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    truth_status: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", json_document, default=dict)

    campaign: Mapped["Campaign"] = relationship(back_populates="source_documents")
    session_note: Mapped["SessionNote | None"] = relationship(back_populates="source_documents")
    extraction_jobs: Mapped[list["ExtractionJob"]] = relationship(back_populates="source_document")
    entities: Mapped[list["Entity"]] = relationship(back_populates="source_document")
    relationships: Mapped[list["Relationship"]] = relationship(back_populates="source_document")
