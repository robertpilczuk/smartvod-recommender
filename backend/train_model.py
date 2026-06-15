"""Trening modelu przewidywania oceny użytkownik-film (Etap 5).

Model: regresja liniowa (scikit-learn) na czterech cechach zbudowanych z danych
MovieLens. Lookupy (średnie użytkownika, filmu, gatunkowe) liczone są tylko na
zbiorze treningowym, żeby nie przeciekały do testu.

Uruchomienie:
    python train_model.py
Zapisuje artefakt modelu do backend/model/recommender.pkl i wypisuje metryki.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

import database

MODEL_DIR = Path(__file__).resolve().parent / "model"
MODEL_PATH = MODEL_DIR / "recommender.pkl"
SMOOTH_VOTES = 50  # próg wygładzania średniej filmu (jak w baseline)
RANDOM_STATE = 42

FEATURES = ["user_mean", "movie_wr", "genre_affinity", "movie_pop"]


def load_frames():
    eng = database.engine
    ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", eng)
    movies = pd.read_sql("SELECT id, genres FROM movies", eng)
    return ratings, movies


def build_lookups(train, movie_genres, global_mean):
    """Średnie liczone na zbiorze treningowym."""
    user_mean = train.groupby("user_id")["rating"].mean()

    agg = train.groupby("movie_id")["rating"].agg(["mean", "count"])
    movie_wr = (
        agg["count"] / (agg["count"] + SMOOTH_VOTES) * agg["mean"]
        + SMOOTH_VOTES / (agg["count"] + SMOOTH_VOTES) * global_mean
    )
    movie_count = agg["count"]

    # Średnia ocena użytkownika per gatunek: rozbijamy oceny po gatunkach filmu
    exploded = train.merge(movie_genres, left_on="movie_id", right_on="id")
    exploded = exploded.explode("genre_list")
    user_genre_mean = exploded.groupby(["user_id", "genre_list"])["rating"].mean()

    return user_mean, movie_wr, movie_count, user_genre_mean


def genre_affinity_vector(df, movie_genres_map, user_genre_mean, user_mean, global_mean):
    """Dla każdej oceny: średnia (po gatunkach filmu) ocen użytkownika dla tych gatunków."""
    ug = user_genre_mean.to_dict()
    um = user_mean.to_dict()
    out = np.empty(len(df), dtype=float)
    uids = df["user_id"].to_numpy()
    mids = df["movie_id"].to_numpy()
    for i in range(len(df)):
        uid = uids[i]
        genres = movie_genres_map.get(mids[i], [])
        vals = [ug[(uid, g)] for g in genres if (uid, g) in ug]
        if vals:
            out[i] = sum(vals) / len(vals)
        else:
            out[i] = um.get(uid, global_mean)
    return out


def build_features(df, lookups, movie_genres_map, global_mean):
    user_mean, movie_wr, movie_count, user_genre_mean = lookups
    feats = pd.DataFrame(index=df.index)
    feats["user_mean"] = df["user_id"].map(user_mean).fillna(global_mean)
    feats["movie_wr"] = df["movie_id"].map(movie_wr).fillna(global_mean)
    feats["genre_affinity"] = genre_affinity_vector(
        df, movie_genres_map, user_genre_mean, user_mean, global_mean
    )
    feats["movie_pop"] = np.log1p(df["movie_id"].map(movie_count).fillna(0))
    return feats[FEATURES]


def main():
    print("Wczytywanie danych z bazy...")
    ratings, movies = load_frames()

    movies["genre_list"] = movies["genres"].str.split("|")
    movie_genres = movies[["id", "genre_list"]]
    movie_genres_map = dict(zip(movies["id"], movies["genre_list"]))

    train, test = train_test_split(ratings, test_size=0.2, random_state=RANDOM_STATE)
    global_mean = float(train["rating"].mean())
    print(f"Train: {len(train)}  Test: {len(test)}  srednia globalna: {global_mean:.4f}")

    print("Budowa lookupow (tylko train)...")
    lookups = build_lookups(train, movie_genres, global_mean)

    print("Budowa cech...")
    X_train = build_features(train, lookups, movie_genres_map, global_mean)
    X_test = build_features(test, lookups, movie_genres_map, global_mean)
    y_train, y_test = train["rating"].to_numpy(), test["rating"].to_numpy()

    print("Trening regresji liniowej...")
    # Uczymy na tablicy numpy (bez nazw kolumn), by predykcja na liscie cech nie ostrzegala
    model = LinearRegression()
    model.fit(X_train.to_numpy(), y_train)

    pred = np.clip(model.predict(X_test.to_numpy()), 1, 5)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    base_pred = np.full_like(y_test, global_mean, dtype=float)
    base_rmse = np.sqrt(mean_squared_error(y_test, base_pred))
    base_mae = mean_absolute_error(y_test, base_pred)

    print("\n=== Wyniki na zbiorze testowym ===")
    print(f"Baseline (srednia globalna): RMSE={base_rmse:.4f}  MAE={base_mae:.4f}")
    print(f"LinearRegression:            RMSE={rmse:.4f}  MAE={mae:.4f}  R2={r2:.4f}")
    print("Wspolczynniki:", dict(zip(FEATURES, np.round(model.coef_, 4))))

    user_mean, movie_wr, movie_count, user_genre_mean = lookups

    # Zapis jako natywne typy Pythona w zagnieżdżonym słowniku — szybkie wczytywanie.
    # Klucze-krotki o typach numpy odpicklowują się wolno, dlatego ich unikamy.
    ug_nested = {}
    for (uid, genre), val in user_genre_mean.items():
        ug_nested.setdefault(int(uid), {})[str(genre)] = float(val)

    artifact = {
        "model": model,
        "features": FEATURES,
        "global_mean": global_mean,
        "smooth_votes": SMOOTH_VOTES,
        "user_mean": {int(k): float(v) for k, v in user_mean.items()},
        "movie_wr": {int(k): float(v) for k, v in movie_wr.items()},
        "movie_count": {int(k): int(v) for k, v in movie_count.items()},
        "user_genre_mean": ug_nested,
        "movie_genres": {int(k): list(v) for k, v in movie_genres_map.items()},
        "metrics": {"rmse": rmse, "mae": mae, "r2": r2,
                    "baseline_rmse": base_rmse, "baseline_mae": base_mae},
    }
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(artifact, MODEL_PATH)
    print(f"\nModel zapisany: {MODEL_PATH}")


if __name__ == "__main__":
    main()
