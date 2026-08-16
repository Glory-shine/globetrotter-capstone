from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user, require_admin
from app.database import get_db
from app.models import Comment, Destination, Favorite
from app.schemas import DestinationCreate, DestinationOut

router = APIRouter(tags=["destinations"])


def _favorite_ids(db: Session, user_id: str) -> set:
    return set(db.scalars(select(Favorite.destination_id).where(Favorite.user_id == user_id)).all())


def _to_out(d: Destination, favorite_ids: Optional[set] = None) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "country": d.country,
        "category": d.category,
        "tags": d.tags,
        "avg_cost_per_day": d.avg_cost_per_day,
        "description": d.description,
        "anecdote": d.anecdote,
        "best_season": d.best_season,
        "latitude": d.latitude,
        "longitude": d.longitude,
        "rating": d.rating,
        "price_range_xaf": d.price_range_xaf,
        "media": {"main": d.media_main, "secondary": d.media_secondary},
        "activities": d.activities,
        "is_favorite": bool(favorite_ids) and d.id in favorite_ids,
    }


@router.get("/destinations", response_model=List[DestinationOut])
def search_destinations(
    country: Optional[str] = Query(None, description="Commune: Bafoussam I / II / III"),
    tag: Optional[str] = Query(None),
    max_cost: Optional[float] = Query(None, ge=0, description="Max average entry fee, in FCFA"),
    q: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = db.scalars(select(Destination)).all()

    if country:
        results = [d for d in results if country.lower() in d.country.lower()]
    if tag:
        results = [d for d in results if tag.lower() in [t.lower() for t in d.tags]]
    if max_cost is not None:
        results = [d for d in results if d.avg_cost_per_day <= max_cost]
    if q:
        needle = q.lower()
        results = [d for d in results if needle in d.name.lower() or needle in d.description.lower()]

    favorite_ids = _favorite_ids(db, current_user.id)
    return [_to_out(d, favorite_ids) for d in results]


@router.get("/destinations/{destination_id}", response_model=DestinationOut)
def get_destination(
    destination_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch a single destination by id.

    Also the endpoint itinerary-service calls synchronously before
    creating an itinerary, to confirm the destination_id it was given is
    real (see itinerary-service's app/clients.py).
    """
    destination = db.get(Destination, destination_id)
    if destination is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination '{destination_id}' does not exist")
    favorite_ids = _favorite_ids(db, current_user.id)
    return _to_out(destination, favorite_ids)


@router.get("/favorites", response_model=List[DestinationOut])
def list_favorites(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Every destination the current user has favorited/liked, newest first."""
    favorites = db.scalars(
        select(Favorite).where(Favorite.user_id == current_user.id).order_by(Favorite.created_at.desc())
    ).all()
    favorite_ids = {f.destination_id for f in favorites}

    destinations_by_id = {d.id: d for d in db.scalars(select(Destination)).all()}
    ordered = [destinations_by_id[f.destination_id] for f in favorites if f.destination_id in destinations_by_id]
    return [_to_out(d, favorite_ids) for d in ordered]


@router.post("/destinations/{destination_id}/favorite", response_model=DestinationOut)
def toggle_favorite(
    destination_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggles the current user's favorite/like on a destination (favorite
    if not yet favorited, remove if already favorited). Liking a place
    here is exactly what makes it show up under "Mes favoris" on the
    profile — the two are the same underlying record, not two systems to
    keep in sync."""
    destination = db.get(Destination, destination_id)
    if destination is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination '{destination_id}' does not exist")

    existing = db.scalar(
        select(Favorite).where(Favorite.user_id == current_user.id, Favorite.destination_id == destination_id)
    )
    if existing:
        db.delete(existing)
    else:
        db.add(Favorite(user_id=current_user.id, destination_id=destination_id))
    db.commit()

    favorite_ids = _favorite_ids(db, current_user.id)
    return _to_out(destination, favorite_ids)


@router.post("/destinations", response_model=DestinationOut, status_code=status.HTTP_201_CREATED)
def create_destination(
    payload: DestinationCreate,
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: manually add a new destination to the catalog."""
    destination = Destination(
        name=payload.name,
        country=payload.country,
        category=payload.category,
        tags=payload.tags,
        avg_cost_per_day=payload.avg_cost_per_day,
        description=payload.description,
        anecdote=payload.anecdote,
        best_season=payload.best_season,
        latitude=payload.latitude,
        longitude=payload.longitude,
        rating=payload.rating,
        price_range_xaf=payload.price_range_xaf,
        media_main=payload.media_main,
        media_secondary=payload.media_secondary,
        activities=[a.model_dump() for a in payload.activities],
    )
    db.add(destination)
    db.commit()
    db.refresh(destination)
    return _to_out(destination, set())


@router.get("/destinations/admin/stats", tags=["admin"])
def get_destination_stats(
    current_user: CurrentUser = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: system-wide catalog counts, for the admin stats page."""
    total_destinations = db.scalar(select(func.count()).select_from(Destination)) or 0
    by_category = dict(db.execute(select(Destination.category, func.count()).group_by(Destination.category)).all())
    by_commune = dict(db.execute(select(Destination.country, func.count()).group_by(Destination.country)).all())
    total_favorites = db.scalar(select(func.count()).select_from(Favorite)) or 0
    total_comments = db.scalar(select(func.count()).select_from(Comment)) or 0
    most_favorited = db.execute(
        select(Destination.name, func.count(Favorite.id).label("n"))
        .join(Favorite, Favorite.destination_id == Destination.id)
        .group_by(Destination.id)
        .order_by(func.count(Favorite.id).desc())
        .limit(5)
    ).all()
    most_commented = db.execute(
        select(Destination.name, func.count(Comment.id).label("n"))
        .join(Comment, Comment.destination_id == Destination.id)
        .group_by(Destination.id)
        .order_by(func.count(Comment.id).desc())
        .limit(5)
    ).all()

    average_rating = db.scalar(select(func.avg(Destination.rating))) or 0
    free_destinations = db.scalar(
        select(func.count()).select_from(Destination).where(Destination.avg_cost_per_day == 0)
    ) or 0
    without_photo = db.scalar(
        select(func.count()).select_from(Destination).where(Destination.media_main == "")
    ) or 0

    tag_counter: dict[str, int] = {}
    for (tags,) in db.execute(select(Destination.tags)).all():
        for tag in tags or []:
            tag_counter[tag] = tag_counter.get(tag, 0) + 1
    top_tags = sorted(tag_counter.items(), key=lambda kv: kv[1], reverse=True)[:8]

    return {
        "total_destinations": total_destinations,
        "destinations_by_category": by_category,
        "destinations_by_commune": by_commune,
        "total_favorites": total_favorites,
        "total_comments": total_comments,
        "most_favorited": [{"name": name, "favorites": n} for name, n in most_favorited],
        "most_commented": [{"name": name, "comments": n} for name, n in most_commented],
        "average_rating": round(float(average_rating), 2),
        "free_destinations": free_destinations,
        "paid_destinations": total_destinations - free_destinations,
        "without_photo": without_photo,
        "top_tags": [{"tag": tag, "count": n} for tag, n in top_tags],
    }
