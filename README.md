Here's the project description in English:

## Project Description

### About the Project
This project implements an API for managing posts and comments using FastAPI and MongoDB. It includes functionality for user registration and authentication, creating and managing posts and comments, content moderation, and comment analytics generation.

### Project Structure
The project is organized as follows:

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

### Database Connection (database/connect.py)
Contains the logic for connecting to the MongoDB database using `motor`, an asynchronous MongoDB driver for Python.

### JWT Utilities (utils/jwt_utils.py)
Implements functions for creating and decoding JWT tokens used for user authentication.

### Registration Routes (routes/registration.py)
Implements the endpoint for registering new users. Email and password validation are performed before saving user data in the database.

### User Data Update Routes (routes/update.py)
Includes endpoints for updating username, email, and password. Each request is logged to ensure change tracking.

### User Data Retrieval Routes (routes/user_data.py)
Allows fetching user data by a specific field or all user data except for the password. Token validation is performed for each request.

### Security Utilities (security/security.py)
Includes functions for hashing and verifying passwords using the `passlib` library.

### Tests (test_requests/test.py)
A script for automated testing of registration and login functionalities, as well as user data retrieval.

### Post and Comment Testing (test_requests/test_post_comments.py)
Includes tests for creating posts and comments, as well as retrieving comments for a post.

### Main File (main.py)
The main file of the application, including routes from all modules and creating an instance of FastAPI.

### Usage
1. **Running the Application**:
   - Ensure MongoDB is running.
   - Install project dependencies with `pip install -r requirements.txt`.
   - Start the FastAPI server with `uvicorn main:app --reload`.

2. **Endpoints**:
   - `/auth/`: Endpoints for authentication.
   - `/delete/`: Endpoints for deleting data.
   - `/registration/`: Endpoints for user registration.
   - `/update/`: Endpoints for updating user data.
   - `/user_data/`: Endpoints for retrieving user data.
   - `/username/`: Endpoints for managing username.

3. **Testing**:
   - Run tests located in `src/test_requests/` with `pytest`.
