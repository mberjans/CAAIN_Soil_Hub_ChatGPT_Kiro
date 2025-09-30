/**
 * Comprehensive Interactive Map System
 * CAAIN Soil Hub - Farm Location Input
 * TICKET-008_farm-location-input-8.1
 * 
 * Advanced interactive map interface with:
 * - Multiple map providers (OpenStreetMap, USDA aerial, NAIP, topographic)
 * - Field boundary drawing and management
 * - Multi-field management capabilities
 * - Satellite imagery integration
 * - Layer switching functionality
 * - Integration with location validation services
 */

class InteractiveMapSystem {
    constructor() {
        this.map = null;
        this.currentProvider = 'openstreetmap';
        this.mapProviders = {};
        this.fields = new Map(); // Store field data
        this.currentField = null;
        this.drawingMode = false;
        this.drawnItems = null;
        this.drawControl = null;
        this.markers = new Map(); // Store location markers
        this.validationService = '/api/v1/validation';
        this.locationService = '/api/v1/locations';
        this.geocodingService = '/api/v1/geocoding';
        
        this.init();
    }

    init() {
        this.initializeMapProviders();
        this.initializeMap();
        this.setupDrawingTools();
        this.setupEventListeners();
        this.loadSavedFields();
        this.setupLayerControls();
    }

    initializeMapProviders() {
        // OpenStreetMap - Default provider
        this.mapProviders.openstreetmap = {
            name: 'OpenStreetMap',
            layer: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19
            }),
            icon: 'fas fa-map',
            description: 'Standard street map with roads and landmarks'
        };

        // USDA Aerial Imagery
        this.mapProviders.usda_aerial = {
            name: 'USDA Aerial',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA, Esri, Maxar, Earthstar Geographics',
                maxZoom: 19
            }),
            icon: 'fas fa-satellite',
            description: 'High-resolution aerial imagery from USDA'
        };

        // NAIP (National Agriculture Imagery Program)
        this.mapProviders.naip = {
            name: 'NAIP Imagery',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_NAIP_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA NAIP',
                maxZoom: 19
            }),
            icon: 'fas fa-seedling',
            description: 'National Agriculture Imagery Program - optimized for agricultural use'
        };

        // Topographic Map
        this.mapProviders.topographic = {
            name: 'Topographic',
            layer: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenTopoMap contributors',
                maxZoom: 17
            }),
            icon: 'fas fa-mountain',
            description: 'Topographic map with elevation contours'
        };

        // USDA Soil Survey (overlay)
        this.mapProviders.soil_survey = {
            name: 'Soil Survey',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Soils/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA NRCS',
                maxZoom: 16,
                opacity: 0.7
            }),
            icon: 'fas fa-layer-group',
            description: 'USDA Soil Survey data overlay',
            isOverlay: true
        };

        // Climate Zone Overlay
        this.mapProviders.climate_zones = {
            name: 'Climate Zones',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Climate_Zones/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA Climate Zones',
                maxZoom: 16,
                opacity: 0.6
            }),
            icon: 'fas fa-thermometer-half',
            description: 'USDA Plant Hardiness Zones',
            isOverlay: true
        };

        // SSURGO Soil Survey Overlay
        this.mapProviders.ssurgo_soils = {
            name: 'SSURGO Soils',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Soils/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA NRCS SSURGO',
                maxZoom: 16,
                opacity: 0.7
            }),
            icon: 'fas fa-seedling',
            description: 'USDA SSURGO Soil Survey data with detailed soil properties',
            isOverlay: true
        };

        // NRCS Conservation Practices Overlay
        this.mapProviders.nrcs_conservation = {
            name: 'Conservation Practices',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Conservation_Practices/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA NRCS',
                maxZoom: 16,
                opacity: 0.6
            }),
            icon: 'fas fa-leaf',
            description: 'NRCS conservation practices and programs',
            isOverlay: true
        };

        // Flood Zones Overlay
        this.mapProviders.flood_zones = {
            name: 'Flood Zones',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Flood_Hazard/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© FEMA Flood Maps',
                maxZoom: 16,
                opacity: 0.5
            }),
            icon: 'fas fa-water',
            description: 'FEMA flood hazard zones and risk areas',
            isOverlay: true
        };

        // Agricultural Districts Overlay
        this.mapProviders.agricultural_districts = {
            name: 'Agricultural Districts',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Agricultural_Districts/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USDA Agricultural Districts',
                maxZoom: 16,
                opacity: 0.6
            }),
            icon: 'fas fa-tractor',
            description: 'Agricultural districts and zoning information',
            isOverlay: true
        };

        // Watershed Boundaries Overlay
        this.mapProviders.watershed_boundaries = {
            name: 'Watershed Boundaries',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Watersheds/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USGS Watersheds',
                maxZoom: 16,
                opacity: 0.5
            }),
            icon: 'fas fa-stream',
            description: 'USGS watershed boundaries and drainage areas',
            isOverlay: true
        };

        // Topographic Contours Overlay
        this.mapProviders.topographic_contours = {
            name: 'Topographic Contours',
            layer: L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/USA_Topographic_Contours/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© USGS Topographic',
                maxZoom: 16,
                opacity: 0.4
            }),
            icon: 'fas fa-mountain',
            description: 'Topographic contour lines for elevation analysis',
            isOverlay: true
        };
    }

    initializeMap() {
        // Initialize Leaflet map
        this.map = L.map('location-map', {
            center: [40.0, -95.0],
            zoom: 6,
            zoomControl: true,
            attributionControl: true
        });

        // Add default layer
        this.mapProviders.openstreetmap.layer.addTo(this.map);

        // Initialize drawn items for field boundaries
        this.drawnItems = new L.FeatureGroup();
        this.map.addLayer(this.drawnItems);

        // Add click handler for location selection
        this.map.on('click', (e) => {
            if (!this.drawingMode) {
                this.addLocationMarker(e.latlng.lat, e.latlng.lng);
            }
        });

        // Add context menu for field management
        this.setupContextMenu();
    }

    setupDrawingTools() {
        // Initialize drawing control
        this.drawControl = new L.Control.Draw({
            position: 'topright',
            draw: {
                polygon: {
                    allowIntersection: false,
                    showArea: true,
                    drawError: {
                        color: '#e1e100',
                        message: '<strong>Error:</strong> Shape edges cannot cross!'
                    },
                    shapeOptions: {
                        color: '#3388ff',
                        fillColor: '#3388ff',
                        fillOpacity: 0.2
                    }
                },
                rectangle: {
                    shapeOptions: {
                        color: '#3388ff',
                        fillColor: '#3388ff',
                        fillOpacity: 0.2
                    }
                },
                circle: false,
                marker: false,
                polyline: false,
                circlemarker: false
            },
            edit: {
                featureGroup: this.drawnItems,
                remove: true
            }
        });

        this.map.addControl(this.drawControl);

        // Handle drawing events
        this.map.on(L.Draw.Event.CREATED, (e) => {
            this.handleFieldCreated(e);
        });

        this.map.on(L.Draw.Event.EDITED, (e) => {
            this.handleFieldEdited(e);
        });

        this.map.on(L.Draw.Event.DELETED, (e) => {
            this.handleFieldDeleted(e);
        });
    }

    setupEventListeners() {
        // Map provider switching
        document.addEventListener('change', (e) => {
            if (e.target.id === 'map-provider-select') {
                this.switchMapProvider(e.target.value);
            }
        });

        // Field management buttons
        document.addEventListener('click', (e) => {
            if (e.target.id === 'add-field-btn') {
                this.startFieldDrawing();
            } else if (e.target.id === 'save-field-btn') {
                this.saveCurrentField();
            } else if (e.target.id === 'delete-field-btn') {
                this.deleteCurrentField();
            } else if (e.target.id === 'clear-all-fields-btn') {
                this.clearAllFields();
            }
        });

        // Layer toggle controls
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('layer-toggle')) {
                this.toggleLayer(e.target.value, e.target.checked);
            }
        });
    }

    setupLayerControls() {
        // Create layer control UI
        const layerControl = document.getElementById('layer-controls');
        if (layerControl) {
            layerControl.innerHTML = this.generateLayerControlHTML();
        }
    }

    generateLayerControlHTML() {
        let html = '<div class="layer-control-panel">';
        html += '<h6><i class="fas fa-layer-group me-2"></i>Map Layers</h6>';
        
        // Base layers
        html += '<div class="base-layers mb-3">';
        html += '<h6 class="small text-muted">Base Maps</h6>';
        Object.entries(this.mapProviders).forEach(([key, provider]) => {
            if (!provider.isOverlay) {
                const checked = key === this.currentProvider ? 'checked' : '';
                html += `
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="base-layer" 
                               id="layer-${key}" value="${key}" ${checked}>
                        <label class="form-check-label" for="layer-${key}">
                            <i class="${provider.icon} me-2"></i>${provider.name}
                        </label>
                    </div>
                `;
            }
        });
        html += '</div>';

        // Overlay layers
        html += '<div class="overlay-layers">';
        html += '<h6 class="small text-muted">Overlays</h6>';
        Object.entries(this.mapProviders).forEach(([key, provider]) => {
            if (provider.isOverlay) {
                html += `
                    <div class="form-check">
                        <input class="form-check-input layer-toggle" type="checkbox" 
                               id="overlay-${key}" value="${key}">
                        <label class="form-check-label" for="overlay-${key}">
                            <i class="${provider.icon} me-2"></i>${provider.name}
                        </label>
                    </div>
                `;
            }
        });
        html += '</div>';

        html += '</div>';
        return html;
    }

    switchMapProvider(providerKey) {
        if (!this.mapProviders[providerKey]) {
            console.error(`Unknown map provider: ${providerKey}`);
            return;
        }

        // Remove current base layer
        Object.entries(this.mapProviders).forEach(([key, provider]) => {
            if (!provider.isOverlay && this.map.hasLayer(provider.layer)) {
                this.map.removeLayer(provider.layer);
            }
        });

        // Add new base layer
        this.mapProviders[providerKey].layer.addTo(this.map);
        this.currentProvider = providerKey;

        // Update UI
        this.updateProviderInfo(providerKey);
    }

    toggleLayer(layerKey, enabled) {
        const provider = this.mapProviders[layerKey];
        if (!provider || !provider.isOverlay) {
            return;
        }

        if (enabled) {
            provider.layer.addTo(this.map);
        } else {
            this.map.removeLayer(provider.layer);
        }
    }

    updateProviderInfo(providerKey) {
        const provider = this.mapProviders[providerKey];
        const infoElement = document.getElementById('map-provider-info');
        if (infoElement) {
            infoElement.innerHTML = `
                <div class="map-provider-info">
                    <h6><i class="${provider.icon} me-2"></i>${provider.name}</h6>
                    <p class="small text-muted mb-0">${provider.description}</p>
                </div>
            `;
        }
    }

    addLocationMarker(latitude, longitude) {
        // Remove existing location marker
        if (this.markers.has('location')) {
            this.map.removeLayer(this.markers.get('location'));
        }

        // Add new location marker
        const marker = L.marker([latitude, longitude], {
            draggable: true,
            icon: L.divIcon({
                className: 'location-marker',
                html: '<i class="fas fa-map-marker-alt text-primary"></i>',
                iconSize: [30, 30],
                iconAnchor: [15, 30]
            })
        }).addTo(this.map);

        marker.bindPopup(`
            <div class="marker-popup">
                <h6>Selected Location</h6>
                <p><strong>Latitude:</strong> ${latitude.toFixed(6)}°</p>
                <p><strong>Longitude:</strong> ${longitude.toFixed(6)}°</p>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="mapSystem.validateLocation(${latitude}, ${longitude})">
                        <i class="fas fa-check me-1"></i>Validate
                    </button>
                    <button class="btn btn-sm btn-success" onclick="mapSystem.saveLocation(${latitude}, ${longitude})">
                        <i class="fas fa-save me-1"></i>Save
                    </button>
                </div>
            </div>
        `);

        this.markers.set('location', marker);

        // Update coordinate inputs
        this.updateCoordinateInputs(latitude, longitude);

        // Enable validation
        this.enableValidationButton();
    }

    handleFieldCreated(e) {
        const layer = e.layer;
        const fieldId = this.generateFieldId();
        
        // Calculate area
        const area = this.calculateArea(layer);
        
        // Create field data
        const fieldData = {
            id: fieldId,
            name: `Field ${this.fields.size + 1}`,
            boundary: layer,
            area: area,
            created: new Date(),
            modified: new Date()
        };

        // Store field
        this.fields.set(fieldId, fieldData);
        this.currentField = fieldId;

        // Add to drawn items
        this.drawnItems.addLayer(layer);

        // Update field list
        this.updateFieldList();

        // Show field info
        this.showFieldInfo(fieldData);

        // Enable field management buttons
        this.enableFieldManagementButtons();
    }

    handleFieldEdited(e) {
        const layers = e.layers;
        layers.eachLayer((layer) => {
            // Find field by layer
            for (const [fieldId, fieldData] of this.fields) {
                if (fieldData.boundary === layer) {
                    // Update field data
                    fieldData.area = this.calculateArea(layer);
                    fieldData.modified = new Date();
                    
                    // Update UI
                    this.updateFieldInfo(fieldId);
                    break;
                }
            }
        });
    }

    handleFieldDeleted(e) {
        const layers = e.layers;
        layers.eachLayer((layer) => {
            // Find and remove field
            for (const [fieldId, fieldData] of this.fields) {
                if (fieldData.boundary === layer) {
                    this.fields.delete(fieldId);
                    if (this.currentField === fieldId) {
                        this.currentField = null;
                        this.disableFieldManagementButtons();
                    }
                    break;
                }
            }
        });
        
        this.updateFieldList();
    }

    calculateArea(layer) {
        if (layer instanceof L.Polygon || layer instanceof L.Rectangle) {
            const area = L.GeometryUtil.geodesicArea(layer.getLatLngs()[0]);
            return {
                squareMeters: area,
                acres: area * 0.000247105,
                hectares: area * 0.0001
            };
        }
        return null;
    }

    generateFieldId() {
        return 'field_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    updateFieldList() {
        const fieldList = document.getElementById('field-list');
        if (!fieldList) return;

        if (this.fields.size === 0) {
            fieldList.innerHTML = '<p class="text-muted">No fields created yet</p>';
            return;
        }

        let html = '<div class="field-list">';
        this.fields.forEach((fieldData, fieldId) => {
            const isActive = fieldId === this.currentField ? 'active' : '';
            html += `
                <div class="field-item ${isActive}" onclick="mapSystem.selectField('${fieldId}')">
                    <div class="field-header">
                        <h6>${fieldData.name}</h6>
                        <span class="field-area">${fieldData.area.acres.toFixed(2)} acres</span>
                    </div>
                    <div class="field-details">
                        <small class="text-muted">
                            Created: ${fieldData.created.toLocaleDateString()}
                        </small>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        fieldList.innerHTML = html;
    }

    selectField(fieldId) {
        this.currentField = fieldId;
        this.updateFieldList();
        this.showFieldInfo(this.fields.get(fieldId));
        this.enableFieldManagementButtons();
    }

    showFieldInfo(fieldData) {
        const fieldInfo = document.getElementById('field-info');
        if (!fieldInfo) return;

        fieldInfo.innerHTML = `
            <div class="field-info-panel">
                <h6><i class="fas fa-info-circle me-2"></i>Field Information</h6>
                <div class="field-details">
                    <p><strong>Name:</strong> ${fieldData.name}</p>
                    <p><strong>Area:</strong> ${fieldData.area.acres.toFixed(2)} acres (${fieldData.area.hectares.toFixed(2)} ha)</p>
                    <p><strong>Created:</strong> ${fieldData.created.toLocaleDateString()}</p>
                    <p><strong>Modified:</strong> ${fieldData.modified.toLocaleDateString()}</p>
                </div>
                <div class="field-actions mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="mapSystem.editFieldName('${fieldData.id}')">
                        <i class="fas fa-edit me-1"></i>Edit Name
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="mapSystem.analyzeField('${fieldData.id}')">
                        <i class="fas fa-chart-line me-1"></i>Analyze
                    </button>
                </div>
            </div>
        `;
    }

    startFieldDrawing() {
        this.drawingMode = true;
        this.drawControl._toolbars.draw._modes.polygon.handler.enable();
        
        // Update UI
        const addFieldBtn = document.getElementById('add-field-btn');
        if (addFieldBtn) {
            addFieldBtn.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Drawing';
            addFieldBtn.onclick = () => this.stopFieldDrawing();
        }
    }

    stopFieldDrawing() {
        this.drawingMode = false;
        this.drawControl._toolbars.draw._modes.polygon.handler.disable();
        
        // Update UI
        const addFieldBtn = document.getElementById('add-field-btn');
        if (addFieldBtn) {
            addFieldBtn.innerHTML = '<i class="fas fa-plus me-2"></i>Add Field';
            addFieldBtn.onclick = () => this.startFieldDrawing();
        }
    }

    saveCurrentField() {
        if (!this.currentField) {
            this.showNotification('No field selected to save', 'warning');
            return;
        }

        const fieldData = this.fields.get(this.currentField);
        if (!fieldData) {
            this.showNotification('Field data not found', 'error');
            return;
        }

        // Save to backend
        this.saveFieldToBackend(fieldData);
    }

    async saveFieldToBackend(fieldData) {
        try {
            const response = await fetch(`${this.locationService}/fields`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: fieldData.name,
                    boundary: this.serializeBoundary(fieldData.boundary),
                    area: fieldData.area,
                    created: fieldData.created.toISOString(),
                    modified: fieldData.modified.toISOString()
                })
            });

            if (response.ok) {
                this.showNotification('Field saved successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Save failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Save error: ${error.message}`, 'error');
        }
    }

    serializeBoundary(layer) {
        if (layer instanceof L.Polygon) {
            return {
                type: 'Polygon',
                coordinates: [layer.getLatLngs()[0].map(latlng => [latlng.lng, latlng.lat])]
            };
        } else if (layer instanceof L.Rectangle) {
            const bounds = layer.getBounds();
            return {
                type: 'Rectangle',
                coordinates: [
                    [bounds.getSouthWest().lng, bounds.getSouthWest().lat],
                    [bounds.getNorthEast().lng, bounds.getNorthEast().lat]
                ]
            };
        }
        return null;
    }

    deleteCurrentField() {
        if (!this.currentField) {
            this.showNotification('No field selected to delete', 'warning');
            return;
        }

        if (confirm('Are you sure you want to delete this field?')) {
            const fieldData = this.fields.get(this.currentField);
            if (fieldData) {
                this.drawnItems.removeLayer(fieldData.boundary);
                this.fields.delete(this.currentField);
                this.currentField = null;
                this.updateFieldList();
                this.disableFieldManagementButtons();
                this.showNotification('Field deleted', 'success');
            }
        }
    }

    clearAllFields() {
        if (this.fields.size === 0) {
            this.showNotification('No fields to clear', 'info');
            return;
        }

        if (confirm(`Are you sure you want to delete all ${this.fields.size} fields?`)) {
            this.fields.clear();
            this.drawnItems.clearLayers();
            this.currentField = null;
            this.updateFieldList();
            this.disableFieldManagementButtons();
            this.showNotification('All fields cleared', 'success');
        }
    }

    async validateLocation(latitude, longitude) {
        try {
            const response = await fetch(`${this.validationService}/coordinates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            });

            const result = await response.json();

            if (result.valid) {
                this.showNotification('Location validated successfully!', 'success');
                this.enableSaveButton();
                
                // Show agricultural context if available
                if (result.geographic_info) {
                    this.showAgriculturalContext(result.geographic_info);
                }
            } else {
                this.showNotification(`Validation failed: ${result.errors.join(', ')}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Validation error: ${error.message}`, 'error');
        }
    }

    async saveLocation(latitude, longitude) {
        try {
            const response = await fetch(`${this.locationService}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: 'Farm Location',
                    coordinates: {
                        latitude: latitude,
                        longitude: longitude
                    }
                })
            });

            if (response.ok) {
                this.showNotification('Location saved successfully!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Save failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Save error: ${error.message}`, 'error');
        }
    }

    async loadSavedFields() {
        try {
            const response = await fetch(`${this.locationService}/fields`);
            if (response.ok) {
                const fields = await response.json();
                fields.forEach(field => {
                    this.loadFieldFromBackend(field);
                });
            }
        } catch (error) {
            console.log('No saved fields found');
        }
    }

    loadFieldFromBackend(fieldData) {
        const fieldId = fieldData.id || this.generateFieldId();
        
        // Create Leaflet layer from boundary data
        let layer;
        if (fieldData.boundary.type === 'Polygon') {
            const latlngs = fieldData.boundary.coordinates[0].map(coord => [coord[1], coord[0]]);
            layer = L.polygon(latlngs, {
                color: '#3388ff',
                fillColor: '#3388ff',
                fillOpacity: 0.2
            });
        } else if (fieldData.boundary.type === 'Rectangle') {
            const bounds = L.latLngBounds(fieldData.boundary.coordinates);
            layer = L.rectangle(bounds, {
                color: '#3388ff',
                fillColor: '#3388ff',
                fillOpacity: 0.2
            });
        }

        if (layer) {
            // Store field data
            this.fields.set(fieldId, {
                id: fieldId,
                name: fieldData.name,
                boundary: layer,
                area: fieldData.area,
                created: new Date(fieldData.created),
                modified: new Date(fieldData.modified)
            });

            // Add to map
            this.drawnItems.addLayer(layer);
        }
    }

    setupContextMenu() {
        // Add context menu for field management
        this.map.on('contextmenu', (e) => {
            const contextMenu = document.getElementById('map-context-menu');
            if (contextMenu) {
                contextMenu.style.display = 'block';
                contextMenu.style.left = e.containerPoint.x + 'px';
                contextMenu.style.top = e.containerPoint.y + 'px';
            }
        });

        // Hide context menu on map click
        this.map.on('click', () => {
            const contextMenu = document.getElementById('map-context-menu');
            if (contextMenu) {
                contextMenu.style.display = 'none';
            }
        });
    }

    updateCoordinateInputs(latitude, longitude) {
        // Update coordinate inputs if they exist
        const latInput = document.getElementById('latitude-decimal');
        const lngInput = document.getElementById('longitude-decimal');
        
        if (latInput) latInput.value = latitude.toFixed(6);
        if (lngInput) lngInput.value = longitude.toFixed(6);
    }

    enableValidationButton() {
        const validateBtn = document.getElementById('validate-btn');
        if (validateBtn) validateBtn.disabled = false;
    }

    enableSaveButton() {
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) saveBtn.disabled = false;
    }

    enableFieldManagementButtons() {
        const saveFieldBtn = document.getElementById('save-field-btn');
        const deleteFieldBtn = document.getElementById('delete-field-btn');
        
        if (saveFieldBtn) saveFieldBtn.disabled = false;
        if (deleteFieldBtn) deleteFieldBtn.disabled = false;
    }

    disableFieldManagementButtons() {
        const saveFieldBtn = document.getElementById('save-field-btn');
        const deleteFieldBtn = document.getElementById('delete-field-btn');
        
        if (saveFieldBtn) saveFieldBtn.disabled = true;
        if (deleteFieldBtn) deleteFieldBtn.disabled = true;
    }

    showNotification(message, type) {
        const notification = document.getElementById('map-notification');
        if (notification) {
            notification.textContent = message;
            notification.className = `alert alert-${type} alert-dismissible fade show`;
            notification.style.display = 'block';

            // Auto-hide after 5 seconds
            setTimeout(() => {
                notification.style.display = 'none';
            }, 5000);
        }
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
        
        const notification = document.getElementById('map-notification');
        if (notification) {
            notification.innerHTML = notification.innerHTML + contextHtml;
        }
    }

    // Public methods for external access
    getCurrentFields() {
        return Array.from(this.fields.values());
    }

    getCurrentField() {
        return this.currentField ? this.fields.get(this.currentField) : null;
    }

    exportFields() {
        const fieldsData = Array.from(this.fields.values()).map(field => ({
            id: field.id,
            name: field.name,
            boundary: this.serializeBoundary(field.boundary),
            area: field.area,
            created: field.created.toISOString(),
            modified: field.modified.toISOString()
        }));

        return JSON.stringify(fieldsData, null, 2);
    }

    importFields(fieldsJson) {
        try {
            const fieldsData = JSON.parse(fieldsJson);
            fieldsData.forEach(field => {
                this.loadFieldFromBackend(field);
            });
            this.updateFieldList();
            this.showNotification('Fields imported successfully!', 'success');
        } catch (error) {
            this.showNotification('Invalid fields data format', 'error');
        }
    }

    editFieldName(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        const newName = prompt('Enter new field name:', fieldData.name);
        if (newName && newName.trim() !== '') {
            fieldData.name = newName.trim();
            fieldData.modified = new Date();
            this.updateFieldList();
            this.showFieldInfo(fieldData);
            this.showNotification('Field name updated successfully!', 'success');
        }
    }

    async analyzeField(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        try {
            this.showNotification('Analyzing field...', 'info');
            
            // Get field center coordinates for analysis
            const bounds = fieldData.boundary.getBounds();
            const center = bounds.getCenter();
            
            // Call field analysis API
            const response = await fetch(`${this.locationService}/fields/${fieldId}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    center_coordinates: {
                        latitude: center.lat,
                        longitude: center.lng
                    },
                    boundary: this.serializeBoundary(fieldData.boundary),
                    area: fieldData.area
                })
            });

            if (response.ok) {
                const analysis = await response.json();
                this.showFieldAnalysis(analysis);
                this.showNotification('Field analysis completed!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Analysis failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            this.showNotification(`Analysis error: ${error.message}`, 'error');
        }
    }

    showFieldAnalysis(analysis) {
        const analysisHtml = `
            <div class="field-analysis-panel mt-3 p-3 bg-light rounded">
                <h6><i class="fas fa-chart-line me-2"></i>Field Analysis Results</h6>
                <div class="analysis-details">
                    <p><strong>Soil Type:</strong> ${analysis.soil_type || 'Unknown'}</p>
                    <p><strong>Climate Zone:</strong> ${analysis.climate_zone || 'Unknown'}</p>
                    <p><strong>USDA Hardiness Zone:</strong> ${analysis.usda_zone || 'Unknown'}</p>
                    <p><strong>Elevation:</strong> ${analysis.elevation ? analysis.elevation + ' meters' : 'Unknown'}</p>
                    <p><strong>Slope:</strong> ${analysis.slope ? analysis.slope + '%' : 'Unknown'}</p>
                    <p><strong>Drainage:</strong> ${analysis.drainage || 'Unknown'}</p>
                </div>
                ${analysis.recommendations ? `
                    <div class="recommendations mt-3">
                        <h6>Recommendations:</h6>
                        <ul>
                            ${analysis.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        const fieldInfo = document.getElementById('field-info');
        if (fieldInfo) {
            fieldInfo.innerHTML = fieldInfo.innerHTML + analysisHtml;
        }
    }

    // Agricultural Analysis Tools
    async performSlopeAnalysis(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        try {
            this.showNotification('Performing slope analysis...', 'info');
            
            const bounds = fieldData.boundary.getBounds();
            const center = bounds.getCenter();
            
            const response = await fetch(`${this.locationService}/fields/${fieldId}/slope-analysis`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    coordinates: {
                        latitude: center.lat,
                        longitude: center.lng
                    },
                    boundary: this.serializeBoundary(fieldData.boundary)
                })
            });

            if (response.ok) {
                const slopeData = await response.json();
                this.showSlopeAnalysis(slopeData);
                this.showNotification('Slope analysis completed!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Slope analysis failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Slope analysis error:', error);
            this.showNotification('Slope analysis failed due to network error', 'error');
        }
    }

    async performDrainageAssessment(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        try {
            this.showNotification('Assessing drainage...', 'info');
            
            const bounds = fieldData.boundary.getBounds();
            const center = bounds.getCenter();
            
            const response = await fetch(`${this.locationService}/fields/${fieldId}/drainage-assessment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    coordinates: {
                        latitude: center.lat,
                        longitude: center.lng
                    },
                    boundary: this.serializeBoundary(fieldData.boundary),
                    area: fieldData.area
                })
            });

            if (response.ok) {
                const drainageData = await response.json();
                this.showDrainageAssessment(drainageData);
                this.showNotification('Drainage assessment completed!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Drainage assessment failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Drainage assessment error:', error);
            this.showNotification('Drainage assessment failed due to network error', 'error');
        }
    }

    async evaluateFieldAccessibility(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        try {
            this.showNotification('Evaluating field accessibility...', 'info');
            
            const bounds = fieldData.boundary.getBounds();
            const center = bounds.getCenter();
            
            const response = await fetch(`${this.locationService}/fields/${fieldId}/accessibility-evaluation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    coordinates: {
                        latitude: center.lat,
                        longitude: center.lng
                    },
                    boundary: this.serializeBoundary(fieldData.boundary),
                    area: fieldData.area
                })
            });

            if (response.ok) {
                const accessibilityData = await response.json();
                this.showAccessibilityEvaluation(accessibilityData);
                this.showNotification('Accessibility evaluation completed!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Accessibility evaluation failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Accessibility evaluation error:', error);
            this.showNotification('Accessibility evaluation failed due to network error', 'error');
        }
    }

    async getSoilSurveyData(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        try {
            this.showNotification('Retrieving soil survey data...', 'info');
            
            const bounds = fieldData.boundary.getBounds();
            const center = bounds.getCenter();
            
            const response = await fetch(`${this.locationService}/fields/${fieldId}/soil-survey`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    coordinates: {
                        latitude: center.lat,
                        longitude: center.lng
                    },
                    boundary: this.serializeBoundary(fieldData.boundary)
                })
            });

            if (response.ok) {
                const soilData = await response.json();
                this.showSoilSurveyData(soilData);
                this.showNotification('Soil survey data retrieved!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Soil survey retrieval failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Soil survey retrieval error:', error);
            this.showNotification('Soil survey retrieval failed due to network error', 'error');
        }
    }

    async getWatershedInformation(fieldId) {
        const fieldData = this.fields.get(fieldId);
        if (!fieldData) {
            this.showNotification('Field not found', 'error');
            return;
        }

        try {
            this.showNotification('Retrieving watershed information...', 'info');
            
            const bounds = fieldData.boundary.getBounds();
            const center = bounds.getCenter();
            
            const response = await fetch(`${this.locationService}/fields/${fieldId}/watershed-info`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    field_id: fieldId,
                    coordinates: {
                        latitude: center.lat,
                        longitude: center.lng
                    },
                    boundary: this.serializeBoundary(fieldData.boundary)
                })
            });

            if (response.ok) {
                const watershedData = await response.json();
                this.showWatershedInformation(watershedData);
                this.showNotification('Watershed information retrieved!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(`Watershed information retrieval failed: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Watershed information retrieval error:', error);
            this.showNotification('Watershed information retrieval failed due to network error', 'error');
        }
    }

    // Display methods for agricultural analysis results
    showSlopeAnalysis(slopeData) {
        const analysisHtml = `
            <div class="agricultural-analysis-panel">
                <h5><i class="fas fa-mountain"></i> Slope Analysis Results</h5>
                <div class="analysis-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Average Slope:</span>
                        <span class="metric-value">${slopeData.average_slope}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Maximum Slope:</span>
                        <span class="metric-value">${slopeData.max_slope}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Slope Classification:</span>
                        <span class="metric-value">${slopeData.slope_classification}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Erosion Risk:</span>
                        <span class="metric-value ${slopeData.erosion_risk.toLowerCase()}">${slopeData.erosion_risk}</span>
                    </div>
                </div>
                <div class="recommendations">
                    <h6>Recommendations:</h6>
                    <ul>
                        ${slopeData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        this.displayAnalysisResults('slope-analysis', analysisHtml);
    }

    showDrainageAssessment(drainageData) {
        const analysisHtml = `
            <div class="agricultural-analysis-panel">
                <h5><i class="fas fa-tint"></i> Drainage Assessment Results</h5>
                <div class="analysis-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Drainage Class:</span>
                        <span class="metric-value">${drainageData.drainage_class}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Water Table Depth:</span>
                        <span class="metric-value">${drainageData.water_table_depth}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Flood Risk:</span>
                        <span class="metric-value ${drainageData.flood_risk.toLowerCase()}">${drainageData.flood_risk}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Drainage Suitability:</span>
                        <span class="metric-value ${drainageData.suitability.toLowerCase()}">${drainageData.suitability}</span>
                    </div>
                </div>
                <div class="recommendations">
                    <h6>Drainage Recommendations:</h6>
                    <ul>
                        ${drainageData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        this.displayAnalysisResults('drainage-assessment', analysisHtml);
    }

    showAccessibilityEvaluation(accessibilityData) {
        const analysisHtml = `
            <div class="agricultural-analysis-panel">
                <h5><i class="fas fa-truck"></i> Field Accessibility Evaluation</h5>
                <div class="analysis-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Road Access:</span>
                        <span class="metric-value ${accessibilityData.road_access.toLowerCase()}">${accessibilityData.road_access}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Equipment Access:</span>
                        <span class="metric-value ${accessibilityData.equipment_access.toLowerCase()}">${accessibilityData.equipment_access}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Distance to Roads:</span>
                        <span class="metric-value">${accessibilityData.distance_to_roads}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Accessibility Score:</span>
                        <span class="metric-value">${accessibilityData.accessibility_score}/10</span>
                    </div>
                </div>
                <div class="recommendations">
                    <h6>Accessibility Recommendations:</h6>
                    <ul>
                        ${accessibilityData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        this.displayAnalysisResults('accessibility-evaluation', analysisHtml);
    }

    showSoilSurveyData(soilData) {
        const analysisHtml = `
            <div class="agricultural-analysis-panel">
                <h5><i class="fas fa-seedling"></i> SSURGO Soil Survey Data</h5>
                <div class="soil-properties">
                    <h6>Soil Properties:</h6>
                    <div class="analysis-metrics">
                        <div class="metric-item">
                            <span class="metric-label">Soil Series:</span>
                            <span class="metric-value">${soilData.soil_series}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Soil Texture:</span>
                            <span class="metric-value">${soilData.texture}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">pH Range:</span>
                            <span class="metric-value">${soilData.ph_range}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Organic Matter:</span>
                            <span class="metric-value">${soilData.organic_matter}</span>
                        </div>
                        <div class="metric-item">
                            <span class="metric-label">Cation Exchange Capacity:</span>
                            <span class="metric-value">${soilData.cec}</span>
                        </div>
                    </div>
                </div>
                <div class="soil-limitations">
                    <h6>Soil Limitations:</h6>
                    <ul>
                        ${soilData.limitations.map(lim => `<li>${lim}</li>`).join('')}
                    </ul>
                </div>
                <div class="recommendations">
                    <h6>Soil Management Recommendations:</h6>
                    <ul>
                        ${soilData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        this.displayAnalysisResults('soil-survey', analysisHtml);
    }

    showWatershedInformation(watershedData) {
        const analysisHtml = `
            <div class="agricultural-analysis-panel">
                <h5><i class="fas fa-stream"></i> Watershed Information</h5>
                <div class="analysis-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Watershed Name:</span>
                        <span class="metric-value">${watershedData.watershed_name}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Watershed Area:</span>
                        <span class="metric-value">${watershedData.watershed_area}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Stream Order:</span>
                        <span class="metric-value">${watershedData.stream_order}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Water Quality:</span>
                        <span class="metric-value ${watershedData.water_quality.toLowerCase()}">${watershedData.water_quality}</span>
                    </div>
                </div>
                <div class="watershed-features">
                    <h6>Watershed Features:</h6>
                    <ul>
                        ${watershedData.features.map(feature => `<li>${feature}</li>`).join('')}
                    </ul>
                </div>
                <div class="recommendations">
                    <h6>Water Management Recommendations:</h6>
                    <ul>
                        ${watershedData.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        this.displayAnalysisResults('watershed-info', analysisHtml);
    }

    displayAnalysisResults(analysisType, htmlContent) {
        // Create or update analysis results panel
        let analysisPanel = document.getElementById('agricultural-analysis-panel');
        if (!analysisPanel) {
            analysisPanel = document.createElement('div');
            analysisPanel.id = 'agricultural-analysis-panel';
            analysisPanel.className = 'agricultural-analysis-panel';
            
            // Add close button
            const closeButton = document.createElement('button');
            closeButton.className = 'btn-close-analysis';
            closeButton.innerHTML = '<i class="fas fa-times"></i>';
            closeButton.onclick = () => analysisPanel.remove();
            
            analysisPanel.appendChild(closeButton);
            
            // Insert after map container
            const mapContainer = document.getElementById('location-map');
            mapContainer.parentNode.insertBefore(analysisPanel, mapContainer.nextSibling);
        }
        
        analysisPanel.innerHTML = htmlContent;
        analysisPanel.style.display = 'block';
        
        // Scroll to analysis panel
        analysisPanel.scrollIntoView({ behavior: 'smooth' });
    }

    // Overlay Management Methods
    addOverlay(overlayName) {
        if (this.mapProviders[overlayName] && this.mapProviders[overlayName].isOverlay) {
            this.mapProviders[overlayName].layer.addTo(this.map);
            this.showNotification(`Added ${this.mapProviders[overlayName].name} overlay`, 'success');
        }
    }

    removeOverlay(overlayName) {
        if (this.mapProviders[overlayName] && this.mapProviders[overlayName].isOverlay) {
            this.map.removeLayer(this.mapProviders[overlayName].layer);
            this.showNotification(`Removed ${this.mapProviders[overlayName].name} overlay`, 'info');
        }
    }

    toggleOverlay(overlayName) {
        if (this.mapProviders[overlayName] && this.mapProviders[overlayName].isOverlay) {
            if (this.map.hasLayer(this.mapProviders[overlayName].layer)) {
                this.removeOverlay(overlayName);
            } else {
                this.addOverlay(overlayName);
            }
        }
    }

    clearAllOverlays() {
        Object.keys(this.mapProviders).forEach(providerName => {
            if (this.mapProviders[providerName].isOverlay) {
                this.removeOverlay(providerName);
            }
        });
    }
}

// Global instance
let mapSystem;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    mapSystem = new InteractiveMapSystem();
});

// Export for external access
window.mapSystem = mapSystem;
