'''Main executable file of a program'''

from fastapi import FastAPI
#from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import Main.funcs as f
import Main.base_class as base
import Main.data_classes as dc

SQLALCHEMY_DATABASE_URL = "sqlite:///./Test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

base.Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()
app = FastAPI()

@app.get("/create_user")
def create_user():
    '''Creates a user and a post for him'''
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
    post1 = dc.Post(title='Second post', content='Bye, world!', user_id=user.id)
    db.add_all([post, post1])
    db.commit()

@app.get("/")
def read_root():
    '''Root'''
    return {'cool':'yes'}

@app.get('/post/all')
def get_post_all():
    '''Retrieves all availiable posts'''
    return db.query(dc.Post).all()

@app.get('/post/all/all')
def get_post_all_all():
    '''Retrieves all availiable posts'''
    results = db.query(dc.Post, dc.User).join(dc.User, dc.User.id == dc.Post.user_id).all()
    return [{'post': post.__dict__, 'user': user.__dict__} for post, user in results]

@app.get('/post/all/{user_id}')
def get_post_all_id(user_id: int):
    '''Retrieves all availiable posts for user'''
    result = db.query(dc.Post).where(dc.Post.user_id == user_id).all()
    if result:
        return result
    return {'error': 'No such user'}

@app.get('/user/all')
def get_user_all():
    '''Retrieves data about all users'''
    return db.query(dc.User).all()

@app.get('/user/update/{id}')
def update_user(id: int):
    '''Updates user data'''
    user = db.query(dc.User).where(dc.User.id == id).first()
    if user:
        user.email = f.string_generator() + '@mail.ru'
        db.commit()
        return {'success': 'User data updated'}
    return {'error': 'No such user'}

@app.get('/user/delete/{id}')
def delete_user(id: int):
    '''Deletes user data'''
    user = db.query(dc.User).where(dc.User.id == id).first()
    if user:
        db.delete(user)
        db.delete(db.query(dc.Post).where(dc.Post.user_id == id).all())
        db.commit()
        return {'success': 'User data deleted'}
    return {'error': 'No such user'}

@app.get('/post/delete/{id}')
def delete_post(id: int):
    '''Deletes post data'''
    post = db.query(dc.Post).where(dc.Post.id == id).first()
    if post:
        db.delete(post)
        db.commit()
        return {'success': 'Post data deleted'}
    return {'error': 'No such post'}

@app.get('/post/update/{id}')
def update_post(id: int):
    '''Updates post data'''
    post = db.query(dc.Post).where(dc.Post.id == id).first()
    if post:
        post.content = 'Updated content'
        db.commit()
        return {'success': 'Post data updated'}
    return {'error': 'No such post'}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)
