import random
import string
import httpx


def generate_valid_password() -> str:
    """
    Generates a valid password with specific requirements:
    - Contains at least one uppercase letter and one special character.
    - Length is 8 characters.

    Returns:
        str: Generated valid password.
    """
    uppercase_letters = string.ascii_uppercase
    special_characters = "@$!%*?&"

    password = [
        random.choice(uppercase_letters),
        random.choice(special_characters),
        *[
            random.choice(string.ascii_letters + string.digits + special_characters)
            for _ in range(6)
        ],
    ]

    random.shuffle(password)
    return "".join(password)


async def send_new_password_email(username: str, email: str, new_password: str):
    """
    Sends a new password email to the user using the Brevo SMTP API.

    Args:
        username (str): User's username.
        email (str): User's email address.
        new_password (str): The new password for the user.
    """
    api_key = "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"
    url = "https://api.brevo.com/v3/smtp/email"

    message_data = {
        "sender": {"name": "test", "email": "test@test"},
        "to": [{"email": email, "name": username}],
        "subject": "New Password",
        "htmlContent": f"Hi {username},<br><br>"
        f"Your new password is: {new_password}<br>",
    }

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=message_data, headers=headers)
        response.raise_for_status()
