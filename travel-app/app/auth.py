"""
Authentication Layer.

- Passwords are hashed with salted PBKDF2-HMAC-SHA256 (stdlib only, no
  native extensions required).
- Sessions are stateless JSON Web Tokens (JWT); no server-side session
  store is needed, which keeps the monolith horizontally-stateless even
  though storage itself is a single file.
"""

import datetime
import hashlib
import hmac
import os
import secrets
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app import storage

SECRET_KEY = os.environ.get("TRAVEL_APP_SECRET_KEY", "dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("TRAVEL_APP_TOKEN_EXPIRE_MIN", "60"))
PBKDF2_ITERATIONS = 100_000

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    )
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest_hex = stored_hash.split("$", 1)
    except ValueError:
        return False
    new_digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(new_digest.hex(), digest_hex)


def create_access_token(data: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    to_encode = data.copy()
    now = datetime.datetime.now(datetime.timezone.utc)
    expire = now + datetime.timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """FastAPI dependency that resolves and returns the authenticated user.

    Wire this into any endpoint with `current_user: dict = Depends(get_current_user)`
    to protect it — used by the destinations, recommendations, and itineraries
    routers per the spec.
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    data = await storage.read_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user
