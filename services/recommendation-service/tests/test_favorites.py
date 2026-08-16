from tests.conftest import make_token


def auth(user_id="user-123", username="traveler1"):
    return {"Authorization": f"Bearer {make_token(user_id=user_id, username=username)}"}


def test_favorites_requires_auth(client):
    assert client.get("/favorites").status_code == 401


def test_new_destination_is_not_favorited_by_default(client, auth_headers):
    response = client.get("/destinations/dest-001", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_favorite"] is False


def test_toggle_favorite_adds_and_removes(client, auth_headers):
    response = client.post("/destinations/dest-001/favorite", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_favorite"] is True

    response = client.get("/destinations/dest-001", headers=auth_headers)
    assert response.json()["is_favorite"] is True

    response = client.post("/destinations/dest-001/favorite", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_favorite"] is False


def test_toggle_favorite_unknown_destination_404(client, auth_headers):
    response = client.post("/destinations/dest-999/favorite", headers=auth_headers)
    assert response.status_code == 404


def test_list_favorites_returns_only_favorited_destinations(client, auth_headers):
    client.post("/destinations/dest-001/favorite", headers=auth_headers)
    client.post("/destinations/dest-002/favorite", headers=auth_headers)

    response = client.get("/favorites", headers=auth_headers)
    assert response.status_code == 200
    names = {d["id"] for d in response.json()}
    assert names == {"dest-001", "dest-002"}
    assert all(d["is_favorite"] for d in response.json())


def test_favorites_are_scoped_per_user(client, auth_headers):
    client.post("/destinations/dest-001/favorite", headers=auth_headers)

    other_headers = auth(user_id="user-456", username="traveler2")
    response = client.get("/favorites", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_my_comments_requires_auth(client):
    assert client.get("/comments/mine").status_code == 401


def test_list_my_comments_returns_own_comments_with_destination_name(client, auth_headers):
    client.post("/destinations/dest-001/comments", json={"text": "Magnifique lieu !"}, headers=auth_headers)
    client.post("/destinations/dest-002/comments", json={"text": "À visiter absolument."}, headers=auth_headers)

    response = client.get("/comments/mine", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {c["destination_id"] for c in body} == {"dest-001", "dest-002"}
    assert all(c["destination_name"] for c in body)


def test_list_my_comments_excludes_other_users(client, auth_headers):
    client.post("/destinations/dest-001/comments", json={"text": "Un commentaire."}, headers=auth_headers)

    other_headers = auth(user_id="user-789", username="traveler3")
    response = client.get("/comments/mine", headers=other_headers)
    assert response.status_code == 200
    assert response.json() == []
