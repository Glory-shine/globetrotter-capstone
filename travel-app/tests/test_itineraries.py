def test_itineraries_requires_auth(client):
    response = client.get("/itineraries")
    assert response.status_code == 401


def test_create_itinerary_success(client, auth_headers):
    payload = {
        "title": "Bali honeymoon",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "items": [
            {"day": 1, "activity": "Arrive, beach sunset"},
            {"day": 3, "activity": "Rice terrace hike"},
        ],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Bali honeymoon"
    assert body["destination_id"] == "dest-001"
    assert len(body["items"]) == 2


def test_create_itinerary_unknown_destination_rejected(client, auth_headers):
    payload = {
        "title": "Nowhere trip",
        "destination_id": "dest-999",
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "items": [],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 404


def test_create_itinerary_end_before_start_rejected(client, auth_headers):
    payload = {
        "title": "Backwards trip",
        "destination_id": "dest-001",
        "start_date": "2026-09-07",
        "end_date": "2026-09-01",
        "items": [],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 422


def test_create_itinerary_item_day_exceeds_trip_length_rejected(client, auth_headers):
    payload = {
        "title": "Too many days",
        "destination_id": "dest-001",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03",  # 3-day trip
        "items": [{"day": 10, "activity": "Impossible day"}],
    }
    response = client.post("/itineraries", json=payload, headers=auth_headers)
    assert response.status_code == 400


def test_list_itineraries_returns_only_own_trips(client, auth_headers):
    client.post(
        "/itineraries",
        json={
            "title": "Trip A",
            "destination_id": "dest-001",
            "start_date": "2026-09-01",
            "end_date": "2026-09-02",
            "items": [],
        },
        headers=auth_headers,
    )

    # A second, unrelated user should see an empty list of their own.
    other = client.post(
        "/register",
        json={
            "username": "other_user",
            "email": "other@example.com",
            "password": "password123",
            "preferences": [],
        },
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    mine = client.get("/itineraries", headers=auth_headers)
    theirs = client.get("/itineraries", headers=other_headers)

    assert len(mine.json()) == 1
    assert len(theirs.json()) == 0
