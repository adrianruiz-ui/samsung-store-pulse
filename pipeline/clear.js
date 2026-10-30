// Limpia lo guardado de corridas anteriores antes de empezar.
(async () => { await new Promise((ok) => { const q = indexedDB.deleteDatabase('ssmx'); q.onsuccess = q.onerror = q.onblocked = ok; }); return 'ok'; })()
