def test_create_destination_requires_admin(client, auth_headers):
    payload = {
        "name": "Belvédère Test",
        "country": "Bafoussam I",
        "category": "Nature",
        "latitude": 5.47,
        "longitude": 10.41,
        "description": "Un point de vue panoramique fictif pour les tests.",
    }
    response = client.post("/destinations", json=payload, headers=auth_headers)
    assert response.status_code == 403


def test_admin_can_create_destination(client, admin_headers):
    payload = {
        "name": "Belvédère Test",
        "country": "Bafoussam I",
        "category": "Nature",
        "tags": ["panorama"],
        "avg_cost_per_day": 0,
        "description": "Un point de vue panoramique fictif ajouté par un administrateur pour les tests.",
        "latitude": 5.47,
        "longitude": 10.41,
        "rating": 4.5,
        "price_range_xaf": "Gratuit",
    }
    response = client.post("/destinations", json=payload, headers=admin_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Belvédère Test"
    assert body["is_favorite"] is False

    listing = client.get("/destinations", headers=admin_headers)
    assert any(d["name"] == "Belvédère Test" for d in listing.json())


def test_destination_stats_requires_admin(client, auth_headers):
    assert client.get("/destinations/admin/stats", headers=auth_headers).status_code == 403


def test_destination_stats_accessible_to_admin(client, admin_headers, auth_headers):
    client.post("/destinations/dest-001/favorite", headers=auth_headers)
    client.post("/destinations/dest-001/comments", json={"text": "Superbe endroit."}, headers=auth_headers)

    response = client.get("/destinations/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total_destinations"] >= 27
    assert body["total_favorites"] >= 1
    assert body["total_comments"] >= 1
    assert isinstance(body["destinations_by_category"], dict)
    assert isinstance(body["most_favorited"], list)
    assert isinstance(body["most_commented"], list)
    assert body["most_commented"][0]["comments"] >= 1
    assert 0 <= body["average_rating"] <= 5
    assert body["free_destinations"] + body["paid_destinations"] == body["total_destinations"]
    assert isinstance(body["top_tags"], list)
    assert body["without_photo"] == 0  # every seeded destination has a real photo
