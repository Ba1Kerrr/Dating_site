from sqlalchemy import create_engine,text,insert,MetaData,Table,values
from sqlalchemy import Integer,Text,Boolean,Column
from passlib.context import CryptContext

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/Dating-site", echo=False)
conn = engine.connect()
metadata = MetaData()

books = Table("profile",metadata,
        Column("username", Text),
        Column("age", Integer),
        Column("gender", Text),
        Column("name", Text),
        Column("password", Text)
)
metadata.create_all(engine)
def insert_values(username, age, gender, name,hashed_password):
    query = text(f"INSERT INTO profile (username, age, gender, name, password) VALUES ('{username}',{age}, '{gender}', '{name}', '{hashed_password}')")
    conn.execute(query)
    conn.commit()