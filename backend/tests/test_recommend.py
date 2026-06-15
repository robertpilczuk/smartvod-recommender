def test_recommend_returns_scored_items_with_reasons(client):
    r = client.post("/api/recommend", json={"genres": ["Sci-fi"], "mood": "surprise", "limit": 3})
    assert r.status_code == 200
    recs = r.json()["recommendations"]
    assert 1 <= len(recs) <= 3
    top = recs[0]
    assert {"id", "title", "score", "reasons"} <= set(top)
    assert isinstance(top["reasons"], list) and top["reasons"]
    # wyniki posortowane malejąco
    scores = [x["score"] for x in recs]
    assert scores == sorted(scores, reverse=True)


def test_recommend_ranks_matching_genre_and_mood_first(client):
    recs = client.post("/api/recommend", json={"genres": ["Sci-fi"], "mood": "surprise", "limit": 5}).json()["recommendations"]
    # Film Sci-Fi (id 1) trafia w gatunek i nastrój oraz ma najwyższą średnią
    assert recs[0]["id"] == 1


def test_recommend_excludes_library_and_rejected(client):
    uid = client.post("/api/register", json={"email": "r@b.pl", "password": "1", "genres": ["Sci-fi"]}).json()["user_id"]
    ids = [x["id"] for x in client.post("/api/recommend", json={"user_id": uid, "limit": 5}).json()["recommendations"]]
    assert 1 in ids and 2 in ids

    client.post("/api/library", json={"user_id": uid, "movie_id": 1, "rating": 5})
    client.post("/api/interactions", json={"user_id": uid, "movie_id": 2, "action": "reject"})

    ids2 = [x["id"] for x in client.post("/api/recommend", json={"user_id": uid, "limit": 5}).json()["recommendations"]]
    assert 1 not in ids2 and 2 not in ids2


def test_recommend_reasons_mention_genre(client):
    recs = client.post("/api/recommend", json={"genres": ["Sci-fi"], "mood": "surprise", "limit": 1}).json()["recommendations"]
    assert any("Sci-fi" in why for why in recs[0]["reasons"])
