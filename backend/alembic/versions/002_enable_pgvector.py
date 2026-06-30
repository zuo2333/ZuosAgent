"""Enable pgvector extension

Revision ID: 002
Revises: 001
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    # This requires superuser privileges and the pgvector extension to be installed
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # Note: Dropping the extension will fail if there are any vector columns
    # We'll handle this in a later migration when tables are dropped
    op.execute("DROP EXTENSION IF EXISTS vector")
