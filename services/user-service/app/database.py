"""
Database engine + session factory for the User Service's own Postgres
database (user_db). Each microservice owns exactly one database and no
other service is permitted to query it directly — this module is that
service's only gateway to its data.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency yielding a request-scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if they don't exist yet. Fine for this project's scope;
    swap for Alembic migrations in a real production rollout."""
    from app import models  # noqa: F401  (ensure models are registered)

    Base.metadata.create_all(bind=engine)
    _seed_default_admin()


def _seed_default_admin():
    """Ensures a single default administrator account always exists, so the
    admin area is reachable out of the box. Credentials: username "admin",
    email admin@example.com, password Admin@123 — change it after first
    login in a real deployment."""
    from app import auth
    from app.models import User

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing is not None:
            if existing.role != "admin":
                existing.role = "admin"
                db.commit()
            return

        db.add(
            User(
                username="admin",
                email="admin@example.com",
                hashed_password=auth.hash_password("Admin@123"),
                role="admin",
                preferences=[],
            )
        )
        db.commit()
    finally:
        db.close()
