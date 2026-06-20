# ------ IMPORTS ------
from fastapi import FastAPI, HTTPException, status
from schemas import PostResponse, PostCreate

# ------ TEMP ------
posts: list[dict] = [
    {
        "id": 1,
        "creator": "Corporal Chicken",
        "title": "Avatar: The Last Airbender",
        "content": "The best show I've ever watched, 10/10 redemption arc",
        "rating": 10,
        "date": "2026-06-20"
    },
    {
        "id": 2,
        "creator": "Corporal Chicken",
        "title": "Godzilla x Kong",
        "content": "A movie about titans having a brawl",
        "rating": 8,
        "date": "2026-06-20"
    }
]

# ------ SETUP ------
app = FastAPI()

@app.get("/")
def home():
    return {"status": "working"}

# ------ POSTS ------
# // Get All
@app.get(
    "/api/posts",
    # the response the client will recieve is a list
    # of the postresponse schema we made
    response_model = list[PostResponse]
)
def get_posts():
    return posts

# // Get Specific 
@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND, 
        detail = "post not found"
    )

@app.post(
    "/api/posts",
    response_model = PostResponse,
    status_code = status.HTTP_201_CREATED
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1

    new_post = {
        "id": new_id,
        "creator": post.creator,
        "title": post.title,
        "content": post.content,
        "rating": post.rating,
        "date": "2026-06-20",
    }

    posts.append(new_post)

    return new_post