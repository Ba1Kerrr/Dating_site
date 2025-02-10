from sqlalchemy import create_engine,text,insert,MetaData,Table,values
from sqlalchemy import Integer,Text,Boolean,Column
from passlib.context import CryptContext
from ast import literal_eval
engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/Dating-site", echo=False)
conn = engine.connect()
metadata = MetaData()

books = Table("profile",metadata,
        Column("username", Text,primary_key=True,unique=True),
        Column("email", Text,unique=True),
        Column("password", Text),
        Column("age", Integer),
        Column("gender", Text),
        Column("name", Text),
        Column("location", Text)
)
metadata.create_all(engine)
def insert_db(username, email,hashed_password):
    query = text(f"INSERT INTO profile (username,email,password) VALUES ('{username}','{email}','{hashed_password}')")
    conn.execute(query)
    conn.commit()

def insert_values_dopinfo(username, age, gender, name,hashed_password):
    query = text(f"INSERT INTO profile (username, age, gender, name, password) VALUES ('{username}',{age}, '{gender}', '{name}', '{hashed_password}')")
    conn.execute(query)
    conn.commit()
#this 2 checks for username and email return True if user exists or False if not
def check_username(username):
    find_user = (conn.execute(text(f"SELECT 1 FROM profile WHERE username = '{username}'")).fetchall())
    return bool([x[0] for x in find_user])

def check_email(email):
    find_email = (conn.execute(text(f"SELECT 1 FROM profile WHERE email = '{email}'")).fetchall())
    return bool([x[0] for x in find_email])
def info_user(username):
    query = text("SELECT username, email, password FROM profile WHERE username = :username")
    result = conn.execute(query, {"username": username}).fetchone()
    if result:
        return dict(zip(['username', 'email', 'password'], result))
    else:
        return None
