from sqlalchemy import (
    create_engine, text, MetaData, Table, Column, Integer, Text,
    String, Boolean, DateTime, BigInteger, Enum, JSON
)
from sqlalchemy.exc import SQLAlchemyError
from funcs.hash import hash_password, verify_password
from dotenv import find_dotenv, load_dotenv
import os
from datetime import datetime
import enum

load_dotenv(find_dotenv("settings/.env"))
engine = create_engine(
    os.environ["DATABASE_ROUTE"],
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    max_overflow=20,
)

ADMIN_USERNAME = "Ba1kerr"
ADMIN_EMAIL    = os.environ.get("admin_email", "ssfs9943@gmail.com")

metadata = MetaData()

class UserStatus(enum.Enum):
    ACTIVE   = "active"
    INACTIVE = "inactive"
    BANNED   = "banned"
    DELETED  = "deleted"

class UserGroup(enum.Enum):
    USER        = "user"
    MODERATOR   = "moderator"
    ADMIN       = "admin"
    SUPER_ADMIN = "super_admin"

table = Table("users", metadata,
    Column("id",                     BigInteger,  primary_key=True, autoincrement=True),
    Column("username",               Text,        unique=True, nullable=False, index=True),
    Column("email",                  Text,        unique=True, nullable=False, index=True),
    Column("phone",                  String(20),  unique=True, nullable=True),
    Column("password_hash",          Text,        nullable=False),
    Column("auth_key",               String(32),  unique=True, nullable=True),
    Column("password_reset_token",   String(64),  nullable=True),
    Column("password_reset_expires", DateTime,    nullable=True),
    Column("verification_token",     String(64),  nullable=True),
    Column("verification_expires",   DateTime,    nullable=True),
    Column("status",       Enum(UserStatus), default=UserStatus.INACTIVE),
    Column("is_verified",  Boolean,  default=False),
    Column("is_deleted",   Boolean,  default=False),
    Column("deleted_at",   DateTime, nullable=True),
    Column("group_id",     Integer,  nullable=True),
    Column("group_name",   Enum(UserGroup), default=UserGroup.USER),
    Column("permissions",  JSON,     nullable=True),
    Column("name",         Text,     nullable=True),
    Column("age",          Integer,  nullable=True),
    Column("gender",       String(10), nullable=True),
    Column("location",     Text,     nullable=True),
    Column("avatar",       Text,     nullable=True),
    Column("bio",          Text,     nullable=True),
    Column("birth_date",   DateTime, nullable=True),
    Column("parent_id",    BigInteger, nullable=True),
    Column("referral_code",String(32), unique=True, nullable=True),
    Column("sms_notification",   Boolean, default=False),
    Column("push_notification",  Boolean, default=True),
    Column("email_notification", Boolean, default=True),
    Column("last_login_ip",  String(45), nullable=True),
    Column("last_login_at",  DateTime,   nullable=True),
    Column("login_count",    Integer,    default=0),
    Column("created_at",     DateTime,   default=datetime.utcnow, index=True),
    Column("updated_at",     DateTime,   default=datetime.utcnow, onupdate=datetime.utcnow),
    Column("created_by",     BigInteger, nullable=True),
    Column("updated_by",     BigInteger, nullable=True),
    Column("metadata",       JSON,       nullable=True),
)

groups = Table("groups", metadata,
    Column("id",          Integer,    primary_key=True),
    Column("name",        String(50), unique=True),
    Column("permissions", JSON),
    Column("description", Text),
    Column("created_at",  DateTime,   default=datetime.utcnow),
)

tokens = Table("tokens", metadata,
    Column("id",          BigInteger,  primary_key=True),
    Column("user_id",     BigInteger,  nullable=False),
    Column("token",       String(512), unique=True),
    Column("type",        String(20)),
    Column("device_info", JSON),
    Column("ip_address",  String(45)),
    Column("expires_at",  DateTime),
    Column("created_at",  DateTime,   default=datetime.utcnow),
    Column("revoked_at",  DateTime,   nullable=True),
)

metadata.create_all(engine)


# ── Users ─────────────────────────────────────────────────────────────────────

def insert_db(username: str, email: str, hashed_password: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO users (username, email, password_hash) VALUES (:u, :e, :p)"),
            {"u": username, "e": email, "p": hashed_password}
        )


def insert_values_dopinfo(username: str, age: int, gender: str, name: str,
                           location: str, avatar: str, bio: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("""UPDATE users
                    SET age=:age, gender=:gender, name=:name,
                        location=:location, avatar=:avatar, bio=:bio
                    WHERE username=:u"""),
            {"u": username, "age": age, "gender": gender, "name": name,
             "location": location, "avatar": avatar, "bio": bio}
        )


def check_username(username: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM users WHERE username = :u"),
            {"u": username}
        ).fetchone()
    return result is not None


def check_email(email: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM users WHERE email = :e"),
            {"e": email}
        ).fetchone()
    return result is not None


def info_user(username: str) -> dict | None:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT username, email, password_hash, avatar, location, gender FROM users WHERE username = :u"),
            {"u": username}
        ).fetchone()
    if result:
        return dict(zip(["username", "email", "password_hash", "avatar", "location", "gender"], result))
    return None


def info_user_email(email: str) -> dict | None:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT username, email, password_hash, avatar FROM users WHERE email = :e"),
            {"e": email}
        ).fetchone()
    if result:
        return dict(zip(["username", "email", "password_hash", "avatar"], result))
    return None


def profile(username: str) -> dict | None:
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT id, username, email, age, gender, name, avatar, location, bio
                    FROM users WHERE username = :u"""),
            {"u": username}
        ).fetchone()
    if result:
        return dict(zip(["id", "username", "email", "age", "gender", "name", "avatar", "location", "bio"], result))
    return None


def update_password(username: str, new_password: str) -> tuple[bool, str]:
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("UPDATE users SET password_hash = :p WHERE username = :u"),
                {"p": new_password, "u": username}
            )
            if result.rowcount == 0:
                return False, "User not found"
        return True, "Password updated successfully"
    except SQLAlchemyError as e:
        return False, f"Database error: {e}"


def update_password_email(email: str, new_password: str) -> tuple[bool, str]:
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("UPDATE users SET password_hash = :p WHERE email = :e"),
                {"p": new_password, "e": email}
            )
            if result.rowcount == 0:
                return False, "User not found"
        return True, "Password updated successfully"
    except SQLAlchemyError as e:
        return False, f"Database error: {e}"


def detect_username_from_email(email: str) -> str | None:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT username FROM users WHERE email = :e"),
            {"e": email}
        ).fetchone()
    return result[0] if result else None


def find_all_users(location: str, gender: str) -> list | None:
    opposite = "female" if gender == "male" else "male"
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT username, location, gender, avatar, age
                    FROM users WHERE location = :loc AND gender = :g"""),
            {"loc": location, "g": opposite}
        ).fetchall()
    if result:
        return [dict(zip(["username", "location", "gender", "avatar", "age"], row)) for row in result]
    return None


# ── Chat ──────────────────────────────────────────────────────────────────────

def create_messages_table() -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                id         SERIAL PRIMARY KEY,
                sender     TEXT NOT NULL REFERENCES users(username),
                receiver   TEXT NOT NULL REFERENCES users(username),
                text       TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                is_read    BOOLEAN DEFAULT FALSE
            )
        """))


def check_match_exists(user1: str, user2: str) -> bool:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 1 FROM matches m
            JOIN users p1 ON p1.username = :u1
            JOIN users p2 ON p2.username = :u2
            WHERE (m.user_id = p1.id AND m.target_id = p2.id)
               OR (m.user_id = p2.id AND m.target_id = p1.id)
            LIMIT 1
        """), {"u1": user1, "u2": user2}).fetchone()
    return result is not None


def save_message(sender: str, receiver: str, text_: str) -> int:
    with engine.begin() as conn:
        result = conn.execute(
            text("INSERT INTO messages (sender, receiver, text) VALUES (:s, :r, :t) RETURNING id"),
            {"s": sender, "r": receiver, "t": text_}
        )
        return result.fetchone()[0]


def get_messages(user1: str, user2: str, limit: int = 50, offset: int = 0) -> list:
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT id, sender, receiver, text,
                   created_at AT TIME ZONE 'UTC' as created_at, is_read
            FROM messages
            WHERE (sender = :u1 AND receiver = :u2)
               OR (sender = :u2 AND receiver = :u1)
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """), {"u1": user1, "u2": user2, "limit": limit, "offset": offset}).fetchall()

        keys = ["id", "sender", "receiver", "text", "created_at", "is_read"]
        messages = [dict(zip(keys, row)) for row in rows]

        conn.execute(text("""
            UPDATE messages SET is_read = TRUE
            WHERE receiver = :u1 AND sender = :u2 AND is_read = FALSE
        """), {"u1": user1, "u2": user2})

    return list(reversed(messages))


def get_user_chats(username: str) -> list:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            WITH matched_users AS (
                SELECT CASE WHEN p1.username = :u THEN p2.username ELSE p1.username END AS companion
                FROM matches m
                JOIN users p1 ON p1.id = m.user_id
                JOIN users p2 ON p2.id = m.target_id
                WHERE p1.username = :u OR p2.username = :u
            ),
            last_messages AS (
                SELECT DISTINCT ON (LEAST(sender, receiver), GREATEST(sender, receiver))
                    sender, receiver, text, created_at AT TIME ZONE 'UTC' as created_at
                FROM messages
                WHERE sender = :u OR receiver = :u
                ORDER BY LEAST(sender, receiver), GREATEST(sender, receiver), created_at DESC
            ),
            unread_counts AS (
                SELECT sender, COUNT(*) as unread
                FROM messages
                WHERE receiver = :u AND is_read = FALSE
                GROUP BY sender
            )
            SELECT mu.companion, p.avatar, lm.text, lm.created_at,
                   COALESCE(uc.unread, 0) AS unread_count
            FROM matched_users mu
            JOIN users p ON p.username = mu.companion
            LEFT JOIN last_messages lm ON (lm.sender = mu.companion OR lm.receiver = mu.companion)
            LEFT JOIN unread_counts uc ON uc.sender = mu.companion
            ORDER BY lm.created_at DESC NULLS LAST
        """), {"u": username}).fetchall()

    keys = ["companion", "avatar", "last_message", "last_message_at", "unread_count"]
    return [dict(zip(keys, row)) for row in rows]


# ── Admin ─────────────────────────────────────────────────────────────────────

def is_admin(username: str) -> bool:
    return username == ADMIN_USERNAME


def ensure_admin_exists() -> None:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT username FROM users WHERE username = :u OR email = :e"),
                {"u": ADMIN_USERNAME, "e": ADMIN_EMAIL}
            ).fetchone()

        if not result:
            print(f"Admin user {ADMIN_USERNAME} not found in database!")
            print(f"User with email {ADMIN_EMAIL} should be the admin")
        else:
            with engine.begin() as conn:
                conn.execute(
                    text("UPDATE users SET group_name = 'admin' WHERE username = :u"),
                    {"u": result[0]}
                )
            print(f"Admin user {result[0]} verified")
    except Exception as e:
        print(f"ensure_admin_exists error: {e}")


def get_user_role(username: str) -> str:
    if username == ADMIN_USERNAME:
        return "admin"
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT group_name FROM users WHERE username = :u"),
                {"u": username}
            ).fetchone()
        return result[0] if result else "user"
    except Exception:
        return "user"


def get_filtered_users(username: str, limit: int = 50, offset: int = 0) -> list[dict]:
    try:
        with engine.connect() as conn:
            me = conn.execute(
                text("SELECT gender, location FROM users WHERE username = :u"),
                {"u": username}
            ).fetchone()

        params: dict = {"u": username, "limit": limit, "offset": offset}
        filters = ["username != :u", "is_deleted = FALSE"]

        if me:
            my_gender, my_location = me[0], me[1]
            if my_gender:
                opposite = "female" if my_gender.lower() == "male" else "male"
                filters.append("gender = :gender")
                params["gender"] = opposite
            if my_location:
                filters.append("location = :location")
                params["location"] = my_location

        where_clause = " AND ".join(filters)
        with engine.connect() as conn:
            rows = conn.execute(
                text(f"""
                    SELECT username, name, age, gender, location, avatar, bio
                    FROM users
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                params
            ).fetchall()

        keys = ["username", "name", "age", "gender", "location", "avatar", "bio"]
        return [dict(zip(keys, row)) for row in rows]
    except Exception:
        return []