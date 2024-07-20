### Project Description

#### About the Project
This project provides an API for managing posts and comments with FastAPI and MongoDB. It includes user registration, authentication, post and comment management, content moderation, and comment analytics.

#### Project Structure
The project directory is organized as follows:

```
project_test/
│
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connect.py
│   │
│   ├── journal/
│   │   ├── __init__.py
│   │   ├── journal.py
│   │   ├── journal_email.py
│   │   ├── journal_password.py
│   │   ├── journal_username.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── models.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── delete.py
│   │   ├── registration.py
│   │   ├── update.py
│   │   ├── user_data.py
│   │   ├── username.py
│   │
│   ├── security/
│   │   ├── __init__.py
│   │   ├── security.py
│   │
│   ├── test_requests/
│   │   ├── __init__.py
│   │   ├── test_auth_regist.py
│   │   ├── test_post_comments.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── email_utils.py
│   │   ├── jwt_utils.py
│   │
│   ├── __init__.py
│   ├── main.py
│
├── __init__.py
└── main.py
```

### Database Connection (`database/connect.py`)
Contains the logic for connecting to MongoDB using `motor`, an asynchronous driver for Python.

### JWT Utilities (`utils/jwt_utils.py`)
Implements functions for creating and decoding JWT tokens for user authentication.

### Registration Routes (`routes/registration.py`)
Provides an endpoint for registering new users, with email and password validation.

### User Data Update Routes (`routes/update.py`)
Includes endpoints for updating username, email, and password, with each request logged.

### User Data Retrieval Routes (`routes/user_data.py`)
Allows retrieval of user data by specific field or all data except the password, with token validation.

### Security Utilities (`security/security.py`)
Functions for hashing and verifying passwords using the `passlib` library.

### Testing
#### Tests (`test_requests/test.py`)
Automated tests for registration and login functionalities, and user data retrieval.

#### Post and Comment Testing (`test_requests/test_post_comments.py`)
Includes:
- **Post Creation**: Tests for creating posts.
- **Comment Creation**: Tests for adding comments to posts.
- **Comment Retrieval**: Tests for retrieving comments associated with posts.

#### Test Coverage
Ensure all routes and functionalities are covered:
- **User Registration**: Test scenarios for valid and invalid registration.
- **Authentication**: Test login functionality and JWT token generation.
- **Data Update**: Test updating user details and ensure logging.
- **Post and Comment Management**: Test creating, updating, and retrieving posts and comments.
- **Analytics**: Test analytics endpoints for correctness in comment statistics.

### Running the Application
1. Ensure MongoDB is running.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the server with `uvicorn main:app --reload`.

### Endpoints
- `/auth/`: Authentication endpoints.
- `/delete/`: Endpoints for deleting data.
- `/registration/`: User registration.
- `/update/`: Update user data.
- `/user_data/`: Retrieve user data.
- `/username/`: Manage usernames.

### Testing
- Run tests using `pytest` from the `src/test_requests/` directory.
