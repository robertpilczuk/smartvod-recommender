from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    """Użytkownik aplikacji oraz użytkownik MovieLens.

    Rozróżnia ich kolumna source: 'app' (konto z logowaniem) lub 'movielens'
    (dane demograficzne do trenowania modelu, bez logowania).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(16), default="app", index=True)

    # Konto aplikacji
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    birthdate: Mapped[str | None] = mapped_column(String(10))  # YYYY-MM-DD

    # Dane demograficzne (MovieLens: M/F, kubełek wieku, kod zawodu, kod pocztowy)
    gender: Mapped[str | None] = mapped_column(String(1))
    age: Mapped[int | None] = mapped_column()
    occupation: Mapped[int | None] = mapped_column()
    zip_code: Mapped[str | None] = mapped_column(String(16))

    created_at: Mapped[datetime] = mapped_column(default=_now)

    ratings: Mapped[list["Rating"]] = relationship(back_populates="user")
    preferences: Mapped["UserPreference | None"] = relationship(back_populates="user")
    interactions: Mapped[list["Interaction"]] = relationship(back_populates="user")
    library_items: Mapped[list["LibraryItem"]] = relationship(back_populates="user")


class Movie(Base):
    """Film z katalogu MovieLens 1M."""

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)  # MovieID z MovieLens
    title: Mapped[str] = mapped_column(String(255), index=True)
    year: Mapped[int | None] = mapped_column()
    genres: Mapped[str] = mapped_column(String(255), default="")  # gatunki rozdzielone |

    ratings: Mapped[list["Rating"]] = relationship(back_populates="movie")


class Rating(Base):
    """Ocena film-użytkownik w skali 1-5 (dane MovieLens oraz oceny aplikacji)."""

    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_rating_user_movie"),
        # Indeks pokrywający przyspiesza agregację średniej i liczby ocen per film
        Index("ix_ratings_movie_rating", "movie_id", "rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), index=True)
    rating: Mapped[int] = mapped_column()
    timestamp: Mapped[int | None] = mapped_column()  # unix time z MovieLens
    created_at: Mapped[datetime] = mapped_column(default=_now)

    user: Mapped["User"] = relationship(back_populates="ratings")
    movie: Mapped["Movie"] = relationship(back_populates="ratings")


class UserPreference(Base):
    """Preferencje z onboardingu: wybrane gatunki i ostatni nastrój."""

    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    genres: Mapped[str] = mapped_column(Text, default="[]")  # lista gatunków jako JSON
    mood: Mapped[str | None] = mapped_column(String(32))
    updated_at: Mapped[datetime] = mapped_column(default=_now, onupdate=_now)

    user: Mapped["User"] = relationship(back_populates="preferences")


class Interaction(Base):
    """Akcja użytkownika na rekomendacji: akceptacja lub odrzucenie z powodem."""

    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), index=True)
    action: Mapped[str] = mapped_column(String(16))  # accept / reject
    reason: Mapped[str | None] = mapped_column(String(32))  # not-today / actor / watched / genre
    aspects: Mapped[str | None] = mapped_column(Text)  # co się podoba (lista cech jako JSON, dla accept)
    mood: Mapped[str | None] = mapped_column(String(32))  # nastrój w chwili akcji
    created_at: Mapped[datetime] = mapped_column(default=_now)

    user: Mapped["User"] = relationship(back_populates="interactions")


class LibraryItem(Base):
    """Tytuł zapisany w bibliotece użytkownika wraz z oceną gwiazdkową 1-5."""

    __tablename__ = "library_items"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_library_user_movie"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), index=True)
    rating: Mapped[int | None] = mapped_column()  # ocena 1-5, null jeśli tylko zapisany
    added_at: Mapped[datetime] = mapped_column(default=_now)

    user: Mapped["User"] = relationship(back_populates="library_items")
