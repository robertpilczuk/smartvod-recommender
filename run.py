#!/usr/bin/env python3
"""SmartVOD — jedno polecenie do uruchomienia całości (macOS, Linux, Windows).

    python run.py            # przygotuj wszystko (jeśli trzeba) i uruchom aplikację
    python run.py --reset    # zbuduj bazę i model od zera, potem uruchom
    python run.py --setup    # tylko przygotowanie, bez uruchamiania serwerów

Skrypt jest idiotoodporny: przy pierwszym uruchomieniu sam tworzy środowisko
Pythona, instaluje zależności, pobiera zbiór MovieLens 1M z oficjalnego serwera
GroupLens, importuje go do bazy, trenuje model i zakłada konto demo. Przy kolejnych
uruchomieniach pomija kroki, które są już gotowe, i od razu startuje serwery.

Używa wyłącznie biblioteki standardowej, więc działa zanim powstanie środowisko
wirtualne. Cała praca na danych odbywa się w środowisku w backend/venv.
"""

import argparse
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / "venv"
DATA = BACKEND / "data"
ZIP_PATH = DATA / "ml-1m.zip"
MODEL_PATH = BACKEND / "model" / "recommender.pkl"

# Oficjalny zbiór MovieLens 1M (GroupLens). Pobierany lokalnie — nie redystrybuujemy
# pliku przez repozytorium, każdy użytkownik ściąga go ze źródła zgodnie z licencją.
MOVIELENS_URL = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"

BACKEND_PORT = 8000
FRONTEND_PORT = 8080
IS_WINDOWS = os.name == "nt"


def venv_python() -> Path:
    """Ścieżka do interpretera Pythona w środowisku wirtualnym backendu."""
    return VENV / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


def step(msg: str) -> None:
    print(f"\n\033[1m▶ {msg}\033[0m" if not IS_WINDOWS else f"\n> {msg}")


def run_py(args, **kwargs) -> subprocess.CompletedProcess:
    """Uruchamia interpreter z venv w katalogu backendu (tam żyją skrypty i baza)."""
    return subprocess.run([str(venv_python()), *args], cwd=str(BACKEND), **kwargs)


def ensure_venv() -> None:
    """Tworzy venv i instaluje zależności, jeśli ich brakuje."""
    if not venv_python().exists():
        step("Tworzę środowisko Pythona (backend/venv)…")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)

    uvicorn = VENV / ("Scripts/uvicorn.exe" if IS_WINDOWS else "bin/uvicorn")
    if not uvicorn.exists():
        step("Instaluję zależności (pip install -r requirements.txt)…")
        run_py(["-m", "pip", "install", "--upgrade", "pip"], check=True)
        run_py(["-m", "pip", "install", "-r", "requirements.txt"], check=True)
    else:
        print("✓ Zależności już zainstalowane.")


def ensure_dataset() -> None:
    """Pobiera ml-1m.zip z serwera GroupLens, jeśli nie ma go lokalnie."""
    if ZIP_PATH.exists() and ZIP_PATH.stat().st_size > 1_000_000:
        print("✓ Zbiór MovieLens już pobrany.")
        return
    step(f"Pobieram zbiór MovieLens 1M z {MOVIELENS_URL}…")
    DATA.mkdir(parents=True, exist_ok=True)

    def progress(block, block_size, total):
        if total > 0:
            pct = min(100, block * block_size * 100 // total)
            print(f"\r  {pct:3d}%", end="", flush=True)

    try:
        urllib.request.urlretrieve(MOVIELENS_URL, ZIP_PATH, progress)
        print("\r  100%")
    except Exception as exc:  # noqa: BLE001  — chcemy czytelny komunikat dla użytkownika
        raise SystemExit(
            f"\nNie udało się pobrać zbioru: {exc}\n"
            f"Pobierz ręcznie {MOVIELENS_URL} i zapisz jako {ZIP_PATH}, "
            f"potem uruchom ponownie."
        )


def movie_count() -> int:
    """Liczba filmów w bazie (0, gdy baza pusta lub nie istnieje)."""
    code = (
        "import database, models;"
        "from sqlalchemy import select, func;"
        "database.init_db();"
        "db = database.SessionLocal();"
        "print(db.scalar(select(func.count()).select_from(models.Movie)))"
    )
    res = run_py(["-c", code], capture_output=True, text=True)
    try:
        return int(res.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0


def ensure_database(reset: bool) -> None:
    """Importuje MovieLens do bazy, jeśli baza jest pusta (lub przy --reset)."""
    if reset:
        step("Reset bazy (--reset): usuwam smartvod.db…")
        (BACKEND / "smartvod.db").unlink(missing_ok=True)
    if movie_count() > 0:
        print("✓ Dane w bazie już zaimportowane.")
        return
    # Zbiór potrzebny dopiero teraz — pobieramy go tylko gdy faktycznie importujemy.
    ensure_dataset()
    step("Importuję MovieLens 1M do bazy (chwilę to potrwa)…")
    run_py(["import_movielens.py", "--zip", str(ZIP_PATH)], check=True)


def ensure_model(reset: bool) -> None:
    """Trenuje model, jeśli artefaktu brak (lub przy --reset)."""
    if reset:
        MODEL_PATH.unlink(missing_ok=True)
    if MODEL_PATH.exists():
        print("✓ Model już wytrenowany.")
        return
    step("Trenuję model regresji liniowej…")
    run_py(["train_model.py"], check=True)


def ensure_demo() -> None:
    """Zakłada/odświeża konto demo (operacja idempotentna)."""
    step("Przygotowuję konto demo (demo@smartvod.pl / demo)…")
    run_py(["seed_demo.py"], check=True)


def launch() -> None:
    """Uruchamia backend (8000) i frontend (8080), otwiera przeglądarkę."""
    step("Startuję serwery…")
    backend = subprocess.Popen(
        [str(venv_python()), "-m", "uvicorn", "main:app", "--port", str(BACKEND_PORT)],
        cwd=str(BACKEND),
    )
    frontend = subprocess.Popen(
        [str(venv_python()), "-m", "http.server", str(FRONTEND_PORT), "--directory", str(FRONTEND)],
    )
    url = f"http://127.0.0.1:{FRONTEND_PORT}/index.html"
    print(f"\n  Backend:  http://127.0.0.1:{BACKEND_PORT}")
    print(f"  Frontend: {url}")
    print("  Konto demo: demo@smartvod.pl / demo")
    print("\n  Zatrzymanie: Ctrl+C")
    time.sleep(2)
    webbrowser.open(url)
    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\nZatrzymuję serwery…")
    finally:
        for proc in (backend, frontend):
            proc.terminate()


def main() -> None:
    parser = argparse.ArgumentParser(description="Uruchom SmartVOD jednym poleceniem.")
    parser.add_argument("--reset", action="store_true", help="zbuduj bazę i model od zera")
    parser.add_argument("--setup", action="store_true", help="tylko przygotowanie, bez uruchamiania")
    args = parser.parse_args()

    print("SmartVOD — przygotowanie i uruchomienie")
    ensure_venv()
    ensure_database(args.reset)
    ensure_model(args.reset)
    ensure_demo()

    if args.setup:
        print("\n✓ Gotowe. Uruchom aplikację poleceniem: python run.py")
        return
    launch()


if __name__ == "__main__":
    main()
