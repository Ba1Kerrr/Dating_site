from sqlalchemy import create_engine,text,insert,MetaData,Table,values
from sqlalchemy import Integer,Text,Boolean,Column
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from hash import hash_password,verify_password
from dotenv import load_dotenv
import os
load_dotenv()
engine = create_engine(f"postgresql+psycopg://postgres:{os.environ['database-route']} ", echo=False)
conn = engine.connect()
metadata = MetaData()

table = Table("profile",metadata,
        Column("username", Text,primary_key=True,unique=True),
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
    query = text(f"INSERT INTO profile (username,email,password) VALUES ('{username}','{email}','{hashed_password}')")
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
    query = text(f"SELECT username,email,age,gender,name,avatar,location,bio FROM profile WHERE username = '{username}'")
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
    query = text(f"SELECT username,location,gender,avatar,age FROM profile WHERE location = '{location}' and gender = '{gender_find}'")
    result = conn.execute(query).fetchall()
    if result:
        keys = ["username", "location", "gender", "avatar","age"]
        return [dict(zip(keys, value)) for value in result]
    else:
        return None