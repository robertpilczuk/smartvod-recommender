# Backend SmartVOD

API rekomendacji oparte na FastAPI. Dane filmowe pochodzą z MovieLens 1M.

## Uruchomienie lokalne

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Po uruchomieniu:

- API: http://127.0.0.1:8000
- sprawdzenie stanu: http://127.0.0.1:8000/api/health
- dokumentacja Swagger: http://127.0.0.1:8000/docs

## Import danych MovieLens 1M

Skrypt czyta `movies.dat`, `users.dat` i `ratings.dat` wprost z archiwum
`ml-1m.zip` i zapisuje je do bazy. Archiwum jest poza repozytorium (licencja).

```bash
python import_movielens.py                  # domyślnie ~/Downloads/ml-1m.zip
python import_movielens.py --zip /sciezka/ml-1m.zip
python import_movielens.py --reset          # usuwa dane MovieLens i importuje od nowa
```

Po imporcie baza zawiera 3883 filmy, 6040 użytkowników MovieLens i 1 000 209 ocen.

## Trening modelu

Model przewiduje ocenę użytkownik-film regresją liniową na czterech cechach
(średnia użytkownika, średnia ważona filmu, dopasowanie gatunkowe, popularność).
Wymaga zaimportowanych danych MovieLens.

```bash
python train_model.py
```

Zapisuje artefakt do `model/recommender.pkl` (poza repozytorium). Na zbiorze
testowym: baseline RMSE 1,12; regresja liniowa RMSE 0,93, MAE 0,73, R2 0,31.

## Konto demo

Skrypt zakłada konto demo z preferencjami i biblioteką ocenionych filmów
(do prezentacji). Wymaga zaimportowanych danych MovieLens.

```bash
python seed_demo.py
```

Logowanie: `demo@smartvod.pl` / `demo`. We frontendzie służy do tego przycisk
„Zaloguj jako demo" na ekranie logowania.

## Testy

Testy korzystają z osobnej bazy tymczasowej i nie wymagają wytrenowanego modelu.

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Endpointy

- `GET /api/health` zwraca `{"status": "ok"}`.
- `POST /api/recommend` zwraca rekomendacje. Body: `user_id`, `mood`, `genres`,
  `limit` (wszystkie opcjonalne). Wynik filmu to suma składników: przewidywana
  ocena z modelu (waga 2,0), genre_match (1,0), mood_match (1,0), popularity (0,5).
  Z propozycji odpadają tytuły z biblioteki i odrzucone. Dla nowego użytkownika
  (cold start) przewidywana ocena schodzi do wartości globalnej, a ranking
  napędzają dopasowanie gatunkowe i nastrój.

  ```bash
  curl -s -X POST http://127.0.0.1:8000/api/recommend \
    -H "Content-Type: application/json" \
    -d '{"genres":["Sci-fi"],"mood":"surprise","limit":5}'
  ```

Konto i dane użytkownika:

- `POST /api/register` zakłada konto (email, hasło, profil, gatunki) i zwraca profil.
- `POST /api/login` loguje po emailu i haśle, zwraca profil. Błędne dane: 401.
- `GET /api/user/{id}` zwraca profil z preferencjami (przywracanie sesji).
- `PUT /api/preferences` zapisuje gatunki i nastrój.
- `POST /api/library` dodaje tytuł do biblioteki lub ustawia ocenę gwiazdkową.
- `GET /api/library/{id}` zwraca bibliotekę z danymi filmów.
- `POST /api/interactions` zapisuje akcję (accept/reject). Dla akceptacji można
  przekazać `aspects` (co się podoba), dla odrzucenia `reason`; oba plus `mood`.

Logowanie jest na poziomie demonstracyjnym: hasło haszowane SHA-256 bez soli,
bez wymagań co do złożoności. Nie jest to mechanizm produkcyjny.

## Stan

Dostępny endpoint zdrowia, endpoint rekomendacji content-based, konfiguracja CORS
dla frontendu (porty 8080 i 5173) oraz baza SQLite z danymi MovieLens 1M.
