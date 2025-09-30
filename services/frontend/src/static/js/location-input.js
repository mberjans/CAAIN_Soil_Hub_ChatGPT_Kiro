/**
 * GPS Coordinate Input System
 * CAAIN Soil Hub - Farm Location Input
 * 
 * Handles multiple coordinate formats, GPS device integration,
 * real-time validation, and coordinate conversion.
 */

class GPSCoordinateInput {
    constructor() {
        this.map = null;
        this.marker = null;
        this.currentCoordinates = null;
        this.validationService = '/api/v1/validation';
        this.geocodingService = '/api/v1/geocoding';
        
        this.init();
    }

    init() {
        this.initializeMap();
        this.setupEventListeners();
        this.loadSavedLocation();
    }

    initializeMap() {
        // Initialize Leaflet map
        this.map = L.map('location-map').setView([40.0, -95.0], 4);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Add click handler for map selection
        this.map.on('click', (e) => {
            this.setCoordinatesFromMap(e.latlng.lat, e.latlng.lng);
        });

        // Add marker for current selection
        this.marker = L.marker([40.0, -95.0], { draggable: true }).addTo(this.map);
        
        this.marker.on('dragend', (e) => {
            const latlng = e.target.getLatLng();
            this.setCoordinatesFromMap(latlng.lat, latlng.lng);
        });
    }

    setupEventListeners() {
        // GPS button state management
        const gpsButton = document.getElementById('gps-button');
        const gpsButtonText = document.getElementById('gps-button-text');
        
        // Watch for GPS availability
        if ('geolocation' in navigator) {
            gpsButton.disabled = false;
            gpsButtonText.textContent = 'Get GPS Location';
        } else {
            gpsButton.disabled = true;
            gpsButtonText.textContent = 'GPS Not Available';
        }
    }

    async getCurrentLocation() {
        const gpsButton = document.getElementById('gps-button');
        const gpsButtonText = document.getElementById('gps-button-text');
        
        if (!navigator.geolocation) {
            this.showValidationFeedback('GPS is not supported by this browser.', 'error');
            return;
        }

        gpsButton.disabled = true;
        gpsButtonText.textContent = 'Getting Location...';

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 300000 // 5 minutes
        };

        try {
            const position = await this.getCurrentPositionPromise(options);
            const { latitude, longitude, accuracy } = position.coords;
            
            // Enhanced GPS reading with additional metadata
            const gpsReading = {
                latitude,
                longitude,
                accuracy,
                altitude: position.coords.altitude || null,
                timestamp: new Date().toISOString(),
                satellite_count: null, // Not available in browser API
                signal_strength: null, // Not available in browser API
                hdop: null, // Not available in browser API
                vdop: null // Not available in browser API
            };
            
            this.setCoordinatesFromGPS(latitude, longitude, accuracy);
            
            // Assess GPS accuracy and show enhanced feedback
            await this.assessGPSAccuracy(gpsReading);
            
        } catch (error) {
            this.handleGPSError(error);
        } finally {
            gpsButton.disabled = false;
            gpsButtonText.textContent = 'Get GPS Location';
        }
    }

    getCurrentPositionPromise(options) {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, options);
        });
    }

    async assessGPSAccuracy(gpsReading) {
        """Assess GPS accuracy using the backend service."""
        try {
            const response = await fetch('/api/v1/gps-accuracy/assess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(gpsReading)
            });

            if (!response.ok) {
                throw new Error(`GPS assessment failed: ${response.statusText}`);
            }

            const assessment = await response.json();
            this.displayGPSAssessment(assessment);
            
        } catch (error) {
            console.error('GPS accuracy assessment error:', error);
            // Fallback to basic accuracy display
            this.showValidationFeedback(
                `GPS location captured with ${Math.round(gpsReading.accuracy)}m accuracy`, 
                'success'
            );
        }
    }

    displayGPSAssessment(assessment) {
        """Display comprehensive GPS accuracy assessment."""
        const accuracyLevel = assessment.accuracy_level;
        const accuracy = Math.round(assessment.horizontal_accuracy);
        const confidence = Math.round(assessment.confidence_score * 100);
        
        // Determine feedback type based on accuracy level
        let feedbackType = 'success';
        let icon = '✓';
        
        switch (accuracyLevel) {
            case 'excellent':
                feedbackType = 'success';
                icon = '✓';
                break;
            case 'good':
                feedbackType = 'success';
                icon = '✓';
                break;
            case 'fair':
                feedbackType = 'warning';
                icon = '⚠';
                break;
            case 'poor':
                feedbackType = 'warning';
                icon = '⚠';
                break;
            case 'unacceptable':
                feedbackType = 'error';
                icon = '✗';
                break;
        }
        
        // Create detailed feedback message
        let message = `${icon} GPS Location Captured\n`;
        message += `Accuracy: ${accuracy}m (${accuracyLevel})\n`;
        message += `Confidence: ${confidence}%\n`;
        message += `Signal Quality: ${assessment.signal_quality}`;
        
        this.showValidationFeedback(message, feedbackType);
        
        // Display recommendations if available
        if (assessment.recommendations && assessment.recommendations.length > 0) {
            this.displayGPSRecommendations(assessment.recommendations);
        }
        
        // Show improvement suggestions if accuracy is poor
        if (assessment.improvement_methods && assessment.improvement_methods.length > 0) {
            this.displayImprovementSuggestions(assessment.improvement_methods);
        }
    }

    displayGPSRecommendations(recommendations) {
        """Display GPS accuracy recommendations."""
        const recommendationsContainer = document.getElementById('gps-recommendations');
        if (!recommendationsContainer) {
            // Create recommendations container if it doesn't exist
            const container = document.createElement('div');
            container.id = 'gps-recommendations';
            container.className = 'gps-recommendations mt-3';
            container.innerHTML = '<h6>GPS Recommendations:</h6>';
            
            const coordinateInfo = document.getElementById('coordinate-info');
            if (coordinateInfo) {
                coordinateInfo.parentNode.insertBefore(container, coordinateInfo.nextSibling);
            }
        }
        
        const container = document.getElementById('gps-recommendations');
        container.innerHTML = '<h6>GPS Recommendations:</h6>';
        
        const ul = document.createElement('ul');
        ul.className = 'list-unstyled small';
        
        recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            li.className = 'text-muted';
            ul.appendChild(li);
        });
        
        container.appendChild(ul);
    }

    displayImprovementSuggestions(improvementMethods) {
        """Display GPS accuracy improvement suggestions."""
        const improvementContainer = document.getElementById('gps-improvement');
        if (!improvementContainer) {
            // Create improvement container if it doesn't exist
            const container = document.createElement('div');
            container.id = 'gps-improvement';
            container.className = 'gps-improvement mt-3';
            container.innerHTML = '<h6>Improve GPS Accuracy:</h6>';
            
            const recommendationsContainer = document.getElementById('gps-recommendations');
            if (recommendationsContainer) {
                recommendationsContainer.parentNode.insertBefore(container, recommendationsContainer.nextSibling);
            }
        }
        
        const container = document.getElementById('gps-improvement');
        container.innerHTML = '<h6>Improve GPS Accuracy:</h6>';
        
        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'btn-group-vertical w-100';
        
        improvementMethods.forEach(method => {
            const button = document.createElement('button');
            button.className = 'btn btn-outline-primary btn-sm mb-1';
            button.textContent = this.getImprovementMethodText(method);
            button.onclick = () => this.applyImprovementMethod(method);
            buttonGroup.appendChild(button);
        });
        
        container.appendChild(buttonGroup);
    }

    getImprovementMethodText(method) {
        """Get human-readable text for improvement method."""
        const methodTexts = {
            'multi_reading_average': 'Take Multiple Readings',
            'differential_gps': 'Use Differential GPS',
            'rtk_correction': 'Use RTK Correction',
            'signal_filtering': 'Apply Signal Filtering'
        };
        return methodTexts[method] || method;
    }

    async applyImprovementMethod(method) {
        """Apply GPS accuracy improvement method."""
        if (!this.currentCoordinates) {
            this.showValidationFeedback('No GPS coordinates available for improvement', 'error');
            return;
        }
        
        try {
            // For multi-reading average, take multiple readings
            if (method === 'multi_reading_average') {
                await this.takeMultipleReadings();
            } else {
                this.showValidationFeedback(
                    `${this.getImprovementMethodText(method)} requires specialized equipment`, 
                    'info'
                );
            }
        } catch (error) {
            console.error('Improvement method error:', error);
            this.showValidationFeedback('Failed to apply improvement method', 'error');
        }
    }

    async takeMultipleReadings() {
        """Take multiple GPS readings for averaging."""
        const readings = [];
        const maxReadings = 5;
        
        this.showValidationFeedback('Taking multiple GPS readings for better accuracy...', 'info');
        
        for (let i = 0; i < maxReadings; i++) {
            try {
                const position = await this.getCurrentPositionPromise({
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0 // Force fresh reading
                });
                
                readings.push({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    altitude: position.coords.altitude || null,
                    timestamp: new Date().toISOString()
                });
                
                // Wait between readings
                if (i < maxReadings - 1) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
                
            } catch (error) {
                console.warn(`Reading ${i + 1} failed:`, error);
            }
        }
        
        if (readings.length >= 2) {
            // Send readings for improvement
            await this.improveGPSAccuracy(readings);
        } else {
            this.showValidationFeedback('Insufficient readings for improvement', 'warning');
        }
    }

    async improveGPSAccuracy(readings) {
        """Improve GPS accuracy using multiple readings."""
        try {
            const response = await fetch('/api/v1/gps-accuracy/improve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ readings })
            });

            if (!response.ok) {
                throw new Error(`GPS improvement failed: ${response.statusText}`);
            }

            const improvement = await response.json();
            this.displayImprovementResult(improvement);
            
        } catch (error) {
            console.error('GPS accuracy improvement error:', error);
            this.showValidationFeedback('Failed to improve GPS accuracy', 'error');
        }
    }

    displayImprovementResult(improvement) {
        """Display GPS accuracy improvement result."""
        const originalAccuracy = Math.round(improvement.original_accuracy);
        const improvedAccuracy = Math.round(improvement.improved_accuracy);
        const improvementPercent = Math.round(improvement.improvement_percentage);
        
        let message = `GPS Accuracy Improved!\n`;
        message += `Original: ${originalAccuracy}m → Improved: ${improvedAccuracy}m\n`;
        message += `Improvement: ${improvementPercent}%`;
        
        this.showValidationFeedback(message, 'success');
        
        // Update coordinates with improved values
        if (improvement.improved_coordinates) {
            this.setCoordinatesFromGPS(
                improvement.improved_coordinates.latitude,
                improvement.improved_coordinates.longitude,
                improvedAccuracy
            );
        }
    }

    handleGPSError(error) {
        let message = 'Unable to get GPS location. ';
        
        switch (error.code) {
            case error.PERMISSION_DENIED:
                message += 'Location access denied. Please enable location permissions.';
                break;
            case error.POSITION_UNAVAILABLE:
                message += 'Location information unavailable.';
                break;
            case error.TIMEOUT:
                message += 'Location request timed out.';
                break;
            default:
                message += 'An unknown error occurred.';
                break;
        }
        
        this.showValidationFeedback(message, 'error');
    }

    setCoordinatesFromGPS(latitude, longitude, accuracy = null) {
        this.currentCoordinates = { latitude, longitude, accuracy };
        this.updateCoordinateInputs(latitude, longitude);
        this.updateMapMarker(latitude, longitude);
        this.updateCoordinateDisplay();
        this.enableValidationButton();
    }

    setCoordinatesFromMap(latitude, longitude) {
        this.currentCoordinates = { latitude, longitude };
        this.updateCoordinateInputs(latitude, longitude);
        this.updateCoordinateDisplay();
        this.enableValidationButton();
    }

    updateCoordinateInputs(latitude, longitude) {
        // Update decimal degrees inputs
        document.getElementById('latitude-decimal').value = latitude.toFixed(6);
        document.getElementById('longitude-decimal').value = longitude.toFixed(6);

        // Update DMS inputs
        this.updateDMSInputs(latitude, longitude);

        // Update UTM inputs
        this.updateUTMInputs(latitude, longitude);

        // Update MGRS input
        this.updateMGRSInput(latitude, longitude);
    }

    updateDMSInputs(latitude, longitude) {
        const latDMS = this.decimalToDMS(latitude, true);
        const lonDMS = this.decimalToDMS(longitude, false);

        document.getElementById('lat-degrees').value = latDMS.degrees;
        document.getElementById('lat-minutes').value = latDMS.minutes.toFixed(2);
        document.getElementById('lat-seconds').value = latDMS.seconds.toFixed(2);

        document.getElementById('lon-degrees').value = lonDMS.degrees;
        document.getElementById('lon-minutes').value = lonDMS.minutes.toFixed(2);
        document.getElementById('lon-seconds').value = lonDMS.seconds.toFixed(2);
    }

    updateUTMInputs(latitude, longitude) {
        // Simplified UTM conversion (in production, use proper UTM library)
        const utm = this.decimalToUTM(latitude, longitude);
        
        document.getElementById('utm-zone').value = utm.zone;
        document.getElementById('utm-easting').value = Math.round(utm.easting);
        document.getElementById('utm-northing').value = Math.round(utm.northing);
    }

    updateMGRSInput(latitude, longitude) {
        // Simplified MGRS conversion (in production, use proper MGRS library)
        const mgrs = this.decimalToMGRS(latitude, longitude);
        document.getElementById('mgrs-coordinate').value = mgrs;
    }

    updateMapMarker(latitude, longitude) {
        this.map.setView([latitude, longitude], 10);
        this.marker.setLatLng([latitude, longitude]);
    }

    updateCoordinateDisplay() {
        if (!this.currentCoordinates) return;

        const { latitude, longitude, accuracy } = this.currentCoordinates;
        
        const coordinateInfo = document.getElementById('coordinate-info');
        coordinateInfo.innerHTML = `
            <strong>Latitude:</strong> ${latitude.toFixed(6)}°<br>
            <strong>Longitude:</strong> ${longitude.toFixed(6)}°<br>
            ${accuracy ? `<strong>Accuracy:</strong> ${Math.round(accuracy)}m<br>` : ''}
            <strong>Format:</strong> ${this.getCurrentFormat()}
        `;

        // Show format conversions
        const formatConversion = document.getElementById('format-conversion');
        formatConversion.innerHTML = this.getFormatConversions(latitude, longitude);

        document.getElementById('coordinate-display').style.display = 'block';
    }

    updateCoordinateDisplayWithConversions(convertedCoordinates) {
        if (!this.currentCoordinates) return;

        const { latitude, longitude, accuracy } = this.currentCoordinates;
        
        const coordinateInfo = document.getElementById('coordinate-info');
        coordinateInfo.innerHTML = `
            <strong>Latitude:</strong> ${latitude.toFixed(6)}°<br>
            <strong>Longitude:</strong> ${longitude.toFixed(6)}°<br>
            ${accuracy ? `<strong>Accuracy:</strong> ${Math.round(accuracy)}m<br>` : ''}
            <strong>Format:</strong> ${this.getCurrentFormat()}
        `;

        // Show format conversions from server response
        const formatConversion = document.getElementById('format-conversion');
        formatConversion.innerHTML = this.formatServerConversions(convertedCoordinates);

        document.getElementById('coordinate-display').style.display = 'block';
    }

    formatServerConversions(convertedCoordinates) {
        const decimal = convertedCoordinates.decimal;
        const dms = convertedCoordinates.dms;
        const utm = convertedCoordinates.utm;
        const mgrs = convertedCoordinates.mgrs;

        return `
            <strong>DMS:</strong> ${dms.latitude.degrees}° ${dms.latitude.minutes.toFixed(2)}′ ${dms.latitude.seconds.toFixed(2)}″ ${dms.latitude.direction}, ${dms.longitude.degrees}° ${dms.longitude.minutes.toFixed(2)}′ ${dms.longitude.seconds.toFixed(2)}″ ${dms.longitude.direction}<br>
            <strong>UTM:</strong> Zone ${utm.zone}${utm.hemisphere} ${Math.round(utm.easting)}E ${Math.round(utm.northing)}N<br>
            <strong>MGRS:</strong> ${mgrs}
        `;
    }

    getFormatConversions(latitude, longitude) {
        const dms = this.decimalToDMS(latitude, true);
        const utm = this.decimalToUTM(latitude, longitude);
        const mgrs = this.decimalToMGRS(latitude, longitude);

        return `
            <strong>DMS:</strong> ${dms.degrees}° ${dms.minutes.toFixed(2)}′ ${dms.seconds.toFixed(2)}″ N, ${this.decimalToDMS(longitude, false).degrees}° ${this.decimalToDMS(longitude, false).minutes.toFixed(2)}′ ${this.decimalToDMS(longitude, false).seconds.toFixed(2)}″ W<br>
            <strong>UTM:</strong> Zone ${utm.zone} ${Math.round(utm.easting)}E ${Math.round(utm.northing)}N<br>
            <strong>MGRS:</strong> ${mgrs}
        `;
    }

    async validateAndUpdateCoordinates() {
        const format = document.getElementById('coordinate-format').value;
        let coordinateData;

        try {
            switch (format) {
                case 'decimal':
                    const lat = parseFloat(document.getElementById('latitude-decimal').value);
                    const lng = parseFloat(document.getElementById('longitude-decimal').value);
                    coordinateData = { latitude: lat, longitude: lng };
                    break;
                case 'dms':
                    coordinateData = {
                        latitude: {
                            degrees: parseInt(document.getElementById('lat-degrees').value) || 0,
                            minutes: parseInt(document.getElementById('lat-minutes').value) || 0,
                            seconds: parseFloat(document.getElementById('lat-seconds').value) || 0,
                            direction: 'N'
                        },
                        longitude: {
                            degrees: parseInt(document.getElementById('lon-degrees').value) || 0,
                            minutes: parseInt(document.getElementById('lon-minutes').value) || 0,
                            seconds: parseFloat(document.getElementById('lon-seconds').value) || 0,
                            direction: 'W'
                        }
                    };
                    break;
                case 'utm':
                    coordinateData = {
                        zone: parseInt(document.getElementById('utm-zone').value) || 1,
                        easting: parseFloat(document.getElementById('utm-easting').value) || 0,
                        northing: parseFloat(document.getElementById('utm-northing').value) || 0,
                        hemisphere: 'N'
                    };
                    break;
                case 'mgrs':
                    coordinateData = {
                        coordinate: document.getElementById('mgrs-coordinate').value
                    };
                    break;
            }

            // Validate using the new coordinate format validation endpoint
            const response = await fetch(`${this.validationService}/coordinate-format`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    format_type: format,
                    coordinate_data: coordinateData
                })
            });

            const result = await response.json();

            if (result.valid) {
                const decimalCoords = result.converted_coordinates.decimal;
                this.currentCoordinates = { 
                    latitude: decimalCoords.latitude, 
                    longitude: decimalCoords.longitude 
                };
                
                this.updateMapMarker(decimalCoords.latitude, decimalCoords.longitude);
                this.updateCoordinateDisplayWithConversions(result.converted_coordinates);
                this.enableValidationButton();
                
                if (result.warnings.length > 0) {
                    this.showValidationFeedback(
                        `Coordinates validated with warnings: ${result.warnings.join(', ')}`, 
                        'warning'
                    );
                } else {
                    this.showValidationFeedback('Coordinates validated successfully!', 'success');
                }
            } else {
                this.showValidationFeedback(
                    `Validation failed: ${result.errors.join(', ')}`, 
                    'error'
                );
            }

        } catch (error) {
            this.showValidationFeedback(`Coordinate validation error: ${error.message}`, 'error');
        }
    }

    async validateLocation() {
        if (!this.currentCoordinates) {
            this.showValidationFeedback('Please enter coordinates first.', 'error');
            return;
        }

        const validateBtn = document.getElementById('validate-btn');
        validateBtn.disabled = true;
        validateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Validating...';

        try {
            const response = await fetch(`${this.validationService}/coordinates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: this.currentCoordinates.latitude,
                    longitude: this.currentCoordinates.longitude
                })
            });

            const result = await response.json();

            if (result.valid) {
                this.showValidationFeedback('Location validated successfully!', 'success');
                this.enableSaveButton();
                
                // Show agricultural context if available
                if (result.geographic_info) {
                    this.showAgriculturalContext(result.geographic_info);
                }
            } else {
                this.showValidationFeedback(
                    `Validation failed: ${result.errors.join(', ')}`, 
                    'error'
                );
            }

        } catch (error) {
            this.showValidationFeedback(
                `Validation error: ${error.message}`, 
                'error'
            );
        } finally {
            validateBtn.disabled = false;
            validateBtn.innerHTML = '<i class="fas fa-check-circle me-2"></i>Validate Location';
        }
    }

    async saveLocation() {
        if (!this.currentCoordinates) {
            this.showValidationFeedback('Please enter and validate coordinates first.', 'error');
            return;
        }

        const saveBtn = document.getElementById('save-btn');
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';

        try {
            const response = await fetch('/api/v1/locations/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: 'Farm Location',
                    coordinates: {
                        latitude: this.currentCoordinates.latitude,
                        longitude: this.currentCoordinates.longitude
                    }
                })
            });

            if (response.ok) {
                this.showValidationFeedback('Location saved successfully!', 'success');
                this.loadSavedLocation();
            } else {
                const error = await response.json();
                this.showValidationFeedback(
                    `Save failed: ${error.detail || 'Unknown error'}`, 
                    'error'
                );
            }

        } catch (error) {
            this.showValidationFeedback(
                `Save error: ${error.message}`, 
                'error'
            );
        } finally {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Location';
        }
    }

    showValidationFeedback(message, type) {
        const feedback = document.getElementById('validation-feedback');
        feedback.textContent = message;
        feedback.className = `validation-feedback validation-${type}`;
        feedback.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            feedback.style.display = 'none';
        }, 5000);
    }

    showAgriculturalContext(geographicInfo) {
        const contextHtml = `
            <div class="mt-3 p-3 bg-light rounded">
                <h6>Agricultural Context</h6>
                <p><strong>Climate Zone:</strong> ${geographicInfo.climate_zone || 'Unknown'}</p>
                <p><strong>USDA Hardiness Zone:</strong> ${geographicInfo.usda_zone || 'Unknown'}</p>
                <p><strong>County:</strong> ${geographicInfo.county || 'Unknown'}</p>
                <p><strong>State:</strong> ${geographicInfo.state || 'Unknown'}</p>
            </div>
        `;
        
        const feedback = document.getElementById('validation-feedback');
        feedback.innerHTML = feedback.innerHTML + contextHtml;
    }

    enableValidationButton() {
        document.getElementById('validate-btn').disabled = false;
    }

    enableSaveButton() {
        document.getElementById('save-btn').disabled = false;
    }

    // Coordinate conversion utilities
    decimalToDMS(decimal, isLatitude) {
        const abs = Math.abs(decimal);
        const degrees = Math.floor(abs);
        const minutes = (abs - degrees) * 60;
        const seconds = (minutes - Math.floor(minutes)) * 60;
        
        return {
            degrees: degrees,
            minutes: Math.floor(minutes),
            seconds: seconds
        };
    }

    dmsToDecimal(dms) {
        return dms.degrees + dms.minutes / 60 + dms.seconds / 3600;
    }

    getDMSFromInputs(isLatitude) {
        const prefix = isLatitude ? 'lat' : 'lon';
        return {
            degrees: parseInt(document.getElementById(`${prefix}-degrees`).value) || 0,
            minutes: parseFloat(document.getElementById(`${prefix}-minutes`).value) || 0,
            seconds: parseFloat(document.getElementById(`${prefix}-seconds`).value) || 0
        };
    }

    decimalToUTM(latitude, longitude) {
        // Simplified UTM conversion (in production, use proper UTM library)
        const zone = Math.floor((longitude + 180) / 6) + 1;
        const easting = (longitude + 180) * 100000;
        const northing = latitude * 100000;
        
        return { zone, easting, northing };
    }

    utmToDecimal(utm) {
        // Simplified UTM to decimal conversion
        const longitude = (utm.easting / 100000) - 180;
        const latitude = utm.northing / 100000;
        
        return { latitude, longitude };
    }

    getUTMFromInputs() {
        return {
            zone: parseInt(document.getElementById('utm-zone').value) || 1,
            easting: parseFloat(document.getElementById('utm-easting').value) || 0,
            northing: parseFloat(document.getElementById('utm-northing').value) || 0
        };
    }

    decimalToMGRS(latitude, longitude) {
        // Simplified MGRS conversion (in production, use proper MGRS library)
        const zone = Math.floor((longitude + 180) / 6) + 1;
        const band = String.fromCharCode(65 + Math.floor((latitude + 80) / 8));
        const easting = Math.floor((longitude + 180) * 1000);
        const northing = Math.floor((latitude + 80) * 1000);
        
        return `${zone}${band} ${easting} ${northing}`;
    }

    mgrsToDecimal(mgrs) {
        // Simplified MGRS to decimal conversion
        const parts = mgrs.split(' ');
        if (parts.length !== 3) {
            throw new Error('Invalid MGRS format');
        }
        
        const zoneBand = parts[0];
        const zone = parseInt(zoneBand.slice(0, -1));
        const easting = parseFloat(parts[1]);
        const northing = parseFloat(parts[2]);
        
        const longitude = (easting / 1000) - 180;
        const latitude = (northing / 1000) - 80;
        
        return { latitude, longitude };
    }

    getCurrentFormat() {
        const format = document.getElementById('coordinate-format').value;
        const formatNames = {
            'decimal': 'Decimal Degrees',
            'dms': 'Degrees Minutes Seconds',
            'utm': 'UTM Coordinates',
            'mgrs': 'MGRS Grid'
        };
        return formatNames[format] || 'Unknown';
    }

    async loadSavedLocation() {
        try {
            const response = await fetch('/api/v1/locations/');
            if (response.ok) {
                const locations = await response.json();
                if (locations.length > 0) {
                    const location = locations[0]; // Use first location
                    this.setCoordinatesFromGPS(
                        location.coordinates.latitude,
                        location.coordinates.longitude
                    );
                }
            }
        } catch (error) {
            console.log('No saved location found');
        }
    }
}

// Global functions for HTML onclick handlers
let gpsInput;

function changeCoordinateFormat() {
    const format = document.getElementById('coordinate-format').value;
    
    // Hide all input sections
    document.getElementById('decimal-inputs').style.display = 'none';
    document.getElementById('dms-inputs').style.display = 'none';
    document.getElementById('utm-inputs').style.display = 'none';
    document.getElementById('mgrs-inputs').style.display = 'none';
    
    // Show selected format
    document.getElementById(`${format}-inputs`).style.display = 'block';
}

function getCurrentLocation() {
    gpsInput.getCurrentLocation();
}

function validateAndUpdateCoordinates() {
    gpsInput.validateAndUpdateCoordinates();
}

function validateLocation() {
    gpsInput.validateLocation();
}

function saveLocation() {
    gpsInput.saveLocation();
}

function centerOnCurrentLocation() {
    gpsInput.getCurrentLocation();
}

function clearMapSelection() {
    gpsInput.map.setView([40.0, -95.0], 4);
    gpsInput.marker.setLatLng([40.0, -95.0]);
    gpsInput.currentCoordinates = null;
    document.getElementById('coordinate-display').style.display = 'none';
    document.getElementById('validate-btn').disabled = true;
    document.getElementById('save-btn').disabled = true;
}

// Address input functions
let addressTimeout;

function handleAddressInput() {
    clearTimeout(addressTimeout);
    addressTimeout = setTimeout(() => {
        const address = document.getElementById('address-input').value;
        if (address.length > 2) {
            searchAddressSuggestions(address);
        } else {
            document.getElementById('address-suggestions').style.display = 'none';
        }
    }, 300);
}

async function searchAddressSuggestions(query) {
    try {
        // Try agricultural address suggestions first
        const agResponse = await fetch(`${gpsInput.geocodingService}/agricultural-address-suggestions?query=${encodeURIComponent(query)}&limit=8&prioritize_agricultural=true`);
        if (agResponse.ok) {
            const agData = await agResponse.json();
            displayAgriculturalAddressSuggestions(agData);
            return;
        }
    } catch (error) {
        console.log('Agricultural address suggestions not available, falling back to regular suggestions');
    }
    
    // Fallback to regular suggestions
    try {
        const response = await fetch(`${gpsInput.geocodingService}/suggestions?query=${encodeURIComponent(query)}`);
        if (response.ok) {
            const suggestions = await response.json();
            displayAddressSuggestions(suggestions);
        }
    } catch (error) {
        console.log('Address suggestions not available');
    }
}

function displayAgriculturalAddressSuggestions(data) {
    const container = document.getElementById('address-suggestions');
    
    if (!data.suggestions || data.suggestions.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.innerHTML = data.suggestions.map(suggestion => {
        const agriculturalType = suggestion.agricultural_type || 'general';
        const typeIcon = getAgriculturalTypeIcon(agriculturalType);
        const typeLabel = getAgriculturalTypeLabel(agriculturalType);
        const confidence = Math.round(suggestion.confidence * 100);
        
        return `
            <a href="#" class="list-group-item list-group-item-action agricultural-suggestion" 
               onclick="selectAgriculturalAddressSuggestion('${suggestion.address}', ${suggestion.latitude}, ${suggestion.longitude})">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <div class="d-flex align-items-center mb-1">
                            <i class="${typeIcon} me-2 text-primary"></i>
                            <span class="fw-bold">${suggestion.address}</span>
                        </div>
                        <div class="small text-muted">
                            ${suggestion.display_name}
                            ${suggestion.county ? ` • ${suggestion.county} County` : ''}
                            ${suggestion.state ? ` • ${suggestion.state}` : ''}
                        </div>
                        ${suggestion.rural_route ? `<div class="small text-info"><i class="fas fa-route me-1"></i>Rural Route: ${suggestion.rural_route}</div>` : ''}
                        ${suggestion.farm_service_agency ? `<div class="small text-success"><i class="fas fa-building me-1"></i>${suggestion.farm_service_agency}</div>` : ''}
                    </div>
                    <div class="text-end">
                        <span class="badge bg-secondary">${typeLabel}</span>
                        <div class="small text-muted">${confidence}%</div>
                    </div>
                </div>
            </a>
        `;
    }).join('');
    
    container.style.display = 'block';
}

function displayAddressSuggestions(suggestions) {
    const container = document.getElementById('address-suggestions');
    
    if (suggestions.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.innerHTML = suggestions.map(suggestion => `
        <a href="#" class="list-group-item list-group-item-action" 
           onclick="selectAddressSuggestion('${suggestion.formatted_address}')">
            ${suggestion.formatted_address}
        </a>
    `).join('');
    
    container.style.display = 'block';
}

function getAgriculturalTypeIcon(type) {
    const icons = {
        'farm': 'fas fa-tractor',
        'rural_route': 'fas fa-route',
        'research_station': 'fas fa-microscope',
        'extension_office': 'fas fa-building',
        'agricultural_facility': 'fas fa-industry',
        'general': 'fas fa-map-marker-alt'
    };
    return icons[type] || icons['general'];
}

function getAgriculturalTypeLabel(type) {
    const labels = {
        'farm': 'Farm',
        'rural_route': 'Rural Route',
        'research_station': 'Research Station',
        'extension_office': 'Extension Office',
        'agricultural_facility': 'Ag Facility',
        'general': 'Location'
    };
    return labels[type] || labels['general'];
}

function selectAgriculturalAddressSuggestion(address, latitude, longitude) {
    document.getElementById('address-input').value = address;
    document.getElementById('address-suggestions').style.display = 'none';
    
    // If we have coordinates, use them directly
    if (latitude && longitude) {
        gpsInput.currentCoordinates = { latitude: latitude, longitude: longitude };
        gpsInput.updateMapDisplay();
        gpsInput.showValidationFeedback('success', 'Agricultural address selected with coordinates');
    } else {
        // Fallback to geocoding
        geocodeAddress();
    }
}

function selectAddressSuggestion(address) {
    document.getElementById('address-input').value = address;
    document.getElementById('address-suggestions').style.display = 'none';
    geocodeAddress();
}

async function geocodeAddress() {
    const address = document.getElementById('address-input').value;
    if (!address.trim()) {
        gpsInput.showValidationFeedback('Please enter an address.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${gpsInput.geocodingService}/geocode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address })
        });
        
        if (response.ok) {
            const result = await response.json();
            gpsInput.setCoordinatesFromGPS(result.latitude, result.longitude);
            gpsInput.showValidationFeedback('Address geocoded successfully!', 'success');
        } else {
            const error = await response.json();
            gpsInput.showValidationFeedback(`Geocoding failed: ${error.detail}`, 'error');
        }
    } catch (error) {
        gpsInput.showValidationFeedback(`Geocoding error: ${error.message}`, 'error');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    gpsInput = new GPSCoordinateInput();
});