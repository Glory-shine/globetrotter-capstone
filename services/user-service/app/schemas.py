from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    preferences: List[str] = Field(default_factory=list)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "user"


class UserProfile(BaseModel):
    """Public profile shape returned by GET /users/me — this is what
    other services (e.g. recommendation-service) receive when they call
    this service on behalf of a request."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: EmailStr
    role: str
    preferences: List[str]
    created_at: datetime
