// Crop Filtering JavaScript for CAAIN Soil Hub
// Provides comprehensive filtering, search, and result display functionality

// Advanced Filter State Management
class FilterStateManager {
    constructor() {
        this.currentFilters = {};
        this.filterHistory = []; // For undo/redo functionality
        this.historyIndex = -1; // Current position in the filter history
        this.debounceTimers = {}; // For debounced updates
        this.changeListeners = []; // For notifying when filters change
        this.userPreferences = this.loadUserPreferences();
        this.sessionId = this.generateSessionId();
        this.filterSnapshots = {}; // To save and restore filter states by label
        this.init();
    }

    init() {
        this.loadFiltersFromUrl();
        this.loadFiltersFromLocalStorage();
        this.loadFilterSnapshots();
        // Add browser back/forward support
        window.addEventListener('popstate', this.handlePopState.bind(this));
    }

    /**
     * Load filters from URL query parameters
     */
    loadFiltersFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const filtersParam = urlParams.get('filters');
        
        if (filtersParam) {
            try {
                const filters = JSON.parse(decodeURIComponent(filtersParam));
                this.currentFilters = this.validateFilters(filters);
                return true;
            } catch (e) {
                console.warn('Could not parse filters from URL:', e);
                return false;
            }
        }
        return false;
    }

    /**
     * Save filters to URL query parameters
     */
    saveFiltersToUrl() {
        const url = new URL(window.location);
        if (Object.keys(this.currentFilters).length > 0) {
            url.searchParams.set('filters', encodeURIComponent(JSON.stringify(this.currentFilters)));
        } else {
            url.searchParams.delete('filters');
        }
        window.history.replaceState({}, '', url);
    }

    /**
     * Load filters from browser localStorage
     */
    loadFiltersFromLocalStorage() {
        try {
            const savedFilters = localStorage.getItem('cropFilters');
            if (savedFilters) {
                const filters = JSON.parse(savedFilters);
                this.currentFilters = this.validateFilters(filters);
                return true;
            }
        } catch (e) {
            console.warn('Could not load filters from localStorage:', e);
        }
        return false;
    }

    /**
     * Save filters to browser localStorage
     */
    saveFiltersToLocalStorage() {
        try {
            localStorage.setItem('cropFilters', JSON.stringify(this.currentFilters));
            return true;
        } catch (e) {
            console.error('Could not save filters to localStorage:', e);
            return false;
        }
    }

    /**
     * Save filters to session storage (temporary storage for current session)
     */
    saveFiltersToSessionStorage() {
        try {
            sessionStorage.setItem('cropFiltersSession', JSON.stringify(this.currentFilters));
            return true;
        } catch (e) {
            console.error('Could not save filters to sessionStorage:', e);
            return false;
        }
    }

    /**
     * Load filters from session storage
     */
    loadFiltersFromSessionStorage() {
        try {
            const savedFilters = sessionStorage.getItem('cropFiltersSession');
            if (savedFilters) {
                const filters = JSON.parse(savedFilters);
                this.currentFilters = this.validateFilters(filters);
                return true;
            }
        } catch (e) {
            console.warn('Could not load filters from sessionStorage:', e);
        }
        return false;
    }

    /**
     * Load saved filter snapshots
     */
    loadFilterSnapshots() {
        try {
            const snapshots = localStorage.getItem('cropFilterSnapshots');
            if (snapshots) {
                this.filterSnapshots = JSON.parse(snapshots);
            }
        } catch (e) {
            console.warn('Could not load filter snapshots:', e);
        }
    }

    /**
     * Save filter snapshots
     */
    saveFilterSnapshots() {
        try {
            localStorage.setItem('cropFilterSnapshots', JSON.stringify(this.filterSnapshots));
        } catch (e) {
            console.error('Could not save filter snapshots:', e);
        }
    }

    /**
     * Save current filters with a label for later retrieval
     */
    saveFilterSnapshot(label, description = '') {
        const snapshot = {
            filters: JSON.parse(JSON.stringify(this.currentFilters)),
            savedAt: new Date().toISOString(),
            description: description,
            sessionId: this.sessionId
        };
        this.filterSnapshots[label] = snapshot;
        this.saveFilterSnapshots();
    }

    /**
     * Load filters from a saved snapshot
     */
    loadFilterSnapshot(label) {
        if (this.filterSnapshots[label]) {
            this.currentFilters = this.validateFilters(JSON.parse(JSON.stringify(this.filterSnapshots[label].filters)));
            this.notifyChangeListeners();
            return true;
        }
        return false;
    }

    /**
     * Delete a saved snapshot
     */
    deleteFilterSnapshot(label) {
        if (this.filterSnapshots[label]) {
            delete this.filterSnapshots[label];
            this.saveFilterSnapshots();
            return true;
        }
        return false;
    }

    /**
     * Validate filters to ensure they are in a valid format
     */
    validateFilters(filters) {
        if (typeof filters !== 'object' || filters === null) {
            return {};
        }
        
        // Validate range values to ensure min <= max
        if (filters.soil_ph_range) {
            filters.soil_ph_range.min = Math.max(3, Math.min(filters.soil_ph_range.min, filters.soil_ph_range.max));
            filters.soil_ph_range.max = Math.max(filters.soil_ph_range.min, filters.soil_ph_range.max);
        }
        
        if (filters.growing_season_range) {
            filters.growing_season_range.min = Math.max(30, Math.min(filters.growing_season_range.min, filters.growing_season_range.max));
            filters.growing_season_range.max = Math.max(filters.growing_season_range.min, filters.growing_season_range.max);
        }
        
        return filters;
    }

    /**
     * Add a filter change listener
     */
    addChangeListener(callback) {
        this.changeListeners.push(callback);
    }

    /**
     * Remove a filter change listener
     */
    removeChangeListener(callback) {
        const index = this.changeListeners.indexOf(callback);
        if (index > -1) {
            this.changeListeners.splice(index, 1);
        }
    }

    /**
     * Notify all change listeners
     */
    notifyChangeListeners() {
        this.changeListeners.forEach(callback => {
            try {
                callback(this.currentFilters);
            } catch (e) {
                console.error('Error in filter change listener:', e);
            }
        });
    }

    /**
     * Set a filter value and save it
     */
    setFilter(key, value) {
        this.currentFilters[key] = value;
        this.saveCurrentState();
        this.notifyChangeListeners();
    }

    /**
     * Get a filter value
     */
    getFilter(key) {
        return this.currentFilters[key];
    }

    /**
     * Remove a filter
     */
    removeFilter(key) {
        delete this.currentFilters[key];
        this.saveCurrentState();
        this.notifyChangeListeners();
    }

    /**
     * Clear all filters
     */
    clearFilters() {
        this.currentFilters = {};
        this.saveCurrentState();
        this.notifyChangeListeners();
    }

    /**
     * Get all current filters
     */
    getFilters() {
        return JSON.parse(JSON.stringify(this.currentFilters));
    }

    /**
     * Save current filter state to all persistent stores
     */
    saveCurrentState() {
        this.saveFiltersToUrl();
        this.saveFiltersToLocalStorage();
        this.saveFiltersToSessionStorage();
    }

    /**
     * Add current state to history for undo/redo functionality
     */
    addToHistory() {
        // Only add to history if different from the current state in history
        const currentState = this.historyIndex >= 0 ? this.filterHistory[this.historyIndex] : null;
        if (currentState && JSON.stringify(currentState) === JSON.stringify(this.currentFilters)) {
            return; // Don't add duplicate state
        }
        
        // Remove any future states if we're not at the end of history
        this.filterHistory = this.filterHistory.slice(0, this.historyIndex + 1);
        // Add the new state
        this.filterHistory.push(JSON.parse(JSON.stringify(this.currentFilters)));
        this.historyIndex = this.filterHistory.length - 1;
    }

    /**
     * Undo the last filter change
     */
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.currentFilters = JSON.parse(JSON.stringify(this.filterHistory[this.historyIndex]));
            this.saveCurrentState();
            this.notifyChangeListeners();
            return true;
        }
        return false;
    }

    /**
     * Redo the last undone filter change
     */
    redo() {
        if (this.historyIndex < this.filterHistory.length - 1) {
            this.historyIndex++;
            this.currentFilters = JSON.parse(JSON.stringify(this.filterHistory[this.historyIndex]));
            this.saveCurrentState();
            this.notifyChangeListeners();
            return true;
        }
        return false;
    }

    /**
     * Check if undo is possible
     */
    canUndo() {
        return this.historyIndex > 0;
    }

    /**
     * Check if redo is possible
     */
    canRedo() {
        return this.historyIndex < this.filterHistory.length - 1;
    }

    /**
     * Get all saved snapshots
     */
    getSnapshots() {
        return { ...this.filterSnapshots };
    }

    /**
     * Load user preferences from localStorage
     */
    loadUserPreferences() {
        try {
            const prefs = localStorage.getItem('cropFilterPreferences');
            return prefs ? JSON.parse(prefs) : {
                autoSave: true,
                saveToUrl: true,
                showHistory: true,
                defaultResultsPerPage: 10
            };
        } catch (e) {
            console.warn('Could not load user preferences:', e);
            return {};
        }
    }

    /**
     * Update user preferences
     */
    updateUserPreferences(newPrefs) {
        this.userPreferences = { ...this.userPreferences, ...newPrefs };
        localStorage.setItem('cropFilterPreferences', JSON.stringify(this.userPreferences));
    }

    /**
     * Generate a unique session ID
     */
    generateSessionId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Handle browser back/forward navigation
     */
    handlePopState(event) {
        if (event.state && event.state.filters) {
            this.currentFilters = event.state.filters;
            this.notifyChangeListeners();
        }
    }

    /**
     * Debounce filter updates to avoid excessive processing
     */
    debounce(key, func, delay = 300) {
        if (this.debounceTimers[key]) {
            clearTimeout(this.debounceTimers[key]);
        }
        this.debounceTimers[key] = setTimeout(() => {
            func();
            delete this.debounceTimers[key];
        }, delay);
    }

    /**
     * Throttle filter updates to limit frequency
     */
    throttle(key, func, delay = 500) {
        if (!this.debounceTimers[key]) {
            func();
            this.debounceTimers[key] = setTimeout(() => {
                delete this.debounceTimers[key];
            }, delay);
        }
    }
}

class CropFilteringManager {
    constructor() {
        this.currentResults = [];
        this.currentPage = 1;
        this.resultsPerPage = 10;
        this.charts = {};
        this.selectedComparisonCrops = [];
        this.filterStateManager = new FilterStateManager();
        this.init();
    }

    init() {
        this.loadFiltersFromUrl();
        this.loadFiltersFromLocalStorage();
        this.initializeHistoryState();
        this.bindEvents();
        this.loadFilterPresets();
        this.displayAppliedFilters();
        // Listen to state changes from the state manager
        this.filterStateManager.addChangeListener(this.handleFilterChange.bind(this));
    }

    handleFilterChange(filters) {
        this.currentFilters = filters;
        this.displayAppliedFilters();
    }

    loadFiltersFromUrl() {
        const loaded = this.filterStateManager.loadFiltersFromUrl();
        if (loaded) {
            this.currentFilters = this.filterStateManager.getFilters();
            this.setFiltersToUI(this.currentFilters);
        }
    }

    saveFiltersToUrl() {
        this.filterStateManager.saveFiltersToUrl();
    }

    loadFiltersFromLocalStorage() {
        const loaded = this.filterStateManager.loadFiltersFromLocalStorage();
        if (loaded) {
            this.currentFilters = this.filterStateManager.getFilters();
            // Only use saved filters if no filters were loaded from URL
            if (Object.keys(this.currentFilters).length === 0) {
                this.setFiltersToUI(this.currentFilters);
            }
        }
    }

    saveFiltersToLocalStorage() {
        this.filterStateManager.saveFiltersToLocalStorage();
    }

    setFiltersToUI(filters) {
        // Set climate filters
        if (filters.climate_zones) {
            const climateSelect = document.getElementById('climate-zones');
            Array.from(climateSelect.options).forEach(option => {
                option.selected = filters.climate_zones.includes(option.value);
            });
        }

        // Set growing season range
        if (filters.growing_season_range) {
            document.getElementById('growing-season-min').value = filters.growing_season_range.min;
            document.getElementById('growing-season-max').value = filters.growing_season_range.max;
            document.getElementById('growing-season-min-value').textContent = filters.growing_season_range.min;
            document.getElementById('growing-season-max-value').textContent = filters.growing_season_range.max;
        }

        // Set drought tolerance
        if (filters.drought_tolerance) {
            document.querySelectorAll('#drought-filters input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = filters.drought_tolerance.includes(checkbox.value);
            });
        }

        // Set soil pH range
        if (filters.soil_ph_range) {
            document.getElementById('ph-min').value = filters.soil_ph_range.min;
            document.getElementById('ph-max').value = filters.soil_ph_range.max;
            document.getElementById('ph-min-value').textContent = filters.soil_ph_range.min;
            document.getElementById('ph-max-value').textContent = filters.soil_ph_range.max;
        }

        // Set soil types
        if (filters.soil_types) {
            const soilSelect = document.getElementById('soil-types');
            Array.from(soilSelect.options).forEach(option => {
                option.selected = filters.soil_types.includes(option.value);
            });
        }

        // Set drainage classes
        if (filters.drainage_classes) {
            document.querySelectorAll('#soil-filters input[type="checkbox"]').forEach(checkbox => {
                if (checkbox.id !== 'drought-low' && checkbox.id !== 'drought-moderate' && 
                    checkbox.id !== 'drought-high' && checkbox.id !== 'drought-very-high') {
                    checkbox.checked = filters.drainage_classes.includes(checkbox.value);
                }
            });
        }

        // Set crop categories
        if (filters.crop_categories) {
            const categorySelect = document.getElementById('crop-categories');
            Array.from(categorySelect.options).forEach(option => {
                option.selected = filters.crop_categories.includes(option.value);
            });
        }

        // Set management complexity
        if (filters.management_complexity) {
            const radio = document.querySelector(`input[name="management-complexity"][value="${filters.management_complexity}"]`);
            if (radio) radio.checked = true;
        }

        // Set pest resistance
        if (filters.pest_resistance) {
            const pestSelect = document.getElementById('pest-resistance');
            Array.from(pestSelect.options).forEach(option => {
                option.selected = filters.pest_resistance.includes(option.value);
            });
        }

        // Set market class
        if (filters.market_class) {
            document.querySelectorAll('#market-filters input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = filters.market_class.includes(checkbox.value);
            });
        }

        // Set market stability
        if (filters.market_stability) {
            const radio = document.querySelector(`input[name="market-stability"][value="${filters.market_stability}"]`);
            if (radio) radio.checked = true;
        }
    }

    initializeHistoryState() {
        // Initial state
        this.filterStateManager.addToHistory();
        // Add browser back/forward support
        window.addEventListener('popstate', this.handlePopState.bind(this));
    }

    addToHistory(filters) {
        this.filterStateManager.addToHistory();
    }

    handlePopState(event) {
        if (event.state && event.state.filters) {
            this.filterStateManager.currentFilters = event.state.filters;
            this.currentFilters = event.state.filters;
            this.setFiltersToUI(this.currentFilters);
            this.applyFilters();
        }
    }

    pushStateToHistory() {
        const state = { filters: JSON.parse(JSON.stringify(this.currentFilters)) };
        const url = new URL(window.location);
        url.searchParams.set('filters', encodeURIComponent(JSON.stringify(this.currentFilters)));
        window.history.pushState(state, '', url);
    }

    addPresetManagement() {
        // Add preset buttons to the UI if they don't exist
        const filterSection = document.querySelector('.col-md-4');
        if (!document.getElementById('preset-controls')) {
            const presetControls = document.createElement('div');
            presetControls.id = 'preset-controls';
            presetControls.innerHTML = `
                <div class=\"mt-3\">
                    <div class=\"d-grid gap-2\">
                        <button id=\"save-preset-btn\" class=\"btn btn-outline-success btn-sm\">
                            <i class=\"fas fa-save\"></i> Save Preset
                        </button>
                        <button id=\"load-preset-btn\" class=\"btn btn-outline-info btn-sm\">
                            <i class=\"fas fa-folder-open\"></i> Load Preset
                        </button>
                        <button id=\"export-config-btn\" class=\"btn btn-outline-secondary btn-sm\">
                            <i class=\"fas fa-file-export\"></i> Export Config
                        </button>
                        <button id=\"import-config-btn\" class=\"btn btn-outline-secondary btn-sm\">
                            <i class=\"fas fa-file-import\"></i> Import Config
                        </button>
                        <button id=\"undo-btn\" class=\"btn btn-outline-warning btn-sm\" disabled>
                            <i class=\"fas fa-undo\"></i> Undo
                        </button>
                        <button id=\"redo-btn\" class=\"btn btn-outline-warning btn-sm\" disabled>
                            <i class=\"fas fa-redo\"></i> Redo
                        </button>
                        <button id=\"save-snapshot-btn\" class=\"btn btn-outline-primary btn-sm\">
                            <i class=\"fas fa-camera\"></i> Save Snapshot
                        </button>
                        <button id=\"load-snapshot-btn\" class=\"btn btn-outline-primary btn-sm\">
                            <i class=\"fas fa-history\"></i> Load Snapshot
                        </button>
                    </div>
                </div>
            `;
            filterSection.appendChild(presetControls);

            // Add event listeners for preset buttons
            document.getElementById('save-preset-btn').addEventListener('click', this.savePreset.bind(this));
            document.getElementById('load-preset-btn').addEventListener('click', this.loadPreset.bind(this));
            document.getElementById('export-config-btn').addEventListener('click', this.exportConfiguration.bind(this));
            document.getElementById('import-config-btn').addEventListener('click', this.importConfiguration.bind(this));
            document.getElementById('undo-btn').addEventListener('click', this.undoFilter.bind(this));
            document.getElementById('redo-btn').addEventListener('click', this.redoFilter.bind(this));
            document.getElementById('save-snapshot-btn').addEventListener('click', this.saveSnapshot.bind(this));
            document.getElementById('load-snapshot-btn').addEventListener('click', this.loadSnapshot.bind(this));
        }
    }

    handleKeyboardShortcuts(event) {
        // Ctrl+Z for undo
        if (event.ctrlKey && event.key === 'z' && !event.shiftKey) {
            event.preventDefault();
            this.undoFilter();
        }
        // Ctrl+Shift+Z or Ctrl+Y for redo
        else if ((event.ctrlKey && event.shiftKey && event.key === 'z') || (event.ctrlKey && event.key === 'y')) {
            event.preventDefault();
            this.redoFilter();
        }
    }

    savePreset() {
        const presetName = prompt('Enter a name for this filter preset:');
        if (presetName) {
            let presets = JSON.parse(localStorage.getItem('cropFilterPresets') || '{}');
            presets[presetName] = JSON.parse(JSON.stringify(this.filterStateManager.getFilters()));
            localStorage.setItem('cropFilterPresets', JSON.stringify(presets));
            alert('Filter preset "' + presetName + '" saved successfully!');
        }
    }

    loadPreset() {
        const presets = JSON.parse(localStorage.getItem('cropFilterPresets') || '{}');
        const presetNames = Object.keys(presets);
        
        if (presetNames.length === 0) {
            alert('No filter presets found. Please save a preset first.');
            return;
        }

        const presetName = prompt(`Select a preset to load:\n${presetNames.join('\n')}\n\nEnter preset name:`);
        if (presetName && presets[presetName]) {
            this.filterStateManager.currentFilters = JSON.parse(JSON.stringify(presets[presetName]));
            this.currentFilters = JSON.parse(JSON.stringify(presets[presetName]));
            this.setFiltersToUI(this.currentFilters);
            this.applyFilters();
            alert('Filter preset "' + presetName + '" loaded successfully!');
        } else if (presetName) {
            alert(`Preset \"${presetName}\" not found.`);
        }
    }

    saveSnapshot() {
        const snapshotName = prompt('Enter a name for this filter snapshot:');
        if (snapshotName) {
            this.filterStateManager.saveFilterSnapshot(snapshotName, 'Manually saved snapshot');
            alert(`Filter snapshot \"${snapshotName}\" saved successfully!`);
        }
    }

    loadSnapshot() {
        const snapshots = this.filterStateManager.getSnapshots();
        const snapshotNames = Object.keys(snapshots);
        
        if (snapshotNames.length === 0) {
            alert('No filter snapshots found. Please save a snapshot first.');
            return;
        }

        const snapshotName = prompt(`Select a snapshot to load:\n${snapshotNames.join('\n')}\n\nEnter snapshot name:`);
        if (snapshotName && snapshots[snapshotName]) {
            if (this.filterStateManager.loadFilterSnapshot(snapshotName)) {
                this.currentFilters = this.filterStateManager.getFilters();
                this.setFiltersToUI(this.currentFilters);
                this.applyFilters();
                alert(`Filter snapshot \"${snapshotName}\" loaded successfully!`);
            } else {
                alert(`Snapshot \"${snapshotName}\" could not be loaded.`);
            }
        } else if (snapshotName) {
            alert(`Snapshot \"${snapshotName}\" not found.`);
        }
    }

    exportConfiguration() {
        const config = {
            filters: JSON.parse(JSON.stringify(this.currentFilters)),
            timestamp: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(config, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportFileDefaultName = `crop-filter-config-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        
        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    }

    importConfiguration() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = (event) => {
            const file = event.target.files[0];
            const reader = new FileReader();
            
            reader.onload = (readerEvent) => {
                try {
                    const config = JSON.parse(readerEvent.target.result);
                    if (config.filters) {
                        this.currentFilters = JSON.parse(JSON.stringify(config.filters));
                        this.setFiltersToUI(this.currentFilters);
                        this.applyFilters();
                        alert('Filter configuration imported successfully!');
                    } else {
                        alert('Invalid configuration file format.');
                    }
                } catch (e) {
                    alert('Error parsing configuration file: ' + e.message);
                }
            };
            
            reader.readAsText(file);
        };
        
        input.click();
    }

    undoFilter() {
        if (this.filterStateManager.canUndo()) {
            this.filterStateManager.undo();
            this.currentFilters = this.filterStateManager.getFilters();
            this.setFiltersToUI(this.currentFilters);
            this.applyFilters();
            this.updateHistoryButtons();
        }
    }

    redoFilter() {
        if (this.filterStateManager.canRedo()) {
            this.filterStateManager.redo();
            this.currentFilters = this.filterStateManager.getFilters();
            this.setFiltersToUI(this.currentFilters);
            this.applyFilters();
            this.updateHistoryButtons();
        }
    }

    updateHistoryButtons() {
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');
        
        if (undoBtn) {
            undoBtn.disabled = !this.filterStateManager.canUndo();
        }
        
        if (redoBtn) {
            redoBtn.disabled = !this.filterStateManager.canRedo();
        }
    }

    bindEvents() {
        // Filter section toggle
        document.querySelectorAll('.filter-header').forEach(header => {
            header.addEventListener('click', this.toggleFilterSection.bind(this));
        });

        // Range slider updates - also update filters when changed
        document.querySelectorAll('.range-slider').forEach(slider => {
            slider.addEventListener('input', this.updateSliderValue.bind(this));
            slider.addEventListener('change', () => {
                // Update the state manager's filters
                const newFilters = this.getFiltersFromUI();
                this.filterStateManager.currentFilters = newFilters;
                this.filterStateManager.saveCurrentState();
            });
        });

        // Listen for all filter changes to update the state manager
        this.addFilterChangeListeners();
        
        // Apply filters button
        document.getElementById('apply-filters').addEventListener('click', this.applyFilters.bind(this));

        // Clear all filters
        document.getElementById('clear-all-filters').addEventListener('click', this.clearAllFilters.bind(this));

        // Reset filters
        document.getElementById('reset-filters').addEventListener('click', this.resetFilters.bind(this));

        // Sort options change
        document.getElementById('sort-options').addEventListener('change', this.applyFilters.bind(this));

        // Filter validation
        setInterval(this.validateFilters.bind(this), 5000); // Validate every 5 seconds
        
        // Visualization tab events
        document.getElementById('visualization-tab').addEventListener('shown.bs.tab', this.renderVisualizations.bind(this));
        
        // Comparison tab events
        document.getElementById('comparison-tab').addEventListener('shown.bs.tab', this.setupComparisonTab.bind(this));
        
        // Crop comparison events
        document.getElementById('compare-selected-btn').addEventListener('click', this.compareSelectedCrops.bind(this));
        
        // Export buttons
        document.getElementById('export-results-btn').addEventListener('click', this.exportResults.bind(this));
        document.getElementById('export-chart-btn').addEventListener('click', this.exportChartAsImage.bind(this));
        
        // Enhanced export chart buttons
        document.querySelectorAll('.export-chart-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const chartId = e.target.dataset.chart;
                this.exportChartAsImageById(chartId);
            });
        });
        
        // Download data buttons
        document.querySelectorAll('.download-data-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const dataType = e.target.dataset.type;
                this.exportResultsByType(dataType);
            });
        });
        
        // Add undo/redo functionality
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
        
        // Add preset management buttons if they exist
        this.addPresetManagement();
        
        // Add quick filter button event listeners
        this.addQuickFilterEventListeners();
    }
    
    addQuickFilterEventListeners() {\n        // Add event listeners to quick filter buttons if they exist\n        document.querySelectorAll('[data-quick-filter]').forEach(btn => {\n            btn.addEventListener('click', (event) => {\n                const filterType = event.target.getAttribute('data-quick-filter') || \n                                  event.target.closest('[data-quick-filter]').getAttribute('data-quick-filter');\n                this.applyQuickFilter(filterType);\n            });\n        });\n        \n        // Add event listeners for smart action buttons\n        const voiceSearchBtn = document.getElementById('voice-search-btn');\n        if (voiceSearchBtn) {\n            voiceSearchBtn.addEventListener('click', this.handleVoiceSearch.bind(this));\n        }\n        \n        const currentLocationBtn = document.getElementById('current-location-btn');\n        if (currentLocationBtn) {\n            currentLocationBtn.addEventListener('click', this.handleCurrentLocation.bind(this));\n        }\n        \n        const cameraScanBtn = document.getElementById('camera-scan-btn');\n        if (cameraScanBtn) {\n            cameraScanBtn.addEventListener('click', this.handleCameraScan.bind(this));\n        }\n        \n        const weatherIntegrationBtn = document.getElementById('weather-integration-btn');\n        if (weatherIntegrationBtn) {\n            weatherIntegrationBtn.addEventListener('click', this.handleWeatherIntegration.bind(this));\n        }\n    }\n    \n    // Handle voice search functionality\n    handleVoiceSearch() {\n        if ('speechRecognition' in window || 'webkitSpeechRecognition' in window) {\n            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;\n            const recognition = new SpeechRecognition();\n            \n            recognition.continuous = false;\n            recognition.interimResults = false;\n            recognition.lang = 'en-US';\n            \n            recognition.start();\n            \n            recognition.onresult = (event) => {\n                const transcript = event.results[0][0].transcript.toLowerCase();\n                console.log('Voice command:', transcript);\n                \n                // Process voice command to apply filters\n                this.processVoiceCommand(transcript);\n            };\n            \n            recognition.onerror = (event) => {\n                console.error('Voice recognition error:', event.error);\n                alert('Could not recognize your voice command. Please try typing your filters instead.');\n            };\n        } else {\n            // Fallback for browsers that don't support speech recognition\n            const voiceCommand = prompt('Enter your voice command (e.g., \"drought tolerant crops\", \"low maintenance crops\"):');\n            if (voiceCommand) {\n                this.processVoiceCommand(voiceCommand.toLowerCase());\n            }\n        }\n    }\n    \n    // Process voice commands to apply corresponding filters\n    processVoiceCommand(command) {\n        // Simple keyword matching for demonstration purposes\n        if (command.includes('drought') || command.includes('dry')) {\n            this.applyQuickFilter('drought');\n        } else if (command.includes('nitrogen') || command.includes('fixing')) {\n            this.applyQuickFilter('nitrogen');\n        } else if (command.includes('low') && command.includes('maint')) {\n            this.applyQuickFilter('low-maintenance');\n        } else if (command.includes('high') && command.includes('yield')) {\n            this.applyQuickFilter('high-yield');\n        } else if (command.includes('organic')) {\n            this.applyQuickFilter('organic');\n        } else if (command.includes('cover') && command.includes('crop')) {\n            this.applyQuickFilter('cover-crop');\n        } else if (command.includes('early')) {\n            this.applyQuickFilter('early-season');\n        } else if (command.includes('late')) {\n            this.applyQuickFilter('late-season');\n        } else if (command.includes('disease')) {\n            this.applyQuickFilter('disease-resistant');\n        } else if (command.includes('pest')) {\n            this.applyQuickFilter('pest-resistant');\n        } else {\n            alert(`Unrecognized voice command: ${command}. Try phrases like \"drought tolerant crops\" or \"low maintenance\".`);\n        }\n    }\n    \n    // Handle getting current location to set climate filters\n    handleCurrentLocation() {\n        if (navigator.geolocation) {\n            navigator.geolocation.getCurrentPosition(\n                (position) => {\n                    const { latitude, longitude } = position.coords;\n                    \n                    // In a real app, we would call an API to get climate zone for these coordinates\n                    // For this demo, we'll just show an alert\n                    alert(`Location detected: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}\\nIn a real app, this would auto-set climate filters based on your location.`);\n                    \n                    // Example: Set climate zone based on location (would require API in real app)\n                    // this.setClimateZoneFromLocation(latitude, longitude);\n                },\n                (error) => {\n                    console.error('Error getting location:', error);\n                    alert('Could not get your location. Please make sure location services are enabled.');\n                }\n            );\n        } else {\n            alert('Geolocation is not supported by your browser. Please enable location services.');\n        }\n    }\n    \n    // Handle camera scan functionality (placeholder)\n    handleCameraScan() {\n        alert('Camera scan functionality would open device camera to scan QR codes or barcodes for crop information. This would require camera API access in a real implementation.');\n    }\n    \n    // Handle weather-based filters (placeholder)\n    handleWeatherIntegration() {\n        alert('Weather-based filtering would integrate with current weather conditions to suggest appropriate crops. In a real app, this would connect to weather APIs.');\n    }\n
    
    addFilterChangeListeners() {
        // Add change listeners to all filter elements to trigger auto-save
        const filterElements = [
            ...document.querySelectorAll('select[multiple]'),
            ...document.querySelectorAll('input[type="checkbox"]'),
            ...document.querySelectorAll('input[type="radio"]')
        ];
        
        filterElements.forEach(element => {
            element.addEventListener('change', () => {
                // Update the current filters without applying them
                const newFilters = this.getFiltersFromUI();
                if (JSON.stringify(newFilters) !== JSON.stringify(this.filterStateManager.getFilters())) {
                    this.filterStateManager.addToHistory(); // Save current state before updating
                    this.filterStateManager.currentFilters = newFilters;
                    this.filterStateManager.saveCurrentState();
                    this.updateHistoryButtons();
                }
            });
        });
    }

    toggleFilterSection(event) {
        const filterSection = event.currentTarget.nextElementSibling;
        const icon = event.currentTarget.querySelector('.fa-chevron-down');
        
        if (filterSection.style.display === 'none') {
            filterSection.style.display = 'block';
            icon.style.transform = 'rotate(180deg)';
        } else {
            filterSection.style.display = 'none';
            icon.style.transform = 'rotate(0deg)';
        }
    }

    updateSliderValue(event) {
        const slider = event.target;
        const value = slider.value;
        const valueElement = document.getElementById(`${slider.id}-value`);
        
        if (valueElement) {
            valueElement.textContent = value;
        }
        
        // Update max slider to not go below min slider
        if (slider.id === 'ph-min') {
            const maxSlider = document.getElementById('ph-max');
            if (maxSlider && parseFloat(value) > parseFloat(maxSlider.value)) {
                maxSlider.value = parseFloat(value);
                document.getElementById('ph-max-value').textContent = parseFloat(value);
            }
        } else if (slider.id === 'ph-max') {
            const minSlider = document.getElementById('ph-min');
            if (minSlider && parseFloat(value) < parseFloat(minSlider.value)) {
                minSlider.value = parseFloat(value);
                document.getElementById('ph-min-value').textContent = parseFloat(value);
            }
        } else if (slider.id === 'growing-season-min') {
            const maxSlider = document.getElementById('growing-season-max');
            if (maxSlider && parseInt(value) > parseInt(maxSlider.value)) {
                maxSlider.value = parseInt(value);
                document.getElementById('growing-season-max-value').textContent = parseInt(value);
            }
        } else if (slider.id === 'growing-season-max') {
            const minSlider = document.getElementById('growing-season-min');
            if (minSlider && parseInt(value) < parseInt(minSlider.value)) {
                minSlider.value = parseInt(value);
                document.getElementById('growing-season-min-value').textContent = parseInt(value);
            }
        }
        
        // Update filters when slider changes
        const newFilters = this.getFiltersFromUI();
        if (JSON.stringify(newFilters) !== JSON.stringify(this.filterStateManager.getFilters())) {
            this.filterStateManager.addToHistory(); // Save current state before updating
            this.filterStateManager.currentFilters = newFilters;
            this.filterStateManager.saveCurrentState();
            this.updateHistoryButtons();
        }
    }

    getFiltersFromUI() {
        const filters = {};

        // Climate filters
        const climateZones = Array.from(document.getElementById('climate-zones').selectedOptions).map(option => option.value);
        if (climateZones.length > 0) {
            filters.climate_zones = climateZones;
        }

        filters.growing_season_range = {
            min: parseInt(document.getElementById('growing-season-min').value),
            max: parseInt(document.getElementById('growing-season-max').value)
        };

        const droughtTolerance = Array.from(document.querySelectorAll('#drought-filters input[type="checkbox"]:checked')).map(checkbox => checkbox.value);
        if (droughtTolerance.length > 0) {
            filters.drought_tolerance = droughtTolerance;
        }

        // Soil filters
        filters.soil_ph_range = {
            min: parseFloat(document.getElementById('ph-min').value),
            max: parseFloat(document.getElementById('ph-max').value)
        };

        const soilTypes = Array.from(document.getElementById('soil-types').selectedOptions).map(option => option.value);
        if (soilTypes.length > 0) {
            filters.soil_types = soilTypes;
        }

        const drainageClasses = Array.from(document.querySelectorAll('#soil-filters input[type="checkbox"]:checked')).map(checkbox => checkbox.value);
        if (drainageClasses.length > 0) {
            filters.drainage_classes = drainageClasses;
        }

        // Agricultural filters
        const cropCategories = Array.from(document.getElementById('crop-categories').selectedOptions).map(option => option.value);
        if (cropCategories.length > 0) {
            filters.crop_categories = cropCategories;
        }

        const managementComplexity = document.querySelector('input[name="management-complexity"]:checked');
        if (managementComplexity) {
            filters.management_complexity = managementComplexity.value;
        }

        const pestResistance = Array.from(document.getElementById('pest-resistance').selectedOptions).map(option => option.value);
        if (pestResistance.length > 0) {
            filters.pest_resistance = pestResistance;
        }

        // Market filters
        const marketClass = Array.from(document.querySelectorAll('#market-filters input[type="checkbox"]:checked')).map(checkbox => checkbox.value);
        if (marketClass.length > 0) {
            filters.market_class = marketClass;
        }

        const marketStability = document.querySelector('input[name="market-stability"]:checked');
        if (marketStability) {
            filters.market_stability = marketStability.value;
        }

        return filters;
    }

    async applyFilters() {
        const filters = this.getFiltersFromUI();
        this.filterStateManager.currentFilters = filters;
        this.currentFilters = filters;

        // Add to filter history for undo/redo functionality
        this.filterStateManager.addToHistory();
        this.updateHistoryButtons();

        // Save to all persistent stores
        this.filterStateManager.saveCurrentState();

        // Show loading indicator
        document.getElementById('loading-indicator').classList.remove('d-none');
        document.getElementById('crop-results-list').innerHTML = '';
        document.getElementById('no-results-message').classList.add('d-none');
        document.getElementById('pagination-container').innerHTML = '';

        try {
            // Validate filters first
            const validation = await this.validateFilters();
            if (!validation.isValid) {
                this.showValidationAlert(validation.messages);
            } else {
                document.getElementById('filter-validation-alert').classList.add('d-none');
            }

            // In a real application, this would be an API call
            // For now, we'll simulate the API call
            const results = await this.simulateCropSearch(filters);
            
            this.currentResults = results;
            this.currentPage = 1;
            this.displayResults();
            // Update visualization if the visualization tab is active
            if (document.querySelector('#visualization-panel').classList.contains('active')) {
                this.renderVisualizations();
            }
            
        } catch (error) {
            console.error('Error applying filters:', error);
            this.showError('Error applying filters. Please try again.');
        } finally {
            document.getElementById('loading-indicator').classList.add('d-none');
        }
        
        this.displayAppliedFilters();
    }

    async validateFilters() {
        const filters = this.currentFilters || this.getFiltersFromUI();
        const messages = [];
        let isValid = true;

        // Check for incompatible climate and growth season combinations
        if (filters.climate_zones && filters.growing_season_range) {
            const northernZones = ['1a', '1b', '2a', '2b', '3a', '3b'];
            const hasNorthernZones = filters.climate_zones.some(zone => northernZones.includes(zone));
            const longSeason = filters.growing_season_range.min > 120;

            if (hasNorthernZones && longSeason) {
                messages.push('Long growing season crops may not mature in northern climate zones');
            }
        }

        // Check pH range validity
        if (filters.soil_ph_range && filters.soil_ph_range.min > filters.soil_ph_range.max) {
            messages.push('Minimum pH cannot be greater than maximum pH');
            isValid = false;
        }

        // Check extreme pH values
        if (filters.soil_ph_range && (filters.soil_ph_range.min < 4.0 || filters.soil_ph_range.max > 9.0)) {
            messages.push('Extreme pH values may limit crop options significantly');
        }

        // Return validation result
        return {
            isValid: isValid,
            messages: messages
        };
    }

    showValidationAlert(messages) {
        const alertElement = document.getElementById('filter-validation-alert');
        const messagesList = document.getElementById('validation-messages');
        
        messagesList.innerHTML = '';
        messages.forEach(msg => {
            const li = document.createElement('li');
            li.textContent = msg;
            messagesList.appendChild(li);
        });
        
        alertElement.classList.remove('d-none');
    }

    async simulateCropSearch(filters) {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 800));

        // For demo purposes, return mock data based on filters
        const mockCrops = [
            {
                id: 'crop-1',
                name: 'Winter Wheat',
                scientific_name: 'Triticum aestivum',
                category: 'grain_crops',
                suitability_score: 0.92,
                description: 'Excellent winter-hardy grain crop with high yield potential.',
                climate_zones: ['3a', '3b', '4a', '4b', '5a', '5b'],
                ph_range: {min: 5.5, max: 7.5},
                maturity_days: 220,
                drought_tolerance: 'moderate',
                management_complexity: 'moderate',
                tags: ['grain', 'winter_crop', 'nitrogen_fixing', 'erosion_control']
            },
            {
                id: 'crop-2',
                name: 'Soybean',
                scientific_name: 'Glycine max',
                category: 'legume_crops',
                suitability_score: 0.88,
                description: 'Nitrogen-fixing legume crop with excellent protein content.',
                climate_zones: ['5a', '5b', '6a', '6b', '7a', '7b'],
                ph_range: {min: 6.0, max: 7.0},
                maturity_days: 100,
                drought_tolerance: 'moderate',
                management_complexity: 'moderate',
                tags: ['nitrogen_fixing', 'organic', 'rotation_crop', 'cover_crop']
            },
            {
                id: 'crop-3',
                name: 'Crimson Clover',
                scientific_name: 'Trifolium incarnatum',
                category: 'cover_crops',
                suitability_score: 0.95,
                description: 'Popular winter annual cover crop for nitrogen fixation.',
                climate_zones: ['6a', '6b', '7a', '7b', '8a', '8b'],
                ph_range: {min: 6.0, max: 7.0},
                maturity_days: 240,
                drought_tolerance: 'low',
                management_complexity: 'low',
                tags: ['nitrogen_fixing', 'erosion_control', 'pollinator_support', 'organic']
            },
            {
                id: 'crop-4',
                name: 'Corn',
                scientific_name: 'Zea mays',
                category: 'grain_crops',
                suitability_score: 0.85,
                description: 'High-yielding cereal grain with significant nitrogen requirements.',
                climate_zones: ['4a', '4b', '5a', '5b', '6a', '6b'],
                ph_range: {min: 5.8, max: 7.0},
                maturity_days: 120,
                drought_tolerance: 'low',
                management_complexity: 'high',
                tags: ['high_yield', 'nitrogen_hungry', 'rotation_crop', 'feed_crop']
            },
            {
                id: 'crop-5',
                name: 'Alfalfa',
                scientific_name: 'Medicago sativa',
                category: 'forage_crops',
                suitability_score: 0.82,
                description: 'Perennial legume for high-quality forage and soil improvement.',
                climate_zones: ['3a', '3b', '4a', '4b', '5a', '5b'],
                ph_range: {min: 6.5, max: 7.5},
                maturity_days: 365,
                drought_tolerance: 'moderate',
                management_complexity: 'high',
                tags: ['perennial', 'nitrogen_fixing', 'drought_tolerant', 'forage']
            }
        ];

        // Filter mock crops based on applied filters
        let filteredCrops = [...mockCrops];

        if (filters.crop_categories && filters.crop_categories.length > 0) {
            filteredCrops = filteredCrops.filter(crop => 
                filters.crop_categories.includes(crop.category));
        }

        if (filters.drought_tolerance && filters.drought_tolerance.length > 0) {
            filteredCrops = filteredCrops.filter(crop => 
                filters.drought_tolerance.includes(crop.drought_tolerance));
        }

        if (filters.management_complexity) {
            filteredCrops = filteredCrops.filter(crop => 
                crop.management_complexity === filters.management_complexity);
        }

        if (filters.soil_ph_range) {
            filteredCrops = filteredCrops.filter(crop => 
                crop.ph_range.min >= filters.soil_ph_range.min && 
                crop.ph_range.max <= filters.soil_ph_range.max);
        }

        if (filters.growing_season_range) {
            filteredCrops = filteredCrops.filter(crop => 
                crop.maturity_days >= filters.growing_season_range.min && 
                crop.maturity_days <= filters.growing_season_range.max);
        }

        if (filters.climate_zones && filters.climate_zones.length > 0) {
            filteredCrops = filteredCrops.filter(crop => 
                crop.climate_zones.some(zone => filters.climate_zones.includes(zone)));
        }

        // Sort by suitability score by default
        const sortField = document.getElementById('sort-options').value;
        if (sortField === 'suitability_score') {
            filteredCrops.sort((a, b) => b.suitability_score - a.suitability_score);
        } else if (sortField === 'name') {
            filteredCrops.sort((a, b) => a.name.localeCompare(b.name));
        } else if (sortField === 'popularity') {
            // Mock popularity sort (in real app this would come from data)
            filteredCrops.sort((a, b) => b.suitability_score - a.suitability_score);
        }

        return filteredCrops;
    }

    displayResults() {
        const container = document.getElementById('crop-results-list');
        const resultsCount = document.getElementById('results-count');
        const noResultsMessage = document.getElementById('no-results-message');
        const paginationContainer = document.getElementById('pagination-container');

        if (this.currentResults.length === 0) {
            noResultsMessage.classList.remove('d-none');
            container.innerHTML = '';
            resultsCount.textContent = '0';
            paginationContainer.innerHTML = '';
            // Update visualization tabs to show no data message
            this.showNoDataMessage();
            return;
        }

        noResultsMessage.classList.add('d-none');
        resultsCount.textContent = this.currentResults.length;

        // Calculate pagination
        const totalPages = Math.ceil(this.currentResults.length / this.resultsPerPage);
        const startIndex = (this.currentPage - 1) * this.resultsPerPage;
        const endIndex = Math.min(startIndex + this.resultsPerPage, this.currentResults.length);
        const resultsToShow = this.currentResults.slice(startIndex, endIndex);

        // Display results
        container.innerHTML = '';
        resultsToShow.forEach(crop => {
            const cropElement = this.createCropCard(crop);
            container.appendChild(cropElement);
        });

        // Create pagination
        this.createPagination(totalPages);
        
        // Update visualization tabs if they are currently active
        const activeTab = document.querySelector('.tab-pane.active');
        if (activeTab.id === 'visualization-panel') {
            this.renderVisualizations();
        }
    }

    createCropCard(crop) {
        const card = document.createElement('div');
        card.className = 'result-card fade-in';

        card.innerHTML = `
            <div class="result-header">
                <div>
                    <h4>${crop.name} <small class="text-muted">(${crop.scientific_name})</small></h4>
                    <span class="badge bg-primary">${crop.category.replace('_', ' ')}</span>
                </div>
                <div class="result-score">${(crop.suitability_score * 100).toFixed(0)}%</div>
            </div>
            
            <p>${crop.description}</p>
            
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-thermometer-half"></i> Climate</h6>
                    <p class="mb-1">Hardiness Zones: ${crop.climate_zones.join(', ')}</p>
                    <p class="mb-1">Maturity: ${crop.maturity_days} days</p>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-vial"></i> Soil Requirements</h6>
                    <p class="mb-1">pH: ${crop.ph_range.min} - ${crop.ph_range.max}</p>
                    <p class="mb-1">Drought Tolerance: ${crop.drought_tolerance}</p>
                </div>
            </div>
            
            <div class="mt-2">
                ${crop.tags.map(tag => `<span class="tag">${tag.replace('_', ' ')}</span>`).join('')}
            </div>
            
            <div class="mt-3">
                <button class="btn btn-sm btn-outline-primary" onclick="cropFilteringManager.viewCropDetails('${crop.id}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="cropFilteringManager.addCropToPlan('${crop.id}')">
                    <i class="fas fa-plus"></i> Add to Plan
                </button>
            </div>
        `;

        return card;
    }

    createPagination(totalPages) {
        const paginationContainer = document.getElementById('pagination-container');
        paginationContainer.innerHTML = '';

        if (totalPages <= 1) return;

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" onclick="cropFilteringManager.goToPage(${this.currentPage - 1})">Previous</a>`;
        paginationContainer.appendChild(prevLi);

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#" onclick="cropFilteringManager.goToPage(${i})">${i}</a>`;
            paginationContainer.appendChild(pageLi);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" onclick="cropFilteringManager.goToPage(${this.currentPage + 1})">Next</a>`;
        paginationContainer.appendChild(nextLi);
    }

    goToPage(page) {
        if (page < 1 || page > Math.ceil(this.currentResults.length / this.resultsPerPage)) return;
        
        this.currentPage = page;
        this.displayResults();
        
        // Scroll to top of results
        document.getElementById('crop-results-list').scrollIntoView({ behavior: 'smooth' });
    }

    displayAppliedFilters() {
        const filtersContainer = document.getElementById('applied-filters-list');
        filtersContainer.innerHTML = '';

        const filters = this.filterStateManager.getFilters();
        if (!filters || Object.keys(filters).length === 0) {
            filtersContainer.innerHTML = '<p class="text-muted">No filters applied</p>';
            return;
        }

        for (const [key, value] of Object.entries(filters)) {
            if (value && (Array.isArray(value) ? value.length > 0 : true)) {
                const filterPreview = document.createElement('div');
                filterPreview.className = 'filter-preview';
                
                let label = key.replace('_', ' ');
                let displayValue = value;

                if (Array.isArray(value)) {
                    displayValue = value.join(', ');
                } else if (typeof value === 'object') {
                    displayValue = JSON.stringify(value);
                }

                filterPreview.textContent = `${label}: ${displayValue}`;
                filtersContainer.appendChild(filterPreview);
            }
        }
    }

    clearAllFilters() {
        // Reset all filter UI elements
        document.querySelectorAll('select[multiple]').forEach(select => {
            Array.from(select.options).forEach(option => option.selected = false);
        });

        document.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(input => {
            input.checked = false;
        });

        // Reset sliders to defaults
        document.getElementById('growing-season-min').value = 60;
        document.getElementById('growing-season-max').value = 150;
        document.getElementById('ph-min').value = 5.5;
        document.getElementById('ph-max').value = 7.5;

        // Update slider value displays
        document.getElementById('growing-season-min-value').textContent = '60';
        document.getElementById('growing-season-max-value').textContent = '150';
        document.getElementById('ph-min-value').textContent = '5.5';
        document.getElementById('ph-max-value').textContent = '7.5';

        // Clear filters using state manager
        this.filterStateManager.clearFilters();
        this.currentFilters = this.filterStateManager.getFilters();
        this.currentResults = [];
        this.currentPage = 1;

        // Add to filter history for undo/redo functionality
        this.filterStateManager.addToHistory();
        this.updateHistoryButtons();

        // Save to all persistent stores
        this.filterStateManager.saveCurrentState();

        // Update UI
        this.displayAppliedFilters();
        document.getElementById('crop-results-list').innerHTML = '';
        document.getElementById('results-count').textContent = '0';
        document.getElementById('pagination-container').innerHTML = '';
        document.getElementById('no-results-message').classList.add('d-none');
        document.getElementById('filter-validation-alert').classList.add('d-none');
    }

    resetFilters() {
        this.clearAllFilters();
    }

    async loadFilterPresets() {
        // In a real app, this would load saved filter presets from the server
        // For now, we'll just initialize with any existing data
        console.log('Loading filter presets...');
    }

    renderVisualizations() {
        if (!this.currentResults || this.currentResults.length === 0) {
            this.showNoDataMessage();
            return;
        }
        
        // Update summary cards
        this.updateSummaryCards();
        
        // Render all charts
        this.renderFilterImpactChart();
        this.renderCategoryDistributionChart();
        this.renderDroughtToleranceChart();
        this.renderYieldPotentialChart();
        this.renderCostAnalysisChart();
        this.renderGeographicDistributionChart();
        this.renderSeasonalTrendChart();
        this.renderSuitabilityDistributionChart();
        this.renderManagementComplexityChart();
    }

    renderFilterImpactChart() {
        const ctx = document.getElementById('filterImpactChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.filterImpactChart) {
            this.charts.filterImpactChart.destroy();
        }

        // Create data for the chart based on the current filters
        const filterCount = Object.keys(this.currentFilters).length;
        const resultCount = this.currentResults.length;
        
        // Calculate the impact of different filter types
        const filterTypes = [];
        const filterValues = [];
        
        for (const [key, value] of Object.entries(this.currentFilters)) {
            if (value && (Array.isArray(value) ? value.length > 0 : true)) {
                filterTypes.push(key);
                if (Array.isArray(value)) {
                    filterValues.push(value.length);
                } else if (typeof value === 'object') {
                    filterValues.push(1); // For range objects
                } else {
                    filterValues.push(1);
                }
            }
        }

        this.charts.filterImpactChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: filterTypes.map(f => f.replace('_', ' ').toUpperCase()),
                datasets: [{
                    label: 'Number of Filter Values Applied',
                    data: filterValues,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Filter Impact Analysis'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Values'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Filter Types'
                        }
                    }
                }
            }
        });
    }

    renderCategoryDistributionChart() {
        const ctx = document.getElementById('categoryDistributionChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.categoryChart) {
            this.charts.categoryChart.destroy();
        }

        // Count crop categories
        const categoryCounts = {};
        this.currentResults.forEach(crop => {
            if (categoryCounts[crop.category]) {
                categoryCounts[crop.category]++;
            } else {
                categoryCounts[crop.category] = 1;
            }
        });

        const labels = Object.keys(categoryCounts).map(cat => cat.replace('_', ' '));
        const data = Object.values(categoryCounts);

        this.charts.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Crop Categories',
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)',
                        'rgba(255, 159, 64, 0.8)',
                        'rgba(199, 199, 199, 0.8)',
                        'rgba(83, 102, 255, 0.8)',
                        'rgba(255, 99, 255, 0.8)',
                        'rgba(99, 255, 132, 0.8)',
                        'rgba(255, 206, 100, 0.8)',
                        'rgba(75, 255, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Crop Category Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderDroughtToleranceChart() {
        const ctx = document.getElementById('droughtToleranceChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.droughtChart) {
            this.charts.droughtChart.destroy();
        }

        // Count drought tolerance levels
        const toleranceCounts = {};
        this.currentResults.forEach(crop => {
            if (toleranceCounts[crop.drought_tolerance]) {
                toleranceCounts[crop.drought_tolerance]++;
            } else {
                toleranceCounts[crop.drought_tolerance] = 1;
            }
        });

        const labels = Object.keys(toleranceCounts).map(tol => tol.replace('_', ' '));
        const data = Object.values(toleranceCounts);

        this.charts.droughtChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Drought Tolerance Levels',
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Drought Tolerance Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    showNoDataMessage() {
        // Show no data message in visualization area
        if (document.getElementById('filterImpactChart')) {
            document.getElementById('filterImpactChart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        if (document.getElementById('categoryDistributionChart')) {
            document.getElementById('categoryDistributionChart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        if (document.getElementById('droughtToleranceChart')) {
            document.getElementById('droughtToleranceChart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        if (document.getElementById('yield-potential-chart')) {
            document.getElementById('yield-potential-chart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        if (document.getElementById('cost-analysis-chart')) {
            document.getElementById('cost-analysis-chart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        if (document.getElementById('geographic-distribution-chart')) {
            document.getElementById('geographic-distribution-chart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        if (document.getElementById('seasonal-trend-chart')) {
            document.getElementById('seasonal-trend-chart').getContext('2d').clearRect(0, 0, 400, 200);
        }
        
        // Display a message on the visualization panel
        document.querySelector('#visualization-panel .card-body').innerHTML = 
            `<div class="text-center p-4">
                <i class="fas fa-chart-bar fa-3x text-muted"></i>
                <h5 class="mt-3">No Data to Visualize</h5>
                <p class="text-muted">Apply filters to see results and visualizations</p>
            </div>`;
    }

    setupComparisonTab() {
        // Populate the crop comparison select with current results
        const selectElement = document.getElementById('crop-comparison-select');
        selectElement.innerHTML = '';
        
        if (!this.currentResults || this.currentResults.length === 0) {
            const option = document.createElement('option');
            option.disabled = true;
            option.textContent = 'No crops available for comparison';
            selectElement.appendChild(option);
            return;
        }
        
        this.currentResults.forEach(crop => {
            const option = document.createElement('option');
            option.value = crop.id;
            option.textContent = crop.name;
            selectElement.appendChild(option);
        });
    }

    compareSelectedCrops() {
        const selectedCropIds = Array.from(document.getElementById('crop-comparison-select').selectedOptions)
            .map(option => option.value);
            
        if (selectedCropIds.length < 2) {
            alert('Please select at least 2 crops for comparison');
            return;
        }
        
        if (selectedCropIds.length > 3) {
            alert('Please select no more than 3 crops for comparison');
            return;
        }
        
        // Find the selected crops in current results
        const selectedCrops = this.currentResults.filter(crop => 
            selectedCropIds.includes(crop.id));
        
        this.renderComparisonCharts(selectedCrops);
    }

    renderComparisonCharts(crops) {
        const container = document.getElementById('comparison-results');
        container.innerHTML = '';

        // Create a comparison card with multiple charts
        const comparisonCard = document.createElement('div');
        comparisonCard.className = 'card mb-4';
        comparisonCard.innerHTML = `
            <div class="card-header">
                <h5><i class="fas fa-balance-scale"></i> Crop Comparison Results</h5>
            </div>
            <div class="card-body">
                <h6>Selected Crops: ${crops.map(c => c.name).join(' vs ')}</h6>
                <div class="row">
                    <div class="col-md-12">
                        <canvas id="comparison-chart-suitability" width="400" height="200"></canvas>
                    </div>
                </div>
                <div class="row mt-4">
                    <div class="col-md-6">
                        <canvas id="comparison-chart-ph" width="400" height="200"></canvas>
                    </div>
                    <div class="col-md-6">
                        <canvas id="comparison-chart-maturity" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        `;
        
        container.appendChild(comparisonCard);

        // Render the comparison charts
        this.createSuitabilityComparisonChart(crops);
        this.createPhRangeComparisonChart(crops);
        this.createMaturityComparisonChart(crops);
    }

    createSuitabilityComparisonChart(crops) {
        const ctx = document.getElementById('comparison-chart-suitability');
        if (!ctx) return;

        const labels = crops.map(crop => crop.name);
        const data = crops.map(crop => crop.suitability_score * 100);

        if (this.charts.suitabilityComparison) {
            this.charts.suitabilityComparison.destroy();
        }

        this.charts.suitabilityComparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Suitability Score (%)',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Suitability Score Comparison'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Suitability Score (%)'
                        }
                    }
                }
            }
        });
    }

    createPhRangeComparisonChart(crops) {
        const ctx = document.getElementById('comparison-chart-ph');
        if (!ctx) return;

        const labels = crops.map(crop => crop.name);
        const minData = crops.map(crop => crop.ph_range.min);
        const maxData = crops.map(crop => crop.ph_range.max);

        if (this.charts.phComparison) {
            this.charts.phComparison.destroy();
        }

        this.charts.phComparison = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Min pH Requirement',
                        data: minData,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Max pH Requirement',
                        data: maxData,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'pH Range Requirements'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'pH Value'
                        }
                    }
                }
            }
        });
    }

    createMaturityComparisonChart(crops) {
        const ctx = document.getElementById('comparison-chart-maturity');
        if (!ctx) return;

        const labels = crops.map(crop => crop.name);
        const data = crops.map(crop => crop.maturity_days);

        if (this.charts.maturityComparison) {
            this.charts.maturityComparison.destroy();
        }

        this.charts.maturityComparison = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Days to Maturity',
                    data: data,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Maturity Days Comparison'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Days'
                        }
                    }
                }
            }
        });
    }

    exportResults() {
        if (!this.currentResults || this.currentResults.length === 0) {
            alert('No results to export');
            return;
        }

        // Create a simple CSV export of results
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += "Name,Scientific Name,Category,Suitability Score,Climate Zones,Min pH,Max pH,Maturity Days,Drought Tolerance\r\n";
        
        this.currentResults.forEach(crop => {
            const climateZones = crop.climate_zones.join(';');
            csvContent += `"${crop.name}","${crop.scientific_name}","${crop.category}","${crop.suitability_score}",` +
                          `"${climateZones}","${crop.ph_range.min}","${crop.ph_range.max}","${crop.maturity_days}","${crop.drought_tolerance}"\r\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "crop_filtering_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    exportChartAsImage() {
        // Export the first chart as an image (or user-selected chart)
        const canvas = document.getElementById('filterImpactChart');
        if (!canvas) {
            alert('No chart available to export');
            return;
        }

        const imageLink = document.createElement('a');
        imageLink.download = 'filter_impact_chart.png';
        imageLink.href = canvas.toDataURL('image/png');
        imageLink.click();
    }
    
    exportChartAsImageById(chartId) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Chart with ID ${chartId} not found`);
            alert(`Chart with ID ${chartId} not found`);
            return;
        }

        const imageLink = document.createElement('a');
        const filename = chartId.replace(/-/g, '_') + '_chart.png';
        imageLink.download = filename;
        imageLink.href = canvas.toDataURL('image/png');
        imageLink.click();
    }
    
    exportResultsByType(dataType) {
        if (!this.currentResults || this.currentResults.length === 0) {
            alert('No data available to download');
            return;
        }

        let content = '';
        let filename = '';

        switch (dataType) {
            case 'results':
                content = this.exportResultsAsCSV();
                filename = 'crop_filtering_results.csv';
                break;
            case 'summary':
                content = this.exportSummaryAsCSV();
                filename = 'crop_filtering_summary.csv';
                break;
            case 'detailed':
                content = this.exportDetailedAsCSV();
                filename = 'crop_filtering_detailed.csv';
                break;
            default:
                console.error('Unknown data type for export');
                return;
        }

        const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    exportResultsAsCSV() {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance\n';
        
        this.currentResults.forEach(crop => {
            const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
            csvContent += `"${crop.name}","${crop.scientific_name}","${crop.category.replace(/_/g, ' ')}",` +
                         `"${crop.suitability_score}","${climateZones}","${crop.ph_range?.min || ''}",` +
                         `"${crop.ph_range?.max || ''}","${crop.maturity_days || ''}","${crop.drought_tolerance || ''}"\n`;
        });
        
        return csvContent;
    }

    exportSummaryAsCSV() {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Category,Count,Percentage,Top Crops\n';
        
        // Count categories
        const categoryCounts = {};
        this.currentResults.forEach(crop => {
            const cat = crop.category.replace(/_/g, ' ');
            categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;
        });
        
        const total = this.currentResults.length;
        
        Object.entries(categoryCounts).forEach(([category, count]) => {
            const percentage = ((count / total) * 100).toFixed(2);
            const topCrops = this.currentResults
                .filter(crop => crop.category.replace(/_/g, ' ') === category)
                .slice(0, 3)
                .map(crop => crop.name)
                .join('; ');
                
            csvContent += `"${category}","${count}","${percentage}%","${topCrops}"\n`;
        });
        
        return csvContent;
    }

    exportDetailedAsCSV() {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance,Management Complexity,Tags\n';
        
        this.currentResults.forEach(crop => {
            const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
            const tags = crop.tags ? crop.tags.join('; ') : '';
            csvContent += `"${crop.name}","${crop.scientific_name}","${crop.category.replace(/_/g, ' ')}",` +
                         `"${crop.suitability_score}","${climateZones}","${crop.ph_range?.min || ''}",` +
                         `"${crop.ph_range?.max || ''}","${crop.maturity_days || ''}","${crop.drought_tolerance || ''}",` +
                         `"${crop.management_complexity || ''}","${tags}"\n`;
        });
        
        return csvContent;
    }

    viewCropDetails(cropId) {
        // In a real app, this would show detailed crop information
        alert(`Viewing details for crop: ${cropId}`);
    }

    addCropToPlan(cropId) {
        // In a real app, this would add the crop to a rotation plan or list
        alert(`Added crop to plan: ${cropId}`);
    }

    showError(message) {
        // Create and show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert after the filter section
        const container = document.querySelector('.container');
        container.insertBefore(errorDiv, container.firstChild);
    }
    
    renderYieldPotentialChart() {
        const ctx = document.getElementById('yield-potential-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.yieldChart) {
            this.charts.yieldChart.destroy();
        }

        // Extract yield data or create mock data if not available
        const labels = this.currentResults.slice(0, 10).map(crop => crop.name);
        const minYield = this.currentResults.slice(0, 10).map(crop => {
            // Use mock data if yield potential is not available
            return crop.yield_potential?.min || Math.floor(Math.random() * 50) + 50;
        });
        const maxYield = this.currentResults.slice(0, 10).map(crop => {
            // Use mock data if yield potential is not available
            return crop.yield_potential?.max || Math.floor(Math.random() * 50) + 100;
        });

        this.charts.yieldChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Min Yield Potential',
                        data: minYield,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Max Yield Potential',
                        data: maxYield,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Yield Potential Comparison'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Crop'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Yield Potential'
                        }
                    }
                }
            }
        });
    }

    renderCostAnalysisChart() {
        const ctx = document.getElementById('cost-analysis-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.costChart) {
            this.charts.costChart.destroy();
        }

        // Create mock cost data
        const labels = this.currentResults.slice(0, 10).map(crop => crop.name);
        const establishmentCost = this.currentResults.slice(0, 10).map(() => Math.floor(Math.random() * 100) + 50);
        const maintenanceCost = this.currentResults.slice(0, 10).map(() => Math.floor(Math.random() * 75) + 25);

        this.charts.costChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Establishment Cost ($/acre)',
                        data: establishmentCost,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Maintenance Cost ($/acre)',
                        data: maintenanceCost,
                        backgroundColor: 'rgba(255, 206, 86, 0.6)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Cost Analysis Comparison'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Crop'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Cost ($/acre)'
                        }
                    }
                }
            }
        });
    }

    renderGeographicDistributionChart() {
        const ctx = document.getElementById('geographic-distribution-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.geoChart) {
            this.charts.geoChart.destroy();
        }

        // Count climate zones across results
        const zoneCounts = {};
        this.currentResults.forEach(crop => {
            if (crop.climate_zones) {
                crop.climate_zones.forEach(zone => {
                    zoneCounts[zone] = (zoneCounts[zone] || 0) + 1;
                });
            }
        });

        const labels = Object.keys(zoneCounts);
        const data = Object.values(zoneCounts);

        this.charts.geoChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Crops per Zone',
                    data: data,
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    pointBackgroundColor: 'rgba(153, 102, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(153, 102, 255, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Climate Zone Distribution'
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0
                    }
                }
            }
        });
    }

    renderSeasonalTrendChart() {
        const ctx = document.getElementById('seasonal-trend-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.seasonalChart) {
            this.charts.seasonalChart.destroy();
        }

        // Group results by planting season
        const seasonData = {
            spring: 0,
            summer: 0,
            fall: 0,
            winter: 0
        };

        this.currentResults.forEach(crop => {
            if (crop.planting_season) {
                crop.planting_season.forEach(season => {
                    if (seasonData[season] !== undefined) {
                        seasonData[season]++;
                    }
                });
            } else {
                seasonData.spring++; // Default to spring
            }
        });

        const labels = Object.keys(seasonData);
        const data = Object.values(seasonData);

        this.charts.seasonalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Suitable Crops by Season',
                    data: data,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Seasonal Planting Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Crops'
                        }
                    }
                }
            }
        });
    }

    renderSuitabilityDistributionChart() {
        const ctx = document.getElementById('suitability-distribution-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.suitabilityDistributionChart) {
            this.charts.suitabilityDistributionChart.destroy();
        }

        // Create bins for suitability scores (0-100% in 20% increments)
        const bins = [
            { label: '0-20%', count: 0 },
            { label: '21-40%', count: 0 },
            { label: '41-60%', count: 0 },
            { label: '61-80%', count: 0 },
            { label: '81-100%', count: 0 }
        ];

        this.currentResults.forEach(crop => {
            const score = crop.suitability_score * 100;
            if (score <= 20) bins[0].count++;
            else if (score <= 40) bins[1].count++;
            else if (score <= 60) bins[2].count++;
            else if (score <= 80) bins[3].count++;
            else bins[4].count++;
        });

        const labels = bins.map(bin => bin.label);
        const data = bins.map(bin => bin.count);

        this.charts.suitabilityDistributionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Crops',
                    data: data,
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.6)', // Red for low suitability
                        'rgba(255, 193, 7, 0.6)',  // Yellow for low-medium
                        'rgba(255, 193, 7, 0.6)',  // Yellow for medium
                        'rgba(40, 167, 69, 0.6)',   // Green for high-medium
                        'rgba(40, 167, 69, 0.6)'    // Green for high
                    ],
                    borderColor: [
                        'rgba(220, 53, 69, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(40, 167, 69, 1)',
                        'rgba(40, 167, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Suitability Score Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Crops'
                        }
                    }
                }
            }
        });
    }

    // Apply quick filter based on type
    applyQuickFilter(filterType) {
        // Reset all filter UI elements first
        this.clearAllQuickFilters();
        
        switch(filterType) {
            case 'drought':
                // Apply high drought tolerance
                document.querySelectorAll('#drought-filters input[type="checkbox"]').forEach(checkbox => {
                    if (checkbox.value === 'high' || checkbox.value === 'very_high') {
                        checkbox.checked = true;
                    }
                });
                break;
                
            case 'nitrogen':
                // Select legume crops which are nitrogen fixing
                const legumeOption = Array.from(document.getElementById('crop-categories').options)
                    .find(option => option.value === 'legume_crops');
                if (legumeOption) legumeOption.selected = true;
                break;
                
            case 'low-maintenance':
                // Select low management complexity
                const lowComplexityRadio = document.querySelector('input[name="management-complexity"][value="low"]');
                if (lowComplexityRadio) lowComplexityRadio.checked = true;
                break;
                
            case 'high-yield':
                // This would typically involve more complex logic in a real app
                // For now, we'll just ensure grain and oilseed crops are selected
                const categorySelect = document.getElementById('crop-categories');
                ['grain_crops', 'oilseed_crops'].forEach(cat => {
                    const option = Array.from(categorySelect.options).find(opt => opt.value === cat);
                    if (option) option.selected = true;
                });
                break;
                
            case 'organic':
                // Select crops suitable for organic farming
                const organicCheck = document.getElementById('market-organic');
                if (organicCheck) organicCheck.checked = true;
                break;
                
            case 'early-season':
                // Set shorter growing season
                document.getElementById('growing-season-min').value = 60;
                document.getElementById('growing-season-max').value = 100;
                this.updateSliderValue({target: document.getElementById('growing-season-min')});
                this.updateSliderValue({target: document.getElementById('growing-season-max')});
                break;
                
            case 'late-season':
                // Set longer growing season
                document.getElementById('growing-season-min').value = 120;
                document.getElementById('growing-season-max').value = 180;
                this.updateSliderValue({target: document.getElementById('growing-season-min')});
                this.updateSliderValue({target: document.getElementById('growing-season-max')});
                break;
                
            case 'disease-resistant':
                // Select crops with disease resistance
                const diseaseResOption = Array.from(document.getElementById('pest-resistance').options)
                    .find(option => option.value === 'disease');
                if (diseaseResOption) diseaseResOption.selected = true;
                break;
                
            case 'heat-tolerant':
                // Apply heat tolerance (similar to drought)
                document.querySelectorAll('#drought-filters input[type="checkbox"]').forEach(checkbox => {
                    if (checkbox.value === 'high' || checkbox.value === 'very_high') {
                        checkbox.checked = true;
                    }
                });
                break;
                
            case 'water-efficient':
                // Similar to drought tolerance
                document.querySelectorAll('#drought-filters input[type="checkbox"]').forEach(checkbox => {
                    if (checkbox.value === 'high' || checkbox.value === 'very_high') {
                        checkbox.checked = true;
                    }
                });
                // Also prefer crops with lower water requirements
                break;
                
            case 'pest-resistant':
                // Select crops with pest resistance
                const pestResOption = Array.from(document.getElementById('pest-resistance').options)
                    .find(option => option.value === 'insect');
                if (pestResOption) pestResOption.selected = true;
                break;
                
            case 'cover-crop':
                // Focus on cover crops
                const coverCropOption = Array.from(document.getElementById('crop-categories').options)
                    .find(option => option.value === 'cover_crops');
                if (coverCropOption) coverCropOption.selected = true;
                break;
                
            case 'rotation-friendly':
                // Select crops that are good for rotation
                const rotationOptions = Array.from(document.getElementById('crop-categories').options)
                    .filter(option => ['legume_crops', 'cover_crops'].includes(option.value));
                rotationOptions.forEach(option => option.selected = true);
                break;
                
            default:
                console.warn(`Unknown quick filter type: ${filterType}`);
        }
        
        // Update filters in state manager
        const newFilters = this.getFiltersFromUI();
        this.filterStateManager.currentFilters = newFilters;
        
        // Add to filter history for undo/redo functionality
        this.filterStateManager.addToHistory();
        this.updateHistoryButtons();
        
        // Apply the filters
        this.applyFilters();
    }
    
    // Clear all quick filter selections
    clearAllQuickFilters() {
        // Reset drought tolerance checkboxes
        document.querySelectorAll('#drought-filters input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Reset management complexity radios
        document.querySelectorAll('input[name="management-complexity"]').forEach(radio => {
            radio.checked = false;
        });
        
        // Reset market class checkboxes
        document.querySelectorAll('#market-filters input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    renderManagementComplexityChart() {
        const ctx = document.getElementById('management-complexity-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.managementComplexityChart) {
            this.charts.managementComplexityChart.destroy();
        }

        // Count management complexity levels
        const complexityCounts = {
            low: 0,
            moderate: 0,
            high: 0
        };

        this.currentResults.forEach(crop => {
            if (crop.management_complexity && complexityCounts[crop.management_complexity] !== undefined) {
                complexityCounts[crop.management_complexity]++;
            }
        });

        const labels = Object.keys(complexityCounts);
        const data = Object.values(complexityCounts);

        this.charts.managementComplexityChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.map(label => label.replace('_', ' ')),
                datasets: [{
                    label: 'Management Complexity',
                    data: data,
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',   // Green for low complexity
                        'rgba(255, 193, 7, 0.8)',   // Yellow for moderate
                        'rgba(220, 53, 69, 0.8)'    // Red for high
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Management Complexity Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateSummaryCards() {
        // Update total results count
        const totalResultsCount = document.getElementById('total-results-count');
        if (totalResultsCount) {
            totalResultsCount.textContent = this.currentResults.length;
        }

        // Update active filters count
        const activeFiltersCount = document.getElementById('active-filters-count');
        if (activeFiltersCount) {
            const filters = this.filterStateManager.getFilters();
            activeFiltersCount.textContent = Object.keys(filters).length;
        }

        // Calculate and update dataset reduction percentage
        // Assuming original dataset size is 1000 for this example (this should come from your data source)
        const originalDatasetSize = 1000; // This should be dynamic based on your actual data
        const reductionPercentage = document.getElementById('reduction-percentage');
        if (reductionPercentage) {
            const reduction = originalDatasetSize - this.currentResults.length;
            const reductionPercent = ((reduction / originalDatasetSize) * 100).toFixed(2);
            reductionPercentage.textContent = `${reductionPercent}%`;
        }

        // Calculate and update average suitability score
        const avgSuitabilityScore = document.getElementById('avg-suitability-score');
        if (avgSuitabilityScore && this.currentResults.length > 0) {
            const totalScore = this.currentResults.reduce((sum, crop) => sum + crop.suitability_score, 0);
            const average = (totalScore / this.currentResults.length).toFixed(2);
            avgSuitabilityScore.textContent = average;
        }
    }
}

// Initialize the crop filtering manager when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.cropFilteringManager = new CropFilteringManager();
});

// Global function for template use
function toggleFilterSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = document.querySelector(`#${sectionId} .fa-chevron-down`);
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        if (icon) icon.style.transform = 'rotate(180deg)';
    } else {
        section.style.display = 'none';
        if (icon) icon.style.transform = 'rotate(0deg)';
    }
}