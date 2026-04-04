"""Initial v1 schema."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260404_0001"
down_revision = None
branch_labels = None
depends_on = None

UUID = sa.Uuid()
JSONB = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "owners",
        sa.Column("id", UUID, nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "campaigns",
        sa.Column("id", UUID, nullable=False),
        sa.Column("owner_id", UUID, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["owners.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "name", name="uq_campaign_owner_name"),
    )
    op.create_table(
        "session_notes",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("session_number", sa.Integer(), nullable=True),
        sa.Column("session_label", sa.Text(), nullable=True),
        sa.Column("played_on", sa.Date(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "session_number IS NOT NULL OR session_label IS NOT NULL",
            name="ck_session_notes_number_or_label",
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "campaign_id", "session_number", name="uq_session_note_campaign_number"
        ),
    )
    op.create_table(
        "source_documents",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("session_note_id", UUID, nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("truth_status", sa.Text(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["session_note_id"], ["session_notes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "extraction_jobs",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("source_document_id", UUID, nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("extractor_kind", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_document_id"], ["source_documents.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "entities",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("source_document_id", UUID, nullable=True),
        sa.Column("provenance_excerpt", sa.Text(), nullable=True),
        sa.Column(
            "provenance_data",
            JSONB,
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_document_id"], ["source_documents.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "extraction_candidates",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("extraction_job_id", UUID, nullable=False),
        sa.Column("candidate_type", sa.Text(), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("provenance_excerpt", sa.Text(), nullable=True),
        sa.Column(
            "provenance_data",
            JSONB,
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["extraction_job_id"], ["extraction_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "entity_relationships",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("source_entity_id", UUID, nullable=False),
        sa.Column("target_entity_id", UUID, nullable=False),
        sa.Column("relationship_type", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Numeric(), nullable=True),
        sa.Column("source_document_id", UUID, nullable=True),
        sa.Column("provenance_excerpt", sa.Text(), nullable=True),
        sa.Column(
            "provenance_data",
            JSONB,
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_document_id"], ["source_documents.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["source_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("entity_relationships")
    op.drop_table("extraction_candidates")
    op.drop_table("entities")
    op.drop_table("extraction_jobs")
    op.drop_table("source_documents")
    op.drop_table("session_notes")
    op.drop_table("campaigns")
    op.drop_table("owners")
