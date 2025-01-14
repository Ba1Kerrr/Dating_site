from fastapi import FastAPI, Request
import uvicorn

"""-----------------------------------------------------------------------------------------------------------------

    The following code is a simple example to create/use DataBase and insert data into it."""
from sqlalchemy import create_engine,text,insert,MetaData,Table,values
from sqlalchemy import Integer,Text,Boolean,Column
engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/sqlalchemy_tuts", echo=False)
conn = engine.connect()
metadata = MetaData()

books = Table("name",metadata,
              Column("Name",Text,primary_key=True)
)
metadata.create_all(engine)
def insert_values(name):
    ins = books.insert().values([name])
    conn.execute(ins)
    conn.commit()
