from pydantic import BaseModel
from typing import List, Optional
import datetime


class PaperBase(BaseModel):
    doi: str
    url: str
    title: str
    authors: List[str]
    subjects: List[str]
    summary: str


class PaperSchema(PaperBase):
    class Config:
        orm_mode = True


class PaperMarkBase(BaseModel):
    doi: str
    is_favorite: Optional[bool] = False
    rating: Optional[int] = None
    note: Optional[str] = None

    is_read: Optional[bool] = False
    is_uninterested: Optional[bool] = False
    is_to_read: Optional[bool] = True
    read_count: Optional[int] = 0
    progress: Optional[int] = 0

    first_read_at: Optional[datetime.datetime] = None
    last_read_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class PaperMarkSchema(PaperMarkBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    id: Optional[int]
    username: str
    password: Optional[str]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
