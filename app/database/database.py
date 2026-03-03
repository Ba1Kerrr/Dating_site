from sqlalchemy import create_engine,text,insert,MetaData,Table,values
from sqlalchemy import Integer,Text,Boolean,Column
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from funcs.hash import hash_password,verify_password
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv("settings/.env"))
engine = create_engine(os.environ['DATABASE_ROUTE'], echo=False)
try:
    conn = engine.connect()
except Exception as e:
    print("""Connection to database failed.""")
metadata = MetaData()

table = Table("profile",metadata,
        Column("id",Integer,primary_key=True,autoincrement=True),
        Column("username", Text,unique=True),
        Column("email", Text,unique=True),
        Column("password", Text),
        Column("age", Integer),
        Column("gender", Text),
        Column("name", Text),
        Column("location", Text),
        Column("avatar", Text),
        Column("bio", Text)
)



metadata.create_all(engine)

def insert_db(username, email,hashed_password):
    query = text(f"INSERT INTO profile (id,username,email,password) VALUES (DEFAULT,'{username}','{email}','{hashed_password}')")
    conn.execute(query)
    conn.commit()

def insert_values_dopinfo(username:str,age:int, gender:str, name:str,location:str,avatar:str,bio:str) -> None:
    query = text(f"""UPDATE PROFILE 
SET AGE = {age}, GENDER = '{gender}', NAME = '{name}', LOCATION = '{location}',avatar = '{avatar}',bio = '{bio}'
WHERE username = '{username}';""")
    conn.execute(query)
    conn.commit()
#this 2 checks for username and email return True if user exists or False if not
def check_username(username):
    find_user = (conn.execute(text(f"SELECT 1 FROM profile WHERE username = '{username}'")).fetchall())
    return bool([x[0] for x in find_user])

def check_email(email):
    find_email = (conn.execute(text(f"SELECT 1 FROM profile WHERE email = '{email}'")).fetchall())
    return bool([x[0] for x in find_email])

def info_user(username): #-> {username:username,email:email,password : hashed_password}
    query = text(f"SELECT username, email, password,avatar,location,gender FROM profile WHERE username = '{username}'")
    result = conn.execute(query, {"username": username}).fetchone()
    if result:
        return dict(zip(['username', 'email','password','avatar','location','gender'], result))
    else:
        return None

def info_user_email(email): #-> {username:username,email:email,password : hashed_password}
    query = text(f"SELECT username, email, password,avatar FROM profile WHERE email = '{email}'")
    result = conn.execute(query, {"email": email}).fetchone()
    if result:
        return dict(zip(['username', 'email', 'password','avatar'], result))
    else:
        return None
def profile(username): #-> {username:username,email:email,password : hashed_password}
    query = text(f"SELECT id,username,email,age,gender,name,avatar,location,bio FROM profile WHERE username = '{username}'")
    result = conn.execute(query, {"username": username}).fetchone()
    if result:
        return dict(zip(['username','email','age','gender','name','avatar','location','bio'], result))
    else:
        return None

def update_password(username, new_password):
    try:
        query = text(f"UPDATE profile SET password = '{new_password}' WHERE username = '{username}'")
        result = conn.execute(query)
        affected_rows = result.rowcount
        
        if affected_rows == 0:
            return False, "User not found"
        elif affected_rows >= 1:
            conn.commit()
            return True, "Password updated successfully"
    
    except SQLAlchemyError as e:
        conn.rollback()
        return False, f"Database error: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"An unexpected error occurred: {e}"

def update_password_email(email, new_password):
    try:
        query = text(f"UPDATE profile SET password = '{new_password}' WHERE username = '{email}'")
        result = conn.execute(query)
        affected_rows = result.rowcount
        
        if affected_rows == 0:
            return False, "User not found"
        elif affected_rows >= 1:
            conn.commit()
            return True, "Password updated successfully"
    except SQLAlchemyError as e:
        conn.rollback()
        return False, f"Database error: {e}"
    except Exception as e:
        conn.rollback()
        return False, f"An unexpected error occurred: {e}"

def detect_username_from_email(email):
    query = text(f"SELECT username FROM profile WHERE email = '{email}'")
    result = conn.execute(query).fetchone()
    if result:
        return result[0]
    else:
        return None
    
def find_all_users(location,gender):
    if gender == 'male':
        gender_find = 'female'
    elif gender == 'female':
        gender_find = 'male'    
    query = text(f"SELECT username,location,gender,avatar,age FROM profile WHERE location = '{location}' and gender = '{gender}'")
    result = conn.execute(query).fetchall()
    if result:
        keys = ["username", "location", "gender", "avatar","age"]
        return [dict(zip(keys, value)) for value in result]
    else:
        return None
# Добавь эти функции в конец database.py

def create_messages_table():
    """Создаёт таблицу messages если не существует"""
    query = text("""
        CREATE TABLE IF NOT EXISTS messages (
            id          SERIAL PRIMARY KEY,
            sender      TEXT NOT NULL REFERENCES profile(username),
            receiver    TEXT NOT NULL REFERENCES profile(username),
            text        TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT NOW(),
            is_read     BOOLEAN DEFAULT FALSE
        )
    """)
    conn.execute(query)
    conn.commit()


def check_match_exists(user1: str, user2: str) -> bool:
    """Проверяет что между двумя пользователями есть мэтч"""
    query = text("""
        SELECT 1 FROM matches m
        JOIN profile p1 ON p1.username = :u1
        JOIN profile p2 ON p2.username = :u2
        WHERE (m.user_id = p1.id AND m.target_id = p2.id)
           OR (m.user_id = p2.id AND m.target_id = p1.id)
        LIMIT 1
    """)
    result = conn.execute(query, {"u1": user1, "u2": user2}).fetchone()
    return result is not None


def save_message(sender: str, receiver: str, text: str) -> int:
    """Сохраняет сообщение, возвращает его id"""
    query = text("""
        INSERT INTO messages (sender, receiver, text)
        VALUES (:sender, :receiver, :text)
        RETURNING id
    """)
    result = conn.execute(query, {"sender": sender, "receiver": receiver, "text": text})
    conn.commit()
    return result.fetchone()[0]


def get_messages(user1: str, user2: str, limit: int = 50, offset: int = 0) -> list:
    """Возвращает историю сообщений между двумя пользователями"""
    query = text("""
        SELECT id, sender, receiver, text,
               created_at AT TIME ZONE 'UTC' as created_at,
               is_read
        FROM messages
        WHERE (sender = :u1 AND receiver = :u2)
           OR (sender = :u2 AND receiver = :u1)
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    rows = conn.execute(query, {
        "u1": user1, "u2": user2,
        "limit": limit, "offset": offset
    }).fetchall()

    keys = ["id", "sender", "receiver", "text", "created_at", "is_read"]
    messages = [dict(zip(keys, row)) for row in rows]

    # Отмечаем как прочитанные
    mark_read_query = text("""
        UPDATE messages SET is_read = TRUE
        WHERE receiver = :receiver AND sender = :sender AND is_read = FALSE
    """)
    conn.execute(mark_read_query, {"receiver": user1, "sender": user2})
    conn.commit()

    return list(reversed(messages))  # от старых к новым


def get_user_chats(username: str) -> list:
    """
    Возвращает список чатов пользователя —
    все мэтчи + последнее сообщение + счётчик непрочитанных
    """
    query = text("""
        WITH matched_users AS (
            SELECT
                CASE WHEN p1.username = :username THEN p2.username
                     ELSE p1.username END AS companion
            FROM matches m
            JOIN profile p1 ON p1.id = m.user_id
            JOIN profile p2 ON p2.id = m.target_id
            WHERE p1.username = :username OR p2.username = :username
        ),
        last_messages AS (
            SELECT DISTINCT ON (
                LEAST(sender, receiver),
                GREATEST(sender, receiver)
            )
                sender, receiver, text,
                created_at AT TIME ZONE 'UTC' as created_at
            FROM messages
            WHERE sender = :username OR receiver = :username
            ORDER BY
                LEAST(sender, receiver),
                GREATEST(sender, receiver),
                created_at DESC
        ),
        unread_counts AS (
            SELECT sender, COUNT(*) as unread
            FROM messages
            WHERE receiver = :username AND is_read = FALSE
            GROUP BY sender
        )
        SELECT
            mu.companion,
            p.avatar,
            lm.text        AS last_message,
            lm.created_at  AS last_message_at,
            COALESCE(uc.unread, 0) AS unread_count
        FROM matched_users mu
        JOIN profile p ON p.username = mu.companion
        LEFT JOIN last_messages lm
            ON (lm.sender = mu.companion OR lm.receiver = mu.companion)
        LEFT JOIN unread_counts uc ON uc.sender = mu.companion
        ORDER BY lm.created_at DESC NULLS LAST
    """)
    rows = conn.execute(query, {"username": username}).fetchall()
    keys = ["companion", "avatar", "last_message", "last_message_at", "unread_count"]
    return [dict(zip(keys, row)) for row in rows]