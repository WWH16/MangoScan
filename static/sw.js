// MangoScan service worker: makes the app installable and shows a friendly
// page when there is no signal. Scanning itself always needs the internet.
// app.py fills in VERSION from a hash of the static files, so any change to the
// CSS, fonts or icons makes phones install this worker again and fetch new copies.
const VERSION = 'mangoscan-__STATIC_VERSION__';
const SHELL = [
    '/offline',
    '/static/css/style.css',
    '/static/fonts/geist-var.woff2',
    '/static/icons/icon-192.png',
    '/static/manifest.webmanifest',
];

self.addEventListener('install', (event) => {
    event.waitUntil(caches.open(VERSION).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const req = event.request;
    if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

    // Pages: always try the network, fall back to the offline page
    if (req.mode === 'navigate') {
        event.respondWith(fetch(req).catch(() => caches.match('/offline')));
        return;
    }

    // Static files: serve from cache, fill the cache on first use
    if (new URL(req.url).pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(req).then((hit) => hit || fetch(req).then((res) => {
                if (res.ok) {
                    const copy = res.clone();
                    caches.open(VERSION).then((cache) => cache.put(req, copy));
                }
                return res;
            }))
        );
    }
});
