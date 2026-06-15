import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Plik bazy leży w katalogu backend (poza repozytorium, zawiera dane MovieLens).
# Ścieżkę można nadpisać zmienną SMARTVOD_DB (używane w testach).
DB_PATH = Path(os.environ.get("SMARTVOD_DB") or Path(__file__).resolve().parent / "smartvod.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False pozwala korzystać z połączenia w obsłudze żądań FastAPI
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Tworzy tabele na podstawie modeli, jeśli jeszcze nie istnieją."""
    import models  # noqa: F401  rejestruje modele w metadanych

    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate():
    """Dodaje kolumny brakujące w istniejącej bazie (create_all nie zmienia schematu)."""
    with engine.begin() as conn:
        cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(interactions)")]
        if "aspects" not in cols:
            conn.exec_driver_sql("ALTER TABLE interactions ADD COLUMN aspects TEXT")
