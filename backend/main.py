import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

import auth
import models
import predict
import recommend
from database import SessionLocal, get_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Rozgrzewka cache, by pierwsze żądanie nie ładowało statystyk i modelu na żywo
    db = SessionLocal()
    try:
        recommend._load_stats(db)
    finally:
        db.close()
    if predict.is_ready():
        predict._load()
    yield


app = FastAPI(title="SmartVOD Recommender API", version="0.1.0", lifespan=lifespan)

# Frontend uruchamiany lokalnie (python -m http.server albo Vite)
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


class RecommendRequest(BaseModel):
    user_id: int | None = None
    mood: str | None = None
    genres: list[str] | None = None
    limit: int = 5


@app.post("/api/recommend")
def api_recommend(req: RecommendRequest, db: Session = Depends(get_db)):
    items = recommend.recommend(
        db,
        user_id=req.user_id,
        mood=req.mood,
        genres=req.genres,
        limit=req.limit,
    )
    return {"recommendations": items}


# ── Konto i preferencje ──────────────────────────────────────────


def _user_payload(db, user):
    """Profil użytkownika wraz z preferencjami (gatunki, nastrój)."""
    pref = db.scalar(
        select(models.UserPreference).where(models.UserPreference.user_id == user.id)
    )
    return {
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "gender": user.gender,
        "birthdate": user.birthdate,
        "genres": json.loads(pref.genres) if pref else [],
        "mood": pref.mood if pref else None,
    }


class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    birthdate: str | None = None
    genres: list[str] | None = None


@app.post("/api/register")
def api_register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    if not email or not req.password:
        raise HTTPException(status_code=400, detail="Email i hasło są wymagane")
    if db.scalar(select(models.User).where(models.User.email == email)):
        raise HTTPException(status_code=409, detail="Konto z tym adresem już istnieje")

    user = models.User(
        source="app",
        email=email,
        password_hash=auth.hash_password(req.password),
        first_name=req.first_name,
        last_name=req.last_name,
        gender=req.gender,
        birthdate=req.birthdate,
    )
    db.add(user)
    db.flush()  # nadaje user.id
    if req.genres is not None:
        db.add(models.UserPreference(user_id=user.id, genres=json.dumps(req.genres)))
    db.commit()
    return _user_payload(db, user)


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/login")
def api_login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    user = db.scalar(select(models.User).where(models.User.email == email))
    if not user or not auth.verify_password(req.password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="Błędny email lub hasło")
    return _user_payload(db, user)


@app.get("/api/user/{user_id}")
def api_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika")
    return _user_payload(db, user)


class PreferencesRequest(BaseModel):
    user_id: int
    genres: list[str] | None = None
    mood: str | None = None


@app.put("/api/preferences")
def api_preferences(req: PreferencesRequest, db: Session = Depends(get_db)):
    if not db.get(models.User, req.user_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika")
    pref = db.scalar(
        select(models.UserPreference).where(models.UserPreference.user_id == req.user_id)
    )
    if not pref:
        pref = models.UserPreference(user_id=req.user_id, genres="[]")
        db.add(pref)
    if req.genres is not None:
        pref.genres = json.dumps(req.genres)
    if req.mood is not None:
        pref.mood = req.mood
    db.commit()
    return {"status": "ok"}


# ── Biblioteka i interakcje ──────────────────────────────────────


class LibraryRequest(BaseModel):
    user_id: int
    movie_id: int
    rating: int | None = None


@app.post("/api/library")
def api_library_add(req: LibraryRequest, db: Session = Depends(get_db)):
    """Dodaje tytuł do biblioteki lub aktualizuje ocenę gwiazdkową."""
    if not db.get(models.User, req.user_id) or not db.get(models.Movie, req.movie_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika lub filmu")
    item = db.scalar(
        select(models.LibraryItem).where(
            models.LibraryItem.user_id == req.user_id,
            models.LibraryItem.movie_id == req.movie_id,
        )
    )
    if not item:
        item = models.LibraryItem(user_id=req.user_id, movie_id=req.movie_id)
        db.add(item)
    if req.rating is not None:
        item.rating = req.rating
    db.commit()
    return {"status": "ok"}


@app.get("/api/library/{user_id}")
def api_library(user_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika")
    rows = db.execute(
        select(models.LibraryItem, models.Movie)
        .join(models.Movie, models.LibraryItem.movie_id == models.Movie.id)
        .where(models.LibraryItem.user_id == user_id)
        .order_by(models.LibraryItem.added_at.desc())
    ).all()
    items = [
        {
            "movie_id": m.id,
            "title": m.title,
            "year": m.year,
            "genres": m.genres,
            "rating": item.rating,
        }
        for item, m in rows
    ]
    return {"library": items}


class InteractionRequest(BaseModel):
    user_id: int
    movie_id: int
    action: str  # accept / reject
    reason: str | None = None
    aspects: list[str] | None = None  # co się podoba (dla accept)
    mood: str | None = None


@app.post("/api/interactions")
def api_interaction(req: InteractionRequest, db: Session = Depends(get_db)):
    if not db.get(models.User, req.user_id) or not db.get(models.Movie, req.movie_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika lub filmu")
    db.add(
        models.Interaction(
            user_id=req.user_id,
            movie_id=req.movie_id,
            action=req.action,
            reason=req.reason,
            aspects=json.dumps(req.aspects) if req.aspects else None,
            mood=req.mood,
        )
    )
    db.commit()
    return {"status": "ok"}
