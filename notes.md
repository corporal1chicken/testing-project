# The "What am I actually doing" document
And here we find out if the chicken actually crosses the road!

### TOOLS
**Python**: The programming language

**FastAPI**: The backend framework being used

**SQLite**: The database being used

**SQLAlchemy**: The ORM* used to talk in Python to the database instead of raw SQL

**Pydantic**: FastAPI data validation for data coming in and going out of the backend

---
### JARGON
**API (Application Programming Interface)**: The 'waiter' (FastAPI) between the 'kitchen' (database) and the 'customer' (the client, e.g. web, mobile, game)

**Endpoint**: The location where the API recieves API calls for data. It is the specific URL and HTTP method (e.g. GET /api/posts)

***ORM (Object Relational Mapping)**: Instead of writing raw prone-to-error SQL, an ORM (in this case, SQLAlchemy) allows for accessing the database record as though they were regular Python objects. 

**Schemas**: Data blueprints for Pydantic to use

**Models**: A table within the database for holding specific information away from everything else

**Dependency Injection**: A way to tell FastAPI "hey, this function depends on another external tool. Get that tool first before running this". In this case, it'll likely be a database connection

**Session**: A temporary workspace opened to the database for a single request, then is automagically closed

---
### ERROR CODES
**200**: (Success) General request was successful

**201**: (Success) A new resource was created

**204**: (Success) No content recieved

**400**: (Error) The client sent data that the server invalidated

**404**: (Error) Content was not found

**422**: (Error) Request could not be processed due to missing or invalid fields

---
### (FIXED) ISSUES
1. PATCH partial update
This was giving a 422 unprocessable entity. THis was due to the PostUpdate schema inheriting from PostBase rather than Pydantic's BaseModel. PostBase required the creator field so PostUpdate required it too, and you almost never wanna update the creator of a post because that's silly. 

2. get_specific_post missing creator object
Forgot to set the response_model to be PostResponse which includes the user object

---
### NOTES
- There cannot be any trailing commas when testing out in Swagger. Gives a 422 JSON Decode Erroe otherwise.
- It is better to have get_specific_user and get_user_posts seperately rather than together like I was trying to do. Why? Because if a user has 300 posts, server will slow right down if I only need their email.