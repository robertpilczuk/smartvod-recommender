def _user(client, email):
    return client.post("/api/register", json={"email": email, "password": "1"}).json()["user_id"]


def test_learn_without_ratings(client):
    uid = _user(client, "nolearn@b.pl")
    r = client.post("/api/learn", json={"user_id": uid}).json()
    assert r["learned"] is False
    assert r["ratings_used"] == 0


def test_learn_from_library_ratings(client):
    uid = _user(client, "learn@b.pl")
    # film 1 to Sci-Fi (ocena 5), film 3 to Drama (ocena 2)
    client.post("/api/library", json={"user_id": uid, "movie_id": 1, "rating": 5})
    client.post("/api/library", json={"user_id": uid, "movie_id": 3, "rating": 2})

    r = client.post("/api/learn", json={"user_id": uid}).json()
    assert r["learned"] is True
    assert r["ratings_used"] == 2
    assert r["avg_rating"] == 3.5
    # najwyżej oceniany gatunek to Sci-Fi (ocena 5 > 2)
    assert r["top_genres"][0] == "Sci-Fi"


def test_learn_stores_profile(client):
    import predict

    uid = _user(client, "prof@b.pl")
    client.post("/api/library", json={"user_id": uid, "movie_id": 2, "rating": 4})
    client.post("/api/learn", json={"user_id": uid})

    profile = predict.get_user_profile(uid)
    assert profile is not None
    assert profile["mean"] == 4.0
    assert profile["genre"]["Comedy"] == 4.0


def test_learn_unknown_user(client):
    assert client.post("/api/learn", json={"user_id": 999999}).status_code == 404
