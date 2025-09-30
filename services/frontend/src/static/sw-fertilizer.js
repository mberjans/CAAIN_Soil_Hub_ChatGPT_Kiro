// Service Worker for Mobile Fertilizer Application
// Provides offline capability and data synchronization

const CACHE_NAME = 'fertilizer-app-v1';
const OFFLINE_URLS = [
    '/',
    '/static/css/mobile-fertilizer-application.css',
    '/static/js/mobile-fertilizer-application.js',
    '/static/images/icon-192x192.png',
    '/static/images/badge-72x72.png'
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching essential files...');
                return cache.addAll(OFFLINE_URLS);
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
                        if (cacheName !== CACHE_NAME) {
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

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip requests to external domains
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version if available
                if (response) {
                    console.log('Serving from cache:', event.request.url);
                    return response;
                }

                // Otherwise fetch from network
                return fetch(event.request)
                    .then((response) => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        const responseToCache = response.clone();

                        // Cache the response for future use
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    })
                    .catch(() => {
                        // If network fails and no cache, show offline page
                        if (event.request.destination === 'document') {
                            return caches.match('/offline.html');
                        }
                    });
            })
    );
});

// Background sync for offline data
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'fertilizer-data-sync') {
        event.waitUntil(syncFertilizerData());
    }
});

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Push notification received:', event);
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from CAAIN Soil Hub',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/xmark.png'
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
        // Open the app
        event.waitUntil(
            clients.openWindow('/mobile-fertilizer-application')
        );
    } else if (event.action === 'close') {
        // Just close the notification
        return;
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/mobile-fertilizer-application')
        );
    }
});

// Sync offline fertilizer data
async function syncFertilizerData() {
    try {
        console.log('Syncing offline fertilizer data...');
        
        // Get offline data from IndexedDB or localStorage
        const offlineData = await getOfflineData();
        
        if (offlineData.length === 0) {
            console.log('No offline data to sync');
            return;
        }

        // Sync each piece of data
        for (const data of offlineData) {
            try {
                const response = await fetch('/api/v1/fertilizer-application/sync-offline', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    console.log('Successfully synced data:', data.timestamp);
                    await removeOfflineData(data.timestamp);
                } else {
                    console.error('Failed to sync data:', data.timestamp);
                }
            } catch (error) {
                console.error('Error syncing data:', error);
            }
        }

        // Notify the client that sync is complete
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'SYNC_COMPLETE',
                syncedCount: offlineData.length
            });
        });

    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// Get offline data from IndexedDB
async function getOfflineData() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('fertilizer-offline-db', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['offline-data'], 'readonly');
            const store = transaction.objectStore('offline-data');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('offline-data')) {
                db.createObjectStore('offline-data', { keyPath: 'timestamp' });
            }
        };
    });
}

// Remove synced data from IndexedDB
async function removeOfflineData(timestamp) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('fertilizer-offline-db', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['offline-data'], 'readwrite');
            const store = transaction.objectStore('offline-data');
            const deleteRequest = store.delete(timestamp);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

// Message handling from main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    } else if (event.data.type === 'CACHE_FERTILIZER_DATA') {
        cacheFertilizerData(event.data.data);
    } else if (event.data.type === 'REGISTER_BACKGROUND_SYNC') {
        registerBackgroundSync();
    }
});

// Cache fertilizer data for offline use
async function cacheFertilizerData(data) {
    try {
        const db = await openDB();
        const transaction = db.transaction(['offline-data'], 'readwrite');
        const store = transaction.objectStore('offline-data');
        
        await store.add({
            ...data,
            timestamp: data.timestamp || Date.now().toString()
        });
        
        console.log('Fertilizer data cached for offline use');
    } catch (error) {
        console.error('Failed to cache fertilizer data:', error);
    }
}

// Register background sync
async function registerBackgroundSync() {
    try {
        await self.registration.sync.register('fertilizer-data-sync');
        console.log('Background sync registered');
    } catch (error) {
        console.error('Failed to register background sync:', error);
    }
}

// Open IndexedDB
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('fertilizer-offline-db', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('offline-data')) {
                db.createObjectStore('offline-data', { keyPath: 'timestamp' });
            }
        };
    });
}

// Periodic background sync (if supported)
if ('periodicSync' in self.registration) {
    self.addEventListener('periodicsync', (event) => {
        if (event.tag === 'fertilizer-periodic-sync') {
            event.waitUntil(syncFertilizerData());
        }
    });
}

console.log('Service Worker loaded successfully');