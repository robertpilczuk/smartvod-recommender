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
├── backend/                                     — API i moduł rekomendacji (w budowie)
├── zrzuty/                                      — zrzuty ekranu i diagramy do dokumentacji
├── dokumentacja_smartvod_Robert_Pilczuk.docx   — dokumentacja (część wspólna + zakres R. Pilczuka)
├── dokumentacja_smartvod_Mateusz_Pichur.docx   — dokumentacja (część wspólna + zakres M. Pichura)
├── prezentacja_smartvod.pptx                   — prezentacja projektu (10–12 min)
└── dokumentacja_smartvod.docx                  — wstępna wersja dokumentacji (materiał źródłowy)
```

## Uruchomienie aplikacji

Frontend nie wymaga procesu budowania — wystarczy otworzyć
`frontend/index.html` w przeglądarce albo uruchomić lokalny serwer:

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
