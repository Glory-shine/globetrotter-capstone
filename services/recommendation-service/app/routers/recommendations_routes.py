from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import clients
from app.auth import CurrentUser, get_authorization_header, get_current_user
from app.database import get_db
from app.models import Destination
from app.recommendation_engine import RecommendationEngine
from app.routers.destinations_routes import _favorite_ids, _to_out
from app.schemas import DestinationOut

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=List[DestinationOut])
def get_recommendations(
    limit: int = Query(5, ge=1, le=20),
    max_budget: Optional[float] = Query(None, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
    authorization: str = Depends(get_authorization_header),
    db: Session = Depends(get_db),
):
    """Personalized picks.

    Two synchronous REST calls happen before scoring, exactly as the
    architecture spec describes: this service reads the caller's
    preferences from user-service and their trip history from
    itinerary-service, forwarding the same bearer token to both. If either
    call fails, we degrade to an empty list for that input rather than
    failing the whole request (see app/clients.py).
    """
    preferences = clients.get_user_preferences(authorization)
    user_itineraries = clients.get_user_itineraries(authorization)

    all_destinations = db.scalars(select(Destination)).all()
    scoring_input = [{"id": d.id, "tags": d.tags, "avg_cost_per_day": d.avg_cost_per_day} for d in all_destinations]
    by_id = {d.id: d for d in all_destinations}

    engine = RecommendationEngine(scoring_input)
    ranked = engine.recommend(
        preferences=preferences,
        user_itineraries=user_itineraries,
        max_budget=max_budget,
        limit=limit,
    )
    favorite_ids = _favorite_ids(db, current_user.id)
    return [_to_out(by_id[r["id"]], favorite_ids) for r in ranked]
