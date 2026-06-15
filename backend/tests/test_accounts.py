def test_register_login_and_user(client):
    r = client.post("/api/register", json={
        "email": "a@b.pl", "password": "123", "first_name": "Ala", "genres": ["Sci-fi"],
    })
    assert r.status_code == 200
    body = r.json()
    uid = body["user_id"]
    assert body["genres"] == ["Sci-fi"]
    assert body["email"] == "a@b.pl"

    # duplikat adresu
    assert client.post("/api/register", json={"email": "a@b.pl", "password": "x"}).status_code == 409

    # złe hasło
    assert client.post("/api/login", json={"email": "a@b.pl", "password": "zle"}).status_code == 401

    # poprawne logowanie
    r = client.post("/api/login", json={"email": "a@b.pl", "password": "123"})
    assert r.status_code == 200 and r.json()["user_id"] == uid

    # profil
    assert client.get(f"/api/user/{uid}").json()["email"] == "a@b.pl"
    assert client.get("/api/user/999999").status_code == 404


def test_register_normalizes_email(client):
    uid = client.post("/api/register", json={"email": "  MIX@Case.PL ", "password": "1"}).json()["user_id"]
    assert client.post("/api/login", json={"email": "mix@case.pl", "password": "1"}).json()["user_id"] == uid


def test_register_requires_email_and_password(client):
    assert client.post("/api/register", json={"email": "", "password": "1"}).status_code == 400
    assert client.post("/api/register", json={"email": "x@y.pl", "password": ""}).status_code == 400


def test_login_unknown_email(client):
    assert client.post("/api/login", json={"email": "brak@nikt.pl", "password": "x"}).status_code == 401


def test_preferences_save_and_read(client):
    uid = client.post("/api/register", json={"email": "p@b.pl", "password": "1"}).json()["user_id"]
    assert client.put("/api/preferences", json={
        "user_id": uid, "genres": ["Komedia"], "mood": "funny",
    }).status_code == 200
    u = client.get(f"/api/user/{uid}").json()
    assert u["genres"] == ["Komedia"] and u["mood"] == "funny"
    assert client.put("/api/preferences", json={"user_id": 999999, "mood": "calm"}).status_code == 404
