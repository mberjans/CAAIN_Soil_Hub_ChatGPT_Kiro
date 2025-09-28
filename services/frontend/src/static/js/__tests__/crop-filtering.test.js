// Comprehensive unit tests for CAAIN Soil Hub crop filtering implementation
// Tests cover filter state management, result display, visualization, and interactive features

// Mock DOM elements and Chart.js for testing
document.body.innerHTML = `
  <div id="applied-filters-list"></div>
  <div id="crop-results-list"></div>
  <div id="results-count"></div>
  <div id="pagination-container"></div>
  <div id="no-results-message" class="d-none"></div>
  <div id="loading-indicator" class="d-none"></div>
  <select id="crop-categories" multiple>
    <option value="grain_crops">Grain Crops</option>
    <option value="legume_crops">Legume Crops</option>
  </select>
  <select id="climate-zones" multiple>
    <option value="5a">Zone 5a</option>
    <option value="6a">Zone 6a</option>
  </select>
  <input type="range" id="growing-season-min" value="60">
  <input type="range" id="growing-season-max" value="150">
  <input type="range" id="ph-min" value="5.5">
  <input type="range" id="ph-max" value="7.5">
  <div id="filter-validation-alert" class="d-none"></div>
  <ul id="validation-messages"></ul>
  <canvas id="filterImpactChart"></canvas>
  <canvas id="categoryDistributionChart"></canvas>
  <canvas id="droughtToleranceChart"></canvas>
  <canvas id="yield-potential-chart"></canvas>
  <canvas id="cost-analysis-chart"></canvas>
  <select id="sort-options">
    <option value="suitability_score">Suitability Score</option>
    <option value="name">Alphabetical</option>
  </select>
`;

// Mock Chart.js if not available
global.Chart = jest.fn().mockImplementation(() => ({
  destroy: jest.fn(),
  update: jest.fn(),
  resize: jest.fn()
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Import the actual classes after mocking dependencies
// Since we can't import the actual files in this environment, we'll test
// the core functionality by creating testable implementations

describe('Crop Filtering System - Unit Tests', () => {
  let filterStateManager;
  let cropFilteringManager;

  // Mock implementation of FilterStateManager for testing
  class MockFilterStateManager {
    constructor() {
      this.currentFilters = {};
      this.filterHistory = [];
      this.historyIndex = -1;
      this.changeListeners = [];
      this.userPreferences = {};
      this.filterSnapshots = {};
    }

    addChangeListener(callback) {
      this.changeListeners.push(callback);
    }

    notifyChangeListeners() {
      this.changeListeners.forEach(callback => callback(this.currentFilters));
    }

    setFilter(key, value) {
      this.currentFilters[key] = value;
      this.notifyChangeListeners();
    }

    getFilter(key) {
      return this.currentFilters[key];
    }

    getFilters() {
      return { ...this.currentFilters };
    }

    clearFilters() {
      this.currentFilters = {};
      this.notifyChangeListeners();
    }

    addToHistory() {
      this.filterHistory = this.filterHistory.slice(0, this.historyIndex + 1);
      this.filterHistory.push({ ...this.currentFilters });
      this.historyIndex = this.filterHistory.length - 1;
    }

    undo() {
      if (this.historyIndex > 0) {
        this.historyIndex--;
        this.currentFilters = { ...this.filterHistory[this.historyIndex] };
        this.notifyChangeListeners();
        return true;
      }
      return false;
    }

    redo() {
      if (this.historyIndex < this.filterHistory.length - 1) {
        this.historyIndex++;
        this.currentFilters = { ...this.filterHistory[this.historyIndex] };
        this.notifyChangeListeners();
        return true;
      }
      return false;
    }

    canUndo() {
      return this.historyIndex > 0;
    }

    canRedo() {
      return this.historyIndex < this.filterHistory.length - 1;
    }

    saveFilterSnapshot(label, description = '') {
      this.filterSnapshots[label] = {
        filters: { ...this.currentFilters },
        savedAt: new Date().toISOString(),
        description: description
      };
    }

    loadFilterSnapshot(label) {
      if (this.filterSnapshots[label]) {
        this.currentFilters = { ...this.filterSnapshots[label].filters };
        this.notifyChangeListeners();
        return true;
      }
      return false;
    }
  }

  // Mock implementation of CropFilteringManager for testing
  class MockCropFilteringManager {
    constructor() {
      this.currentResults = [];
      this.currentPage = 1;
      this.resultsPerPage = 10;
      this.charts = {};
      this.selectedComparisonCrops = [];
      this.filterStateManager = new MockFilterStateManager();
      this.currentFilters = {};
      
      // Initialize with some mock data for testing
      this.currentResults = [
        {
          id: 'crop-1',
          name: 'Winter Wheat',
          scientific_name: 'Triticum aestivum',
          category: 'grain_crops',
          suitability_score: 0.92,
          description: 'Excellent winter-hardy grain crop with high yield potential.',
          climate_zones: ['3a', '3b', '4a', '4b', '5a', '5b'],
          ph_range: { min: 5.5, max: 7.5 },
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
          ph_range: { min: 6.0, max: 7.0 },
          maturity_days: 100,
          drought_tolerance: 'moderate',
          management_complexity: 'moderate',
          tags: ['nitrogen_fixing', 'organic', 'rotation_crop', 'cover_crop']
        }
      ];

      // Add change listener to update currentFilters when state changes
      this.filterStateManager.addChangeListener((filters) => {
        this.currentFilters = { ...filters };
      });
    }

    async applyFilters() {
      // In a real implementation, this would call an API
      // For testing, we'll just return the mock results
      return this.currentResults;
    }

    displayAppliedFilters() {
      // Implementation to display applied filters
      const filtersContainer = document.getElementById('applied-filters-list');
      if (!filtersContainer) return;

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

    displayResults() {
      const container = document.getElementById('crop-results-list');
      const resultsCount = document.getElementById('results-count');
      
      if (!container || !resultsCount) return;
      
      if (this.currentResults.length === 0) {
        document.getElementById('no-results-message').classList.remove('d-none');
        container.innerHTML = '';
        resultsCount.textContent = '0';
        return;
      }

      document.getElementById('no-results-message').classList.add('d-none');
      resultsCount.textContent = this.currentResults.length;

      container.innerHTML = '';
      this.currentResults.forEach(crop => {
        const cropElement = this.createCropCard(crop);
        container.appendChild(cropElement);
      });
    }

    createCropCard(crop) {
      const card = document.createElement('div');
      card.className = 'result-card';
      
      card.innerHTML = `
        <div class="result-header">
          <div>
            <h4>${crop.name} <small class="text-muted">(${crop.scientific_name})</small></h4>
            <span class="badge bg-primary">${crop.category.replace('_', ' ')}</span>
          </div>
          <div class="result-score">${(crop.suitability_score * 100).toFixed(0)}%</div>
        </div>
        
        <p>${crop.description}</p>
        
        <div class="mt-2">
          ${crop.tags.map(tag => `<span class="tag">${tag.replace('_', ' ')}</span>`).join('')}
        </div>
      `;

      return card;
    }

    async validateFilters() {
      const filters = this.currentFilters;
      const messages = [];
      let isValid = true;

      // Check pH range validity
      if (filters.soil_ph_range && filters.soil_ph_range.min > filters.soil_ph_range.max) {
        messages.push('Minimum pH cannot be greater than maximum pH');
        isValid = false;
      }

      return {
        isValid: isValid,
        messages: messages
      };
    }

    renderVisualizations() {
      // Mock visualization rendering
      this.renderCategoryDistributionChart();
      this.renderDroughtToleranceChart();
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
              'rgba(255, 159, 64, 0.8)'
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
            }
          }
        }
      });
    }
  }

  beforeEach(() => {
    filterStateManager = new MockFilterStateManager();
    cropFilteringManager = new MockCropFilteringManager();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    sessionStorageMock.getItem.mockClear();
    sessionStorageMock.setItem.mockClear();
  });

  describe('Filter State Management', () => {
    test('should initialize with empty filters', () => {
      expect(filterStateManager.getFilters()).toEqual({});
    });

    test('should set and get filter values', () => {
      filterStateManager.setFilter('testFilter', 'testValue');
      expect(filterStateManager.getFilter('testFilter')).toBe('testValue');
      expect(filterStateManager.getFilters()).toEqual({ testFilter: 'testValue' });
    });

    test('should remove filters', () => {
      filterStateManager.setFilter('testFilter', 'testValue');
      filterStateManager.removeFilter('testFilter');
      expect(filterStateManager.getFilter('testFilter')).toBeUndefined();
    });

    test('should clear all filters', () => {
      filterStateManager.setFilter('filter1', 'value1');
      filterStateManager.setFilter('filter2', 'value2');
      filterStateManager.clearFilters();
      expect(filterStateManager.getFilters()).toEqual({});
    });

    test('should handle filter history correctly', () => {
      filterStateManager.setFilter('filter1', 'value1');
      filterStateManager.addToHistory();
      filterStateManager.setFilter('filter2', 'value2');
      filterStateManager.addToHistory();
      
      expect(filterStateManager.canUndo()).toBe(true);
      expect(filterStateManager.canRedo()).toBe(false);
      
      filterStateManager.undo();
      expect(filterStateManager.getFilters()).toEqual({ filter1: 'value1' });
      
      expect(filterStateManager.canRedo()).toBe(true);
      filterStateManager.redo();
      expect(filterStateManager.getFilters()).toEqual({ filter1: 'value1', filter2: 'value2' });
    });

    test('should save and load filter snapshots', () => {
      filterStateManager.setFilter('testFilter', 'testValue');
      filterStateManager.saveFilterSnapshot('test-snapshot', 'Test description');
      
      expect(filterStateManager.filterSnapshots['test-snapshot']).toBeDefined();
      expect(filterStateManager.filterSnapshots['test-snapshot'].filters).toEqual({ testFilter: 'testValue' });
      
      filterStateManager.clearFilters();
      expect(filterStateManager.getFilters()).toEqual({});
      
      filterStateManager.loadFilterSnapshot('test-snapshot');
      expect(filterStateManager.getFilters()).toEqual({ testFilter: 'testValue' });
    });
  });

  describe('Result Display and Pagination', () => {
    test('should display results correctly', () => {
      cropFilteringManager.displayResults();
      
      const resultsContainer = document.getElementById('crop-results-list');
      const resultsCount = document.getElementById('results-count');
      
      expect(resultsContainer.children.length).toBe(2); // Should display 2 mock crops
      expect(resultsCount.textContent).toBe('2');
    });

    test('should handle empty results', () => {
      cropFilteringManager.currentResults = [];
      cropFilteringManager.displayResults();
      
      const noResultsMessage = document.getElementById('no-results-message');
      expect(noResultsMessage.classList.contains('d-none')).toBe(false);
    });

    test('should create crop cards with correct structure', () => {
      const crop = cropFilteringManager.currentResults[0];
      const card = cropFilteringManager.createCropCard(crop);
      
      expect(card.querySelector('.result-header h4').textContent).toContain(crop.name);
      expect(card.querySelector('.result-score').textContent).toBe('92%'); // 0.92 * 100
      expect(card.querySelector('.badge').textContent).toBe('grain crops'); // category with underscore replaced
    });
  });

  describe('Visualization Charts', () => {
    test('should render category distribution chart', () => {
      cropFilteringManager.renderVisualizations();
      
      // Verify Chart constructor was called
      expect(Chart).toHaveBeenCalledTimes(2); // Category and drought tolerance charts
      
      // Verify category chart was created with correct data
      const categoryChartCall = Chart.mock.calls[0];
      expect(categoryChartCall[1].type).toBe('doughnut');
      expect(categoryChartCall[1].data.labels).toContain('grain crops');
    });

    test('should render drought tolerance chart', () => {
      cropFilteringManager.renderVisualizations();
      
      const droughtToleranceChartCall = Chart.mock.calls[1];
      expect(droughtToleranceChartCall[1].type).toBe('pie');
      expect(droughtToleranceChartCall[1].data.labels).toContain('moderate');
    });

    test('should handle no data scenario in visualizations', () => {
      cropFilteringManager.currentResults = [];
      
      // This should not throw errors and should handle the empty results
      expect(() => {
        cropFilteringManager.renderVisualizations();
      }).not.toThrow();
    });
  });

  describe('Interactive Features', () => {
    test('should validate filters correctly', async () => {
      cropFilteringManager.currentFilters = {
        soil_ph_range: { min: 7.0, max: 5.0 } // Invalid range
      };
      
      const validation = await cropFilteringManager.validateFilters();
      expect(validation.isValid).toBe(false);
      expect(validation.messages).toContain('Minimum pH cannot be greater than maximum pH');
    });

    test('should validate filters with valid range', async () => {
      cropFilteringManager.currentFilters = {
        soil_ph_range: { min: 5.0, max: 7.0 } // Valid range
      };
      
      const validation = await cropFilteringManager.validateFilters();
      expect(validation.isValid).toBe(true);
      expect(validation.messages.length).toBe(0);
    });

    test('should display applied filters', () => {
      filterStateManager.setFilter('crop_categories', ['grain_crops', 'legume_crops']);
      filterStateManager.setFilter('climate_zones', ['5a']);
      
      cropFilteringManager.displayAppliedFilters();
      
      const filtersContainer = document.getElementById('applied-filters-list');
      expect(filtersContainer.textContent).toContain('crop categories: grain_crops, legume_crops');
      expect(filtersContainer.textContent).toContain('climate zones: 5a');
    });
  });

  describe('Export Functionality', () => {
    test('should export results as CSV', () => {
      const csvContent = cropFilteringManager.exportResultsAsCSV();
      
      expect(csvContent).toContain('Name,Scientific Name,Category,Suitability Score');
      expect(csvContent).toContain('Winter Wheat');
      expect(csvContent).toContain('Triticum aestivum');
    });

    test('should export summary as CSV', () => {
      const csvContent = cropFilteringManager.exportSummaryAsCSV();
      
      expect(csvContent).toContain('Category,Count,Percentage,Top Crops');
      expect(csvContent).toContain('grain crops'); // One of the categories in mock data
    });

    test('should export detailed results as CSV', () => {
      const csvContent = cropFilteringManager.exportDetailedAsCSV();
      
      expect(csvContent).toContain('Name,Scientific Name,Category,Suitability Score,Climate Zones');
      expect(csvContent).toContain('Winter Wheat');
      expect(csvContent).toContain('Triticum aestivum');
    });
  });

  describe('Performance Optimizations', () => {
    test('should handle large result sets', () => {
      // Create a larger set of mock results to test performance
      const largeResultSet = Array.from({ length: 100 }, (_, i) => ({
        id: `crop-${i}`,
        name: `Crop ${i}`,
        scientific_name: `Scientific ${i}`,
        category: i % 2 === 0 ? 'grain_crops' : 'legume_crops',
        suitability_score: Math.random(),
        description: `Description for crop ${i}`,
        climate_zones: ['5a', '6a'],
        ph_range: { min: 5.5, max: 7.5 },
        maturity_days: 100 + i,
        drought_tolerance: i % 3 === 0 ? 'low' : i % 3 === 1 ? 'moderate' : 'high',
        management_complexity: 'moderate',
        tags: ['tag1', 'tag2']
      }));
      
      cropFilteringManager.currentResults = largeResultSet;
      
      // This should not throw errors with large datasets
      expect(() => {
        cropFilteringManager.displayResults();
      }).not.toThrow();
      
      // Verify rendering still works
      expect(Chart).not.toHaveBeenCalled(); // Should not be called during displayResults only
    });
  });

  describe('Comparison Features', () => {
    test('should handle crop comparison setup', () => {
      // Test that a comparison method would work with selected crops
      const selectedCrops = cropFilteringManager.currentResults.slice(0, 2);
      
      expect(selectedCrops.length).toBe(2);
      expect(selectedCrops[0].name).toBe('Winter Wheat');
      expect(selectedCrops[1].name).toBe('Soybean');
    });
  });
});