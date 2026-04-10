"""Add relationship semantics fields and custom relationship types."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260410_0002"
down_revision = "20260404_0001"
branch_labels = None
depends_on = None

UUID = sa.Uuid()
JSONB = postgresql.JSONB(astext_type=sa.Text())


def upgrade() -> None:
    op.create_table(
        "relationship_type_definitions",
        sa.Column("id", UUID, nullable=False),
        sa.Column("campaign_id", UUID, nullable=False),
        sa.Column("key", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("family", sa.Text(), nullable=False),
        sa.Column("reverse_label", sa.Text(), nullable=True),
        sa.Column("is_symmetric", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "allowed_source_types",
            JSONB,
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "allowed_target_types",
            JSONB,
            server_default=sa.text("'[]'::jsonb"),
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
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            """
            (
                is_symmetric = true
                AND reverse_label IS NULL
            )
            OR
            (
                is_symmetric = false
                AND reverse_label IS NOT NULL
                AND btrim(reverse_label) <> ''
            )
            """,
            name="ck_relationship_type_definitions_direction_labels",
        ),
        sa.UniqueConstraint(
            "campaign_id",
            "key",
            name="uq_relationship_type_definitions_campaign_key",
        ),
    )
    op.create_index(
        "ix_relationship_type_definitions_campaign_id",
        "relationship_type_definitions",
        ["campaign_id"],
        unique=False,
    )

    op.add_column(
        "entity_relationships",
        sa.Column(
            "lifecycle_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'current'"),
        ),
    )
    op.add_column(
        "entity_relationships",
        sa.Column(
            "visibility_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'public'"),
        ),
    )
    op.add_column(
        "entity_relationships",
        sa.Column(
            "certainty_status",
            sa.Text(),
            nullable=False,
            server_default=sa.text("'confirmed'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("entity_relationships", "certainty_status")
    op.drop_column("entity_relationships", "visibility_status")
    op.drop_column("entity_relationships", "lifecycle_status")
    op.drop_index(
        "ix_relationship_type_definitions_campaign_id",
        table_name="relationship_type_definitions",
    )
    op.drop_table("relationship_type_definitions")
