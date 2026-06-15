/* ════════════════════════════════════════════════════════════
   SmartVOD Recommender — app.js
   Logika nawigacji SPA, dobór rekomendacji (content-based),
   obsługa zdarzeń i trwały stan użytkownika (localStorage).
   ════════════════════════════════════════════════════════════ */

/* ── KATALOG TREŚCI (dane statyczne prototypu) ─────────────── */
const MOVIES = [
  { id: 1,  title: 'Oppenheimer',          year: 2023, genre: 'Dramat / Historia',        genres: ['Dramat', 'Historyczny'],   moods: ['moving', 'inspire'],          rating: 8.9, runtime: '3h',        emoji: '💥', bg: '#1a1215', platforms: ['Max', 'SkyShowtime'] },
  { id: 2,  title: 'Dune: Część 2',        year: 2024, genre: 'Sci-fi / Epicki',          genres: ['Sci-fi', 'Akcja'],         moods: ['surprise', 'adrenaline'],     rating: 8.5, runtime: '2h46m',     emoji: '🏜️', bg: '#1a130a', platforms: ['Max', 'Canal+'] },
  { id: 3,  title: 'The Bear',             year: 2024, genre: 'Dramat / Komedia',         genres: ['Dramat', 'Komedia'],       moods: ['moving', 'funny'],            rating: 8.6, runtime: '30–60 min', emoji: '🍳', bg: '#0f1a14', platforms: ['Disney+'] },
  { id: 4,  title: 'Poor Things',          year: 2023, genre: 'Fantasy / Czarna komedia', genres: ['Fantasy', 'Komedia'],      moods: ['surprise', 'funny'],          rating: 8.0, runtime: '2h21m',     emoji: '🌹', bg: '#0f0f1a', platforms: ['Disney+', 'SkyShowtime'] },
  { id: 5,  title: 'Civil War',            year: 2024, genre: 'Thriller / Dramat',        genres: ['Thriller', 'Dramat'],      moods: ['adrenaline'],                 rating: 7.3, runtime: '1h49m',     emoji: '📷', bg: '#141414', platforms: ['Apple TV+', 'Prime Video'] },
  { id: 6,  title: 'Shōgun',               year: 2024, genre: 'Dramat historyczny',       genres: ['Dramat', 'Historyczny'],   moods: ['moving', 'surprise'],         rating: 8.9, runtime: '60 min',    emoji: '⚔️', bg: '#150f0a', platforms: ['Disney+'] },
  { id: 7,  title: 'Alien: Romulus',       year: 2024, genre: 'Sci-fi / Horror',          genres: ['Sci-fi', 'Horror'],        moods: ['adrenaline'],                 rating: 7.4, runtime: '1h59m',     emoji: '👾', bg: '#0a1520', platforms: ['Disney+'] },
  { id: 8,  title: 'W głowie się nie mieści 2', year: 2024, genre: 'Animacja / Familijny', genres: ['Animacja', 'Familijny'], moods: ['funny', 'moving'],            rating: 7.8, runtime: '1h40m',     emoji: '🎭', bg: '#1a1225', platforms: ['Disney+'] },
  { id: 9,  title: 'Grand Budapest Hotel', year: 2014, genre: 'Komedia',                  genres: ['Komedia'],                 moods: ['funny', 'calm'],              rating: 8.1, runtime: '1h39m',     emoji: '🏨', bg: '#1a0f15', platforms: ['Disney+', 'Prime Video'] },
  { id: 10, title: 'Interstellar',         year: 2014, genre: 'Sci-fi / Dramat',          genres: ['Sci-fi', 'Dramat'],        moods: ['surprise', 'moving'],         rating: 8.7, runtime: '2h49m',     emoji: '🌌', bg: '#0a1220', platforms: ['Max', 'Prime Video'] },
  { id: 11, title: 'Parasite',             year: 2019, genre: 'Thriller / Czarna komedia', genres: ['Thriller', 'Dramat'],     moods: ['surprise', 'adrenaline'],     rating: 8.5, runtime: '2h12m',     emoji: '🏠', bg: '#101814', platforms: ['Max', 'Canal+'] },
  { id: 12, title: 'La La Land',           year: 2016, genre: 'Musical / Romans',         genres: ['Muzyczny', 'Romans'],      moods: ['moving', 'calm'],             rating: 8.0, runtime: '2h8m',      emoji: '🎷', bg: '#1a1408', platforms: ['Netflix', 'Max'] },
  { id: 13, title: 'Free Solo',            year: 2018, genre: 'Dokumentalny',             genres: ['Dokumentalny'],            moods: ['inspire', 'adrenaline'],      rating: 8.1, runtime: '1h40m',     emoji: '🧗', bg: '#14110a', platforms: ['Disney+'] },
  { id: 14, title: 'Ted Lasso',            year: 2023, genre: 'Komedia / Sport',          genres: ['Komedia'],                 moods: ['funny', 'calm', 'inspire'],   rating: 8.8, runtime: '30–45 min', emoji: '⚽', bg: '#0f1a10', platforms: ['Apple TV+'] },
  { id: 15, title: 'Planeta Ziemia III',   year: 2023, genre: 'Dokumentalny / Przyroda',  genres: ['Dokumentalny', 'Familijny'], moods: ['calm', 'inspire'],          rating: 9.0, runtime: '60 min',    emoji: '🌍', bg: '#0a141a', platforms: ['Max'] },
  { id: 16, title: 'Na noże',              year: 2019, genre: 'Kryminał / Komedia',       genres: ['Kryminał', 'Komedia'],     moods: ['funny', 'surprise'],          rating: 7.9, runtime: '2h10m',     emoji: '🔪', bg: '#140f0f', platforms: ['Netflix', 'Prime Video'] },
];

const GENRES = [
  { label: 'Komedia', icon: '😂' }, { label: 'Horror', icon: '👻' },
  { label: 'Sci-fi', icon: '🚀' }, { label: 'Thriller', icon: '🔪' },
  { label: 'Romans', icon: '💕' }, { label: 'Akcja', icon: '💥' },
  { label: 'Dramat', icon: '🎭' }, { label: 'Animacja', icon: '🎨' },
  { label: 'Dokumentalny', icon: '🎬' }, { label: 'Fantasy', icon: '🧙' },
  { label: 'Kryminał', icon: '🔍' }, { label: 'Historyczny', icon: '⚔️' },
  { label: 'Muzyczny', icon: '🎵' }, { label: 'Familijny', icon: '👨‍👩‍👧' },
  { label: 'Wszystko!', icon: '🌈' },
];

/* ── ADAPTER WYŚWIETLANIA FILMU MOVIELENS ──────────────────────
   Backend zwraca filmy z gatunkami po angielsku i bez oprawy wizualnej.
   Tu dorabiamy etykiety PL, emoji i kolor tła z gatunku oraz demonstracyjną
   dostępność VOD (statyczna, przypisywana stabilnie po id filmu). */
const GENRE_PL = {
  Action: 'Akcja', Adventure: 'Przygodowy', Animation: 'Animacja',
  "Children's": 'Familijny', Comedy: 'Komedia', Crime: 'Kryminał',
  Documentary: 'Dokumentalny', Drama: 'Dramat', Fantasy: 'Fantasy',
  'Film-Noir': 'Kryminał', Horror: 'Horror', Musical: 'Muzyczny',
  Mystery: 'Kryminał', Romance: 'Romans', 'Sci-Fi': 'Sci-fi',
  Thriller: 'Thriller', War: 'Wojenny', Western: 'Western',
};
const GENRE_EMOJI = {
  Action: '💥', Adventure: '🗺️', Animation: '🎨', "Children's": '👨‍👩‍👧',
  Comedy: '😂', Crime: '🔍', Documentary: '🎬', Drama: '🎭', Fantasy: '🧙',
  'Film-Noir': '🕵️', Horror: '👻', Musical: '🎵', Mystery: '🔎',
  Romance: '💕', 'Sci-Fi': '🚀', Thriller: '🔪', War: '⚔️', Western: '🤠',
};
const GENRE_BG = {
  Action: '#1a130a', Adventure: '#14110a', Animation: '#1a1225',
  "Children's": '#1a1408', Comedy: '#1a0f15', Crime: '#140f0f',
  Documentary: '#0a141a', Drama: '#1a1215', Fantasy: '#0f0f1a',
  'Film-Noir': '#101010', Horror: '#150a0a', Musical: '#1a1408',
  Mystery: '#101814', Romance: '#1a0f15', 'Sci-Fi': '#0a1220',
  Thriller: '#141414', War: '#150f0a', Western: '#14110a',
};
const DEMO_PLATFORMS = ['Netflix', 'Max', 'Disney+', 'Prime Video', 'Canal+', 'Apple TV+', 'SkyShowtime'];

function demoPlatforms(id) {
  // Stabilny wybór 1–2 platform na podstawie id (dane demonstracyjne)
  const a = DEMO_PLATFORMS[id % DEMO_PLATFORMS.length];
  const b = DEMO_PLATFORMS[(id * 3 + 1) % DEMO_PLATFORMS.length];
  return a === b ? [a] : [a, b];
}

function adaptMovie(apiMovie) {
  const enGenres = (apiMovie.genres || '').split('|').filter(Boolean);
  const primary = enGenres[0] || 'Drama';
  const plGenres = [...new Set(enGenres.map(g => GENRE_PL[g] || g))];
  return {
    id: apiMovie.id,
    title: apiMovie.title,
    year: apiMovie.year,
    genre: plGenres.join(' / ') || '—',
    genres: plGenres,
    rating: apiMovie.avg_rating,            // średnia ocen widzów (skala 1–5)
    predictedRating: apiMovie.predicted_rating,
    reasons: apiMovie.reasons || [],
    emoji: GENRE_EMOJI[primary] || '🎬',
    bg: GENRE_BG[primary] || '#141414',
    platforms: demoPlatforms(apiMovie.id),
  };
}

/* ── STAN APLIKACJI (trwały — localStorage) ────────────────── */
const STORAGE_KEY = 'smartvod_state';

// Przykładowa biblioteka startowa prototypu (oceny w skali 1–5)
const SEED_LIBRARY = [
  { id: 1, rating: 5 }, // Oppenheimer
  { id: 6, rating: 5 }, // Shōgun
  { id: 3, rating: 4 }, // The Bear
  { id: 4, rating: 4 }, // Poor Things
  { id: 2, rating: 5 }, // Dune: Część 2
];

const DEFAULT_STATE = {
  userId: null,             // id konta w backendzie (po rejestracji/logowaniu)
  profile: null,            // { firstName, lastName, email, gender, birthdate }
  genres: [],               // preferencje gatunkowe z onboardingu
  mood: null,               // nastrój wybrany przed sesją
  time: 'do 2h',            // szacowany czas wolny
  permanentRejects: [],     // odrzucenia trwałe (aktor / widziane / gatunek)
  library: SEED_LIBRARY,    // zapisane tytuły z ocenami
  sessionsCount: 7,
};

const SESSION_FETCH = 12;   // ile propozycji pobieramy (5 na ekran + zapas na podmiany)

let state = loadState();
let sessionRejects = [];    // odrzucenia tymczasowe („nie dziś") — tylko bieżąca sesja
let currentMovies = [];
let recommendationBuffer = []; // zapas propozycji do podmiany po decyzji
let libraryItems = [];      // ostatnio wyrenderowana biblioteka (do modala „gdzie obejrzeć")
let pendingRejectId = null;
let pendingAcceptId = null;
let sessionAdded = 0;       // liczba tytułów dodanych do biblioteki w bieżącej sesji
let activeScreen = 'screen-landing';

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return Object.assign({}, DEFAULT_STATE, JSON.parse(raw));
  } catch (e) { /* uszkodzony zapis — start od stanu domyślnego */ }
  return structuredClone(DEFAULT_STATE);
}

function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) { /* tryb prywatny */ }
}

/* ── NAWIGACJA SPA ─────────────────────────────────────────── */
const PRE_LOGIN_SCREENS = new Set(['screen-landing', 'screen-login', 'screen-register']);

function logoClick() {
  if (PRE_LOGIN_SCREENS.has(activeScreen)) {
    go('screen-login');
  } else {
    go('screen-library');
  }
}

function go(id) {
  activeScreen = id;
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
  if (id === 'screen-home') renderHome();
  if (id === 'screen-genres') renderGenres();
  if (id === 'screen-mood') renderMoodSelection();
  if (id === 'screen-recommendations') {
    renderContextLine();
    if (currentMovies.length === 0) {
      renderLoadingMovies();
      buildSession().then(renderMovies);
    } else {
      renderMovies();
    }
  }
  if (id === 'screen-library') renderLibrary();
}

/* ── REJESTRACJA / LOGOWANIE (prototyp frontendu) ──────────── */
function showError(elId, message) {
  const el = document.getElementById(elId);
  el.textContent = message;
  el.classList.add('visible');
}

function clearError(elId) {
  document.getElementById(elId).classList.remove('visible');
}

function validEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); }

async function submitRegister() {
  const firstName = document.getElementById('reg-firstname').value.trim();
  const lastName  = document.getElementById('reg-lastname').value.trim();
  const email     = document.getElementById('reg-email').value.trim();
  const password  = document.getElementById('reg-password').value;
  const gender    = document.getElementById('reg-gender').value;
  const birthdate = document.getElementById('reg-birthdate').value;

  if (!firstName)         return showError('register-error', 'Podaj swoje imię.');
  if (!validEmail(email)) return showError('register-error', 'Podaj poprawny adres e-mail.');
  if (!password)          return showError('register-error', 'Podaj hasło.');

  clearError('register-error');
  try {
    const user = await API.register({
      email, password,
      first_name: firstName, last_name: lastName,
      gender, birthdate, genres: state.genres,
    });
    state.userId = user.user_id;
    state.profile = { firstName: user.first_name || firstName, lastName, email, gender, birthdate };
    state.genres = user.genres || state.genres;
    saveState();
    go('screen-genres');
  } catch (e) {
    showError('register-error', e.message);
  }
}

async function submitLogin() {
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  if (!validEmail(email)) return showError('login-error', 'Podaj poprawny adres e-mail.');
  if (!password)          return showError('login-error', 'Podaj hasło.');

  clearError('login-error');
  try {
    const user = await API.login(email, password);
    state.userId = user.user_id;
    state.profile = {
      firstName: user.first_name || email.split('@')[0],
      lastName: user.last_name, email,
      gender: user.gender, birthdate: user.birthdate,
    };
    state.genres = user.genres || [];
    state.mood = user.mood || null;
    saveState();
    go('screen-home');
  } catch (e) {
    showError('login-error', e.message);
  }
}

// Logowanie na gotowe konto demo (do prezentacji)
async function demoLogin() {
  clearError('login-error');
  try {
    const user = await API.login('demo@smartvod.pl', 'demo');
    state.userId = user.user_id;
    state.profile = {
      firstName: user.first_name || 'Demo', lastName: user.last_name,
      email: user.email, gender: user.gender, birthdate: user.birthdate,
    };
    state.genres = user.genres || [];
    state.mood = user.mood || null;
    saveState();
    go('screen-home');
  } catch (e) {
    showError('login-error', 'Konto demo niedostępne. W backendzie uruchom: python seed_demo.py');
  }
}

/* ── EKRAN GŁÓWNY ──────────────────────────────────────────── */
function renderHome() {
  const greeting = document.getElementById('home-greeting');
  if (greeting) {
    greeting.textContent = state.profile?.firstName
      ? `Witaj, ${state.profile.firstName}`
      : 'Witaj w SmartVOD';
  }
}

/* ── ONBOARDING — GATUNKI ──────────────────────────────────── */
function genreCountLabel(n) {
  if (n === 1) return 'Wybrano: 1 gatunek';
  if (n >= 2 && n <= 4) return `Wybrano: ${n} gatunki`;
  return `Wybrano: ${n} gatunków`;
}

function renderGenres() {
  const grid = document.getElementById('genre-grid');
  grid.innerHTML = '';
  GENRES.forEach(g => {
    const chip = document.createElement('button');
    chip.className = 'chip' + (state.genres.includes(g.label) ? ' selected' : '');
    chip.innerHTML = `<span class="chip-icon">${g.icon}</span> ${g.label}`;
    chip.onclick = () => {
      chip.classList.toggle('selected');
      if (chip.classList.contains('selected')) {
        state.genres.push(g.label);
      } else {
        state.genres = state.genres.filter(x => x !== g.label);
      }
      saveState();
      document.getElementById('genre-count').textContent = genreCountLabel(state.genres.length);
    };
    grid.appendChild(chip);
  });
  document.getElementById('genre-count').textContent = genreCountLabel(state.genres.length);
}

// Zapis wybranych gatunków do backendu, potem przejście na ekran główny
async function proceedFromGenres() {
  if (state.userId) {
    try {
      await API.savePreferences({ user_id: state.userId, genres: state.genres });
    } catch (e) { /* brak połączenia — preferencje zostają lokalnie */ }
  }
  go('screen-home');
}

/* ── WYBÓR NASTROJU I CZASU ────────────────────────────────── */
function selectMood(el) {
  document.querySelectorAll('.mood-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  state.mood = el.dataset.mood;
  saveState();
}

function selectTime(el) {
  document.querySelectorAll('#time-chips .chip').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  state.time = el.textContent.trim();
  saveState();
}

function renderMoodSelection() {
  document.querySelectorAll('.mood-card').forEach(c => {
    c.classList.toggle('selected', c.dataset.mood === state.mood);
  });
  document.querySelectorAll('#time-chips .chip').forEach(c => {
    c.classList.toggle('selected', c.textContent.trim() === state.time);
  });
}

/* ── DOBÓR REKOMENDACJI (content-based) ────────────────────────
   Punktacja kandydata:
   +3  — zgodność z wybranym nastrojem,
   +1  — za każdy gatunek wspólny z preferencjami użytkownika,
   +r/10 — bonus za ocenę zbiorczą (tie-breaker).
   Wykluczone: tytuły z biblioteki, odrzucenia trwałe i sesyjne. */
function scoreMovie(m) {
  let score = m.rating / 10;
  if (state.mood && m.moods.includes(state.mood)) score += 3;
  if (state.genres.includes('Wszystko!')) {
    score += 1;
  } else {
    score += m.genres.filter(g => state.genres.includes(g)).length;
  }
  return score;
}

function candidatePool(excludeIds = []) {
  const libraryIds = new Set(state.library.map(x => x.id));
  return MOVIES
    .filter(m => !libraryIds.has(m.id))
    .filter(m => !state.permanentRejects.includes(m.id))
    .filter(m => !sessionRejects.includes(m.id))
    .filter(m => !excludeIds.includes(m.id))
    .sort((a, b) => scoreMovie(b) - scoreMovie(a) || Math.random() - 0.5);
}

// Parametry bieżącej sesji ustawiane przez wejścia z ekranu głównego / nastroju
let sessionParams = { mood: null, genres: [], surprise: false };

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

async function beginSession(params) {
  sessionParams = params;
  state.sessionsCount += 1;
  state.mood = params.mood;
  if (state.userId && params.mood) {
    try { await API.savePreferences({ user_id: state.userId, mood: params.mood }); } catch (e) { /* offline */ }
  }
  saveState();
  sessionRejects = [];
  sessionAdded = 0;
  currentMovies = [];        // pusty stan wymusi świeże pobranie w go()
  recommendationBuffer = [];
  go('screen-recommendations');
}

// Wejścia w sesję
function startSession() {                 // z ekranu nastroju
  beginSession({ mood: state.mood, genres: state.genres, surprise: false });
}
function startSuggest() {                  // „Podpowiedz film" (gatunki, bez nastroju)
  beginSession({ mood: null, genres: state.genres, surprise: false });
}
function startSurprise() {                 // „Zaskocz mnie" (poluzowane filtry)
  beginSession({ mood: null, genres: [], surprise: true });
}

async function buildSession() {
  const { mood, genres, surprise } = sessionParams;
  if (state.userId) {
    try {
      const data = await API.getRecommendations({
        user_id: state.userId, genres, mood, limit: surprise ? 30 : SESSION_FETCH,
      });
      let all = (data.recommendations || []).map(adaptMovie);
      if (surprise) all = shuffle(all);   // szeroki, mniej przewidywalny wachlarz
      currentMovies = all.slice(0, 5);
      recommendationBuffer = all.slice(5);
      return;
    } catch (e) {
      // brak połączenia z API — fallback do lokalnego katalogu (tryb demo/offline)
    }
  }
  currentMovies = candidatePool().slice(0, 5);
  recommendationBuffer = [];
}

function renderContextLine() {
  const days = ['Niedziela', 'Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota'];
  const now = new Date();
  const h = now.getHours();
  const part = h < 6 ? 'noc 🌙' : h < 12 ? 'rano ☀️' : h < 18 ? 'popołudnie 🌤' : 'wieczór 🌙';
  const moodLabel = sessionParams.mood
    ? (document.querySelector(`.mood-card[data-mood="${sessionParams.mood}"] .mood-label`)?.textContent || '')
    : '';
  const moodPart = moodLabel ? `nastrój: ${moodLabel} · ` : '';
  document.getElementById('context-line').textContent =
    `Na podstawie Twoich preferencji · ${moodPart}${days[now.getDay()]}, ${part}`;
}

/* ── EKRAN REKOMENDACJI ────────────────────────────────────── */
function renderLoadingMovies() {
  updateAddedCount();
  document.getElementById('movies-grid').innerHTML =
    '<p class="muted text-center" style="grid-column:1/-1;padding:40px 0;">Dobieramy rekomendacje…</p>';
}

function renderMovies() {
  updateAddedCount();
  const grid = document.getElementById('movies-grid');
  grid.innerHTML = '';
  if (currentMovies.length === 0) {
    grid.innerHTML = '<p class="muted text-center" style="grid-column:1/-1;padding:40px 0;">Brak dalszych propozycji w tej sesji.</p>';
    return;
  }
  currentMovies.forEach(movie => {
    const el = document.createElement('div');
    el.className = 'movie-card';
    el.id = `movie-${movie.id}`;
    const reasonsHtml = (movie.reasons && movie.reasons.length)
      ? `<ul class="movie-reasons">${movie.reasons.map(r => `<li>${r}</li>`).join('')}</ul>`
      : '';
    el.innerHTML = `
      <div class="movie-poster" style="background:${movie.bg}">
        <div class="movie-poster-bg">${movie.emoji}</div>
        <div class="movie-poster-gradient"></div>
      </div>
      <div class="movie-info">
        <div class="movie-title">${movie.title}</div>
        <div class="movie-meta">${movie.year ? movie.year + ' · ' : ''}${movie.genre}</div>
        <div class="movie-rating">
          <span class="star">★</span> ${movie.rating ?? '—'}
          &nbsp;·&nbsp; <span style="font-size:11px;color:var(--muted)">ocena widzów</span>
        </div>
        ${reasonsHtml}
      </div>
      <div class="movie-actions" style="flex-direction:column;">
        <div style="display:flex;gap:8px;">
          <button class="btn btn-primary btn-sm" style="flex:1;" onclick="openAcceptModal(${movie.id})">✓ Chcę obejrzeć</button>
          <button class="btn btn-outline btn-sm" onclick="openRejectModal(${movie.id})">✕</button>
        </div>
        <button class="btn btn-ghost btn-sm" style="padding:6px;font-size:12px;color:var(--gold);" onclick="openWhereModal(${movie.id})">📍 Gdzie obejrzeć?</button>
      </div>
    `;
    grid.appendChild(el);
  });
}

function updateAddedCount() {
  const el = document.getElementById('added-count');
  if (el) el.textContent = `Dodane: ${sessionAdded}`;
}

// Podmiana karty po decyzji (akceptacja albo odrzucenie) na następną propozycję
function advanceCard(id) {
  const idx = currentMovies.findIndex(m => m.id === id);
  if (idx === -1) return;
  const replacement = nextReplacement();
  if (replacement) {
    currentMovies[idx] = replacement;
  } else {
    currentMovies.splice(idx, 1); // brak kandydatów — usuń kartę bez zastępstwa
  }
  renderMovies();
}

/* ── AKCEPTACJA: co Ci się podoba ──────────────────────────── */
function openAcceptModal(id) {
  pendingAcceptId = id;
  const movie = currentMovies.find(m => m.id === id);
  document.getElementById('accept-movie-title').textContent = movie ? `„${movie.title}"` : '';
  document.querySelectorAll('#aspect-chips .chip').forEach(c => c.classList.remove('selected'));
  document.getElementById('accept-modal').classList.add('open');
}

function closeAcceptModal() {
  document.getElementById('accept-modal').classList.remove('open');
  pendingAcceptId = null;
}

function toggleAspect(el) {
  el.classList.toggle('selected');
}

function confirmAccept() {
  if (pendingAcceptId === null) return;
  const acceptedId = pendingAcceptId;
  const aspects = [...document.querySelectorAll('#aspect-chips .chip.selected')].map(c => c.dataset.aspect);
  closeAcceptModal();

  // Dodanie do biblioteki (bez oceny — ocena po obejrzeniu) i sygnał z cechami
  if (state.userId) {
    API.addToLibrary({ user_id: state.userId, movie_id: acceptedId }).catch(() => {});
    API.recordInteraction({
      user_id: state.userId, movie_id: acceptedId, action: 'accept', aspects, mood: state.mood,
    }).catch(() => { /* offline — sygnał zostaje lokalnie */ });
  } else if (!state.library.find(x => x.id === acceptedId)) {
    state.library.unshift({ id: acceptedId, rating: 0 });
    saveState();
  }

  sessionAdded += 1;
  const card = document.getElementById(`movie-${acceptedId}`);
  if (card) card.classList.add('accepted');
  setTimeout(() => advanceCard(acceptedId), 400);
}

/* ── ODRZUCANIE PROPOZYCJI (sygnały dla modelu) ────────────── */
function openRejectModal(id) {
  pendingRejectId = id;
  const movie = currentMovies.find(m => m.id === id);
  document.getElementById('modal-movie-title').textContent = `„${movie.title}"`;
  document.getElementById('reject-modal').classList.add('open');
}

function closeModal() {
  document.getElementById('reject-modal').classList.remove('open');
  pendingRejectId = null;
}

function rejectMovie(reason) {
  if (pendingRejectId === null) return;
  const rejectedId = pendingRejectId; // zachowaj id, bo closeModal() zeruje pendingRejectId
  closeModal();

  // „Nie dziś" = sygnał tymczasowy (sesja); pozostałe powody = sygnał trwały
  if (reason === 'not-today') {
    sessionRejects.push(rejectedId);
  } else if (!state.permanentRejects.includes(rejectedId)) {
    state.permanentRejects.push(rejectedId);
    saveState();
  }
  // Sygnał odrzucenia do backendu (bez blokowania UI)
  if (state.userId) {
    API.recordInteraction({
      user_id: state.userId, movie_id: rejectedId, action: 'reject', reason, mood: state.mood,
    }).catch(() => { /* offline — sygnał zostaje lokalnie */ });
  }

  const card = document.getElementById(`movie-${rejectedId}`);
  if (card) card.classList.add('rejected');

  setTimeout(() => advanceCard(rejectedId), 600);
}

// Następna propozycja na podmianę: najpierw z bufora API, w trybie demo z lokalnego katalogu
function nextReplacement() {
  const shownIds = new Set(currentMovies.map(m => m.id));
  while (recommendationBuffer.length) {
    const cand = recommendationBuffer.shift();
    if (!shownIds.has(cand.id) &&
        !state.permanentRejects.includes(cand.id) &&
        !sessionRejects.includes(cand.id)) {
      return cand;
    }
  }
  if (!state.userId) {
    return candidatePool([...shownIds])[0];
  }
  return null;
}

/* ── MODAL „GDZIE OBEJRZEĆ" ────────────────────────────────── */
function openWhereModal(id) {
  const movie = currentMovies.find(m => m.id === id)
    || libraryItems.find(m => m.id === id)
    || MOVIES.find(m => m.id === id);
  document.getElementById('where-title').textContent = movie.title;
  const container = document.getElementById('where-platforms');
  container.innerHTML = movie.platforms.map(p => `
    <div class="card flex items-center justify-between" style="padding:16px 20px;">
      <div style="font-weight:500;">${p}</div>
      <a href="#" style="color:var(--gold);font-size:14px;text-decoration:none;">Otwórz →</a>
    </div>
  `).join('');
  document.getElementById('where-modal').classList.add('open');
}

function closeWhereModal() {
  document.getElementById('where-modal').classList.remove('open');
}

/* ── BIBLIOTEKA I STATYSTYKI ───────────────────────────────── */
function libraryFromLocal() {
  return state.library
    .map(x => ({ ...MOVIES.find(m => m.id === x.id), myRating: x.rating }))
    .filter(x => x.id);
}

async function renderLibrary() {
  let items;
  if (state.userId) {
    try {
      const data = await API.getLibrary(state.userId);
      items = data.library.map(it => ({
        ...adaptMovie({ id: it.movie_id, title: it.title, year: it.year, genres: it.genres }),
        myRating: it.rating || 0,
      }));
    } catch (e) {
      items = libraryFromLocal();   // offline — z lokalnego stanu
    }
  } else {
    items = libraryFromLocal();
  }
  libraryItems = items;

  // Statystyki wyliczane z rzeczywistej zawartości biblioteki
  const rated = items.filter(x => x.myRating > 0);
  const avg = rated.length ? (rated.reduce((s, x) => s + x.myRating, 0) / rated.length).toFixed(1) : '—';
  const genreCounts = {};
  items.forEach(x => x.genres.forEach(g => { genreCounts[g] = (genreCounts[g] || 0) + 1; }));
  const favGenre = Object.entries(genreCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || '—';

  document.getElementById('stat-saved').textContent = items.length;
  document.getElementById('stat-watched').textContent = rated.length;
  document.getElementById('stat-avg').textContent = avg;
  document.getElementById('stat-genre').textContent = favGenre;

  const totalRatings = rated.length;
  document.getElementById('learn-text').textContent =
    `Na podstawie Twoich ${state.sessionsCount} sesji i ${totalRatings} ocen SmartVOD coraz lepiej rozumie Twój gust. Kolejne rekomendacje będą jeszcze trafniejsze.`;

  const greeting = document.getElementById('library-greeting');
  greeting.textContent = state.profile?.firstName
    ? `Zapisane tytuły i historia gustu — ${state.profile.firstName}`
    : 'Zapisane tytuły i historia Twojego gustu';

  // Dwie sekcje: tytuły do obejrzenia (bez oceny) i już ocenione
  const watchlist = items.filter(x => !(x.myRating > 0));
  const ratedItems = items.filter(x => x.myRating > 0);
  const section = (title, list) => list.length
    ? `<h3 class="mb-4">${title}</h3><div class="library-grid mb-8">${list.map(libraryCard).join('')}</div>`
    : '';
  const sections = document.getElementById('library-sections');
  sections.innerHTML = items.length
    ? section('Do obejrzenia', watchlist) + section('Ocenione', ratedItems)
    : '<p class="muted">Biblioteka jest pusta. Rozpocznij sesję, aby dodać tytuły.</p>';
}

// Karta biblioteki z interaktywną oceną gwiazdkową (ocena po obejrzeniu)
function libraryCard(item) {
  const stars = [1, 2, 3, 4, 5]
    .map(i => `<span class="s${i <= item.myRating ? ' lit' : ''}" onclick="rateLibraryItem(${item.id}, ${i})">★</span>`)
    .join('');
  return `
    <div class="movie-card">
      <div class="movie-poster" style="background:${item.bg};cursor:pointer;" onclick="openWhereModal(${item.id})">
        <div class="movie-poster-bg">${item.emoji}</div>
        <div class="movie-poster-gradient"></div>
      </div>
      <div class="movie-info">
        <div class="movie-title">${item.title}</div>
        <div class="movie-meta">${item.year || ''}</div>
        <div class="star-rating" title="Oceń po obejrzeniu">${stars}</div>
      </div>
    </div>`;
}

// Zapis oceny tytułu w bibliotece (po obejrzeniu)
async function rateLibraryItem(movieId, stars) {
  if (state.userId) {
    try { await API.addToLibrary({ user_id: state.userId, movie_id: movieId, rating: stars }); }
    catch (e) { /* offline — pomijamy */ }
  } else {
    const it = state.library.find(x => x.id === movieId);
    if (it) it.rating = stars;
    saveState();
  }
  renderLibrary();  // przelicza statystyki i przenosi tytuł do „Ocenione"
}

/* ── ZAMYKANIE MODALI KLIKNIĘCIEM W TŁO ────────────────────── */
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.classList.remove('open');
    }
  });
});

/* ── TRYB PODGLĄDU (parametry URL — do testów i dokumentacji) ─
   ?demo=1                    — przykładowy profil i preferencje
   ?screen=<id>               — otwarcie wskazanego ekranu
   ?modal=accept|reject|where — otwarcie modala  */
(function applyPreviewParams() {
  const p = new URLSearchParams(location.search);
  if (p.get('demo') === '1') {
    state.profile = { firstName: 'Jan', lastName: 'Kowalski', email: 'jan@example.com' };
    state.genres = ['Sci-fi', 'Thriller', 'Dramat', 'Komedia'];
    state.mood = 'surprise';
    sessionParams = { mood: 'surprise', genres: state.genres, surprise: false };
  }
  const screen = p.get('screen');
  if (screen && document.getElementById(screen)) go(screen);
  const modal = p.get('modal');
  if (modal === 'accept' && currentMovies.length) openAcceptModal(currentMovies[0].id);
  if (modal === 'reject' && currentMovies.length) openRejectModal(currentMovies[0].id);
  if (modal === 'where' && currentMovies.length) openWhereModal(currentMovies[1]?.id || currentMovies[0].id);
})();

/* ── PRZYWRACANIE SESJI ────────────────────────────────────────
   Po odświeżeniu odświeżamy profil i preferencje z backendu.
   Jeśli konto już nie istnieje, czyścimy zapamiętane id. */
(async function initSession() {
  if (!state.userId) return;
  try {
    const u = await API.getUser(state.userId);
    state.profile = {
      firstName: u.first_name, lastName: u.last_name, email: u.email,
      gender: u.gender, birthdate: u.birthdate,
    };
    state.genres = u.genres || state.genres;
    state.mood = u.mood || state.mood;
    saveState();
  } catch (e) {
    if (e.status === 404) { state.userId = null; saveState(); }
  }
})();
