from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from src.models.models import Post, PostCreate, PostInDB
from src.database.connect import connect_to_database_mongo, get_mongo_url
from src.utils.jwt_utils import decode_access_token
from jose.exceptions import ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer
from src.routes.comments import send_delayed_reply
import asyncio
from bson import ObjectId
import logging
from better_profanity import profanity

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/posts/", response_model=PostInDB)
async def create_post(
    post: PostCreate,
    token: str = Depends(oauth2_scheme)
):
    """
    Endpoint to create a new post.
    """
    try:
        # Decode the token
        user_data = decode_access_token(token)
        author_id = user_data.get("id")

        # Connect to the database
        mongo_url = await get_mongo_url()
        if not mongo_url:
            raise HTTPException(status_code=500, detail="Failed to get MongoDB URL")

        database = await connect_to_database_mongo(mongo_url)
        if not database:
            raise HTTPException(status_code=500, detail="Failed to connect to MongoDB")

        try:
            # Create a new ObjectId for the post
            post_id = ObjectId()
            is_blocked = profanity.contains_profanity(post.content)
            post_obj = PostInDB(
                id=str(post_id),
                title=post.title,
                content=post.content,
                author_id=str(ObjectId(author_id)),
                auto_reply_enabled=post.auto_reply_enabled,
                auto_reply_delay=post.auto_reply_delay,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                blocked=is_blocked
            )

            # Convert fields back to ObjectId for database insertion
            post_data = post_obj.dict(by_alias=True)
            post_data["_id"] = ObjectId(post_data["_id"])

            # Insert the post into the database
            await database.posts_collection.insert_one(post_data)

            # Handle auto-reply if enabled
            if post.auto_reply_enabled:
                delay = post.auto_reply_delay or 60
                asyncio.create_task(send_delayed_reply(post_obj.id, None, delay))

            return post_obj
        finally:
            if database:
                try:
                    await database.close()
                except Exception as e:
                    logger.error(f"Error closing MongoDB client: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to close MongoDB client")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/posts/{post_id}", response_model=PostInDB)
async def get_post(post_id: str):
    """
    Endpoint to retrieve a specific post by ID if it is not blocked.

    Args:
    - post_id (str): The ID of the post to retrieve.

    Returns:
    - PostInDB: The requested post.

    Raises:
    - HTTPException: If post is not found, blocked, or any error occurs during retrieval.
    """
    try:
        if not ObjectId.is_valid(post_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")

        mongo_url = await get_mongo_url()
        database = await connect_to_database_mongo(mongo_url)

        if not database:
            raise HTTPException(status_code=500, detail="Failed to connect to the database")

        try:
            post = await database.posts_collection.find_one({"_id": ObjectId(post_id), "blocked": False})
            if post is None:
                raise HTTPException(status_code=404, detail="Post not found or is blocked")

            return PostInDB(**{
                **post,
                "_id": str(post["_id"]),
                "author_id": str(post["author_id"])
            }).dict(by_alias=True)
        finally:
            if database:
                try:
                    await database.close()
                except Exception as e:
                    logger.error(f"Error closing MongoDB client: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to close MongoDB client")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/", response_model=list[PostInDB])
async def get_posts():
    """
    Endpoint to retrieve all posts that are not blocked.

    Returns:
    - list[PostInDB]: List of all non-blocked posts.

    Raises:
    - HTTPException: If connection to MongoDB fails or any other unexpected error occurs.
    """
    try:
        mongo_url = await get_mongo_url()
        database = await connect_to_database_mongo(mongo_url)

        if not database:
            raise HTTPException(status_code=500, detail="Failed to connect to the database")

        try:
            posts = await database.posts_collection.find({"blocked": False}).to_list(length=None)
            return [PostInDB(**{
                **post,
                "_id": str(post["_id"]),
                "author_id": str(post["author_id"])
            }).dict(by_alias=True) for post in posts]
        finally:
            if database:
                try:
                    await database.close()
                except Exception as e:
                    logger.error(f"Error closing MongoDB client: {str(e)}")
                    raise HTTPException(status_code=500, detail="Failed to close MongoDB client")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
