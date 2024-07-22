from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    username: str
    email: EmailStr

class UserLog(BaseModel):
    _id: str
    field: str
    state_before: str
    state_after: str
    timestamp: datetime

class LoginData(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class PostBase(BaseModel):
    title: str
    content: str
    author_id: str
    auto_reply_enabled: bool = False
    auto_reply_delay: int = 60

class PostCreate(BaseModel):
    title: str
    content: str
    auto_reply_enabled: bool = False
    auto_reply_delay: int = 60

class PostInDB(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    content: str
    author_id: str
    auto_reply_enabled: bool
    auto_reply_delay: int
    created_at: datetime
    updated_at: datetime
    blocked: bool = False

class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    auto_reply_enabled: Optional[bool] = False
    auto_reply_delay: Optional[int] = 60
    blocked: bool = False

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str
        }

class CommentBase(BaseModel):
    post_id: str
    content: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CommentCreate(BaseModel):
    content: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Comment(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    post_id: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    blocked: bool = False

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    blocked: bool

class CommentAnalyticsResponse(BaseModel):
    date: datetime
    total_comments: int
    blocked_comments: int
