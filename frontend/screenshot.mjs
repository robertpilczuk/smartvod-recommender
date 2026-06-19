// Generowanie zrzutów ekranów do dokumentacji SmartVOD.
// Uruchom przy działającym backendzie (8000) i serwerze frontu (8080):
//   node screenshot.mjs
import puppeteer from 'puppeteer-core';
import { mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = 'http://127.0.0.1:8080/index.html';
// fileURLToPath dekoduje spacje w ścieżce (inaczej zostają %20)
const OUT = fileURLToPath(new URL('../zrzuty_nowe/', import.meta.url));
mkdirSync(OUT, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: 'new',
  args: ['--no-sandbox', '--force-color-profile=srgb', '--hide-scrollbars'],
  defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 2 },
});
const page = await browser.newPage();
page.on('pageerror', (e) => console.log('PAGEERROR:', e.message));

async function shot(name, full = true) {
  await page.screenshot({ path: `${OUT}${name}.png`, fullPage: full });
  console.log('  ✓', name);
}

// ── 1. Ekrany statyczne (tryb podglądu ?demo=1&screen=) ──
const statics = [
  ['ekran01_landing', 'screen-landing'],
  ['ekran02_logowanie', 'screen-login'],
  ['ekran03_rejestracja', 'screen-register'],
  ['ekran04_onboarding_gatunki', 'screen-genres'],
  ['ekran05_glowny', 'screen-home'],
  ['ekran06_nastroj', 'screen-mood'],
];
console.log('Ekrany statyczne:');
for (const [name, screen] of statics) {
  await page.goto(`${BASE}?demo=1&screen=${screen}`, { waitUntil: 'networkidle0' });
  await sleep(450);
  await shot(name);
}

// ── 2. Ekrany z danymi — logowanie demo do prawdziwego backendu ──
console.log('Logowanie demo:');
await page.goto(BASE, { waitUntil: 'networkidle0' });
await page.evaluate(() => demoLogin());
await page.waitForFunction(
  () => document.getElementById('screen-home').classList.contains('active'),
  { timeout: 20000 },
);
console.log('  ✓ zalogowano (home)');

// Rekomendacje ("Podpowiedz film" — na bazie gatunków)
console.log('Ekrany z danymi:');
await page.evaluate(() => startSuggest());
await page.waitForFunction(
  () => document.querySelectorAll('#movies-grid .movie-card').length > 0,
  { timeout: 25000 },
);
await sleep(900);
await shot('ekran07_rekomendacje');

// Panel "Co Ci się podoba?" (modal akceptacji)
await page.evaluate(() => openAcceptModal(currentMovies[0].id));
await page.waitForFunction(
  () => document.getElementById('accept-modal').classList.contains('open'),
  { timeout: 5000 },
);
await sleep(400);
await shot('ekran08_panel_co_lubie', false);
await page.evaluate(() => document.getElementById('accept-modal').classList.remove('open'));
await sleep(200);

// Biblioteka
await page.evaluate(() => go('screen-library'));
await page.waitForFunction(
  () => document.getElementById('screen-library').classList.contains('active'),
  { timeout: 10000 },
);
await sleep(1200);
await shot('ekran09_biblioteka');

// Profil (po douczeniu na ocenach)
await page.evaluate(() => learnModel());
await page.waitForFunction(
  () => document.getElementById('screen-profile').classList.contains('active'),
  { timeout: 25000 },
);
await sleep(1200);
await shot('ekran10_profil');

await browser.close();
console.log('\nGotowe → zrzuty_nowe/');
