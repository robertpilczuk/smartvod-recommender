"""Baseline rekomendacji content-based (Etap 4).

Wynik filmu to suma trzech składników w skali zbliżonej do 0-1:
    final_score = W_POP * popularity + W_GENRE * genre_match + W_MOOD * mood_match

- popularity   — średnia ocena filmu wygładzona wzorem ważonym (IMDb), 0-1
- genre_match  — udział gatunków filmu zgodnych z preferencjami użytkownika, 0-1
- mood_match   — 1, gdy film trafia w gatunki przypisane nastrojowi, inaczej 0

Z kandydatów odpadają tytuły z biblioteki użytkownika i wcześniej odrzucone.
"""

from sqlalchemy import func, select

import models

# Wagi składników (dobrane eksploracyjnie, opis w dokumentacji)
W_POP = 1.0
W_GENRE = 1.5
W_MOOD = 1.0

# Minimalna liczba ocen, by film w ogóle był kandydatem
MIN_RATINGS = 20
# Próg wygładzania we wzorze ważonym (im wyższy, tym mocniej ściąga ku średniej globalnej)
SMOOTH_VOTES = 50

# Gatunek aplikacji (PL) -> gatunki MovieLens (EN)
GENRE_MAP = {
    "Komedia": {"Comedy"},
    "Horror": {"Horror"},
    "Sci-fi": {"Sci-Fi"},
    "Thriller": {"Thriller"},
    "Romans": {"Romance"},
    "Akcja": {"Action", "Adventure"},
    "Dramat": {"Drama"},
    "Animacja": {"Animation"},
    "Dokumentalny": {"Documentary"},
    "Fantasy": {"Fantasy"},
    "Kryminał": {"Crime", "Film-Noir", "Mystery"},
    "Historyczny": {"War"},
    "Muzyczny": {"Musical"},
    "Familijny": {"Children's", "Animation"},
}

# Nastrój -> gatunki MovieLens (na podstawie opisów nastrojów w interfejsie)
MOOD_MAP = {
    "funny": {"Comedy"},
    "adrenaline": {"Thriller", "Horror", "Action"},
    "surprise": {"Sci-Fi", "Fantasy", "Mystery", "Adventure"},
    "moving": {"Drama", "Romance"},
    "inspire": {"Documentary", "War"},
    "calm": {"Comedy", "Drama", "Romance", "Children's", "Animation", "Musical"},
}

# Pamięć podręczna statystyk filmów: {movie_id: (avg, count)} oraz średnia globalna
_stats_cache = None
_global_mean = None


def _load_stats(db):
    """Liczy średnią ocenę i liczbę ocen dla każdego filmu (raz, potem z pamięci)."""
    global _stats_cache, _global_mean
    if _stats_cache is not None:
        return _stats_cache, _global_mean

    rows = db.execute(
        select(
            models.Rating.movie_id,
            func.avg(models.Rating.rating),
            func.count(models.Rating.rating),
        ).group_by(models.Rating.movie_id)
    ).all()
    _stats_cache = {mid: (float(avg), int(cnt)) for mid, avg, cnt in rows}
    _global_mean = (
        sum(avg for avg, _ in _stats_cache.values()) / len(_stats_cache)
        if _stats_cache
        else 3.5
    )
    return _stats_cache, _global_mean


def _weighted_rating(avg, count, mean):
    """Wzór ważony (IMDb): równoważy średnią filmu i średnią globalną wg liczby ocen."""
    return (count / (count + SMOOTH_VOTES)) * avg + (SMOOTH_VOTES / (count + SMOOTH_VOTES)) * mean


def _preferred_ml_genres(genres):
    """Zamienia listę gatunków aplikacji na zbiór gatunków MovieLens.

    Pusta lista lub 'Wszystko!' oznacza brak preferencji (neutralny składnik gatunkowy).
    """
    if not genres or "Wszystko!" in genres:
        return None
    out = set()
    for g in genres:
        out |= GENRE_MAP.get(g, set())
    return out or None


def _excluded_movie_ids(db, user_id):
    """Tytuły z biblioteki i wcześniej odrzucone, których nie proponujemy ponownie."""
    if user_id is None:
        return set()
    in_library = db.scalars(
        select(models.LibraryItem.movie_id).where(models.LibraryItem.user_id == user_id)
    ).all()
    rejected = db.scalars(
        select(models.Interaction.movie_id).where(
            models.Interaction.user_id == user_id,
            models.Interaction.action == "reject",
        )
    ).all()
    return set(in_library) | set(rejected)


def recommend(db, user_id=None, mood=None, genres=None, limit=5):
    # Gatunki: z żądania albo z zapisanych preferencji użytkownika
    if genres is None and user_id is not None:
        pref = db.scalar(
            select(models.UserPreference).where(models.UserPreference.user_id == user_id)
        )
        if pref:
            import json

            genres = json.loads(pref.genres or "[]")
            mood = mood or pref.mood

    pref_ml = _preferred_ml_genres(genres)
    mood_ml = MOOD_MAP.get(mood, set())
    excluded = _excluded_movie_ids(db, user_id)
    stats, mean = _load_stats(db)

    movies = db.execute(select(models.Movie)).scalars().all()
    scored = []
    for m in movies:
        if m.id in excluded:
            continue
        avg, count = stats.get(m.id, (0.0, 0))
        if count < MIN_RATINGS:
            continue

        movie_genres = set(m.genres.split("|")) if m.genres else set()

        popularity = (_weighted_rating(avg, count, mean) - 1.0) / 4.0
        if pref_ml is None:
            genre_match = 0.0
        else:
            genre_match = (
                len(movie_genres & pref_ml) / len(movie_genres) if movie_genres else 0.0
            )
        mood_match = 1.0 if (mood_ml and movie_genres & mood_ml) else 0.0

        score = W_POP * popularity + W_GENRE * genre_match + W_MOOD * mood_match
        scored.append(
            {
                "id": m.id,
                "title": m.title,
                "year": m.year,
                "genres": m.genres,
                "avg_rating": round(avg, 2),
                "rating_count": count,
                "score": round(score, 4),
                "components": {
                    "popularity": round(popularity, 4),
                    "genre_match": round(genre_match, 4),
                    "mood_match": mood_match,
                },
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]
