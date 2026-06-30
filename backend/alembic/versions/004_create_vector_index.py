"""Create vector index for long_term_memories

Revision ID: 004
Revises: 003
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Vector dimension for bge-large-zh-v1.5 (local) or text-embedding-3-small (OpenAI)
# bge-large-zh: 1024 dimensions
# text-embedding-3-small: 1536 dimensions
# We use 1536 as default (OpenAI), but can be configured based on embedding service
VECTOR_DIMENSION = 1536


def upgrade() -> None:
    # Create HNSW index for vector similarity search
    # HNSW parameters:
    # - m: number of bi-directional links created for each new element (default 16)
    # - ef_construction: size of the dynamic candidate list for construction (default 64)
    #
    # Note: This index is created for 1536-dimensional vectors (OpenAI text-embedding-3-small)
    # If using local bge-large-zh-v1.5 (1024 dimensions), the index will need to be recreated
    #
    # For PostgreSQL, we need to use the vector_cosine_ops or vector_l2_ops operator class
    # cosine distance is typically better for semantic similarity
    op.execute(f"""
        CREATE INDEX IF NOT EXISTS ix_long_term_memories_embedding
        ON long_term_memories
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_long_term_memories_embedding")
