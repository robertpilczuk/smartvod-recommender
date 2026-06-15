"""Import danych MovieLens 1M do bazy SmartVOD.

Czyta movies.dat, users.dat i ratings.dat wprost z archiwum ml-1m.zip
i zapisuje je do tabel movies, users (source='movielens') oraz ratings.

Uruchomienie:
    python import_movielens.py                      # domyślnie ~/Downloads/ml-1m.zip
    python import_movielens.py --zip /sciezka/ml-1m.zip
    python import_movielens.py --reset              # najpierw usuwa dane MovieLens
"""

import argparse
import re
import zipfile
from pathlib import Path

from sqlalchemy import delete, func, select, text

import database
import models

DEFAULT_ZIP = Path.home() / "Downloads" / "ml-1m.zip"
ENCODING = "latin-1"
SEP = "::"
BATCH = 20000

TITLE_YEAR = re.compile(r"^(.*?)\s*\((\d{4})\)\s*$")


def _rows(zf, name):
    """Zwraca wiersze pliku .dat z archiwum, rozbite po separatorze ::."""
    with zf.open(f"ml-1m/{name}") as fh:
        for raw in fh:
            line = raw.decode(ENCODING).rstrip("\n")
            if line:
                yield line.split(SEP)


def _parse_title(raw_title):
    m = TITLE_YEAR.match(raw_title)
    if m:
        return m.group(1), int(m.group(2))
    return raw_title, None


def import_movies(db, zf):
    rows = [
        {"id": int(mid), "title": title, "year": year, "genres": genres}
        for mid, raw_title, genres in _rows(zf, "movies.dat")
        for title, year in [_parse_title(raw_title)]
    ]
    db.bulk_insert_mappings(models.Movie, rows)
    db.commit()
    return len(rows)


def import_users(db, zf):
    rows = [
        {
            "id": int(uid),
            "source": "movielens",
            "gender": gender,
            "age": int(age),
            "occupation": int(occ),
            "zip_code": zip_code,
        }
        for uid, gender, age, occ, zip_code in _rows(zf, "users.dat")
    ]
    db.bulk_insert_mappings(models.User, rows)
    db.commit()
    return len(rows)


def import_ratings(db, zf):
    total = 0
    batch = []
    for uid, mid, rating, ts in _rows(zf, "ratings.dat"):
        batch.append(
            {
                "user_id": int(uid),
                "movie_id": int(mid),
                "rating": int(rating),
                "timestamp": int(ts),
            }
        )
        if len(batch) >= BATCH:
            db.bulk_insert_mappings(models.Rating, batch)
            db.commit()
            total += len(batch)
            batch = []
    if batch:
        db.bulk_insert_mappings(models.Rating, batch)
        db.commit()
        total += len(batch)
    return total


def reset_movielens(db):
    """Usuwa dane MovieLens (oceny, filmy, użytkowników movielens). Konta aplikacji zostają."""
    db.execute(delete(models.Rating))
    db.execute(delete(models.Movie))
    db.execute(delete(models.User).where(models.User.source == "movielens"))
    db.commit()


def already_imported(db):
    return db.scalar(select(func.count()).select_from(models.Movie)) > 0


def main():
    parser = argparse.ArgumentParser(description="Import MovieLens 1M do bazy SmartVOD")
    parser.add_argument("--zip", type=Path, default=DEFAULT_ZIP, help="ścieżka do ml-1m.zip")
    parser.add_argument("--reset", action="store_true", help="usuń dane MovieLens przed importem")
    args = parser.parse_args()

    if not args.zip.exists():
        raise SystemExit(f"Nie znaleziono archiwum: {args.zip}")

    database.init_db()
    db = database.SessionLocal()
    try:
        if args.reset:
            reset_movielens(db)
        if already_imported(db):
            n = db.scalar(select(func.count()).select_from(models.Movie))
            raise SystemExit(
                f"Baza zawiera już {n} filmów. Użyj --reset, aby zaimportować od nowa."
            )

        # Szybszy zapis dużej liczby wierszy w SQLite
        db.execute(text("PRAGMA synchronous=OFF"))
        db.execute(text("PRAGMA journal_mode=MEMORY"))

        with zipfile.ZipFile(args.zip) as zf:
            print("Import filmów...")
            nm = import_movies(db, zf)
            print(f"  filmy: {nm}")
            print("Import użytkowników...")
            nu = import_users(db, zf)
            print(f"  użytkownicy: {nu}")
            print("Import ocen (to chwilę potrwa)...")
            nr = import_ratings(db, zf)
            print(f"  oceny: {nr}")

        print(f"Gotowe: {nm} filmów, {nu} użytkowników, {nr} ocen.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
