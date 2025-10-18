/**
 * Mobile Offline Database
 * 
 * Provides offline storage and synchronization for variety data,
 * recommendations, and user preferences using IndexedDB and service workers.
 */

class MobileOfflineDatabase {
    constructor() {
        this.dbName = 'AFASOfflineDB';
        this.dbVersion = 1;
        this.db = null;
        this.serviceWorker = null;
        this.syncQueue = [];
        this.isOnline = navigator.onLine;
        this.deviceIntegration = null;
        
        this.init();
    }

    async init() {
        this.deviceIntegration = new MobileDeviceIntegration();
        
        // Wait for device integration to initialize
        await new Promise(resolve => {
            const checkInit = () => {
                if (this.deviceIntegration) {
                    resolve();
                } else {
                    setTimeout(checkInit, 100);
                }
            };
            checkInit();
        });

        await this.openDatabase();
        await this.registerServiceWorker();
        this.setupEventListeners();
        this.loadOfflineData();
    }

    /**
     * Open IndexedDB database
     */
    async openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => {
                console.error('Database failed to open');
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('Database opened successfully');
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                this.createObjectStores(db);
            };
        });
    }

    /**
     * Create object stores
     */
    createObjectStores(db) {
        // Varieties store
        if (!db.objectStoreNames.contains('varieties')) {
            const varietiesStore = db.createObjectStore('varieties', { keyPath: 'id' });
            varietiesStore.createIndex('cropType', 'crop_type', { unique: false });
            varietiesStore.createIndex('lastUpdated', 'last_updated', { unique: false });
        }

        // Recommendations store
        if (!db.objectStoreNames.contains('recommendations')) {
            const recommendationsStore = db.createObjectStore('recommendations', { keyPath: 'id' });
            recommendationsStore.createIndex('userId', 'user_id', { unique: false });
            recommendationsStore.createIndex('createdAt', 'created_at', { unique: false });
            recommendationsStore.createIndex('synced', 'synced', { unique: false });
        }

        // User preferences store
        if (!db.objectStoreNames.contains('preferences')) {
            const preferencesStore = db.createObjectStore('preferences', { keyPath: 'key' });
        }

        // Sync queue store
        if (!db.objectStoreNames.contains('syncQueue')) {
            const syncQueueStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
            syncQueueStore.createIndex('timestamp', 'timestamp', { unique: false });
            syncQueueStore.createIndex('type', 'type', { unique: false });
        }

        // Field data store
        if (!db.objectStoreNames.contains('fieldData')) {
            const fieldDataStore = db.createObjectStore('fieldData', { keyPath: 'id' });
            fieldDataStore.createIndex('userId', 'user_id', { unique: false });
            fieldDataStore.createIndex('lastUpdated', 'last_updated', { unique: false });
        }

        // Photos store
        if (!db.objectStoreNames.contains('photos')) {
            const photosStore = db.createObjectStore('photos', { keyPath: 'id' });
            photosStore.createIndex('userId', 'user_id', { unique: false });
            photosStore.createIndex('createdAt', 'created_at', { unique: false });
            photosStore.createIndex('synced', 'synced', { unique: false });
        }

        // Strategy tracking store
        if (!db.objectStoreNames.contains('strategyTracking')) {
            const trackingStore = db.createObjectStore('strategyTracking', { keyPath: 'client_event_id' });
            trackingStore.createIndex('strategyId', 'strategy_id', { unique: false });
            trackingStore.createIndex('synced', 'synced', { unique: false });
            trackingStore.createIndex('createdAt', 'created_at', { unique: false });
        }
    }

    /**
     * Register service worker
     */
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                this.serviceWorker = registration;
                console.log('Service worker registered successfully');

                // Listen for service worker messages
                navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage.bind(this));
            } catch (error) {
                console.error('Service worker registration failed:', error);
            }
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Online/offline status
        window.addEventListener('online', this.handleOnline.bind(this));
        window.addEventListener('offline', this.handleOffline.bind(this));

        // Network changes
        document.addEventListener('mobileDevice:networkChange', this.handleNetworkChange.bind(this));

        // App visibility changes
        document.addEventListener('mobileDevice:visibilityChange', this.handleVisibilityChange.bind(this));
    }

    /**
     * Handle online status
     */
    handleOnline() {
        this.isOnline = true;
        this.showNotification('Connection restored - syncing data', { type: 'success' });
        this.syncOfflineData();
    }

    /**
     * Handle offline status
     */
    handleOffline() {
        this.isOnline = false;
        this.showNotification('Working offline - data will sync when connected', { type: 'warning' });
    }

    /**
     * Handle network changes
     */
    handleNetworkChange(event) {
        const { effectiveType, saveData } = event.detail;
        
        if (saveData) {
            this.enableDataSavingMode();
        }
        
        if (effectiveType === 'slow-2g' || effectiveType === '2g') {
            this.enableLowBandwidthMode();
        }
    }

    /**
     * Handle app visibility changes
     */
    handleVisibilityChange(event) {
        const { visible } = event.detail;
        
        if (visible && this.isOnline) {
            // App became visible and we're online - sync data
            this.syncOfflineData();
        }
    }

    /**
     * Handle service worker messages
     */
    handleServiceWorkerMessage(event) {
        const { type, data } = event.data;
        
        switch (type) {
            case 'SYNC_COMPLETE':
                this.handleSyncComplete(data);
                break;
            case 'SYNC_ERROR':
                this.handleSyncError(data);
                break;
            case 'CACHE_UPDATED':
                this.handleCacheUpdated(data);
                break;
        }
    }

    /**
     * Load offline data
     */
    async loadOfflineData() {
        try {
            // Load varieties
            await this.loadVarieties();
            
            // Load user preferences
            await this.loadUserPreferences();
            
            // Load field data
            await this.loadFieldData();
            
            console.log('Offline data loaded successfully');
        } catch (error) {
            console.error('Error loading offline data:', error);
        }
    }

    /**
     * Load varieties from offline storage
     */
    async loadVarieties() {
        const varieties = await this.getAllFromStore('varieties');
        return varieties;
    }

    /**
     * Load user preferences
     */
    async loadUserPreferences() {
        const preferences = await this.getAllFromStore('preferences');
        return preferences;
    }

    /**
     * Load field data
     */
    async loadFieldData() {
        const fieldData = await this.getAllFromStore('fieldData');
        return fieldData;
    }

    /**
     * Save variety to offline storage
     */
    async saveVariety(variety) {
        const varietyData = {
            ...variety,
            last_updated: new Date().toISOString(),
            offline: true
        };

        await this.saveToStore('varieties', varietyData);
        
        // Add to sync queue if offline
        if (!this.isOnline) {
            await this.addToSyncQueue('variety', varietyData);
        }
    }

    /**
     * Save recommendation to offline storage
     */
    async saveRecommendation(recommendation) {
        const recommendationData = {
            ...recommendation,
            id: recommendation.id || this.generateId(),
            created_at: new Date().toISOString(),
            synced: this.isOnline
        };

        await this.saveToStore('recommendations', recommendationData);
        
        // Add to sync queue if offline
        if (!this.isOnline) {
            await this.addToSyncQueue('recommendation', recommendationData);
        }
    }

    /**
     * Save field data to offline storage
     */
    async saveFieldData(fieldData) {
        const data = {
            ...fieldData,
            id: fieldData.id || this.generateId(),
            last_updated: new Date().toISOString()
        };

        await this.saveToStore('fieldData', data);
        
        // Add to sync queue if offline
        if (!this.isOnline) {
            await this.addToSyncQueue('fieldData', data);
        }
    }

    /**
     * Save photo to offline storage
     */
    async savePhoto(photoData) {
        const photo = {
            ...photoData,
            id: photoData.id || this.generateId(),
            created_at: new Date().toISOString(),
            synced: this.isOnline
        };

        await this.saveToStore('photos', photo);
        
        // Add to sync queue if offline
        if (!this.isOnline) {
            await this.addToSyncQueue('photo', photo);
        }
    }

    /**
     * Queue strategy progress for offline storage and sync
     */
    async queueStrategyProgress(entry) {
        const storedEntry = this.prepareStrategyTrackingEntry(entry);
        await this.saveToStore('strategyTracking', storedEntry);

        if (this.isOnline) {
            try {
                await this.syncStrategyProgress(storedEntry);
                return storedEntry;
            } catch (error) {
                console.error('Immediate strategy sync failed, adding to queue:', error);
            }
        }

        await this.addToSyncQueue('strategyProgress', storedEntry);
        return storedEntry;
    }

    /**
     * Prepare strategy tracking entry for persistence
     */
    prepareStrategyTrackingEntry(entry) {
        const stored = {};
        const nowIso = new Date().toISOString();

        stored.client_event_id = entry && entry.client_event_id ? entry.client_event_id : this.generateId();
        stored.strategy_id = entry && entry.strategy_id ? entry.strategy_id : null;
        stored.version_number = entry && entry.version_number ? entry.version_number : 1;
        stored.user_id = entry && entry.user_id ? entry.user_id : null;
        stored.field_id = entry && entry.field_id ? entry.field_id : null;
        stored.activity_type = entry && entry.activity_type ? entry.activity_type : 'recorded';
        stored.status = entry && entry.status ? entry.status : 'recorded';
        stored.activity_timestamp = this.normalizeTimestamp(entry && entry.activity_timestamp ? entry.activity_timestamp : nowIso);
        stored.device_identifier = entry && entry.device_identifier ? entry.device_identifier : null;
        stored.notes = entry && entry.notes ? entry.notes : null;
        stored.captured_offline = entry && typeof entry.captured_offline === 'boolean' ? entry.captured_offline : !this.isOnline;
        stored.gps = this.normalizeGps(entry && entry.gps ? entry.gps : null);
        stored.application = this.normalizeNestedObject(entry && entry.application ? entry.application : null);
        stored.cost_summary = this.normalizeNestedObject(entry && entry.cost_summary ? entry.cost_summary : null);
        stored.yield_summary = this.normalizeNestedObject(entry && entry.yield_summary ? entry.yield_summary : null);
        stored.photos = this.normalizePhotoList(entry && entry.photos ? entry.photos : []);
        stored.attachments = this.normalizeNestedObject(entry && entry.attachments ? entry.attachments : null);
        stored.synced = false;
        stored.activity_id = entry && entry.activity_id ? entry.activity_id : null;
        stored.created_at = nowIso;
        stored.updated_at = nowIso;

        return stored;
    }

    /**
     * Normalize GPS payload
     */
    normalizeGps(gps) {
        if (!gps) {
            return null;
        }

        const normalized = {};
        if (typeof gps.latitude === 'number') {
            normalized.latitude = gps.latitude;
        }
        if (typeof gps.longitude === 'number') {
            normalized.longitude = gps.longitude;
        }
        if (typeof gps.accuracy === 'number') {
            normalized.accuracy = gps.accuracy;
        }

        return normalized;
    }

    /**
     * Normalize nested objects (application, cost, yield, attachments)
     */
    normalizeNestedObject(source) {
        if (!source) {
            return {};
        }

        const target = {};
        for (const key in source) {
            if (Object.prototype.hasOwnProperty.call(source, key)) {
                const value = source[key];
                if (value instanceof Date) {
                    target[key] = value.toISOString();
                } else {
                    target[key] = value;
                }
            }
        }
        return target;
    }

    /**
     * Normalize photo metadata list
     */
    normalizePhotoList(photos) {
        const normalized = [];
        if (!photos) {
            return normalized;
        }

        let index = 0;
        while (index < photos.length) {
            const photo = photos[index];
            if (photo) {
                const photoEntry = {};
                for (const key in photo) {
                    if (Object.prototype.hasOwnProperty.call(photo, key)) {
                        let value = photo[key];
                        if (value instanceof Date) {
                            value = value.toISOString();
                        }
                        if (key === 'captured_at') {
                            value = this.normalizeTimestamp(value);
                        }
                        photoEntry[key] = value;
                    }
                }
                normalized.push(photoEntry);
            }
            index += 1;
        }

        return normalized;
    }

    /**
     * Normalize timestamp values to ISO 8601 strings
     */
    normalizeTimestamp(value) {
        if (!value) {
            return new Date().toISOString();
        }

        if (value instanceof Date) {
            return value.toISOString();
        }

        if (typeof value === 'number') {
            return new Date(value).toISOString();
        }

        if (typeof value === 'string') {
            const parsed = Date.parse(value);
            if (!isNaN(parsed)) {
                return new Date(parsed).toISOString();
            }
        }

        return new Date().toISOString();
    }

    /**
     * Sync strategy progress entry with backend
     */
    async syncStrategyProgress(entry) {
        const payload = this.prepareStrategyPayload(entry);

        const response = await fetch('/api/v1/mobile-strategy/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error('Failed to sync strategy progress');
        }

        const result = await response.json();
        const statusValue = result && result.status ? result.status : entry.status;
        const activityId = result && result.activity_id ? result.activity_id : entry.activity_id;
        await this.markStrategyTrackingSynced(entry.client_event_id, activityId, statusValue);
        return result;
    }

    /**
     * Prepare API payload for strategy progress
     */
    prepareStrategyPayload(entry) {
        const payload = {};

        payload.client_event_id = entry.client_event_id;
        payload.strategy_id = entry.strategy_id;
        payload.version_number = entry.version_number;
        payload.user_id = entry.user_id;
        if (entry.field_id) {
            payload.field_id = entry.field_id;
        }
        payload.activity_type = entry.activity_type || 'recorded';
        payload.status = entry.status || 'recorded';
        payload.activity_timestamp = this.normalizeTimestamp(entry.activity_timestamp);
        if (entry.device_identifier) {
            payload.device_identifier = entry.device_identifier;
        }
        if (entry.notes) {
            payload.notes = entry.notes;
        }
        payload.captured_offline = entry.captured_offline === true;

        if (entry.gps && Object.keys(entry.gps).length > 0) {
            payload.gps = entry.gps;
        }
        if (entry.application && Object.keys(entry.application).length > 0) {
            payload.application = entry.application;
        }
        if (entry.cost_summary && Object.keys(entry.cost_summary).length > 0) {
            payload.cost_summary = entry.cost_summary;
        }
        if (entry.yield_summary && Object.keys(entry.yield_summary).length > 0) {
            payload.yield_summary = entry.yield_summary;
        }

        payload.photos = [];
        if (entry.photos) {
            let photoIndex = 0;
            while (photoIndex < entry.photos.length) {
                const photo = entry.photos[photoIndex];
                if (photo) {
                    payload.photos.push(photo);
                }
                photoIndex += 1;
            }
        }

        if (entry.attachments && Object.keys(entry.attachments).length > 0) {
            payload.attachments = entry.attachments;
        }

        return payload;
    }

    /**
     * Retrieve pending strategy tracking entries
     */
    async getPendingStrategyTrackingEntries() {
        const entries = await this.getAllFromStore('strategyTracking');
        const pending = [];

        let index = 0;
        while (index < entries.length) {
            const record = entries[index];
            if (record && !record.synced) {
                pending.push(record);
            }
            index += 1;
        }

        return pending;
    }

    /**
     * Mark strategy tracking entry as synced
     */
    async markStrategyTrackingSynced(clientEventId, activityId, status) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['strategyTracking'], 'readwrite');
            const store = transaction.objectStore('strategyTracking');
            const request = store.get(clientEventId);

            request.onsuccess = () => {
                const record = request.result;
                if (!record) {
                    resolve(false);
                    return;
                }

                record.synced = true;
                record.activity_id = activityId || record.activity_id;
                record.status = status || record.status;
                record.synced_at = new Date().toISOString();
                record.updated_at = new Date().toISOString();

                const updateRequest = store.put(record);
                updateRequest.onsuccess = () => resolve(true);
                updateRequest.onerror = () => reject(updateRequest.error);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Save user preference
     */
    async savePreference(key, value) {
        const preference = {
            key,
            value,
            last_updated: new Date().toISOString()
        };

        await this.saveToStore('preferences', preference);
    }

    /**
     * Get user preference
     */
    async getPreference(key) {
        const preference = await this.getFromStore('preferences', key);
        return preference ? preference.value : null;
    }

    /**
     * Add item to sync queue
     */
    async addToSyncQueue(type, data) {
        const syncItem = {
            type,
            data,
            timestamp: new Date().toISOString(),
            retryCount: 0
        };

        await this.saveToStore('syncQueue', syncItem);
    }

    /**
     * Sync offline data
     */
    async syncOfflineData() {
        if (!this.isOnline) return;

        try {
            const syncItems = await this.getAllFromStore('syncQueue');
            
            for (const item of syncItems) {
                try {
                    await this.syncItem(item);
                    await this.removeFromStore('syncQueue', item.id);
                } catch (error) {
                    console.error('Sync error for item:', item, error);
                    item.retryCount++;
                    
                    if (item.retryCount < 3) {
                        await this.saveToStore('syncQueue', item);
                    } else {
                        await this.removeFromStore('syncQueue', item.id);
                    }
                }
            }

            this.showNotification('Data synchronized successfully', { type: 'success' });
        } catch (error) {
            console.error('Error syncing offline data:', error);
            this.showNotification('Sync failed - will retry later', { type: 'error' });
        }
    }

    /**
     * Sync individual item
     */
    async syncItem(item) {
        const { type, data } = item;

        switch (type) {
            case 'variety':
                await this.syncVariety(data);
                break;
            case 'recommendation':
                await this.syncRecommendation(data);
                break;
            case 'fieldData':
                await this.syncFieldData(data);
                break;
            case 'photo':
                await this.syncPhoto(data);
                break;
            case 'strategyProgress':
                await this.syncStrategyProgress(data);
                break;
        }
    }

    /**
     * Sync variety data
     */
    async syncVariety(varietyData) {
        const response = await fetch('/api/v1/varieties', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(varietyData)
        });

        if (!response.ok) {
            throw new Error(`Failed to sync variety: ${response.statusText}`);
        }
    }

    /**
     * Sync recommendation data
     */
    async syncRecommendation(recommendationData) {
        const response = await fetch('/api/v1/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(recommendationData)
        });

        if (!response.ok) {
            throw new Error(`Failed to sync recommendation: ${response.statusText}`);
        }
    }

    /**
     * Sync field data
     */
    async syncFieldData(fieldData) {
        const response = await fetch('/api/v1/fields', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(fieldData)
        });

        if (!response.ok) {
            throw new Error(`Failed to sync field data: ${response.statusText}`);
        }
    }

    /**
     * Sync photo data
     */
    async syncPhoto(photoData) {
        const formData = new FormData();
        formData.append('photo', photoData.blob);
        formData.append('metadata', JSON.stringify(photoData.metadata));

        const response = await fetch('/api/v1/photos', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Failed to sync photo: ${response.statusText}`);
        }
    }

    /**
     * Enable data saving mode
     */
    enableDataSavingMode() {
        // Reduce data usage, disable auto-sync, etc.
        this.showNotification('Data saving mode enabled', { type: 'info' });
    }

    /**
     * Enable low bandwidth mode
     */
    enableLowBandwidthMode() {
        // Reduce data usage, disable animations, etc.
        this.showNotification('Low bandwidth mode enabled', { type: 'info' });
    }

    /**
     * Handle sync complete
     */
    handleSyncComplete(data) {
        console.log('Sync completed:', data);
    }

    /**
     * Handle sync error
     */
    handleSyncError(data) {
        console.error('Sync error:', data);
        this.showNotification('Sync error occurred', { type: 'error' });
    }

    /**
     * Handle cache updated
     */
    handleCacheUpdated(data) {
        console.log('Cache updated:', data);
        this.showNotification('App updated - new features available', { type: 'success' });
    }

    /**
     * Generic save to store
     */
    async saveToStore(storeName, data) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Generic get from store
     */
    async getFromStore(storeName, key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Generic get all from store
     */
    async getAllFromStore(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Generic remove from store
     */
    async removeFromStore(storeName, key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Show notification
     */
    showNotification(message, options = {}) {
        if (this.deviceIntegration) {
            this.deviceIntegration.showNotification(message, options);
        }
    }

    /**
     * Get database statistics
     */
    async getDatabaseStats() {
        const stats = {};
        
        const stores = ['varieties', 'recommendations', 'preferences', 'syncQueue', 'fieldData', 'photos', 'strategyTracking'];
        
        for (const storeName of stores) {
            const items = await this.getAllFromStore(storeName);
            stats[storeName] = items.length;
        }
        
        return stats;
    }

    /**
     * Clear all data
     */
    async clearAllData() {
        const stores = ['varieties', 'recommendations', 'preferences', 'syncQueue', 'fieldData', 'photos', 'strategyTracking'];
        
        for (const storeName of stores) {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            await store.clear();
        }
        
        this.showNotification('All offline data cleared', { type: 'success' });
    }
}

// Export for use in other modules
window.MobileOfflineDatabase = MobileOfflineDatabase;
