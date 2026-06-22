# ------ IMPORTS ------
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from datetime import datetime

# ------ POSTS ------
# // Base
# This is the base model all posts will follow and inherit from.
class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 50)
    content: str = Field(min_length = 1)
    creator: str = Field(min_length = 1, max_length = 50)
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