/**
 * Comprehensive Current Location Detection System
 * CAAIN Soil Hub - Farm Location Input
 * TICKET-008_farm-location-input-9.1
 * 
 * Advanced current location detection with multiple fallback methods:
 * - GPS location detection with high-accuracy and assisted GPS
 * - IP-based geolocation fallback
 * - Manual location entry
 * - Location history management
 * - Privacy controls and location permission management
 * - Battery optimization and location caching
 */

class CurrentLocationDetectionSystem {
    constructor() {
        this.currentLocation = null;
        this.locationHistory = [];
        this.favoriteLocations = [];
        this.permissionsStatus = {
            gps_available: false,
            gps_permission_granted: false,
            location_services_enabled: false,
            privacy_mode_active: false,
            battery_optimization_active: false
        };
        
        this.config = {
            gps_timeout_seconds: 15,
            gps_high_accuracy: true,
            gps_maximum_age_seconds: 300, // 5 minutes
            ip_geolocation_timeout_seconds: 10,
            location_cache_ttl_seconds: 3600, // 1 hour
            battery_optimization_enabled: true,
            privacy_mode_enabled: true,
            location_history_enabled: true,
            max_location_history_entries: 50,
            location_history_ttl_days: 30
        };
        
        this.batteryOptimization = {
            low_battery_threshold: 20, // percentage
            reduced_accuracy_mode: true,
            reduced_frequency_mode: true,
            background_location_disabled: true
        };
        
        this.apiEndpoints = {
            detect: '/api/v1/current-location/detect',
            history: '/api/v1/current-location/history',
            favorite: '/api/v1/current-location/favorite',
            permissions: '/api/v1/current-location/permissions',
            requestPermission: '/api/v1/current-location/permissions/request',
            sources: '/api/v1/current-location/sources',
            validate: '/api/v1/current-location/validate',
            accuracyLevels: '/api/v1/current-location/accuracy-levels'
        };
        
        this.init();
    }
    
    init() {
        this.checkGeolocationSupport();
        this.loadLocationHistory();
        this.loadFavoriteLocations();
        this.checkBatteryStatus();
        this.setupEventListeners();
        this.updatePermissionsStatus();
    }
    
    checkGeolocationSupport() {
        if ('geolocation' in navigator) {
            this.permissionsStatus.gps_available = true;
            console.log('GPS geolocation is supported');
        } else {
            this.permissionsStatus.gps_available = false;
            console.warn('GPS geolocation is not supported by this browser');
        }
    }
    
    async detectCurrentLocation(options = {}) {
        const {
            preferredSources = ['gps', 'ip_geolocation', 'saved_location', 'manual_entry'],
            privacyLevel = 'standard',
            batteryLevel = null,
            user_id = this.getUserId(),
            session_id = this.getSessionId()
        } = options;
        
        console.log('Starting comprehensive location detection...');
        
        // Check battery optimization
        const optimizedSources = this.optimizeSourcesForBattery(preferredSources, batteryLevel);
        
        // Try each source in order
        for (const source of optimizedSources) {
            try {
                console.log(`Attempting location detection using ${source}`);
                
                let result = null;
                
                switch (source) {
                    case 'gps':
                        result = await this.detectGPSLocation(batteryLevel);
                        break;
                    case 'ip_geolocation':
                        result = await this.detectIPLocation();
                        break;
                    case 'saved_location':
                        result = await this.getSavedLocation(user_id);
                        break;
                    case 'manual_entry':
                        result = await this.getManualLocation();
                        break;
                    default:
                        continue;
                }
                
                if (result && result.success) {
                    // Validate the detected location
                    const validationResult = await this.validateLocation(result.location);
                    
                    // Store in location history
                    if (this.config.location_history_enabled) {
                        await this.storeLocationHistory(result.location, user_id, session_id, source);
                    }
                    
                    // Cache the location
                    this.cacheLocation(result.location, user_id);
                    
                    // Update current location
                    this.currentLocation = result.location;
                    
                    // Trigger location detected event
                    this.triggerLocationDetectedEvent(result, validationResult);
                    
                    return {
                        success: true,
                        location: result.location,
                        fallback_used: source,
                        confidence_score: result.confidence_score,
                        battery_impact: this.assessBatteryImpact(source, batteryLevel),
                        privacy_level: privacyLevel,
                        validation_result: validationResult
                    };
                }
                
            } catch (error) {
                console.warn(`Location detection failed for ${source}:`, error);
                continue;
            }
        }
        
        // All methods failed
        console.error('All location detection methods failed');
        return {
            success: false,
            error_message: 'All location detection methods failed',
            battery_impact: 'minimal'
        };
    }
    
    async detectGPSLocation(batteryLevel = null) {
        if (!this.permissionsStatus.gps_available) {
            throw new Error('GPS is not available on this device');
        }
        
        return new Promise((resolve, reject) => {
            const options = {
                enableHighAccuracy: this.config.gps_high_accuracy,
                timeout: this.config.gps_timeout_seconds * 1000,
                maximumAge: this.config.gps_maximum_age_seconds * 1000
            };
            
            // Adjust options for battery optimization
            if (batteryLevel && batteryLevel < this.batteryOptimization.low_battery_threshold) {
                options.enableHighAccuracy = false;
                options.timeout = 5000; // Reduce timeout for low battery
            }
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const locationReading = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy_meters: position.coords.accuracy,
                        altitude: position.coords.altitude,
                        heading: position.coords.heading,
                        speed: position.coords.speed,
                        timestamp: new Date().toISOString(),
                        source: 'gps',
                        confidence_score: this.calculateGPSConfidence(position.coords),
                        battery_level: batteryLevel,
                        satellite_count: null, // Not available in browser API
                        hdop: null, // Not available in browser API
                        vdop: null // Not available in browser API
                    };
                    
                    resolve({
                        success: true,
                        location: locationReading,
                        confidence_score: locationReading.confidence_score
                    });
                },
                (error) => {
                    console.error('GPS location error:', error);
                    reject(new Error(`GPS location failed: ${error.message}`));
                },
                options
            );
        });
    }
    
    async detectIPLocation() {
        try {
            const response = await fetch(this.apiEndpoints.detect, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.getUserId(),
                    session_id: this.getSessionId(),
                    preferred_sources: ['ip_geolocation'],
                    privacy_level: 'minimal'
                })
            });
            
            if (!response.ok) {
                throw new Error(`IP geolocation failed: ${response.statusText}`);
            }
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            console.error('IP geolocation error:', error);
            throw error;
        }
    }
    
    async getSavedLocation(userId) {
        try {
            const favorites = this.favoriteLocations.filter(loc => loc.user_id === userId);
            
            if (favorites.length > 0) {
                // Return the most recent favorite location
                const latestFavorite = favorites.sort((a, b) => 
                    new Date(b.created_at) - new Date(a.created_at)
                )[0];
                
                return {
                    success: true,
                    location: latestFavorite.location,
                    confidence_score: 0.9 // Saved locations are highly trusted
                };
            }
            
            return null;
            
        } catch (error) {
            console.error('Error getting saved location:', error);
            return null;
        }
    }
    
    async getManualLocation() {
        // This would typically open a modal or form for manual entry
        // For now, return null to indicate manual entry is needed
        return null;
    }
    
    calculateGPSConfidence(coords) {
        let confidence = 1.0;
        
        // Reduce confidence based on accuracy
        if (coords.accuracy > 100) {
            confidence *= 0.7;
        } else if (coords.accuracy > 50) {
            confidence *= 0.8;
        } else if (coords.accuracy > 20) {
            confidence *= 0.9;
        }
        
        // Reduce confidence if altitude is not available
        if (coords.altitude === null) {
            confidence *= 0.95;
        }
        
        return Math.max(confidence, 0.1); // Minimum confidence
    }
    
    optimizeSourcesForBattery(sources, batteryLevel) {
        if (batteryLevel && batteryLevel < this.batteryOptimization.low_battery_threshold) {
            console.log(`Low battery detected (${batteryLevel}%), enabling battery optimization`);
            // Remove GPS and other battery-intensive sources when battery is low
            return sources.filter(source => 
                ['ip_geolocation', 'saved_location', 'manual_entry'].includes(source)
            );
        }
        
        return sources;
    }
    
    assessBatteryImpact(source, batteryLevel) {
        if (source === 'gps') {
            return batteryLevel && batteryLevel < 50 ? 'high' : 'medium';
        } else if (source === 'ip_geolocation') {
            return 'low';
        } else if (source === 'saved_location') {
            return 'minimal';
        } else {
            return 'low';
        }
    }
    
    async validateLocation(location) {
        try {
            const response = await fetch(this.apiEndpoints.validate, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(location)
            });
            
            if (!response.ok) {
                throw new Error(`Location validation failed: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error validating location:', error);
            return null;
        }
    }
    
    async storeLocationHistory(location, userId, sessionId, source) {
        try {
            const historyEntry = {
                id: this.generateUUID(),
                location: location,
                user_id: userId,
                session_id: sessionId,
                created_at: new Date().toISOString(),
                expires_at: new Date(Date.now() + this.config.location_history_ttl_days * 24 * 60 * 60 * 1000).toISOString(),
                is_favorite: false,
                notes: null
            };
            
            this.locationHistory.unshift(historyEntry);
            
            // Clean up old entries
            this.cleanupLocationHistory();
            
            // Save to localStorage
            this.saveLocationHistoryToStorage();
            
        } catch (error) {
            console.error('Error storing location history:', error);
        }
    }
    
    cleanupLocationHistory() {
        const currentTime = new Date();
        
        // Remove expired entries
        this.locationHistory = this.locationHistory.filter(entry => {
            const expiresAt = new Date(entry.expires_at);
            return expiresAt > currentTime;
        });
        
        // Limit number of entries per user
        const userCounts = {};
        const filteredHistory = [];
        
        for (const entry of this.locationHistory) {
            const userId = entry.user_id;
            if (userCounts[userId] < this.config.max_location_history_entries) {
                filteredHistory.push(entry);
                userCounts[userId] = (userCounts[userId] || 0) + 1;
            }
        }
        
        this.locationHistory = filteredHistory;
    }
    
    cacheLocation(location, userId) {
        try {
            const cacheKey = `${userId}:${location.latitude.toFixed(6)}:${location.longitude.toFixed(6)}`;
            const cacheEntry = {
                location: location,
                timestamp: new Date().toISOString(),
                ttl: this.config.location_cache_ttl_seconds
            };
            
            // Store in sessionStorage for this session
            sessionStorage.setItem(`location_cache_${cacheKey}`, JSON.stringify(cacheEntry));
            
        } catch (error) {
            console.error('Error caching location:', error);
        }
    }
    
    async getLocationHistory(userId, limit = 10, includeFavoritesOnly = false) {
        try {
            let userHistory = this.locationHistory.filter(entry => entry.user_id === userId);
            
            if (includeFavoritesOnly) {
                userHistory = userHistory.filter(entry => entry.is_favorite);
            }
            
            // Sort by creation time (most recent first)
            userHistory.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            return userHistory.slice(0, limit);
            
        } catch (error) {
            console.error('Error getting location history:', error);
            return [];
        }
    }
    
    async saveLocationAsFavorite(location, userId, sessionId, notes = null) {
        try {
            const favoriteEntry = {
                id: this.generateUUID(),
                location: location,
                user_id: userId,
                session_id: sessionId,
                created_at: new Date().toISOString(),
                is_favorite: true,
                notes: notes
            };
            
            this.favoriteLocations.push(favoriteEntry);
            
            // Save to localStorage
            this.saveFavoriteLocationsToStorage();
            
            return true;
            
        } catch (error) {
            console.error('Error saving favorite location:', error);
            return false;
        }
    }
    
    async requestLocationPermission(userId) {
        try {
            if (!this.permissionsStatus.gps_available) {
                throw new Error('GPS is not available on this device');
            }
            
            // Request permission by attempting to get location
            const result = await this.detectGPSLocation();
            
            if (result.success) {
                this.permissionsStatus.gps_permission_granted = true;
                this.permissionsStatus.location_services_enabled = true;
                this.updatePermissionsStatus();
                
                return {
                    permission_requested: true,
                    permission_granted: true,
                    message: 'Location permission granted successfully'
                };
            } else {
                return {
                    permission_requested: true,
                    permission_granted: false,
                    message: 'Location permission denied by user'
                };
            }
            
        } catch (error) {
            console.error('Error requesting location permission:', error);
            return {
                permission_requested: true,
                permission_granted: false,
                message: `Location permission request failed: ${error.message}`
            };
        }
    }
    
    async getLocationPermissionsStatus() {
        try {
            const response = await fetch(this.apiEndpoints.permissions);
            
            if (!response.ok) {
                throw new Error(`Failed to get permissions status: ${response.statusText}`);
            }
            
            const status = await response.json();
            this.permissionsStatus = { ...this.permissionsStatus, ...status };
            
            return this.permissionsStatus;
            
        } catch (error) {
            console.error('Error getting permissions status:', error);
            return this.permissionsStatus;
        }
    }
    
    async getAvailableLocationSources() {
        try {
            const response = await fetch(this.apiEndpoints.sources);
            
            if (!response.ok) {
                throw new Error(`Failed to get location sources: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error getting location sources:', error);
            return [];
        }
    }
    
    async getLocationAccuracyLevels() {
        try {
            const response = await fetch(this.apiEndpoints.accuracyLevels);
            
            if (!response.ok) {
                throw new Error(`Failed to get accuracy levels: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.error('Error getting accuracy levels:', error);
            return [];
        }
    }
    
    checkBatteryStatus() {
        if ('getBattery' in navigator) {
            navigator.getBattery().then(battery => {
                this.batteryLevel = Math.round(battery.level * 100);
                this.batteryOptimizationActive = battery.level < (this.batteryOptimization.low_battery_threshold / 100);
                
                console.log(`Battery level: ${this.batteryLevel}%`);
                
                if (this.batteryOptimizationActive) {
                    console.log('Battery optimization is active');
                }
            });
        } else {
            console.log('Battery API not available');
        }
    }
    
    loadLocationHistory() {
        try {
            const stored = localStorage.getItem('location_history');
            if (stored) {
                this.locationHistory = JSON.parse(stored);
                this.cleanupLocationHistory();
            }
        } catch (error) {
            console.error('Error loading location history:', error);
            this.locationHistory = [];
        }
    }
    
    loadFavoriteLocations() {
        try {
            const stored = localStorage.getItem('favorite_locations');
            if (stored) {
                this.favoriteLocations = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error loading favorite locations:', error);
            this.favoriteLocations = [];
        }
    }
    
    saveLocationHistoryToStorage() {
        try {
            localStorage.setItem('location_history', JSON.stringify(this.locationHistory));
        } catch (error) {
            console.error('Error saving location history:', error);
        }
    }
    
    saveFavoriteLocationsToStorage() {
        try {
            localStorage.setItem('favorite_locations', JSON.stringify(this.favoriteLocations));
        } catch (error) {
            console.error('Error saving favorite locations:', error);
        }
    }
    
    updatePermissionsStatus() {
        // Update UI elements based on permissions status
        const gpsButton = document.getElementById('gps-location-btn');
        const gpsStatus = document.getElementById('gps-status');
        
        if (gpsButton) {
            gpsButton.disabled = !this.permissionsStatus.gps_available;
        }
        
        if (gpsStatus) {
            if (this.permissionsStatus.gps_permission_granted) {
                gpsStatus.textContent = 'GPS Permission Granted';
                gpsStatus.className = 'status-granted';
            } else if (this.permissionsStatus.gps_available) {
                gpsStatus.textContent = 'GPS Available - Permission Required';
                gpsStatus.className = 'status-available';
            } else {
                gpsStatus.textContent = 'GPS Not Available';
                gpsStatus.className = 'status-unavailable';
            }
        }
    }
    
    setupEventListeners() {
        // GPS button click handler
        const gpsButton = document.getElementById('gps-location-btn');
        if (gpsButton) {
            gpsButton.addEventListener('click', () => {
                this.detectCurrentLocation({ preferredSources: ['gps'] });
            });
        }
        
        // IP geolocation button click handler
        const ipButton = document.getElementById('ip-location-btn');
        if (ipButton) {
            ipButton.addEventListener('click', () => {
                this.detectCurrentLocation({ preferredSources: ['ip_geolocation'] });
            });
        }
        
        // Request permission button click handler
        const permissionButton = document.getElementById('request-permission-btn');
        if (permissionButton) {
            permissionButton.addEventListener('click', () => {
                this.requestLocationPermission(this.getUserId());
            });
        }
        
        // Save as favorite button click handler
        const favoriteButton = document.getElementById('save-favorite-btn');
        if (favoriteButton) {
            favoriteButton.addEventListener('click', () => {
                if (this.currentLocation) {
                    this.saveLocationAsFavorite(
                        this.currentLocation,
                        this.getUserId(),
                        this.getSessionId(),
                        'Current location'
                    );
                }
            });
        }
    }
    
    triggerLocationDetectedEvent(result, validationResult) {
        const event = new CustomEvent('locationDetected', {
            detail: {
                result: result,
                validation: validationResult,
                timestamp: new Date().toISOString()
            }
        });
        
        document.dispatchEvent(event);
    }
    
    getUserId() {
        // In a real application, this would get the actual user ID
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }
    
    getSessionId() {
        // Generate or retrieve session ID
        let sessionId = sessionStorage.getItem('session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('session_id', sessionId);
        }
        return sessionId;
    }
    
    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    // Public API methods
    async getCurrentLocation() {
        return this.currentLocation;
    }
    
    async getLocationHistory(userId = null, limit = 10) {
        return await this.getLocationHistory(userId || this.getUserId(), limit);
    }
    
    async getFavoriteLocations(userId = null) {
        const userIdToUse = userId || this.getUserId();
        return this.favoriteLocations.filter(loc => loc.user_id === userIdToUse);
    }
    
    async clearLocationHistory() {
        this.locationHistory = [];
        this.saveLocationHistoryToStorage();
    }
    
    async clearFavoriteLocations() {
        this.favoriteLocations = [];
        this.saveFavoriteLocationsToStorage();
    }
}

// Initialize the system when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.currentLocationSystem = new CurrentLocationDetectionSystem();
    
    // Listen for location detected events
    document.addEventListener('locationDetected', (event) => {
        const { result, validation } = event.detail;
        
        console.log('Location detected:', result);
        
        // Update UI with detected location
        updateLocationDisplay(result.location, validation);
        
        // Show success message
        showLocationSuccessMessage(result);
    });
});

// Helper functions for UI updates
function updateLocationDisplay(location, validation) {
    const latElement = document.getElementById('detected-latitude');
    const lngElement = document.getElementById('detected-longitude');
    const accuracyElement = document.getElementById('detected-accuracy');
    const sourceElement = document.getElementById('detected-source');
    const confidenceElement = document.getElementById('detected-confidence');
    
    if (latElement) latElement.textContent = location.latitude.toFixed(6);
    if (lngElement) lngElement.textContent = location.longitude.toFixed(6);
    if (accuracyElement) accuracyElement.textContent = location.accuracy_meters ? `${Math.round(location.accuracy_meters)}m` : 'Unknown';
    if (sourceElement) sourceElement.textContent = location.source.toUpperCase();
    if (confidenceElement) confidenceElement.textContent = `${Math.round(location.confidence_score * 100)}%`;
    
    // Update validation status
    if (validation) {
        const validationElement = document.getElementById('validation-status');
        if (validationElement) {
            if (validation.validation.valid) {
                validationElement.textContent = 'Location Valid';
                validationElement.className = 'validation-valid';
            } else {
                validationElement.textContent = 'Location Issues Detected';
                validationElement.className = 'validation-warning';
            }
        }
    }
}

function showLocationSuccessMessage(result) {
    const messageElement = document.getElementById('location-message');
    if (messageElement) {
        messageElement.textContent = `Location detected using ${result.fallback_used} with ${Math.round(result.confidence_score * 100)}% confidence`;
        messageElement.className = 'message-success';
        
        // Hide message after 5 seconds
        setTimeout(() => {
            messageElement.textContent = '';
            messageElement.className = '';
        }, 5000);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CurrentLocationDetectionSystem;
}
