"""Create memory system tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create short_term_memories table (1:1 with sessions)
    op.create_table(
        'short_term_memories',
        sa.Column('session_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('entities', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('pending_tasks', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id')
    )

    # 2. Create long_term_memories table
    op.create_table(
        'long_term_memories',
        sa.Column('id', postgresql.UUID(as_uuid=False), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('memory_type', sa.String(20), nullable=False),  # fact, preference, event
        # Use vector type from pgvector (1536 dimensions for OpenAI embeddings)
        sa.Column('embedding', sa.Text(), nullable=True),  # Will be altered to vector type below
        sa.Column('importance', sa.Numeric(3, 2), nullable=False, server_default='0.5'),
        sa.Column('decay_factor', sa.Numeric(3, 2), nullable=False, server_default='1.0'),
        sa.Column('access_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('source_session_id', postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    # Alter embedding column to vector type
    op.execute("ALTER TABLE long_term_memories ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)")

    op.create_index('ix_long_term_memories_user_id', 'long_term_memories', ['user_id'])
    op.create_index('ix_long_term_memories_memory_type', 'long_term_memories', ['memory_type'])
    op.create_index('ix_long_term_memories_created_at', 'long_term_memories', ['created_at'])

    # 3. Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('user_id', sa.String(100), nullable=False),
        sa.Column('nickname', sa.String(100), nullable=True),
        sa.Column('language', sa.String(10), nullable=False, server_default='zh-CN'),
        sa.Column('response_style', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{"verbosity": "normal"}'),
        sa.Column('tech_level', sa.String(20), nullable=False, server_default='intermediate'),  # beginner, intermediate, expert
        sa.Column('interests', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('task_distribution', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('active_hours', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('tool_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('knowledge_graph', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{"entities": [], "relations": []}'),
        sa.Column('profile_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('last_inferred_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    op.drop_table('user_profiles')
    op.drop_index('ix_long_term_memories_created_at', table_name='long_term_memories')
    op.drop_index('ix_long_term_memories_memory_type', table_name='long_term_memories')
    op.drop_index('ix_long_term_memories_user_id', table_name='long_term_memories')
    op.drop_table('long_term_memories')
    op.drop_table('short_term_memories')
