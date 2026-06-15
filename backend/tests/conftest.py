"""Wspólna konfiguracja testów backendu.

Ustawia tymczasową bazę i wyłącza model (tryb baseline) zanim zaimportujemy
aplikację, a następnie zasiewa kilka filmów, użytkowników i ocen.
"""

import os
import tempfile

# Musi być ustawione przed importem aplikacji (database odczytuje ścieżkę przy imporcie)
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".db")
os.environ["SMARTVOD_DB"] = _DB_PATH
os.environ["SMARTVOD_MODEL"] = "/nieistniejacy/recommender.pkl"

import pytest
from fastapi.testclient import TestClient

import database
import main
import models
import recommend

# Filmy testowe: różne gatunki i malejące średnie ocen (mid 1 -> 5, mid 5 -> 1)
MOVIES = [
    (1, "Test Sci-Fi", "Sci-Fi", 1990),
    (2, "Test Comedy", "Comedy", 1991),
    (3, "Test Drama", "Drama", 1992),
    (4, "Test Action", "Action|Adventure", 1993),
    (5, "Test Horror", "Horror", 1994),
]


def _seed(db):
    for mid, title, genres, year in MOVIES:
        db.add(models.Movie(id=mid, title=title, genres=genres, year=year))
    for uid in range(1, 31):
        db.add(models.User(id=uid, source="movielens", gender="M", age=25))
    # Każdy z 30 użytkowników ocenia każdy film (>= 20 ocen, by film był kandydatem)
    for uid in range(1, 31):
        for mid, *_ in MOVIES:
            db.add(models.Rating(user_id=uid, movie_id=mid, rating=max(1, 6 - mid)))
    db.commit()


@pytest.fixture
def client():
    database.init_db()
    db = database.SessionLocal()
    for M in (models.Rating, models.Interaction, models.LibraryItem,
              models.UserPreference, models.Movie, models.User):
        db.query(M).delete()
    db.commit()
    _seed(db)
    db.close()

    # Cache statystyk liczony na świeżych danych przy starcie aplikacji
    recommend._stats_cache = None
    recommend._global_mean = None

    with TestClient(main.app) as c:
        yield c
