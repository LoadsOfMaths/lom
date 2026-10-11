/* Sports Day – service worker.
   Everything the app needs is in index.html (fonts and images are embedded),
   so we precache the page, manifest and icons and serve them from the cache.
   Bump VERSION whenever you publish a change so phones pick it up. */
const VERSION = 'sports-day-v1';
const PRECACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(VERSION)
      .then(cache => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('sports-day-') && k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Page loads: always give back the cached app, refresh it quietly in the background.
  if (req.mode === 'navigate') {
    event.respondWith(
      caches.open(VERSION).then(async cache => {
        const cached = (await cache.match('./index.html')) || (await cache.match('./'));
        const refresh = fetch(req).then(res => {
          if (res && res.ok) cache.put('./index.html', res.clone());
          return res;
        }).catch(() => null);
        if (cached) { event.waitUntil(refresh); return cached; }
        return (await refresh) || new Response('Offline and not yet cached.', { status: 503, headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
      })
    );
    return;
  }

  // Everything else: cache first, fall back to the network.
  event.respondWith(
    caches.match(req, { ignoreSearch: true }).then(hit => hit || fetch(req).then(res => {
      if (res && res.ok) { const copy = res.clone(); caches.open(VERSION).then(c => c.put(req, copy)); }
      return res;
    }))
  );
});
