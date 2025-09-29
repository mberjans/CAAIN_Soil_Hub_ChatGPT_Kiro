/**
 * Mobile PWA Features Module
 * 
 * Provides comprehensive Progressive Web App features including:
 * - App installation and lifecycle management
 * - Advanced offline functionality
 * - Background sync and data synchronization
 * - Push notifications and user engagement
 * - Native device feature integration
 * - Performance optimization and caching
 * - File system access and sharing
 */

class MobilePWAFeatures {
    constructor() {
        this.isInstalled = false;
        this.isOnline = navigator.onLine;
        this.deferredPrompt = null;
        this.registration = null;
        this.syncManager = null;
        this.notificationManager = null;
        this.fileSystemManager = null;
        this.performanceMonitor = null;
        
        this.init();
    }

    async init() {
        console.log('Initializing Mobile PWA Features...');
        
        try {
            await this.registerServiceWorker();
            await this.setupAppInstallation();
            await this.initializeBackgroundSync();
            await this.setupPushNotifications();
            await this.initializeFileSystemAccess();
            await this.setupPerformanceMonitoring();
            await this.setupOfflineDetection();
            await this.setupAppLifecycle();
            
            console.log('Mobile PWA Features initialized successfully');
        } catch (error) {
            console.error('Failed to initialize PWA features:', error);
        }
    }

    /**
     * Register service worker for PWA functionality
     */
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                this.registration = await navigator.serviceWorker.register('/static/sw.js', {
                    scope: '/'
                });
                
                console.log('Service Worker registered:', this.registration);
                
                // Handle service worker updates
                this.registration.addEventListener('updatefound', () => {
                    const newWorker = this.registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
                
                // Listen for messages from service worker
                navigator.serviceWorker.addEventListener('message', (event) => {
                    this.handleServiceWorkerMessage(event.data);
                });
                
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    /**
     * Setup app installation prompts and management
     */
    async setupAppInstallation() {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (event) => {
            console.log('App installation prompt available');
            event.preventDefault();
            this.deferredPrompt = event;
            this.showInstallButton();
        });

        // Listen for app installed event
        window.addEventListener('appinstalled', (event) => {
            console.log('App installed successfully');
            this.isInstalled = true;
            this.hideInstallButton();
            this.trackAppInstallation();
        });

        // Check if app is already installed
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('App is running in standalone mode');
        }
    }

    /**
     * Initialize background sync for offline data
     */
    async initializeBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            this.syncManager = new BackgroundSyncManager();
            await this.syncManager.initialize();
        }
    }

    /**
     * Setup push notifications
     */
    async setupPushNotifications() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            this.notificationManager = new NotificationManager();
            await this.notificationManager.initialize();
        }
    }

    /**
     * Initialize file system access for PWA
     */
    async initializeFileSystemAccess() {
        if ('showOpenFilePicker' in window || 'showSaveFilePicker' in window) {
            this.fileSystemManager = new FileSystemManager();
            await this.fileSystemManager.initialize();
        }
    }

    /**
     * Setup performance monitoring
     */
    async setupPerformanceMonitoring() {
        this.performanceMonitor = new PerformanceMonitor();
        await this.performanceMonitor.initialize();
    }

    /**
     * Setup offline detection and handling
     */
    async setupOfflineDetection() {
        window.addEventListener('online', () => {
            console.log('App is online');
            this.isOnline = true;
            this.handleOnlineStatus();
        });

        window.addEventListener('offline', () => {
            console.log('App is offline');
            this.isOnline = false;
            this.handleOfflineStatus();
        });

        // Initial status check
        this.isOnline = navigator.onLine;
        if (!this.isOnline) {
            this.handleOfflineStatus();
        }
    }

    /**
     * Setup app lifecycle management
     */
    async setupAppLifecycle() {
        // Handle app visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handleAppBackground();
            } else {
                this.handleAppForeground();
            }
        });

        // Handle page unload
        window.addEventListener('beforeunload', () => {
            this.handleAppUnload();
        });

        // Handle app focus/blur
        window.addEventListener('focus', () => {
            this.handleAppFocus();
        });

        window.addEventListener('blur', () => {
            this.handleAppBlur();
        });
    }

    /**
     * Show install button when app can be installed
     */
    showInstallButton() {
        const installButton = document.getElementById('install-app-button');
        if (installButton) {
            installButton.style.display = 'block';
            installButton.addEventListener('click', () => {
                this.installApp();
            });
        }
    }

    /**
     * Hide install button
     */
    hideInstallButton() {
        const installButton = document.getElementById('install-app-button');
        if (installButton) {
            installButton.style.display = 'none';
        }
    }

    /**
     * Install the app
     */
    async installApp() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            console.log('Install prompt outcome:', outcome);
            this.deferredPrompt = null;
        }
    }

    /**
     * Handle online status
     */
    async handleOnlineStatus() {
        // Show online indicator
        this.showStatusIndicator('online', 'Connected');
        
        // Trigger background sync
        if (this.syncManager) {
            await this.syncManager.syncAll();
        }
        
        // Refresh critical data
        await this.refreshCriticalData();
    }

    /**
     * Handle offline status
     */
    handleOfflineStatus() {
        // Show offline indicator
        this.showStatusIndicator('offline', 'Offline Mode');
        
        // Enable offline features
        this.enableOfflineMode();
    }

    /**
     * Show status indicator
     */
    showStatusIndicator(status, message) {
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `status-indicator ${status}`;
            indicator.textContent = message;
            indicator.style.display = 'block';
            
            // Hide after 3 seconds
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 3000);
        }
    }

    /**
     * Enable offline mode features
     */
    enableOfflineMode() {
        // Show offline banner
        this.showOfflineBanner();
        
        // Disable online-only features
        this.disableOnlineFeatures();
        
        // Enable offline alternatives
        this.enableOfflineAlternatives();
    }

    /**
     * Show offline banner
     */
    showOfflineBanner() {
        const banner = document.getElementById('offline-banner');
        if (banner) {
            banner.style.display = 'block';
        }
    }

    /**
     * Hide offline banner
     */
    hideOfflineBanner() {
        const banner = document.getElementById('offline-banner');
        if (banner) {
            banner.style.display = 'none';
        }
    }

    /**
     * Disable online-only features
     */
    disableOnlineFeatures() {
        const onlineElements = document.querySelectorAll('[data-online-only]');
        onlineElements.forEach(element => {
            element.disabled = true;
            element.classList.add('offline-disabled');
        });
    }

    /**
     * Enable offline alternatives
     */
    enableOfflineAlternatives() {
        const offlineElements = document.querySelectorAll('[data-offline-alternative]');
        offlineElements.forEach(element => {
            element.style.display = 'block';
        });
    }

    /**
     * Refresh critical data when online
     */
    async refreshCriticalData() {
        try {
            // Refresh variety data
            await this.refreshVarietyData();
            
            // Refresh user preferences
            await this.refreshUserPreferences();
            
            // Refresh field data
            await this.refreshFieldData();
            
        } catch (error) {
            console.error('Failed to refresh critical data:', error);
        }
    }

    /**
     * Refresh variety data
     */
    async refreshVarietyData() {
        try {
            const response = await fetch('/api/v1/crop-taxonomy/varieties');
            if (response.ok) {
                const data = await response.json();
                // Cache for offline use
                if (this.registration) {
                    this.registration.active.postMessage({
                        type: 'CACHE_VARIETY_DATA',
                        data: data
                    });
                }
            }
        } catch (error) {
            console.error('Failed to refresh variety data:', error);
        }
    }

    /**
     * Refresh user preferences
     */
    async refreshUserPreferences() {
        try {
            const response = await fetch('/api/v1/user/preferences');
            if (response.ok) {
                const preferences = await response.json();
                localStorage.setItem('userPreferences', JSON.stringify(preferences));
            }
        } catch (error) {
            console.error('Failed to refresh user preferences:', error);
        }
    }

    /**
     * Refresh field data
     */
    async refreshFieldData() {
        try {
            const response = await fetch('/api/v1/fields');
            if (response.ok) {
                const fields = await response.json();
                localStorage.setItem('fieldData', JSON.stringify(fields));
            }
        } catch (error) {
            console.error('Failed to refresh field data:', error);
        }
    }

    /**
     * Handle service worker messages
     */
    handleServiceWorkerMessage(data) {
        switch (data.type) {
            case 'SYNC_COMPLETE':
                this.handleSyncComplete(data.data);
                break;
            case 'CACHE_UPDATED':
                this.handleCacheUpdated(data.data);
                break;
            case 'NOTIFICATION_RECEIVED':
                this.handleNotificationReceived(data.data);
                break;
            default:
                console.log('Unknown service worker message:', data);
        }
    }

    /**
     * Handle sync completion
     */
    handleSyncComplete(data) {
        console.log('Background sync completed:', data);
        this.showSyncCompleteNotification();
    }

    /**
     * Handle cache updates
     */
    handleCacheUpdated(data) {
        console.log('Cache updated:', data);
        // Refresh UI if needed
        this.refreshUI();
    }

    /**
     * Handle notification received
     */
    handleNotificationReceived(data) {
        console.log('Notification received:', data);
        // Handle in-app notification
        this.showInAppNotification(data);
    }

    /**
     * Show sync complete notification
     */
    showSyncCompleteNotification() {
        const notification = document.createElement('div');
        notification.className = 'sync-notification';
        notification.innerHTML = `
            <div class="sync-icon">✓</div>
            <div class="sync-message">Data synchronized successfully</div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    /**
     * Show in-app notification
     */
    showInAppNotification(data) {
        const notification = document.createElement('div');
        notification.className = 'in-app-notification';
        notification.innerHTML = `
            <div class="notification-icon">📱</div>
            <div class="notification-content">
                <div class="notification-title">${data.title}</div>
                <div class="notification-message">${data.message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * Refresh UI elements
     */
    refreshUI() {
        // Trigger custom refresh event
        const event = new CustomEvent('pwaRefresh');
        document.dispatchEvent(event);
    }

    /**
     * Handle app background
     */
    handleAppBackground() {
        console.log('App moved to background');
        // Pause non-essential operations
        this.pauseNonEssentialOperations();
    }

    /**
     * Handle app foreground
     */
    handleAppForeground() {
        console.log('App moved to foreground');
        // Resume operations
        this.resumeOperations();
        
        // Check for updates
        this.checkForUpdates();
    }

    /**
     * Handle app focus
     */
    handleAppFocus() {
        console.log('App gained focus');
        // Refresh data if needed
        if (this.isOnline) {
            this.refreshCriticalData();
        }
    }

    /**
     * Handle app blur
     */
    handleAppBlur() {
        console.log('App lost focus');
        // Save current state
        this.saveAppState();
    }

    /**
     * Handle app unload
     */
    handleAppUnload() {
        console.log('App unloading');
        // Save final state
        this.saveAppState();
    }

    /**
     * Pause non-essential operations
     */
    pauseNonEssentialOperations() {
        // Pause animations, timers, etc.
        const animations = document.querySelectorAll('[data-animation]');
        animations.forEach(animation => {
            animation.style.animationPlayState = 'paused';
        });
    }

    /**
     * Resume operations
     */
    resumeOperations() {
        // Resume animations, timers, etc.
        const animations = document.querySelectorAll('[data-animation]');
        animations.forEach(animation => {
            animation.style.animationPlayState = 'running';
        });
    }

    /**
     * Check for updates
     */
    async checkForUpdates() {
        if (this.registration) {
            try {
                await this.registration.update();
            } catch (error) {
                console.error('Failed to check for updates:', error);
            }
        }
    }

    /**
     * Save app state
     */
    saveAppState() {
        const appState = {
            timestamp: Date.now(),
            currentPage: window.location.pathname,
            userData: this.getUserData(),
            formData: this.getFormData()
        };
        
        localStorage.setItem('appState', JSON.stringify(appState));
    }

    /**
     * Get user data
     */
    getUserData() {
        return {
            preferences: localStorage.getItem('userPreferences'),
            fieldData: localStorage.getItem('fieldData'),
            varietySelections: localStorage.getItem('varietySelections')
        };
    }

    /**
     * Get form data
     */
    getFormData() {
        const forms = document.querySelectorAll('form');
        const formData = {};
        
        forms.forEach((form, index) => {
            const data = new FormData(form);
            formData[`form_${index}`] = Object.fromEntries(data);
        });
        
        return formData;
    }

    /**
     * Show update notification
     */
    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <div class="update-icon">🔄</div>
                <div class="update-message">App update available</div>
                <button class="update-button" onclick="this.updateApp()">Update Now</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Add update functionality
        notification.querySelector('.update-button').updateApp = () => {
            this.updateApp();
            notification.remove();
        };
    }

    /**
     * Update the app
     */
    updateApp() {
        if (this.registration && this.registration.waiting) {
            this.registration.waiting.postMessage({ type: 'SKIP_WAITING' });
            window.location.reload();
        }
    }

    /**
     * Track app installation
     */
    trackAppInstallation() {
        // Send analytics event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'app_installed', {
                event_category: 'PWA',
                event_label: 'Mobile Variety Selection'
            });
        }
        
        // Store installation timestamp
        localStorage.setItem('appInstalled', Date.now().toString());
    }

    /**
     * Get app installation status
     */
    getInstallationStatus() {
        return {
            isInstalled: this.isInstalled,
            installTimestamp: localStorage.getItem('appInstalled'),
            canInstall: !!this.deferredPrompt
        };
    }

    /**
     * Get PWA capabilities
     */
    getPWACapabilities() {
        return {
            serviceWorker: 'serviceWorker' in navigator,
            pushNotifications: 'PushManager' in window,
            backgroundSync: 'sync' in window.ServiceWorkerRegistration.prototype,
            fileSystemAccess: 'showOpenFilePicker' in window,
            webShare: 'share' in navigator,
            clipboard: 'clipboard' in navigator,
            geolocation: 'geolocation' in navigator,
            camera: 'mediaDevices' in navigator,
            offlineStorage: 'indexedDB' in window
        };
    }
}

/**
 * Background Sync Manager
 */
class BackgroundSyncManager {
    constructor() {
        this.syncTags = [
            'save-recommendations',
            'sync-varieties',
            'sync-field-data',
            'sync-photos'
        ];
    }

    async initialize() {
        console.log('Background Sync Manager initialized');
    }

    async syncAll() {
        for (const tag of this.syncTags) {
            await this.registerSync(tag);
        }
    }

    async registerSync(tag) {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            try {
                const registration = await navigator.serviceWorker.ready;
                await registration.sync.register(tag);
                console.log(`Background sync registered: ${tag}`);
            } catch (error) {
                console.error(`Failed to register sync ${tag}:`, error);
            }
        }
    }
}

/**
 * Notification Manager
 */
class NotificationManager {
    constructor() {
        this.permission = 'default';
    }

    async initialize() {
        this.permission = Notification.permission;
        console.log('Notification Manager initialized');
    }

    async requestPermission() {
        if ('Notification' in window) {
            this.permission = await Notification.requestPermission();
            return this.permission === 'granted';
        }
        return false;
    }

    async subscribeToPush() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
                });
                
                // Send subscription to server
                await this.sendSubscriptionToServer(subscription);
                return subscription;
            } catch (error) {
                console.error('Failed to subscribe to push notifications:', error);
                return null;
            }
        }
        return null;
    }

    async sendSubscriptionToServer(subscription) {
        try {
            await fetch('/api/v1/notifications/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subscription)
            });
        } catch (error) {
            console.error('Failed to send subscription to server:', error);
        }
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
}

/**
 * File System Manager
 */
class FileSystemManager {
    constructor() {
        this.supportedFeatures = {
            openFile: 'showOpenFilePicker' in window,
            saveFile: 'showSaveFilePicker' in window,
            directoryAccess: 'showDirectoryPicker' in window
        };
    }

    async initialize() {
        console.log('File System Manager initialized');
    }

    async openFile(accept = {}) {
        if (this.supportedFeatures.openFile) {
            try {
                const [fileHandle] = await window.showOpenFilePicker({
                    types: [{
                        description: 'Agricultural Data Files',
                        accept: accept
                    }]
                });
                return await fileHandle.getFile();
            } catch (error) {
                console.error('Failed to open file:', error);
                return null;
            }
        }
        return null;
    }

    async saveFile(data, filename, type = 'application/json') {
        if (this.supportedFeatures.saveFile) {
            try {
                const fileHandle = await window.showSaveFilePicker({
                    suggestedName: filename,
                    types: [{
                        description: 'Agricultural Data Files',
                        accept: { [type]: [`.${filename.split('.').pop()}`] }
                    }]
                });
                
                const writable = await fileHandle.createWritable();
                await writable.write(data);
                await writable.close();
                
                return fileHandle;
            } catch (error) {
                console.error('Failed to save file:', error);
                return null;
            }
        }
        return null;
    }
}

/**
 * Performance Monitor
 */
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
    }

    async initialize() {
        console.log('Performance Monitor initialized');
        this.startMonitoring();
    }

    startMonitoring() {
        // Monitor Core Web Vitals
        this.monitorCoreWebVitals();
        
        // Monitor resource loading
        this.monitorResourceLoading();
        
        // Monitor user interactions
        this.monitorUserInteractions();
    }

    monitorCoreWebVitals() {
        // Largest Contentful Paint (LCP)
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            this.metrics.lcp = lastEntry.startTime;
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay (FID)
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            entries.forEach((entry) => {
                this.metrics.fid = entry.processingStart - entry.startTime;
            });
        }).observe({ entryTypes: ['first-input'] });

        // Cumulative Layout Shift (CLS)
        let clsValue = 0;
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            entries.forEach((entry) => {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            });
            this.metrics.cls = clsValue;
        }).observe({ entryTypes: ['layout-shift'] });
    }

    monitorResourceLoading() {
        window.addEventListener('load', () => {
            const navigation = performance.getEntriesByType('navigation')[0];
            this.metrics.pageLoadTime = navigation.loadEventEnd - navigation.fetchStart;
            this.metrics.domContentLoaded = navigation.domContentLoadedEventEnd - navigation.fetchStart;
        });
    }

    monitorUserInteractions() {
        let interactionCount = 0;
        document.addEventListener('click', () => {
            interactionCount++;
            this.metrics.interactionCount = interactionCount;
        });
    }

    getMetrics() {
        return { ...this.metrics };
    }

    reportMetrics() {
        const metrics = this.getMetrics();
        console.log('Performance Metrics:', metrics);
        
        // Send to analytics if available
        if (typeof gtag !== 'undefined') {
            Object.entries(metrics).forEach(([key, value]) => {
                gtag('event', 'performance_metric', {
                    event_category: 'Performance',
                    event_label: key,
                    value: Math.round(value)
                });
            });
        }
    }
}

// Initialize PWA features when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.mobilePWAFeatures = new MobilePWAFeatures();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MobilePWAFeatures };
}
