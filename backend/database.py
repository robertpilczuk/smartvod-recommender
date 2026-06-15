from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Plik bazy leży w katalogu backend (poza repozytorium, zawiera dane MovieLens)
DB_PATH = Path(__file__).resolve().parent / "smartvod.db"
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
