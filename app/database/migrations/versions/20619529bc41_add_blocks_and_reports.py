"""add_blocks_and_reports

Revision ID: 20619529bc41
Revises: 72ac892d7820
Create Date: 2026-03-21 00:10:40.694063
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20619529bc41'
down_revision: Union[str, None] = '72ac892d7820'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── blocks: кто кого заблокировал ───────────────────────────────
    op.create_table(
        'blocks',
        sa.Column('id',         sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('blocker_id', sa.BigInteger(), nullable=False),
        sa.Column('blocked_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(),   server_default=sa.func.now(), nullable=False),
 
        sa.ForeignKeyConstraint(['blocker_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['blocked_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('blocker_id', 'blocked_id', name='uq_block_pair'),
    )
    op.create_index('idx_blocks_blocker', 'blocks', ['blocker_id'])
    op.create_index('idx_blocks_blocked', 'blocks', ['blocked_id'])
 
    # ── reports: жалобы ─────────────────────────────────────────────
    op.create_table(
        'reports',
        sa.Column('id',          sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('reporter_id', sa.BigInteger(), nullable=False),
        sa.Column('target_id',   sa.BigInteger(), nullable=False),
        sa.Column('reason',      sa.String(50),   nullable=False),   # spam|fake|abuse|other
        sa.Column('comment',     sa.Text(),        nullable=True),
        sa.Column('status',      sa.String(20),   server_default='pending', nullable=False),  # pending|reviewed|dismissed
        sa.Column('reviewed_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at',  sa.DateTime(),   server_default=sa.func.now(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(),   nullable=True),
 
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'],   ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_reports_target',   'reports', ['target_id'])
    op.create_index('idx_reports_reporter', 'reports', ['reporter_id'])
    op.create_index('idx_reports_status',   'reports', ['status'])
 
 
def downgrade() -> None:
    op.drop_index('idx_reports_status',   table_name='reports')
    op.drop_index('idx_reports_reporter', table_name='reports')
    op.drop_index('idx_reports_target',   table_name='reports')
    op.drop_table('reports')
 
    op.drop_index('idx_blocks_blocked', table_name='blocks')
    op.drop_index('idx_blocks_blocker', table_name='blocks')
    op.drop_table('blocks')
