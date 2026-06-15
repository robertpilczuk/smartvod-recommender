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

## Stan

Na ten moment dostępny jest endpoint `GET /api/health` zwracający `{"status": "ok"}`
oraz konfiguracja CORS dla frontendu uruchamianego na portach 8080 i 5173.
