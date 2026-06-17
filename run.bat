@echo off
REM Uruchamia backend (port 8000) i frontend (port 8080) w osobnych oknach (Windows).
REM Wymaga wczesniejszego przygotowania backendu (patrz docs/prezentacja.md).
cd /d "%~dp0"

if not exist "backend\venv\Scripts\uvicorn.exe" (
  echo Brak srodowiska backendu. W katalogu backend wykonaj:
  echo   python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
  pause
  exit /b 1
)

start "SmartVOD backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && uvicorn main:app --port 8000"
start "SmartVOD frontend" cmd /k "cd /d %~dp0frontend && python -m http.server 8080"

echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:8080
echo Zamknij oba okna, aby zatrzymac aplikacje.
