# ------ IMPORTS ------
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr
)

from datetime import datetime

# ------ USERS ------
# // Base
class UserBase(BaseModel):
    username: str = Field(min_length = 1, max_length = 50)
    email: EmailStr = Field(max_length = 120)

# // Create
class UserCreate(UserBase):
    # We recive the raw password from the client
    password: str = Field(min_length = 8)

# // Update
class UserUpdate(UserBase):
    username: str | None = Field(default = None, min_length = 1, max_length = 50)
    email: EmailStr | None = Field(default = None, max_length = 120)

# // Public Response
# WHat the public sees about this users.
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes = True)

    id: int
    username: str

# // Private Response
# WHat the user sees about themselves. Inherits from UserPublic.
class UserPrivate(UserPublic):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

# ------ POSTS ------
# // Base
# This is the base model all posts will follow and inherit from.
class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 50)
    content: str = Field(min_length = 1)
    rating: int

# // Create
class PostCreate(PostBase):
    pass

# // Update
# This needs to inherit Pydantic's BaseModel so that the creator field isn't required
class PostUpdate(BaseModel):
    title: str | None = Field(default = None, min_length = 1, max_length = 50)
    content: str | None = Field(default = None, min_length = 1)
    rating: int | None = Field(default = None)

# // Response
# Inherits from PostBase meaning it has its own attributes on top of POstBase.
class PostResponse(PostBase):
    # Essentially, allow it to be able to read the properties of the post
    # passed through. By default, Pydantic expects normal Python dicts, but SQLAlchemy
    # doesn't do that. So this is a switch to say yes it is fine to use dot notation.
    model_config = ConfigDict(from_attributes = True)

    id: int
    date: datetime
    user_id: int
    # The client will also recieve the actual creator's object to. They can do
    # post.creator.username for example
    # CHANGE: This will now only see the Public version of this user which doesn't include
    # the email for privacy.
    creator: UserPublic