/* ════════════════════════════════════════════════════════════
   SmartVOD Recommender — api.js
   Klient REST do backendu FastAPI. Wszystkie metody zwracają
   sparsowany JSON, a przy błędzie rzucają Error z treścią z API.
   ════════════════════════════════════════════════════════════ */

const API_BASE = 'http://127.0.0.1:8000';

async function apiRequest(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) opts.body = JSON.stringify(body);

  const res = await fetch(API_BASE + path, opts);
  let data = null;
  try { data = await res.json(); } catch (e) { /* brak treści */ }

  if (!res.ok) {
    const err = new Error((data && data.detail) || `Błąd połączenia (${res.status})`);
    err.status = res.status;
    throw err;
  }
  return data;
}

const API = {
  base: API_BASE,
  health: () => apiRequest('GET', '/api/health'),
  register: (payload) => apiRequest('POST', '/api/register', payload),
  login: (email, password) => apiRequest('POST', '/api/login', { email, password }),
  getUser: (id) => apiRequest('GET', `/api/user/${id}`),
  savePreferences: (payload) => apiRequest('PUT', '/api/preferences', payload),
  getRecommendations: (payload) => apiRequest('POST', '/api/recommend', payload),
  addToLibrary: (payload) => apiRequest('POST', '/api/library', payload),
  getLibrary: (id) => apiRequest('GET', `/api/library/${id}`),
  recordInteraction: (payload) => apiRequest('POST', '/api/interactions', payload),
};

window.API = API;
