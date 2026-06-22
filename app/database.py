# ------ IMPORTS ------
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ------ SETUP ------
# This tells SQLAlchemy to use SQLite database driver and create a file
# if it doesn't already exist.
SQLALCHEMY_DATABASE_URL = "sqlite:///./application.db"

# This creates the actual engine to talk to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # By default, SQLite only allows 1 thread to communicate with it at a time.
    # Because FastAPI is async, we tell SQLite that FastAPI will handle thread
    # safety and to allow it to talk to it via different threads.
    connect_args = {"check_same_thread": False},
)

# This is a factory class that creates database sessions whgen we need it.
# Sessions are a transaction with a database, each request has its own session.
SessionLocal = sessionmaker(
    # Tells SQLAlchemy not to save data to the database automagically so we
    # always have control on when data is written.
    autocommit = False, 
    autoflush = False, 
    # Connects this session factory to the database.
    bind = engine
)

# ------ CLASSES ------
# Parent class for all database tables. Classes that inherit this are essentially
# alligned with SQLAlchemy so it knows how to map python objects to SQL.
class Base(DeclarativeBase):
    pass

# ------ FUNCTIONS ------
# THis gets a temporary session and returns it.
def get_database():
    # Gets a token, when called it opens a temporary area (db) that executes the code
    # the it is returned here and closed.
    with SessionLocal() as db:
        yield db