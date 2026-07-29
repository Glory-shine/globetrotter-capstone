def test_destinations_requires_auth(client):
    response = client.get("/destinations")
    assert response.status_code == 401


def test_list_all_destinations(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers)
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert len(names) >= 6
    assert "Yaoundé (centre-ville)" in names
    assert "Bamenda Highlands" in names


def test_filter_by_tag(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"tag": "beach"})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert names == ["Kribi Beachfront"]


def test_filter_by_country(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"country": "Cameroon"})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert len(names) >= 6
    assert "Yaoundé (centre-ville)" in names


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


def test_free_text_search_includes_imported_csv_destinations(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"q": "yaoundé"})
    assert response.status_code == 200
    names = [d["name"] for d in response.json()]
    assert "Yaoundé (centre-ville)" in names


def test_destinations_include_media_payloads(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers)
    assert response.status_code == 200

    destination = next((d for d in response.json() if d["name"] == "Bafoussam"), None)
    assert destination is not None
    assert destination["media"]["main"]
    assert destination["media"]["secondary"]
