'''Main executable file of a program'''

from fastapi import FastAPI
#from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import funcs as f
import base_class as base
import data_classes as dc

SQLALCHEMY_DATABASE_URL = "sqlite:///./Test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

base.Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

un = f.string_generator()
while not f.check_availiability(un, db):
    un = f.string_generator()
em = un + '@mail.ru'
pw = hash(f.string_generator(15))

user = dc.User(username=un, email=em, password=pw)
db.add(user)
db.commit()

# user_id will be given when posting a post made by user
post = dc.Post(title='First post', content='Hello, world!', user_id=user.id)
db.add(post)
db.commit()


users = db.query(dc.User).all()
posts = db.query(dc.Post).all()

app = FastAPI()

@app.get("/")
def read_root():
    '''Root'''
    return users, posts

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
