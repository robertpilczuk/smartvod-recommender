# SmartVOD Recommender. Scenariusz prezentacji

Dokument dla prowadzącego pokaz (Mateusz). Zawiera instrukcję uruchomienia na
Windows, scenariusz krok po kroku z gotowym tekstem do czytania oraz mapę
pokrycia wymagań projektu. Czas pokazu: około 10 minut.

Konto demo: `demo@smartvod.pl` / hasło `demo`.

---

## 1. Uruchomienie na Windows

### Wymagania wstępne

- Python 3.11 lub nowszy (zaznacz „Add Python to PATH" przy instalacji).
- Plik danych `ml-1m.zip` w folderze Pobrane (`%USERPROFILE%\Downloads\ml-1m.zip`).
- Przeglądarka (Chrome lub Edge).

### Przygotowanie backendu (jednorazowo)

Otwórz wiersz polecenia (cmd) w folderze projektu i wykonaj:

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python import_movielens.py --zip "%USERPROFILE%\Downloads\ml-1m.zip"
python train_model.py
python seed_demo.py
cd ..
```

Import i trening trwają kilka minut (raz). Po nich baza ma 3 883 filmy,
6 040 użytkowników i 1 000 209 ocen, a model jest zapisany.

### Uruchomienie aplikacji

Najprościej dwuklikiem na `run.bat` w folderze projektu. Otworzą się dwa okna
(backend i frontend). Backend wstaje kilkanaście sekund, w jego oknie pojawi się
`Application startup complete`.

Alternatywnie, ręcznie w dwóch oknach cmd:

```bat
REM Okno 1 (backend)
cd backend
venv\Scripts\activate
uvicorn main:app --port 8000

REM Okno 2 (frontend)
cd frontend
python -m http.server 8080
```

Następnie w przeglądarce otwórz: `http://127.0.0.1:8080`

### Przed samą prezentacją (checklista)

1. Uruchom `run.bat`, poczekaj na `Application startup complete` w oknie backendu.
2. Otwórz `http://127.0.0.1:8080`, kliknij „Zaloguj jako demo", sprawdź, że wchodzi.
3. Wejdź w „Moja biblioteka" i raz kliknij „Naucz na moich ocenach", żeby zobaczyć,
   że ekran profilu się wczytuje. Potem wróć na start. Demonstracja gotowa.
4. Gdyby port był zajęty: zamknij stare okna albo zmień port (np. `--port 8001`).

---

## 2. Scenariusz prezentacji (z tekstem do czytania)

Każdy krok ma: co zrobić na ekranie, tekst do powiedzenia (kursywą) i które
wymaganie projektu pokrywa.

### Krok 1. Wprowadzenie (ekran startowy)

Pokaż stronę startową aplikacji.

> „SmartVOD Recommender to aplikacja, która pomaga wybrać film lub serial spośród
> wielu platform streamingowych. Nie streamuje treści, pełni rolę doradcy i
> agregatora. Pod spodem działa moduł uczenia maszynowego wytrenowany na zbiorze
> MovieLens 1M, czyli na milionie rzeczywistych ocen filmów. Pokażemy pełną
> ścieżkę użytkownika, od logowania, przez rekomendacje, po uczenie modelu na
> ocenach użytkownika."

Pokrywa: cel i koncepcja projektu.

### Krok 2. Logowanie i konto użytkownika

Na ekranie logowania kliknij „Zaloguj jako demo".

> „Aplikacja ma rejestrację i logowanie. Konta są zapisywane w bazie danych, a
> hasła haszowane. Dla pokazu korzystamy z przygotowanego konta demo, które ma już
> preferencje i kilka ocenionych tytułów. Przy normalnej rejestracji użytkownik
> przechodzi dodatkowo onboarding, czyli wybór ulubionych gatunków."

Pokrywa: rejestracja i logowanie, konta w bazie, onboarding preferencji.

### Krok 3. Ekran główny i tryby doboru

Pokaż ekran główny z trzema kafelkami.

> „Po zalogowaniu trafiamy na ekran główny. Użytkownik decyduje, jak chce dobrać
> film. Wybierz nastrój dopasowuje propozycje do nastroju. Podpowiedz film
> korzysta z zapisanych gatunków. Niespodzianka losuje tytuły z całego katalogu,
> do eksploracji. Nastrój nie jest narzucany przy każdej sesji."

Pokrywa: personalizacja, różne ścieżki doboru.

### Krok 4. Dobór po nastroju

Kliknij „Wybierz nastrój", wybierz na przykład „Adrenalina", potem „Pokaż
rekomendacje".

> „Wybieram nastrój Adrenalina. Nastrój działa jak filtr gatunków, więc dostaniemy
> filmy z dreszczykiem: thrillery, horrory, kino akcji. Dla innego nastroju, na
> przykład Wzrusz mnie, system pokaże dramaty i romanse."

Pokrywa: dobór po nastroju, dopasowanie treści.

### Krok 5. Rekomendacje i wyjaśnienia

Pokaż pięć kart. Wskaż listę powodów pod tytułem każdego filmu.

> „To są rekomendacje. Dla każdego filmu model przewiduje, jak użytkownik go oceni,
> a pod tytułem widać krótkie uzasadnienie: wysoka przewidywana ocena, zgodność z
> gatunkiem, dopasowanie do nastroju. To jest moduł sztucznej inteligencji oparty
> na regresji liniowej. Rekomendacje są więc nie tylko trafne, ale i wytłumaczalne."

Pokrywa: rekomendacje, moduł ML, wyjaśnialność wyników.

### Krok 6. Wybór filmu i zbieranie preferencji

Na jednej karcie kliknij „Chcę obejrzeć". W panelu zaznacz na przykład Gatunek i
Klimat, kliknij „Zapisz i dalej". Pokaż, że na miejsce karty wchodzi nowy film.

> „Kiedy film mnie interesuje, klikam Chcę obejrzeć i zaznaczam, co konkretnie mi
> się podoba: gatunek, klimat, obsada, fabuła. Te sygnały zapisujemy. Tytuł trafia
> do biblioteki, a na jego miejsce od razu pojawia się kolejna propozycja, więc
> przeglądanie jest płynne i nie kończy się po pięciu filmach."

Pokrywa: akceptacja, zbieranie preferencji, ciągłość rekomendacji.

### Krok 7. Odrzucenie z powodem

Na innej karcie kliknij znak odrzucenia, wybierz powód, na przykład „Już to
widziałem".

> „Film można też odrzucić, podając powód. To również sygnał dla systemu. Tytuły
> odrzucone i już obejrzane nie wracają w kolejnych propozycjach."

Pokrywa: odrzucanie z powodem, filtrowanie historii.

### Krok 8. Tryb Niespodzianka

Wróć na ekran główny, kliknij „Niespodzianka". Potem wróć i kliknij jeszcze raz,
pokazując inny zestaw.

> „Tryb Niespodzianka losuje pięć filmów z całego katalogu i przy każdym wejściu
> daje inny zestaw. To opcja na eksplorację, kiedy nie mamy konkretnego pomysłu."

Pokrywa: eksploracja, różnorodność propozycji.

### Krok 9. Biblioteka, oceny i statystyki

Przejdź do „Moja biblioteka". Pokaż sekcje „Do obejrzenia" i „Ocenione". Wystaw
gwiazdki przy jednym tytule. Wskaż kafelki statystyk u góry.

> „W bibliotece tytuły dzielą się na te do obejrzenia i już ocenione. Ocenę
> gwiazdkową wystawiamy po obejrzeniu. U góry są statystyki gustu: liczba
> zapisanych i obejrzanych tytułów, średnia ocena i ulubiony gatunek. Wszystkie
> liczone na bieżąco z prawdziwych danych użytkownika."

Pokrywa: biblioteka, oceny po obejrzeniu, statystyki.

### Krok 10. Uczenie modelu i profil gustu (punkt kluczowy)

W bibliotece kliknij „Naucz na moich ocenach". Przejdź na ekran profilu. Pokaż
podsumowanie gustu i karuzelę propozycji w zielonych ramkach. Dodaj jedną do
biblioteki przyciskiem.

> „Teraz najważniejsze: model uczy się na ocenach użytkownika. Po kliknięciu
> system liczy z naszych ocen średnią i preferencje gatunkowe, i aktualizuje nasz
> profil. Dostajemy podsumowanie gustu oraz karuzelę filmów, które najprawdopodobniej
> polubimy, wyróżnionych zieloną ramką jako podpowiedzi modelu. Po nauczeniu
> przewidywane oceny dla naszego konta realnie rosną, bo system zna już nasz gust.
> Każdy z tych tytułów można od razu dodać do biblioteki."

Pokrywa: uczenie maszynowe na danych użytkownika, personalizacja, prezentacja wyników.

### Krok 11. Dostępność na platformach VOD

Kliknij plakat dowolnego filmu, pokaż okno „Gdzie obejrzeć".

> „Dla każdego tytułu pokazujemy, na których platformach jest dostępny. W tej
> wersji dane o dostępności są demonstracyjne, ale to właśnie ta funkcja czyni z
> aplikacji agregatora, a nie kolejny serwis streamingowy."

Pokrywa: agregacja dostępności VOD.

### Krok 12. Architektura i jakość (slajd lub krótkie omówienie)

> „Od strony technicznej to aplikacja full-stack. Frontend w czystym HTML, CSS i
> JavaScript rozmawia przez REST z backendem w FastAPI. Dane trzymamy w bazie
> SQLite, model zbudowaliśmy w bibliotece scikit-learn. Trenowaliśmy go na zbiorze
> MovieLens 1M. Model to regresja liniowa przewidująca ocenę, z błędem RMSE około
> 0,93, wyraźnie lepszym od prostego baseline'u. Backend udostępnia dziewięć
> endpointów REST, a całość jest pokryta testami: 27 testów backendu i 14 testów
> frontendu."

Pokrywa: wymagania techniczne, model i dane, testy i jakość.

### Krok 13. Podsumowanie

> „Pokazaliśmy pełną ścieżkę: od logowania, przez dobór po nastroju i gatunkach, z
> wyjaśnialnymi rekomendacjami, po zbieranie preferencji, bibliotekę z ocenami i
> uczenie modelu na danych użytkownika. Projekt łączy działający interfejs z
> realnym modułem uczenia maszynowego. Dziękujemy."

---

## 3. Mapa pokrycia wymagań

| Wymaganie | Gdzie w pokazie |
|-----------|-----------------|
| Rejestracja i logowanie | Krok 2 |
| Onboarding preferencji (gatunki) | Krok 2 (wzmianka), pełny przy rejestracji |
| Personalizacja, nastrój | Kroki 3 i 4 |
| Rekomendacje | Kroki 5 i 6 |
| Moduł AI/ML (regresja) | Kroki 5, 10, 12 |
| Wyjaśnialność rekomendacji | Krok 5 |
| Odrzucenia z powodem | Krok 7 |
| Eksploracja | Krok 8 |
| Biblioteka i oceny | Krok 9 |
| Statystyki gustu | Krok 9 |
| Uczenie na danych użytkownika | Krok 10 |
| Dostępność VOD | Krok 11 |
| Architektura, baza, testy | Krok 12 |

---

## 4. Gdyby coś nie zadziałało (plan B)

- Backend nie wstaje (port zajęty): zamknij stare okna konsoli albo uruchom backend
  na innym porcie (`uvicorn main:app --port 8001`) i otwórz aplikację mimo to.
  Frontend ma tryb lokalny, więc sam interfejs i nawigacja działają bez backendu.
- Strona pokazuje stare zachowanie: odśwież z czyszczeniem pamięci podręcznej
  (Ctrl+F5).
- „Naucz na moich ocenach" zgłasza brak ocen: wejdź do biblioteki i wystaw kilka
  gwiazdek, potem powtórz.
- Rekomendacje się nie ładują: sprawdź, czy w oknie backendu jest
  `Application startup complete`. Pierwsze uruchomienie po starcie bywa wolniejsze.
