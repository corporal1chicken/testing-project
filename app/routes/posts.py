# ------ IMPORTS ------
from fastapi import HTTPException, status, Depends, APIRouter
from schemas import PostResponse, PostCreate, PostUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_database, engine
from auth import CurrentUser

from typing import Annotated

# ------ SETUP ------
router = APIRouter()

# ------ ENDPOINTS ------
# // Get All
# @app.get is the HTTP request we are making, in this case, a get
# to retrieve data.
@router.get(
    # We don't need a URL becuase the app sets that up.
    "",
    # We are telling the client what data to expect back.
    response_model = list[PostResponse]
)
# Dependency Injection: We are telling FastAPI that this function depends on this tool
# which is get_database. Run that first before running this function.
# Annotated[Session] is the python typehint.
async def get_all_posts(database: Annotated[AsyncSession, Depends(get_database)]):
    # This is SQLAlchemy in play, execute an operation on the active database as
    # Python objects, not raw SQL.
    result = await database.execute(select(models.Post))
    # .scalars() tells SQLAlchemy to return the data as instances of the Post class.
    posts = result.scalars().all()

    return posts

# // Get Specific 
@router.get(
    "/{post_id}",
    response_model = PostResponse
)
async def get_specific_post(
    post_id: int, 
    database: Annotated[AsyncSession, Depends(get_database)]
):
    result = await database.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if post:
        return post
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = "post not found"
    )

# // Create Post
@router.post(
    "",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED
)
# current_user: Runs the alias we created in auth which checks for a valid token
async def create_post(
    post: PostCreate, 
    current_user: CurrentUser, 
    database: Annotated[AsyncSession, Depends(get_database)]
):
    new_post = models.Post(
        title = post.title,
        content = post.content,
        rating = post.rating,
        user_id = current_user.id
    )

    database.add(new_post)
    await database.commit()
    await database.refresh(new_post, attribute_names = ["author"])

    return new_post

# // Delete Post
@router.delete(
    "/{post_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
async def delete_post(
    post_id: int, 
    current_user: CurrentUser, 
    database: Annotated[AsyncSession, Depends(get_database)]
):
    result = await database.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "post not found"
        )

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "not authorised to delete this post"
        )
    
    await database.delete(post)
    await database.commit()

# // Partially Update Post
@router.patch(
    "/{post_id}",
    response_model = PostResponse
)
async def update_post_partial(
    post_id: int, 
    post_data: PostUpdate, 
    current_user: CurrentUser,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    result = await database.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "not authorised to update this post"
        )

    update_data = post_data.model_dump(exclude_unset = True)

    for field, value in update_data.items():
        setattr(post, field, value)

    await database.commit()
    await database.refresh(post, attribute_names = ["creator"])
    
    return post

# // Fully Update Post
@router.put(
    "/{post_id}",
    response_model = PostResponse
)
async def update_post_full(
    post_id: int, 
    post_data: PostCreate,
    current_user: CurrentUser,
    database: Annotated[AsyncSession, Depends(get_database)]
):
    result = await database.execute(
        select(models.Post)
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = "Post not found"
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "not authorised to update this post"
        )

    post.title = post_data.title
    post.content = post_data.content
    post.rating = post_data.rating

    await database.commit()
    await database.refresh(post, attribute_names = ["creator"])
    
    return post