# ------ IMPORTS ------
from fastapi import FastAPI

from fastapi_swagger_ui_theme import setup_swagger_ui_theme

from database import Base, engine
from routes import posts, users

# ------ SETUP ------
app = FastAPI(docs_url = None)

# This looks at all the models that inherit from base and 
# creates the tables if they don't exist.
Base.metadata.create_all(bind = engine)

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
def home():
    return {"status": "working"}