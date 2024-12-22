from fastapi import FastAPI, Request
import uvicorn
from pydantic import BaseModel
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
"""-----------------------------------------------------------------------------------------------------------------

    The following code is a simple example to make pydantic model."""

class Data(BaseModel):
    name: str

"""-----------------------------------------------------------------------------------------------------------------

    The following code is a simple example to use fastapi to input data to the database."""

app = FastAPI()

@app.get("/")
async def root(name : str):
    insert_values(name)
    return {"message": f"Hello, {name}"}

if __name__ == "__main__":
    uvicorn.run("fast:app", port=8000,reload=True)
