# SmartVOD Recommender. Frontend

Jednostronicowa aplikacja (SPA) w czystym HTML, CSS i JavaScript, bez frameworków
i bez procesu budowania. Komunikuje się z backendem przez REST (`js/api.js`),
a gdy backend jest niedostępny, działa na lokalnym katalogu filmów (tryb demo).

Projekt zaliczeniowy. Praktyka zawodowa (Warsztaty), Lubelska Akademia WSEI.

## Uruchomienie

```bash
python3 -m http.server 8080
# następnie: http://127.0.0.1:8080
```

Backend uruchamia się osobno (patrz `../backend/README.md`) albo razem przez
`../run.sh`. Bez backendu działa tryb lokalny.

## Struktura plików

```
frontend/
├── index.html      struktura dokumentu i ekrany aplikacji
├── css/style.css   stylowanie, zmienne CSS, responsywność
├── js/api.js       klient REST do backendu
├── js/app.js       nawigacja SPA, dobór rekomendacji, stan
└── tests/          testy (node --test)
```

## Przepływ

1. Rejestracja lub logowanie (konto demo: `demo@smartvod.pl` / `demo`).
2. Ekran główny z trzema wejściami: Wybierz nastrój, Podpowiedz film, Zaskocz mnie.
   Nastrój nie jest wymuszany przy każdej sesji.
3. Rekomendacje (pięć propozycji z powodami). Dla każdej: Chcę obejrzeć (panel
   co Ci się podoba) albo Odrzuć (z powodem). Po decyzji pojawia się kolejna.
4. Biblioteka: tytuły Do obejrzenia i Ocenione, ocena gwiazdkowa po obejrzeniu,
   statystyki gustu. Modal Gdzie obejrzeć pokazuje platformy VOD (dane demo).

Stan konta (identyfikator użytkownika) jest utrwalany w localStorage.

## Testy

```bash
node --test tests/*.test.mjs
```

Testy obejmują klienta `api.js` (zamockowany fetch) i czyste funkcje `app.js`.

## Tryb podglądu (parametry URL)

```
index.html?demo=1&screen=screen-recommendations
index.html?demo=1&screen=screen-recommendations&modal=accept
index.html?demo=1&screen=screen-recommendations&modal=reject
```

- `demo=1` przykładowy profil i preferencje (tryb lokalny)
- `screen=<id>` otwarcie wskazanego ekranu
- `modal=accept|reject|where` otwarcie modala
