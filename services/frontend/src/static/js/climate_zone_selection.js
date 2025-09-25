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
        // Auto-detection form listeners - updated to match HTML structure
        const coordsForm = document.getElementById('coordinateForm');
        const addressForm = document.getElementById('addressForm');
        
        if (coordsForm) {
            coordsForm.addEventListener('submit', (e) => this.handleCoordsSubmit(e));
        }
        
        if (addressForm) {
            addressForm.addEventListener('submit', (e) => this.handleAddressSubmit(e));
        }

        // Manual zone selection
        const selectManualZoneBtn = document.getElementById('selectManualZone');
        if (selectManualZoneBtn) {
            selectManualZoneBtn.addEventListener('click', () => this.handleManualZoneSelection());
        }

        // Zone type selection listeners for manual selection
        const zoneTypeRadios = document.querySelectorAll('input[name="zoneType"]');
        zoneTypeRadios.forEach(radio => {
            radio.addEventListener('change', (e) => this.handleZoneTypeChange(e));
        });

        // Result action buttons
        const confirmZoneBtn = document.getElementById('confirmZoneSelection');
        const showAlternativesBtn = document.getElementById('showAlternatives');
        const proceedBtn = document.getElementById('proceedWithZone');
        const resetBtn = document.getElementById('resetSelection');

        if (confirmZoneBtn) {
            confirmZoneBtn.addEventListener('click', () => this.confirmZoneSelection());
        }
        if (showAlternativesBtn) {
            showAlternativesBtn.addEventListener('click', () => this.showAlternativeZones());
        }
        if (proceedBtn) {
            proceedBtn.addEventListener('click', () => this.proceedToRecommendations());
        }
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSelection());
        }
    }

    async loadInitialData() {
        try {
            // Load available zones
            await this.loadAvailableZones();
            await this.loadUSDAZones();
            await this.loadKoppenTypes();
            
            // Populate dropdowns
            this.populateZoneDropdowns();
            
            // Load any existing overrides
            this.loadOverrideFromStorage();
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

    handleManualZoneSelection() {
        const manualForm = document.getElementById('manualZoneForm');
        if (manualForm) {
            const formData = new FormData(manualForm);
            const zoneType = formData.get('zoneType');
            
            if (!zoneType) {
                this.showAlert('Please select a zone type (USDA or Köppen)', 'warning');
                return;
            }
            
            let selectedZone = null;
            if (zoneType === 'usda') {
                selectedZone = formData.get('usda-zone');
                if (!selectedZone) {
                    this.showAlert('Please select a USDA zone', 'warning');
                    return;
                }
            } else if (zoneType === 'koppen') {
                selectedZone = formData.get('koppen-climate');
                if (!selectedZone) {
                    this.showAlert('Please select a Köppen climate type', 'warning');
                    return;
                }
            }
            
            this.validateAndProcessManualSelection(zoneType, selectedZone);
        }
    }

    async validateAndProcessManualSelection(zoneType, selectedZone) {
        const btn = document.getElementById('selectManualZone');
        this.showLoadingState(btn);

        try {
            const response = await fetch('/api/climate/validate-zone', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: zoneType,
                    zone: selectedZone
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.displayValidationResults(result, zoneType, selectedZone);
            } else {
                const error = await response.json();
                this.showAlert(error.detail || 'Error validating climate zone', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('Network error during validation. Please try again.', 'danger');
        } finally {
            this.hideLoadingState(btn);
        }
    }

    displayValidationResults(result, zoneType, selectedZone) {
        const resultsDiv = document.getElementById('validation-results');
        if (!resultsDiv) return;

        resultsDiv.style.display = 'block';
        
        let html = `
            <div class="alert alert-success">
                <h5><i class="fas fa-check-circle"></i> Climate Zone Validated</h5>
                <p><strong>Selection Method:</strong> Manual Selection</p>
            </div>
        `;

        // Display selected zone information
        html += `
            <div class="card mb-3">
                <div class="card-header">
                    <h6><i class="fas fa-map-marker-alt"></i> Selected Climate Zone</h6>
                </div>
                <div class="card-body">
                    <h4 class="text-primary">${selectedZone}</h4>
                    <p class="mb-1"><strong>Type:</strong> ${zoneType.toUpperCase()}</p>
                    ${result.description ? `<p class="mb-0 text-muted">${result.description}</p>` : ''}
                </div>
            </div>
        `;

        // Display validation feedback
        if (result.validation_status) {
            const statusClass = result.validation_status === 'verified' ? 'success' : 
                               result.validation_status === 'warning' ? 'warning' : 'info';
            html += `
                <div class="alert alert-${statusClass}">
                    <h6><i class="fas fa-info-circle"></i> Validation Status</h6>
                    <p class="mb-0">${result.validation_message || 'Zone selection validated successfully'}</p>
                </div>
            `;
        }

        // Display characteristics
        if (result.characteristics) {
            html += `
                <div class="mt-3">
                    <div class="alert alert-info">
                        <h6><i class="fas fa-thermometer-half"></i> Zone Characteristics</h6>
                        <ul class="mb-0">
                            ${result.characteristics.map(char => `<li>${char}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        // Display alternative suggestions if available
        if (result.alternatives && result.alternatives.length > 0) {
            html += `
                <div class="mt-3">
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-exclamation-triangle"></i> Alternative Suggestions</h6>
                        <p>Based on typical conditions, you might also consider these zones:</p>
                        <ul class="mb-2">
                            ${result.alternatives.map(alt => `<li><strong>${alt.zone}</strong> - ${alt.reason}</li>`).join('')}
                        </ul>
                        <button class="btn btn-sm btn-outline-primary" onclick="climateZoneSelector.showAlternativeZones()">
                            View Alternative Options
                        </button>
                    </div>
                </div>
            `;
        }

        resultsDiv.innerHTML = html;
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    confirmZoneSelection() {
        // Check if there's an active override
        const override = localStorage.getItem('climate_zone_override');
        let confirmedZone;
        
        if (override) {
            try {
                const overrideData = JSON.parse(override);
                confirmedZone = {
                    method: 'override',
                    original_zone: overrideData.original_zone,
                    active_zone: overrideData.override_zone,
                    override_reason: overrideData.reason,
                    timestamp: new Date().toISOString()
                };
            } catch (error) {
                console.error('Error parsing override data:', error);
                confirmedZone = this.getCurrentlySelectedZone();
            }
        } else {
            confirmedZone = this.getCurrentlySelectedZone();
        }
        
        if (!confirmedZone) {
            this.showAlert('No zone selected to confirm', 'warning');
            return;
        }

        localStorage.setItem('confirmed_climate_zone', JSON.stringify(confirmedZone));
        
        if (confirmedZone.method === 'override') {
            this.showAlert('Climate zone override confirmed and saved for recommendations', 'success');
        } else {
            this.showAlert('Climate zone selection confirmed and saved', 'success');
        }
        
        // Show proceed button
        const proceedBtn = document.getElementById('proceedWithZone');
        if (proceedBtn) {
            proceedBtn.style.display = 'inline-block';
        }
    }

    showAlternativeZones() {
        // This would typically fetch alternative zones from the backend
        const alternativesContainer = document.getElementById('alternative-zones');
        if (alternativesContainer) {
            alternativesContainer.style.display = 'block';
            alternativesContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }

    proceedToRecommendations() {
        const confirmedZone = localStorage.getItem('confirmed_climate_zone');
        if (!confirmedZone) {
            this.showAlert('Please confirm your zone selection first', 'warning');
            return;
        }

        // Redirect to recommendations page or trigger next step
        this.showAlert('Proceeding to agricultural recommendations...', 'info');
        // In a real implementation, this would navigate to the next page
        // window.location.href = '/recommendations';
    }

    resetSelection() {
        // Clear all forms and results
        const forms = document.querySelectorAll('form');
        forms.forEach(form => form.reset());
        
        const resultsDivs = document.querySelectorAll('[id$="-results"]');
        resultsDivs.forEach(div => div.style.display = 'none');
        
        // Clear stored data
        localStorage.removeItem('confirmed_climate_zone');
        localStorage.removeItem('climate_zone_override');
        
        // Hide zone type specific groups
        document.getElementById('usda-zone-group').style.display = 'none';
        document.getElementById('koppen-zone-group').style.display = 'none';
        
        // Remove any existing modals
        const modal = document.getElementById('overrideModal');
        if (modal) {
            modal.remove();
        }
        
        this.showAlert('Selection reset successfully', 'info');
    }

    getCurrentlySelectedZone() {
        // Check detection results first
        const detectionResults = document.getElementById('detection-results');
        if (detectionResults && detectionResults.style.display !== 'none') {
            // Extract zone information from detection results
            const usdaZone = detectionResults.querySelector('.text-primary')?.textContent;
            const koppenZone = detectionResults.querySelector('.text-success')?.textContent;
            
            if (usdaZone || koppenZone) {
                return {
                    method: 'detected',
                    usda: usdaZone || null,
                    koppen: koppenZone || null,
                    timestamp: new Date().toISOString()
                };
            }
        }
        
        // Check manual selection results
        const manualResults = document.getElementById('manual-results');
        if (manualResults && manualResults.style.display !== 'none') {
            const selectedZone = manualResults.querySelector('.text-primary')?.textContent;
            const zoneType = manualResults.querySelector('strong')?.nextSibling?.textContent?.trim();
            
            if (selectedZone && zoneType) {
                return {
                    method: 'manual',
                    type: zoneType.toLowerCase(),
                    zone: selectedZone,
                    timestamp: new Date().toISOString()
                };
            }
        }
        
        return null;
    }

    showOverrideDialog() {
        const currentZone = this.getCurrentlySelectedZone();
        if (!currentZone) {
            this.showAlert('Please detect or select a climate zone first before overriding', 'warning');
            return;
        }

        // Create override modal
        const modalHtml = `
            <div class="modal fade" id="overrideModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"><i class="fas fa-edit"></i> Override Climate Zone</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-warning">
                                <i class="fas fa-exclamation-triangle"></i>
                                <strong>Warning:</strong> Overriding your climate zone may affect the accuracy of agricultural recommendations. 
                                Please ensure you have local knowledge or data to support this change.
                            </div>
                            
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <h6>Current Zone</h6>
                                    <div class="card bg-light">
                                        <div class="card-body">
                                            <p class="mb-1"><strong>Zone:</strong> ${this.formatCurrentZone(currentZone)}</p>
                                            <p class="mb-0"><strong>Method:</strong> ${currentZone.method === 'detected' ? 'Auto-Detected' : 'Manual Selection'}</p>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6>Override Zone</h6>
                                    <form id="overrideForm">
                                        <div class="mb-3">
                                            <label class="form-label">Zone Type</label>
                                            <select class="form-select" name="overrideZoneType" id="overrideZoneType" required>
                                                <option value="">Select Zone Type</option>
                                                <option value="usda">USDA Hardiness Zone</option>
                                                <option value="koppen">Köppen Climate Type</option>
                                            </select>
                                        </div>
                                        
                                        <div class="mb-3" id="overrideUsdaGroup" style="display: none;">
                                            <label class="form-label">USDA Zone</label>
                                            <select class="form-select" name="overrideUsdaZone" id="overrideUsdaZone">
                                                <option value="">Select USDA Zone</option>
                                            </select>
                                        </div>
                                        
                                        <div class="mb-3" id="overrideKoppenGroup" style="display: none;">
                                            <label class="form-label">Köppen Climate Type</label>
                                            <select class="form-select" name="overrideKoppenZone" id="overrideKoppenZone">
                                                <option value="">Select Köppen Type</option>
                                            </select>
                                        </div>
                                    </form>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Reason for Override <span class="text-danger">*</span></label>
                                <textarea class="form-control" id="overrideReason" rows="3" placeholder="Please explain why you're overriding the detected zone (e.g., local microclimate, elevation differences, historical weather patterns, etc.)" required></textarea>
                                <div class="form-text">This information helps improve our zone detection accuracy.</div>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="confirmOverride" required>
                                    <label class="form-check-label" for="confirmOverride">
                                        I understand that overriding the climate zone may affect recommendation accuracy
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-warning" id="applyOverride">
                                <i class="fas fa-save"></i> Apply Override
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        const existingModal = document.getElementById('overrideModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Initialize modal functionality
        this.initializeOverrideModal();

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('overrideModal'));
        modal.show();
    }

    initializeOverrideModal() {
        // Populate zone dropdowns
        this.populateOverrideDropdowns();

        // Zone type change handler
        document.getElementById('overrideZoneType').addEventListener('change', (e) => {
            const zoneType = e.target.value;
            const usdaGroup = document.getElementById('overrideUsdaGroup');
            const koppenGroup = document.getElementById('overrideKoppenGroup');

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
        });

        // Apply override handler
        document.getElementById('applyOverride').addEventListener('click', () => {
            this.applyZoneOverride();
        });
    }

    populateOverrideDropdowns() {
        // Populate USDA zones
        const usdaSelect = document.getElementById('overrideUsdaZone');
        if (usdaSelect && this.usdaZones.length > 0) {
            usdaSelect.innerHTML = '<option value="">Select USDA Zone</option>';
            this.usdaZones.forEach(zone => {
                const option = document.createElement('option');
                option.value = zone.zone_id || zone.name;
                option.textContent = `${zone.zone_id || zone.name} - ${zone.description || zone.temp_range}`;
                usdaSelect.appendChild(option);
            });
        }

        // Populate Köppen types
        const koppenSelect = document.getElementById('overrideKoppenZone');
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

    async applyZoneOverride() {
        const form = document.getElementById('overrideForm');
        const formData = new FormData(form);
        const reason = document.getElementById('overrideReason').value.trim();
        const confirmed = document.getElementById('confirmOverride').checked;

        // Validation
        if (!confirmed) {
            this.showAlert('Please confirm that you understand the implications of overriding the climate zone', 'warning');
            return;
        }

        if (!reason || reason.length < 10) {
            this.showAlert('Please provide a detailed reason for the override (at least 10 characters)', 'warning');
            return;
        }

        const zoneType = formData.get('overrideZoneType');
        let overrideZone = null;

        if (zoneType === 'usda') {
            overrideZone = formData.get('overrideUsdaZone');
        } else if (zoneType === 'koppen') {
            overrideZone = formData.get('overrideKoppenZone');
        }

        if (!overrideZone) {
            this.showAlert('Please select an override zone', 'warning');
            return;
        }

        const applyBtn = document.getElementById('applyOverride');
        this.showLoadingState(applyBtn);

        try {
            const currentZone = this.getCurrentlySelectedZone();
            const overrideData = {
                original_zone: currentZone,
                override_zone: {
                    type: zoneType,
                    zone: overrideZone
                },
                reason: reason,
                timestamp: new Date().toISOString()
            };

            // Save override to local storage
            localStorage.setItem('climate_zone_override', JSON.stringify(overrideData));

            // Submit override to backend for logging
            const response = await fetch('/api/climate/zone-override', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(overrideData)
            });

            if (response.ok) {
                const result = await response.json();
                this.displayOverrideResults(overrideData, result);
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('overrideModal'));
                modal.hide();
                
                this.showAlert('Climate zone override applied successfully', 'success');
            } else {
                // Even if backend fails, we can still use the local override
                this.displayOverrideResults(overrideData, { status: 'local_only' });
                
                const modal = bootstrap.Modal.getInstance(document.getElementById('overrideModal'));
                modal.hide();
                
                this.showAlert('Climate zone override applied (saved locally)', 'info');
            }
        } catch (error) {
            console.error('Error applying override:', error);
            // Save locally even if network fails
            const currentZone = this.getCurrentlySelectedZone();
            const overrideData = {
                original_zone: currentZone,
                override_zone: {
                    type: zoneType,
                    zone: overrideZone
                },
                reason: reason,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem('climate_zone_override', JSON.stringify(overrideData));
            this.displayOverrideResults(overrideData, { status: 'local_only' });
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('overrideModal'));
            modal.hide();
            
            this.showAlert('Climate zone override applied (saved locally)', 'info');
        } finally {
            this.hideLoadingState(applyBtn);
        }
    }

    displayOverrideResults(overrideData, result) {
        const resultsDiv = document.getElementById('override-results');
        if (!resultsDiv) {
            // Create results div if it doesn't exist
            const detectionResults = document.getElementById('detection-results');
            const newDiv = document.createElement('div');
            newDiv.id = 'override-results';
            newDiv.className = 'row mb-4';
            detectionResults.parentNode.insertBefore(newDiv, detectionResults.nextSibling);
        }

        const overrideResultsDiv = document.getElementById('override-results');
        overrideResultsDiv.style.display = 'block';

        let html = `
            <div class="col-12">
                <div class="card agricultural-card">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-edit"></i> Climate Zone Override Applied</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle"></i>
                            <strong>Override Active:</strong> You are using a custom climate zone that differs from the detected zone.
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Original Zone</h6>
                                <div class="card bg-light">
                                    <div class="card-body">
                                        <p class="mb-1"><strong>Zone:</strong> ${this.formatCurrentZone(overrideData.original_zone)}</p>
                                        <p class="mb-0"><strong>Method:</strong> ${overrideData.original_zone.method === 'detected' ? 'Auto-Detected' : 'Manual Selection'}</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>Override Zone</h6>
                                <div class="card bg-warning">
                                    <div class="card-body">
                                        <p class="mb-1"><strong>Zone:</strong> ${overrideData.override_zone.zone}</p>
                                        <p class="mb-0"><strong>Type:</strong> ${overrideData.override_zone.type.toUpperCase()}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <h6>Override Reason</h6>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <p class="mb-0">${overrideData.reason}</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3 d-flex gap-2 flex-wrap">
                            <button class="btn btn-primary" onclick="climateZoneSelector.confirmZoneSelection()">
                                <i class="fas fa-check"></i> Confirm Override
                            </button>
                            <button class="btn btn-outline-secondary" onclick="climateZoneSelector.clearOverride()">
                                <i class="fas fa-undo"></i> Remove Override
                            </button>
                            <button class="btn btn-outline-danger" onclick="climateZoneSelector.resetSelection()">
                                <i class="fas fa-redo"></i> Start Over
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        overrideResultsDiv.innerHTML = html;
        overrideResultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    clearOverride() {
        localStorage.removeItem('climate_zone_override');
        const overrideResults = document.getElementById('override-results');
        if (overrideResults) {
            overrideResults.style.display = 'none';
        }
        this.showAlert('Climate zone override cleared', 'info');
    }

    formatCurrentZone(zoneData) {
        if (!zoneData) return 'Unknown';
        
        if (zoneData.method === 'detected') {
            const zones = [];
            if (zoneData.usda) zones.push(`USDA ${zoneData.usda}`);
            if (zoneData.koppen) zones.push(`Köppen ${zoneData.koppen}`);
            return zones.join(', ') || 'Unknown';
        } else if (zoneData.method === 'manual') {
            return `${zoneData.type?.toUpperCase()} ${zoneData.zone}`;
        }
        
        return 'Unknown';
    }

    loadOverrideFromStorage() {
        const override = localStorage.getItem('climate_zone_override');
        if (override) {
            try {
                const overrideData = JSON.parse(override);
                this.displayOverrideResults(overrideData, { status: 'loaded_from_storage' });
                this.showAlert('Previously saved climate zone override loaded', 'info');
            } catch (error) {
                console.error('Error loading override from storage:', error);
                localStorage.removeItem('climate_zone_override');
            }
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

        // Add validation confidence and feedback
        if (result.confidence_level) {
            const confidenceClass = result.confidence_level >= 0.8 ? 'success' : 
                                   result.confidence_level >= 0.6 ? 'warning' : 'danger';
            html += `
                <div class="mt-3">
                    <div class="alert alert-${confidenceClass}">
                        <h6><i class="fas fa-chart-line"></i> Detection Confidence</h6>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-${confidenceClass}" style="width: ${(result.confidence_level * 100).toFixed(1)}%"></div>
                        </div>
                        <p class="mb-0">Confidence Level: ${(result.confidence_level * 100).toFixed(1)}%</p>
                        ${result.confidence_level < 0.7 ? '<small class="text-muted">Consider manual verification or alternative detection methods.</small>' : ''}
                    </div>
                </div>
            `;
        }

        // Add action buttons for user feedback and confirmation
        html += `
            <div class="mt-3 d-flex gap-2 flex-wrap">
                <button class="btn btn-primary" id="confirmZoneSelection" onclick="climateZoneSelector.confirmZoneSelection()">
                    <i class="fas fa-check"></i> Confirm This Zone
                </button>
                <button class="btn btn-outline-warning" id="overrideZone" onclick="climateZoneSelector.showOverrideDialog()">
                    <i class="fas fa-edit"></i> Override Zone
                </button>
                <button class="btn btn-outline-secondary" id="showAlternatives" onclick="climateZoneSelector.showAlternativeZones()">
                    <i class="fas fa-search"></i> Show Alternatives
                </button>
                <button class="btn btn-outline-danger" id="resetSelection" onclick="climateZoneSelector.resetSelection()">
                    <i class="fas fa-redo"></i> Start Over
                </button>
            </div>
        `;

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

        // Add action buttons for manual selection results
        html += `
            <div class="mt-3 d-flex gap-2 flex-wrap">
                <button class="btn btn-primary" id="confirmZoneSelection" onclick="climateZoneSelector.confirmZoneSelection()">
                    <i class="fas fa-check"></i> Confirm This Zone
                </button>
                <button class="btn btn-outline-warning" id="overrideZone" onclick="climateZoneSelector.showOverrideDialog()">
                    <i class="fas fa-edit"></i> Override Zone
                </button>
                <button class="btn btn-outline-secondary" id="showAlternatives" onclick="climateZoneSelector.showAlternativeZones()">
                    <i class="fas fa-search"></i> Show Alternatives
                </button>
                <button class="btn btn-outline-danger" id="resetSelection" onclick="climateZoneSelector.resetSelection()">
                    <i class="fas fa-redo"></i> Start Over
                </button>
            </div>
        `;

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

    static validateZoneCompatibility(primaryZone, secondaryZone) {
        // Check if two zones are compatible for cross-reference validation
        if (!primaryZone || !secondaryZone) return { compatible: false, message: 'Missing zone data' };
        
        // Extract numeric values for comparison
        const primaryNum = parseInt(primaryZone.replace(/[^0-9]/g, ''));
        const secondaryNum = parseInt(secondaryZone.replace(/[^0-9]/g, ''));
        
        const difference = Math.abs(primaryNum - secondaryNum);
        
        if (difference <= 1) {
            return { compatible: true, message: 'Zones are highly compatible' };
        } else if (difference <= 2) {
            return { compatible: true, message: 'Zones are moderately compatible with some variation expected' };
        } else {
            return { compatible: false, message: 'Significant zone difference detected - consider validation' };
        }
    }

    static generateAlternativeSuggestions(currentZone, zoneType) {
        const alternatives = [];
        
        if (zoneType === 'usda') {
            const zoneNum = parseInt(currentZone);
            const isSubZone = currentZone.includes('a') || currentZone.includes('b');
            
            // Suggest adjacent zones
            if (zoneNum > 1) {
                alternatives.push({
                    zone: `${zoneNum - 1}${isSubZone ? 'b' : ''}`,
                    reason: 'Cooler adjacent zone for areas with microclimatic variation'
                });
            }
            if (zoneNum < 11) {
                alternatives.push({
                    zone: `${zoneNum + 1}${isSubZone ? 'a' : ''}`,
                    reason: 'Warmer adjacent zone for protected or urban heat island areas'
                });
            }
            
            // Suggest sub-zone alternatives
            if (isSubZone) {
                const baseZone = currentZone.replace(/[ab]$/, '');
                const currentSub = currentZone.slice(-1);
                const altSub = currentSub === 'a' ? 'b' : 'a';
                alternatives.push({
                    zone: `${baseZone}${altSub}`,
                    reason: `Alternative sub-zone within Zone ${baseZone}`
                });
            }
        }
        
        return alternatives;
    }

    static calculateConfidenceScore(detectionData) {
        let confidence = 0.5; // Base confidence
        
        // Increase confidence based on data quality
        if (detectionData.gps_accuracy && detectionData.gps_accuracy < 10) confidence += 0.2;
        if (detectionData.multiple_sources) confidence += 0.15;
        if (detectionData.recent_weather_data) confidence += 0.1;
        if (detectionData.elevation_data) confidence += 0.05;
        
        // Cap at 1.0
        return Math.min(confidence, 1.0);
    }

    static formatValidationMessage(validationResult) {
        if (!validationResult) return 'No validation data available';
        
        const messages = [];
        
        if (validationResult.accuracy_high) {
            messages.push('✓ High accuracy detection based on precise location data');
        }
        if (validationResult.cross_validated) {
            messages.push('✓ Cross-validated with multiple climate databases');
        }
        if (validationResult.seasonal_consistency) {
            messages.push('✓ Consistent with historical seasonal patterns');
        }
        if (validationResult.warnings && validationResult.warnings.length > 0) {
            messages.push(`⚠ ${validationResult.warnings.join(', ')}`);
        }
        
        return messages.length > 0 ? messages.join('<br>') : 'Standard validation applied';
    }
}

// Initialize the climate zone selector when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.climateZoneSelector = new ClimateZoneSelector();
    window.ClimateZoneUtils = ClimateZoneUtils;
});

// Export for use in other scripts
window.ClimateZoneSelector = ClimateZoneSelector;