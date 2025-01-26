from sqlalchemy import create_engine,text,insert,MetaData,Table,values
from sqlalchemy import Integer,Text,Boolean,Column
from passlib.context import CryptContext

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/sqlalchemy_tuts", echo=False)
conn = engine.connect()
metadata = MetaData()

books = Table("name",metadata,
        Column("username", Text),
        Column("age", Integer),
        Column("age", Integer),
        Column("gender", Boolean),
        Column("name", Text),
        Column("avatar", Text)
)
metadata.create_all(engine)
def insert_values(name):
    ins = books.insert().values([name])
    conn.execute(ins)
    conn.commit()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

password = 'ada'
hashed_password = get_password_hash(password)

insert_values(name = {
        "username": 'ada',
        "email": '123456@gmail.com',
        "age": 18,
        "gender": 1,
        "name": 'ada',
        "password": hashed_password
        }
)