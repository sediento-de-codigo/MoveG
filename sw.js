// sw.js
const CACHE_NAME = 'moveg-v1';

self.addEventListener('fetch', (event) => {
    // Intentamos ir a la red primero
    event.respondWith(
        fetch(event.request)
            .catch(() => {
                // Si falla la red (offline), buscamos en caché
                return caches.match(event.request);
            })
    );
});