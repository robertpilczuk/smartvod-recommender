#!/bin/bash
# Uruchamia backend (port 8000) i frontend (port 8080) do prezentacji SmartVOD.
# Zatrzymanie: Ctrl+C (skrypt ubija oba procesy).

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ ! -x "$ROOT/backend/venv/bin/uvicorn" ]; then
  echo "Brak środowiska backendu. W katalogu backend wykonaj:"
  echo "  python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

"$ROOT/backend/venv/bin/uvicorn" main:app --app-dir "$ROOT/backend" --port 8000 &
BACK=$!
python3 -m http.server 8080 --directory "$ROOT/frontend" &
FRONT=$!

trap 'kill $BACK $FRONT 2>/dev/null' EXIT
echo "Backend:  http://127.0.0.1:8000"
echo "Frontend: http://127.0.0.1:8080"
echo "Zatrzymanie: Ctrl+C"
wait
