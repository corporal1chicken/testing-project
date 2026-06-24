# ------ IMPORTS ------
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# ------ TABLES ------
class User(Base):
    __tablename__ = "users"

    # Same pattern as the posts.
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    username: Mapped[str] = mapped_column(String(50), unique = True, nullable = False)
    email: Mapped[str] = mapped_column(String(120), unique = True, nullable = False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable = False)

    # NOT a database column. Tells SQLAlchemy to look at the posts table and
    # find any row where the user ID is equal to this user's ID and 
    # throw it in a list.
    posts: Mapped[list[Post]] = relationship(
        back_populates = "creator",
        # Tells SQLAlchemy that when a user is deleted, it should delete all their
        # posts too.
        cascade = "all, delete-orphan"
    )

class Post(Base):
    # Same pattern as the user model.
    __tablename__ = "posts"

    # Mapped[int] is a type for IDEs. mapped_column[] are SQL constraints and the actual column.
    # primary_key means SQLite will automatically generate a unique auto incrementing
    # ID. index is for search queries and can run it much faster.
    id: Mapped[int] = mapped_column(Integer, primary_key = True, index = True)
    title: Mapped[str] = mapped_column(String(100), nullable = False)
    content: Mapped[str] = mapped_column(Text, nullable = False)
    rating: Mapped[int] = mapped_column(Integer, nullable = False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        default = lambda: datetime.now(UTC),
    )
    
    user_id: Mapped[int] = mapped_column(
        # Creates a rule inside SQLite that this post must have a valid user ID.
        # Otherwise it will reject it if it doesn't
        ForeignKey("users.id"),
        nullable = False,
        index = True,
    )

    # Eseentially, attach the post's creator's object to this post.
    creator: Mapped[User] = relationship(back_populates = "posts")