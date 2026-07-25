def test_register_new_user_returns_token(client):
    response = client.post(
        "/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
            "preferences": ["culture"],
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_register_duplicate_username_rejected(client):
    payload = {
        "username": "bob",
        "email": "bob1@example.com",
        "password": "password123",
        "preferences": [],
    }
    first = client.post("/register", json=payload)
    assert first.status_code == 201

    payload["email"] = "bob2@example.com"
    second = client.post("/register", json=payload)
    assert second.status_code == 409


def test_register_weak_password_rejected(client):
    response = client.post(
        "/register",
        json={
            "username": "carol",
            "email": "carol@example.com",
            "password": "short",
            "preferences": [],
        },
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/register",
        json={
            "username": "dave",
            "email": "dave@example.com",
            "password": "password123",
            "preferences": [],
        },
    )
    response = client.post("/login", json={"username": "dave", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_rejected(client):
    client.post(
        "/register",
        json={
            "username": "erin",
            "email": "erin@example.com",
            "password": "password123",
            "preferences": [],
        },
    )
    response = client.post("/login", json={"username": "erin", "password": "wrongpass"})
    assert response.status_code == 401


def test_login_unknown_user_rejected(client):
    response = client.post("/login", json={"username": "ghost", "password": "whatever123"})
    assert response.status_code == 401
