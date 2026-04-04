from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.entity import Entity
    from app.models.extraction import ExtractionCandidate, ExtractionJob
    from app.models.owner import Owner
    from app.models.relationship import Relationship
    from app.models.session_note import SessionNote
    from app.models.source_document import SourceDocument


class Campaign(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "campaigns"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_campaign_owner_name"),)

    owner_id: Mapped[UUID] = mapped_column(
        Uuid(),
        ForeignKey("owners.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    owner: Mapped["Owner"] = relationship(back_populates="campaigns")
    session_notes: Mapped[list["SessionNote"]] = relationship(back_populates="campaign")
    source_documents: Mapped[list["SourceDocument"]] = relationship(back_populates="campaign")
    extraction_jobs: Mapped[list["ExtractionJob"]] = relationship(back_populates="campaign")
    extraction_candidates: Mapped[list["ExtractionCandidate"]] = relationship(
        back_populates="campaign"
    )
    entities: Mapped[list["Entity"]] = relationship(back_populates="campaign")
    relationships: Mapped[list["Relationship"]] = relationship(back_populates="campaign")
