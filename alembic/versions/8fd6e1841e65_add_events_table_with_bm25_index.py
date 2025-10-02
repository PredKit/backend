"""Add event table with BM25 index

Revision ID: 8fd6e1841e65
Revises:
Create Date: 2025-09-30 23:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8fd6e1841e65"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create event table
    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("platform_id", sa.String(length=255), nullable=False),
        sa.Column("search_text", sa.Text(), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("platform", "platform_id", name="uq_event_platform_id"),
    )

    # Create standard indexes
    op.create_index("ix_event_created_at", "event", ["created_at"])

    # Create ParadeDB BM25 index for full-text search
    op.execute("""
        CREATE INDEX IF NOT EXISTS search_idx ON event
        USING bm25 (id, search_text)
        WITH (key_field='id')
    """)


def downgrade() -> None:
    # Drop BM25 index first
    op.execute("DROP INDEX IF EXISTS search_idx")

    # Drop standard indexes
    op.drop_index("ix_event_created_at", table_name="event")

    # Drop table
    op.drop_table("event")
