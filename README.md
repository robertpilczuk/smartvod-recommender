# SmartVOD Recommender

Aplikacja webowa do rekomendacji treści filmowych i serialowych z elementami
personalizacji opartej na preferencjach użytkownika. Projekt nie streamuje treści —
pełni rolę doradcy i agregatora, wskazując, na której platformie VOD dostępny jest
wybrany tytuł.

Projekt zaliczeniowy — **Praktyka zawodowa (Warsztaty)**, Lubelska Akademia WSEI,
Wydział Transportu i Informatyki, kierunek Informatyka.

Zespół projektowy: **Robert Pilczuk** i **Mateusz Pichur**.
Prowadzący: mgr inż. Tomasz Piętas.

## Zawartość repozytorium

```
.
├── frontend/                                   — aplikacja (frontend SPA)
│   ├── index.html                              — struktura 8 ekranów
│   ├── css/style.css                           — stylowanie, design tokens, responsywność
│   ├── js/app.js                               — logika SPA, dobór rekomendacji, stan
│   └── README.md                               — opis aplikacji i instrukcja uruchomienia
├── backend/                                     — API FastAPI, baza i moduł rekomendacji
│   ├── main.py                                 — endpointy REST
│   ├── recommend.py / predict.py               — rekomendacje i model oceny
│   ├── import_movielens.py / train_model.py    — import danych i trening
│   └── seed_demo.py                            — konto demo
├── run.sh                                       — uruchomienie backendu i frontendu
├── zrzuty/                                      — zrzuty ekranu i diagramy do dokumentacji
├── dokumentacja_smartvod_Robert_Pilczuk.docx   — dokumentacja (część wspólna + zakres R. Pilczuka)
├── dokumentacja_smartvod_Mateusz_Pichur.docx   — dokumentacja (część wspólna + zakres M. Pichura)
├── prezentacja_smartvod.pptx                   — prezentacja projektu (10–12 min)
└── dokumentacja_smartvod.docx                  — wstępna wersja dokumentacji (materiał źródłowy)
```

## Uruchomienie aplikacji

### Pełna aplikacja (backend + frontend)

Przygotowanie backendu (jednorazowo):

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python import_movielens.py      # import MovieLens 1M (wymaga ~/Downloads/ml-1m.zip)
python train_model.py           # trening modelu
python seed_demo.py             # konto demo do prezentacji
```

Uruchomienie backendu i frontendu jedną komendą:

```bash
./run.sh
# Backend:  http://127.0.0.1:8000
# Frontend: http://127.0.0.1:8080
```

Konto demo: `demo@smartvod.pl` / `demo` (przycisk „Zaloguj jako demo").
Szczegóły backendu i endpointów opisuje `backend/README.md`.

### Sam frontend (tryb demo, bez backendu)

Frontend działa też samodzielnie z lokalnym katalogiem filmów:

```bash
cd frontend
python3 -m http.server 8080
# następnie: http://127.0.0.1:8080
```

## Podział pracy

- **Robert Pilczuk** — koncepcja systemu, analiza wymagań, mechanizm rekomendacji,
  model sygnałów odrzuceń, projekt schematu bazy danych, logika aplikacji (`app.js`),
  testowanie, dokumentacja końcowa.
- **Mateusz Pichur** — projekt UI/UX (makiety w Figmie), system wizualny,
  struktura HTML, stylowanie CSS, responsywność, wstępna wersja dokumentacji.

Szczegółowy zakres pracy każdej z osób opisano w rozdziale 6 odpowiedniej dokumentacji.
