def test_register_returns_token(client):
    response = client.post(
        "/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123", "preferences": ["culture"]},
    )
    assert response.status_code == 201
    assert "access_token" in response.json()


def test_register_duplicate_username_rejected(client):
    payload = {"username": "bob", "email": "bob1@example.com", "password": "password123", "preferences": []}
    assert client.post("/register", json=payload).status_code == 201
    payload["email"] = "bob2@example.com"
    assert client.post("/register", json=payload).status_code == 409


def test_login_success_and_wrong_password(client):
    client.post(
        "/register",
        json={"username": "dave", "email": "dave@example.com", "password": "password123", "preferences": []},
    )
    ok = client.post("/login", json={"username": "dave", "password": "password123"})
    assert ok.status_code == 200
    bad = client.post("/login", json={"username": "dave", "password": "wrongpass"})
    assert bad.status_code == 401


def test_get_my_profile_requires_auth(client):
    assert client.get("/users/me").status_code == 401


def test_get_my_profile_returns_preferences(client):
    reg = client.post(
        "/register",
        json={
            "username": "erin",
            "email": "erin@example.com",
            "password": "password123",
            "preferences": ["beach", "food"],
        },
    )
    token = reg.json()["access_token"]
    profile = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    body = profile.json()
    assert body["username"] == "erin"
    assert body["preferences"] == ["beach", "food"]


def test_self_registration_always_gets_user_role(client):
    reg = client.post(
        "/register",
        json={"username": "frank", "email": "frank@example.com", "password": "password123", "preferences": []},
    )
    assert reg.status_code == 201
    assert reg.json()["role"] == "user"

    profile = client.get("/users/me", headers={"Authorization": f"Bearer {reg.json()['access_token']}"})
    assert profile.json()["role"] == "user"


def test_default_admin_account_exists_and_can_log_in(client):
    response = client.post("/login", json={"username": "admin", "password": "Admin@123"})
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "admin"


def test_admin_stats_requires_admin_role(client):
    reg = client.post(
        "/register",
        json={"username": "gina", "email": "gina@example.com", "password": "password123", "preferences": []},
    )
    token = reg.json()["access_token"]
    response = client.get("/users/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_stats_accessible_to_admin(client):
    login = client.post("/login", json={"username": "admin", "password": "Admin@123"})
    token = login.json()["access_token"]

    client.post(
        "/register",
        json={"username": "hank", "email": "hank@example.com", "password": "password123", "preferences": []},
    )

    response = client.get("/users/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["total_users"] >= 2  # admin + hank
    assert body["users_by_role"]["admin"] >= 1
    assert body["users_by_role"]["user"] >= 1
    assert isinstance(body["recent_signups"], list)
    assert len(body["recent_signups"]) >= 2
    assert any(u["username"] == "hank" for u in body["recent_signups"])
