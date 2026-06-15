import recommend


def test_preferred_ml_genres_mapping():
    assert recommend._preferred_ml_genres(["Sci-fi"]) == {"Sci-Fi"}
    assert "Crime" in recommend._preferred_ml_genres(["Kryminał"])
    # brak preferencji lub "Wszystko!" oznacza neutralny składnik gatunkowy
    assert recommend._preferred_ml_genres([]) is None
    assert recommend._preferred_ml_genres(["Wszystko!"]) is None


def test_weighted_rating_between_movie_and_global_mean():
    # Film z małą liczbą ocen jest ściągany ku średniej globalnej
    wr = recommend._weighted_rating(avg=5.0, count=10, mean=3.0)
    assert 3.0 < wr < 5.0


def test_build_reasons_uses_components():
    reasons = recommend._build_reasons(
        genres_pl=["Sci-fi"], mood="surprise", movie_genres={"Sci-Fi"},
        predicted_rating=4.6, avg=4.3, mood_match=1.0,
    )
    assert any("przewidywana" in r.lower() for r in reasons)
    assert any("Sci-fi" in r for r in reasons)
    assert any("nastroj" in r.lower() for r in reasons)
    assert len(reasons) <= 3


def test_build_reasons_fallback_when_nothing_matches():
    reasons = recommend._build_reasons(
        genres_pl=[], mood=None, movie_genres={"Drama"},
        predicted_rating=2.0, avg=2.5, mood_match=0.0,
    )
    assert reasons == ["Popularny tytuł dopasowany do profilu"]
