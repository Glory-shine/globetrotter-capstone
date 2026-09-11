from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ActivityOut(BaseModel):
    name: str
    price: str  # pre-formatted, e.g. "1 500 FCFA" or "Gratuit"


class MediaOut(BaseModel):
    main: Optional[str] = None
    secondary: List[str] = []


PRICE_NOTE = (
    "Les prix affichés sont des estimations maximales, à titre indicatif — "
    "ils se négocient généralement sur place, en particulier pour le moto-taxi et le taxi."
)


class DestinationOut(BaseModel):
    id: str
    name: str
    country: str  # commune (Bafoussam I / II — Baleng / III — Bamougoum)
    category: str
    tags: List[str]
    avg_cost_per_day: float  # average entry fee, in FCFA — indicative maximum
    description: str
    anecdote: str
    best_season: str
    latitude: float
    longitude: float
    rating: float
    price_range_xaf: str
    price_note: str = PRICE_NOTE
    media: MediaOut
    activities: List[ActivityOut]
    is_favorite: bool = False


class DestinationCreate(BaseModel):
    """Payload for admin-created destinations. Mirrors DestinationOut's
    editable fields, minus id/is_favorite which the server controls."""

    name: str = Field(..., min_length=2, max_length=200)
    country: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=50)
    tags: List[str] = []
    avg_cost_per_day: float = Field(0, ge=0)
    description: str = Field(..., min_length=10)
    anecdote: str = ""
    best_season: str = "Toute l'année"
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    rating: float = Field(4.0, ge=0, le=5)
    price_range_xaf: str = ""
    media_main: Optional[str] = None
    media_secondary: List[str] = []
    activities: List[ActivityOut] = []


class FareEstimate(BaseModel):
    from_id: str
    from_name: str
    to_id: str
    to_name: str
    mode: str  # "moto" | "taxi"
    distance_km: float
    duration_min: int
    price_fcfa: int
    price_label: str
    note: str


class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[str] = None


class CommentOut(BaseModel):
    id: str
    destination_id: str
    parent_id: Optional[str] = None
    user_id: str
    username: str
    text: str
    likes_count: int
    liked_by_me: bool
    created_at: datetime
    replies: List["CommentOut"] = []


CommentOut.model_rebuild()


class MyCommentOut(BaseModel):
    """A comment written by the current user, enriched with enough context
    about its destination to let the profile page link straight back to
    where it was posted."""

    id: str
    destination_id: str
    destination_name: str
    parent_id: Optional[str] = None
    text: str
    created_at: datetime
