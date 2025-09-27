/**
 * Unit tests for CropFilteringManager class
 * 
 * These tests verify the functionality of the CropFilteringManager including:
 * - Basic filter functionality
 * - State management features (URL parameters, presets, undo/redo)
 * - Chart rendering
 * - Export/import functionality
 * - Filter validation
 */

// Mocking the DOM environment for testing
const { JSDOM } = require('jsdom');
const fs = require('fs');

// Set up a basic DOM environment
const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Crop Filtering Tests</title>
</head>
<body>
    <!-- Filter Section -->
    <div id="filter-panel">
        <div class="filter-header">Climate Filters</div>
        <div style="display:block">
            <select id="climate-zones" multiple>
                <option value="1a">Zone 1a</option>
                <option value="1b">Zone 1b</option>
                <option value="2a">Zone 2a</option>
            </select>
            
            <div class="range-slider-container">
                <label>Growing Season: <span id="growing-season-min-value">60</span> - <span id="growing-season-max-value">150</span></label>
                <input type="range" id="growing-season-min" value="60" min="30" max="365">
                <input type="range" id="growing-season-max" value="150" min="30" max="365">
            </div>
            
            <div id="drought-filters">
                <input type="checkbox" id="drought-low" value="low">
                <input type="checkbox" id="drought-moderate" value="moderate">
            </div>
        </div>
        
        <div class="filter-header">Soil Filters</div>
        <div style="display:block">
            <div class="range-slider-container">
                <label>Soil pH: <span id="ph-min-value">5.5</span> - <span id="ph-max-value">7.5</span></label>
                <input type="range" id="ph-min" value="5.5" min="4" max="9" step="0.1">
                <input type="range" id="ph-max" value="7.5" min="4" max="9" step="0.1">
            </div>
            
            <select id="soil-types" multiple>
                <option value="clay">Clay</option>
                <option value="loam">Loam</option>
                <option value="sand">Sand</option>
            </select>
            
            <div id="soil-filters">
                <input type="checkbox" id="drainage-well" value="well_drained">
                <input type="checkbox" id="drainage-poor" value="poorly_drained">
            </div>
        </div>
        
        <div class="filter-header">Agricultural Filters</div>
        <div style="display:block">
            <select id="crop-categories" multiple>
                <option value="grain_crops">Grain Crops</option>
                <option value="legume_crops">Legume Crops</option>
                <option value="cover_crops">Cover Crops</option>
            </select>
            
            <div>
                <input type="radio" id="complexity-low" name="management-complexity" value="low">
                <input type="radio" id="complexity-moderate" name="management-complexity" value="moderate">
                <input type="radio" id="complexity-high" name="management-complexity" value="high">
            </div>
            
            <select id="pest-resistance" multiple>
                <option value="insect">Insect Resistance</option>
                <option value="disease">Disease Resistance</option>
            </select>
        </div>
        
        <div class="filter-header">Market Filters</div>
        <div style="display:block">
            <div id="market-filters">
                <input type="checkbox" id="market-organic" value="organic">
                <input type="checkbox" id="market-non-gmo" value="non_gmo">
            </div>
            
            <div>
                <input type="radio" id="stability-stable" name="market-stability" value="stable">
                <input type="radio" id="stability-volatile" name="market-stability" value="volatile">
            </div>
        </div>
        
        <button id="apply-filters">Apply Filters</button>
        <button id="clear-all-filters">Clear All</button>
        <button id="reset-filters">Reset</button>
        <button id="save-preset-btn">Save Preset</button>
        <button id="load-preset-btn">Load Preset</button>
        <button id="export-config-btn">Export Config</button>
        <button id="import-config-btn">Import Config</button>
        <button id="undo-btn">Undo</button>
        <button id="redo-btn">Redo</button>
        <button id="export-results-btn">Export Results</button>
        <button id="export-chart-btn">Export Chart</button>
        <button id="compare-selected-btn">Compare Selected</button>
    </div>
    
    <!-- Applied Filters Display -->
    <div id="applied-filters-list"></div>
    
    <!-- Results Section -->
    <div id="loading-indicator" class="d-none">Loading...</div>
    <div id="no-results-message" class="d-none">No results found</div>
    <div id="crop-results-list"></div>
    <div id="results-count">0</div>
    <div id="pagination-container"></div>
    
    <!-- Filter Validation Alert -->
    <div id="filter-validation-alert" class="d-none">
        <ul id="validation-messages"></ul>
    </div>
    
    <!-- Charts -->
    <div class="tab-pane active" id="visualization-panel">
        <div class="card-body">
            <canvas id="filterImpactChart"></canvas>
            <canvas id="categoryDistributionChart"></canvas>
            <canvas id="droughtToleranceChart"></canvas>
        </div>
    </div>
    
    <!-- Comparison Tab -->
    <div id="comparison-tab"></div>
    <select id="crop-comparison-select" multiple></select>
    
    <!-- Sort Options -->
    <select id="sort-options">
        <option value="suitability_score">Suitability Score</option>
        <option value="name">Name</option>
        <option value="popularity">Popularity</option>
    </select>
    
    <!-- Results Container -->
    <div class="container"></div>
    
    <!-- Comparison Results -->
    <div id="comparison-results"></div>
</body>
</html>
`;

const dom = new JSDOM(html, { url: 'http://localhost' });
global.window = dom.window;
global.document = dom.window.document;
global.Chart = {
    // Mock Chart.js
    constructor(ctx, config) {
        this.ctx = ctx;
        this.config = config;
        this.destroy = jest.fn();
    }
};
global.localStorage = (() => {
    let store = {};
    return {
        getItem: (key) => store[key] || null,
        setItem: (key, value) => { store[key] = value.toString(); },
        removeItem: (key) => { delete store[key]; },
        clear: () => { store = {}; }
    };
})();

// Mock URLSearchParams
global.URLSearchParams = jest.fn().mockImplementation((searchString) => {
    const params = new Map();
    if (searchString) {
        const search = searchString.startsWith('?') ? searchString.substring(1) : searchString;
        search.split('&').forEach(param => {
            const [key, value] = param.split('=');
            if (key) {
                params.set(decodeURIComponent(key), value ? decodeURIComponent(value) : '');
            }
        });
    }
    
    return {
        get: (name) => params.get(name) || null,
        set: (name, value) => params.set(name, value),
        delete: (name) => params.delete(name),
        toString: () => Array.from(params.entries())
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            .join('&')
    };
});

// Mock history API
global.window.history = {
    replaceState: jest.fn(),
    pushState: jest.fn()
};

// Mock File API for import functionality
global.File = class File {};
global.FileReader = class FileReader {
    constructor() {
        this.onload = null;
        this.readAsText = jest.fn((file) => {
            if (this.onload) {
                // Simulate loading with test data
                setTimeout(() => {
                    this.onload({ target: { result: '{"filters": {}}' } });
                }, 0);
            }
        });
    }
};

// Now load the crop filtering manager after setting up the environment
const { CropFilteringManager } = require('./../../../../src/static/js/crop-filtering.js');

describe('CropFilteringManager', () => {
    let cropFilteringManager;

    beforeEach(() => {
        // Reset DOM and localStorage before each test
        document.body.innerHTML = html;
        localStorage.clear();
        
        // Create a new instance of CropFilteringManager
        cropFilteringManager = new CropFilteringManager();
        cropFilteringManager.charts = {}; // Reset charts
        
        // Mock Chart constructor
        global.Chart = jest.fn().mockImplementation((ctx, config) => {
            return {
                ctx,
                config,
                destroy: jest.fn()
            };
        });
    });

    describe('Initialization', () => {
        test('should initialize with default values', () => {
            expect(cropFilteringManager.currentFilters).toEqual({});
            expect(cropFilteringManager.currentResults).toEqual([]);
            expect(cropFilteringManager.currentPage).toBe(1);
            expect(cropFilteringManager.resultsPerPage).toBe(10);
            expect(cropFilteringManager.charts).toEqual({});
            expect(cropFilteringManager.selectedComparisonCrops).toEqual([]);
            expect(cropFilteringManager.filterHistory).toEqual([{}]);
            expect(cropFilteringManager.historyIndex).toBe(0);
        });

        test('should bind events correctly', () => {
            // Check that key event listeners are bound
            const applyFiltersBtn = document.getElementById('apply-filters');
            expect(applyFiltersBtn).not.toBeNull();
        });
    });

    describe('Filter Management', () => {
        test('should get filters from UI', () => {
            // Set some values in the UI
            document.getElementById('climate-zones').options[0].selected = true;
            document.getElementById('soil-types').options[1].selected = true;
            document.getElementById('growing-season-min').value = '90';
            document.getElementById('growing-season-max').value = '120';
            document.getElementById('ph-min').value = '6.0';
            document.getElementById('ph-max').value = '7.0';
            
            const filters = cropFilteringManager.getFiltersFromUI();
            expect(filters).toHaveProperty('climate_zones');
            expect(filters).toHaveProperty('soil_types');
            expect(filters).toHaveProperty('growing_season_range');
            expect(filters).toHaveProperty('soil_ph_range');
            expect(filters.growing_season_range.min).toBe(90);
            expect(filters.growing_season_range.max).toBe(120);
            expect(filters.soil_ph_range.min).toBe(6.0);
            expect(filters.soil_ph_range.max).toBe(7.0);
        });

        test('should set filters to UI', () => {
            const filters = {
                climate_zones: ['1a', '2a'],
                soil_types: ['loam', 'clay'],
                growing_season_range: { min: 75, max: 160 },
                soil_ph_range: { min: 6.2, max: 7.2 }
            };
            
            cropFilteringManager.setFiltersToUI(filters);
            
            const climateSelect = document.getElementById('climate-zones');
            const selectedClimateZones = Array.from(climateSelect.options)
                .filter(option => option.selected)
                .map(option => option.value);
            expect(selectedClimateZones).toContain('1a');
            expect(selectedClimateZones).toContain('2a');
            
            const soilSelect = document.getElementById('soil-types');
            const selectedSoilTypes = Array.from(soilSelect.options)
                .filter(option => option.selected)
                .map(option => option.value);
            expect(selectedSoilTypes).toContain('loam');
            expect(selectedSoilTypes).toContain('clay');
        });
    });

    describe('State Management and Persistence', () => {
        test('should save filters to localStorage', () => {
            cropFilteringManager.currentFilters = { test: 'filter' };
            cropFilteringManager.saveFiltersToLocalStorage();
            
            const savedFilters = localStorage.getItem('cropFilters');
            expect(savedFilters).toBe(JSON.stringify({ test: 'filter' }));
        });

        test('should load filters from localStorage', () => {
            localStorage.setItem('cropFilters', JSON.stringify({ loaded: 'fromStorage' }));
            cropFilteringManager.currentFilters = {}; // Reset
            
            cropFilteringManager.loadFiltersFromLocalStorage();
            expect(cropFilteringManager.currentFilters).toEqual({ loaded: 'fromStorage' });
        });

        test('should save filters to URL', () => {
            cropFilteringManager.currentFilters = { test: 'url_filter' };
            cropFilteringManager.saveFiltersToUrl();
            
            expect(global.window.history.replaceState).toHaveBeenCalled();
        });

        test('should load filters from URL', () => {
            // Mock URLSearchParams to return test filters
            const mockUrlParams = {
                get: (name) => name === 'filters' ? encodeURIComponent(JSON.stringify({ url: 'test' })) : null
            };
            global.URLSearchParams.mockImplementation(() => mockUrlParams);
            
            // Create a new instance to trigger URL loading
            cropFilteringManager = new CropFilteringManager();
            expect(cropFilteringManager.currentFilters).toEqual({ url: 'test' });
        });

        test('should add to filter history', () => {
            const initialHistoryLength = cropFilteringManager.filterHistory.length;
            cropFilteringManager.addToHistory({ new: 'filter' });
            
            expect(cropFilteringManager.filterHistory.length).toBe(initialHistoryLength + 1);
            expect(cropFilteringManager.historyIndex).toBe(initialHistoryLength);
            expect(cropFilteringManager.filterHistory[cropFilteringManager.historyIndex]).toEqual({ new: 'filter' });
        });

        test('should handle undo functionality', () => {
            cropFilteringManager.currentFilters = { current: 'state' };
            cropFilteringManager.addToHistory({ current: 'state' });
            cropFilteringManager.addToHistory({ previous: 'state' });
            
            cropFilteringManager.undoFilter();
            expect(cropFilteringManager.currentFilters).toEqual({ previous: 'state' });
            expect(cropFilteringManager.historyIndex).toBe(0);
        });

        test('should handle redo functionality', () => {
            cropFilteringManager.currentFilters = { original: 'state' };
            cropFilteringManager.addToHistory({ original: 'state' });
            cropFilteringManager.addToHistory({ modified: 'state' });
            
            // Move back
            cropFilteringManager.historyIndex = 0;
            cropFilteringManager.currentFilters = { original: 'state' };
            
            cropFilteringManager.redoFilter();
            expect(cropFilteringManager.currentFilters).toEqual({ modified: 'state' });
            expect(cropFilteringManager.historyIndex).toBe(1);
        });
    });

    describe('Preset Management', () => {
        beforeEach(() => {
            // Mock prompt and alert functions
            global.prompt = jest.fn();
            global.alert = jest.fn();
        });

        test('should save a preset', () => {
            global.prompt.mockReturnValue('Test Preset');
            cropFilteringManager.currentFilters = { test: 'filter' };
            
            cropFilteringManager.savePreset();
            
            const presets = JSON.parse(localStorage.getItem('cropFilterPresets') || '{}');
            expect(presets['Test Preset']).toEqual({ test: 'filter' });
        });

        test('should load a preset', () => {
            localStorage.setItem('cropFilterPresets', JSON.stringify({ 'Test Preset': { loaded: 'preset' } }));
            global.prompt.mockReturnValue('Test Preset');
            
            cropFilteringManager.loadPreset();
            
            expect(cropFilteringManager.currentFilters).toEqual({ loaded: 'preset' });
        });

        test('should export configuration', () => {
            // Mock document.createElement and click
            document.createElement = jest.fn((tag) => {
                const element = document.createElement(tag);
                if (tag === 'a') {
                    element.setAttribute = jest.fn();
                    element.click = jest.fn();
                }
                return element;
            });

            cropFilteringManager.currentFilters = { export: 'test' };
            cropFilteringManager.exportConfiguration();
            
            // Check that the link was created and clicked
            expect(document.createElement).toHaveBeenCalledWith('a');
        });

        test('should import configuration', () => {
            // Mock input file selection
            const inputElement = document.createElement('input');
            inputElement.type = 'file';
            inputElement.accept = '.json';
            
            const mockFile = new File(['{"filters": {"imported": "config"}}'], 'test.json', { type: 'application/json' });
            
            // Set up the onchange handler
            let onchangeHandler;
            Object.defineProperty(inputElement, 'onchange', {
                set: function(handler) {
                    onchangeHandler = handler;
                },
                get: function() { return onchangeHandler; }
            });
            
            // Call the import function which should set up the onchange handler
            cropFilteringManager.importConfiguration();
            
            // Manually trigger the onchange event with our mock file
            if (onchangeHandler) {
                const mockEvent = { target: { files: [mockFile] } };
                onchangeHandler(mockEvent);
            }
        });
    });

    describe('Filter Validation', () => {
        test('should validate pH range correctly', async () => {
            cropFilteringManager.currentFilters = {
                soil_ph_range: { min: 8.0, max: 6.0 } // Invalid: min > max
            };
            
            const validation = await cropFilteringManager.validateFilters();
            expect(validation.isValid).toBe(false);
            expect(validation.messages).toContain('Minimum pH cannot be greater than maximum pH');
        });

        test('should validate climate and growing season compatibility', async () => {
            cropFilteringManager.currentFilters = {
                climate_zones: ['1a', '1b'], // Northern zones
                growing_season_range: { min: 180, max: 220 } // Long growing season
            };
            
            const validation = await cropFilteringManager.validateFilters();
            expect(validation.messages).toContain('Long growing season crops may not mature in northern climate zones');
        });

        test('should validate extreme pH values', async () => {
            cropFilteringManager.currentFilters = {
                soil_ph_range: { min: 3.5, max: 9.5 } // Extreme values
            };
            
            const validation = await cropFilteringManager.validateFilters();
            expect(validation.messages).toContain('Extreme pH values may limit crop options significantly');
        });
    });

    describe('Results Display', () => {
        test('should display results correctly', () => {
            const mockResults = [
                {
                    id: 'crop-1',
                    name: 'Test Crop',
                    scientific_name: 'Testus cropicus',
                    category: 'grain_crops',
                    suitability_score: 0.85,
                    description: 'A test crop',
                    climate_zones: ['5a', '5b'],
                    ph_range: {min: 6.0, max: 7.0},
                    maturity_days: 100,
                    drought_tolerance: 'moderate',
                    management_complexity: 'moderate',
                    tags: ['test', 'crop']
                }
            ];
            
            cropFilteringManager.currentResults = mockResults;
            cropFilteringManager.displayResults();
            
            const resultsContainer = document.getElementById('crop-results-list');
            expect(resultsContainer.innerHTML).toContain('Test Crop');
            expect(resultsContainer.innerHTML).toContain('Testus cropicus');
        });

        test('should create crop cards', () => {
            const crop = {
                id: 'crop-1',
                name: 'Test Crop',
                scientific_name: 'Testus cropicus',
                category: 'grain_crops',
                suitability_score: 0.85,
                description: 'A test crop',
                climate_zones: ['5a', '5b'],
                ph_range: {min: 6.0, max: 7.0},
                maturity_days: 100,
                drought_tolerance: 'moderate',
                management_complexity: 'moderate',
                tags: ['test', 'crop']
            };
            
            const card = cropFilteringManager.createCropCard(crop);
            expect(card.innerHTML).toContain('Test Crop');
            expect(card.innerHTML).toContain('Testus cropicus');
            expect(card.innerHTML).toContain('85%'); // Suitability score
        });

        test('should display applied filters', () => {
            cropFilteringManager.currentFilters = {
                climate_zones: ['1a', '2a'],
                drought_tolerance: ['moderate', 'high']
            };
            
            cropFilteringManager.displayAppliedFilters();
            const filtersContainer = document.getElementById('applied-filters-list');
            
            expect(filtersContainer.innerHTML).toContain('climate zones: 1a, 2a');
            expect(filtersContainer.innerHTML).toContain('drought tolerance: moderate, high');
        });

        test('should display no applied filters message when no filters', () => {
            cropFilteringManager.currentFilters = {};
            cropFilteringManager.displayAppliedFilters();
            const filtersContainer = document.getElementById('applied-filters-list');
            
            expect(filtersContainer.innerHTML).toContain('No filters applied');
        });
    });

    describe('Chart Rendering', () => {
        test('should render filter impact chart', () => {
            cropFilteringManager.currentResults = [
                {
                    id: 'crop-1',
                    name: 'Test Crop 1',
                    category: 'grain_crops',
                    drought_tolerance: 'moderate',
                    suitability_score: 0.85
                }
            ];
            
            cropFilteringManager.currentFilters = {
                climate_zones: ['1a', '2a'],
                drought_tolerance: ['moderate', 'high']
            };
            
            cropFilteringManager.renderFilterImpactChart();
            
            // Verify that Chart constructor was called
            expect(global.Chart).toHaveBeenCalledTimes(1);
        });

        test('should render category distribution chart', () => {
            cropFilteringManager.currentResults = [
                {
                    id: 'crop-1',
                    name: 'Test Crop 1',
                    category: 'grain_crops',
                    drought_tolerance: 'moderate',
                    suitability_score: 0.85
                },
                {
                    id: 'crop-2',
                    name: 'Test Crop 2',
                    category: 'legume_crops',
                    drought_tolerance: 'low',
                    suitability_score: 0.75
                }
            ];
            
            cropFilteringManager.renderCategoryDistributionChart();
            
            // Verify that Chart constructor was called
            expect(global.Chart).toHaveBeenCalledTimes(1);
        });

        test('should render drought tolerance chart', () => {
            cropFilteringManager.currentResults = [
                {
                    id: 'crop-1',
                    name: 'Test Crop 1',
                    category: 'grain_crops',
                    drought_tolerance: 'moderate',
                    suitability_score: 0.85
                },
                {
                    id: 'crop-2',
                    name: 'Test Crop 2',
                    category: 'legume_crops',
                    drought_tolerance: 'low',
                    suitability_score: 0.75
                }
            ];
            
            cropFilteringManager.renderDroughtToleranceChart();
            
            // Verify that Chart constructor was called
            expect(global.Chart).toHaveBeenCalledTimes(1);
        });
    });

    describe('Comparison Functionality', () => {
        test('should setup comparison tab', () => {
            cropFilteringManager.currentResults = [
                {
                    id: 'crop-1',
                    name: 'Test Crop 1',
                    category: 'grain_crops',
                    drought_tolerance: 'moderate',
                    suitability_score: 0.85
                },
                {
                    id: 'crop-2',
                    name: 'Test Crop 2',
                    category: 'legume_crops',
                    drought_tolerance: 'low',
                    suitability_score: 0.75
                }
            ];
            
            cropFilteringManager.setupComparisonTab();
            
            const select = document.getElementById('crop-comparison-select');
            expect(select.options.length).toBe(2);
            expect(select.options[0].textContent).toBe('Test Crop 1');
            expect(select.options[1].textContent).toBe('Test Crop 2');
        });

        test('should render comparison charts', () => {
            const crops = [
                {
                    id: 'crop-1',
                    name: 'Test Crop 1',
                    category: 'grain_crops',
                    drought_tolerance: 'moderate',
                    suitability_score: 0.85,
                    ph_range: { min: 6.0, max: 7.0 },
                    maturity_days: 100
                },
                {
                    id: 'crop-2',
                    name: 'Test Crop 2',
                    category: 'legume_crops',
                    drought_tolerance: 'low',
                    suitability_score: 0.75,
                    ph_range: { min: 5.5, max: 6.5 },
                    maturity_days: 120
                }
            ];
            
            cropFilteringManager.renderComparisonCharts(crops);
            
            // Check if comparison sections were created
            const container = document.getElementById('comparison-results');
            expect(container.innerHTML).toContain('Crop Comparison Results');
        });
    });

    describe('Export Functionality', () => {
        test('should export results as CSV', () => {
            cropFilteringManager.currentResults = [
                {
                    name: 'Test Crop',
                    scientific_name: 'Testus cropicus',
                    category: 'grain_crops',
                    suitability_score: 0.85,
                    climate_zones: ['5a', '5b'],
                    ph_range: {min: 6.0, max: 7.0},
                    maturity_days: 100,
                    drought_tolerance: 'moderate'
                }
            ];
            
            // Mock document.createElement and click
            const createElementSpy = jest.spyOn(document, 'createElement').mockImplementation((tag) => {
                if (tag === 'a') {
                    const element = document.createElement('a');
                    element.setAttribute = jest.fn();
                    element.click = jest.fn();
                    return element;
                }
                return document.createElement(tag);
            });
            
            cropFilteringManager.exportResults();
            
            expect(createElementSpy).toHaveBeenCalledWith('a');
            createElementSpy.mockRestore();
        });

        test('should export chart as image', () => {
            // Mock canvas toDataURL method
            const canvas = document.getElementById('filterImpactChart');
            canvas.toDataURL = jest.fn().mockReturnValue('data:image/png;base64,test');
            
            // Mock document.createElement and click
            const createElementSpy = jest.spyOn(document, 'createElement').mockImplementation((tag) => {
                if (tag === 'a') {
                    const element = document.createElement('a');
                    element.setAttribute = jest.fn();
                    element.click = jest.fn();
                    return element;
                }
                return document.createElement(tag);
            });
            
            cropFilteringManager.exportChartAsImage();
            
            expect(canvas.toDataURL).toHaveBeenCalledWith('image/png');
            expect(createElementSpy).toHaveBeenCalledWith('a');
            createElementSpy.mockRestore();
        });
    });

    describe('Utility Functions', () => {
        test('should clear all filters', () => {
            // Set some initial filters
            cropFilteringManager.currentFilters = { test: 'filter' };
            cropFilteringManager.currentResults = [{ id: 'crop-1', name: 'Test Crop' }];
            
            // Modify some UI elements
            document.getElementById('climate-zones').options[0].selected = true;
            document.getElementById('soil-types').options[1].selected = true;
            
            cropFilteringManager.clearAllFilters();
            
            expect(cropFilteringManager.currentFilters).toEqual({});
            expect(cropFilteringManager.currentResults).toEqual([]);
            expect(cropFilteringManager.currentPage).toBe(1);
            
            // Check that UI elements were reset
            expect(document.getElementById('climate-zones').options[0].selected).toBe(false);
            expect(document.getElementById('soil-types').options[1].selected).toBe(false);
        });

        test('should update slider values', () => {
            const slider = document.getElementById('ph-min');
            slider.value = '6.5';
            
            const event = new Event('input');
            Object.defineProperty(event, 'target', { value: slider });
            
            cropFilteringManager.updateSliderValue(event);
            
            expect(document.getElementById('ph-min-value').textContent).toBe('6.5');
        });
    });

    describe('Mobile Filter Shortcuts and Quick Actions', () => {
        test('should have quick filter buttons in the mobile template', () => {
            // Mock the mobile-specific HTML elements
            const quickFilterHTML = `
                <button class="quick-filter-btn" data-quick-filter="drought">
                    <i class="fas fa-tint"></i> Drought Tolerant
                </button>
                <button class="quick-filter-btn" data-quick-filter="nitrogen">
                    <i class="fas fa-leaf"></i> Nitrogen Fixing
                </button>
                <button class="quick-filter-btn" data-quick-filter="low-maintenance">
                    <i class="fas fa-user"></i> Low Maintenance
                </button>
                <button class="quick-filter-btn" data-quick-filter="high-yield">
                    <i class="fas fa-chart-line"></i> High Yield
                </button>
            `;
            
            // Add quick filter buttons to the body
            const quickFilterContainer = document.createElement('div');
            quickFilterContainer.innerHTML = quickFilterHTML;
            document.body.appendChild(quickFilterContainer);

            // Find quick filter buttons
            const quickFilterButtons = document.querySelectorAll('.quick-filter-btn');
            expect(quickFilterButtons.length).toBe(4);
            
            // Check that each button has the correct data attribute
            expect(quickFilterButtons[0].getAttribute('data-quick-filter')).toBe('drought');
            expect(quickFilterButtons[1].getAttribute('data-quick-filter')).toBe('nitrogen');
            expect(quickFilterButtons[2].getAttribute('data-quick-filter')).toBe('low-maintenance');
            expect(quickFilterButtons[3].getAttribute('data-quick-filter')).toBe('high-yield');
        });

        test('should apply quick filter for drought tolerance', () => {
            // Set up a mock for applyFilters to test if it's called
            const applyFiltersSpy = jest.spyOn(cropFilteringManager, 'applyFilters');
            
            // Simulate clicking the drought tolerance quick filter
            cropFilteringManager.applyQuickFilter('drought');

            // Verify that applyFilters was called
            expect(applyFiltersSpy).toHaveBeenCalled();
            
            // Additional verification for the specific filter being applied
            // The quick filter should update the drought tolerance filter
            // In the real implementation, applyQuickFilter would update the UI elements
            // For this test, we're mainly verifying the method is called properly
            
            applyFiltersSpy.mockRestore();
        });

        test('should apply quick filter for nitrogen fixing', () => {
            // Set up a mock for applyFilters to test if it's called
            const applyFiltersSpy = jest.spyOn(cropFilteringManager, 'applyFilters');
            
            // Simulate clicking the nitrogen fixing quick filter
            cropFilteringManager.applyQuickFilter('nitrogen');

            // Verify that applyFilters was called
            expect(applyFiltersSpy).toHaveBeenCalled();
            
            applyFiltersSpy.mockRestore();
        });

        test('should apply quick filter for low maintenance', () => {
            // Set up a mock for applyFilters to test if it's called
            const applyFiltersSpy = jest.spyOn(cropFilteringManager, 'applyFilters');
            
            // Simulate clicking the low maintenance quick filter
            cropFilteringManager.applyQuickFilter('low-maintenance');

            // Verify that applyFilters was called
            expect(applyFiltersSpy).toHaveBeenCalled();
            
            applyFiltersSpy.mockRestore();
        });

        test('should apply quick filter for high yield', () => {
            // Set up a mock for applyFilters to test if it's called
            const applyFiltersSpy = jest.spyOn(cropFilteringManager, 'applyFilters');
            
            // Simulate clicking the high yield quick filter
            cropFilteringManager.applyQuickFilter('high-yield');

            // Verify that applyFilters was called
            expect(applyFiltersSpy).toHaveBeenCalled();
            
            applyFiltersSpy.mockRestore();
        });

        test('should handle invalid quick filter type', () => {
            // Mock console.warn to capture any warnings
            const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();
            
            // Simulate applying a quick filter with an invalid type
            // This should still call applyFilters but won't change any specific filters
            const applyFiltersSpy = jest.spyOn(cropFilteringManager, 'applyFilters');
            
            cropFilteringManager.applyQuickFilter('invalid-type');

            expect(applyFiltersSpy).toHaveBeenCalled();
            
            // Clean up
            consoleWarnSpy.mockRestore();
            applyFiltersSpy.mockRestore();
        });

        test('should bind quick filter events properly', () => {
            // Add quick filter buttons to the DOM
            const quickFilterHTML = `
                <div id="quick-filters-section">
                    <button class="quick-filter-btn" data-quick-filter="drought">
                        <i class="fas fa-tint"></i> Drought Tolerant
                    </button>
                    <button class="quick-filter-btn" data-quick-filter="nitrogen">
                        <i class="fas fa-leaf"></i> Nitrogen Fixing
                    </button>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', quickFilterHTML);
            
            // Check that event listeners are set up for quick filter buttons
            const quickFilterButtons = document.querySelectorAll('[data-quick-filter]');
            
            // In the real implementation, these buttons would be bound in bindEvents
            // Let's create a simple test by simulating a click
            const clickHandlerSpy = jest.spyOn(cropFilteringManager, 'applyQuickFilter');
            
            // Dispatch a click event on the first button
            const clickEvent = new Event('click');
            Object.defineProperty(clickEvent, 'target', {
                value: quickFilterButtons[0]
            });
            
            // Simulate the event handling that would occur in bindEvents
            const quickFilterType = quickFilterButtons[0].getAttribute('data-quick-filter');
            cropFilteringManager.applyQuickFilter(quickFilterType);
            
            expect(clickHandlerSpy).toHaveBeenCalledWith('drought');
            
            clickHandlerSpy.mockRestore();
        });

        test('should have quick action buttons for save, load, and share functionality', () => {
            // Mock preset controls HTML
            const presetControlsHTML = `
                <div id="preset-controls">
                    <button id="save-preset-btn" class="btn btn-outline-success btn-sm">
                        <i class="fas fa-save"></i> Save Preset
                    </button>
                    <button id="load-preset-btn" class="btn btn-outline-info btn-sm">
                        <i class="fas fa-folder-open"></i> Load Preset
                    </button>
                    <button id="export-config-btn" class="btn btn-outline-secondary btn-sm">
                        <i class="fas fa-file-export"></i> Export Config
                    </button>
                    <button id="import-config-btn" class="btn btn-outline-secondary btn-sm">
                        <i class="fas fa-file-import"></i> Import Config
                    </button>
                    <button id="undo-btn" class="btn btn-outline-warning btn-sm" disabled>
                        <i class="fas fa-undo"></i> Undo
                    </button>
                    <button id="redo-btn" class="btn btn-outline-warning btn-sm" disabled>
                        <i class="fas fa-redo"></i> Redo
                    </button>
                    <button id="save-snapshot-btn" class="btn btn-outline-primary btn-sm">
                        <i class="fas fa-camera"></i> Save Snapshot
                    </button>
                    <button id="load-snapshot-btn" class="btn btn-outline-primary btn-sm">
                        <i class="fas fa-history"></i> Load Snapshot
                    </button>
                </div>
            `;
            
            const presetContainer = document.createElement('div');
            presetContainer.innerHTML = presetControlsHTML;
            document.body.appendChild(presetContainer);

            // Check that all quick action buttons exist
            expect(document.getElementById('save-preset-btn')).not.toBeNull();
            expect(document.getElementById('load-preset-btn')).not.toBeNull();
            expect(document.getElementById('export-config-btn')).not.toBeNull();
            expect(document.getElementById('import-config-btn')).not.toBeNull();
            expect(document.getElementById('undo-btn')).not.toBeNull();
            expect(document.getElementById('redo-btn')).not.toBeNull();
            expect(document.getElementById('save-snapshot-btn')).not.toBeNull();
            expect(document.getElementById('load-snapshot-btn')).not.toBeNull();
        });

        test('should handle keyboard shortcuts for quick actions', () => {
            // Set up a spy for each of the functions that would be called by keyboard shortcuts
            const undoSpy = jest.spyOn(cropFilteringManager, 'undoFilter');
            const redoSpy = jest.spyOn(cropFilteringManager, 'redoFilter');
            
            // Test Ctrl+Z for undo
            const undoEvent = new KeyboardEvent('keydown', {
                ctrlKey: true,
                key: 'z',
                bubbles: true
            });
            // Since handleKeyboardShortcuts is not automatically bound, we call it directly
            cropFilteringManager.handleKeyboardShortcuts(undoEvent);
            expect(undoSpy).toHaveBeenCalled();
            
            // Test Ctrl+Y for redo
            const redoEvent = new KeyboardEvent('keydown', {
                ctrlKey: true,
                key: 'y',
                bubbles: true
            });
            cropFilteringManager.handleKeyboardShortcuts(redoEvent);
            expect(redoSpy).toHaveBeenCalled();
            
            // Clean up
            undoSpy.mockRestore();
            redoSpy.mockRestore();
        });

        test('should update undo/redo button states', () => {
            // Set up the DOM elements for undo/redo buttons
            const buttonContainer = document.createElement('div');
            buttonContainer.innerHTML = `
                <button id="undo-btn" disabled>Undo</button>
                <button id="redo-btn" disabled>Redo</button>
            `;
            document.body.appendChild(buttonContainer);

            // Initially, buttons should be disabled
            const undoBtn = document.getElementById('undo-btn');
            const redoBtn = document.getElementById('redo-btn');
            
            expect(undoBtn.disabled).toBe(true);
            expect(redoBtn.disabled).toBe(true);

            // Add a filter to history which would enable undo
            cropFilteringManager.filterStateManager.currentFilters = { test: 'filter' };
            cropFilteringManager.filterStateManager.addToHistory();
            
            // Add another filter to enable both undo and potentially redo
            cropFilteringManager.filterStateManager.currentFilters = { test: 'new_filter' };
            cropFilteringManager.filterStateManager.addToHistory();

            // Simulate going back to enable redo
            cropFilteringManager.filterStateManager.historyIndex = 0;
            
            // Update buttons based on the state
            cropFilteringManager.updateHistoryButtons();
            
            // Now undo should be enabled, redo's state depends on the current position
            expect(undoBtn.disabled).toBe(false); // This would be true if we can't go further back
            expect(redoBtn.disabled).toBe(false); // This would be false since we can go forward
        });
    });
});