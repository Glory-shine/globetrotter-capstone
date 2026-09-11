def test_fare_requires_auth(client):
    assert client.get("/fare", params={"from_id": "dest-001", "to_id": "dest-005", "mode": "moto"}).status_code == 401


def test_fare_moto_between_two_real_destinations(client, auth_headers):
    response = client.get(
        "/fare",
        headers=auth_headers,
        params={"from_id": "dest-001", "to_id": "dest-005", "mode": "moto"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "moto"
    assert body["from_name"] == "Chefferie Supérieure de Bafoussam"
    assert body["to_name"] == "Marché A (Grand Marché de Bafoussam)"
    assert body["distance_km"] > 0
    assert body["price_fcfa"] >= 250  # moto minimum fare


def test_fare_moto_costs_more_than_taxi_for_same_trip(client, auth_headers):
    moto = client.get(
        "/fare", headers=auth_headers, params={"from_id": "dest-001", "to_id": "dest-007", "mode": "moto"}
    ).json()
    taxi = client.get(
        "/fare", headers=auth_headers, params={"from_id": "dest-001", "to_id": "dest-007", "mode": "taxi"}
    ).json()
    assert moto["price_fcfa"] > taxi["price_fcfa"]


def test_fare_unknown_destination_404(client, auth_headers):
    response = client.get(
        "/fare", headers=auth_headers, params={"from_id": "dest-001", "to_id": "dest-999", "mode": "moto"}
    )
    assert response.status_code == 404


def test_fare_same_origin_and_destination_rejected(client, auth_headers):
    response = client.get(
        "/fare", headers=auth_headers, params={"from_id": "dest-001", "to_id": "dest-001", "mode": "moto"}
    )
    assert response.status_code == 400


def test_fare_invalid_mode_rejected(client, auth_headers):
    response = client.get(
        "/fare", headers=auth_headers, params={"from_id": "dest-001", "to_id": "dest-005", "mode": "bus"}
    )
    assert response.status_code == 422
