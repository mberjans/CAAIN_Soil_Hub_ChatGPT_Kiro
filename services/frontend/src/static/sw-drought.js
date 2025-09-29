// Service Worker for Mobile Drought Management
// Provides offline functionality and caching for field-ready operations

const CACHE_NAME = 'drought-management-v1';
const OFFLINE_CACHE = 'drought-offline-v1';

// Files to cache for offline functionality
const CACHE_FILES = [
    '/',
    '/static/css/mobile-drought-management.css',
    '/static/js/mobile-drought-management.js',
    '/static/css/agricultural.css',
    '/static/js/agricultural.js',
    '/static/images/app-icon-192.png',
    '/static/images/app-icon-512.png',
    '/manifest.json'
];

// API endpoints that should be cached
const API_CACHE_PATTERNS = [
    '/api/v1/drought/fields',
    '/api/v1/drought/practices',
    '/api/v1/drought/field-status'
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching essential files...');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => {
                console.log('Service Worker installed successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker installation failed:', error);
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
                        if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated successfully');
                return self.clients.claim();
            })
    );
});

// Fetch event - handle requests with offline fallback
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);
    
    // Handle different types of requests
    if (request.method === 'GET') {
        // Static files - serve from cache first
        if (isStaticFile(request)) {
            event.respondWith(handleStaticFile(request));
        }
        // API requests - network first with cache fallback
        else if (isApiRequest(request)) {
            event.respondWith(handleApiRequest(request));
        }
        // Other requests - network first
        else {
            event.respondWith(handleNetworkFirst(request));
        }
    }
    // POST/PUT/DELETE requests - network only, store for offline sync
    else if (['POST', 'PUT', 'DELETE'].includes(request.method)) {
        event.respondWith(handleOfflineSync(request));
    }
});

// Handle static files (CSS, JS, images)
async function handleStaticFile(request) {
    try {
        // Try cache first
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // If not in cache, fetch from network and cache
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('Failed to handle static file:', error);
        return new Response('Offline - file not available', { status: 503 });
    }
}

// Handle API requests
async function handleApiRequest(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // Cache successful responses
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Network failed, trying cache for:', request.url);
        
        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline response for API requests
        return new Response(JSON.stringify({
            error: 'Offline',
            message: 'This data is not available offline',
            timestamp: new Date().toISOString()
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Handle network-first requests
async function handleNetworkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return new Response('Offline - content not available', { status: 503 });
    }
}

// Handle offline sync for POST/PUT/DELETE requests
async function handleOfflineSync(request) {
    try {
        // Try network first
        const networkResponse = await fetch(request);
        return networkResponse;
    } catch (error) {
        console.log('Network failed, storing for offline sync:', request.url);
        
        // Store request for offline sync
        await storeOfflineRequest(request);
        
        // Return success response to user
        return new Response(JSON.stringify({
            success: true,
            message: 'Request saved for offline sync',
            timestamp: new Date().toISOString()
        }), {
            status: 202,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Store offline requests for later sync
async function storeOfflineRequest(request) {
    try {
        const offlineCache = await caches.open(OFFLINE_CACHE);
        
        // Clone request to avoid consuming the body
        const requestClone = request.clone();
        
        // Store request data
        const requestData = {
            url: request.url,
            method: request.method,
            headers: Object.fromEntries(request.headers.entries()),
            timestamp: new Date().toISOString()
        };
        
        // For requests with body, we need to handle them differently
        if (request.method === 'POST' || request.method === 'PUT') {
            const body = await request.text();
            requestData.body = body;
        }
        
        // Store in cache with unique key
        const cacheKey = `offline-${Date.now()}-${Math.random()}`;
        await offlineCache.put(cacheKey, new Response(JSON.stringify(requestData)));
        
        console.log('Stored offline request:', cacheKey);
    } catch (error) {
        console.error('Failed to store offline request:', error);
    }
}

// Sync offline requests when back online
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        event.waitUntil(syncOfflineRequests());
    }
});

// Sync stored offline requests
async function syncOfflineRequests() {
    try {
        const offlineCache = await caches.open(OFFLINE_CACHE);
        const requests = await offlineCache.keys();
        
        for (const request of requests) {
            try {
                const response = await offlineCache.match(request);
                const requestData = await response.json();
                
                // Recreate the original request
                const syncRequest = new Request(requestData.url, {
                    method: requestData.method,
                    headers: requestData.headers,
                    body: requestData.body
                });
                
                // Try to sync
                const syncResponse = await fetch(syncRequest);
                
                if (syncResponse.ok) {
                    // Success - remove from offline cache
                    await offlineCache.delete(request);
                    console.log('Successfully synced offline request:', requestData.url);
                }
            } catch (error) {
                console.error('Failed to sync offline request:', error);
            }
        }
    } catch (error) {
        console.error('Failed to sync offline requests:', error);
    }
}

// Handle push notifications
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: 'New drought alert for your fields',
        icon: '/static/images/app-icon-192.png',
        badge: '/static/images/app-icon-192.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/mobile-drought-management'
        },
        actions: [
            {
                action: 'view',
                title: 'View Alert',
                icon: '/static/images/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/images/dismiss-icon.png'
            }
        ]
    };
    
    if (event.data) {
        const data = event.data.json();
        options.body = data.message || options.body;
        options.data = { ...options.data, ...data };
    }
    
    event.waitUntil(
        self.registration.showNotification('Drought Alert', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event);
    
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/mobile-drought-management')
        );
    }
});

// Helper functions
function isStaticFile(request) {
    const url = new URL(request.url);
    return url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/);
}

function isApiRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/');
}

// Background sync registration
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'REGISTER_BACKGROUND_SYNC') {
        self.registration.sync.register('background-sync')
            .then(() => {
                console.log('Background sync registered');
            })
            .catch((error) => {
                console.error('Background sync registration failed:', error);
            });
    }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'drought-sync') {
        event.waitUntil(syncOfflineRequests());
    }
});

// Handle app updates
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Clean up old offline data
setInterval(async () => {
    try {
        const offlineCache = await caches.open(OFFLINE_CACHE);
        const requests = await offlineCache.keys();
        
        // Remove requests older than 7 days
        const sevenDaysAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
        
        for (const request of requests) {
            const response = await offlineCache.match(request);
            const requestData = await response.json();
            const requestTime = new Date(requestData.timestamp).getTime();
            
            if (requestTime < sevenDaysAgo) {
                await offlineCache.delete(request);
                console.log('Cleaned up old offline request:', requestData.url);
            }
        }
    } catch (error) {
        console.error('Failed to clean up offline data:', error);
    }
}, 24 * 60 * 60 * 1000); // Run daily