from fastapi import APIRouter, Header, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.utils.jwt_utils import decode_access_token
from src.database.connect import Database, connect_to_database_mongo, get_mongo_url
from bson import ObjectId

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user_by_id(user_id: ObjectId, database: Database):
    """
    Retrieve user data from the database by user ID.

    Args:
    - user_id (ObjectId): The ID of the user to retrieve.
    - database (Database): The database connection.

    Returns:
    - dict: The user data.

    Raises:
    - HTTPException: If the user is not found.
    """
    user = await database.users_collection.find_one({"_id": user_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/user_data/{field}", response_model=dict, tags=["User_information"])
async def get_user_data_by_field(
    field: str, token: str = Depends(oauth2_scheme)
):
    """
    Retrieve a specific field of user data from the database.

    Args:
    - field (str): The field of user data to retrieve.
    - token (str): OAuth2 token for authentication.

    Returns:
    - dict: A dictionary containing the requested field and its value.

    Raises:
    - HTTPException: If token is invalid, user is not found, field is not present, or user is forbidden.
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

        user_id = ObjectId(user_data.get("id"))

        # Get user data by ObjectId
        user = await get_user_by_id(user_id, database)

        # Ensure the user making the request is the same as the user to be updated
        if user_data.get("id") != str(user_id):
            raise HTTPException(status_code=403, detail="Forbidden")

        # If the requested field is not present or is empty, return all user data (excluding password)
        if not field or field.isspace() or field not in user:
            user.pop("password", None)
            return user

        # Get the requested field from user data
        user_field = user.get(field)

        if user_field is None:
            raise HTTPException(status_code=404, detail=f"Field '{field}' not found")

        return {field: user_field}
    except HTTPException as e:
        raise e


@router.get("/user_data/", response_model=dict, tags=["User_information"])
async def get_user_data(
    token: str = Depends(oauth2_scheme)
):
    """
    Retrieve all user data from the database.

    Args:
    - token (str): OAuth2 token for authentication.

    Returns:
    - dict: A dictionary containing all user data (excluding password).

    Raises:
    - HTTPException: If token is invalid, user is not found, or database connection fails.
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

        user_id = ObjectId(user_data.get("id"))

        # Get user data by ObjectId
        user = await get_user_by_id(user_id, database)

        # Ensure the user making the request is the same as the user to be updated
        if user_data.get("id") != str(user_id):
            raise HTTPException(status_code=403, detail="Forbidden")

        # Remove the 'password' field
        user.pop("password", None)

        # Convert ObjectId to string
        user["_id"] = str(user["_id"])

        return user

    except HTTPException as e:
        raise e
