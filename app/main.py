# ------ IMPORTS ------
from fastapi import FastAPI

from fastapi_swagger_ui_theme import setup_swagger_ui_theme

from database import Base, engine
from routes import posts, users

from contextlib import asynccontextmanager

# ------ SETUP ------
# Async Manager.
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # On Startup.
    async with engine.begin() as connection:
        # Create database tables if they don't exist yet.
        await connection.run_sync(Base.metadata.create_all)

    # Hold.                       
    yield

    # On Shutdown.
    await engine.dispose()

app = FastAPI(lifespan = lifespan, docs_url = None)

# Routers
# Connects each router to the main app.
app.include_router(
    # The route we are connecting.
    posts.router, 
    # Sets the URL for this route.
    prefix = "/api/posts",
    # Add a tags for a collapsable section on the docs.
    tags = ["posts"]
)

app.include_router(
    users.router, 
    prefix = "/api/users",
    tags = ["users"]
)

# Dark Mode
setup_swagger_ui_theme(
    app, 
    docs_path = "/docs", 
    title = "Swagger Docs"
)

# // Home Route
@app.get("/")
async def home():
    return {"status": "working"}