from fastapi import APIRouter, Depends, HTTPException
from src.routes.update import oauth2_scheme
from src.utils.jwt_utils import decode_access_token
from src.database.connect import connect_to_database_mongo, get_mongo_url
from bson import ObjectId
from jose.exceptions import ExpiredSignatureError
from src.models.models import UserLog

router = APIRouter()

@router.get("/user_logs/{user_id}", response_model=dict, tags=["User_information"])
async def get_user_logs(
    user_id: str,
    token: str = Depends(oauth2_scheme),
):
    """
    Retrieves user logs for a specified user ID.

    Args:
        user_id (str): User ID for which logs are requested.
        token (str, optional): Access token for authentication. Defaults to Depends(oauth2_scheme).

    Returns:
        dict: Dictionary containing user logs.
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
    user_id = ObjectId(user_id)

    logs = []

    # Retrieve username change logs
    username_logs_cursor = database.journal_username_collection.find(
        {"user": user_id, "field": "username"}
    ).sort("timestamp", -1)

    async for log in username_logs_cursor:
        logs.append(
            UserLog(
                _id=str(log["_id"]),
                field=log["field"],
                state_before=log["state_before"],
                state_after=log["state_after"],
                timestamp=str(log["timestamp"]),
            )
        )

    # Retrieve email change logs
    email_logs_cursor = database.journal_email_collection.find(
        {"user": user_id}
    ).sort("timestamp", -1)

    async for log in email_logs_cursor:
        logs.append(
            UserLog(
                _id=str(log["_id"]),
                field=log["field"],
                state_before=log.get("state_before"),
                state_after=log.get("state_after"),
                timestamp=str(log["timestamp"]),
            )
        )

    # Retrieve password change logs
    password_logs_cursor = database.journal_password_collection.find(
        {"user": user_id}
    ).sort("timestamp", -1)

    async for log in password_logs_cursor:
        logs.append(
            UserLog(
                _id=str(log["_id"]),
                field=log["field"],
                state_before=log.get("state_before"),
                state_after=log.get("state_after"),
                timestamp=str(log["timestamp"]),
            )
        )

    # Return logs data
    return {"data": logs}
