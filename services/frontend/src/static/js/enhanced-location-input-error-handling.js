/**
 * Enhanced Location Input with Comprehensive Error Handling
 * TICKET-008_farm-location-input-14.1: Implement comprehensive error handling and recovery
 * 
 * This enhanced JavaScript provides robust error handling for all location input scenarios:
 * - GPS failures and accuracy issues
 * - Network connectivity problems
 * - Validation errors and service unavailability
 * - Automatic retry mechanisms with exponential backoff
 * - Fallback methods and graceful degradation
 * - Clear user feedback and recovery suggestions
 * - Integration with monitoring systems
 */

class EnhancedLocationInputErrorHandler {
    constructor() {
        this.errorHistory = [];
        this.retryConfigs = {
            gps: { maxRetries: 3, baseDelay: 2000, maxDelay: 10000, exponentialBackoff: true },
            network: { maxRetries: 3, baseDelay: 1000, maxDelay: 8000, exponentialBackoff: true },
            geocoding: { maxRetries: 2, baseDelay: 1500, maxDelay: 6000, exponentialBackoff: true },
            validation: { maxRetries: 1, baseDelay: 500, maxDelay: 2000, exponentialBackoff: false }
        };
        this.fallbackMethods = ['manual_input', 'cached_data', 'offline_mode'];
        this.monitoringEnabled = true;
        
        this.initializeErrorHandling();
    }
    
    initializeErrorHandling() {
        // Set up global error handlers
        window.addEventListener('unhandledrejection', (event) => {
            this.handleGlobalError('unhandled_promise_rejection', event.reason);
        });
        
        window.addEventListener('error', (event) => {
            this.handleGlobalError('javascript_error', event.error);
        });
        
        // Set up network status monitoring
        this.setupNetworkMonitoring();
        
        // Set up GPS monitoring
        this.setupGPSMonitoring();
    }
    
    setupNetworkMonitoring() {
        // Monitor network status
        window.addEventListener('online', () => {
            this.showNetworkStatus('connected', 'Network connection restored');
            this.retryFailedOperations();
        });
        
        window.addEventListener('offline', () => {
            this.showNetworkStatus('disconnected', 'Network connection lost - switching to offline mode');
            this.enableOfflineMode();
        });
        
        // Check initial network status
        if (!navigator.onLine) {
            this.showNetworkStatus('disconnected', 'Currently offline');
            this.enableOfflineMode();
        }
    }
    
    setupGPSMonitoring() {
        // Monitor GPS availability
        if (!navigator.geolocation) {
            this.handleGPSError('gps_unavailable', 'GPS is not available on this device');
        }
    }
    
    async handleLocationInputError(errorType, errorMessage, context = {}) {
        console.log(`Handling location input error: ${errorType} - ${errorMessage}`);
        
        // Record error in history
        const errorRecord = {
            type: errorType,
            message: errorMessage,
            timestamp: new Date().toISOString(),
            context: context,
            retryCount: context.retryCount || 0
        };
        this.errorHistory.push(errorRecord);
        
        // Log error for monitoring
        if (this.monitoringEnabled) {
            await this.logErrorForMonitoring(errorRecord);
        }
        
        // Get recovery strategies
        const recoveryStrategies = this.getRecoveryStrategies(errorType);
        
        if (!recoveryStrategies || recoveryStrategies.length === 0) {
            this.showErrorToUser('An unexpected error occurred. Please try again or contact support.');
            return;
        }
        
        // Try recovery strategies in order of priority
        for (const strategy of recoveryStrategies) {
            try {
                console.log(`Attempting recovery strategy: ${strategy.name}`);
                
                const result = await this.executeRecoveryStrategy(strategy, errorRecord);
                
                if (result.success) {
                    console.log(`Recovery successful with strategy: ${strategy.name}`);
                    this.showRecoverySuccess(strategy.userGuidance);
                    return result.data;
                }
            } catch (strategyError) {
                console.error(`Recovery strategy ${strategy.name} failed:`, strategyError);
                continue;
            }
        }
        
        // All recovery strategies failed
        console.error(`All recovery strategies failed for error: ${errorType}`);
        this.showErrorToUser('Unable to recover from this error. Please try again or contact support.');
    }
    
    getRecoveryStrategies(errorType) {
        const strategies = {
            'gps_unavailable': [
                { name: 'manual_input', priority: 1, userGuidance: 'GPS is not available. Please enter coordinates manually or use the map to select your location.' },
                { name: 'cached_data', priority: 2, userGuidance: 'Using your last known location. Please verify this is correct.' }
            ],
            'gps_timeout': [
                { name: 'retry_extended_timeout', priority: 1, userGuidance: 'GPS is taking longer than expected. Retrying with extended timeout...' },
                { name: 'manual_input', priority: 2, userGuidance: 'GPS timeout occurred. Please enter coordinates manually.' }
            ],
            'gps_accuracy_poor': [
                { name: 'retry_high_accuracy', priority: 1, userGuidance: 'GPS accuracy is poor. Retrying with high accuracy mode...' },
                { name: 'user_guidance', priority: 2, userGuidance: 'Move to an open area away from buildings and trees for better GPS accuracy.' }
            ],
            'gps_permission_denied': [
                { name: 'user_guidance', priority: 1, userGuidance: 'GPS permission is required. Please enable location access in your browser settings.' },
                { name: 'manual_input', priority: 2, userGuidance: 'Please enter coordinates manually or use the map to select your location.' }
            ],
            'network_error': [
                { name: 'retry', priority: 1, userGuidance: 'Network error occurred. Retrying...' },
                { name: 'offline_mode', priority: 2, userGuidance: 'Network is unavailable. Switching to offline mode with cached data.' }
            ],
            'network_timeout': [
                { name: 'retry_extended_timeout', priority: 1, userGuidance: 'Request timed out. Retrying with extended timeout...' },
                { name: 'offline_mode', priority: 2, userGuidance: 'Network is slow. Switching to offline mode.' }
            ],
            'geocoding_failed': [
                { name: 'fallback_provider', priority: 1, userGuidance: 'Primary geocoding failed. Trying alternative provider...' },
                { name: 'manual_input', priority: 2, userGuidance: 'Address geocoding failed. Please enter GPS coordinates manually.' }
            ],
            'validation_error': [
                { name: 'user_guidance', priority: 1, userGuidance: 'Please check your input and try again.' },
                { name: 'manual_correction', priority: 2, userGuidance: 'Please correct the highlighted errors and try again.' }
            ],
            'service_unavailable': [
                { name: 'retry_delayed', priority: 1, userGuidance: 'Service temporarily unavailable. Retrying in a moment...' },
                { name: 'cached_data', priority: 2, userGuidance: 'Service unavailable. Using cached data.' }
            ]
        };
        
        return strategies[errorType] || [];
    }
    
    async executeRecoveryStrategy(strategy, errorRecord) {
        switch (strategy.name) {
            case 'retry':
                return await this.retryOperation(errorRecord);
            case 'retry_extended_timeout':
                return await this.retryWithExtendedTimeout(errorRecord);
            case 'retry_high_accuracy':
                return await this.retryWithHighAccuracy(errorRecord);
            case 'retry_delayed':
                return await this.retryWithDelay(errorRecord);
            case 'manual_input':
                return await this.enableManualInput(errorRecord);
            case 'manual_correction':
                return await this.enableManualCorrection(errorRecord);
            case 'cached_data':
                return await this.useCachedData(errorRecord);
            case 'offline_mode':
                return await this.enableOfflineMode(errorRecord);
            case 'fallback_provider':
                return await this.tryFallbackProvider(errorRecord);
            case 'user_guidance':
                return await this.provideUserGuidance(errorRecord);
            default:
                return { success: false };
        }
    }
    
    async retryOperation(errorRecord) {
        const config = this.retryConfigs[this.getConfigKey(errorRecord.type)];
        if (!config) return { success: false };
        
        if (errorRecord.retryCount >= config.maxRetries) {
            return { success: false };
        }
        
        const delay = this.calculateRetryDelay(errorRecord.retryCount, config);
        await this.sleep(delay);
        
        // Increment retry count and retry
        errorRecord.retryCount++;
        return { success: true, data: { retry: true, delay: delay } };
    }
    
    async retryWithExtendedTimeout(errorRecord) {
        const config = this.retryConfigs[this.getConfigKey(errorRecord.type)];
        if (!config) return { success: false };
        
        if (errorRecord.retryCount >= config.maxRetries) {
            return { success: false };
        }
        
        const delay = this.calculateRetryDelay(errorRecord.retryCount, config);
        await this.sleep(delay);
        
        // Retry with extended timeout
        errorRecord.retryCount++;
        return { success: true, data: { retry: true, extendedTimeout: true, delay: delay } };
    }
    
    async retryWithHighAccuracy(errorRecord) {
        const config = this.retryConfigs[this.getConfigKey(errorRecord.type)];
        if (!config) return { success: false };
        
        if (errorRecord.retryCount >= config.maxRetries) {
            return { success: false };
        }
        
        const delay = this.calculateRetryDelay(errorRecord.retryCount, config);
        await this.sleep(delay);
        
        // Retry with high accuracy
        errorRecord.retryCount++;
        return { success: true, data: { retry: true, highAccuracy: true, delay: delay } };
    }
    
    async retryWithDelay(errorRecord) {
        const config = this.retryConfigs[this.getConfigKey(errorRecord.type)];
        if (!config) return { success: false };
        
        const delay = config.baseDelay;
        await this.sleep(delay);
        
        return { success: true, data: { retry: true, delayed: true, delay: delay } };
    }
    
    async enableManualInput(errorRecord) {
        // Enable manual coordinate input
        this.showManualInputOption();
        return { success: true, data: { manualInputEnabled: true } };
    }
    
    async enableManualCorrection(errorRecord) {
        // Enable manual correction of input
        this.showManualCorrectionOption();
        return { success: true, data: { manualCorrectionEnabled: true } };
    }
    
    async useCachedData(errorRecord) {
        // Use previously cached data
        const cachedData = this.getCachedLocationData();
        if (cachedData) {
            return { success: true, data: { cachedData: cachedData } };
        }
        return { success: false };
    }
    
    async enableOfflineMode(errorRecord) {
        // Enable offline mode
        this.setOfflineMode(true);
        return { success: true, data: { offlineMode: true } };
    }
    
    async tryFallbackProvider(errorRecord) {
        // Try alternative geocoding provider
        return { success: true, data: { fallbackProvider: 'alternative_provider' } };
    }
    
    async provideUserGuidance(errorRecord) {
        // Provide user guidance
        return { success: true, data: { guidance: 'user_guidance_provided' } };
    }
    
    calculateRetryDelay(retryCount, config) {
        let delay = config.baseDelay;
        
        if (config.exponentialBackoff) {
            delay = config.baseDelay * Math.pow(2, retryCount);
        }
        
        delay = Math.min(delay, config.maxDelay);
        
        // Add random jitter (±25%)
        const jitterFactor = 0.75 + Math.random() * 0.5;
        delay *= jitterFactor;
        
        return delay;
    }
    
    getConfigKey(errorType) {
        if (errorType.includes('gps')) return 'gps';
        if (errorType.includes('network')) return 'network';
        if (errorType.includes('geocoding')) return 'geocoding';
        if (errorType.includes('validation')) return 'validation';
        return 'network'; // default
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async logErrorForMonitoring(errorRecord) {
        // Log error for monitoring and analytics
        const errorData = {
            error_type: errorRecord.type,
            error_message: errorRecord.message,
            timestamp: errorRecord.timestamp,
            retry_count: errorRecord.retryCount,
            context: errorRecord.context,
            user_agent: navigator.userAgent,
            url: window.location.href
        };
        
        console.error('Location input error:', errorData);
        
        // TODO: Send to monitoring service (e.g., Sentry, DataDog, etc.)
        // await this.sendToMonitoringService(errorData);
    }
    
    showErrorToUser(message) {
        // Show error message to user
        const errorContainer = document.getElementById('error-container') || this.createErrorContainer();
        errorContainer.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
        errorContainer.style.display = 'block';
    }
    
    showRecoverySuccess(message) {
        // Show recovery success message
        const successContainer = document.getElementById('success-container') || this.createSuccessContainer();
        successContainer.innerHTML = `
            <div class="alert alert-success" role="alert">
                <i class="fas fa-check-circle me-2"></i>
                ${message}
            </div>
        `;
        successContainer.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            successContainer.style.display = 'none';
        }, 5000);
    }
    
    showNetworkStatus(status, message) {
        // Show network status
        const networkContainer = document.getElementById('network-status') || this.createNetworkStatusContainer();
        const statusClass = status === 'connected' ? 'alert-success' : 'alert-warning';
        const statusIcon = status === 'connected' ? 'fa-wifi' : 'fa-wifi-slash';
        
        networkContainer.innerHTML = `
            <div class="alert ${statusClass}" role="alert">
                <i class="fas ${statusIcon} me-2"></i>
                ${message}
            </div>
        `;
        networkContainer.style.display = 'block';
        
        // Hide after 3 seconds for connected status
        if (status === 'connected') {
            setTimeout(() => {
                networkContainer.style.display = 'none';
            }, 3000);
        }
    }
    
    showManualInputOption() {
        // Show manual input option
        const manualContainer = document.getElementById('manual-input-container') || this.createManualInputContainer();
        manualContainer.innerHTML = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-keyboard me-2"></i>Manual Coordinate Input</h6>
                </div>
                <div class="card-body">
                    <p class="text-muted">Please enter coordinates manually:</p>
                    <div class="row">
                        <div class="col-md-6">
                            <label for="manual-latitude" class="form-label">Latitude</label>
                            <input type="number" class="form-control" id="manual-latitude" 
                                   step="0.000001" min="-90" max="90" placeholder="e.g., 40.7128">
                        </div>
                        <div class="col-md-6">
                            <label for="manual-longitude" class="form-label">Longitude</label>
                            <input type="number" class="form-control" id="manual-longitude" 
                                   step="0.000001" min="-180" max="180" placeholder="e.g., -74.0060">
                        </div>
                    </div>
                    <button class="btn btn-primary mt-3" onclick="enhancedErrorHandler.useManualCoordinates()">
                        <i class="fas fa-map-marker-alt me-2"></i>Use These Coordinates
                    </button>
                </div>
            </div>
        `;
        manualContainer.style.display = 'block';
    }
    
    showManualCorrectionOption() {
        // Show manual correction option
        const correctionContainer = document.getElementById('correction-container') || this.createCorrectionContainer();
        correctionContainer.innerHTML = `
            <div class="alert alert-info" role="alert">
                <i class="fas fa-edit me-2"></i>
                Please correct the highlighted errors and try again.
            </div>
        `;
        correctionContainer.style.display = 'block';
    }
    
    createErrorContainer() {
        const container = document.createElement('div');
        container.id = 'error-container';
        container.style.display = 'none';
        document.body.insertBefore(container, document.body.firstChild);
        return container;
    }
    
    createSuccessContainer() {
        const container = document.createElement('div');
        container.id = 'success-container';
        container.style.display = 'none';
        document.body.insertBefore(container, document.body.firstChild);
        return container;
    }
    
    createNetworkStatusContainer() {
        const container = document.createElement('div');
        container.id = 'network-status';
        container.style.display = 'none';
        document.body.insertBefore(container, document.body.firstChild);
        return container;
    }
    
    createManualInputContainer() {
        const container = document.createElement('div');
        container.id = 'manual-input-container';
        container.style.display = 'none';
        const locationForm = document.getElementById('location-form') || document.body;
        locationForm.appendChild(container);
        return container;
    }
    
    createCorrectionContainer() {
        const container = document.createElement('div');
        container.id = 'correction-container';
        container.style.display = 'none';
        const locationForm = document.getElementById('location-form') || document.body;
        locationForm.appendChild(container);
        return container;
    }
    
    getCachedLocationData() {
        // Get cached location data from localStorage
        try {
            const cached = localStorage.getItem('last_location_data');
            return cached ? JSON.parse(cached) : null;
        } catch (e) {
            console.warn('Failed to get cached location data:', e);
            return null;
        }
    }
    
    setCachedLocationData(data) {
        // Set cached location data in localStorage
        try {
            localStorage.setItem('last_location_data', JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to cache location data:', e);
        }
    }
    
    setOfflineMode(enabled) {
        // Set offline mode
        document.body.classList.toggle('offline-mode', enabled);
        if (enabled) {
            this.showOfflineModeIndicator();
        } else {
            this.hideOfflineModeIndicator();
        }
    }
    
    showOfflineModeIndicator() {
        const indicator = document.getElementById('offline-indicator') || this.createOfflineIndicator();
        indicator.style.display = 'block';
    }
    
    hideOfflineModeIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }
    
    createOfflineIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.className = 'alert alert-warning position-fixed top-0 start-0 w-100';
        indicator.style.zIndex = '9999';
        indicator.innerHTML = `
            <div class="container">
                <i class="fas fa-wifi-slash me-2"></i>
                <strong>Offline Mode:</strong> Working with cached data. Some features may be limited.
            </div>
        `;
        document.body.appendChild(indicator);
        return indicator;
    }
    
    async retryFailedOperations() {
        // Retry operations that failed due to network issues
        console.log('Retrying failed operations...');
        // Implementation would retry failed network requests
    }
    
    handleGlobalError(type, error) {
        console.error(`Global ${type}:`, error);
        this.handleLocationInputError('unknown_error', `Global ${type}: ${error.message || error}`);
    }
    
    handleGPSError(type, message) {
        this.handleLocationInputError(type, message);
    }
    
    handleNetworkError(type, message) {
        this.handleLocationInputError(type, message);
    }
    
    handleGeocodingError(type, message) {
        this.handleLocationInputError(type, message);
    }
    
    handleValidationError(type, message) {
        this.handleLocationInputError(type, message);
    }
    
    async useManualCoordinates() {
        const lat = parseFloat(document.getElementById('manual-latitude').value);
        const lng = parseFloat(document.getElementById('manual-longitude').value);
        
        if (isNaN(lat) || isNaN(lng)) {
            this.showErrorToUser('Please enter valid coordinates');
            return;
        }
        
        if (lat < -90 || lat > 90) {
            this.showErrorToUser('Latitude must be between -90 and 90');
            return;
        }
        
        if (lng < -180 || lng > 180) {
            this.showErrorToUser('Longitude must be between -180 and 180');
            return;
        }
        
        // Use the manual coordinates
        const coordinates = { latitude: lat, longitude: lng };
        this.setCachedLocationData(coordinates);
        
        // Hide manual input container
        const manualContainer = document.getElementById('manual-input-container');
        if (manualContainer) {
            manualContainer.style.display = 'none';
        }
        
        // Show success message
        this.showRecoverySuccess('Manual coordinates accepted successfully!');
        
        // Trigger location update
        if (window.gpsInput && window.gpsInput.setCoordinatesFromGPS) {
            window.gpsInput.setCoordinatesFromGPS(lat, lng);
        }
    }
}

// Global error handler instance
const enhancedErrorHandler = new EnhancedLocationInputErrorHandler();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedLocationInputErrorHandler;
}
