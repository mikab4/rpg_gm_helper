from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin, json_document, utcnow

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.source_document import SourceDocument


class ExtractionJob(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "extraction_jobs"

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_document_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("source_documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    extractor_kind: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="extraction_jobs")
    source_document: Mapped["SourceDocument"] = relationship(back_populates="extraction_jobs")
    candidates: Mapped[list["ExtractionCandidate"]] = relationship(back_populates="extraction_job")


class ExtractionCandidate(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "extraction_candidates"

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    extraction_job_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("extraction_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    candidate_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(json_document, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_data: Mapped[dict[str, object]] = mapped_column(json_document, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    campaign: Mapped["Campaign"] = relationship(back_populates="extraction_candidates")
    extraction_job: Mapped["ExtractionJob"] = relationship(back_populates="candidates")
