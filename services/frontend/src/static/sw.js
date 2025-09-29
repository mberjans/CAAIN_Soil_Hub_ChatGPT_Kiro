// Service Worker for Mobile Variety Selection
// Provides comprehensive PWA features including offline capability, background sync, push notifications, and advanced mobile features

const CACHE_NAME = 'mobile-variety-selection-v3';
const STATIC_CACHE = 'static-v3';
const DYNAMIC_CACHE = 'dynamic-v3';
const OFFLINE_CACHE = 'offline-v3';
const API_CACHE = 'api-v3';

// App shell files for instant loading
const APP_SHELL_FILES = [
    '/mobile-variety-selection',
    '/static/css/mobile-variety-selection.css',
    '/static/js/mobile-variety-selection.js',
    '/static/js/mobile-device-integration.js',
    '/static/js/mobile-camera-crop-id.js',
    '/static/js/mobile-gps-field-mapping.js',
    '/static/js/mobile-offline-database.js',
    '/static/js/mobile-pwa-features.js',
    '/static/css/bootstrap.min.css',
    '/static/css/font-awesome.min.css',
    '/static/js/bootstrap.bundle.min.js',
    '/manifest.json',
    '/static/css/app-shell.css',
    '/static/js/app-shell.js',
    '/static/templates/app-shell.html'
];

// Critical resources for offline functionality
const CRITICAL_RESOURCES = [
    '/mobile-variety-selection',
    '/static/css/mobile-variety-selection.css',
    '/static/js/mobile-variety-selection.js',
    '/static/js/mobile-offline-database.js',
    '/static/js/mobile-pwa-features.js',
    '/manifest.json'
];

// Non-critical resources that can be cached lazily
const NON_CRITICAL_RESOURCES = [
    '/static/js/mobile-device-integration.js',
    '/static/js/mobile-camera-crop-id.js',
    '/static/js/mobile-gps-field-mapping.js',
    '/static/css/bootstrap.min.css',
    '/static/css/font-awesome.min.css',
    '/static/js/bootstrap.bundle.min.js'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    '/api/v1/crop-taxonomy/crops',
    '/api/v1/crop-taxonomy/crops/search',
    '/api/v1/locations/search',
    '/api/v1/crop-analysis/identify',
    '/api/v1/varieties',
    '/api/v1/recommendations',
    '/api/v1/fields',
    '/api/v1/photos'
];

// Install event - implement app shell architecture
self.addEventListener('install', (event) => {
    console.log('Service Worker installing with app shell architecture...');
    
    event.waitUntil(
        Promise.all([
            // Cache critical app shell resources immediately
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('Caching critical app shell resources...');
                return cache.addAll(CRITICAL_RESOURCES);
            }),
            
            // Cache offline fallback data
            caches.open(OFFLINE_CACHE).then((cache) => {
                console.log('Caching offline fallback data...');
                return cache.addAll([
                    '/offline.html',
                    '/static/data/offline-crops.json',
                    '/static/data/offline-varieties.json'
                ]);
            })
        ])
        .then(() => {
            console.log('App shell cached successfully');
            return self.skipWaiting();
        })
        .catch((error) => {
            console.error('Error caching app shell:', error);
        })
    );
});

// Activate event - clean up old caches and initialize PWA features
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating with PWA features...');
    
    event.waitUntil(
        Promise.all([
            // Clean up old caches
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (![STATIC_CACHE, DYNAMIC_CACHE, OFFLINE_CACHE, API_CACHE].includes(cacheName)) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // Initialize background sync
            initializeBackgroundSync(),
            
            // Initialize push notifications
            initializePushNotifications(),
            
            // Cache non-critical resources in background
            cacheNonCriticalResources()
        ])
        .then(() => {
            console.log('Service Worker activated with PWA features');
            return self.clients.claim();
        })
        .catch((error) => {
            console.error('Error during service worker activation:', error);
        })
    );
});

// Fetch event - comprehensive PWA strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle API requests with network-first strategy
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(handleApiRequest(request));
        return;
    }

    // Handle app shell requests with cache-first strategy
    if (CRITICAL_RESOURCES.some(file => url.pathname.includes(file))) {
        event.respondWith(handleAppShellRequest(request));
        return;
    }

    // Handle static assets with cache-first strategy
    if (NON_CRITICAL_RESOURCES.some(file => url.pathname.includes(file))) {
        event.respondWith(handleStaticAssetRequest(request));
        return;
    }

    // Handle HTML requests with network-first strategy
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(handleHtmlRequest(request));
        return;
    }

    // Handle images with cache-first strategy
    if (request.headers.get('accept').includes('image/')) {
        event.respondWith(handleImageRequest(request));
        return;
    }

    // Default: stale-while-revalidate strategy
    event.respondWith(handleDefaultRequest(request));
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
    
    switch (event.tag) {
        case 'save-recommendations':
            event.waitUntil(syncSavedRecommendations());
            break;
        case 'sync-varieties':
            event.waitUntil(syncVarieties());
            break;
        case 'sync-field-data':
            event.waitUntil(syncFieldData());
            break;
        case 'sync-photos':
            event.waitUntil(syncPhotos());
            break;
        case 'sync-all':
            event.waitUntil(syncAllData());
            break;
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

// Sync varieties from offline storage
async function syncVarieties() {
    try {
        const pendingVarieties = await getPendingData('varieties');
        
        for (const variety of pendingVarieties) {
            try {
                const response = await fetch('/api/v1/varieties', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(variety)
                });
                
                if (response.ok) {
                    await removePendingData('varieties', variety.id);
                    console.log('Synced variety:', variety.id);
                }
            } catch (error) {
                console.error('Failed to sync variety:', error);
            }
        }
    } catch (error) {
        console.error('Variety sync failed:', error);
    }
}

// Sync field data from offline storage
async function syncFieldData() {
    try {
        const pendingFieldData = await getPendingData('fieldData');
        
        for (const fieldData of pendingFieldData) {
            try {
                const response = await fetch('/api/v1/fields', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(fieldData)
                });
                
                if (response.ok) {
                    await removePendingData('fieldData', fieldData.id);
                    console.log('Synced field data:', fieldData.id);
                }
            } catch (error) {
                console.error('Failed to sync field data:', error);
            }
        }
    } catch (error) {
        console.error('Field data sync failed:', error);
    }
}

// Sync photos from offline storage
async function syncPhotos() {
    try {
        const pendingPhotos = await getPendingData('photos');
        
        for (const photo of pendingPhotos) {
            try {
                const formData = new FormData();
                formData.append('photo', photo.blob);
                formData.append('metadata', JSON.stringify(photo.metadata));

                const response = await fetch('/api/v1/photos', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    await removePendingData('photos', photo.id);
                    console.log('Synced photo:', photo.id);
                }
            } catch (error) {
                console.error('Failed to sync photo:', error);
            }
        }
    } catch (error) {
        console.error('Photo sync failed:', error);
    }
}

// Sync all pending data
async function syncAllData() {
    await Promise.all([
        syncSavedRecommendations(),
        syncVarieties(),
        syncFieldData(),
        syncPhotos()
    ]);
    
    // Notify main thread that sync is complete
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
        client.postMessage({
            type: 'SYNC_COMPLETE',
            data: { timestamp: Date.now() }
        });
    });
}

// Generic function to get pending data from IndexedDB
async function getPendingData(storeName) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('AFASOfflineDB', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
    });
}

// Generic function to remove pending data from IndexedDB
async function removePendingData(storeName, id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('AFASOfflineDB', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}