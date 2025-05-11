const CACHE_NAME = 'ua-nav-access-cache-v1';
const urlsToCache = [
  './',
  './homepage.html',
  './chatbot_ui.html',
  './manifest.json',
  './your-css-or-js-files-if-any'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
