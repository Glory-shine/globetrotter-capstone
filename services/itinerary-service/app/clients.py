"""
Outbound synchronous REST call: itinerary-service → recommendation-service.

Before persisting a new itinerary, this service must confirm the
destination actually exists — but destinations live in a database this
service doesn't have access to (database-per-service). So it asks the
service that owns that data instead of querying it directly.

The caller's own bearer token is forwarded rather than minting a separate
service credential — recommendation-service's endpoint is protected by the
same shared-secret JWT, so this "just works" and keeps auth logic in one
place. If recommendation-service is slow or down, we fail loudly with a
503 rather than silently accepting an unverifiable destination_id — this
is the network-latency/availability trade-off the architecture doc warns
about.
"""

import httpx
from fastapi import HTTPException, status

from app.config import settings


def validate_destination(destination_id: str, authorization_header: str) -> dict:
    url = f"{settings.recommendation_service_url}/destinations/{destination_id}"
    try:
        response = httpx.get(
            url,
            headers={"Authorization": authorization_header},
            timeout=5.0,
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach recommendation-service to validate the destination.",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination '{destination_id}' does not exist",
        )
    if response.status_code == 401:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")
    response.raise_for_status()
    return response.json()
