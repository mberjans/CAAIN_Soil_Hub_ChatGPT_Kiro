/**
 * Field Management JavaScript
 * Autonomous Farm Advisory System - Field Management Interface
 * Version: 1.0
 * Date: December 2024
 */

class FieldManagementSystem {
    constructor() {
        this.map = null;
        this.drawnItems = null;
        this.fields = [];
        this.selectedFields = [];
        this.fieldTemplates = {
            corn_field: {
                field_type: 'cropland',
                soil_type: 'loam',
                drainage_class: 'well_drained',
                slope_percent: 2.0,
                organic_matter: 3.5,
                irrigation_available: false,
                tile_drainage: true,
                good_accessibility: true,
                notes: 'Standard corn field configuration'
            },
            soybean_field: {
                field_type: 'cropland',
                soil_type: 'clay_loam',
                drainage_class: 'moderately_well_drained',
                slope_percent: 1.5,
                organic_matter: 4.0,
                irrigation_available: false,
                tile_drainage: true,
                good_accessibility: true,
                notes: 'Soybean field configuration'
            },
            mixed_crop: {
                field_type: 'cropland',
                soil_type: 'loam',
                drainage_class: 'well_drained',
                slope_percent: 2.5,
                organic_matter: 3.8,
                irrigation_available: true,
                tile_drainage: true,
                good_accessibility: true,
                notes: 'Multi-crop rotation field'
            }
        };
        
        this.init();
    }

    async init() {
        console.log('Initializing Field Management System...');
        
        // Initialize map
        this.initializeMap();
        
        // Load existing fields
        await this.loadFields();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Update statistics
        this.updateStatistics();
        
        console.log('Field Management System initialized successfully');
    }

    initializeMap() {
        // Initialize Leaflet map
        this.map = L.map('field-map').setView([40.0, -95.0], 6);
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // Initialize drawn items layer
        this.drawnItems = new L.FeatureGroup();
        this.map.addLayer(this.drawnItems);
        
        // Add draw control
        const drawControl = new L.Control.Draw({
            edit: {
                featureGroup: this.drawnItems
            },
            draw: {
                polygon: true,
                rectangle: true,
                circle: false,
                marker: true,
                polyline: false
            }
        });
        this.map.addControl(drawControl);
        
        // Handle draw events
        this.map.on(L.Draw.Event.CREATED, (event) => {
            this.handleDrawCreated(event);
        });
        
        this.map.on(L.Draw.Event.EDITED, (event) => {
            this.handleDrawEdited(event);
        });
        
        this.map.on(L.Draw.Event.DELETED, (event) => {
            this.handleDrawDeleted(event);
        });
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('field-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterFields(e.target.value);
            });
        }
        
        // Filter dropdowns
        const typeFilter = document.getElementById('field-type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', () => {
                this.applyFilters();
            });
        }
        
        const soilFilter = document.getElementById('soil-type-filter');
        if (soilFilter) {
            soilFilter.addEventListener('change', () => {
                this.applyFilters();
            });
        }
        
        // Form validation
        const fieldForm = document.getElementById('field-form');
        if (fieldForm) {
            fieldForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.validateFieldForm();
            });
        }
    }

    async loadFields() {
        try {
            console.log('Loading fields from API...');
            
            // Call the field management API endpoint
            const response = await fetch('http://localhost:8000/api/v1/fields/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.getAuthToken()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.fields = data.fields || [];
                this.renderFieldList();
                this.renderFieldMap();
            } else {
                console.warn('Failed to load fields, using mock data');
                this.loadMockFields();
            }
        } catch (error) {
            console.error('Error loading fields:', error);
            this.loadMockFields();
        }
    }

    loadMockFields() {
        // Mock data for development/testing
        this.fields = [
            {
                id: '1',
                field_name: 'North Field',
                field_number: 'NF-001',
                field_type: 'cropland',
                size_acres: 80.5,
                soil_type: 'loam',
                drainage_class: 'well_drained',
                slope_percent: 2.0,
                organic_matter: 3.5,
                irrigation_available: false,
                tile_drainage: true,
                good_accessibility: true,
                notes: 'Primary corn field',
                boundary: {
                    type: 'Polygon',
                    coordinates: [[[-95.0, 40.0], [-94.9, 40.0], [-94.9, 40.1], [-95.0, 40.1], [-95.0, 40.0]]]
                },
                created_at: '2024-01-15T10:00:00Z'
            },
            {
                id: '2',
                field_name: 'South Field',
                field_number: 'SF-002',
                field_type: 'cropland',
                size_acres: 65.2,
                soil_type: 'clay_loam',
                drainage_class: 'moderately_well_drained',
                slope_percent: 1.5,
                organic_matter: 4.0,
                irrigation_available: true,
                tile_drainage: true,
                good_accessibility: true,
                notes: 'Soybean rotation field',
                boundary: {
                    type: 'Polygon',
                    coordinates: [[[-95.0, 39.9], [-94.9, 39.9], [-94.9, 40.0], [-95.0, 40.0], [-95.0, 39.9]]]
                },
                created_at: '2024-01-20T14:30:00Z'
            },
            {
                id: '3',
                field_name: 'East Pasture',
                field_number: 'EP-003',
                field_type: 'pasture',
                size_acres: 45.8,
                soil_type: 'sandy_loam',
                drainage_class: 'well_drained',
                slope_percent: 3.0,
                organic_matter: 2.8,
                irrigation_available: false,
                tile_drainage: false,
                good_accessibility: true,
                notes: 'Livestock pasture area',
                boundary: {
                    type: 'Polygon',
                    coordinates: [[[-94.9, 40.0], [-94.8, 40.0], [-94.8, 40.1], [-94.9, 40.1], [-94.9, 40.0]]]
                },
                created_at: '2024-02-01T09:15:00Z'
            }
        ];
        
        this.renderFieldList();
        this.renderFieldMap();
    }

    renderFieldList() {
        const fieldListContainer = document.getElementById('field-list');
        if (!fieldListContainer) return;
        
        if (this.fields.length === 0) {
            fieldListContainer.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-map-marked-alt fa-3x mb-3"></i>
                    <p>No fields found. Create your first field to get started.</p>
                </div>
            `;
            return;
        }
        
        const fieldListHTML = this.fields.map(field => this.createFieldListItem(field)).join('');
        fieldListContainer.innerHTML = fieldListHTML;
    }

    createFieldListItem(field) {
        const soilTypeDisplay = this.getSoilTypeDisplay(field.soil_type);
        const fieldTypeDisplay = this.getFieldTypeDisplay(field.field_type);
        const drainageDisplay = this.getDrainageDisplay(field.drainage_class);
        
        return `
            <div class="field-list-item" data-field-id="${field.id}" onclick="fieldManager.selectField('${field.id}')">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="field-name">${field.field_name}</h6>
                        <div class="field-details">
                            <div class="row">
                                <div class="col-6">
                                    <small><strong>Type:</strong> ${fieldTypeDisplay}</small><br>
                                    <small><strong>Size:</strong> ${field.size_acres} acres</small>
                                </div>
                                <div class="col-6">
                                    <small><strong>Soil:</strong> ${soilTypeDisplay}</small><br>
                                    <small><strong>Drainage:</strong> ${drainageDisplay}</small>
                                </div>
                            </div>
                            ${field.notes ? `<small class="text-muted mt-2 d-block"><em>${field.notes}</em></small>` : ''}
                        </div>
                    </div>
                    <div class="field-actions">
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); fieldManager.editField('${field.id}')" title="Edit Field">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); fieldManager.deleteField('${field.id}')" title="Delete Field">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderFieldMap() {
        if (!this.map) return;
        
        // Clear existing field markers
        this.map.eachLayer(layer => {
            if (layer instanceof L.Marker || layer instanceof L.Polygon) {
                if (layer.fieldId) {
                    this.map.removeLayer(layer);
                }
            }
        });
        
        // Add field boundaries and markers
        this.fields.forEach(field => {
            if (field.boundary && field.boundary.coordinates) {
                this.addFieldToMap(field);
            }
        });
    }

    addFieldToMap(field) {
        if (!field.boundary || !field.boundary.coordinates) return;
        
        try {
            const coordinates = field.boundary.coordinates[0];
            const latLngs = coordinates.map(coord => [coord[1], coord[0]]); // Convert [lng, lat] to [lat, lng]
            
            const polygon = L.polygon(latLngs, {
                color: this.getFieldColor(field.field_type),
                fillColor: this.getFieldColor(field.field_type),
                fillOpacity: 0.3,
                weight: 2
            });
            
            polygon.fieldId = field.id;
            polygon.addTo(this.map);
            
            // Add popup
            polygon.bindPopup(this.createFieldPopup(field));
            
            // Add click handler
            polygon.on('click', () => {
                this.selectField(field.id);
            });
            
            // Add center marker
            const center = polygon.getBounds().getCenter();
            const marker = L.marker(center, {
                icon: this.createFieldIcon(field.field_type)
            });
            
            marker.fieldId = field.id;
            marker.addTo(this.map);
            marker.bindPopup(this.createFieldPopup(field));
            
            marker.on('click', () => {
                this.selectField(field.id);
            });
            
        } catch (error) {
            console.error('Error adding field to map:', error);
        }
    }

    createFieldPopup(field) {
        const soilTypeDisplay = this.getSoilTypeDisplay(field.soil_type);
        const fieldTypeDisplay = this.getFieldTypeDisplay(field.field_type);
        
        return `
            <div class="field-popup">
                <h6 class="mb-2">${field.field_name}</h6>
                <div class="field-popup-details">
                    <small><strong>Type:</strong> ${fieldTypeDisplay}</small><br>
                    <small><strong>Size:</strong> ${field.size_acres} acres</small><br>
                    <small><strong>Soil:</strong> ${soilTypeDisplay}</small><br>
                    <small><strong>Number:</strong> ${field.field_number || 'N/A'}</small>
                </div>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="fieldManager.editField('${field.id}')">
                        <i class="fas fa-edit me-1"></i>Edit
                    </button>
                </div>
            </div>
        `;
    }

    createFieldIcon(fieldType) {
        const colors = {
            cropland: '#28a745',
            pasture: '#ffc107',
            orchard: '#fd7e14',
            vineyard: '#6f42c1',
            greenhouse: '#20c997'
        };
        
        return L.divIcon({
            className: 'field-marker',
            html: `<div style="background-color: ${colors[fieldType] || '#6c757d'}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });
    }

    getFieldColor(fieldType) {
        const colors = {
            cropland: '#28a745',
            pasture: '#ffc107',
            orchard: '#fd7e14',
            vineyard: '#6f42c1',
            greenhouse: '#20c997'
        };
        return colors[fieldType] || '#6c757d';
    }

    selectField(fieldId) {
        // Remove previous selection
        document.querySelectorAll('.field-list-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Add selection to clicked field
        const fieldItem = document.querySelector(`[data-field-id="${fieldId}"]`);
        if (fieldItem) {
            fieldItem.classList.add('selected');
        }
        
        // Show field details
        this.showFieldDetails(fieldId);
        
        // Center map on field
        const field = this.fields.find(f => f.id === fieldId);
        if (field && field.boundary) {
            this.centerMapOnField(field);
        }
    }

    showFieldDetails(fieldId) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;
        
        const detailsPanel = document.getElementById('field-details-panel');
        const detailsContent = document.getElementById('field-details-content');
        
        if (!detailsPanel || !detailsContent) return;
        
        const soilTypeDisplay = this.getSoilTypeDisplay(field.soil_type);
        const fieldTypeDisplay = this.getFieldTypeDisplay(field.field_type);
        const drainageDisplay = this.getDrainageDisplay(field.drainage_class);
        
        detailsContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h5 class="mb-3">${field.field_name}</h5>
                    <div class="field-detail-item">
                        <strong>Field Number:</strong> ${field.field_number || 'N/A'}<br>
                        <strong>Type:</strong> ${fieldTypeDisplay}<br>
                        <strong>Size:</strong> ${field.size_acres} acres<br>
                        <strong>Soil Type:</strong> ${soilTypeDisplay}<br>
                        <strong>Drainage:</strong> ${drainageDisplay}<br>
                        <strong>Slope:</strong> ${field.slope_percent || 'N/A'}%<br>
                        <strong>Organic Matter:</strong> ${field.organic_matter || 'N/A'}%
                    </div>
                </div>
                <div class="col-md-6">
                    <h6 class="mb-3">Characteristics</h6>
                    <div class="field-characteristics">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" ${field.irrigation_available ? 'checked' : ''} disabled>
                            <label class="form-check-label">Irrigation Available</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" ${field.tile_drainage ? 'checked' : ''} disabled>
                            <label class="form-check-label">Tile Drainage</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" ${field.good_accessibility ? 'checked' : ''} disabled>
                            <label class="form-check-label">Good Accessibility</label>
                        </div>
                    </div>
                    ${field.notes ? `<div class="mt-3"><strong>Notes:</strong><br><small class="text-muted">${field.notes}</small></div>` : ''}
                </div>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary me-2" onclick="fieldManager.editField('${field.id}')">
                    <i class="fas fa-edit me-1"></i>Edit Field
                </button>
                <button class="btn btn-outline-secondary" onclick="fieldManager.analyzeField('${field.id}')">
                    <i class="fas fa-chart-line me-1"></i>Analyze Field
                </button>
                <button class="btn btn-outline-success" onclick="fieldManager.optimizeField('${field.id}')">
                    <i class="fas fa-tools me-1"></i>Optimize Field
                </button>
            </div>
        `;
        
        detailsPanel.style.display = 'block';
    }

    centerMapOnField(field) {
        if (!field.boundary || !field.boundary.coordinates) return;
        
        try {
            const coordinates = field.boundary.coordinates[0];
            const latLngs = coordinates.map(coord => [coord[1], coord[0]]);
            const bounds = L.latLngBounds(latLngs);
            this.map.fitBounds(bounds, { padding: [20, 20] });
        } catch (error) {
            console.error('Error centering map on field:', error);
        }
    }

    filterFields(searchTerm) {
        const fieldItems = document.querySelectorAll('.field-list-item');
        
        fieldItems.forEach(item => {
            const fieldName = item.querySelector('.field-name').textContent.toLowerCase();
            const fieldDetails = item.querySelector('.field-details').textContent.toLowerCase();
            const searchLower = searchTerm.toLowerCase();
            
            if (fieldName.includes(searchLower) || fieldDetails.includes(searchLower)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    applyFilters() {
        const typeFilter = document.getElementById('field-type-filter').value;
        const soilFilter = document.getElementById('soil-type-filter').value;
        
        const fieldItems = document.querySelectorAll('.field-list-item');
        
        fieldItems.forEach(item => {
            const fieldId = item.dataset.fieldId;
            const field = this.fields.find(f => f.id === fieldId);
            
            if (!field) return;
            
            let show = true;
            
            if (typeFilter && field.field_type !== typeFilter) {
                show = false;
            }
            
            if (soilFilter && field.soil_type !== soilFilter) {
                show = false;
            }
            
            item.style.display = show ? 'block' : 'none';
        });
    }

    updateStatistics() {
        const totalFields = this.fields.length;
        const totalAcres = this.fields.reduce((sum, field) => sum + (field.size_acres || 0), 0);
        const avgFieldSize = totalFields > 0 ? (totalAcres / totalFields).toFixed(1) : 0;
        const activeFields = this.fields.filter(field => field.field_type === 'cropland').length;
        
        document.getElementById('total-fields').textContent = totalFields;
        document.getElementById('total-acres').textContent = totalAcres.toFixed(1);
        document.getElementById('avg-field-size').textContent = avgFieldSize;
        document.getElementById('active-fields').textContent = activeFields;
    }

    // Form handling methods
    openFieldForm() {
        const modal = new bootstrap.Modal(document.getElementById('fieldFormModal'));
        modal.show();
    }

    validateFieldForm() {
        const form = document.getElementById('field-form');
        const formData = new FormData(form);
        
        const fieldData = {
            field_name: document.getElementById('field-name').value,
            field_number: document.getElementById('field-number').value,
            field_type: document.getElementById('field-type').value,
            size_acres: parseFloat(document.getElementById('size-acres').value),
            soil_type: document.getElementById('soil-type').value,
            drainage_class: document.getElementById('drainage-class').value,
            slope_percent: parseFloat(document.getElementById('slope-percent').value) || null,
            organic_matter: parseFloat(document.getElementById('organic-matter').value) || null,
            irrigation_available: document.getElementById('irrigation-available').checked,
            tile_drainage: document.getElementById('tile-drainage').checked,
            good_accessibility: document.getElementById('good-accessibility').checked,
            notes: document.getElementById('field-notes').value,
            boundary: this.getBoundaryFromForm()
        };
        
        // Validate required fields
        if (!fieldData.field_name || !fieldData.field_type || !fieldData.size_acres) {
            this.showAlert('Please fill in all required fields.', 'error');
            return;
        }
        
        // Validate size
        if (fieldData.size_acres <= 0) {
            this.showAlert('Field size must be greater than 0.', 'error');
            return;
        }
        
        this.saveField(fieldData);
    }

    getBoundaryFromForm() {
        const boundaryText = document.getElementById('boundary-coordinates').value;
        if (!boundaryText.trim()) return null;
        
        try {
            return JSON.parse(boundaryText);
        } catch (error) {
            console.error('Invalid boundary JSON:', error);
            return null;
        }
    }

    async saveField(fieldData) {
        try {
            console.log('Saving field:', fieldData);
            
            // Show loading state
            this.showLoading(true);
            
            // Transform field data to match API schema
            const apiData = {
                location_id: "00000000-0000-0000-0000-000000000000", // Default location ID
                field_name: fieldData.field_name,
                field_number: fieldData.field_number || null,
                field_type: fieldData.field_type,
                size_acres: fieldData.size_acres,
                boundary: fieldData.boundary,
                characteristics: {
                    soil_type: fieldData.soil_type || null,
                    drainage_class: fieldData.drainage_class || null,
                    slope_percent: fieldData.slope_percent || null,
                    organic_matter_percent: fieldData.organic_matter || null,
                    irrigation_available: fieldData.irrigation_available || false,
                    tile_drainage: fieldData.tile_drainage || false,
                    accessibility: fieldData.good_accessibility ? "good" : "moderate"
                },
                notes: fieldData.notes || null
            };
            
            // Call the field management API endpoint
            const response = await fetch('http://localhost:8000/api/v1/fields/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.getAuthToken()
                },
                body: JSON.stringify(apiData)
            });
            
            if (response.ok) {
                const newField = await response.json();
                this.fields.push(newField);
                this.renderFieldList();
                this.renderFieldMap();
                this.updateStatistics();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('fieldFormModal'));
                modal.hide();
                
                // Reset form
                document.getElementById('field-form').reset();
                
                this.showAlert('Field saved successfully!', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save field');
            }
        } catch (error) {
            console.error('Error saving field:', error);
            this.showAlert('Failed to save field. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // Draw handling methods
    handleDrawCreated(event) {
        const layer = event.layer;
        const type = event.layerType;
        
        if (type === 'polygon') {
            const coordinates = this.extractCoordinatesFromPolygon(layer);
            document.getElementById('boundary-coordinates').value = JSON.stringify({
                type: 'Polygon',
                coordinates: [coordinates]
            });
            
            this.calculateAreaFromBoundary();
        }
    }

    handleDrawEdited(event) {
        // Handle edit events if needed
        console.log('Field boundary edited');
    }

    handleDrawDeleted(event) {
        // Handle delete events if needed
        console.log('Field boundary deleted');
    }

    extractCoordinatesFromPolygon(polygon) {
        const latLngs = polygon.getLatLngs()[0];
        return latLngs.map(latLng => [latLng.lng, latLng.lat]);
    }

    drawFieldBoundary() {
        // Enable drawing mode
        if (this.map && this.map.drawControl) {
            this.map.drawControl.setDrawingOptions({
                polygon: true
            });
        }
    }

    calculateAreaFromBoundary() {
        const boundaryText = document.getElementById('boundary-coordinates').value;
        if (!boundaryText.trim()) return;
        
        try {
            const boundary = JSON.parse(boundaryText);
            if (boundary.type === 'Polygon' && boundary.coordinates[0]) {
                const area = this.calculatePolygonArea(boundary.coordinates[0]);
                document.getElementById('size-acres').value = area.toFixed(2);
            }
        } catch (error) {
            console.error('Error calculating area:', error);
        }
    }

    calculatePolygonArea(coordinates) {
        // Simple area calculation - in production, use a proper geospatial library
        if (coordinates.length < 3) return 0;
        
        let area = 0;
        for (let i = 0; i < coordinates.length - 1; i++) {
            const [lng1, lat1] = coordinates[i];
            const [lng2, lat2] = coordinates[i + 1];
            area += (lng2 - lng1) * (lat2 + lat1);
        }
        
        // Convert to acres (rough approximation)
        return Math.abs(area) * 0.000247105; // Square degrees to acres
    }

    // Template methods
    applyFieldTemplate(templateName) {
        const template = this.fieldTemplates[templateName];
        if (!template) return;
        
        // Fill form with template data
        Object.keys(template).forEach(key => {
            const element = document.getElementById(key.replace('_', '-'));
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = template[key];
                } else {
                    element.value = template[key];
                }
            }
        });
        
        this.showAlert(`Applied ${templateName.replace('_', ' ')} template`, 'success');
    }

    // Utility methods
    getSoilTypeDisplay(soilType) {
        const displays = {
            clay: 'Clay',
            clay_loam: 'Clay Loam',
            loam: 'Loam',
            sandy_loam: 'Sandy Loam',
            sand: 'Sand',
            silt_loam: 'Silt Loam'
        };
        return displays[soilType] || soilType;
    }

    getFieldTypeDisplay(fieldType) {
        const displays = {
            cropland: 'Cropland',
            pasture: 'Pasture',
            orchard: 'Orchard',
            vineyard: 'Vineyard',
            greenhouse: 'Greenhouse'
        };
        return displays[fieldType] || fieldType;
    }

    getDrainageDisplay(drainageClass) {
        const displays = {
            well_drained: 'Well Drained',
            moderately_well_drained: 'Moderately Well Drained',
            somewhat_poorly_drained: 'Somewhat Poorly Drained',
            poorly_drained: 'Poorly Drained'
        };
        return displays[drainageClass] || drainageClass;
    }

    getAuthToken() {
        // Get authentication token from localStorage or cookies
        return localStorage.getItem('auth_token') || '';
    }

    showAlert(message, type = 'info') {
        // Create and show alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }

    showLoading(show) {
        const buttons = document.querySelectorAll('button[onclick="saveField()"]');
        buttons.forEach(button => {
            if (show) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';
            } else {
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-save me-2"></i>Save Field';
            }
        });
    }

    // Action methods
    editField(fieldId) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;
        
        // Populate form with field data
        document.getElementById('field-name').value = field.field_name;
        document.getElementById('field-number').value = field.field_number || '';
        document.getElementById('field-type').value = field.field_type;
        document.getElementById('size-acres').value = field.size_acres;
        document.getElementById('soil-type').value = field.soil_type || '';
        document.getElementById('drainage-class').value = field.drainage_class || '';
        document.getElementById('slope-percent').value = field.slope_percent || '';
        document.getElementById('organic-matter').value = field.organic_matter || '';
        document.getElementById('irrigation-available').checked = field.irrigation_available || false;
        document.getElementById('tile-drainage').checked = field.tile_drainage || false;
        document.getElementById('good-accessibility').checked = field.good_accessibility || false;
        document.getElementById('field-notes').value = field.notes || '';
        
        if (field.boundary) {
            document.getElementById('boundary-coordinates').value = JSON.stringify(field.boundary);
        }
        
        // Open modal
        this.openFieldForm();
    }

    async deleteField(fieldId) {
        if (!confirm('Are you sure you want to delete this field? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`http://localhost:8000/api/v1/fields/${fieldId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': 'Bearer ' + this.getAuthToken()
                }
            });
            
            if (response.ok) {
                this.fields = this.fields.filter(f => f.id !== fieldId);
                this.renderFieldList();
                this.renderFieldMap();
                this.updateStatistics();
                this.showAlert('Field deleted successfully!', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to delete field');
            }
        } catch (error) {
            console.error('Error deleting field:', error);
            this.showAlert('Failed to delete field. Please try again.', 'error');
        }
    }

    async analyzeField(fieldId) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;
        
        try {
            // Show loading state
            this.showLoading(true);
            
            // Prepare analysis request
            const analysisRequest = {
                field_id: field.id,
                field_name: field.field_name,
                coordinates: {
                    latitude: this.getFieldCenterLat(field),
                    longitude: this.getFieldCenterLng(field)
                },
                boundary: field.boundary,
                area_acres: field.size_acres,
                soil_type: field.soil_type,
                drainage_class: field.drainage_class,
                slope_percent: field.slope_percent,
                organic_matter_percent: field.organic_matter,
                irrigation_available: field.irrigation_available,
                tile_drainage: field.tile_drainage,
                accessibility: field.good_accessibility ? 'good' : 'fair'
            };
            
            // Call productivity analysis API
            const response = await fetch(`http://localhost:8000/api/v1/fields/${fieldId}/productivity-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.getAuthToken()
                },
                body: JSON.stringify(analysisRequest)
            });
            
            if (response.ok) {
                const analysisResult = await response.json();
                this.showFieldAnalysisResults(fieldId, analysisResult);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }
        } catch (error) {
            console.error('Error analyzing field:', error);
            this.showAlert('Failed to analyze field. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    importFields() {
        this.showAlert('Import functionality coming soon!', 'info');
    }

    exportFields() {
        this.showAlert('Export functionality coming soon!', 'info');
    }

    bulkEditFields() {
        this.showAlert('Bulk edit functionality coming soon!', 'info');
    }

    // Field analysis helper methods
    getFieldCenterLat(field) {
        if (field.boundary && field.boundary.coordinates) {
            const coords = field.boundary.coordinates[0];
            const lats = coords.map(coord => coord[1]);
            return (Math.min(...lats) + Math.max(...lats)) / 2;
        }
        return 40.0; // Default latitude
    }

    getFieldCenterLng(field) {
        if (field.boundary && field.boundary.coordinates) {
            const coords = field.boundary.coordinates[0];
            const lngs = coords.map(coord => coord[0]);
            return (Math.min(...lngs) + Math.max(...lngs)) / 2;
        }
        return -95.0; // Default longitude
    }

    showFieldAnalysisResults(fieldId, analysisResult) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;

        // Create analysis results modal
        const modalHtml = `
            <div class="modal fade" id="fieldAnalysisModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-chart-line me-2"></i>
                                Field Productivity Analysis - ${field.field_name}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${this.createAnalysisResultsContent(analysisResult)}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-primary" onclick="fieldManager.exportAnalysisResults('${fieldId}')">
                                <i class="fas fa-download me-2"></i>Export Results
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if present
        const existingModal = document.getElementById('fieldAnalysisModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('fieldAnalysisModal'));
        modal.show();
    }

    createAnalysisResultsContent(analysisResult) {
        const productivityLevel = analysisResult.productivity_level.replace('_', ' ').toUpperCase();
        const productivityScore = analysisResult.overall_productivity_score;
        
        return `
            <div class="row">
                <!-- Overall Productivity Score -->
                <div class="col-12 mb-4">
                    <div class="card border-primary">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-trophy me-2"></i>
                                Overall Productivity Assessment
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="text-center">
                                        <div class="display-4 text-primary fw-bold">${productivityScore}</div>
                                        <div class="h5 text-muted">Productivity Score</div>
                                        <div class="badge bg-${this.getProductivityBadgeColor(productivityLevel)} fs-6">${productivityLevel}</div>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6>Optimization Priorities:</h6>
                                    <ul class="list-unstyled">
                                        ${analysisResult.optimization_priorities.map(priority => `<li><i class="fas fa-arrow-right text-primary me-2"></i>${priority}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Detailed Analysis Sections -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-seedling me-2"></i>
                                Soil Productivity Analysis
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Soil Quality Score:</span>
                                    <span class="fw-bold">${analysisResult.soil_analysis.soil_quality_score}/10</span>
                                </div>
                                <div class="progress mt-1">
                                    <div class="progress-bar bg-success" style="width: ${analysisResult.soil_analysis.soil_quality_score * 10}%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Productivity Potential:</strong> 
                                <span class="badge bg-${this.getProductivityBadgeColor(analysisResult.soil_analysis.productivity_potential)}">
                                    ${analysisResult.soil_analysis.productivity_potential.replace('_', ' ').toUpperCase()}
                                </span>
                            </div>
                            <div class="mb-3">
                                <strong>Fertility Status:</strong> ${analysisResult.soil_analysis.fertility_status}
                            </div>
                            <div>
                                <strong>Improvements:</strong>
                                <ul class="small">
                                    ${analysisResult.soil_analysis.improvement_recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-cloud-sun me-2"></i>
                                Climate Suitability Analysis
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Climate Score:</span>
                                    <span class="fw-bold">${analysisResult.climate_analysis.climate_score}/10</span>
                                </div>
                                <div class="progress mt-1">
                                    <div class="progress-bar bg-info" style="width: ${analysisResult.climate_analysis.climate_score * 10}%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Growing Season:</strong> ${analysisResult.climate_analysis.growing_season_length} days
                            </div>
                            <div class="mb-3">
                                <strong>Frost Risk:</strong> 
                                <span class="badge bg-${this.getRiskBadgeColor(analysisResult.climate_analysis.frost_risk_level)}">
                                    ${analysisResult.climate_analysis.frost_risk_level.toUpperCase()}
                                </span>
                            </div>
                            <div class="mb-3">
                                <strong>Drought Risk:</strong> 
                                <span class="badge bg-${this.getRiskBadgeColor(analysisResult.climate_analysis.drought_risk_level)}">
                                    ${analysisResult.climate_analysis.drought_risk_level.toUpperCase()}
                                </span>
                            </div>
                            <div>
                                <strong>Suitable Crops:</strong>
                                <div class="mt-1">
                                    ${analysisResult.climate_analysis.suitable_crops.map(crop => `<span class="badge bg-light text-dark me-1">${crop}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0">
                                <i class="fas fa-road me-2"></i>
                                Accessibility Analysis
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Accessibility Score:</span>
                                    <span class="fw-bold">${analysisResult.accessibility_analysis.accessibility_score}/10</span>
                                </div>
                                <div class="progress mt-1">
                                    <div class="progress-bar bg-warning" style="width: ${analysisResult.accessibility_analysis.accessibility_score * 10}%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Road Access:</strong> ${analysisResult.accessibility_analysis.road_access_quality}
                            </div>
                            <div class="mb-3">
                                <strong>Equipment Access:</strong> ${analysisResult.accessibility_analysis.equipment_accessibility}
                            </div>
                            <div class="mb-3">
                                <strong>Operational Efficiency:</strong> ${analysisResult.accessibility_analysis.operational_efficiency}
                            </div>
                            <div>
                                <strong>Improvements:</strong>
                                <ul class="small">
                                    ${analysisResult.accessibility_analysis.improvement_opportunities.map(opp => `<li>${opp}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-secondary text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-tractor me-2"></i>
                                Equipment Efficiency Analysis
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="d-flex justify-content-between">
                                    <span>Equipment Efficiency:</span>
                                    <span class="fw-bold">${analysisResult.equipment_analysis.equipment_efficiency_score}/10</span>
                                </div>
                                <div class="progress mt-1">
                                    <div class="progress-bar bg-secondary" style="width: ${analysisResult.equipment_analysis.equipment_efficiency_score * 10}%"></div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <strong>Recommended Equipment:</strong>
                                <ul class="small">
                                    ${analysisResult.equipment_analysis.recommended_equipment.map(equip => `<li>${equip}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="mb-3">
                                <strong>ROI Estimate:</strong> ${analysisResult.equipment_analysis.cost_benefit_analysis.roi_percentage}%
                            </div>
                            <div>
                                <strong>Optimizations:</strong>
                                <ul class="small">
                                    ${analysisResult.equipment_analysis.efficiency_optimizations.map(opt => `<li>${opt}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Implementation Roadmap -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-dark text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-map-marked-alt me-2"></i>
                                Implementation Roadmap
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Optimization Priorities:</h6>
                                    <ol>
                                        ${analysisResult.optimization_priorities.map(priority => `<li>${priority}</li>`).join('')}
                                    </ol>
                                </div>
                                <div class="col-md-6">
                                    <h6>Implementation Steps:</h6>
                                    <ol>
                                        ${analysisResult.implementation_roadmap.map(step => `<li>${step}</li>`).join('')}
                                    </ol>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getProductivityBadgeColor(level) {
        const colors = {
            'VERY_HIGH': 'success',
            'HIGH': 'primary',
            'MEDIUM': 'warning',
            'LOW': 'danger',
            'VERY_LOW': 'dark'
        };
        return colors[level] || 'secondary';
    }

    getRiskBadgeColor(risk) {
        const colors = {
            'LOW': 'success',
            'MODERATE': 'warning',
            'HIGH': 'danger'
        };
        return colors[risk] || 'secondary';
    }

    exportAnalysisResults(fieldId) {
        this.showAlert('Export functionality coming soon!', 'info');
    }

    async optimizeField(fieldId) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;
        
        try {
            // Show loading state
            this.showLoading(true);
            
            // Prepare optimization request
            const optimizationRequest = {
                field_id: field.id,
                field_name: field.field_name,
                coordinates: {
                    latitude: this.getFieldCenterLat(field),
                    longitude: this.getFieldCenterLng(field)
                },
                boundary: field.boundary,
                area_acres: field.size_acres,
                soil_type: field.soil_type,
                drainage_class: field.drainage_class,
                slope_percent: field.slope_percent,
                organic_matter_percent: field.organic_matter,
                irrigation_available: field.irrigation_available,
                tile_drainage: field.tile_drainage,
                accessibility: field.good_accessibility ? 'good' : 'fair',
                current_equipment: ['Standard tractor', 'Basic implements'],
                budget_constraints: {
                    'annual_budget': 50000,
                    'max_investment': 100000
                },
                optimization_goals: ['efficiency', 'cost_reduction', 'productivity']
            };
            
            // Call optimization analysis API
            const response = await fetch(`http://localhost:8000/api/v1/fields/${fieldId}/optimization-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + this.getAuthToken()
                },
                body: JSON.stringify(optimizationRequest)
            });
            
            if (response.ok) {
                const optimizationResult = await response.json();
                this.showFieldOptimizationResults(fieldId, optimizationResult);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Optimization failed');
            }
        } catch (error) {
            console.error('Error optimizing field:', error);
            this.showAlert('Failed to optimize field. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showFieldOptimizationResults(fieldId, optimizationResult) {
        const field = this.fields.find(f => f.id === fieldId);
        if (!field) return;

        // Create optimization results modal
        const modalHtml = `
            <div class="modal fade" id="fieldOptimizationModal" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-tools me-2"></i>
                                Field Optimization Analysis - ${field.field_name}
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${this.createOptimizationResultsContent(optimizationResult)}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="button" class="btn btn-success" onclick="fieldManager.exportOptimizationResults('${fieldId}')">
                                <i class="fas fa-download me-2"></i>Export Results
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if present
        const existingModal = document.getElementById('fieldOptimizationModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('fieldOptimizationModal'));
        modal.show();
    }

    createOptimizationResultsContent(optimizationResult) {
        const optimizationScore = optimizationResult.overall_optimization_score;
        const totalCost = optimizationResult.total_implementation_cost;
        const totalSavings = optimizationResult.total_annual_savings;
        const roi = optimizationResult.overall_roi_percentage;
        const paybackPeriod = optimizationResult.payback_period_years;
        
        return `
            <div class="row">
                <!-- Overall Optimization Score -->
                <div class="col-12 mb-4">
                    <div class="card border-success">
                        <div class="card-header bg-success text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-trophy me-2"></i>
                                Overall Optimization Assessment
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="display-4 text-success fw-bold">${optimizationScore}</div>
                                        <div class="h5 text-muted">Optimization Score</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="display-4 text-primary fw-bold">$${totalCost.toLocaleString()}</div>
                                        <div class="h5 text-muted">Total Investment</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="display-4 text-info fw-bold">$${totalSavings.toLocaleString()}</div>
                                        <div class="h5 text-muted">Annual Savings</div>
                                    </div>
                                </div>
                                <div class="col-md-3">
                                    <div class="text-center">
                                        <div class="display-4 text-warning fw-bold">${roi.toFixed(1)}%</div>
                                        <div class="h5 text-muted">ROI</div>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <div class="row">
                                    <div class="col-md-6">
                                        <strong>Payback Period:</strong> ${paybackPeriod.toFixed(1)} years
                                    </div>
                                    <div class="col-md-6">
                                        <strong>Risk Assessment:</strong> ${optimizationResult.risk_assessment}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Layout Optimization -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-map-marked-alt me-2"></i>
                                Layout Optimization
                            </h6>
                        </div>
                        <div class="card-body">
                            ${optimizationResult.layout_recommendations.map(rec => `
                                <div class="mb-3">
                                    <h6>${rec.description}</h6>
                                    <div class="row">
                                        <div class="col-6">
                                            <small>Current: ${rec.current_efficiency}%</small><br>
                                            <small>Optimized: ${rec.optimized_efficiency}%</small>
                                        </div>
                                        <div class="col-6">
                                            <small>Gain: ${rec.efficiency_gain}%</small><br>
                                            <small>Cost: $${rec.implementation_cost.toLocaleString()}</small>
                                        </div>
                                    </div>
                                    <div class="progress mt-1">
                                        <div class="progress-bar bg-primary" style="width: ${rec.optimized_efficiency}%"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Access Road Optimization -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-warning text-dark">
                            <h6 class="mb-0">
                                <i class="fas fa-road me-2"></i>
                                Access Road Optimization
                            </h6>
                        </div>
                        <div class="card-body">
                            ${optimizationResult.access_road_recommendations.map(rec => `
                                <div class="mb-3">
                                    <h6>${rec.road_type}</h6>
                                    <div class="row">
                                        <div class="col-6">
                                            <small>Length: ${rec.length_feet.toLocaleString()} ft</small><br>
                                            <small>Width: ${rec.width_feet} ft</small>
                                        </div>
                                        <div class="col-6">
                                            <small>Surface: ${rec.surface_type}</small><br>
                                            <small>Cost: $${rec.total_cost.toLocaleString()}</small>
                                        </div>
                                    </div>
                                    <div class="mt-2">
                                        <strong>Benefits:</strong>
                                        <ul class="small">
                                            ${rec.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                                        </ul>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Equipment Optimization -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-info text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-tractor me-2"></i>
                                Equipment Optimization
                            </h6>
                        </div>
                        <div class="card-body">
                            ${optimizationResult.equipment_recommendations.map(rec => `
                                <div class="mb-3">
                                    <h6>${rec.equipment_type}</h6>
                                    <div class="row">
                                        <div class="col-6">
                                            <small>Current: ${rec.current_efficiency}%</small><br>
                                            <small>Recommended: ${rec.recommended_efficiency}%</small>
                                        </div>
                                        <div class="col-6">
                                            <small>Improvement: ${rec.efficiency_improvement}%</small><br>
                                            <small>ROI: ${rec.roi_percentage}%</small>
                                        </div>
                                    </div>
                                    <div class="progress mt-1">
                                        <div class="progress-bar bg-info" style="width: ${rec.recommended_efficiency}%"></div>
                                    </div>
                                    <div class="mt-2">
                                        <small><strong>Cost:</strong> $${(rec.equipment_cost + rec.installation_cost).toLocaleString()}</small><br>
                                        <small><strong>Payback:</strong> ${rec.payback_period_years} years</small>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Economic Optimization -->
                <div class="col-md-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-secondary text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-dollar-sign me-2"></i>
                                Economic Optimization
                            </h6>
                        </div>
                        <div class="card-body">
                            ${optimizationResult.economic_recommendations.map(rec => `
                                <div class="mb-3">
                                    <h6>${rec.optimization_area}</h6>
                                    <div class="row">
                                        <div class="col-6">
                                            <small>Current: $${rec.current_cost_per_acre}/acre</small><br>
                                            <small>Optimized: $${rec.optimized_cost_per_acre}/acre</small>
                                        </div>
                                        <div class="col-6">
                                            <small>Savings: $${rec.cost_savings_per_acre}/acre</small><br>
                                            <small>ROI: ${rec.roi_percentage}%</small>
                                        </div>
                                    </div>
                                    <div class="progress mt-1">
                                        <div class="progress-bar bg-secondary" style="width: ${(rec.optimized_cost_per_acre / rec.current_cost_per_acre) * 100}%"></div>
                                    </div>
                                    <div class="mt-2">
                                        <small><strong>Total Savings:</strong> $${rec.total_cost_savings.toLocaleString()}</small><br>
                                        <small><strong>Payback:</strong> ${rec.payback_period_years} years</small>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Implementation Plan -->
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-dark text-white">
                            <h6 class="mb-0">
                                <i class="fas fa-calendar-alt me-2"></i>
                                Implementation Plan
                            </h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                ${optimizationResult.implementation_plan.map(plan => `
                                    <div class="col-md-4 mb-3">
                                        <div class="card border-dark">
                                            <div class="card-header bg-light">
                                                <h6 class="mb-0">${plan.phase.replace('_', ' ').toUpperCase()}</h6>
                                            </div>
                                            <div class="card-body">
                                                <div class="mb-2">
                                                    <strong>Duration:</strong> ${plan.duration_months} months
                                                </div>
                                                <div class="mb-2">
                                                    <strong>Cost:</strong> $${plan.total_cost.toLocaleString()}
                                                </div>
                                                <div class="mb-2">
                                                    <strong>Priority Recommendations:</strong>
                                                    <ul class="small">
                                                        ${plan.priority_recommendations.map(rec => `<li>${rec}</li>`).join('')}
                                                    </ul>
                                                </div>
                                                <div>
                                                    <strong>Success Metrics:</strong>
                                                    <ul class="small">
                                                        ${plan.success_metrics.map(metric => `<li>${metric}</li>`).join('')}
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    exportOptimizationResults(fieldId) {
        this.showAlert('Export functionality coming soon!', 'info');
    }
}

// Global functions for HTML onclick handlers
function openFieldForm() {
    fieldManager.openFieldForm();
}

function saveField() {
    fieldManager.validateFieldForm();
}

function drawFieldBoundary() {
    fieldManager.drawFieldBoundary();
}

function calculateAreaFromBoundary() {
    fieldManager.calculateAreaFromBoundary();
}

function applyFieldTemplate(templateName) {
    fieldManager.applyFieldTemplate(templateName);
}

function importFields() {
    fieldManager.importFields();
}

function exportFields() {
    fieldManager.exportFields();
}

function bulkEditFields() {
    fieldManager.bulkEditFields();
}

// Initialize the field management system when the page loads
let fieldManager;

document.addEventListener('DOMContentLoaded', function() {
    fieldManager = new FieldManagementSystem();
});