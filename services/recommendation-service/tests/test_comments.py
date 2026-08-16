from tests.conftest import make_token


def auth(user_id="user-123", username="traveler1"):
    return {"Authorization": f"Bearer {make_token(user_id=user_id, username=username)}"}


def test_list_comments_requires_auth(client):
    assert client.get("/destinations/dest-001/comments").status_code == 401


def test_list_comments_unknown_destination_404(client, auth_headers):
    response = client.get("/destinations/dest-999/comments", headers=auth_headers)
    assert response.status_code == 404


def test_list_comments_empty_by_default(client, auth_headers):
    response = client.get("/destinations/dest-001/comments", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_comment(client, auth_headers):
    response = client.post(
        "/destinations/dest-001/comments", json={"text": "Superbe visite, très instructif !"}, headers=auth_headers
    )
    assert response.status_code == 201
    body = response.json()
    assert body["text"] == "Superbe visite, très instructif !"
    assert body["username"] == "traveler1"
    assert body["likes_count"] == 0
    assert body["liked_by_me"] is False
    assert body["replies"] == []


def test_create_comment_unknown_destination_404(client, auth_headers):
    response = client.post("/destinations/dest-999/comments", json={"text": "Test"}, headers=auth_headers)
    assert response.status_code == 404


def test_create_comment_blank_text_rejected(client, auth_headers):
    response = client.post("/destinations/dest-001/comments", json={"text": ""}, headers=auth_headers)
    assert response.status_code == 422


def test_reply_to_a_comment_is_nested(client, auth_headers):
    top = client.post(
        "/destinations/dest-001/comments", json={"text": "Quelqu'un a une astuce pour la visite ?"}, headers=auth_headers
    ).json()

    other = auth(user_id="user-456", username="kofi")
    reply = client.post(
        "/destinations/dest-001/comments",
        json={"text": "Arrivez tôt le matin, c'est plus calme.", "parent_id": top["id"]},
        headers=other,
    )
    assert reply.status_code == 201
    assert reply.json()["parent_id"] == top["id"]

    listing = client.get("/destinations/dest-001/comments", headers=auth_headers).json()
    assert len(listing) == 1  # only the top-level comment at the root
    assert len(listing[0]["replies"]) == 1
    assert listing[0]["replies"][0]["text"] == "Arrivez tôt le matin, c'est plus calme."


def test_reply_to_unknown_parent_404(client, auth_headers):
    response = client.post(
        "/destinations/dest-001/comments", json={"text": "Réponse orpheline", "parent_id": "does-not-exist"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_like_and_unlike_comment_toggles(client, auth_headers):
    comment = client.post(
        "/destinations/dest-001/comments", json={"text": "À visiter absolument."}, headers=auth_headers
    ).json()

    liker = auth(user_id="user-789", username="amina")
    liked = client.post(f"/comments/{comment['id']}/like", headers=liker)
    assert liked.status_code == 200
    assert liked.json()["likes_count"] == 1
    assert liked.json()["liked_by_me"] is True

    unliked = client.post(f"/comments/{comment['id']}/like", headers=liker)
    assert unliked.status_code == 200
    assert unliked.json()["likes_count"] == 0
    assert unliked.json()["liked_by_me"] is False


def test_like_unknown_comment_404(client, auth_headers):
    response = client.post("/comments/does-not-exist/like", headers=auth_headers)
    assert response.status_code == 404


def test_comments_are_scoped_per_destination(client, auth_headers):
    client.post("/destinations/dest-001/comments", json={"text": "Sur la chefferie"}, headers=auth_headers)
    client.post("/destinations/dest-005/comments", json={"text": "Sur le marché"}, headers=auth_headers)

    dest_1_comments = client.get("/destinations/dest-001/comments", headers=auth_headers).json()
    dest_5_comments = client.get("/destinations/dest-005/comments", headers=auth_headers).json()

    assert len(dest_1_comments) == 1
    assert len(dest_5_comments) == 1
    assert dest_1_comments[0]["text"] != dest_5_comments[0]["text"]
