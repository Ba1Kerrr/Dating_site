"""add_subscriptions_and_profile_views

Revision ID: 72ac892d7820
Revises: 2bc5be39b05b
Create Date: 2026-03-20 23:17:21.964530
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '72ac892d7820'
down_revision: Union[str, None] = '2bc5be39b05b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'subscriptions',
        sa.Column('id',         sa.Integer(),                          nullable=False),
        sa.Column('user_id',    sa.Integer(),                          nullable=False),
        sa.Column('plan',       sa.String(20),  server_default='free', nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True),          nullable=True),
        sa.Column('is_active',  sa.Boolean(),   server_default='true', nullable=False),
        sa.Column('payment_id', sa.String(255),                        nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_sub_user_active', 'subscriptions', ['user_id', 'is_active'])

    op.create_table(
        'profile_views',
        sa.Column('id',        sa.Integer(),                          nullable=False),
        sa.Column('viewer_id', sa.Integer(),                          nullable=False),
        sa.Column('target_id', sa.Integer(),                          nullable=False),
        sa.Column('viewed_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['viewer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_pv_target', 'profile_views', ['target_id'])
    op.create_index('idx_pv_viewer', 'profile_views', ['viewer_id'])

    op.execute(
        "INSERT INTO subscriptions (user_id, plan, is_active) "
        "SELECT id, 'free', TRUE FROM users"
    )


def downgrade() -> None:
    op.drop_index('idx_pv_viewer', table_name='profile_views')
    op.drop_index('idx_pv_target', table_name='profile_views')
    op.drop_table('profile_views')

    op.drop_index('idx_sub_user_active', table_name='subscriptions')
    op.drop_table('subscriptions')