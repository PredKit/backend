"""Add pgai vectorizer for semantic search

Revision ID: a1b2c3d4e5f6
Revises: 8fd6e1841e65
Create Date: 2025-10-12 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "8fd6e1841e65"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    Set up pgai vectorizer for automatic embedding generation.

    This migration:
    1. Enables required PostgreSQL extensions (pgvector, ai schema)
    2. Configures OpenAI API key from environment
    3. Creates a vectorizer that automatically generates embeddings for search_text
    4. Creates event_embedding view with embeddings and chunks

    Note: The vectorizer worker must be running to process embeddings.
    You can run it with: pgai vectorizer worker -d <database-url>
    """

    # Enable pgvector extension (required by pgai)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Enable pgai extension (creates ai schema and functions)
    # This assumes pgai is already installed in the database
    # If not, run: pip install pgai && pgai install -d <database-url>
    op.execute("CREATE SCHEMA IF NOT EXISTS ai")

    # Set OpenAI API key for the vectorizer
    # Note: In production, this should be set via postgres configuration or secrets
    # For now, the vectorizer worker will use OPENAI_API_KEY from environment

    # Create the vectorizer for the event table
    # This will:
    # - Automatically generate embeddings for the search_text column
    # - Create an event_embedding view with all columns + embedding + chunk
    # - Keep embeddings in sync as data changes
    # - Uses 512 dimensions (shortened from 1536) for better cost/performance
    op.execute("""
        SELECT ai.create_vectorizer(
            'event'::regclass,
            destination => ai.destination_table(
                target_table => 'event_embedding_store',
                view_name => 'event_embedding'
            ),
            embedding => ai.embedding_openai(
                model => 'text-embedding-3-small',
                dimensions => 512
            ),
            chunking => ai.chunking_recursive_character_text_splitter(
                chunk_size => 800,
                chunk_overlap => 200
            ),
            formatting => ai.formatting_python_template(
                template => 'Platform: $chunk[platform]\\nEvent: $chunk'
            ),
            loading => ai.loading_column('search_text'),
            scheduling => ai.scheduling_none(),
            indexing => ai.indexing_none()
        )
    """)


def downgrade() -> None:
    """Remove pgai vectorizer and related objects"""

    # Drop the vectorizer (this will cascade to destination table and view)
    op.execute("""
        SELECT ai.drop_vectorizer('event'::regclass, drop_all => true)
    """)

    # Note: We don't drop pgvector or ai schema as they might be used by other features
    # If you need to fully clean up, manually run:
    # DROP EXTENSION IF EXISTS vector CASCADE;
    # DROP SCHEMA IF EXISTS ai CASCADE;
