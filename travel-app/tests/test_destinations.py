def test_destinations_requires_auth(client):
    response = client.get("/destinations")
    assert response.status_code == 401


def test_list_all_destinations(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 6


def test_filter_by_tag(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"tag": "beach"})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert names == ["Kribi Beachfront"]


def test_filter_by_country(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"country": "Cameroon"})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert len(names) == 6


def test_filter_by_max_cost(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"max_cost": 50000})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert "Yaoundé Food Trail" in names
    assert "Waza National Park" not in names


def test_free_text_search(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"q": "waterfall"})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert names == ["Lobé Waterfalls", "Ekom Nkam Waterfalls"]
