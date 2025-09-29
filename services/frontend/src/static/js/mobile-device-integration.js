/**
 * Mobile Device Integration Module
 * 
 * Provides comprehensive device integration for mobile agricultural applications
 * including camera, GPS, sensors, and push notifications.
 */

class MobileDeviceIntegration {
    constructor() {
        this.camera = null;
        this.gps = null;
        this.sensors = {};
        this.notifications = null;
        this.deviceCapabilities = {};
        this.permissions = {};
        
        this.init();
    }

    async init() {
        await this.checkDeviceCapabilities();
        await this.requestPermissions();
        this.setupEventListeners();
    }

    /**
     * Check device capabilities and initialize available features
     */
    async checkDeviceCapabilities() {
        this.deviceCapabilities = {
            camera: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
            gps: 'geolocation' in navigator,
            accelerometer: 'Accelerometer' in window,
            gyroscope: 'Gyroscope' in window,
            magnetometer: 'Magnetometer' in window,
            notifications: 'Notification' in window && 'serviceWorker' in navigator,
            vibration: 'vibrate' in navigator,
            battery: 'getBattery' in navigator,
            connection: 'connection' in navigator,
            storage: 'storage' in navigator && 'estimate' in navigator.storage
        };

        console.log('Device capabilities:', this.deviceCapabilities);
    }

    /**
     * Request necessary permissions for device features
     */
    async requestPermissions() {
        const permissions = [];

        if (this.deviceCapabilities.camera) {
            permissions.push(this.requestCameraPermission());
        }

        if (this.deviceCapabilities.gps) {
            permissions.push(this.requestLocationPermission());
        }

        if (this.deviceCapabilities.notifications) {
            permissions.push(this.requestNotificationPermission());
        }

        try {
            const results = await Promise.allSettled(permissions);
            results.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    console.log(`Permission ${index} granted`);
                } else {
                    console.warn(`Permission ${index} denied:`, result.reason);
                }
            });
        } catch (error) {
            console.error('Error requesting permissions:', error);
        }
    }

    /**
     * Request camera permission
     */
    async requestCameraPermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment', // Use back camera
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                } 
            });
            
            // Stop the stream immediately - we just needed permission
            stream.getTracks().forEach(track => track.stop());
            
            this.permissions.camera = true;
            return true;
        } catch (error) {
            console.error('Camera permission denied:', error);
            this.permissions.camera = false;
            return false;
        }
    }

    /**
     * Request location permission
     */
    async requestLocationPermission() {
        return new Promise((resolve) => {
            if (!navigator.geolocation) {
                this.permissions.location = false;
                resolve(false);
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.permissions.location = true;
                    resolve(true);
                },
                (error) => {
                    console.error('Location permission denied:', error);
                    this.permissions.location = false;
                    resolve(false);
                },
                { timeout: 5000, enableHighAccuracy: true }
            );
        });
    }

    /**
     * Request notification permission
     */
    async requestNotificationPermission() {
        try {
            const permission = await Notification.requestPermission();
            this.permissions.notifications = permission === 'granted';
            return this.permissions.notifications;
        } catch (error) {
            console.error('Notification permission error:', error);
            this.permissions.notifications = false;
            return false;
        }
    }

    /**
     * Setup event listeners for device events
     */
    setupEventListeners() {
        // Battery status monitoring
        if (this.deviceCapabilities.battery) {
            this.setupBatteryMonitoring();
        }

        // Network status monitoring
        if (this.deviceCapabilities.connection) {
            this.setupNetworkMonitoring();
        }

        // Storage monitoring
        if (this.deviceCapabilities.storage) {
            this.setupStorageMonitoring();
        }

        // Device orientation changes
        window.addEventListener('orientationchange', this.handleOrientationChange.bind(this));
        
        // App visibility changes
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
    }

    /**
     * Setup battery monitoring
     */
    async setupBatteryMonitoring() {
        try {
            const battery = await navigator.getBattery();
            
            battery.addEventListener('levelchange', () => {
                this.handleBatteryLevelChange(battery.level);
            });

            battery.addEventListener('chargingchange', () => {
                this.handleBatteryChargingChange(battery.charging);
            });

            // Initial battery status
            this.handleBatteryLevelChange(battery.level);
            this.handleBatteryChargingChange(battery.charging);
        } catch (error) {
            console.error('Battery monitoring setup failed:', error);
        }
    }

    /**
     * Setup network monitoring
     */
    setupNetworkMonitoring() {
        const connection = navigator.connection;
        
        connection.addEventListener('change', () => {
            this.handleNetworkChange({
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            });
        });

        // Initial network status
        this.handleNetworkChange({
            effectiveType: connection.effectiveType,
            downlink: connection.downlink,
            rtt: connection.rtt,
            saveData: connection.saveData
        });
    }

    /**
     * Setup storage monitoring
     */
    async setupStorageMonitoring() {
        try {
            const estimate = await navigator.storage.estimate();
            this.handleStorageChange(estimate);
            
            // Monitor storage changes
            navigator.storage.addEventListener('change', async () => {
                const newEstimate = await navigator.storage.estimate();
                this.handleStorageChange(newEstimate);
            });
        } catch (error) {
            console.error('Storage monitoring setup failed:', error);
        }
    }

    /**
     * Handle battery level changes
     */
    handleBatteryLevelChange(level) {
        const batteryPercentage = Math.round(level * 100);
        
        // Emit custom event
        this.emit('batteryLevelChange', { level: batteryPercentage });
        
        // Show low battery warning
        if (batteryPercentage < 20) {
            this.showLowBatteryWarning(batteryPercentage);
        }
    }

    /**
     * Handle battery charging status changes
     */
    handleBatteryChargingChange(charging) {
        this.emit('batteryChargingChange', { charging });
    }

    /**
     * Handle network changes
     */
    handleNetworkChange(networkInfo) {
        this.emit('networkChange', networkInfo);
        
        // Adjust app behavior based on network conditions
        if (networkInfo.saveData) {
            this.enableDataSavingMode();
        }
        
        if (networkInfo.effectiveType === 'slow-2g' || networkInfo.effectiveType === '2g') {
            this.enableLowBandwidthMode();
        }
    }

    /**
     * Handle storage changes
     */
    handleStorageChange(storageInfo) {
        const usedPercentage = (storageInfo.usage / storageInfo.quota) * 100;
        
        this.emit('storageChange', {
            used: storageInfo.usage,
            quota: storageInfo.quota,
            percentage: usedPercentage
        });
        
        // Show storage warning
        if (usedPercentage > 80) {
            this.showStorageWarning(usedPercentage);
        }
    }

    /**
     * Handle device orientation changes
     */
    handleOrientationChange() {
        const orientation = screen.orientation ? screen.orientation.type : 'unknown';
        this.emit('orientationChange', { orientation });
        
        // Adjust UI for orientation
        this.adjustUIForOrientation(orientation);
    }

    /**
     * Handle app visibility changes
     */
    handleVisibilityChange() {
        const isVisible = !document.hidden;
        this.emit('visibilityChange', { visible: isVisible });
        
        if (isVisible) {
            this.resumeApp();
        } else {
            this.pauseApp();
        }
    }

    /**
     * Show low battery warning
     */
    showLowBatteryWarning(level) {
        this.showNotification(`Low battery: ${level}% remaining`, {
            type: 'warning',
            duration: 5000
        });
    }

    /**
     * Show storage warning
     */
    showStorageWarning(percentage) {
        this.showNotification(`Storage almost full: ${Math.round(percentage)}% used`, {
            type: 'warning',
            duration: 5000
        });
    }

    /**
     * Enable data saving mode
     */
    enableDataSavingMode() {
        // Reduce image quality, disable auto-sync, etc.
        this.emit('dataSavingModeEnabled');
    }

    /**
     * Enable low bandwidth mode
     */
    enableLowBandwidthMode() {
        // Reduce data usage, disable animations, etc.
        this.emit('lowBandwidthModeEnabled');
    }

    /**
     * Adjust UI for device orientation
     */
    adjustUIForOrientation(orientation) {
        const isLandscape = orientation.includes('landscape');
        
        if (isLandscape) {
            document.body.classList.add('landscape-mode');
            document.body.classList.remove('portrait-mode');
        } else {
            document.body.classList.add('portrait-mode');
            document.body.classList.remove('landscape-mode');
        }
    }

    /**
     * Resume app when it becomes visible
     */
    resumeApp() {
        // Resume background tasks, refresh data, etc.
        this.emit('appResumed');
    }

    /**
     * Pause app when it becomes hidden
     */
    pauseApp() {
        // Pause background tasks, save state, etc.
        this.emit('appPaused');
    }

    /**
     * Show notification
     */
    showNotification(message, options = {}) {
        const {
            type = 'info',
            duration = 3000,
            persistent = false
        } = options;

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `mobile-notification mobile-notification-${type}`;
        notification.textContent = message;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-hide if not persistent
        if (!persistent) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, duration);
        }
        
        // Vibrate if supported
        if (this.deviceCapabilities.vibration) {
            navigator.vibrate(200);
        }
    }

    /**
     * Emit custom events
     */
    emit(eventName, data) {
        const event = new CustomEvent(`mobileDevice:${eventName}`, {
            detail: data
        });
        document.dispatchEvent(event);
    }

    /**
     * Get current device information
     */
    getDeviceInfo() {
        return {
            capabilities: this.deviceCapabilities,
            permissions: this.permissions,
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screen: {
                width: screen.width,
                height: screen.height,
                orientation: screen.orientation ? screen.orientation.type : 'unknown'
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
    }

    /**
     * Check if feature is available
     */
    isFeatureAvailable(feature) {
        return this.deviceCapabilities[feature] === true;
    }

    /**
     * Check if permission is granted
     */
    hasPermission(permission) {
        return this.permissions[permission] === true;
    }
}

// Export for use in other modules
window.MobileDeviceIntegration = MobileDeviceIntegration;

// CSS for notifications
const notificationStyles = `
.mobile-notification {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%) translateY(-100px);
    background: rgba(0, 0, 0, 0.9);
    color: white;
    padding: 12px 20px;
    border-radius: 25px;
    font-size: 14px;
    font-weight: 500;
    z-index: 10000;
    transition: transform 0.3s ease;
    max-width: 90%;
    text-align: center;
    backdrop-filter: blur(10px);
}

.mobile-notification.show {
    transform: translateX(-50%) translateY(0);
}

.mobile-notification-info {
    background: rgba(23, 162, 184, 0.9);
}

.mobile-notification-warning {
    background: rgba(255, 193, 7, 0.9);
    color: #000;
}

.mobile-notification-error {
    background: rgba(220, 53, 69, 0.9);
}

.mobile-notification-success {
    background: rgba(40, 167, 69, 0.9);
}

.landscape-mode .mobile-notification {
    top: 10px;
    font-size: 12px;
    padding: 8px 16px;
}

@media (max-width: 768px) {
    .mobile-notification {
        font-size: 13px;
        padding: 10px 18px;
    }
}
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);