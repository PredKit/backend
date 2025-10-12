"""add_indexes_to_event_embedding_store

Revision ID: 035162834881
Revises: a1b2c3d4e5f6
Create Date: 2025-10-12 17:42:26.395998

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "035162834881"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add indexes to event_embedding_store for efficient semantic search."""
    # Index on id for joining back to source events
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_event_embedding_source_id 
        ON event_embedding_store(id)
    """)

    # HNSW index on embedding vector for fast similarity search
    # Using cosine distance (vector_cosine_ops) to match our search queries
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_event_embedding_vector 
        ON event_embedding_store 
        USING hnsw (embedding vector_cosine_ops)
    """)


def downgrade() -> None:
    """Remove indexes from event_embedding_store."""
    op.execute("DROP INDEX IF EXISTS idx_event_embedding_vector")
    op.execute("DROP INDEX IF EXISTS idx_event_embedding_source_id")
