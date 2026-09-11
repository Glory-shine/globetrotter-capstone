from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import CurrentUser, get_current_user
from app.database import get_db
from app.fare import estimate_fare
from app.models import Destination
from app.schemas import FareEstimate

router = APIRouter(tags=["fare"])


@router.get("/fare", response_model=FareEstimate)
def get_fare_estimate(
    from_id: str = Query(..., description="Origin destination id"),
    to_id: str = Query(..., description="Arrival destination id"),
    mode: str = Query("moto", pattern="^(moto|taxi)$"),
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Estimate the moto-taxi or taxi fare between two catalog destinations,
    using their real coordinates. See app/fare.py for the pricing model and
    its real-world basis."""
    origin = db.get(Destination, from_id)
    if origin is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination '{from_id}' does not exist")

    arrival = db.get(Destination, to_id)
    if arrival is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Destination '{to_id}' does not exist")

    if from_id == to_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Origin and destination must differ")

    result = estimate_fare(origin.latitude, origin.longitude, arrival.latitude, arrival.longitude, mode)

    return FareEstimate(
        from_id=origin.id,
        from_name=origin.name,
        to_id=arrival.id,
        to_name=arrival.name,
        mode=mode,
        distance_km=result.distance_km,
        duration_min=result.duration_min,
        price_fcfa=result.price_fcfa,
        price_label=result.price_label,
        note=result.note,
    )
