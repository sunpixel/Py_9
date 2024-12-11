'''Main file for an endpoint'''

# pylint: disable=C0301

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, joinedload

from Main import base_class as base
from Main import data_classes as dc
#from Main import funcs as f

SQLALCHEMY_DATABASE_URL = "sqlite:///./Test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

base.Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()
app = FastAPI()

@app.get("/create_user", response_class=HTMLResponse)
def get_create_user_form():
    '''Function that returns the create user form'''
    return FileResponse("static/create_user.html")

@app.get("/create_post", response_class=HTMLResponse)
def get_create_post_form(user_id: int):
    '''Function that returns the create post form'''
    posts = db.query(dc.Post).options(joinedload(dc.Post.users)).all()
    posts_data = [{"username": post.users.username, "title": post.title, "content": post.content, "user_id": post.user_id, "id": post.id} for post in posts]
    return HTMLResponse(content=create_post_html(user_id, posts_data))

def create_post_html(user_id: int, posts_data: list):
    '''Function that generates the create post HTML with existing posts'''
    with open("static/create_post.html", "r", encoding='UTF-8') as file:    # set encoding for specifi value
        html_content = file.read()
    posts_html = "".join(
        f"<div class='post'><h3>{post['username']}</h3><h4>{post['title']}</h4><p>{post['content']}</p>"
        f"{'<button onclick=\"showEditForm(' + str(post['id']) + ', \'' + post['title'] + '\', \'' + post['content'] + '\')\">Edit</button>' if post['user_id'] == user_id else ''}"
        f"<form id='editForm-{post['id']}' class='edit-form' method='post' action='/edit_post'>"
        f"<input type='hidden' name='post_id' value='{post['id']}'>"
        f"<div class='form-group'><label for='edit-title-{post['id']}'>Title:</label><input type='text' id='edit-title-{post['id']}' name='title' value='{post['title']}' required></div>"
        f"<div class='form-group'><label for='edit-content-{post['id']}'>Content:</label><textarea id='edit-content-{post['id']}' name='content' required>{post['content']}</textarea></div>"
        f"<div class='form-group'><button type='submit'>Save</button></div>"
        f"</form></div>"
        for post in posts_data
    )
    return html_content.replace('<div id="postsContainer"></div>', posts_html)

@app.get("/login", response_class=HTMLResponse)
def get_login_form():
    '''Function that returns the login form'''
    return FileResponse("static/login.html")

@app.post("/login")
def login(
    username_or_email: str = Form(...),
    password: str = Form(...)
):
    '''Function that handles user login'''
    user = db.query(dc.User).filter(
        (dc.User.username == username_or_email) | (dc.User.email == username_or_email)
    ).first()
    if not user or user.password != password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return RedirectResponse(url=f"/create_post?user_id={user.id}", status_code=303)

@app.post("/create_user")
def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    '''Function that creates a user'''
    user = dc.User(username=username, email=email, password=password)
    try:
        db.add(user)
        db.commit()
    except exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return RedirectResponse(url=f"/create_post?user_id={user.id}", status_code=303)

@app.post("/create_post")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    user_id: int = Form(...)
):
    '''Function that creates a post'''
    post = dc.Post(title=title, content=content, user_id=user_id)
    db.add(post)
    db.commit()
    return RedirectResponse(url=f"/create_post?user_id={user_id}", status_code=303)

@app.post("/edit_post")
def edit_post(
    post_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    '''Function that edits a post'''
    post = db.query(dc.Post).filter(dc.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.title = title
    post.content = content
    db.commit()
    return RedirectResponse(url=f"/create_post?user_id={post.user_id}", status_code=303)

@app.get("/users", response_class=HTMLResponse)
def get_users_form():
    '''Function that returns the users form'''
    return FileResponse("static/users.html")

@app.get("/users_get", response_class=JSONResponse)
def get_users():
    '''Function that returns all users'''
    users = db.query(dc.User).all()
    return [{"id": user.id, "username": user.username, "email": user.email, "password": user.password} for user in users]

@app.post("/edit_user")
def edit_user(
    user_id: int = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    '''Function that edits a user'''
    user = db.query(dc.User).filter(dc.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = username
    user.email = email
    user.password = password
    db.commit()
    return RedirectResponse(url="/users", status_code=303)
