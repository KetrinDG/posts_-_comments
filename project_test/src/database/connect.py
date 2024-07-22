import aiofiles
import asyncio
import configparser
import logging
import pathlib
from typing import Union
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo.results import InsertOneResult

# Set up logging configuration
logging.basicConfig(level=logging.INFO)


class Database:
    """
    Represents a MongoDB database connection using AsyncIO with motor.

    Attributes:
        client (AsyncIOMotorClient): AsyncIO MongoDB client.
        db (AsyncIOMotorDatabase): MongoDB database instance.
        users_collection (AsyncIOMotorCollection): Collection for user data.
        posts_collection (AsyncIOMotorCollection): Collection for posts data.
        comments_collection (AsyncIOMotorCollection): Collection for comments data.
        journal_username_collection (AsyncIOMotorCollection): Collection for journal username data.
        journal_email_collection (AsyncIOMotorCollection): Collection for journal email data.
        journal_password_collection (AsyncIOMotorCollection): Collection for journal password data.
        user_notifications_collection (AsyncIOMotorCollection): Collection for user notifications data.
    """

    def __init__(self, url: str):
        """
        Initializes the Database instance.

        Args:
            url (str): MongoDB connection URL.
        """
        self.client: AsyncIOMotorClient = AsyncIOMotorClient(url)
        self.db: AsyncIOMotorDatabase = self.client["TestDemoDataBase"]
        self.users_collection: AsyncIOMotorCollection = self.db["users"]
        self.posts_collection: AsyncIOMotorCollection = self.db["posts"]
        self.comments_collection: AsyncIOMotorCollection = self.db["comments"]
        self.journal_username_collection: AsyncIOMotorCollection = self.db["journal_username"]
        self.journal_email_collection: AsyncIOMotorCollection = self.db["journal_email"]
        self.journal_password_collection: AsyncIOMotorCollection = self.db["journal_password"]
        self.user_notifications_collection: AsyncIOMotorCollection = self.db["user_notifications"]

    async def __aenter__(self):
        """
        Asynchronous context manager entry. Returns self.
        """
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Asynchronous context manager exit. Closes the MongoDB client.
        """
        await self.close()

    async def close(self):
        """
        Closes the MongoDB client connection.
        """
        try:
            if self.client:
                logging.info("Closing the client...")
                await self.client.close()
                logging.info("Client closed.")
            else:
                logging.warning("No client to close.")
        except Exception as e:
            logging.error("Error while closing the connection: %s", e)

    async def save_user(self, user_data: dict) -> Union[bool, str]:
        """
        Saves user data to the MongoDB 'users' collection.

        Args:
            user_data (dict): Data of the user to be saved.

        Returns:
            Union[bool, str]: Inserted ID if successful, False if failed.
        """
        try:
            insert_result: InsertOneResult = await self.users_collection.insert_one(
                user_data
            )
            return insert_result.inserted_id
        except Exception as e:
            logging.error("Error while saving user data: %s", e)
            return False


async def connect_to_database_mongo(url: str) -> Union[None, Database]:
    """
    Connects to MongoDB using the provided URL.

    Args:
        url (str): MongoDB connection URL.

    Returns:
        Union[None, Database]: Database instance if successful, None if failed.
    """
    try:
        database = Database(url)
        await database.client.admin.command("ping")
        logging.info("Connected to MongoDB. Ping successful!")
        return database
    except Exception as e:
        logging.error("Failed to connect to MongoDB: %s", e)
        return None


async def get_mongo_url() -> str:
    """
    Retrieves MongoDB connection URL from configuration file.

    Returns:
        str: MongoDB connection URL.
    """
    file_config = pathlib.Path(__file__).parent.parent / "settings.ini"
    async with aiofiles.open(file_config, mode="r") as config_file:
        config_text = await config_file.read()
        config = configparser.ConfigParser()
        config.read_string(config_text)

        mongo_user = config.get("mongo", "user")
        mongo_pass = config.get("mongo", "password")
        mongo_db = config.get("mongo", "db_name")
        mongo_domain = config.get("mongo", "domain")

        url = f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_domain}/?retryWrites=true&w=majority"
        return url
