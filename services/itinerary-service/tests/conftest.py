import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".sqlite3")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["RECOMMENDATION_SERVICE_URL"] = "http://recommendation-service.invalid"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@rabbitmq.invalid/"

import datetime  # noqa: E402

import jwt  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


def make_token(user_id: str = "user-123", username: str = "traveler1", role: str = "user") -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + datetime.timedelta(minutes=30),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture()
def auth_headers():
    return {"Authorization": f"Bearer {make_token()}"}


@pytest.fixture()
def admin_headers():
    return {"Authorization": f"Bearer {make_token(user_id='admin-1', username='admin', role='admin')}"}


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
