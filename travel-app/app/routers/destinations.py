from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app import auth, storage
from app.models import DestinationOut

router = APIRouter(tags=["destinations"])


@router.get("/destinations", response_model=List[DestinationOut])
async def search_destinations(
    country: Optional[str] = Query(None, description="Exact country match, case-insensitive"),
    tag: Optional[str] = Query(None, description="e.g. beach, culture, mountain, nightlife"),
    max_cost: Optional[float] = Query(None, ge=0, description="Max average cost per day"),
    q: Optional[str] = Query(None, description="Free-text search over name and description"),
    current_user: dict = Depends(auth.get_current_user),
):
    data = await storage.read_data()
    results = data["destinations"]

    if country:
        results = [d for d in results if d["country"].lower() == country.lower()]
    if tag:
        results = [d for d in results if tag.lower() in [t.lower() for t in d["tags"]]]
    if max_cost is not None:
        results = [d for d in results if d["avg_cost_per_day"] <= max_cost]
    if q:
        needle = q.lower()
        results = [
            d for d in results if needle in d["name"].lower() or needle in d["description"].lower()
        ]

    return results
