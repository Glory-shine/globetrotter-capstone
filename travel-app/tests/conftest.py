import json

import pytest
from fastapi.testclient import TestClient

SEED_DESTINATIONS = [
    {
        "id": "dest-001",
        "name": "Yaoundé Food Trail",
        "country": "Cameroon",
        "tags": ["food", "culture", "nature", "budget"],
        "climate": "tropical",
        "avg_cost_per_day": 32000.0,
        "price_range_xaf": "15,000-40,000",
        "description": "A spirited city loop through boukarous, street food stalls, and green neighbourhoods.",
        "best_season": "Nov-Mar",
        "category": "food",
        "latitude": 3.8480,
        "longitude": 11.5021,
        "rating": 4.7,
        "budget_tier": "budget",
    },
    {
        "id": "dest-002",
        "name": "National Museum of Yaoundé",
        "country": "Cameroon",
        "tags": ["culture", "history", "food"],
        "climate": "tropical",
        "avg_cost_per_day": 45000.0,
        "price_range_xaf": "20,000-55,000",
        "description": "A rich stop for history lovers with exhibitions on Cameroonian heritage.",
        "best_season": "Year-round",
        "category": "culture",
        "latitude": 3.8680,
        "longitude": 11.5190,
        "rating": 4.5,
        "budget_tier": "mid",
    },
    {
        "id": "dest-003",
        "name": "Waza National Park",
        "country": "Cameroon",
        "tags": ["adventure", "nature", "wildlife"],
        "climate": "sahelian",
        "avg_cost_per_day": 85000.0,
        "price_range_xaf": "60,000-120,000",
        "description": "Wildlife safaris and dramatic landscapes in northern Cameroon.",
        "best_season": "Nov-Apr",
        "category": "nature",
        "latitude": 11.3000,
        "longitude": 14.6500,
        "rating": 4.8,
        "budget_tier": "premium",
    },
    {
        "id": "dest-004",
        "name": "Kribi Beachfront",
        "country": "Cameroon",
        "tags": ["beach", "nature", "budget", "romantic"],
        "climate": "coastal",
        "avg_cost_per_day": 38000.0,
        "price_range_xaf": "18,000-50,000",
        "description": "Relaxed beaches, grilled fish, and palm-fringed evenings by the Atlantic.",
        "best_season": "Nov-Apr",
        "category": "nature",
        "latitude": 2.9360,
        "longitude": 9.9060,
        "rating": 4.4,
        "budget_tier": "budget",
    },
    {
        "id": "dest-005",
        "name": "Lobé Waterfalls",
        "country": "Cameroon",
        "tags": ["adventure", "nature", "waterfall"],
        "climate": "tropical",
        "avg_cost_per_day": 42000.0,
        "price_range_xaf": "20,000-55,000",
        "description": "A scenic ecotourism escape with river views, hiking, and dramatic cascades.",
        "best_season": "Jun-Oct",
        "category": "nature",
        "latitude": 4.0200,
        "longitude": 9.7000,
        "rating": 4.6,
        "budget_tier": "mid",
    },
    {
        "id": "dest-008",
        "name": "Ekom Nkam Waterfalls",
        "country": "Cameroon",
        "tags": ["adventure", "nature", "waterfall"],
        "climate": "humid",
        "avg_cost_per_day": 47000.0,
        "price_range_xaf": "20,000-60,000",
        "description": "A dramatic waterfall escape ideal for hiking, photography, and eco-travel.",
        "best_season": "Nov-Feb",
        "category": "nature",
        "latitude": 5.1200,
        "longitude": 10.9300,
        "rating": 4.6,
        "budget_tier": "mid",
    },
    {
        "id": "dest-cm-001",
        "name": "Yaoundé (centre-ville)",
        "country": "Cameroon",
        "tags": ["city", "centre", "culture"],
        "climate": "tropical",
        "avg_cost_per_day": 25000.0,
        "price_range_xaf": "10,000-40,000",
        "description": "Capitale politique du Cameroun",
        "best_season": "Year-round",
        "category": "local",
        "latitude": 3.8480,
        "longitude": 11.5021,
        "rating": 4.3,
        "budget_tier": "budget",
    },
    {
        "id": "dest-cm-002",
        "name": "Bamenda Highlands",
        "country": "Cameroon",
        "tags": ["nature", "adventure", "budget"],
        "climate": "highland",
        "avg_cost_per_day": 34000.0,
        "price_range_xaf": "15,000-45,000",
        "description": "Cool climate, scenic villages, and adventure routes that feel far from the city.",
        "best_season": "Nov-Feb",
        "category": "nature",
        "latitude": 5.9600,
        "longitude": 10.1500,
        "rating": 4.4,
        "budget_tier": "budget",
    },
]


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """A TestClient wired to a fresh, disposable JSON datastore per test."""
    db_path = tmp_path / "db.json"
    db_path.write_text(
        json.dumps({"users": [], "destinations": SEED_DESTINATIONS, "itineraries": []})
    )
    monkeypatch.setenv("TRAVEL_APP_DB_PATH", str(db_path))
    monkeypatch.setenv("TRAVEL_APP_SECRET_KEY", "test-secret-key")

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    """Registers a user with beach/romantic preferences and returns auth headers."""
    response = client.post(
        "/register",
        json={
            "username": "traveler1",
            "email": "traveler1@example.com",
            "password": "supersecret123",
            "preferences": ["beach", "romantic"],
        },
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
