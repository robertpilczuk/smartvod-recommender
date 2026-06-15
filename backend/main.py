from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

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
