"""ORM models owned exclusively by this service: the destination/place
catalog (Bafoussam edition — geolocation, category, real photo references,
a rating, priced on-site activities, and a fun anecdote) plus visitor
comments/replies/likes attached to each destination."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    # Repurposed for the Bafoussam edition: holds the commune/arrondissement
    # (Bafoussam I, II — Baleng, or III — Bamougoum) instead of a country.
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Site type: Chefferie, Musée, Marché, Nature, Monument, Religieux,
    # Sport, Transport, Culture...
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    tags: Mapped[list] = mapped_column(JSON, default=list)

    # Average entry fee in FCFA (0 = free / visite libre). This is an
    # indicative maximum — see DestinationOut.price_note in schemas.py.
    avg_cost_per_day: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    description: Mapped[str] = mapped_column(String(600), nullable=False)
    best_season: Mapped[str] = mapped_column(String(150), nullable=False)

    # A short, fun cultural tidbit shown on the details page ("Le
    # saviez-vous ?"), separate from the factual description.
    anecdote: Mapped[str] = mapped_column(String(600), default="")

    # Real GPS coordinates (WGS84) for map display and fare estimation.
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    rating: Mapped[float] = mapped_column(Float, default=4.5)
    price_range_xaf: Mapped[str] = mapped_column(String(50), default="")

    # Real photography, hotlinked from Wikimedia Commons (see seed_data.py
    # for sourcing notes). `media_main` is the hero image; `media_secondary`
    # is a gallery of additional real photos where available.
    media_main: Mapped[str] = mapped_column(String(500), default="")
    media_secondary: Mapped[list] = mapped_column(JSON, default=list)

    # On-site paid activities: [{"name": "...", "price": "1 500 FCFA"}, ...]
    activities: Mapped[list] = mapped_column(JSON, default=list)


class Favorite(Base):
    """A user's saved/liked destination — powers the "Mes favoris" section
    of the profile. One row per (user_id, destination_id) pair."""

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "destination_id", name="uq_favorite_user_destination"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    destination_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Comment(Base):
    """A visitor comment or reply attached to a destination.

    `parent_id` is null for a top-level comment and set to the id of the
    comment being answered for a reply — one level of nesting, which is
    all a "reply to a comment" feature needs. `liked_by` stores the ids of
    users who liked it; the count and "did I like this" flag are derived
    at serialization time (see routers/comments_routes.py)."""

    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    destination_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    parent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("comments.id"), nullable=True, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    liked_by: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
