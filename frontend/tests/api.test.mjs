import { test } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const apiSrc = fs.readFileSync(path.join(__dirname, '../js/api.js'), 'utf8');

// Ładuje api.js z podstawionym fetch i zwraca obiekt API
function loadAPI(fetchImpl) {
  global.window = {};
  global.fetch = fetchImpl;
  eval(apiSrc);
  return global.window.API;
}

test('register wysyła POST na właściwy URL z poprawnym body', async () => {
  let captured;
  const API = loadAPI(async (url, opts) => {
    captured = { url, opts };
    return { ok: true, status: 200, json: async () => ({ user_id: 1 }) };
  });
  const r = await API.register({ email: 'a@b.pl', password: '123' });
  assert.equal(r.user_id, 1);
  assert.ok(captured.url.endsWith('/api/register'));
  assert.equal(captured.opts.method, 'POST');
  assert.deepEqual(JSON.parse(captured.opts.body), { email: 'a@b.pl', password: '123' });
});

test('login buduje body z email i password', async () => {
  let body;
  const API = loadAPI(async (url, opts) => {
    body = JSON.parse(opts.body);
    return { ok: true, status: 200, json: async () => ({ user_id: 7 }) };
  });
  await API.login('x@y.pl', 'pass');
  assert.deepEqual(body, { email: 'x@y.pl', password: 'pass' });
});

test('błąd HTTP rzuca Error z treścią z API i statusem', async () => {
  const API = loadAPI(async () => ({
    ok: false, status: 401, json: async () => ({ detail: 'Błędny email lub hasło' }),
  }));
  await assert.rejects(
    () => API.login('a@b.pl', 'x'),
    (e) => {
      assert.equal(e.message, 'Błędny email lub hasło');
      assert.equal(e.status, 401);
      return true;
    },
  );
});

test('błąd bez treści daje komunikat z kodem', async () => {
  const API = loadAPI(async () => ({ ok: false, status: 500, json: async () => { throw new Error('no body'); } }));
  await assert.rejects(() => API.health(), (e) => {
    assert.match(e.message, /500/);
    return true;
  });
});

test('getLibrary używa GET na poprawnym URL', async () => {
  let captured;
  const API = loadAPI(async (url, opts) => {
    captured = { url, method: opts.method, hasBody: opts.body !== undefined };
    return { ok: true, status: 200, json: async () => ({ library: [] }) };
  });
  await API.getLibrary(42);
  assert.ok(captured.url.endsWith('/api/library/42'));
  assert.equal(captured.method, 'GET');
  assert.equal(captured.hasBody, false);
});

test('savePreferences używa metody PUT', async () => {
  let method;
  const API = loadAPI(async (url, opts) => {
    method = opts.method;
    return { ok: true, status: 200, json: async () => ({ status: 'ok' }) };
  });
  await API.savePreferences({ user_id: 1, mood: 'calm' });
  assert.equal(method, 'PUT');
});
