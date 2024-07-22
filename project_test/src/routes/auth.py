import secrets
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from src.models.models import TokenResponse, LoginData, User, ResetPasswordRequest
from src.database.connect import connect_to_database_mongo, get_mongo_url
import src.utils.jwt_utils as jwt_utils
from src.routes.update import update_password_in_db
from src.utils.email_utils import generate_valid_password, send_new_password_email
from src.routes.registration import is_valid_password

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login/", response_model=TokenResponse, tags=["Authentication"])
async def login_for_access_token(user_data: LoginData):
    """
    Endpoint to authenticate users and issue access tokens.
    """
    # Normalize user email to lowercase
    normalized_email = user_data.email.lower()

    # Connect to the database and find the user by lowercase email
    database = await connect_to_database_mongo(await get_mongo_url())
    if not database:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to the database",
        )

    user = await database.users_collection.find_one({"email": normalized_email})
    if not user or not is_valid_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка, что все необходимые поля присутствуют в данных из базы данных
    if "_id" not in user or "username" not in user or "email" not in user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Incomplete user data",
        )

    # Create a User object
    user_data = User(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
    )

    # Create a JWT token
    token_data = {
        "sub": user_data.email,
        "username": user_data.username,
        "id": user_data.id,
    }
    token = jwt_utils.create_access_token(token_data)

    # Create a TokenResponse object for the response
    token_response = TokenResponse(
        access_token=token, token_type="bearer", user=user_data
    )

    return token_response


@router.post("/logout/", tags=["Authentication"])
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Endpoint to invalidate and logout a user's access token.
    """
    jwt_utils.invalidate_token(token)
    return {"message": "Logged out successfully"}


@router.post("/forgot_password/", response_model=dict, tags=["Authentication"])
async def forgot_password(request: ResetPasswordRequest):
    """
    Endpoint to initiate the password reset process.
    """
    # Connect to the database
    database = await connect_to_database_mongo(await get_mongo_url())
    if not database:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to the database",
        )

    # Find user by email
    user = await database.users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Generate a unique token and save it in the database
    unique_token = secrets.token_urlsafe(32)

    # Update user record with reset password token
    await database.users_collection.update_one(
        {"email": request.email}, {"$set": {"reset_token": unique_token}}
    )

    # Create URL for password reset
    reset_password_url = f"http://127.0.0.1:8000/get_new_pass/{unique_token}"

    # Send email with password reset URL
    await send_new_password_email(user["username"], request.email, reset_password_url)

    return {"message": f"Email sent with URL to verify: {reset_password_url}"}


@router.get("/get_new_pass/{token}", tags=["Authentication"])
async def get_new_password(token: str):
    """
    Endpoint to reset a user's password using a token.
    """
    # Connect to the database
    database = await connect_to_database_mongo(await get_mongo_url())
    if not database:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to the database",
        )

    # Find user by token
    user = await database.users_collection.find_one({"reset_token": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token or token expired",
        )

    # Generate new password
    new_password = generate_valid_password()

    # Update password in the database
    user_id = user["_id"]
    await update_password_in_db(user_id, new_password, database)

    # Send new password to user's email
    await send_new_password_email(user["username"], user["email"], new_password)

    # Remove reset password token
    await database.users_collection.update_one(
        {"reset_token": token}, {"$unset": {"reset_token": ""}}
    )

    return {"message": "New password sent to email."}
