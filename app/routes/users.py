# ------- IMPORTS -------
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import selectinload, Session

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status
)

import models
from database import get_database

from schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    PostResponse
)

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
# // Create User
@router.post(
    "",
    response_model = UserResponse,
    status_code = status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.User)
        .where(models.User.username == user.username)
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "username already exists"
        )
    
    result = database.execute(
        select(models.User)
        .where(models.User.email == user.email)
    )

    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "email already exists"
        )
    
    new_user = models.User(
        username = user.username,
        email = user.email
    )

    database.add(new_user)
    database.commit()
    database.refresh(new_user)

    return new_user

# // Get All Users
@router.get(
    "",
    response_model = list[UserResponse]
)
def get_all_users(database: Annotated[Session, Depends(get_database)]):
    result = database.execute(select(models.User))
    users = result.scalars().all()

    return users

# // Get Specific User
@router.get(
    "/{user_id}", 
    response_model = UserResponse
)
async def get_specific_user(user_id: int, database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )

    existing_user = result.scalars().first()

    if existing_user:
        return existing_user
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail = "user not found"
    )

# // Get User Posts
@router.get(
    "/{user_id}/posts", 
    response_model = list[PostResponse]
)
def get_user_posts(user_id: int, database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found",
        )

    result = database.execute(
        select(models.Post)
        .options(selectinload(models.Post.creator))
        .where(models.Post.user_id == user_id)
    )

    posts = result.scalars().all()

    return posts

# // Update User
@router.patch(
    "/{user_id}", 
    response_model = UserResponse
)
def update_user(user_id: int, user_update: UserUpdate, database: Annotated[Session, Depends(get_database)],):
    result = database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "user not found",
        )

    if user_update.username is not None and user_update.username != user.username:
        result = database.execute(
            select(models.User)
            .where(models.User.username == user_update.username),
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "username already exists",
            )

    if user_update.email is not None and user_update.email != user.email:
        result = database.execute(
            select(models.User)
            .where(models.User.email == user_update.email),
        )
        existing_email = result.scalars().first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail = "email already registered",
            )
        
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email

    database.commit()
    database.refresh(user)

    return user

# // Delete User
@router.delete(
    "/{user_id}",
    status_code = status.HTTP_204_NO_CONTENT
)
def delete_user(user_id: int, database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.User)
        .where(models.User.id == user_id)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "user not found",
        )

    database.delete(user)
    database.commit()