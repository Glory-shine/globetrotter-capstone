from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---- Auth ----

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    preferences: List[str] = Field(
        default_factory=list,
        description="Interest tags, e.g. ['beach', 'nightlife', 'food']",
    )


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Destinations ----

class DestinationOut(BaseModel):
    id: str
    name: str
    country: str
    tags: List[str]
    climate: str
    avg_cost_per_day: float
    price_range_xaf: Optional[str] = None
    description: str
    best_season: str
    category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    budget_tier: Optional[str] = None


# ---- Itineraries ----

class ItineraryItem(BaseModel):
    day: int = Field(..., ge=1, description="1-indexed day of the trip")
    activity: str = Field(..., min_length=1, max_length=200)


class ItineraryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    destination_id: str
    start_date: date
    end_date: date
    items: List[ItineraryItem] = Field(default_factory=list)

    @field_validator("end_date")
    @classmethod
    def end_date_after_start_date(cls, v: date, info):
        start = info.data.get("start_date")
        if start is not None and v < start:
            raise ValueError("end_date must be on or after start_date")
        return v


class ItineraryOut(BaseModel):
    id: str
    user_id: str
    title: str
    destination_id: str
    start_date: date
    end_date: date
    items: List[ItineraryItem]
    created_at: str
