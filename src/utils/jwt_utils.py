from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException

# Use a real random key in a production environment
SECRET_KEY = "1f0285df6466d548d01d925436fa9bc5ff0f7ed3f0ddbb4b8b07712dc02ea87e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

# Set for storing invalidated tokens
invalid_tokens = set()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Creates an access token with the provided data and optional expiration time.

    Args:
        data (dict): Data to be encoded in the token (e.g., user_id, username).
        expires_delta (timedelta, optional): Optional expiration time for the token.

    Returns:
        str: Generated JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodes and validates the access token.

    Args:
        token (str): JWT access token to decode.

    Returns:
        dict: Decoded data from the token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    if token in invalid_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def invalidate_token(token: str):
    """
    Invalidates a token by adding it to the set of invalidated tokens.

    Args:
        token (str): JWT access token to invalidate.
    """
    invalid_tokens.add(token)
