import datetime
from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import clients, events
from app.auth import CurrentUser, get_current_user, require_admin
from app.database import get_db
from app.models import Itinerary
from app.schemas import ItineraryCreate, ItineraryOut
from app.trip_planner import validate_trip_length

router = APIRouter(tags=["itineraries"])


@router.post("/itineraries", response_model=ItineraryOut, status_code=201)
def create_itinerary(
    payload: ItineraryCreate,
    authorization: str = Header(...),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a validated itinerary.

    Two cross-service checks happen before anything is written:
    1. Synchronous REST call to recommendation-service to confirm the
       destination exists (see app/clients.py).
    2. Local validation that day-by-day items fit within the trip span.

    After the write, an `itinerary.created` event is published to RabbitMQ
    (best-effort, see app/events.py) for any interested subscriber.
    """
    clients.validate_destination(payload.destination_id, authorization)
    validate_trip_length(payload.start_date, payload.end_date, payload.items)

    itinerary = Itinerary(
        user_id=current_user.id,
        title=payload.title,
        destination_id=payload.destination_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        items=[item.model_dump() for item in payload.items],
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(itinerary)
    db.commit()
    db.refresh(itinerary)

    events.publish_itinerary_created(
        {
            "id": itinerary.id,
            "user_id": itinerary.user_id,
            "destination_id": itinerary.destination_id,
            "title": itinerary.title,
        }
    )
    return itinerary


@router.get("/itineraries", response_model=List[ItineraryOut])
def list_itineraries(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    itineraries = db.scalars(
        select(Itinerary).where(Itinerary.user_id == current_user.id).order_by(Itinerary.created_at.desc())
    ).all()
    return itineraries


@router.get("/itineraries/admin/stats", tags=["admin"])
def get_itinerary_stats(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: system-wide itinerary counts, for the admin stats page."""
    all_itineraries = db.scalars(select(Itinerary)).all()
    unique_users = {i.user_id for i in all_itineraries}
    destination_counts: dict[str, int] = {}
    for i in all_itineraries:
        destination_counts[i.destination_id] = destination_counts.get(i.destination_id, 0) + 1
    most_planned = sorted(destination_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]

    item_counts = [len(i.items or []) for i in all_itineraries]
    average_items = round(sum(item_counts) / len(item_counts), 1) if item_counts else 0

    recent_itineraries = sorted(all_itineraries, key=lambda i: i.created_at, reverse=True)[:5]

    return {
        "total_itineraries": len(all_itineraries),
        "unique_planners": len(unique_users),
        "most_planned_destination_ids": [{"destination_id": d, "itineraries": n} for d, n in most_planned],
        "average_items_per_itinerary": average_items,
        "recent_itineraries": [
            {
                "title": i.title,
                "destination_id": i.destination_id,
                "created_at": i.created_at,
                "items": len(i.items or []),
            }
            for i in recent_itineraries
        ],
    }
