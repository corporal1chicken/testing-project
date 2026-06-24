# The "What am I actually doing" document
And here we find out if the chicken actually crosses the road!

### TOOLS
**Python**: The programming language

**FastAPI**: The backend framework being used

**SQLite**: The database being used

**SQLAlchemy**: The ORM* used to talk in Python to the database instead of raw SQL

**Pydantic**: FastAPI data validation for data coming in and going out of the backend

---
### PACKAGAES
**FastAPI, SQLAlchemy**: ^

**Pwdlib (Argon2)**: Used for password hashing. Argon2 is the more modern and more resistant to GPU cracking attacks.

**Pyjwt**: Library recommended to use with FastAPI, simple and focused for JWT tokens.

---
### JARGON
**API (Application Programming Interface)**: The 'waiter' (FastAPI) between the 'kitchen' (database) and the 'customer' (the client, e.g. web, mobile, game)

**Endpoint**: The location where the API recieves API calls for data. It is the specific URL and HTTP method (e.g. GET /api/posts)

***ORM (Object Relational Mapping)**: Instead of writing raw prone-to-error SQL, an ORM (in this case, SQLAlchemy) allows for accessing the database record as though they were regular Python objects. 

**Schemas**: Data blueprints for Pydantic to use

**Models**: A table within the database for holding specific information away from everything else

**Dependency Injection**: A way to tell FastAPI "hey, this function depends on another external tool. Get that tool first before running this". In this case, it'll likely be a database connection

**Session**: A temporary workspace opened to the database for a single request, then is automagically closed

**Authentication**: Answers the question of "Who are you?".

**Authorisation**: Answers the question of "What are you allowed to do?". Once a user is logged in, they can only do certain actions. For example, an admin can delete any posts whereas a user can only delete theirs.

**JWT (Json Web Tokens)**: A token given to the frontend client when the user logs in. THht toekn is needed for protected routes, such as updating user settings.

**Password Hashing**: Scramble the password with a unique salt for every different password (even if the password itself is the same)

---
### ERROR CODES
**200**: (Success) General request was successful

**201**: (Success) A new resource was created

**204**: (Success) No content recieved

**400**: (Error) The client sent data that the server invalidated

**401**: (Error) "I don't know who you are"

**404**: (Error) Content was not found

**422**: (Error) Request could not be processed due to missing or invalid fields

---
### (FIXED) ISSUES
1. PATCH partial update
This was giving a 422 unprocessable entity. THis was due to the PostUpdate schema inheriting from PostBase rather than Pydantic's BaseModel. PostBase required the creator field so PostUpdate required it too, and you almost never wanna update the creator of a post because that's silly. 

2. get_specific_post missing creator object
Forgot to set the response_model to be PostResponse which includes the user object.

---
### NOTES
- There cannot be any trailing commas when testing out in Swagger. Gives a 422 JSON Decode Erroe otherwise.
- It is better to have get_specific_user and get_user_posts seperately rather than together like I was trying to do. Why? Because if a user has 300 posts, server will slow right down if I only need their email.
- When adding new fields to SQLite, it is often better to just delete the old database file and let it create a new one. In real production, you'd use migrations so you don't wipe existing user data.
- Never store raw passwords in the database if it gets stolen, bye bye data and hello lawsuits.
- A .env file is for secret environment variables, basically if you have top secret CIA files we don't want people to see. Include in gitignore, that's cruical.
- Difference between encryption and hashing is that the former is reversable, the latter is not. Argon2 generates a differnt salt for every password, the same password can have differnt hashes.
- For security, don't reveal what went wrong when failing to login. Don't which is incorrect (password or email). Or just lie and say the password is incorrect when its the email.
- Best practise to organise routes, with paramiticised ones at the end.

---
### MISC
- python -c "import secrets; print(secrets.token_hex(32))"
Run this command in the terminal for a super super secret key.

- JSON Web Tokens (JWT) Structure
It has 3 parts. (1) Header: contains the algorithm and type. (2) Payload: contains the data and expiration. (3) Signiture: proves the token wasn't tampered with. Signiture is created with our secret key meaning only our server can create valid tokens.