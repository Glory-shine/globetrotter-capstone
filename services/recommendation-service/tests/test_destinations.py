def test_destinations_requires_auth(client):
    assert client.get("/destinations").status_code == 401


def test_reseeding_adds_missing_destinations_to_a_partially_seeded_db(client, auth_headers, db_session):
    """Regression test: on a database that already has *some* destinations
    (e.g. a Postgres volume from an earlier version of the catalog),
    re-running the seed must add whatever is missing rather than bailing
    out because the table isn't empty."""
    from app.models import Destination
    from app.seed_data import MOCK_DESTINATIONS, seed_destinations

    # Simulate an "old" database that only ever got the first destination.
    db_session.query(Destination).delete()
    db_session.add(Destination(**MOCK_DESTINATIONS[0]))
    db_session.commit()

    seed_destinations()

    response = client.get("/destinations", headers=auth_headers)
    assert len(response.json()) == len(MOCK_DESTINATIONS)


def test_list_all_destinations_seeded(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 70  # Bafoussam catalog seeded on startup (incl. santé & éducation)


def test_filter_by_tag(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"tag": "marche"})
    assert response.status_code == 200
    names = {d["name"] for d in response.json()}
    assert "Marché A (Grand Marché de Bafoussam)" in names
    assert "Marché B" in names


def test_filter_by_country_commune(client, auth_headers):
    response = client.get("/destinations", headers=auth_headers, params={"country": "Bamougoum"})
    assert response.status_code == 200
    names = {d["name"] for d in response.json()}
    assert names == {
        "Chutes de la Metché",
        "Aéroport de Bafoussam-Bamougoum (BFX)",
        "Chefferie Bamougoum",
        "Grottes de Doumelong",
    }


def test_destination_has_real_coordinates_and_media(client, auth_headers):
    response = client.get("/destinations/dest-001", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Chefferie Supérieure de Bafoussam"
    assert body["latitude"] == 5.4740
    assert body["longitude"] == 10.4130
    assert body["media"]["main"].startswith("https://commons.wikimedia.org/")
    assert len(body["activities"]) == 2
    assert body["activities"][0]["price"] == "2 000 FCFA"
    assert body["anecdote"]  # non-empty fun fact
    assert "négoci" in body["price_note"].lower()


def test_get_unknown_destination_404(client, auth_headers):
    response = client.get("/destinations/dest-999", headers=auth_headers)
    assert response.status_code == 404
