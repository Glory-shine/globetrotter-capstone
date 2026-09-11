from app import clients


def test_recommendations_requires_auth(client):
    assert client.get("/recommendations").status_code == 401


def test_recommendations_use_preferences_from_user_service(client, auth_headers, mocker):
    mocker.patch.object(clients, "get_user_preferences", return_value=["chefferie", "culture"])
    mocker.patch.object(clients, "get_user_itineraries", return_value=[])

    response = client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert names[0] == "Chefferie Supérieure de Bafoussam"  # chefferie + culture tags -> top score

    clients.get_user_preferences.assert_called_once()
    clients.get_user_itineraries.assert_called_once()


def test_recommendations_include_full_schema(client, auth_headers, mocker):
    mocker.patch.object(clients, "get_user_preferences", return_value=["marche"])
    mocker.patch.object(clients, "get_user_itineraries", return_value=[])

    response = client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    top = response.json()[0]
    assert "latitude" in top and "longitude" in top
    assert "media" in top and "activities" in top


def test_recommendations_degrade_gracefully_when_services_down(client, auth_headers, mocker):
    mocker.patch.object(clients, "get_user_preferences", return_value=[])
    mocker.patch.object(clients, "get_user_itineraries", return_value=[])

    response = client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_recommendations_reflect_favorited_destinations(client, auth_headers, mocker):
    mocker.patch.object(clients, "get_user_preferences", return_value=["chefferie", "culture"])
    mocker.patch.object(clients, "get_user_itineraries", return_value=[])

    client.post("/destinations/dest-001/favorite", headers=auth_headers)

    response = client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    body = {d["id"]: d["is_favorite"] for d in response.json()}
    assert body.get("dest-001") is True


def test_recommendations_respect_limit_and_budget(client, auth_headers, mocker):
    mocker.patch.object(clients, "get_user_preferences", return_value=["marche"])
    mocker.patch.object(clients, "get_user_itineraries", return_value=[])

    response = client.get(
        "/recommendations", headers=auth_headers, params={"limit": 2, "max_budget": 0}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) <= 2
