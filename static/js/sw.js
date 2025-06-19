const CACHE_NAME = 'smartreminder-v3';
const STATIC_CACHE = 'static-v3';
const DYNAMIC_CACHE = 'dynamic-v3';

const STATIC_FILES = [
    '/',
    '/offline',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/main.js',
    '/static/js/notes.js',
    '/static/js/reminders.js',
    '/static/manifest.json',
    '/static/icons/favicon.ico',
    '/static/icons/icon-72x72.png',
    '/static/icons/icon-96x96.png',
    '/static/icons/icon-128x128.png',
    '/static/icons/icon-144x144.png',
    '/static/icons/icon-152x152.png',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-384x384.png',
    '/static/icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', function(event) {
    console.log('[Service Worker] Installing Service Worker...', event);
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(function(cache) {
                console.log('[Service Worker] Pre-caching static files');
                return cache.addAll(STATIC_FILES);
            })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName !== CACHE_NAME;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        })
    );
});

self.addEventListener('fetch', function(event) {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin) && 
        !event.request.url.includes('bootstrap')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                
                return fetch(event.request)
                    .then(function(res) {
                        // Check if we received a valid response
                        if(!res || res.status !== 200) {
                            if (event.request.headers.get('accept').includes('text/html')) {
                                return caches.match('/offline');
                            }
                            return res;
                        }

                        return caches.open(DYNAMIC_CACHE)
                            .then(function(cache) {
                                // Put a copy in dynamic cache
                                if (!event.request.url.includes('chrome-extension')) {
                                    cache.put(event.request.url, res.clone());
                                }
                                return res;
                            });
                    })
                    .catch(function(err) {
                        if (event.request.headers.get('accept').includes('text/html')) {
                            return caches.match('/offline');
                        }
                    });
            })
    );
                    });
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    }
                ).catch(function() {
                    // If the network is unavailable and the requested resource isn't in the cache,
                    // show the offline page for navigate requests
                    if (event.request.mode === 'navigate') {
                        return caches.match('/offline');
                    }
                });
            })
    );
});