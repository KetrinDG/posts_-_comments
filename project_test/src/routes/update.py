import secrets
from fastapi import APIRouter, Depends, Header, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from src.database.connect import Database, connect_to_database_mongo, get_mongo_url
from src.utils.jwt_utils import decode_access_token
from src.routes.registration import is_valid_password, is_valid_email
from bson import ObjectId
from jose.exceptions import ExpiredSignatureError
import time

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def update_username_in_db(
    user_id: ObjectId, current_name: str, new_name: str, database: Database
) -> dict:
    """
    Update user's username in the database.

    Args:
    - user_id (ObjectId): ID of the user to update.
    - current_name (str): Current username.
    - new_name (str): New username to update.
    - database (Database): Instance of Database connected to MongoDB.

    Returns:
    - dict: Success message upon username update.

    Raises:
    - HTTPException: If user is not found or database connection fails.
    """
    await database.users_collection.update_one(
        {"_id": user_id}, {"$set": {"username": new_name}}
    )
    timestamp = int(time.time())
    document_to_insert = {
        "user": user_id,
        "field": "username",
        "state_before": current_name,
        "state_after": new_name,
        "timestamp": timestamp,
    }
    await database.journal_username_collection.insert_one(document_to_insert)
    return {"message": "Username updated"}

@router.patch("/update_username/", response_model=dict)
async def update_username(
    new_name: str = Body(..., embed=True, description="New username"),
    token: str = Depends(oauth2_scheme),
):
    """
    Endpoint to update user's username.

    Args:
    - new_name (str): New username to update.
    - token (str): OAuth2 token for authentication.

    Returns:
    - dict: Success message upon username update.

    Raises:
    - HTTPException: If token is expired, user is not found, or username update fails.
    """
    try:
        user_data = decode_access_token(token)
        database = await connect_to_database_mongo(await get_mongo_url())
        if not database:
            raise HTTPException(
                status_code=500, detail="Failed to connect to the database"
            )
        user_id = user_data.get("id")
        user_id_obj = ObjectId(user_id)
        user = await database.users_collection.find_one({"_id": user_id_obj})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        current_name = user.get("username")
        if user_data.get("id") != str(user_id_obj):
            raise HTTPException(status_code=403, detail="Forbidden")
        response_message = await update_username_in_db(
            user_id_obj, current_name, new_name, database
        )
        return response_message
    except HTTPException as e:
        raise e

async def update_password_in_db(
    user_id: ObjectId, new_password: str, database: Database
) -> dict:
    """
    Update user's password in the database.

    Args:
    - user_id (ObjectId): ID of the user to update.
    - new_password (str): New password to update.
    - database (Database): Instance of Database connected to MongoDB.

    Returns:
    - dict: Success message upon password update.

    Raises:
    - HTTPException: If user is not found, password format is invalid, or database connection fails.
    """
    if not is_valid_password(new_password):
        raise HTTPException(status_code=400, detail="Invalid password format")
    await database.users_collection.update_one(
        {"_id": user_id}, {"$set": {"password": new_password}}
    )
    timestamp = int(time.time())
    document_to_insert = {
        "user": user_id,
        "field": "password",
        "state_before": "***",
        "state_after": "***",
        "timestamp": timestamp,
    }
    await database.journal_password_collection.insert_one(document_to_insert)
    return {"message": "Password updated"}

@router.patch(
    "/update_password/",
    response_model=dict,
    dependencies=[Depends(oauth2_scheme)],
)
async def update_password(
    new_password: str = Body(..., embed=True, description="New password"),
    token: str = Depends(oauth2_scheme),
):
    """
    Endpoint to update user's password.

    Args:
    - new_password (str): New password to update.
    - token (str): OAuth2 token for authentication.

    Returns:
    - dict: Success message upon password update.

    Raises:
    - HTTPException: If token is expired, user is not found, password update fails, or database connection fails.
    """
    try:
        user_data = decode_access_token(token)
        database = await connect_to_database_mongo(await get_mongo_url())
        if not database:
            raise HTTPException(
                status_code=500, detail="Failed to connect to the database"
            )
        user_id_obj = ObjectId(user_data.get("id"))
        user = await database.users_collection.find_one({"_id": user_id_obj})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        response_message = await update_password_in_db(
            user_id_obj, new_password, database
        )
        return response_message
    except HTTPException as e:
        raise e

async def update_email_in_db(
    user_id: ObjectId, new_email: str, database: Database
) -> dict:
    """
    Update user's email in the database.

    Args:
    - user_id (ObjectId): ID of the user to update.
    - new_email (str): New email to update.
    - database (Database): Instance of Database connected to MongoDB.

    Returns:
    - dict: Success message upon email update.

    Raises:
    - HTTPException: If user is not found, email format is invalid, or database connection fails.
    """
    user = await database.users_collection.find_one({"_id": user_id})
    current_email = user.get("email")
    if not is_valid_email(new_email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    new_email = new_email.lower()
    await database.users_collection.update_one(
        {"_id": user_id}, {"$set": {"email": new_email}}
    )
    timestamp = int(time.time())
    document_to_insert = {
        "user": user_id,
        "field": "email",
        "state_before": current_email,
        "state_after": new_email,
        "timestamp": timestamp,
    }
    await database.journal_email_collection.insert_one(document_to_insert)
    return {"message": "Email updated"}

@router.patch(
    "/update_email/",
    response_model=dict,
    dependencies=[Depends(oauth2_scheme)],
)
async def update_email(
    new_email: str = Body(..., embed=True, description="New email"),
    token: str = Depends(oauth2_scheme),
):
    """
    Endpoint to update user's email.

    Args:
    - new_email (str): New email to update.
    - token (str): OAuth2 token for authentication.

    Returns:
    - dict: Success message upon email update.

    Raises:
    - HTTPException: If token is expired, user is not found, email update fails, or database connection fails.
    """
    try:
        user_data = decode_access_token(token)
        database = await connect_to_database_mongo(await get_mongo_url())
        if not database:
            raise HTTPException(
                status_code=500, detail="Failed to connect to the database"
            )
        user_id_obj = ObjectId(user_data.get("id"))
        user = await database.users_collection.find_one({"_id": user_id_obj})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        response_message = await update_email_in_db(user_id_obj, new_email, database)
        return response_message
    except HTTPException as e:
        raise e


