from fastapi import APIRouter, Depends, HTTPException
from src.routes.update import oauth2_scheme
from src.utils.jwt_utils import decode_access_token
from src.database.connect import Database, connect_to_database_mongo, get_mongo_url
from bson import ObjectId

router = APIRouter()

async def delete_user_logs_from_db(user_id: ObjectId, database: Database) -> None:
    """
    Async function to delete user logs from relevant collections.

    Args:
    - user_id (ObjectId): The ObjectId of the user whose logs are to be deleted.
    - database (Database): Connected MongoDB database instance.
    """
    await database.journal_username_collection.delete_many({"user": user_id})
    await database.journal_email_collection.delete_many({"user": user_id})
    await database.journal_password_collection.delete_many({"user": user_id})

async def delete_user_from_db(user_id: ObjectId, database: Database) -> dict:
    """
    Async function to delete a user and associated data from MongoDB.

    Args:
    - user_id (ObjectId): The ObjectId of the user to be deleted.
    - database (Database): Connected MongoDB database instance.

    Returns:
    - dict: Message confirming successful deletion.
    """
    # Delete user logs first
    await delete_user_logs_from_db(user_id, database)

    # Delete user's posts and associated comments
    posts_cursor = database.posts_collection.find({"author_id": str(user_id)}, {"_id": 1})
    async for post in posts_cursor:
        await database.comments_collection.delete_many({"post_id": str(post["_id"])})

    await database.posts_collection.delete_many({"author_id": str(user_id)})

    # Delete the user from the users collection
    result = await database.users_collection.delete_one({"_id": user_id})

    if result.deleted_count == 1:
        return {"message": "User deleted"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete(
    "/delete_account/",
    response_model=dict,
    dependencies=[Depends(oauth2_scheme)],
)
async def delete_account(token: str = Depends(oauth2_scheme)):
    """
    Endpoint to delete the user account and associated data from MongoDB.

    Args:
    - token (str): OAuth2 token for user authentication.
    """
    try:
        # Decode and verify the access token
        user_data = decode_access_token(token)

        # Connect to the MongoDB database
        database = await connect_to_database_mongo(await get_mongo_url())

        if not database:
            raise HTTPException(
                status_code=500, detail="Failed to connect to the database"
            )

        user_id_obj = ObjectId(user_data.get("id"))

        # Call the function to delete user logs and then delete the user
        await delete_user_logs_from_db(user_id_obj, database)
        response_message = await delete_user_from_db(user_id_obj, database)

        return response_message
    except HTTPException as e:
        raise e
