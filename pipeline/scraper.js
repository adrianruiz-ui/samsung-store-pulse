// Se ejecuta en una pestaña de Google Maps ya abierta en la ficha de la tienda.
// Uso desde la herramienta de JavaScript del navegador:  await (SCRAPER)('SS001')
// Guarda el resultado en IndexedDB (base "ssmx", tabla "rev") para exportarlo al final con export.js.
async (SID) => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const head = document.querySelector('div.F7nice');
  const ht = head ? head.innerText.replace(/\s+/g, ' ') : '';
  const rating = parseFloat((ht.match(/(\d[.,]\d)/) || [])[1]?.replace(',', '.')) || null;
  const total = parseInt(((ht.match(/\(([\d.,\s]+)\)/) || [])[1] || '').replace(/[^\d]/g, '')) || null;
  const tab = [...document.querySelectorAll('button[role="tab"]')].find((b) => /Reseñas|Opiniones/i.test(b.innerText || b.getAttribute('aria-label') || ''));
  if (!tab) return JSON.stringify({ id: SID, err: 'no tab' });
  tab.click(); await sleep(2500);
  const sortBtn = [...document.querySelectorAll('button')].find((b) => /Ordenar/i.test(b.getAttribute('aria-label') || b.innerText || ''));
  if (sortBtn) { sortBtn.click(); await sleep(1500); const nw = [...document.querySelectorAll('[role="menuitemradio"],[role="menuitem"]')].find((x) => /recientes/i.test(x.innerText)); nw && nw.click(); await sleep(2500); }
  const t0 = Date.now();
  const sc = [...document.querySelectorAll('div.m6QErb.DxyBCb')].sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
  let last = -1, stall = 0;
  while (Date.now() - t0 < 36000) {
    const n = new Set([...document.querySelectorAll('div.jftiEf[data-review-id]')].map((e) => e.dataset.reviewId)).size;
    if (n >= 300) break;
    if (n === last) { if (++stall > 18) break; } else stall = 0;
    last = n; sc.scrollTop = sc.scrollHeight; await sleep(700);
  }
  document.querySelectorAll('div.jftiEf button.w8nwRe').forEach((b) => { if (/Más/i.test(b.innerText)) b.click(); });
  await sleep(800);
  const seen = new Set(), out = [];
  for (const e of document.querySelectorAll('div.jftiEf[data-review-id]')) {
    const id = e.dataset.reviewId; if (seen.has(id)) continue; seen.add(id);
    const star = e.querySelector('span[role="img"][aria-label*="estrella"]'); const txt = e.querySelector('span.wiI7pd');
    out.push({ id, r: star ? parseInt(star.getAttribute('aria-label')) : null, d: (e.querySelector('span.rsqaWe') || {}).innerText || '', t: txt ? txt.innerText.replace(/\s+/g, ' ').trim() : '', resp: !!e.querySelector('div.CDe7pd'), lg: /Local Guide/.test(e.innerText) });
    if (out.length >= 300) break;
  }
  const rec = { store: SID, name: (document.querySelector('h1') || {}).innerText || '', rating, total, scraped: new Date().toISOString(), reviews: out };
  await new Promise((ok, ko) => { const q = indexedDB.open('ssmx', 1); q.onupgradeneeded = () => q.result.createObjectStore('rev', { keyPath: 'store' }); q.onsuccess = () => { const tx = q.result.transaction('rev', 'readwrite'); tx.objectStore('rev').put(rec); tx.oncomplete = ok; tx.onerror = ko; }; q.onerror = ko; });
  return JSON.stringify({ id: SID, n: out.length, rating, total, secs: Math.round((Date.now() - t0) / 1000) });
}
