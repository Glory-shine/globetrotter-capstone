def test_recommendations_requires_auth(client):
    response = client.get("/recommendations")
    assert response.status_code == 401


def test_recommendations_match_preferences(client, auth_headers):
    # auth_headers registers a user with preferences=["beach", "romantic"]
    response = client.get("/recommendations", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) > 0
    names = [d["name"] for d in body]
    # Kribi Beachfront has both beach and romantic tags, should rank highest
    assert names[0] == "Kribi Beachfront"


def test_recommendations_respect_limit(client, auth_headers):
    response = client.get("/recommendations", headers=auth_headers, params={"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_recommendations_respect_budget(client, auth_headers):
    response = client.get(
        "/recommendations", headers=auth_headers, params={"max_budget": 50000, "limit": 3}
    )
    assert response.status_code == 200
    body = response.json()
    assert any(d["name"] == "Yaoundé Food Trail" for d in body)


def test_recommendations_include_local_context_fields(client, auth_headers):
    response = client.get("/recommendations", headers=auth_headers, params={"limit": 3})
    assert response.status_code == 200
    body = response.json()
    assert any("price_range_xaf" in item for item in body)
    assert any(item.get("category") for item in body)
