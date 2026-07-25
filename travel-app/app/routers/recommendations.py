from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app import auth, storage
from app.models import DestinationOut
from app.recommendation import RecommendationEngine

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=List[DestinationOut])
async def get_recommendations(
    limit: int = Query(5, ge=1, le=20),
    max_budget: Optional[float] = Query(None, ge=0),
    current_user: dict = Depends(auth.get_current_user),
):
    data = await storage.read_data()
    user_itineraries = [i for i in data["itineraries"] if i["user_id"] == current_user["id"]]

    engine = RecommendationEngine(data["destinations"])
    return engine.recommend(
        preferences=current_user.get("preferences", []),
        user_itineraries=user_itineraries,
        max_budget=max_budget,
        limit=limit,
    )
