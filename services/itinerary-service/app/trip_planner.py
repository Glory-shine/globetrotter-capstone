from datetime import date
from typing import List

from fastapi import HTTPException, status

from app.schemas import ItineraryItem


def validate_trip_length(start: date, end: date, items: List[ItineraryItem]) -> int:
    trip_days = (end - start).days + 1
    if trip_days < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trip must span at least one day")
    for item in items:
        if item.day > trip_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Itinerary item day {item.day} exceeds trip length of {trip_days} day(s)",
            )
    return trip_days
