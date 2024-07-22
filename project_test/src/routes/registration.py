from fastapi import APIRouter, HTTPException
from src.database.connect import connect_to_database_mongo, get_mongo_url
from src.models.models import UserCreate
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


def is_valid_email(email: str) -> bool:
    """
    Validate email format.

    Args:
    - email (str): Email address to validate.

    Returns:
    - bool: True if the email format is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
    return re.match(pattern, email) is not None


def is_valid_password(password: str) -> bool:
    """
    Validate password format.

    Password must:
    - Be at least 8 characters long.
    - Contain at least one uppercase letter.
    - Contain at least one special character among @$!%*?&.

    Args:
    - password (str): Password to validate.

    Returns:
    - bool: True if the password format is valid, False otherwise.
    """
    pattern = r"^(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return re.match(pattern, password) is not None


@router.post("/registration/")
async def registration(
    user_create: UserCreate,
):
    """
    Endpoint to register a new user.

    Args:
    - user_create (UserCreate): User registration data including username, email, and password.

    Returns:
    - dict: Success message upon successful registration.

    Raises:
    - HTTPException: If email format is invalid, email length exceeds maximum, password format is invalid,
      user already exists, or database connection fails.
    """
    try:
        email = user_create.email.lower()
        name = user_create.username

        if not is_valid_email(email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        if len(email) > 200:
            raise HTTPException(
                status_code=400, detail="Email exceeds maximum length of 200 characters"
            )
        if not is_valid_password(user_create.password):
            raise HTTPException(status_code=400, detail="Invalid password format")

        url = await get_mongo_url()
        database = await connect_to_database_mongo(url)

        if database:
            try:
                existing_user = await database.users_collection.find_one(
                    {"email": email}
                )
                if existing_user:
                    raise HTTPException(
                        status_code=400, detail="User already registered"
                    )

                user_data = {
                    "username": name,
                    "email": email,
                    "password": user_create.password,
                }

                await database.save_user(user_data)

                return {"message": "User successfully registered."}
            finally:
                await database.close()
        else:
            raise HTTPException(
                status_code=500, detail="Failed to connect to the database"
            )

    except HTTPException as e:
        raise e
