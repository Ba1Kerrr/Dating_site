# database.py — полная замена с параметризованными запросами (без SQL-инъекций)
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, Text
from sqlalchemy.exc import SQLAlchemyError
from funcs.hash import hash_password, verify_password
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv("settings/.env"))
engine = create_engine(os.environ["DATABASE_ROUTE"], echo=False)

try:
    conn = engine.connect()
except Exception:
    print("Connection to database failed.")

metadata = MetaData()

table = Table("profile", metadata,
    Column("id",       Integer, primary_key=True, autoincrement=True),
    Column("username", Text,    unique=True),
    Column("email",    Text,    unique=True),
    Column("password", Text),
    Column("age",      Integer),
    Column("gender",   Text),
    Column("name",     Text),
    Column("location", Text),
    Column("avatar",   Text),
    Column("bio",      Text),
)
metadata.create_all(engine)


# Users

def insert_db(username: str, email: str, hashed_password: str) -> None:
    conn.execute(
        text("INSERT INTO profile (username, email, password) VALUES (:u, :e, :p)"),
        {"u": username, "e": email, "p": hashed_password}
    )
    conn.commit()


def insert_values_dopinfo(username: str, age: int, gender: str, name: str,
                           location: str, avatar: str, bio: str) -> None:
    conn.execute(
        text("""UPDATE profile
                SET age=:age, gender=:gender, name=:name,
                    location=:location, avatar=:avatar, bio=:bio
                WHERE username=:u"""),
        {"u": username, "age": age, "gender": gender, "name": name,
         "location": location, "avatar": avatar, "bio": bio}
    )
    conn.commit()


def check_username(username: str) -> bool:
    result = conn.execute(
        text("SELECT 1 FROM profile WHERE username = :u"),
        {"u": username}
    ).fetchone()
    return result is not None


def check_email(email: str) -> bool:
    result = conn.execute(
        text("SELECT 1 FROM profile WHERE email = :e"),
        {"e": email}
    ).fetchone()
    return result is not None


def info_user(username: str) -> dict | None:
    result = conn.execute(
        text("SELECT username, email, password, avatar, location, gender FROM profile WHERE username = :u"),
        {"u": username}
    ).fetchone()
    if result:
        return dict(zip(["username", "email", "password", "avatar", "location", "gender"], result))
    return None


def info_user_email(email: str) -> dict | None:
    result = conn.execute(
        text("SELECT username, email, password, avatar FROM profile WHERE email = :e"),
        {"e": email}
    ).fetchone()
    if result:
        return dict(zip(["username", "email", "password", "avatar"], result))
    return None


def profile(username: str) -> dict | None:
    result = conn.execute(
        text("""SELECT id, username, email, age, gender, name, avatar, location, bio
                FROM profile WHERE username = :u"""),
        {"u": username}
    ).fetchone()
    if result:
        return dict(zip(["id", "username", "email", "age", "gender", "name", "avatar", "location", "bio"], result))
    return None


def update_password(username: str, new_password: str) -> tuple[bool, str]:
    try:
        result = conn.execute(
            text("UPDATE profile SET password = :p WHERE username = :u"),
            {"p": new_password, "u": username}
        )
        if result.rowcount == 0:
            return False, "User not found"
        conn.commit()
        return True, "Password updated successfully"
    except SQLAlchemyError as e:
        conn.rollback()
        return False, f"Database error: {e}"


def update_password_email(email: str, new_password: str) -> tuple[bool, str]:
    try:
        result = conn.execute(
            text("UPDATE profile SET password = :p WHERE email = :e"),
            {"p": new_password, "e": email}
        )
        if result.rowcount == 0:
            return False, "User not found"
        conn.commit()
        return True, "Password updated successfully"
    except SQLAlchemyError as e:
        conn.rollback()
        return False, f"Database error: {e}"


def detect_username_from_email(email: str) -> str | None:
    result = conn.execute(
        text("SELECT username FROM profile WHERE email = :e"),
        {"e": email}
    ).fetchone()
    return result[0] if result else None


def find_all_users(location: str, gender: str) -> list | None:
    opposite = "female" if gender == "male" else "male"
    result = conn.execute(
        text("""SELECT username, location, gender, avatar, age
                FROM profile WHERE location = :loc AND gender = :g"""),
        {"loc": location, "g": opposite}
    ).fetchall()
    if result:
        return [dict(zip(["username", "location", "gender", "avatar", "age"], row)) for row in result]
    return None


# Chat

def create_messages_table() -> None:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS messages (
            id         SERIAL PRIMARY KEY,
            sender     TEXT NOT NULL REFERENCES profile(username),
            receiver   TEXT NOT NULL REFERENCES profile(username),
            text       TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            is_read    BOOLEAN DEFAULT FALSE
        )
    """))
    conn.commit()


def check_match_exists(user1: str, user2: str) -> bool:
    result = conn.execute(text("""
        SELECT 1 FROM matches m
        JOIN profile p1 ON p1.username = :u1
        JOIN profile p2 ON p2.username = :u2
        WHERE (m.user_id = p1.id AND m.target_id = p2.id)
           OR (m.user_id = p2.id AND m.target_id = p1.id)
        LIMIT 1
    """), {"u1": user1, "u2": user2}).fetchone()
    return result is not None


def save_message(sender: str, receiver: str, text_: str) -> int:
    result = conn.execute(
        text("INSERT INTO messages (sender, receiver, text) VALUES (:s, :r, :t) RETURNING id"),
        {"s": sender, "r": receiver, "t": text_}
    )
    conn.commit()
    return result.fetchone()[0]


def get_messages(user1: str, user2: str, limit: int = 50, offset: int = 0) -> list:
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
    conn.commit()

    return list(reversed(messages))


def get_user_chats(username: str) -> list:
    rows = conn.execute(text("""
        WITH matched_users AS (
            SELECT CASE WHEN p1.username = :u THEN p2.username ELSE p1.username END AS companion
            FROM matches m
            JOIN profile p1 ON p1.id = m.user_id
            JOIN profile p2 ON p2.id = m.target_id
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
        JOIN profile p ON p.username = mu.companion
        LEFT JOIN last_messages lm ON (lm.sender = mu.companion OR lm.receiver = mu.companion)
        LEFT JOIN unread_counts uc ON uc.sender = mu.companion
        ORDER BY lm.created_at DESC NULLS LAST
    """), {"u": username}).fetchall()

    keys = ["companion", "avatar", "last_message", "last_message_at", "unread_count"]
    return [dict(zip(keys, row)) for row in rows]