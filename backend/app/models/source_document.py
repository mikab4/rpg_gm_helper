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
    from app.models.entity import Entity
    from app.models.extraction import ExtractionJob
    from app.models.relationship import Relationship
    from app.models.session_note import SessionNote


class SourceDocument(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "source_documents"
    __table_args__ = (
        UniqueConstraint("id", "campaign_id", name="uq_source_document_id_campaign"),
        ForeignKeyConstraint(
            ["session_note_id", "campaign_id"],
            ["session_notes.id", "session_notes.campaign_id"],
            ondelete="RESTRICT",
            name="fk_source_documents_session_note_campaign",
        ),
        Index("ix_source_documents_campaign_id", "campaign_id"),
        Index(
            "ix_source_documents_session_note_id_campaign_id",
            "session_note_id",
            "campaign_id",
        ),
    )

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_note_id: Mapped[UUID | None] = mapped_column(
        Uuid(),
        nullable=True,
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    truth_status: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata",
        json_document,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )

    campaign: Mapped["Campaign"] = relationship(
        back_populates="source_documents",
        lazy="select",
        overlaps="session_note,source_documents",
    )
    session_note: Mapped["SessionNote | None"] = relationship(
        back_populates="source_documents",
        lazy="select",
        overlaps="campaign,source_documents",
    )
    extraction_jobs: Mapped[list["ExtractionJob"]] = relationship(
        back_populates="source_document",
        lazy="selectin",
        overlaps="campaign,extraction_jobs",
    )
    entities: Mapped[list["Entity"]] = relationship(
        back_populates="source_document",
        lazy="selectin",
        overlaps="campaign,entities",
    )
    relationships: Mapped[list["Relationship"]] = relationship(
        back_populates="source_document",
        lazy="selectin",
        overlaps="campaign,relationships",
    )
