"""add roles and admin

Revision ID: 2bc5be39b05b
Revises: 0f1e5a7d211e
Create Date: 2026-03-04 21:18:05.445425
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import os
import bcrypt
import json


revision: str = '2bc5be39b05b'
down_revision: Union[str, None] = '0f1e5a7d211e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def upgrade() -> None:
    admin_username = os.environ.get("admin_username", "Ba1kerr")
    admin_email    = os.environ.get("admin_email",    "ssfs9943@gmail.com")
    admin_password = os.environ.get("admin_password", "")

    conn = op.get_bind()

    groups = [
        ("user",        "Regular user",                        {"can_like": True, "can_chat": True, "can_report": True}),
        ("moderator",   "Can review reports and ban users",    {"can_like": True, "can_chat": True, "can_ban": True, "can_review_reports": True}),
        ("vip",         "VIP with extended features",          {"can_like": True, "can_chat": True, "can_see_likes": True, "can_boost_profile": True}),
        ("admin",       "Full access",                         {"can_like": True, "can_chat": True, "can_ban": True, "can_manage_users": True, "can_manage_roles": True}),
        ("super_admin", "God mode",                            {"all": True}),
    ]

    for name, description, permissions in groups:
        exists = conn.execute(
            sa.text("SELECT 1 FROM groups WHERE name = :name"),
            {"name": name}
        ).fetchone()
        if not exists:
            conn.execute(
                sa.text(
                    "INSERT INTO groups (name, description, permissions, created_at) "
                    "VALUES (:name, :description, :permissions, :created_at)"
                ),
                {
                    "name":        name,
                    "description": description,
                    "permissions": json.dumps(permissions),
                    "created_at":  datetime.utcnow(),
                }
            )

    admin_group = conn.execute(
        sa.text("SELECT id FROM groups WHERE name = 'admin'")
    ).fetchone()
    admin_group_id = admin_group[0] if admin_group else None

    if admin_password:
        hashed = hash_password(admin_password)
        exists = conn.execute(
            sa.text("SELECT 1 FROM users WHERE username = :u OR email = :e"),
            {"u": admin_username, "e": admin_email}
        ).fetchone()

        if not exists:
            conn.execute(
                sa.text(
                    "INSERT INTO users (username, email, password_hash, group_name, group_id, status, is_verified, created_at) "
                    "VALUES (:username, :email, :password_hash, 'admin', :group_id, 'active', true, :created_at)"
                ),
                {
                    "username":      admin_username,
                    "email":         admin_email,
                    "password_hash": hashed,
                    "group_id":      admin_group_id,
                    "created_at":    datetime.utcnow(),
                }
            )
        else:
            conn.execute(
                sa.text(
                    "UPDATE users SET group_name = 'admin', group_id = :group_id, "
                    "status = 'active', is_verified = true "
                    "WHERE username = :u OR email = :e"
                ),
                {"group_id": admin_group_id, "u": admin_username, "e": admin_email}
            )


def downgrade() -> None:
    conn = op.get_bind()
    admin_username = os.environ.get("admin_username", "Ba1kerr")
    admin_email    = os.environ.get("admin_email",    "ssfs9943@gmail.com")
    conn.execute(
        sa.text("DELETE FROM users WHERE username = :u OR email = :e"),
        {"u": admin_username, "e": admin_email}
    )
    conn.execute(sa.text("DELETE FROM groups"))