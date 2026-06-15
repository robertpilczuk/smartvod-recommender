"""Konto demo do prezentacji SmartVOD.

Zakłada (lub odświeża) konto demo z preferencjami i biblioteką ocenionych
filmów, żeby od razu było co pokazać. Wymaga zaimportowanych danych MovieLens.

Uruchomienie:
    python seed_demo.py
Konto: demo@smartvod.pl / demo
"""

import json

from sqlalchemy import delete, select

import auth
import database
import models

DEMO_EMAIL = "demo@smartvod.pl"
DEMO_PASSWORD = "demo"
DEMO_FIRST_NAME = "Demo"
DEMO_GENRES = ["Sci-fi", "Dramat", "Komedia"]
DEMO_MOOD = "surprise"

# Tytuły MovieLens (zapis z przecinkiem) wraz z oceną gwiazdkową w bibliotece
DEMO_LIBRARY = [
    ("Matrix, The", 5),
    ("Shawshank Redemption, The", 5),
    ("Back to the Future", 4),
    ("Forrest Gump", 5),
    ("Godfather, The", 5),
    ("Toy Story", 4),
]


def main():
    database.init_db()
    db = database.SessionLocal()
    try:
        if db.scalar(select(models.Movie).limit(1)) is None:
            raise SystemExit("Brak danych MovieLens. Uruchom najpierw: python import_movielens.py")

        user = db.scalar(select(models.User).where(models.User.email == DEMO_EMAIL))
        if user is None:
            user = models.User(source="app", email=DEMO_EMAIL, first_name=DEMO_FIRST_NAME)
            db.add(user)
            db.flush()
        user.password_hash = auth.hash_password(DEMO_PASSWORD)

        # Czyścimy poprzednie dane demo, żeby skrypt był idempotentny
        db.execute(delete(models.LibraryItem).where(models.LibraryItem.user_id == user.id))
        db.execute(delete(models.Interaction).where(models.Interaction.user_id == user.id))
        db.execute(delete(models.UserPreference).where(models.UserPreference.user_id == user.id))

        db.add(models.UserPreference(
            user_id=user.id, genres=json.dumps(DEMO_GENRES), mood=DEMO_MOOD,
        ))

        added = 0
        for title, rating in DEMO_LIBRARY:
            movie = db.scalar(select(models.Movie).where(models.Movie.title == title))
            if movie is None:
                print(f"  pomijam (brak w bazie): {title}")
                continue
            db.add(models.LibraryItem(user_id=user.id, movie_id=movie.id, rating=rating))
            db.add(models.Interaction(user_id=user.id, movie_id=movie.id, action="accept", mood=DEMO_MOOD))
            added += 1

        db.commit()
        print(f"Konto demo gotowe: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"  preferencje: {DEMO_GENRES}, nastrój: {DEMO_MOOD}")
        print(f"  biblioteka: {added} tytułów")
    finally:
        db.close()


if __name__ == "__main__":
    main()
