"""
JWT verification for the Recommendation Service — same pattern as
itinerary-service: no local user store, tokens are verified locally
against the shared signing secret.
"""

from typing import Any, Dict

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=True)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")


class CurrentUser:
    def __init__(self, id: str, username: str, role: str = "user"):
        self.id = id
        self.username = username
        self.role = role


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return CurrentUser(id=user_id, username=payload.get("username", ""), role=payload.get("role", "user"))


def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Gate for admin-only endpoints (manual destination creation,
    system-wide stats). 403s any authenticated-but-non-admin caller."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user


def get_authorization_header(authorization: str = Header(...)) -> str:
    """Raw `Authorization: Bearer <token>` value, forwarded as-is to
    user-service/itinerary-service so they can verify it independently."""
    return authorization
