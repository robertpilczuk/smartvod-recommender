"""Przewidywanie oceny użytkownik-film na podstawie wytrenowanego modelu (Etap 5).

Artefakt modelu (model/recommender.pkl) powstaje przez train_model.py.
Funkcja predict_rating buduje wektor cech identycznie jak podczas treningu
i zwraca przewidywaną ocenę w skali 1-5.

Cold start:
- nieznany użytkownik  -> średnia użytkownika zastąpiona średnią globalną,
- nieznany film        -> średnia filmu zastąpiona średnią globalną.
"""

import math
import os
from pathlib import Path

import joblib
import numpy as np

# Ścieżkę modelu można nadpisać zmienną SMARTVOD_MODEL (używane w testach).
MODEL_PATH = Path(os.environ.get("SMARTVOD_MODEL") or Path(__file__).resolve().parent / "model" / "recommender.pkl")

_artifact = None


def _load():
    global _artifact
    if _artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Brak modelu: {MODEL_PATH}. Uruchom najpierw: python train_model.py"
            )
        _artifact = joblib.load(MODEL_PATH)
    return _artifact


def is_ready():
    return MODEL_PATH.exists()


def _features(art, user_id, movie_id):
    gmean = art["global_mean"]
    user_mean = art["user_mean"].get(user_id, gmean)
    movie_wr = art["movie_wr"].get(movie_id, gmean)
    movie_count = art["movie_count"].get(movie_id, 0)

    genres = art["movie_genres"].get(movie_id, [])
    ug = art["user_genre_mean"].get(user_id, {})
    vals = [ug[g] for g in genres if g in ug]
    genre_affinity = sum(vals) / len(vals) if vals else user_mean

    return [user_mean, movie_wr, genre_affinity, math.log1p(movie_count)]


def predict_rating(user_id, movie_id):
    art = _load()
    x = _features(art, user_id, movie_id)
    pred = float(art["model"].predict([x])[0])
    return max(1.0, min(5.0, pred))


def predict_ratings(user_id, movie_ids):
    """Przewiduje oceny użytkownika dla wielu filmów jednym wywołaniem modelu.

    Zwraca słownik {movie_id: ocena 1-5}.
    """
    art = _load()
    if not movie_ids:
        return {}
    matrix = np.array([_features(art, user_id, mid) for mid in movie_ids])
    preds = np.clip(art["model"].predict(matrix), 1.0, 5.0)
    return {mid: float(p) for mid, p in zip(movie_ids, preds)}
