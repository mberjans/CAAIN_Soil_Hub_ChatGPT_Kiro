/**
 * Mobile Location Input JavaScript
 * Handles touch gestures, GPS integration, and mobile-optimized interactions
 */

class MobileLocationInput {
    constructor() {
        this.currentMethod = 'gps';
        this.currentLocation = null;
        this.locationHistory = [];
        this.mobileMap = null;
        this.mapMarker = null;
        this.isOnline = navigator.onLine;
        this.gpsWatchId = null;
        this.batteryOptimization = false;
        
        // Initialize the mobile location input system
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTouchGestures();
        this.setupOnlineOfflineHandling();
        this.loadLocationHistory();
        this.initializeMap();
        this.setupBatteryOptimization();
        
        // Auto-detect current location on load
        this.getCurrentLocation();
    }

    setupEventListeners() {
        // Address input with debounced search
        const addressInput = document.getElementById('addressInput');
        if (addressInput) {
            let searchTimeout;
            addressInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.handleAddressSearch(e.target.value);
                }, 300);
            });
        }

        // Coordinate inputs
        const latitudeInput = document.getElementById('latitudeInput');
        const longitudeInput = document.getElementById('longitudeInput');
        
        if (latitudeInput) {
            latitudeInput.addEventListener('input', () => this.validateCoordinates());
        }
        if (longitudeInput) {
            longitudeInput.addEventListener('input', () => this.validateCoordinates());
        }

        // Battery optimization toggle
        const batteryOptimization = document.getElementById('batteryOptimization');
        if (batteryOptimization) {
            batteryOptimization.addEventListener('change', (e) => {
                this.batteryOptimization = e.target.checked;
                this.updateGPSSettings();
            });
        }

        // High accuracy toggle
        const highAccuracy = document.getElementById('highAccuracy');
        if (highAccuracy) {
            highAccuracy.addEventListener('change', (e) => {
                this.updateGPSSettings();
            });
        }

        // Prevent zoom on double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (event) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);

        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                if (this.mobileMap) {
                    this.mobileMap.invalidateSize();
                }
            }, 100);
        });
    }

    setupTouchGestures() {
        // Swipe gestures for method switching
        let startX = 0;
        let startY = 0;
        let isScrolling = false;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isScrolling = false;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;

            const diffX = Math.abs(e.touches[0].clientX - startX);
            const diffY = Math.abs(e.touches[0].clientY - startY);

            if (diffY > diffX) {
                isScrolling = true;
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY || isScrolling) return;

            const diffX = startX - e.changedTouches[0].clientX;
            const threshold = 50;

            if (Math.abs(diffX) > threshold) {
                if (diffX > 0) {
                    this.switchToNextMethod();
                } else {
                    this.switchToPreviousMethod();
                }
            }

            startX = 0;
            startY = 0;
            isScrolling = false;
        }, { passive: true });

        // Touch feedback for interactive elements
        document.addEventListener('touchstart', (e) => {
            if (e.target.classList.contains('btn') || 
                e.target.classList.contains('method-header') ||
                e.target.classList.contains('history-item')) {
                e.target.style.transform = 'scale(0.95)';
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (e.target.classList.contains('btn') || 
                e.target.classList.contains('method-header') ||
                e.target.classList.contains('history-item')) {
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 150);
            }
        }, { passive: true });
    }

    setupOnlineOfflineHandling() {
        const offlineIndicator = document.getElementById('offlineIndicator');
        
        window.addEventListener('online', () => {
            this.isOnline = true;
            offlineIndicator.classList.remove('show');
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            offlineIndicator.classList.add('show');
        });

        // Initial state
        if (!this.isOnline) {
            offlineIndicator.classList.add('show');
        }
    }

    setupBatteryOptimization() {
        // Check if battery API is available
        if ('getBattery' in navigator) {
            navigator.getBattery().then((battery) => {
                const batteryOptimization = document.getElementById('batteryOptimization');
                
                // Auto-enable battery optimization if battery is low
                if (battery.level < 0.2) {
                    batteryOptimization.checked = true;
                    this.batteryOptimization = true;
                }

                // Update GPS settings when battery level changes
                battery.addEventListener('levelchange', () => {
                    if (battery.level < 0.15 && !this.batteryOptimization) {
                        this.showBatteryWarning();
                    }
                });
            });
        }
    }

    initializeMap() {
        // Initialize Leaflet map for mobile
        this.mobileMap = L.map('mobileMap', {
            zoomControl: false,
            attributionControl: false,
            touchZoom: true,
            doubleClickZoom: false,
            scrollWheelZoom: false,
            dragging: true,
            tap: true
        }).setView([40.0, -95.0], 4);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.mobileMap);

        // Add map click handler
        this.mobileMap.on('click', (e) => {
            this.handleMapClick(e.latlng);
        });

        // Add map move handler for marker updates
        this.mobileMap.on('move', () => {
            if (this.mapMarker) {
                const center = this.mobileMap.getCenter();
                this.mapMarker.setLatLng(center);
                this.updateLocationFromMap(center);
            }
        });
    }

    toggleMethod(method) {
        // Remove active class from all methods
        document.querySelectorAll('.method-card').forEach(card => {
            card.classList.remove('active');
        });

        // Add active class to selected method
        const methodCard = document.getElementById(`${method}-method`);
        if (methodCard) {
            methodCard.classList.add('active');
            this.currentMethod = method;
        }

        // Initialize method-specific features
        if (method === 'map' && this.mobileMap) {
            setTimeout(() => {
                this.mobileMap.invalidateSize();
            }, 100);
        }
    }

    switchToNextMethod() {
        const methods = ['gps', 'map', 'manual'];
        const currentIndex = methods.indexOf(this.currentMethod);
        const nextIndex = (currentIndex + 1) % methods.length;
        this.toggleMethod(methods[nextIndex]);
    }

    switchToPreviousMethod() {
        const methods = ['gps', 'map', 'manual'];
        const currentIndex = methods.indexOf(this.currentMethod);
        const prevIndex = (currentIndex - 1 + methods.length) % methods.length;
        this.toggleMethod(methods[prevIndex]);
    }

    async getCurrentLocation() {
        const gpsStatus = document.getElementById('gpsStatus');
        const statusIndicator = gpsStatus.querySelector('.status-indicator');
        
        statusIndicator.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i><span>Getting location...</span>';

        if (!navigator.geolocation) {
            this.showGPSError('Geolocation is not supported by this browser');
            return;
        }

        const options = {
            enableHighAccuracy: document.getElementById('highAccuracy').checked,
            timeout: this.batteryOptimization ? 10000 : 30000,
            maximumAge: this.batteryOptimization ? 300000 : 60000 // 5 minutes vs 1 minute
        };

        try {
            const position = await this.getCurrentPosition(options);
            this.handleGPSSuccess(position);
        } catch (error) {
            this.handleGPSError(error);
        }
    }

    getCurrentPosition(options) {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, options);
        });
    }

    handleGPSSuccess(position) {
        const { latitude, longitude, accuracy } = position.coords;
        
        this.currentLocation = {
            latitude,
            longitude,
            accuracy,
            source: 'gps',
            timestamp: new Date()
        };

        // Update GPS status
        const gpsStatus = document.getElementById('gpsStatus');
        const statusIndicator = gpsStatus.querySelector('.status-indicator');
        statusIndicator.innerHTML = '<i class="fas fa-check-circle text-success"></i><span>Location found!</span>';

        // Show location display
        const locationDisplay = document.getElementById('locationDisplay');
        locationDisplay.style.display = 'block';
        
        document.getElementById('displayLatitude').textContent = latitude.toFixed(6);
        document.getElementById('displayLongitude').textContent = longitude.toFixed(6);
        document.getElementById('displayAccuracy').textContent = `${Math.round(accuracy)}m`;

        // Update map if visible
        if (this.mobileMap) {
            this.mobileMap.setView([latitude, longitude], 15);
            this.addMapMarker(latitude, longitude);
        }

        // Update manual input fields
        document.getElementById('latitudeInput').value = latitude.toFixed(6);
        document.getElementById('longitudeInput').value = longitude.toFixed(6);

        // Validate location
        this.validateLocation(latitude, longitude);

        // Enable save button
        document.getElementById('saveButton').disabled = false;
    }

    handleGPSError(error) {
        let errorMessage = 'Unable to get location';
        
        switch (error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = 'Location access denied. Please enable location services.';
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = 'Location information unavailable.';
                break;
            case error.TIMEOUT:
                errorMessage = 'Location request timed out.';
                break;
        }

        this.showGPSError(errorMessage);
    }

    showGPSError(message) {
        const gpsStatus = document.getElementById('gpsStatus');
        const statusIndicator = gpsStatus.querySelector('.status-indicator');
        statusIndicator.innerHTML = `<i class="fas fa-exclamation-triangle text-warning"></i><span>${message}</span>`;
    }

    handleMapClick(latlng) {
        const { lat, lng } = latlng;
        
        this.currentLocation = {
            latitude: lat,
            longitude: lng,
            accuracy: null,
            source: 'map',
            timestamp: new Date()
        };

        this.addMapMarker(lat, lng);
        this.updateLocationFromMap(latlng);
        this.validateLocation(lat, lng);
        
        // Enable save button
        document.getElementById('saveButton').disabled = false;
    }

    addMapMarker(lat, lng) {
        if (this.mapMarker) {
            this.mobileMap.removeLayer(this.mapMarker);
        }

        this.mapMarker = L.marker([lat, lng], {
            draggable: true
        }).addTo(this.mobileMap);

        this.mapMarker.on('dragend', (e) => {
            const marker = e.target;
            const position = marker.getLatLng();
            this.updateLocationFromMap(position);
        });
    }

    updateLocationFromMap(latlng) {
        const { lat, lng } = latlng;
        
        this.currentLocation = {
            latitude: lat,
            longitude: lng,
            accuracy: null,
            source: 'map',
            timestamp: new Date()
        };

        // Update manual input fields
        document.getElementById('latitudeInput').value = lat.toFixed(6);
        document.getElementById('longitudeInput').value = lng.toFixed(6);

        this.validateLocation(lat, lng);
    }

    async handleAddressSearch(query) {
        if (query.length < 3) {
            this.hideAddressSuggestions();
            return;
        }

        try {
            const suggestions = await this.searchAddresses(query);
            this.showAddressSuggestions(suggestions);
        } catch (error) {
            console.error('Address search error:', error);
        }
    }

    async searchAddresses(query) {
        // In a real implementation, this would call the location validation service
        // For now, we'll simulate some results
        const mockSuggestions = [
            {
                text: `${query} Farm Road, Iowa`,
                details: 'Agricultural area, suitable for farming',
                coordinates: { lat: 42.0308, lng: -93.6319 }
            },
            {
                text: `Rural Route 1, ${query}`,
                details: 'Rural delivery route',
                coordinates: { lat: 41.8781, lng: -87.6298 }
            }
        ];

        return mockSuggestions.filter(suggestion => 
            suggestion.text.toLowerCase().includes(query.toLowerCase())
        );
    }

    showAddressSuggestions(suggestions) {
        const container = document.getElementById('addressSuggestions');
        container.innerHTML = '';

        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <div class="suggestion-text">${suggestion.text}</div>
                <div class="suggestion-details">${suggestion.details}</div>
            `;
            
            item.addEventListener('click', () => {
                this.selectAddressSuggestion(suggestion);
            });
            
            container.appendChild(item);
        });

        container.style.display = 'block';
    }

    hideAddressSuggestions() {
        const container = document.getElementById('addressSuggestions');
        container.style.display = 'none';
    }

    selectAddressSuggestion(suggestion) {
        document.getElementById('addressInput').value = suggestion.text;
        this.hideAddressSuggestions();
        
        this.currentLocation = {
            latitude: suggestion.coordinates.lat,
            longitude: suggestion.coordinates.lng,
            accuracy: null,
            source: 'address',
            timestamp: new Date()
        };

        // Update map
        if (this.mobileMap) {
            this.mobileMap.setView([suggestion.coordinates.lat, suggestion.coordinates.lng], 15);
            this.addMapMarker(suggestion.coordinates.lat, suggestion.coordinates.lng);
        }

        // Update coordinate inputs
        document.getElementById('latitudeInput').value = suggestion.coordinates.lat.toFixed(6);
        document.getElementById('longitudeInput').value = suggestion.coordinates.lng.toFixed(6);

        this.validateLocation(suggestion.coordinates.lat, suggestion.coordinates.lng);
        document.getElementById('saveButton').disabled = false;
    }

    validateCoordinates() {
        const lat = parseFloat(document.getElementById('latitudeInput').value);
        const lng = parseFloat(document.getElementById('longitudeInput').value);

        if (!isNaN(lat) && !isNaN(lng)) {
            this.currentLocation = {
                latitude: lat,
                longitude: lng,
                accuracy: null,
                source: 'manual',
                timestamp: new Date()
            };

            this.validateLocation(lat, lng);
            document.getElementById('saveButton').disabled = false;
        }
    }

    async validateLocation(lat, lng) {
        const validationSection = document.getElementById('validationSection');
        const validationContent = document.getElementById('validationContent');
        
        validationSection.style.display = 'block';
        validationContent.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Validating location...</div>';

        try {
            const response = await fetch('/api/v1/validation/agricultural', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: lat,
                    longitude: lng
                })
            });

            const result = await response.json();
            this.displayValidationResults(result);
        } catch (error) {
            console.error('Validation error:', error);
            this.displayValidationError();
        }
    }

    displayValidationResults(result) {
        const validationContent = document.getElementById('validationContent');
        
        let html = '';
        
        if (result.valid) {
            html += '<div class="validation-item"><div class="validation-icon success"><i class="fas fa-check"></i></div><div class="validation-text">Location is valid for agricultural use</div></div>';
        } else {
            html += '<div class="validation-item"><div class="validation-icon error"><i class="fas fa-times"></i></div><div class="validation-text">Location validation failed</div></div>';
        }

        if (result.warnings && result.warnings.length > 0) {
            result.warnings.forEach(warning => {
                html += `<div class="validation-item"><div class="validation-icon warning"><i class="fas fa-exclamation-triangle"></i></div><div class="validation-text">${warning}</div></div>`;
            });
        }

        if (result.geographic_info) {
            const info = result.geographic_info;
            if (info.state) {
                html += `<div class="validation-item"><div class="validation-icon success"><i class="fas fa-map-marker-alt"></i></div><div class="validation-text">State: ${info.state}</div></div>`;
            }
            if (info.climate_zone) {
                html += `<div class="validation-item"><div class="validation-icon success"><i class="fas fa-thermometer-half"></i></div><div class="validation-text">Climate Zone: ${info.climate_zone}</div></div>`;
            }
        }

        validationContent.innerHTML = html;
    }

    displayValidationError() {
        const validationContent = document.getElementById('validationContent');
        validationContent.innerHTML = '<div class="validation-item"><div class="validation-icon error"><i class="fas fa-exclamation-triangle"></i></div><div class="validation-text">Unable to validate location. Please check your connection.</div></div>';
    }

    setCoordinateFormat(format) {
        // Remove active class from all format buttons
        document.querySelectorAll('.format-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Add active class to selected format
        const selectedBtn = document.querySelector(`[data-format="${format}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('active');
        }

        // Update input fields based on format
        if (format === 'dms') {
            this.convertToDMS();
        } else {
            this.convertToDecimal();
        }
    }

    convertToDMS() {
        // Implementation for DMS conversion
        // This would convert decimal degrees to degrees, minutes, seconds
    }

    convertToDecimal() {
        // Implementation for decimal conversion
        // This would convert DMS to decimal degrees
    }

    updateGPSSettings() {
        // Update GPS settings based on battery optimization and accuracy preferences
        if (this.gpsWatchId) {
            navigator.geolocation.clearWatch(this.gpsWatchId);
        }

        if (this.batteryOptimization) {
            // Use less accurate but more battery-efficient settings
            console.log('Battery optimization enabled');
        }
    }

    showBatteryWarning() {
        // Show battery warning when battery is low
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning position-fixed';
        notification.style.top = '100px';
        notification.style.left = '10px';
        notification.style.right = '10px';
        notification.style.zIndex = '1000';
        notification.innerHTML = '<i class="fas fa-battery-quarter me-2"></i>Low battery detected. Consider enabling battery optimization.';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    async saveLocation() {
        if (!this.currentLocation) {
            this.showError('No location selected');
            return;
        }

        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.style.display = 'flex';

        try {
            // Save to location history
            this.addToHistory(this.currentLocation);

            // Save to server if online
            if (this.isOnline) {
                await this.saveToServer(this.currentLocation);
            } else {
                // Save to local storage for offline sync
                this.saveToLocalStorage(this.currentLocation);
            }

            this.showSuccess('Location saved successfully!');
            
            // Navigate back or to next step
            setTimeout(() => {
                this.navigateToNextStep();
            }, 1500);

        } catch (error) {
            console.error('Save error:', error);
            this.showError('Failed to save location');
        } finally {
            loadingOverlay.style.display = 'none';
        }
    }

    addToHistory(location) {
        const historyEntry = {
            id: Date.now(),
            name: this.generateLocationName(location),
            latitude: location.latitude,
            longitude: location.longitude,
            source: location.source,
            timestamp: location.timestamp,
            favorite: false
        };

        this.locationHistory.unshift(historyEntry);
        
        // Keep only last 10 entries
        if (this.locationHistory.length > 10) {
            this.locationHistory = this.locationHistory.slice(0, 10);
        }

        this.saveHistoryToStorage();
        this.updateHistoryDisplay();
    }

    generateLocationName(location) {
        const source = location.source.charAt(0).toUpperCase() + location.source.slice(1);
        const date = new Date(location.timestamp).toLocaleDateString();
        return `${source} Location - ${date}`;
    }

    updateHistoryDisplay() {
        const historySection = document.getElementById('locationHistory');
        const historyList = document.getElementById('historyList');
        
        if (this.locationHistory.length === 0) {
            historySection.style.display = 'none';
            return;
        }

        historySection.style.display = 'block';
        
        historyList.innerHTML = this.locationHistory.map(entry => `
            <div class="history-item" onclick="mobileLocationInput.selectHistoryItem(${entry.id})">
                <div class="history-icon">
                    <i class="fas fa-map-marker-alt"></i>
                </div>
                <div class="history-info">
                    <div class="location-name">${entry.name}</div>
                    <div class="location-coords">${entry.latitude.toFixed(6)}, ${entry.longitude.toFixed(6)}</div>
                </div>
                <div class="history-actions">
                    <button class="history-action-btn" onclick="event.stopPropagation(); mobileLocationInput.toggleFavorite(${entry.id})">
                        <i class="fas fa-star ${entry.favorite ? 'text-warning' : ''}"></i>
                    </button>
                    <button class="history-action-btn" onclick="event.stopPropagation(); mobileLocationInput.deleteHistoryItem(${entry.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    selectHistoryItem(id) {
        const entry = this.locationHistory.find(item => item.id === id);
        if (entry) {
            this.currentLocation = {
                latitude: entry.latitude,
                longitude: entry.longitude,
                accuracy: null,
                source: 'history',
                timestamp: new Date()
            };

            // Update inputs
            document.getElementById('latitudeInput').value = entry.latitude.toFixed(6);
            document.getElementById('longitudeInput').value = entry.longitude.toFixed(6);

            // Update map
            if (this.mobileMap) {
                this.mobileMap.setView([entry.latitude, entry.longitude], 15);
                this.addMapMarker(entry.latitude, entry.longitude);
            }

            this.validateLocation(entry.latitude, entry.longitude);
            document.getElementById('saveButton').disabled = false;
        }
    }

    toggleFavorite(id) {
        const entry = this.locationHistory.find(item => item.id === id);
        if (entry) {
            entry.favorite = !entry.favorite;
            this.saveHistoryToStorage();
            this.updateHistoryDisplay();
        }
    }

    deleteHistoryItem(id) {
        this.locationHistory = this.locationHistory.filter(item => item.id !== id);
        this.saveHistoryToStorage();
        this.updateHistoryDisplay();
    }

    clearAllInputs() {
        // Clear all input fields
        document.getElementById('addressInput').value = '';
        document.getElementById('latitudeInput').value = '';
        document.getElementById('longitudeInput').value = '';
        
        // Clear map
        if (this.mapMarker) {
            this.mobileMap.removeLayer(this.mapMarker);
            this.mapMarker = null;
        }
        
        // Clear validation
        document.getElementById('validationSection').style.display = 'none';
        
        // Disable save button
        document.getElementById('saveButton').disabled = true;
        
        // Clear current location
        this.currentLocation = null;
        
        // Hide address suggestions
        this.hideAddressSuggestions();
    }

    clearHistory() {
        this.locationHistory = [];
        this.saveHistoryToStorage();
        this.updateHistoryDisplay();
    }

    async syncOfflineData() {
        // Sync any offline data when connection is restored
        const offlineData = this.getOfflineData();
        if (offlineData.length > 0) {
            try {
                for (const location of offlineData) {
                    await this.saveToServer(location);
                }
                this.clearOfflineData();
                this.showSuccess('Offline data synced successfully!');
            } catch (error) {
                console.error('Sync error:', error);
            }
        }
    }

    // Storage methods
    loadLocationHistory() {
        const stored = localStorage.getItem('mobileLocationHistory');
        if (stored) {
            this.locationHistory = JSON.parse(stored);
            this.updateHistoryDisplay();
        }
    }

    saveHistoryToStorage() {
        localStorage.setItem('mobileLocationHistory', JSON.stringify(this.locationHistory));
    }

    saveToLocalStorage(location) {
        const offlineData = this.getOfflineData();
        offlineData.push(location);
        localStorage.setItem('mobileLocationOfflineData', JSON.stringify(offlineData));
    }

    getOfflineData() {
        const stored = localStorage.getItem('mobileLocationOfflineData');
        return stored ? JSON.parse(stored) : [];
    }

    clearOfflineData() {
        localStorage.removeItem('mobileLocationOfflineData');
    }

    async saveToServer(location) {
        // Implementation for saving to server
        const response = await fetch('/api/v1/locations/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                latitude: location.latitude,
                longitude: location.longitude,
                source: location.source,
                accuracy: location.accuracy
            })
        });

        if (!response.ok) {
            throw new Error('Failed to save location');
        }

        return response.json();
    }

    // Utility methods
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.top = '100px';
        notification.style.left = '10px';
        notification.style.right = '10px';
        notification.style.zIndex = '1000';
        notification.innerHTML = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    navigateToNextStep() {
        // Navigate to next step in the farm setup process
        window.location.href = '/farm-profile';
    }

    // Public methods for HTML onclick handlers
    centerOnCurrentLocation() {
        this.getCurrentLocation();
    }

    clearMapSelection() {
        if (this.mapMarker) {
            this.mobileMap.removeLayer(this.mapMarker);
            this.mapMarker = null;
        }
    }

    toggleMapType() {
        // Toggle between different map types
        console.log('Toggle map type');
    }

    showHelp() {
        const modal = new bootstrap.Modal(document.getElementById('helpModal'));
        modal.show();
    }

    goBack() {
        window.history.back();
    }
}

// Initialize the mobile location input system
let mobileLocationInput;

function initializeMobileLocationInput() {
    mobileLocationInput = new MobileLocationInput();
}

// Global functions for HTML onclick handlers
function toggleMethod(method) {
    mobileLocationInput.toggleMethod(method);
}

function getCurrentLocation() {
    mobileLocationInput.getCurrentLocation();
}

function centerOnCurrentLocation() {
    mobileLocationInput.centerOnCurrentLocation();
}

function clearMapSelection() {
    mobileLocationInput.clearMapSelection();
}

function toggleMapType() {
    mobileLocationInput.toggleMapType();
}

function setCoordinateFormat(format) {
    mobileLocationInput.setCoordinateFormat(format);
}

function clearAllInputs() {
    mobileLocationInput.clearAllInputs();
}

function saveLocation() {
    mobileLocationInput.saveLocation();
}

function clearHistory() {
    mobileLocationInput.clearHistory();
}

function showHelp() {
    mobileLocationInput.showHelp();
}

function goBack() {
    mobileLocationInput.goBack();
}