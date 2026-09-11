from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItineraryItem(BaseModel):
    day: int = Field(..., ge=1)
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
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    destination_id: str
    start_date: date
    end_date: date
    items: List[ItineraryItem]
    created_at: datetime
