# SmartVOD Recommender

Aplikacja webowa do rekomendacji treści filmowych i serialowych z elementami
personalizacji opartej na preferencjach użytkownika. Prototyp frontendu (SPA)
zrealizowany w czystym HTML5/CSS3/JavaScript ES6+, bez zewnętrznych frameworków.

Projekt zaliczeniowy — Praktyka zawodowa (Warsztaty), Lubelska Akademia WSEI.

## Uruchomienie

Aplikacja nie wymaga backendu ani procesu budowania — wystarczy otworzyć
`index.html` w przeglądarce, albo uruchomić lokalny serwer:

```bash
python3 -m http.server 8080
# następnie: http://127.0.0.1:8080
```

## Struktura plików

```
smartvod/
├── index.html      — struktura dokumentu, znaczniki wszystkich 8 ekranów
├── css/
│   └── style.css   — pełne stylowanie, zmienne CSS (design tokens), responsywność
└── js/
    └── app.js      — logika nawigacji SPA, dobór rekomendacji, stan (localStorage)
```

## Funkcjonalności

- Rejestracja i logowanie z walidacją pól (prototyp — bez backendu).
- Onboarding: wybór preferencji spośród 15 gatunków.
- Sesja rekomendacyjna: wybór nastroju (6 opcji) i szacowanego czasu wolnego.
- 5 propozycji dobieranych metodą content-based: punktacja za zgodność
  z nastrojem (+3) i za każdy wspólny gatunek (+1), z bonusem za ocenę zbiorczą.
- Odrzucanie propozycji z 4 powodami: „nie dziś" działa jako sygnał tymczasowy
  (bieżąca sesja), pozostałe powody jako sygnał trwały. Odrzucone tytuły
  są zastępowane kolejnym najlepszym kandydatem.
- Ocenianie wybranych tytułów (1–5 gwiazdek) i zapis do biblioteki.
- Biblioteka ze statystykami wyliczanymi z rzeczywistych danych
  (liczba zapisanych, obejrzanych, średnia ocena, ulubiony gatunek).
- Modal „Gdzie obejrzeć" — dostępność tytułu na platformach VOD (dane statyczne).
- Stan użytkownika utrwalany w localStorage.

## Tryb podglądu (do testów i dokumentacji)

Parametry URL pozwalają otworzyć aplikację w zadanym stanie:

```
index.html?demo=1&screen=screen-recommendations&accept=2
index.html?demo=1&screen=screen-recommendations&modal=reject
index.html?demo=1&screen=screen-rate&accept=3&rated=1
```

- `demo=1` — przykładowy profil i preferencje
- `screen=<id>` — otwarcie wskazanego ekranu
- `accept=<n>` — akceptacja n pierwszych propozycji
- `modal=reject|where` — otwarcie modala
- `rated=1` — przykładowe oceny gwiazdkowe
