from app import clients, events


def test_itineraries_requires_auth(client):
    assert client.get("/itineraries").status_code == 401


def test_create_itinerary_success(client, auth_headers, mocker):
    mocker.patch.object(clients, "validate_destination", return_value={"id": "dest-001", "name": "Bali"})
    mocker.patch.object(events, "publish_itinerary_created", return_value=None)

    payload = {
        "title": "Bali honeymoon",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "items": [{"day": 1, "activity": "Beach sunset"}],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Bali honeymoon"
    assert len(body["items"]) == 1

    # Confirms the async event publish was invoked (fire-and-forget).
    events.publish_itinerary_created.assert_called_once()


def test_admin_stats_requires_admin_role(client, auth_headers):
    assert client.get("/itineraries/admin/stats", headers=auth_headers).status_code == 403


def test_admin_stats_accessible_to_admin(client, auth_headers, admin_headers, mocker):
    mocker.patch.object(clients, "validate_destination", return_value={"id": "dest-001", "name": "Bali"})
    mocker.patch.object(events, "publish_itinerary_created", return_value=None)

    payload = {
        "title": "Bali honeymoon",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "items": [{"day": 1, "activity": "Beach sunset"}],
    }
    client.post("/itineraries", json=payload, headers=auth_headers)

    response = client.get("/itineraries/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_itineraries"] >= 1
    assert body["unique_planners"] >= 1
    assert isinstance(body["most_planned_destination_ids"], list)
    assert body["average_items_per_itinerary"] >= 1
    assert isinstance(body["recent_itineraries"], list)
    assert body["recent_itineraries"][0]["title"] == "Bali honeymoon"


def test_create_itinerary_unknown_destination_rejected(client, auth_headers, mocker):
    from fastapi import HTTPException

    mocker.patch.object(
        clients,
        "validate_destination",
        side_effect=HTTPException(status_code=404, detail="Destination 'dest-999' does not exist"),
    )
    payload = {
        "title": "Nowhere trip",
        "destination_id": "dest-999",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "items": [],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 404


def test_create_itinerary_recommendation_service_down(client, auth_headers, mocker):
    from fastapi import HTTPException

    mocker.patch.object(
        clients,
        "validate_destination",
        side_effect=HTTPException(status_code=503, detail="Could not reach recommendation-service"),
    )
    payload = {
        "title": "Trip",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-02",
        "items": [],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 503


def test_create_itinerary_item_day_exceeds_trip_length(client, auth_headers, mocker):
    mocker.patch.object(clients, "validate_destination", return_value={"id": "dest-001"})
    mocker.patch.object(events, "publish_itinerary_created", return_value=None)

    payload = {
        "title": "Too many days",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03",
        "items": [{"day": 10, "activity": "Impossible"}],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 400


def test_list_itineraries_scoped_to_caller(client, mocker):
    mocker.patch.object(clients, "validate_destination", return_value={"id": "dest-001"})
    mocker.patch.object(events, "publish_itinerary_created", return_value=None)

    from tests.conftest import make_token

    headers_a = {"Authorization": f"Bearer {make_token(user_id='user-a')}"}
    headers_b = {"Authorization": f"Bearer {make_token(user_id='user-b')}"}

    payload = {
        "title": "Trip A",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-02",
        "items": [],
    }
    client.post("/itineraries", json=payload, headers=headers_a)

    mine = client.get("/itineraries", headers=headers_a)
    theirs = client.get("/itineraries", headers=headers_b)

    assert len(mine.json()) == 1
    assert len(theirs.json()) == 0
