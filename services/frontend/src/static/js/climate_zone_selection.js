// Climate Zone Selection JavaScript Functions

class ClimateZoneSelector {
    constructor() {
        this.currentLocation = null;
        this.availableZones = [];
        this.usdaZones = [];
        this.koppenTypes = [];
        
        this.initializeEventListeners();
        this.loadInitialData();
    }

    initializeEventListeners() {
        // Auto-detection form listeners
        const coordsForm = document.getElementById('coords-form');
        const addressForm = document.getElementById('address-form');
        const manualForm = document.getElementById('manual-zone-form');
        
        if (coordsForm) {
            coordsForm.addEventListener('submit', (e) => this.handleCoordsSubmit(e));
        }
        
        if (addressForm) {
            addressForm.addEventListener('submit', (e) => this.handleAddressSubmit(e));
        }
        
        if (manualForm) {
            manualForm.addEventListener('submit', (e) => this.handleManualSubmit(e));
        }

        // Get current location button
        const getCurrentLocationBtn = document.getElementById('get-current-location');
        if (getCurrentLocationBtn) {
            getCurrentLocationBtn.addEventListener('click', () => this.getCurrentLocation());
        }

        // Zone type selection listeners
        const zoneTypeRadios = document.querySelectorAll('input[name="zone_type"]');
        zoneTypeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => this.handleZoneTypeChange(e));
        });
    }

    async loadInitialData() {
        try {
            // Load available zones
            await this.loadAvailableZones();
            await this.loadUSDAZones();
            await this.loadKoppenTypes();
            
            // Populate dropdowns
            this.populateZoneDropdowns();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showAlert('Error loading zone data. Please refresh the page.', 'danger');
        }
    }

    async loadAvailableZones() {
        try {
            const response = await fetch('/api/climate/zones');
            if (response.ok) {
                this.availableZones = await response.json();
            }
        } catch (error) {
            console.error('Error loading available zones:', error);
        }
    }

    async loadUSDAZones() {
        try {
            const response = await fetch('/api/climate/usda-zones');
            if (response.ok) {
                this.usdaZones = await response.json();
            }
        } catch (error) {
            console.error('Error loading USDA zones:', error);
        }
    }

    async loadKoppenTypes() {
        try {
            const response = await fetch('/api/climate/koppen-types');
            if (response.ok) {
                this.koppenTypes = await response.json();
            }
        } catch (error) {
            console.error('Error loading Köppen types:', error);
        }
    }

    populateZoneDropdowns() {
        // Populate USDA zones dropdown
        const usdaSelect = document.getElementById('usda-zone');
        if (usdaSelect && this.usdaZones.length > 0) {
            usdaSelect.innerHTML = '<option value="">Select USDA Zone</option>';
            this.usdaZones.forEach(zone => {
                const option = document.createElement('option');
                option.value = zone.zone_id || zone.name;
                option.textContent = `${zone.zone_id || zone.name} - ${zone.description || zone.temp_range}`;
                usdaSelect.appendChild(option);
            });
        }

        // Populate Köppen types dropdown
        const koppenSelect = document.getElementById('koppen-climate');
        if (koppenSelect && this.koppenTypes.length > 0) {
            koppenSelect.innerHTML = '<option value="">Select Köppen Type</option>';
            this.koppenTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.code || type.name;
                option.textContent = `${type.code || type.name} - ${type.description || type.name}`;
                koppenSelect.appendChild(option);
            });
        }
    }

    async handleCoordsSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const latitude = parseFloat(formData.get('latitude'));
        const longitude = parseFloat(formData.get('longitude'));
        
        // Validate coordinates
        if (!this.validateCoordinates(latitude, longitude)) {
            this.showAlert('Please enter valid coordinates (Latitude: -90 to 90, Longitude: -180 to 180)', 'danger');
            return;
        }

        const submitBtn = event.target.querySelector('button[type="submit"]');
        this.showLoadingState(submitBtn);

        try {
            const response = await fetch('/api/climate/detect-zone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayDetectionResults(result, 'coordinates');
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Error detecting climate zone', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Network error. Please try again.', 'danger');
        } finally {
            this.hideLoadingState(submitBtn);
        }
    }

    async handleAddressSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const address = formData.get('address').trim();
        
        if (!address || address.length < 3) {
            this.showAlert('Please enter a valid address', 'danger');
            return;
        }

        const submitBtn = event.target.querySelector('button[type="submit"]');
        this.showLoadingState(submitBtn);

        try {
            const response = await fetch('/api/climate/zone-from-address', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    address: address
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayDetectionResults(result, 'address');
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Error detecting climate zone from address', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Network error. Please try again.', 'danger');
        } finally {
            this.hideLoadingState(submitBtn);
        }
    }

    async handleManualSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const zoneType = formData.get('zone_type');
        
        let zoneData = {};
        
        if (zoneType === 'usda') {
            const usdaZone = formData.get('usda_zone');
            if (!usdaZone) {
                this.showAlert('Please select a USDA zone', 'danger');
                return;
            }
            zoneData = { type: 'usda', zone: usdaZone };
        } else if (zoneType === 'koppen') {
            const koppenClimate = formData.get('koppen_climate');
            if (!koppenClimate) {
                this.showAlert('Please select a Köppen climate type', 'danger');
                return;
            }
            zoneData = { type: 'koppen', zone: koppenClimate };
        } else {
            this.showAlert('Please select a zone type', 'danger');
            return;
        }

        const submitBtn = event.target.querySelector('button[type="submit"]');
        this.showLoadingState(submitBtn);

        try {
            const response = await fetch('/api/climate/validate-zone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(zoneData)
            });

            if (response.ok) {
                const result = await response.json();
                this.displayManualResults(result, zoneData);
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Error validating climate zone', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Network error. Please try again.', 'danger');
        } finally {
            this.hideLoadingState(submitBtn);
        }
    }

    getCurrentLocation() {
        if (!navigator.geolocation) {
            this.showAlert('Geolocation is not supported by this browser', 'warning');
            return;
        }

        const btn = document.getElementById('get-current-location');
        this.showLoadingState(btn);

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                
                // Fill in the coordinates form
                document.getElementById('latitude').value = latitude.toFixed(6);
                document.getElementById('longitude').value = longitude.toFixed(6);
                
                this.showAlert('Location detected successfully', 'success');
                this.hideLoadingState(btn);
            },
            (error) => {
                let message = 'Error getting your location: ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message += 'Location access denied by user';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message += 'Location information unavailable';
                        break;
                    case error.TIMEOUT:
                        message += 'Location request timed out';
                        break;
                    default:
                        message += 'Unknown error occurred';
                        break;
                }
                this.showAlert(message, 'danger');
                this.hideLoadingState(btn);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    }

    handleZoneTypeChange(event) {
        const zoneType = event.target.value;
        const usdaGroup = document.getElementById('usda-zone-group');
        const koppenGroup = document.getElementById('koppen-zone-group');
        
        if (zoneType === 'usda') {
            usdaGroup.style.display = 'block';
            koppenGroup.style.display = 'none';
        } else if (zoneType === 'koppen') {
            usdaGroup.style.display = 'none';
            koppenGroup.style.display = 'block';
        } else {
            usdaGroup.style.display = 'none';
            koppenGroup.style.display = 'none';
        }
    }

    displayDetectionResults(result, method) {
        const resultsDiv = document.getElementById('detection-results');
        if (!resultsDiv) return;

        resultsDiv.style.display = 'block';
        
        let html = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> Climate Zone Detected Successfully</h5>
                <p><strong>Detection Method:</strong> ${method === 'coordinates' ? 'GPS Coordinates' : 'Address Lookup'}</p>
            </div>
        `;

        if (result.location) {
            html += `
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h6>Location Information</h6>
                        <p><strong>Coordinates:</strong> ${result.location.latitude}, ${result.location.longitude}</p>
                        ${result.location.address ? `<p><strong>Address:</strong> ${result.location.address}</p>` : ''}
                    </div>
                </div>
            `;
        }

        if (result.climate_zones) {
            html += '<div class="row">';
            
            if (result.climate_zones.usda) {
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-thermometer-half"></i> USDA Hardiness Zone</h6>
                            </div>
                            <div class="card-body">
                                <h4 class="text-primary">${result.climate_zones.usda.zone}</h4>
                                <p class="mb-1"><strong>Temperature Range:</strong> ${result.climate_zones.usda.temp_range}</p>
                                <p class="mb-0 text-muted">${result.climate_zones.usda.description}</p>
                            </div>
                        </div>
                    </div>
                `;
            }

            if (result.climate_zones.koppen) {
                html += `
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-header">
                                <h6><i class="fas fa-cloud-sun"></i> Köppen Climate Type</h6>
                            </div>
                            <div class="card-body">
                                <h4 class="text-success">${result.climate_zones.koppen.code}</h4>
                                <p class="mb-1"><strong>Classification:</strong> ${result.climate_zones.koppen.name}</p>
                                <p class="mb-0 text-muted">${result.climate_zones.koppen.description}</p>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
        }

        if (result.recommendations) {
            html += `
                <div class="mt-3">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-lightbulb"></i> Agricultural Recommendations</h6>
                        <ul class="mb-0">
                            ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        resultsDiv.innerHTML = html;
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    displayManualResults(result, zoneData) {
        const resultsDiv = document.getElementById('manual-results');
        if (!resultsDiv) return;

        resultsDiv.style.display = 'block';
        
        let html = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> Climate Zone Validated</h5>
                <p><strong>Selection Method:</strong> Manual Selection</p>
            </div>
        `;

        html += `
            <div class="card">
                <div class="card-header">
                    <h6><i class="fas fa-map-marker-alt"></i> Selected Climate Zone</h6>
                </div>
                <div class="card-body">
                    <h4 class="text-primary">${zoneData.zone}</h4>
                    <p class="mb-1"><strong>Type:</strong> ${zoneData.type.toUpperCase()}</p>
                    ${result.description ? `<p class="mb-0 text-muted">${result.description}</p>` : ''}
                </div>
            </div>
        `;

        if (result.characteristics) {
            html += `
                <div class="mt-3">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-info-circle"></i> Zone Characteristics</h6>
                        <ul class="mb-0">
                            ${result.characteristics.map(char => `<li>${char}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        resultsDiv.innerHTML = html;
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    validateCoordinates(latitude, longitude) {
        return !isNaN(latitude) && !isNaN(longitude) && 
               latitude >= -90 && latitude <= 90 && 
               longitude >= -180 && longitude <= 180;
    }

    showLoadingState(button) {
        if (!button) return;
        
        const spinner = button.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'inline-block';
        }
        
        button.disabled = true;
        const originalText = button.textContent;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<span class="loading-spinner spinner-border spinner-border-sm me-2"></span>Loading...';
    }

    hideLoadingState(button) {
        if (!button) return;
        
        button.disabled = false;
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.textContent = originalText;
            button.removeAttribute('data-original-text');
        }
    }

    showAlert(message, type = 'info', container = null) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
        } else {
            const alertContainer = document.getElementById('alert-container') || document.body;
            alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        }
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Utility functions for climate zone operations
class ClimateZoneUtils {
    static formatTemperatureRange(tempRange) {
        if (!tempRange) return 'N/A';
        return tempRange.includes('°') ? tempRange : `${tempRange}°F`;
    }

    static getZoneColor(zoneType, zone) {
        const usdaColors = {
            '1': '#1e3a8a', '2': '#1e40af', '3': '#1d4ed8', '4': '#2563eb',
            '5': '#3b82f6', '6': '#60a5fa', '7': '#93c5fd', '8': '#dbeafe',
            '9': '#fef3c7', '10': '#fde68a', '11': '#fcd34d'
        };
        
        if (zoneType === 'usda' && usdaColors[zone]) {
            return usdaColors[zone];
        }
        
        return '#6b7280'; // Default gray
    }

    static validateZoneFormat(zoneType, zone) {
        if (zoneType === 'usda') {
            return /^[1-9][0-9]?[ab]?$/i.test(zone);
        } else if (zoneType === 'koppen') {
            return /^[A-E][a-z]*$/i.test(zone);
        }
        return false;
    }

    static getSeasonalRecommendations(zone, month = null) {
        const currentMonth = month || new Date().getMonth() + 1;
        const recommendations = [];
        
        // Basic seasonal recommendations based on USDA zones
        const zoneNum = parseInt(zone);
        
        if (currentMonth >= 3 && currentMonth <= 5) { // Spring
            recommendations.push('Consider spring planting of cool-season crops');
            if (zoneNum >= 6) recommendations.push('Begin warm-season crop preparation');
        } else if (currentMonth >= 6 && currentMonth <= 8) { // Summer
            recommendations.push('Monitor irrigation needs carefully');
            recommendations.push('Consider heat-tolerant varieties');
        } else if (currentMonth >= 9 && currentMonth <= 11) { // Fall
            recommendations.push('Plan fall/winter cover crops');
            if (zoneNum <= 7) recommendations.push('Prepare for frost protection');
        } else { // Winter
            recommendations.push('Plan crop rotations for next season');
            if (zoneNum >= 8) recommendations.push('Consider winter growing opportunities');
        }
        
        return recommendations;
    }
}

// Initialize the climate zone selector when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.climateZoneSelector = new ClimateZoneSelector();
    window.ClimateZoneUtils = ClimateZoneUtils;
});

// Export for use in other scripts
window.ClimateZoneSelector = ClimateZoneSelector;