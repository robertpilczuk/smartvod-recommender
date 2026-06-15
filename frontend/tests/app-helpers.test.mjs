import { test } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const appSrc = fs.readFileSync(path.join(__dirname, '../js/app.js'), 'utf8');

// app.js zawiera kod DOM uruchamiany przy ładowaniu, więc podstawiamy atrapy
// przeglądarki i wyciągamy czyste funkcje przez doklejone wyrażenie.
function loadApp() {
  const noop = () => {};
  global.document = {
    querySelectorAll: () => [],
    getElementById: () => null,
    addEventListener: noop,
  };
  global.window = {};
  global.location = { search: '' };
  global.localStorage = { getItem: () => null, setItem: noop };
  global.fetch = async () => ({ ok: true, status: 200, json: async () => ({}) });
  if (!global.structuredClone) global.structuredClone = (x) => JSON.parse(JSON.stringify(x));

  const expr = appSrc + '\n;({ adaptMovie, validEmail, genreCountLabel, demoPlatforms, shuffle, libraryCard });';
  return eval(expr);
}

const app = loadApp();

test('validEmail rozpoznaje poprawne i błędne adresy', () => {
  assert.ok(app.validEmail('a@b.pl'));
  assert.ok(app.validEmail('jan.kowalski@example.com'));
  assert.ok(!app.validEmail('zly-email'));
  assert.ok(!app.validEmail('a@b'));
  assert.ok(!app.validEmail(''));
});

test('adaptMovie mapuje gatunki na PL i dorabia oprawę', () => {
  const m = app.adaptMovie({
    id: 10, title: 'Film', year: 1999, genres: 'Sci-Fi|Comedy',
    avg_rating: 4.2, predicted_rating: 4.5, reasons: ['x'],
  });
  assert.equal(m.title, 'Film');
  assert.deepEqual(m.genres, ['Sci-fi', 'Komedia']);
  assert.equal(m.rating, 4.2);
  assert.equal(m.predictedRating, 4.5);
  assert.deepEqual(m.reasons, ['x']);
  assert.ok(m.emoji && m.bg);
  assert.ok(Array.isArray(m.platforms) && m.platforms.length >= 1);
});

test('adaptMovie radzi sobie z brakiem gatunków', () => {
  const m = app.adaptMovie({ id: 1, title: 'Bez', year: 2000, genres: '' });
  assert.equal(m.genre, '—');
  assert.ok(m.emoji);
});

test('genreCountLabel poprawnie odmienia liczbę', () => {
  assert.match(app.genreCountLabel(1), /1 gatunek$/);
  assert.match(app.genreCountLabel(3), /3 gatunki$/);
  assert.match(app.genreCountLabel(7), /gatunków$/);
});

test('demoPlatforms jest stabilne dla tego samego id', () => {
  assert.deepEqual(app.demoPlatforms(5), app.demoPlatforms(5));
  assert.ok(app.demoPlatforms(5).length >= 1);
});

test('shuffle zachowuje wszystkie elementy', () => {
  const input = [1, 2, 3, 4, 5];
  const out = app.shuffle(input);
  assert.equal(out.length, input.length);
  assert.deepEqual([...out].sort(), input);
  assert.deepEqual(input, [1, 2, 3, 4, 5]); // nie modyfikuje wejścia
});

test('libraryCard zapala tyle gwiazdek, ile wynosi ocena', () => {
  const item = { id: 1, title: 'X', year: 2000, bg: '#000', emoji: '🎬', myRating: 3 };
  const html = app.libraryCard(item);
  assert.equal((html.match(/class="s lit"/g) || []).length, 3);
  assert.ok(html.includes('rateLibraryItem(1, 5)')); // gwiazdki klikalne
});
