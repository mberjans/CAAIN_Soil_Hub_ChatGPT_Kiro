/**
 * Mobile GPS Field Mapping
 * 
 * Provides GPS-based field mapping and location services
 * for agricultural field management and tracking.
 */

class MobileGPSFieldMapping {
    constructor() {
        this.currentPosition = null;
        this.watchId = null;
        this.fieldBoundary = [];
        this.fieldArea = 0;
        this.isTracking = false;
        this.trackingHistory = [];
        this.deviceIntegration = null;
        this.mapElement = null;
        this.markerLayer = null;
        
        this.init();
    }

    async init() {
        this.deviceIntegration = new MobileDeviceIntegration();
        
        // Wait for device integration to initialize
        await new Promise(resolve => {
            const checkInit = () => {
                if (this.deviceIntegration && this.deviceIntegration.isFeatureAvailable('gps')) {
                    resolve();
                } else {
                    setTimeout(checkInit, 100);
                }
            };
            checkInit();
        });

        this.setupMapElement();
        this.setupEventListeners();
        this.getCurrentLocation();
    }

    /**
     * Setup map element
     */
    setupMapElement() {
        this.mapElement = document.getElementById('fieldMap');
        if (this.mapElement) {
            this.initializeMap();
        }
    }

    /**
     * Initialize map
     */
    initializeMap() {
        // Create a simple map visualization
        this.mapElement.innerHTML = `
            <div class="map-container">
                <div class="map-overlay">
                    <div class="map-controls">
                        <button id="startTracking" class="map-btn btn-start">
                            <i class="fas fa-play"></i> Start Tracking
                        </button>
                        <button id="stopTracking" class="map-btn btn-stop" style="display: none;">
                            <i class="fas fa-stop"></i> Stop Tracking
                        </button>
                        <button id="clearField" class="map-btn btn-clear">
                            <i class="fas fa-trash"></i> Clear Field
                        </button>
                    </div>
                    <div class="map-info">
                        <div class="info-item">
                            <span class="info-label">Latitude:</span>
                            <span id="currentLat">--</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Longitude:</span>
                            <span id="currentLng">--</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Accuracy:</span>
                            <span id="currentAccuracy">--</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Field Area:</span>
                            <span id="fieldArea">0 acres</span>
                        </div>
                    </div>
                </div>
                <div class="map-canvas" id="mapCanvas">
                    <div class="map-placeholder">
                        <i class="fas fa-map fa-3x text-muted mb-3"></i>
                        <p class="text-muted">GPS Field Mapping</p>
                        <p class="small text-muted">Tap "Start Tracking" to begin mapping your field</p>
                    </div>
                </div>
            </div>
        `;

        this.setupMapControls();
    }

    /**
     * Setup map controls
     */
    setupMapControls() {
        const startBtn = document.getElementById('startTracking');
        const stopBtn = document.getElementById('stopTracking');
        const clearBtn = document.getElementById('clearField');

        if (startBtn) {
            startBtn.addEventListener('click', this.startFieldTracking.bind(this));
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', this.stopFieldTracking.bind(this));
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', this.clearFieldBoundary.bind(this));
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Device orientation changes
        document.addEventListener('mobileDevice:orientationChange', this.handleOrientationChange.bind(this));
        
        // App visibility changes
        document.addEventListener('mobileDevice:visibilityChange', this.handleVisibilityChange.bind(this));
    }

    /**
     * Get current location
     */
    async getCurrentLocation() {
        if (!this.deviceIntegration.hasPermission('location')) {
            this.showError('Location permission is required for field mapping');
            return;
        }

        try {
            const position = await this.getPositionPromise();
            this.currentPosition = position;
            this.updateLocationDisplay(position);
            this.showSuccess('Location acquired successfully');
        } catch (error) {
            console.error('Error getting location:', error);
            this.showError('Failed to get location: ' + error.message);
        }
    }

    /**
     * Get position as promise
     */
    getPositionPromise() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                resolve,
                reject,
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                }
            );
        });
    }

    /**
     * Start field tracking
     */
    startFieldTracking() {
        if (!this.deviceIntegration.hasPermission('location')) {
            this.showError('Location permission is required');
            return;
        }

        this.isTracking = true;
        this.fieldBoundary = [];
        this.trackingHistory = [];

        // Start watching position
        this.watchId = navigator.geolocation.watchPosition(
            this.handlePositionUpdate.bind(this),
            this.handlePositionError.bind(this),
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 1000
            }
        );

        // Update UI
        this.updateTrackingUI();
        this.showSuccess('Field tracking started');
    }

    /**
     * Stop field tracking
     */
    stopFieldTracking() {
        this.isTracking = false;

        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }

        // Calculate field area
        this.calculateFieldArea();

        // Update UI
        this.updateTrackingUI();
        this.showSuccess('Field tracking stopped');
    }

    /**
     * Handle position updates
     */
    handlePositionUpdate(position) {
        this.currentPosition = position;
        this.updateLocationDisplay(position);

        if (this.isTracking) {
            const point = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                timestamp: position.timestamp
            };

            this.fieldBoundary.push(point);
            this.trackingHistory.push(point);
            this.updateFieldVisualization();
        }
    }

    /**
     * Handle position errors
     */
    handlePositionError(error) {
        console.error('Position error:', error);
        
        let message = 'Location error: ';
        switch (error.code) {
            case error.PERMISSION_DENIED:
                message += 'Permission denied';
                break;
            case error.POSITION_UNAVAILABLE:
                message += 'Position unavailable';
                break;
            case error.TIMEOUT:
                message += 'Request timeout';
                break;
            default:
                message += 'Unknown error';
                break;
        }

        this.showError(message);
    }

    /**
     * Update location display
     */
    updateLocationDisplay(position) {
        const latElement = document.getElementById('currentLat');
        const lngElement = document.getElementById('currentLng');
        const accuracyElement = document.getElementById('currentAccuracy');

        if (latElement) {
            latElement.textContent = position.coords.latitude.toFixed(6);
        }

        if (lngElement) {
            lngElement.textContent = position.coords.longitude.toFixed(6);
        }

        if (accuracyElement) {
            accuracyElement.textContent = `${Math.round(position.coords.accuracy)}m`;
        }
    }

    /**
     * Update tracking UI
     */
    updateTrackingUI() {
        const startBtn = document.getElementById('startTracking');
        const stopBtn = document.getElementById('stopTracking');

        if (this.isTracking) {
            if (startBtn) startBtn.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'inline-block';
        } else {
            if (startBtn) startBtn.style.display = 'inline-block';
            if (stopBtn) stopBtn.style.display = 'none';
        }
    }

    /**
     * Update field visualization
     */
    updateFieldVisualization() {
        const mapCanvas = document.getElementById('mapCanvas');
        if (!mapCanvas) return;

        if (this.fieldBoundary.length === 0) {
            mapCanvas.innerHTML = `
                <div class="map-placeholder">
                    <i class="fas fa-map fa-3x text-muted mb-3"></i>
                    <p class="text-muted">GPS Field Mapping</p>
                    <p class="small text-muted">Tap "Start Tracking" to begin mapping your field</p>
                </div>
            `;
            return;
        }

        // Create field boundary visualization
        const boundaryPoints = this.fieldBoundary.map(point => 
            `${point.latitude},${point.longitude}`
        ).join(' ');

        mapCanvas.innerHTML = `
            <div class="field-visualization">
                <div class="field-boundary">
                    <svg viewBox="0 0 400 300" class="field-svg">
                        <polygon 
                            points="${this.generatePolygonPoints()}" 
                            fill="rgba(40, 167, 69, 0.3)" 
                            stroke="#28a745" 
                            stroke-width="2"
                        />
                        ${this.generateFieldMarkers()}
                    </svg>
                </div>
                <div class="field-stats">
                    <div class="stat-item">
                        <span class="stat-label">Points:</span>
                        <span class="stat-value">${this.fieldBoundary.length}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Area:</span>
                        <span class="stat-value">${this.fieldArea.toFixed(2)} acres</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generate polygon points for SVG
     */
    generatePolygonPoints() {
        if (this.fieldBoundary.length < 3) return '';

        // Simple projection for visualization
        const centerLat = this.fieldBoundary.reduce((sum, p) => sum + p.latitude, 0) / this.fieldBoundary.length;
        const centerLng = this.fieldBoundary.reduce((sum, p) => sum + p.longitude, 0) / this.fieldBoundary.length;

        return this.fieldBoundary.map(point => {
            const x = 200 + (point.longitude - centerLng) * 10000;
            const y = 150 + (point.latitude - centerLat) * 10000;
            return `${x},${y}`;
        }).join(' ');
    }

    /**
     * Generate field markers
     */
    generateFieldMarkers() {
        return this.fieldBoundary.map((point, index) => {
            const centerLat = this.fieldBoundary.reduce((sum, p) => sum + p.latitude, 0) / this.fieldBoundary.length;
            const centerLng = this.fieldBoundary.reduce((sum, p) => sum + p.longitude, 0) / this.fieldBoundary.length;
            
            const x = 200 + (point.longitude - centerLng) * 10000;
            const y = 150 + (point.latitude - centerLat) * 10000;
            
            return `<circle cx="${x}" cy="${y}" r="3" fill="#dc3545" />`;
        }).join('');
    }

    /**
     * Calculate field area using shoelace formula
     */
    calculateFieldArea() {
        if (this.fieldBoundary.length < 3) {
            this.fieldArea = 0;
            return;
        }

        // Convert to meters using Haversine formula for distance
        let area = 0;
        const n = this.fieldBoundary.length;

        for (let i = 0; i < n; i++) {
            const j = (i + 1) % n;
            const lat1 = this.fieldBoundary[i].latitude * Math.PI / 180;
            const lng1 = this.fieldBoundary[i].longitude * Math.PI / 180;
            const lat2 = this.fieldBoundary[j].latitude * Math.PI / 180;
            const lng2 = this.fieldBoundary[j].longitude * Math.PI / 180;

            area += (lng2 - lng1) * (2 + Math.sin(lat1) + Math.sin(lat2));
        }

        area = Math.abs(area) * 6371000 * 6371000 / 2; // Earth radius squared
        this.fieldArea = area / 4046.86; // Convert to acres

        // Update display
        const areaElement = document.getElementById('fieldArea');
        if (areaElement) {
            areaElement.textContent = `${this.fieldArea.toFixed(2)} acres`;
        }
    }

    /**
     * Clear field boundary
     */
    clearFieldBoundary() {
        this.fieldBoundary = [];
        this.fieldArea = 0;
        this.trackingHistory = [];
        
        this.updateFieldVisualization();
        
        const areaElement = document.getElementById('fieldArea');
        if (areaElement) {
            areaElement.textContent = '0 acres';
        }

        this.showSuccess('Field boundary cleared');
    }

    /**
     * Handle device orientation changes
     */
    handleOrientationChange(event) {
        const { orientation } = event.detail;
        
        // Adjust map layout for orientation
        if (orientation.includes('landscape')) {
            this.adjustMapForLandscape();
        } else {
            this.adjustMapForPortrait();
        }
    }

    /**
     * Adjust map for landscape orientation
     */
    adjustMapForLandscape() {
        const mapContainer = document.querySelector('.map-container');
        if (mapContainer) {
            mapContainer.classList.add('landscape-mode');
        }
    }

    /**
     * Adjust map for portrait orientation
     */
    adjustMapForPortrait() {
        const mapContainer = document.querySelector('.map-container');
        if (mapContainer) {
            mapContainer.classList.remove('landscape-mode');
        }
    }

    /**
     * Handle app visibility changes
     */
    handleVisibilityChange(event) {
        const { visible } = event.detail;
        
        if (visible && this.isTracking) {
            // Resume tracking when app becomes visible
            this.resumeTracking();
        } else if (!visible && this.isTracking) {
            // Pause tracking when app becomes hidden
            this.pauseTracking();
        }
    }

    /**
     * Resume tracking
     */
    resumeTracking() {
        if (this.isTracking && !this.watchId) {
            this.watchId = navigator.geolocation.watchPosition(
                this.handlePositionUpdate.bind(this),
                this.handlePositionError.bind(this),
                {
                    enableHighAccuracy: true,
                    timeout: 5000,
                    maximumAge: 1000
                }
            );
        }
    }

    /**
     * Pause tracking
     */
    pauseTracking() {
        if (this.watchId) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
    }

    /**
     * Export field data
     */
    exportFieldData() {
        const fieldData = {
            boundary: this.fieldBoundary,
            area: this.fieldArea,
            trackingHistory: this.trackingHistory,
            exportDate: new Date().toISOString()
        };

        const dataStr = JSON.stringify(fieldData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `field_data_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    /**
     * Get field data
     */
    getFieldData() {
        return {
            boundary: this.fieldBoundary,
            area: this.fieldArea,
            trackingHistory: this.trackingHistory,
            currentPosition: this.currentPosition
        };
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        if (this.deviceIntegration) {
            this.deviceIntegration.showNotification(message, { type: 'success' });
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.deviceIntegration) {
            this.deviceIntegration.showNotification(message, { type: 'error' });
        }
    }
}

// Export for use in other modules
window.MobileGPSFieldMapping = MobileGPSFieldMapping;

// CSS for GPS field mapping
const gpsStyles = `
.map-container {
    position: relative;
    background: #f8f9fa;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.map-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 10;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
}

.map-controls {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.map-btn {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-start {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
}

.btn-stop {
    background: linear-gradient(135deg, #dc3545, #e83e8c);
    color: white;
}

.btn-clear {
    background: linear-gradient(135deg, #ffc107, #fd7e14);
    color: white;
}

.map-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.map-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
}

.info-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0.5rem;
    background: rgba(40, 167, 69, 0.1);
    border-radius: 8px;
}

.info-label {
    font-size: 0.8rem;
    color: #6c757d;
    font-weight: 500;
}

.info-item span:last-child {
    font-weight: 600;
    color: #28a745;
}

.map-canvas {
    height: 300px;
    position: relative;
    background: linear-gradient(135deg, #e9ecef, #f8f9fa);
}

.map-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #6c757d;
}

.field-visualization {
    height: 100%;
    position: relative;
}

.field-boundary {
    height: 200px;
    background: white;
    border-radius: 8px;
    margin: 1rem;
    overflow: hidden;
}

.field-svg {
    width: 100%;
    height: 100%;
}

.field-stats {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    padding: 1rem;
    display: flex;
    justify-content: space-around;
}

.stat-item {
    text-align: center;
}

.stat-label {
    display: block;
    font-size: 0.8rem;
    color: #6c757d;
    margin-bottom: 0.25rem;
}

.stat-value {
    font-size: 1.2rem;
    font-weight: 600;
    color: #28a745;
}

.landscape-mode .map-canvas {
    height: 200px;
}

.landscape-mode .map-info {
    grid-template-columns: repeat(4, 1fr);
}

@media (max-width: 768px) {
    .map-controls {
        justify-content: center;
    }
    
    .map-btn {
        padding: 0.4rem 0.8rem;
        font-size: 0.8rem;
    }
    
    .map-info {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .field-stats {
        flex-direction: column;
        gap: 0.5rem;
    }
}
`;

// Inject styles
const gpsStyleSheet = document.createElement('style');
gpsStyleSheet.textContent = gpsStyles;
document.head.appendChild(gpsStyleSheet);