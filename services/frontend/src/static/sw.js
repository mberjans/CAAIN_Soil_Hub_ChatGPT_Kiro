// Service Worker for Mobile Variety Selection
// Provides offline capability and cached variety database

const CACHE_NAME = 'mobile-variety-selection-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/static/css/mobile-variety-selection.css',
    '/static/js/mobile-variety-selection.js',
    '/static/css/bootstrap.min.css',
    '/static/css/font-awesome.min.css',
    '/static/js/bootstrap.bundle.min.js',
    '/manifest.json'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    '/api/v1/crop-taxonomy/crops',
    '/api/v1/crop-taxonomy/crops/search',
    '/api/v1/locations/search'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Caching static files...');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Error caching static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Handle API requests
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle static file requests
    if (STATIC_FILES.some(file => url.pathname.includes(file))) {
        event.respondWith(handleStaticRequest(request));
        return;
    }

    // Handle HTML requests
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(handleHtmlRequest(request));
        return;
    }

    // Default: try network first, then cache
    event.respondWith(
        fetch(request)
            .then((response) => {
                // Cache successful responses
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(DYNAMIC_CACHE)
                        .then((cache) => {
                            cache.put(request, responseClone);
                        });
                }
                return response;
            })
            .catch(() => {
                // Return cached version if network fails
                return caches.match(request);
            })
    );
});

// Handle API requests with offline fallback
async function handleApiRequest(request) {
    const url = new URL(request.url);
    
    try {
        // Try network first
        const response = await fetch(request);
        
        if (response.ok) {
            // Cache successful API responses
            const responseClone = response.clone();
            const cache = await caches.open(DYNAMIC_CACHE);
            await cache.put(request, responseClone);
            
            return response;
        }
        
        throw new Error('API request failed');
    } catch (error) {
        console.log('Network failed, trying cache for:', url.pathname);
        
        // Try to serve from cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline fallback for specific endpoints
        return getOfflineFallback(url.pathname);
    }
}

// Handle static file requests
async function handleStaticRequest(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.error('Failed to fetch static file:', request.url);
        return new Response('Static file not available offline', { status: 404 });
    }
}

// Handle HTML requests
async function handleHtmlRequest(request) {
    try {
        const response = await fetch(request);
        return response;
    } catch (error) {
        // Return cached HTML or offline page
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page
        return new Response(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Offline - CAAIN Soil Hub</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
                    .offline-icon { font-size: 4rem; color: #6c757d; margin-bottom: 1rem; }
                    h1 { color: #343a40; margin-bottom: 1rem; }
                    p { color: #6c757d; margin-bottom: 2rem; }
                    .btn { padding: 0.75rem 1.5rem; background: #28a745; color: white; border: none; border-radius: 0.375rem; text-decoration: none; }
                </style>
            </head>
            <body>
                <div class="offline-icon">📱</div>
                <h1>You're Offline</h1>
                <p>This page is not available offline. Please check your internet connection and try again.</p>
                <a href="/" class="btn">Go to Home</a>
            </body>
            </html>
        `, {
            headers: { 'Content-Type': 'text/html' }
        });
    }
}

// Get offline fallback data for specific API endpoints
function getOfflineFallback(pathname) {
    if (pathname.includes('/crop-taxonomy/crops')) {
        return new Response(JSON.stringify({
            crops: [
                {
                    id: 'corn',
                    name: 'Corn',
                    scientific_name: 'Zea mays',
                    category: 'grain_crops'
                },
                {
                    id: 'soybeans',
                    name: 'Soybeans',
                    scientific_name: 'Glycine max',
                    category: 'oilseed_crops'
                },
                {
                    id: 'wheat',
                    name: 'Wheat',
                    scientific_name: 'Triticum aestivum',
                    category: 'grain_crops'
                },
                {
                    id: 'cotton',
                    name: 'Cotton',
                    scientific_name: 'Gossypium hirsutum',
                    category: 'fiber_crops'
                }
            ]
        }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    if (pathname.includes('/locations/search')) {
        return new Response(JSON.stringify([]), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    // Default offline response
    return new Response(JSON.stringify({
        error: 'Service unavailable offline',
        message: 'This feature requires an internet connection'
    }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
    });
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'save-recommendations') {
        event.waitUntil(syncSavedRecommendations());
    }
});

// Sync saved recommendations when back online
async function syncSavedRecommendations() {
    try {
        // Get pending recommendations from IndexedDB
        const pendingRecommendations = await getPendingRecommendations();
        
        for (const recommendation of pendingRecommendations) {
            try {
                const response = await fetch('/api/v1/recommendations/variety/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(recommendation)
                });
                
                if (response.ok) {
                    // Remove from pending list
                    await removePendingRecommendation(recommendation.id);
                    console.log('Synced recommendation:', recommendation.id);
                }
            } catch (error) {
                console.error('Failed to sync recommendation:', error);
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// IndexedDB helpers for offline storage
async function getPendingRecommendations() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('MobileVarietySelection', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingRecommendations'], 'readonly');
            const store = transaction.objectStore('pendingRecommendations');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('pendingRecommendations')) {
                db.createObjectStore('pendingRecommendations', { keyPath: 'id' });
            }
        };
    });
}

async function removePendingRecommendation(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('MobileVarietySelection', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingRecommendations'], 'readwrite');
            const store = transaction.objectStore('pendingRecommendations');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New variety recommendations available!',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Recommendations',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('CAAIN Soil Hub', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/mobile-variety-selection')
        );
    }
});

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_VARIETY_DATA') {
        cacheVarietyData(event.data.data);
    }
});

// Cache variety data for offline use
async function cacheVarietyData(varietyData) {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const response = new Response(JSON.stringify(varietyData), {
            headers: { 'Content-Type': 'application/json' }
        });
        
        await cache.put('/api/v1/crop-taxonomy/varieties/offline', response);
        console.log('Variety data cached for offline use');
    } catch (error) {
        console.error('Failed to cache variety data:', error);
    }
}