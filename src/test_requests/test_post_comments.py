import sys
import os
import unittest
import requests
from datetime import timedelta, date
from bson import ObjectId

# Adding project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.jwt_utils import create_access_token

class TestCreatePost(unittest.TestCase):
    host = "http://127.0.0.1:8000"
    post_id = None  # Variable to store the ID of the created post

    def setUp(self):
        """Create a new post before each test."""
        self.post_id = self.create_test_post()

    def test_create_post(self):
        """Test creating a post."""
        headers = {"content-type": "application/json"}
        token = self.get_auth_token()

        post_data = {
            "title": "Test Post Title",
            "content": "This is a test post content",
            "auto_reply_enabled": False,
            "auto_reply_delay": 30,
            "author_id": "669924f2ebe61a73a91b5db8"  # Using a valid ObjectId
        }

        response = requests.post(
            f"{self.host}/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        response_json = response.json()

        # Print response for debugging
        print("Create Post Response:", response_json)

        self.assertEqual(response.status_code, 200)
        self.assertIn("_id", response_json)
        self.post_id = response_json["_id"]  # Get ID as a string

    def test_create_comment(self):
        """Test creating a comment."""
        headers = {"content-type": "application/json"}
        token = self.get_auth_token()

        # Use the post ID from the previous test
        post_id = self.post_id

        comment_data = {
            "content": "This is a test comment content."
        }

        response = requests.post(
            f"{self.host}/posts/{post_id}/comments/",
            json=comment_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        response_json = response.json()

        # Log response for debugging
        print("Create Comment Response:", response_json)

        self.assertEqual(response.status_code, 200)
        self.assertIn("content", response_json)
        self.assertEqual(response_json["content"], comment_data["content"])

    def test_comment_analytics(self):
        """Test comment analytics."""
        headers = {"content-type": "application/json"}
        token = self.get_auth_token()

        date_from = (date.today() - timedelta(days=7)).isoformat()
        date_to = date.today().isoformat()

        response = requests.get(
            f"{self.host}/api/comments-daily-breakdown?date_from={date_from}&date_to={date_to}",
            headers={"Authorization": f"Bearer {token}"}
        )

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response_json, list)  # Ensure the response is a list

    def get_auth_token(self):
        """Generate a token based on test user data."""
        user_data = {
            "id": "669924f2ebe61a73a91b5db8",  # Using a valid ObjectId
            "email": "test@example.com"
        }
        token = create_access_token(user_data, expires_delta=timedelta(minutes=30))
        return token

    def create_test_post(self):
        """Create a test post and return its ID."""
        headers = {"content-type": "application/json"}
        post_data = {
            "title": "Test Post Title",
            "content": "This is a test post content",
            "auto_reply_enabled": False,
            "auto_reply_delay": 30,
            "author_id": "669924f2ebe61a73a91b5db8"  # Using a valid ObjectId
        }

        response = requests.post(
            f"{self.host}/posts/",
            json=post_data,
            headers={"Authorization": f"Bearer {self.get_auth_token()}"}
        )

        response_json = response.json()

        # Print response for debugging
        print("Create Test Post Response:", response_json)

        self.assertEqual(response.status_code, 200)
        self.assertIn("_id", response_json)
        return response_json["_id"]  # Return ID as a string

if __name__ == "__main__":
    unittest.main()
