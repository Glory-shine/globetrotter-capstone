import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import auth
from app.database import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRegister

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Create a user and immediately return a JWT, exactly like the
    monolith did — the frontend's flow is unchanged."""
    existing_username = db.scalar(select(User).where(User.username.ilike(payload.username)))
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    existing_email = db.scalar(select(User).where(User.email.ilike(payload.email)))
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=auth.hash_password(payload.password),
        role="user",  # self-registration can never grant admin rights
        preferences=payload.preferences,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": user.id, "username": user.username, "role": user.role})
    return TokenResponse(access_token=token, role=user.role)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username.ilike(payload.username)))
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = auth.create_access_token({"sub": user.id, "username": user.username, "role": user.role})
    return TokenResponse(access_token=token, role=user.role)
