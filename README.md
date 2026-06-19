# SmartVOD Recommender

Aplikacja webowa do rekomendacji treści filmowych z elementami personalizacji
opartej na preferencjach użytkownika. Projekt nie streamuje treści — pełni rolę
doradcy i agregatora, wskazując, na której platformie VOD dostępny jest dany tytuł.

Projekt zaliczeniowy — **Praktyka zawodowa (Warsztaty)**, Lubelska Akademia WSEI,
Wydział Transportu i Informatyki, kierunek Informatyka.

Zespół: **Robert Pilczuk** i **Mateusz Pichur**. Prowadzący: mgr inż. Tomasz Piętas.

## Szybki start — jedno polecenie

Wymagania: **Python 3.10+** oraz połączenie z internetem (przy pierwszym
uruchomieniu pobierany jest zbiór danych). Nic więcej nie trzeba instalować ręcznie.

```bash
python run.py
```

To jedno polecenie działa identycznie na **macOS, Linux i Windows**. Przy pierwszym
uruchomieniu skrypt automatycznie:

1. tworzy środowisko Pythona (`backend/venv`) i instaluje zależności,
2. pobiera zbiór **MovieLens 1M** z oficjalnego serwera GroupLens,
3. importuje dane do bazy SQLite, trenuje model i zakłada konto demo,
4. uruchamia backend (port 8000) i frontend (port 8080) oraz otwiera przeglądarkę.

Kolejne uruchomienia pomijają gotowe kroki i od razu startują aplikację.

```bash
python run.py --reset   # zbuduj bazę i model od zera
python run.py --setup   # samo przygotowanie, bez startu serwerów
```

Wygodne skróty: `./run.sh` (macOS/Linux), `run.bat` (Windows, dwuklik) — oba wołają `run.py`.

Konto demo: `demo@smartvod.pl` / `demo` (przycisk „Zaloguj jako demo").

## Struktura repozytorium

```
.
├── run.py                    — jedno polecenie: przygotowanie + uruchomienie (mac/Win/Linux)
├── run.sh / run.bat          — wrappery na run.py
├── backend/                  — API FastAPI, baza SQLite i moduł rekomendacji
│   ├── main.py               — endpointy REST
│   ├── recommend.py          — logika rekomendacji (hybryda: model + gatunki + nastrój)
│   ├── predict.py            — model oceny i douczanie profilu użytkownika
│   ├── import_movielens.py   — import zbioru MovieLens 1M do bazy
│   ├── train_model.py        — trening modelu regresji liniowej
│   ├── seed_demo.py          — konto demo
│   ├── data/                 — pobrany ml-1m.zip (poza repo, patrz „Dane i licencja")
│   ├── tests/                — testy pytest
│   └── README.md             — opis backendu i endpointów
├── frontend/                 — aplikacja (HTML/CSS/JS, 9 ekranów)
│   ├── index.html            — struktura ekranów
│   ├── css/style.css         — design tokens, responsywność
│   ├── js/app.js             — logika SPA, dobór rekomendacji, stan
│   ├── js/api.js             — klient REST do backendu
│   └── tests/                — testy (wbudowany test runner Node)
└── docs/                     — architektura.md, prezentacja.md
```

Dokumentacja końcowa (`.docx`) i prezentacja (`.pptx`) są przekazywane osobno —
nie trzymamy ich w repozytorium (duże pliki binarne, oddawane prowadzącemu).

## Dane i licencja

Aplikacja używa zbioru **MovieLens 1M** (GroupLens, University of Minnesota).
Zgodnie z licencją GroupLens zbiór jest **wykorzystywany** do celów badawczych/
edukacyjnych, ale **nie jest redystrybuowany** przez to repozytorium — `run.py`
pobiera go bezpośrednio ze źródła przy pierwszym uruchomieniu i zapisuje w
`backend/data/` (katalog poza repo). Baza `smartvod.db` i artefakty modelu są
pochodnymi danych i również nie trafiają do repo — powstają lokalnie.

Źródło zbioru: <https://grouplens.org/datasets/movielens/1m/>

## Testy

```bash
# Backend (pytest, osobna baza tymczasowa, bez modelu)
backend/venv/bin/python -m pip install -r backend/requirements-dev.txt
cd backend && venv/bin/python -m pytest

# Frontend (wbudowany test runner Node, bez npm)
cd frontend && node --test tests/*.test.mjs
```

## Architektura

Aplikacja jest full-stack. Frontend (HTML, CSS, JavaScript) komunikuje się przez
REST z backendem FastAPI, który liczy rekomendacje na danych MovieLens 1M w SQLite.
Rekomendacja łączy przewidywaną ocenę z modelu regresji liniowej z dopasowaniem
gatunków, nastroju i popularnością filmu. Pełny opis: `docs/architektura.md`.

## Podział pracy

- **Robert Pilczuk** — koncepcja systemu, analiza wymagań, mechanizm rekomendacji,
  model sygnałów odrzuceń, projekt schematu bazy, logika aplikacji (`app.js`),
  testowanie, dokumentacja końcowa.
- **Mateusz Pichur** — projekt UI/UX (makiety w Figmie), system wizualny,
  struktura HTML, stylowanie CSS, responsywność, wstępna wersja dokumentacji.

Szczegółowy zakres pracy każdej osoby opisuje rozdział 6 odpowiedniej dokumentacji
końcowej (przekazywanej osobno, poza repozytorium).
