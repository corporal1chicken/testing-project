# ------ IMPORTS ------
from fastapi import FastAPI, HTTPException, status, Request, Depends
from schemas import PostResponse, PostCreate

from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi_swagger_ui_theme import setup_swagger_ui_theme

import models
from database import Base, get_database, engine

from typing import Annotated

# ------ SETUP ------
app = FastAPI(docs_url = None)

# This looks at all the models that inherit from base and 
# creates the tables if they don't exist.
Base.metadata.create_all(bind = engine)

# Dark Mode
setup_swagger_ui_theme(app, docs_path="/docs", title="Swagger Docs")

# // Home Route
# Simple status message
@app.get("/")
def home():
    return {"status": "working"}

# ------ POSTS ------
# // Get All
# @app.get is the HTTP request we are making, in this case, a get
# to retrieve data.
@app.get(
    # The URL for this endpoint.
    "/api/posts",
    # We are telling the client what data to expect back.
    response_model = list[PostResponse]
)
# Dependency Injection: We are telling FastAPI that this function depends on this tool
# which is get_database. Run that first before running this function.
# Annotated[Session] is the python typehint.
def get_all_posts(database: Annotated[Session, Depends(get_database)]):
    # This is SQLAlchemy in play, execute an operation on the active database.
    result = database.execute(select(models.Post))
    # .scalars() tells SQLAlchemy to return the data ase instances of the Post class.
    posts = result.scalars().all()

    return posts

# // Get Specific 
@app.get("/api/posts/{post_id}")
def get_specific_post(post_id: int, database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if post:
        return post
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = "Post not found"
    )

# // Create Post
@app.post(
    "/api/posts",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED
)
def create_post(post: PostCreate, database: Annotated[Session, Depends(get_database)]):
    new_post = models.Post(
        title = post.title,
        content = post.content,
        creator = post.creator,
        rating = post.rating
    )

    database.add(new_post)
    database.commit()
    database.refresh(new_post)

    return new_post