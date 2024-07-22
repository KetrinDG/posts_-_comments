from passlib.context import CryptContext

class Hashing:
    # Initialize CryptContext with bcrypt scheme
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        """
        Verify if a plain text password matches a hashed password.

        Args:
        - plain_password (str): Plain text password to verify.
        - hashed_password (str): Hashed password stored in the database.

        Returns:
        - bool: True if plain_password matches hashed_password, False otherwise.
        """
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password):
        """
        Hash a plain text password using bcrypt.

        Args:
        - password (str): Plain text password to hash.

        Returns:
        - str: Hashed password suitable for storage.
        """
        return cls.pwd_context.hash(password)
