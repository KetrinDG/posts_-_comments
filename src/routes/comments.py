from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, date
from bson import ObjectId
import asyncio
import logging

from src.models.models import Comment, CommentCreate, PostInDB, CommentResponse, CommentAnalyticsResponse
from src.database.connect import Database, connect_to_database_mongo, get_mongo_url
from better_profanity import profanity
from fastapi.security import OAuth2PasswordBearer
from src.utils.jwt_utils import decode_access_token
from jose.exceptions import ExpiredSignatureError

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)

async def create_auto_reply(post_id: str, author_id: str, delay: int, content: str):
    """
    Creates an auto-reply comment for a post after a specified delay.

    Args:
        post_id (str): ID of the post to which the auto-reply will be associated.
        author_id (str): ID of the author of the auto-reply comment.
        delay (int): Delay in seconds before sending the auto-reply.
        content (str): Content of the auto-reply comment.
    """
    mongo_url = await get_mongo_url()
    database = await connect_to_database_mongo(mongo_url)
    try:
        logger.info(f"Creating auto-reply for post_id: {post_id} with delay: {delay} seconds")
        await asyncio.sleep(delay)

        auto_reply_comment = {
            "_id": str(ObjectId()),  # Ensure _id is a string
            "post_id": post_id,
            "content": content,
            "author_id": author_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "blocked": False
        }

        result = await database.comments_collection.insert_one(auto_reply_comment)
        logger.info(f"Auto-reply inserted with id: {result.inserted_id}")

    except Exception as e:
        logger.error(f"Error creating auto-reply: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create auto-reply")

async def send_delayed_reply(post_id: str, comment_id: Optional[str], delay: int):
    """
    Sends a delayed reply to a post or comment after a specified delay.

    Args:
        post_id (str): ID of the post to which the auto-reply will be associated.
        comment_id (Optional[str]): ID of the comment to which the auto-reply is related. If None, replies to the post.
        delay (int): Delay in seconds before sending the auto-reply.
    """
    mongo_url = await get_mongo_url()
    database = await connect_to_database_mongo(mongo_url)
    try:
        logger.info(f"Preparing to send delayed reply for post_id: {post_id} after {delay} seconds")
        await asyncio.sleep(delay)

        post_id_obj = ObjectId(post_id)
        post = await database.posts_collection.find_one({"_id": post_id_obj})
        if not post:
            logger.error(f"Post with id {post_id} not found")
            return

        auto_reply_content = f"Auto-reply to your post: {post.get('title', '')}"

        if comment_id:
            comment_id_str = str(comment_id).strip()
            if len(comment_id_str) != 24:
                logger.error(f"Invalid comment_id length: '{comment_id_str}'")
                return

            comment_id_obj = ObjectId(comment_id_str)
            comment = await database.comments_collection.find_one({"_id": comment_id_obj})

            if comment:
                auto_reply_content = f"Auto-reply to comment: {comment.get('content', '')}"
            else:
                logger.error(f"Comment with id {comment_id_str} not found")

        await create_auto_reply(post_id, post["author_id"], delay, auto_reply_content)
        logger.info(f"Auto-reply created successfully for post_id: {post_id}")

    except Exception as e:
        logger.error(f"Error sending delayed reply: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send delayed reply")

async def insert_comment_into_db(
        post_id: str, comment: CommentCreate, author_id: str, database: Database
) -> dict:
    """
    Inserts a new comment into the database.

    Args:
        post_id (str): ID of the post to which the comment is related.
        comment (CommentCreate): Comment data to insert.
        author_id (str): ID of the author of the comment.
        database (Database): Instance of Database connected to MongoDB.

    Returns:
        dict: The inserted comment with its ID.

    Raises:
        HTTPException: If the post is not found or database connection fails.
    """
    comment_obj = {
        "_id": str(ObjectId()),  # Generate a new ObjectId for the comment
        "post_id": post_id,
        "content": comment.content,
        "author_id": author_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "blocked": profanity.contains_profanity(comment.content)
    }
    result = await database.comments_collection.insert_one(comment_obj)
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to insert comment")

    # Convert the _id to string
    comment_obj["_id"] = str(result.inserted_id)

    return comment_obj

@router.post("/posts/{post_id}/comments/", response_model=CommentResponse)
async def create_comment(
        post_id: str,
        comment: CommentCreate,
        token: str = Depends(oauth2_scheme)
):
    """
    Endpoint to create a new comment on a post.

    Args:
        post_id (str): ID of the post to which the comment is related.
        comment (CommentCreate): Comment data to insert.
        token (str): OAuth2 token for authentication.

    Returns:
        CommentResponse: The created comment.

    Raises:
        HTTPException: If the token is expired, post is not found, comment creation fails, or database connection fails.
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

        # Find the post by post_id as an ObjectId
        post_id_obj = ObjectId(post_id)
        post_dict = await database.posts_collection.find_one({"_id": post_id_obj})

        if not post_dict:
            raise HTTPException(status_code=404, detail=f"Post with id {post_id} not found")

        if post_dict.get("blocked", False):
            raise HTTPException(status_code=403, detail="Post is blocked")

        # Insert the comment into the database
        comment_obj = await insert_comment_into_db(post_id, comment, author_id, database)

        # Auto-reply logic
        if post_dict.get("auto_reply_enabled"):
            delay = post_dict.get("auto_reply_delay", 0)
            auto_reply_content = f"Auto-reply to your post: {post_dict.get('title', '')}"
            asyncio.create_task(send_delayed_reply(post_id, comment_obj["_id"], delay))
            logger.info(f"Auto-reply task created for post_id: {post_id}")

        # Return CommentResponse with id as a string
        return CommentResponse(
            id=comment_obj["_id"],  # Ensure id is a string
            post_id=comment_obj["post_id"],
            content=comment_obj["content"],
            author_id=comment_obj["author_id"],
            created_at=comment_obj["created_at"],
            updated_at=comment_obj["updated_at"],
            blocked=comment_obj["blocked"]
        )

    except HTTPException as e:
        logger.error(f"HTTP error: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create comment")


@router.get("/posts/{post_id}/comments/", response_model=List[CommentResponse])
async def get_comments(post_id: str):
    """
    Retrieves all comments for a specified post.

    Args:
        post_id (str): ID of the post for which to retrieve comments.

    Returns:
        List[CommentResponse]: List of comments related to the specified post.

    Raises:
        HTTPException: If the database connection fails, or no comments are found.
    """
    database = None
    client = None
    try:
        mongo_url = await get_mongo_url()
        logger.info(f"Connecting to MongoDB at {mongo_url}")
        database = await connect_to_database_mongo(mongo_url)

        if not database:
            raise HTTPException(status_code=500, detail="Failed to connect to the database")

        client = database.client
        logger.info(f"Looking for comments with post_id: {post_id}")

        comments_cursor = database.comments_collection.find({"post_id": post_id, "blocked": False})
        comments = await comments_cursor.to_list(length=None)

        if not comments:
            raise HTTPException(status_code=404, detail="No comments found for the specified post_id")

        logger.info(f"Retrieved {len(comments)} comments for post {post_id}")

        comments_response = []
        for comment in comments:
            logger.info(f"Processing comment with id: {comment['_id']}")
            comments_response.append(CommentResponse(
                id=str(comment["_id"]),
                post_id=comment["post_id"],
                content=comment["content"],
                author_id=comment["author_id"],
                created_at=comment["created_at"],
                updated_at=comment["updated_at"],
                blocked=comment["blocked"]
            ))

        return comments_response

    except HTTPException as e:
        logger.error(f"HTTP error: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comments")

    finally:
        if client:
            client.close()


@router.get("/api/comments-daily-breakdown", response_model=List[CommentAnalyticsResponse])
async def get_comments_daily_breakdown(
    date_from: date = Query(..., description="Start date in YYYY-MM-DD format"),
    date_to: date = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Endpoint to retrieve daily breakdown of comments within a date range.

    Args:
    - date_from (date): Start date for analytics in YYYY-MM-DD format.
    - date_to (date): End date for analytics in YYYY-MM-DD format.
    """
    database = None
    try:
        mongo_url = await get_mongo_url()
        database = await connect_to_database_mongo(mongo_url)

        if not database:
            raise HTTPException(status_code=500, detail="Failed to connect to the database")

        # Convert date objects to datetime
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        date_to_dt = datetime.combine(date_to, datetime.max.time())

        pipeline = [
            {"$match": {"created_at": {"$gte": date_from_dt, "$lte": date_to_dt}}},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "total_comments": {"$sum": 1},
                    "blocked_comments": {"$sum": {"$cond": ["$blocked", 1, 0]}},
                }
            },
            {"$sort": {"_id": 1}}
        ]

        results = await database.comments_collection.aggregate(pipeline).to_list(length=None)

        analytics_response = [
            CommentAnalyticsResponse(
                date=datetime.strptime(result["_id"], "%Y-%m-%d").date(),
                total_comments=result["total_comments"],
                blocked_comments=result["blocked_comments"]
            )
            for result in results
        ]

        return analytics_response

    except HTTPException as e:
        logger.error(f"HTTPException: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if database and database.client:
            try:
                await database.client.close()
                logger.info("Closed MongoDB client connection")
            except Exception as e:
                logger.error(f"Error closing MongoDB client: {str(e)}")