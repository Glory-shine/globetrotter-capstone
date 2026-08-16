import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routing import resolve_target
from app.config import settings


def test_routing_table_maps_known_paths():
    assert resolve_target("/register") == settings.user_service_url
    assert resolve_target("/login") == settings.user_service_url
    assert resolve_target("/users/me") == settings.user_service_url
    assert resolve_target("/destinations") == settings.recommendation_service_url
    assert resolve_target("/destinations/dest-001") == settings.recommendation_service_url
    assert resolve_target("/recommendations") == settings.recommendation_service_url
    assert resolve_target("/fare") == settings.recommendation_service_url
    assert resolve_target("/favorites") == settings.recommendation_service_url
    assert resolve_target("/comments/abc123/like") == settings.recommendation_service_url
    assert resolve_target("/itineraries") == settings.itinerary_service_url


def test_routing_table_returns_none_for_unknown_path():
    assert resolve_target("/does-not-exist") is None


def test_unknown_path_returns_404():
    with TestClient(app) as client:
        response = client.get("/nope")
    assert response.status_code == 404


def test_health_endpoint_reports_gateway_status():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["gateway"] == "ok"
        assert "user-service" in body["services"]
        assert "itinerary-service" in body["services"]
        assert "recommendation-service" in body["services"]


def test_proxy_forwards_request_and_response(mocker):
    """Verifies the proxy forwards method/headers/body to the resolved
    service and relays the upstream response back unchanged, without
    needing a real backend service running."""
    import httpx

    fake_response = httpx.Response(
        status_code=201,
        json={"access_token": "fake-token", "token_type": "bearer"},
        request=httpx.Request("POST", "http://user-service.invalid/register"),
    )
    mock_request = mocker.patch("app.main._client.request", return_value=fake_response)

    with TestClient(app) as client:
        response = client.post(
            "/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )

    assert response.status_code == 201
    assert response.json()["access_token"] == "fake-token"

    called_kwargs = mock_request.call_args.kwargs
    assert called_kwargs["method"] == "POST"
    assert called_kwargs["url"] == f"{settings.user_service_url}/register"


def test_proxy_returns_503_when_upstream_unreachable(mocker):
    import httpx

    mocker.patch("app.main._client.request", side_effect=httpx.ConnectError("refused"))

    with TestClient(app) as client:
        response = client.get("/destinations")

    assert response.status_code == 503
