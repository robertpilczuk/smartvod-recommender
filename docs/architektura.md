# SmartVOD Recommender. Dokumentacja techniczna

Opis warstwy działającej aplikacji: architektury, danych, modelu rekomendacji
i ograniczeń. Dotyczy wersji full-stack (frontend, backend, baza, model).

## Architektura

Aplikacja składa się z trzech warstw.

- Frontend: jednostronicowa aplikacja w czystym HTML, CSS i JavaScript
  (`frontend/`). Plik `js/app.js` obsługuje nawigację po ekranach i stan sesji,
  a `js/api.js` komunikuje się z backendem przez REST. Stan konta (identyfikator
  użytkownika) trzymany jest w `localStorage`.
- Backend: API w FastAPI (`backend/main.py`). Logika rekomendacji jest w
  `recommend.py`, model oceny w `predict.py`, dostęp do bazy w `database.py`
  i `models.py`. Hasła obsługuje `auth.py`.
- Dane i model: baza SQLite (`smartvod.db`) z danymi MovieLens i kontami
  aplikacji oraz model zapisany w `model/recommender.pkl`.

Przepływ żądania rekomendacji:

```
przeglądarka (app.js) -> api.js -> POST /api/recommend -> recommend.py
   -> predict.py (model) + statystyki z bazy -> lista filmów z wynikiem i powodami
```

Endpointy REST:

- `GET /api/health` stan serwera.
- `POST /api/recommend` rekomendacje dla użytkownika lub preferencji.
- `POST /api/register`, `POST /api/login`, `GET /api/user/{id}` konto.
- `PUT /api/preferences` zapis gatunków i nastroju.
- `POST /api/library`, `GET /api/library/{id}` biblioteka i oceny.
- `POST /api/interactions` akceptacje (z zaznaczeniem co się podoba) i odrzucenia z powodem.

## Przepływ użytkownika

1. Rejestracja lub logowanie. Konto demo: `demo@smartvod.pl` / `demo`.
2. Przy rejestracji onboarding gatunków (można pominąć).
3. Ekran główny z trzema wejściami w sesję:
   - Wybierz nastrój: ekran nastroju, potem rekomendacje ograniczone do gatunków
     przypisanych nastrojowi (twardy filtr, patrz tabela niżej).
   - Podpowiedz film: rekomendacje na podstawie zapisanych gatunków, bez nastroju.
   - Niespodzianka: losowy zestaw filmów z katalogu, inny przy każdym wejściu.
   Nastrój nie jest wymuszany przy każdej sesji.

   Podział nastrój na gatunki MovieLens:

   | Nastrój | Gatunki |
   |---------|---------|
   | Rozśmiesz mnie | Comedy |
   | Adrenalina | Thriller, Horror, Action |
   | Zaskocz mnie | Sci-Fi, Fantasy, Mystery, Adventure |
   | Wzrusz mnie | Drama, Romance |
   | Zainspiruj mnie | Documentary, War |
   | Coś spokojnego | Comedy, Drama, Romance, Children's, Animation, Musical |

   Uwaga: wejście „Niespodzianka" na ekranie głównym losuje z całego katalogu i nie
   korzysta z tego podziału. Wiersz „Zaskocz mnie" w tabeli dotyczy nastroju
   wybieranego na ekranie nastroju.
4. Ekran rekomendacji pokazuje pięć propozycji z wynikiem i powodami. Dla każdej:
   - Chcę obejrzeć: panel co Ci się podoba (gatunek, klimat, obsada, fabuła).
     Tytuł trafia do biblioteki, a wybrane cechy zapisujemy jako interakcję.
   - Odrzuć: wybór powodu. Powód trafia do interakcji i wpływa na kolejne propozycje.
   Po każdej decyzji na miejscu karty pojawia się kolejna propozycja.
5. Biblioteka dzieli tytuły na Do obejrzenia i Ocenione. Ocenę gwiazdkową
   wystawia się po obejrzeniu, w bibliotece. Tu też widać statystyki gustu.

## Dane MovieLens 1M

Zbiór MovieLens 1M zawiera 1 000 209 ocen, 6 040 użytkowników i 3 883 filmy,
w skali ocen od 1 do 5. Pliki źródłowe (`movies.dat`, `users.dat`, `ratings.dat`)
mają separator `::` i kodowanie latin-1. Archiwum `ml-1m.zip` jest poza
repozytorium ze względu na licencję.

Import wykonuje `import_movielens.py`. Skrypt czyta pliki wprost z archiwum,
rozdziela tytuł i rok, dekoduje znaki i zapisuje dane do tabel `movies`, `users`
(z oznaczeniem `source = movielens`) oraz `ratings`. Gatunki w MovieLens są po
angielsku, dlatego aplikacja mapuje je na polskie etykiety przy wyświetlaniu.

Konta zakładane w aplikacji trafiają do tej samej tabeli `users` z oznaczeniem
`source = app`, więc ich identyfikatory nie kolidują z użytkownikami MovieLens.

## Model rekomendacji

### Przewidywanie oceny

Model przewiduje, jak użytkownik oceni film. Jest to regresja liniowa
(scikit-learn) na czterech cechach budowanych z danych MovieLens:

- średnia ocen użytkownika,
- średnia ważona ocen filmu (wzór ograniczający wpływ filmów z małą liczbą ocen),
- dopasowanie gatunkowe, czyli średnia ocen użytkownika dla gatunków danego filmu,
- popularność filmu (logarytm liczby ocen).

Lookupy liczone są tylko na zbiorze treningowym, żeby nie przeciekały do testu.
Podział danych to 80 procent treningu i 20 procent testu.

Wyniki na zbiorze testowym (200 042 ocen):

| Model | RMSE | MAE | R2 |
|-------|------|-----|----|
| Baseline (średnia globalna) | 1,1197 | 0,9360 | . |
| Regresja liniowa | 0,9287 | 0,7331 | 0,3121 |

Najsilniejszą cechą jest dopasowanie gatunkowe.

### Wynik hybrydowy

Końcowy wynik filmu łączy przewidywaną ocenę z sygnałami treściowymi:

```
final_score = 2,0 * pred_norm + 1,0 * genre_match + 1,0 * mood_match + 0,5 * popularity
```

- `pred_norm` to przewidywana ocena przeskalowana do zakresu 0 do 1,
- `genre_match` to udział gatunków filmu zgodnych z preferencjami,
- `mood_match` wynosi 1, gdy film trafia w gatunki przypisane nastrojowi,
- `popularity` to średnia ważona ocen filmu w zakresie 0 do 1.

Kandydatami są filmy z co najmniej 20 ocenami. Z propozycji odpadają tytuły
z biblioteki użytkownika i wcześniej odrzucone. Do każdej propozycji dołączane
są krótkie wyjaśnienia (pole `reasons`), na przykład zgodność z gatunkiem albo
wysoka przewidywana ocena.

### Cold start

Nowy użytkownik aplikacji nie występuje w danych treningowych modelu, więc jego
przewidywana ocena schodzi do wartości globalnej. Ranking napędzają wtedy
dopasowanie gatunkowe i nastrój wybrane podczas onboardingu.

## Ograniczenia

- Logowanie jest na poziomie demonstracyjnym. Hasło jest haszowane SHA-256 bez
  soli i bez wymagań co do złożoności. Nie jest to mechanizm produkcyjny.
- Wagi wyniku hybrydowego i próg liczby ocen dobrano eksploracyjnie. Mają
  charakter demonstracyjny, nie były strojone na osobnym zbiorze walidacyjnym.
- Model trenowany jest na danych MovieLens. Oceny i sygnały interakcji
  (akceptacje z zaznaczonymi cechami, odrzucenia z powodem) z kont aplikacji
  są zapisywane, ale nie powodują ponownego treningu modelu. Personalizacja
  dla nowych użytkowników opiera się na cold starcie i sygnałach treściowych.
- Mapowanie gatunków jest przybliżone. MovieLens nie ma osobnej kategorii
  historycznej, więc gatunek Historyczny mapowany jest na War.
- Dostępność na platformach VOD jest danymi demonstracyjnymi przypisywanymi
  stabilnie po identyfikatorze filmu. Aplikacja nie sprawdza realnej dostępności.
- Baza to pojedynczy plik SQLite, odpowiedni do prezentacji i jednego procesu.
- Start backendu trwa kilkanaście sekund z powodu wczytania modelu i statystyk.
  Po rozgrzewce odpowiedzi są szybkie.
