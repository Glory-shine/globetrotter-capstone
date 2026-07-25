"""
Business Logic Layer — Trip Planner.

Validates that an itinerary references a real destination and that its
day-by-day items fit within the actual span of the trip before the data
access layer is asked to persist anything.
"""

from datetime import date
from typing import Any, Dict, List

from fastapi import HTTPException, status


class TripPlanner:
    def __init__(self, destinations: List[Dict[str, Any]]):
        self._by_id = {d["id"]: d for d in destinations}

    def validate_destination(self, destination_id: str) -> Dict[str, Any]:
        dest = self._by_id.get(destination_id)
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination '{destination_id}' does not exist",
            )
        return dest

    def validate_trip_length(self, start: date, end: date, items: List[Any]) -> int:
        trip_days = (end - start).days + 1
        if trip_days < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip must span at least one day",
            )
        for item in items:
            if item.day > trip_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Itinerary item day {item.day} exceeds trip length of {trip_days} day(s)",
                )
        return trip_days
