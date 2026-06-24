# ------- IMPORTS -------
from typing import Annotated
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, Session

from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status
)

import models
from database import get_database

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    create_access_token, 
    verify_access_token, 
    hash_password, 
    verify_password, 
    oauth2_scheme
)

from config import settings

from schemas import (
    UserCreate,
    UserUpdate,
    UserPublic,
    UserPrivate, 
    Token,
    PostResponse
)

# ------- SETUP -------
router = APIRouter()

# ------- ENDPOINTS -------
# // Create User
@router.post(
    "",
    response_model = UserPrivate,
    status_code = status.HTTP_201_CREATED,
)
def create_user(user: UserCreate, database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.User)
        .where(func.lower(models.User.username) == user.username.lower())
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "username already exists"
        )
    
    result = database.execute(
        select(models.User)
        .where(func.lower(models.User.email) == user.email.lower())
    )

    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "email already exists"
        )
    
    new_user = models.User(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_password(user.password)
    )

    database.add(new_user)
    database.commit()
    database.refresh(new_user)

    return new_user

@router.post(
    "/token", 
    response_model = Token
)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], database: Annotated[Session, Depends(get_database)]):
    result = database.execute(
        select(models.User)
        .where(func.lower(models.User.email) == form_data.username.lower(),)
    )

    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "incorrect email or password",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes = settings.access_token_expire_minutes)

    access_token = create_access_token(
        data = {"sub": str(user.id)},
        expires_delta = access_token_expires,
    )

    return Token(access_token = access_token, token_type = "bearer")

# // Get Current User
@router.get(
    "/me", 
    response_model = UserPrivate
)
# Protected route, forces the client to provide a valid token
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], database: Annotated[Session, Depends(get_database)]):
    # Decode and verify the token
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail=  "invalid or expired token",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    result = database.execute(
        select(models.User)
        .where(models.User.id == user_id_int),
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "user not found",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    
    return user

# // Get All Users
@router.get(
    "",
    response_model = list[UserPublic]
)
def get_all_users(database: Annotated[Session, Depends(get_database)]):
    result = database.execute(select(models.User))
    users = result.scalars().all()

    return users

# // Get Specific User
@router.get(
    "/{user_id}", 
    response_model = UserPublic
)
def get_specific_user(user_id: int, database: Annotated[Session, Depends(get_database)]):
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
    response_model = UserPrivate
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

    if user_update.username is not None and user_update.username.lower() != user.username.lower():
        result = database.execute(
            select(models.User)
            .where(func.lower(models.User.username) == user_update.username.lower()),
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "username already exists",
            )

    if user_update.email is not None and user_update.email.lower() != user.email.lower():
        result = database.execute(
            select(models.User)
            .where(func.lower(models.User.email) == user_update.email.lower()),
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
        user.email = user_update.email.lower()

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