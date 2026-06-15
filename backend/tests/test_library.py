def _new_user(client, email):
    return client.post("/api/register", json={"email": email, "password": "1"}).json()["user_id"]


def test_library_add_update_and_list(client):
    uid = _new_user(client, "l@b.pl")
    assert client.post("/api/library", json={"user_id": uid, "movie_id": 1, "rating": 5}).status_code == 200
    # ponowny zapis aktualizuje ocenę (upsert, bez duplikatu)
    assert client.post("/api/library", json={"user_id": uid, "movie_id": 1, "rating": 4}).status_code == 200

    lib = client.get(f"/api/library/{uid}").json()["library"]
    assert len(lib) == 1
    assert lib[0]["movie_id"] == 1 and lib[0]["rating"] == 4
    assert lib[0]["title"] == "Test Sci-Fi"


def test_library_add_without_rating(client):
    uid = _new_user(client, "n@b.pl")
    assert client.post("/api/library", json={"user_id": uid, "movie_id": 2}).status_code == 200
    lib = client.get(f"/api/library/{uid}").json()["library"]
    assert lib[0]["rating"] is None


def test_library_invalid_movie_or_user(client):
    uid = _new_user(client, "e@b.pl")
    assert client.post("/api/library", json={"user_id": uid, "movie_id": 99999, "rating": 5}).status_code == 404
    assert client.get("/api/library/999999").status_code == 404


def test_interaction_recorded(client):
    uid = _new_user(client, "i@b.pl")
    assert client.post("/api/interactions", json={
        "user_id": uid, "movie_id": 2, "action": "reject", "reason": "watched", "mood": "funny",
    }).status_code == 200
    assert client.post("/api/interactions", json={
        "user_id": uid, "movie_id": 99999, "action": "reject",
    }).status_code == 404
