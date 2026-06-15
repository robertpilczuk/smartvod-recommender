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


def test_recommend_mood_filters_to_mood_genres(client):
    # nastrój „funny" mapuje na Comedy, więc wraca tylko film komediowy (id 2)
    recs = client.post("/api/recommend", json={"mood": "funny", "limit": 5}).json()["recommendations"]
    ids = {x["id"] for x in recs}
    assert ids == {2}


def test_recommend_surprise_returns_random_subset(client):
    recs = client.post("/api/recommend", json={"surprise": True, "limit": 3}).json()["recommendations"]
    assert len(recs) == 3
    # wszystkie z dostępnej puli (pięć zasianych filmów)
    assert {x["id"] for x in recs} <= {1, 2, 3, 4, 5}


def test_recommend_reasons_mention_genre(client):
    recs = client.post("/api/recommend", json={"genres": ["Sci-fi"], "mood": "surprise", "limit": 1}).json()["recommendations"]
    assert any("Sci-fi" in why for why in recs[0]["reasons"])
