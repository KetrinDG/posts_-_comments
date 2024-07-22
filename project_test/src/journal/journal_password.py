from fastapi import APIRouter, HTTPException
from src.database.connect import connect_to_database_mongo, get_mongo_url
from bson import ObjectId

router = APIRouter()

@router.get("/password_logs/{user_id}", response_model=dict, tags=["User_information"])
async def get_password_logs(user_id: str):
    """
    Retrieves password change logs for a specified user ID.

    Args:
        user_id (str): User ID for which logs are requested.

    Returns:
        dict: Dictionary containing password change logs.
    """
    try:
        # Connect to the MongoDB database
        database = await connect_to_database_mongo(await get_mongo_url())

        if not database:
            raise HTTPException(
                status_code=500, detail="Failed to connect to the database"
            )

        user_id_obj = ObjectId(user_id)

        # Get password change logs for the specified user and sort them by timestamp in descending order
        logs_cursor = database.journal_password_collection.find(
            {"user": user_id_obj}
        ).sort("timestamp", -1)

        logs = []
        async for log in logs_cursor:
            logs.append(
                {
                    "_id": str(log["_id"]),
                    "field": log["field"],
                    "state_before": log.get("state_before"),
                    "state_after": log.get("state_after"),
                    "timestamp": str(log["timestamp"]),
                }
            )

        return {"data": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
