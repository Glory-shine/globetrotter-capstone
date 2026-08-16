from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import User
from app.schemas import UserProfile

router = APIRouter(tags=["users"])


@router.get("/users/me", response_model=UserProfile)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile.

    This is a dual-purpose endpoint: the frontend never calls it directly
    today, but **recommendation-service calls it on the user's behalf**
    (forwarding the same bearer token) to read `preferences` — this is the
    service-to-service synchronous REST call the architecture calls for.
    """
    return current_user


@router.get("/users/admin/stats", tags=["admin"])
def get_user_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Admin-only: system-wide user counts, for the admin stats page."""
    all_users = db.scalars(select(User)).all()
    total_users = len(all_users)
    by_role: dict[str, int] = {}
    for u in all_users:
        by_role[u.role] = by_role.get(u.role, 0) + 1

    with_preferences = sum(1 for u in all_users if u.preferences)
    recent_users = sorted(all_users, key=lambda u: u.created_at, reverse=True)[:5]

    return {
        "total_users": total_users,
        "users_by_role": by_role,
        "users_with_preferences": with_preferences,
        "recent_signups": [
            {"username": u.username, "role": u.role, "created_at": u.created_at} for u in recent_users
        ],
    }
