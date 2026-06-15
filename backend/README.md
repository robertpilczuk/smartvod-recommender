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

## Stan

Dostępny jest endpoint `GET /api/health` zwracający `{"status": "ok"}`,
konfiguracja CORS dla frontendu (porty 8080 i 5173) oraz baza SQLite z danymi
MovieLens 1M.
