from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.source_document import SourceDocument


class SessionNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "session_notes"
    __table_args__ = (
        UniqueConstraint("campaign_id", "session_number", name="uq_session_note_campaign_number"),
        UniqueConstraint("id", "campaign_id", name="uq_session_note_id_campaign"),
        CheckConstraint(
            "session_number IS NOT NULL OR session_label IS NOT NULL",
            name="ck_session_notes_number_or_label",
        ),
        Index("ix_session_notes_campaign_id", "campaign_id"),
    )

    campaign_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_number: Mapped[int | None] = mapped_column(nullable=True)
    session_label: Mapped[str | None] = mapped_column(Text, nullable=True)
    played_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    campaign: Mapped["Campaign"] = relationship(back_populates="session_notes", lazy="select")
    source_documents: Mapped[list["SourceDocument"]] = relationship(
        back_populates="session_note",
        lazy="selectin",
        overlaps="campaign,source_documents",
    )
