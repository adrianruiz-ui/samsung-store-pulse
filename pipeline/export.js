// Descarga todo lo guardado en IndexedDB como samsung_resenas_AAAA-MM-DD.json en la carpeta de Descargas, y limpia la base.
(async () => {
  const db = await new Promise((ok, ko) => { const q = indexedDB.open('ssmx', 1); q.onupgradeneeded = () => q.result.createObjectStore('rev', { keyPath: 'store' }); q.onsuccess = () => ok(q.result); q.onerror = ko; });
  const all = await new Promise((ok, ko) => { const r = db.transaction('rev').objectStore('rev').getAll(); r.onsuccess = () => ok(r.result); r.onerror = ko; });
  const name = 'samsung_resenas_' + new Date().toISOString().slice(0, 10) + '.json';
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(all)], { type: 'application/json' })); a.download = name; document.body.appendChild(a); a.click(); a.remove();
  return JSON.stringify({ file: name, stores: all.length, reviews: all.reduce((s, x) => s + x.reviews.length, 0), short: all.filter((x) => x.reviews.length < 100).map((x) => x.store + ':' + x.reviews.length) });
})()
