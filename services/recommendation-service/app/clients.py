"""
Outbound synchronous REST calls: recommendation-service → user-service and
recommendation-service → itinerary-service.

Per the architecture spec, RecommendationService "reads data from User and
Itinerary services" rather than owning that data itself. Both calls simply
forward the caller's own bearer token — no separate service credential is
minted, so each downstream service authenticates the request exactly as if
the client had called it directly. Both are best-effort: if a downstream
service is unavailable, we degrade to an empty result rather than failing
the whole recommendations request, since a slightly-less-personalized
recommendation is far better than no recommendation at all.
"""

import logging
from typing import List

import httpx

from app.config import settings

logger = logging.getLogger("recommendation-service.clients")


def get_user_preferences(authorization_header: str) -> List[str]:
    try:
        response = httpx.get(
            f"{settings.user_service_url}/users/me",
            headers={"Authorization": authorization_header},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json().get("preferences", [])
    except httpx.HTTPError as exc:
        logger.warning("user-service unavailable, falling back to no preferences: %s", exc)
        return []


def get_user_itineraries(authorization_header: str) -> List[dict]:
    try:
        response = httpx.get(
            f"{settings.itinerary_service_url}/itineraries",
            headers={"Authorization": authorization_header},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        logger.warning("itinerary-service unavailable, falling back to no history: %s", exc)
        return []
