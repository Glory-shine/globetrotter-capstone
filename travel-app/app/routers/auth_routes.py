import datetime
import uuid

from fastapi import APIRouter, HTTPException, status

from app import auth, storage
from app.models import TokenResponse, UserLogin, UserRegister

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    data = await storage.read_data()

    if any(u["username"].lower() == payload.username.lower() for u in data["users"]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    if any(u["email"].lower() == payload.email.lower() for u in data["users"]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = {
        "id": str(uuid.uuid4()),
        "username": payload.username,
        "email": payload.email,
        "hashed_password": auth.hash_password(payload.password),
        "preferences": payload.preferences,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    data["users"].append(user)
    await storage.write_data(data)

    token = auth.create_access_token({"sub": user["id"], "username": user["username"]})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    data = await storage.read_data()
    user = next(
        (u for u in data["users"] if u["username"].lower() == payload.username.lower()), None
    )
    if not user or not auth.verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = auth.create_access_token({"sub": user["id"], "username": user["username"]})
    return TokenResponse(access_token=token)
