import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, status

from app import auth, storage
from app.models import ItineraryCreate, ItineraryOut
from app.trip_planner import TripPlanner

router = APIRouter(tags=["itineraries"])


@router.post("/itineraries", response_model=ItineraryOut, status_code=status.HTTP_201_CREATED)
async def create_itinerary(
    payload: ItineraryCreate,
    current_user: dict = Depends(auth.get_current_user),
):
    data = await storage.read_data()

    planner = TripPlanner(data["destinations"])
    planner.validate_destination(payload.destination_id)
    planner.validate_trip_length(payload.start_date, payload.end_date, payload.items)

    itinerary = {
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "title": payload.title,
        "destination_id": payload.destination_id,
        "start_date": payload.start_date.isoformat(),
        "end_date": payload.end_date.isoformat(),
        "items": [item.model_dump() for item in payload.items],
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    data["itineraries"].append(itinerary)
    await storage.write_data(data)
    return itinerary


@router.get("/itineraries", response_model=List[ItineraryOut])
async def list_itineraries(current_user: dict = Depends(auth.get_current_user)):
    data = await storage.read_data()
    return [i for i in data["itineraries"] if i["user_id"] == current_user["id"]]
