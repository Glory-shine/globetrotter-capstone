"""ORM models owned by the Itinerary Service.

Note this service does NOT have a foreign key to a `destinations` table —
that table lives in a different database owned by recommendation-service.
Cross-service references are stored as plain ids (`destination_id`) and
validated over the network, not enforced by a DB constraint. This is the
standard trade-off of database-per-service: referential integrity across
services becomes an application-level concern.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    start_date: Mapped[str] = mapped_column(Date, nullable=False)
    end_date: Mapped[str] = mapped_column(Date, nullable=False)
    items: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
