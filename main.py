from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.routes import auth, update, delete, user_data, posts, comments, registration
from src.journal import (
    journal,
    journal_username,
    journal_password,
    journal_email,
)

app = FastAPI()

# Include routers for different endpoints
app.include_router(auth.router)
app.include_router(registration.router)
app.include_router(update.router)
app.include_router(user_data.router, prefix="/api")
app.include_router(delete.router)
app.include_router(journal.router)
app.include_router(journal_username.router)
app.include_router(journal_email.router)
app.include_router(journal_password.router)
app.include_router(posts.router)
app.include_router(comments.router)

# Configure CORS (Cross-Origin Resource Sharing) middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Run the FastAPI application using Uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=8000)
