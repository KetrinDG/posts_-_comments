from fastapi import APIRouter, Depends, HTTPException
from src.routes.auth import oauth2_scheme
from src.utils.jwt_utils import decode_access_token
from src.database.connect import connect_to_database_mongo, get_mongo_url
from bson import ObjectId
from jose.exceptions import ExpiredSignatureError

router = APIRouter()

@router.get("/username_logs/{user_id}", response_model=dict, tags=["User_information"])
async def get_username_logs(
    user_id: str,
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieves username change logs for a specified user ID.

    Args:
        user_id (str): User ID for which logs are requested.
        token (str, optional): Access token for authentication. Defaults to Depends(oauth2_scheme).

    Returns:
        dict: Dictionary containing username change logs.
    """
    try:
        # Decode and validate the access token
        user_data = decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    # Connect to MongoDB database
    database = await connect_to_database_mongo(await get_mongo_url())

    if not database:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

    # Convert user_id to ObjectId type
    user_id_obj = ObjectId(user_id)

    # Get username change logs for the specified user and sort them by timestamp in descending order
    logs_cursor = database.journal_username_collection.find(
        {"user": user_id_obj, "field": "username"}
    ).sort("timestamp", -1)

    logs = []

    async for log in logs_cursor:
        logs.append(
            {
                "_id": str(log["_id"]),
                "field": log["field"],
                "state_before": log["state_before"],
                "state_after": log["state_after"],
                "timestamp": str(log["timestamp"]),
            }
        )

    return {"data": logs}
