# What are Schemas?
# essentially a data bluepirnt for all data leaving and entering
# the backend. define different schemas which can be used for different
# operations such as get, post etc. cruically, define what data the client
# recieves back

# ------ IMPORTS ------
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

# ------ POSTS ------
# // Base
# this is the base model all posts will follow and inherit from
class PostBase(BaseModel):
    title: str = Field(min_length = 1, max_length = 50)
    content: str = Field(min_length = 1)
    creator: str = Field(min_length = 1, max_length = 50)
    rating: int

# // Create
class PostCreate(PostBase):
    pass

# // Response
# inherits from postbase meaning it has its own attributes on top of postbase
class PostResponse(PostBase):
    # essentially, allow it to be able to read the properties of the post
    # passed through
    model_config = ConfigDict(from_attributes = True)

    # add some extra properties
    id: int
    date: str