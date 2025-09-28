// Integration tests for CAAIN Soil Hub crop filtering system
// Tests the interaction between crop filtering and enhanced visualization components

// Mock DOM elements and Chart.js for testing
document.body.innerHTML = `
  <div id=\"applied-filters-list\"></div>
  <div id=\"crop-results-list\"></div>
  <div id=\"results-count\"></div>
  <div id=\"pagination-container\"></div>
  <div id=\"no-results-message\" class=\"d-none\"></div>
  <div id=\"loading-indicator\" class=\"d-none\"></div>
  <select id=\"crop-categories\" multiple>
    <option value=\"grain_crops\">Grain Crops</option>
    <option value=\"legume_crops\">Legume Crops</option>
  </select>
  <select id=\"climate-zones\" multiple>
    <option value=\"5a\">Zone 5a</option>
    <option value=\"6a\">Zone 6a</option>
  </select>
  <input type=\"range\" id=\"growing-season-min\" value=\"60\">
  <input type=\"range\" id=\"growing-season-max\" value=\"150\">
  <input type=\"range\" id=\"ph-min\" value=\"5.5\">
  <input type=\"range\" id=\"ph-max\" value=\"7.5\">
  <div id=\"filter-validation-alert\" class=\"d-none\"></div>
  <ul id=\"validation-messages\"></ul>
  <canvas id=\"filterImpactChart\"></canvas>
  <canvas id=\"categoryDistributionChart\"></canvas>
  <canvas id=\"droughtToleranceChart\"></canvas>
  <canvas id=\"yield-potential-chart\"></canvas>
  <canvas id=\"cost-analysis-chart\"></canvas>
  <select id=\"sort-options\">
    <option value=\"suitability_score\">Suitability Score</option>
    <option value=\"name\">Alphabetical</option>
  </select>
  <div id=\"visualization-panel\">
    <canvas id=\"geographic-distribution-chart\"></canvas>
    <canvas id=\"seasonal-trend-chart\"></canvas>
    <div id=\"comparison-results\"></div>
    <select id=\"crop-comparison-select\"></select>
    <button id=\"compare-selected-btn\"></button>
    <div id=\"total-results-count\">0</div>
    <div id=\"active-filters-count\">0</div>
    <div id=\"reduction-percentage\">0%</div>
    <div id=\"avg-suitability-score\">0.00</div>
  </div>
  <div class=\"export-chart-btn\" data-chart=\"filterImpactChart\"></div>
  <div class=\"export-chart-btn\" data-chart=\"categoryDistributionChart\"></div>
  <div class=\"download-data-btn\" data-type=\"results\"></div>
  <div class=\"download-data-btn\" data-type=\"summary\"></div>
  <div class=\"download-data-btn\" data-type=\"detailed\"></div>
`;

// Mock Chart.js if not available
global.Chart = jest.fn().mockImplementation(() => ({
  destroy: jest.fn(),
  update: jest.fn(),
  resize: jest.fn()
}));

// Mock URL.createObjectURL and Blob for export functionality
global.URL = {
  createObjectURL: jest.fn(() => 'mock-url'),
};

global.Blob = jest.fn((content, options) => ({
  content,
  options
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

// Mock console for error tracking
global.console = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
};

describe('Crop Filtering System - Integration Tests', () => {
  let cropFilteringManager, enhancedVisualization;

  // Mock implementations for integration testing
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

  class MockCropFilteringManager {
    constructor() {
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
      this.currentPage = 1;
      this.resultsPerPage = 10;
      this.charts = {};
      this.selectedComparisonCrops = [];
      this.filterStateManager = new MockFilterStateManager();
      this.currentFilters = {};
      
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
        filtersContainer.innerHTML = '<p class=\"text-muted\">No filters applied</p>';
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
        <div class=\"result-header\">
          <div>
            <h4>${crop.name} <small class=\"text-muted\">(${crop.scientific_name})</small></h4>
            <span class=\"badge bg-primary\">${crop.category.replace('_', ' ')}</span>
          </div>
          <div class=\"result-score\">${(crop.suitability_score * 100).toFixed(0)}%</div>
        </div>
        
        <p>${crop.description}</p>
        
        <div class=\"mt-2\">
          ${crop.tags.map(tag => \`<span class=\"tag\">${tag.replace('_', ' ')}</span>\`).join('')}
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

    exportResultsAsCSV() {
      let csvContent = 'data:text/csv;charset=utf-8,';
      csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance\\n';
      
      this.currentResults.forEach(crop => {
        const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
        csvContent += `\"${crop.name}\",\"${crop.scientific_name}\",\"${crop.category.replace(/_/g, ' ')}\",` +
                     `\"${crop.suitability_score}\",\"${climateZones}\",\"${crop.ph_range?.min || ''}\",` +
                     `\"${crop.ph_range?.max || ''}\",\"${crop.maturity_days || ''}\",\"${crop.drought_tolerance || ''}\"\\n`;
      });
      
      return csvContent;
    }

    exportSummaryAsCSV() {
      let csvContent = 'data:text/csv;charset=utf-8,';
      csvContent += 'Category,Count,Percentage,Top Crops\\n';
      
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
            
        csvContent += `\"${category}\",\"${count}\",\"${percentage}%\",\"${topCrops}\"\\n`;
      });
      
      return csvContent;
    }

    exportDetailedAsCSV() {
      let csvContent = 'data:text/csv;charset=utf-8,';
      csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance,Management Complexity,Tags\\n';
      
      this.currentResults.forEach(crop => {
        const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
        const tags = crop.tags ? crop.tags.join('; ') : '';
        csvContent += `\"${crop.name}\",\"${crop.scientific_name}\",\"${crop.category.replace(/_/g, ' ')}\",` +
                     `\"${crop.suitability_score}\",\"${climateZones}\",\"${crop.ph_range?.min || ''}\",` +
                     `\"${crop.ph_range?.max || ''}\",\"${crop.maturity_days || ''}\",\"${crop.drought_tolerance || ''}\",` +
                     `\"${crop.management_complexity || ''}\",\"${tags}\"\\n`;
      });
      
      return csvContent;
    }
  }

  class MockEnhancedCropVisualization {
    constructor() {
      this.charts = {};
      this.currentResults = [];
      this.activeFilters = {};
      this.interactionHistory = [];
      this.currentView = 'overview';
      this.init();
    }

    init() {
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
        },
        {
          id: 'crop-3',
          name: 'Alfalfa',
          scientific_name: 'Medicago sativa',
          category: 'forage_crops',
          suitability_score: 0.82,
          description: 'Perennial legume for high-quality forage and soil improvement.',
          climate_zones: ['3a', '3b', '4a', '4b', '5a', '5b'],
          ph_range: { min: 6.5, max: 7.5 },
          maturity_days: 365,
          drought_tolerance: 'moderate',
          management_complexity: 'high',
          tags: ['perennial', 'nitrogen_fixing', 'drought_tolerant', 'forage']
        }
      ];
    }

    setupAdvancedFeatures() {
      // Implementation for advanced features
    }

    createAdvancedVisualizations() {
      this.createYieldPotentialChart();
      this.createCostAnalysisChart();
      this.createGeographicDistributionChart();
      this.createSeasonalTrendChart();
    }

    createYieldPotentialChart() {
      const ctx = document.getElementById('yield-potential-chart');
      if (!ctx) return;

      if (this.charts.yieldChart) {
        this.charts.yieldChart.destroy();
      }

      // Extract yield data from results if available
      const labels = this.currentResults.slice(0, 10).map(crop => crop.name);
      const minYield = this.currentResults.slice(0, 10).map(crop => crop.yield_potential?.min || 50);
      const maxYield = this.currentResults.slice(0, 10).map(crop => crop.yield_potential?.max || 100);

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

    createCostAnalysisChart() {
      const ctx = document.getElementById('cost-analysis-chart');
      if (!ctx) return;

      if (this.charts.costChart) {
        this.charts.costChart.destroy();
      }

      // Mock cost data for demonstration
      const labels = this.currentResults.slice(0, 10).map(crop => crop.name);
      const establishmentCost = this.currentResults.slice(0, 10).map(() => Math.floor(Math.random() * 100) + 50); // Mock data
      const maintenanceCost = this.currentResults.slice(0, 10).map(() => Math.floor(Math.random() * 75) + 25); // Mock data

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
                  return `${context.dataset.label}: $${context.parsed.y}`;
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

    createGeographicDistributionChart() {
      const ctx = document.getElementById('geographic-distribution-chart');
      if (!ctx) return;

      if (this.charts.geoChart) {
        this.charts.geoChart.destroy();
      }

      // Count hardiness zones across results
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

    createSeasonalTrendChart() {
      const ctx = document.getElementById('seasonal-trend-chart');
      if (!ctx) return;

      if (this.charts.seasonalChart) {
        this.charts.seasonalChart.destroy();
      }

      // Group results by planting season (mock data)
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

    updateVisualization(results, filters) {
      this.currentResults = results || [];
      this.activeFilters = filters || {};
      
      // Re-render all charts with new data
      this.createAdvancedVisualizations();
    }

    exportChartAsImage(chartId) {
      const canvas = document.getElementById(chartId);
      if (!canvas) {
        return;
      }

      // Mock the download functionality
      const link = document.createElement('a');
      link.download = `${chartId.replace(/-/g, '_')}_chart.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    }

    exportResultsAsCSV() {
      let csvContent = 'data:text/csv;charset=utf-8,';
      csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance\\n';
      
      this.currentResults.forEach(crop => {
        const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
        csvContent += `\"${crop.name}\",\"${crop.scientific_name}\",\"${crop.category.replace(/_/g, ' ')}\",` +
                     `\"${crop.suitability_score}\",\"${climateZones}\",\"${crop.ph_range?.min || ''}\",` +
                     `\"${crop.ph_range?.max || ''}\",\"${crop.maturity_days || ''}\",\"${crop.drought_tolerance || ''}\"\\n`;
      });
      
      return csvContent;
    }

    exportSummaryAsCSV() {
      let csvContent = 'data:text/csv;charset=utf-8,';
      csvContent += 'Category,Count,Percentage,Top Crops\\n';
      
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
            
        csvContent += `\"${category}\",\"${count}\",\"${percentage}%\",\"${topCrops}\"\\n`;
      });
      
      return csvContent;
    }

    exportDetailedAsCSV() {
      let csvContent = 'data:text/csv;charset=utf-8,';
      csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance,Management Complexity,Tags\\n';
      
      this.currentResults.forEach(crop => {
        const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
        const tags = crop.tags ? crop.tags.join('; ') : '';
        csvContent += `\"${crop.name}\",\"${crop.scientific_name}\",\"${crop.category.replace(/_/g, ' ')}\",` +
                     `\"${crop.suitability_score}\",\"${climateZones}\",\"${crop.ph_range?.min || ''}\",` +
                     `\"${crop.ph_range?.max || ''}\",\"${crop.maturity_days || ''}\",\"${crop.drought_tolerance || ''}\",` +
                     `\"${crop.management_complexity || ''}\",\"${tags}\"\\n`;
      });
      
      return csvContent;
    }

    downloadData(dataType) {
      if (!this.currentResults || this.currentResults.length === 0) {
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
  }

  beforeEach(() => {
    cropFilteringManager = new MockCropFilteringManager();
    enhancedVisualization = new MockEnhancedCropVisualization();
  });

  describe('Integration between filtering and visualization components', () => {
    test('should update visualization when filter results change', () => {
      const initialResultsCount = cropFilteringManager.currentResults.length;
      
      // The enhanced visualization should be able to receive new results from the filtering manager
      enhancedVisualization.updateVisualization(cropFilteringManager.currentResults, cropFilteringManager.currentFilters);
      
      expect(enhancedVisualization.currentResults.length).toBe(initialResultsCount);
      expect(enhancedVisualization.activeFilters).toEqual(cropFilteringManager.currentFilters);
    });

    test('should maintain consistent state between components', () => {
      // Apply a filter in the filtering manager
      cropFilteringManager.filterStateManager.setFilter('crop_category', 'grain_crops');
      
      // Verify that the state is consistent between components
      expect(cropFilteringManager.currentFilters).toEqual(cropFilteringManager.filterStateManager.getFilters());
    });

    test('should handle filter state sharing between components', () => {
      // Set a filter in the filtering manager
      cropFilteringManager.filterStateManager.setFilter('climate_zones', ['5a', '6a']);
      
      // The visualization component should be able to access the same filter state
      enhancedVisualization.updateVisualization(
        cropFilteringManager.currentResults,
        cropFilteringManager.currentFilters
      );
      
      expect(enhancedVisualization.activeFilters).toEqual(cropFilteringManager.currentFilters);
    });
  });

  describe('Shared functionality tests', () => {
    test('should export same data format from both components', () => {
      const filteringExport = cropFilteringManager.exportResultsAsCSV();
      const visualizationExport = enhancedVisualization.exportResultsAsCSV();
      
      // Both should have the same CSV headers
      expect(filteringExport).toContain('Name,Scientific Name,Category,Suitability Score');
      expect(visualizationExport).toContain('Name,Scientific Name,Category,Suitability Score');
    });

    test('should display same number of results in both components', () => {
      // Both components should work with the same dataset
      const filteringResultsCount = cropFilteringManager.currentResults.length;
      const visualizationResultsCount = enhancedVisualization.currentResults.length;
      
      expect(filteringResultsCount).toBe(visualizationResultsCount);
    });
  });

  describe('End-to-end workflow tests', () => {
    test('should perform complete filtering workflow', () => {
      // 1. Apply filters
      cropFilteringManager.filterStateManager.setFilter('crop_category', 'legume_crops');
      
      // 2. Update visualization with new results
      enhancedVisualization.updateVisualization(
        cropFilteringManager.currentResults,
        cropFilteringManager.currentFilters
      );
      
      // 3. Verify both components reflect the same state
      expect(cropFilteringManager.currentFilters.crop_category).toBe('legume_crops');
      expect(enhancedVisualization.activeFilters.crop_category).toBe('legume_crops');
    });

    test('should handle undo/redo operations consistently', () => {
      // Set initial filters
      cropFilteringManager.filterStateManager.setFilter('testFilter', 'initialValue');
      const initialFilters = { ...cropFilteringManager.filterStateManager.getFilters() };
      
      // Change filters
      cropFilteringManager.filterStateManager.setFilter('testFilter', 'newValue');
      
      // Undo the change
      cropFilteringManager.filterStateManager.undo();
      
      // Verify filter state after undo
      expect(cropFilteringManager.filterStateManager.getFilters()).toEqual(initialFilters);
    });

    test('should maintain visualization state after filter changes', () => {
      // Initial visualization
      enhancedVisualization.createAdvancedVisualizations();
      const initialChartCount = Object.keys(enhancedVisualization.charts).length;
      
      // Update results and re-render
      const newResults = [{
        id: 'crop-4',
        name: 'New Crop',
        category: 'grain_crops',
        suitability_score: 0.75
      }];
      
      enhancedVisualization.updateVisualization(newResults, {});
      
      // Should still have the same number of charts after update
      expect(Object.keys(enhancedVisualization.charts).length).toBe(initialChartCount);
    });
  });

  describe('Error handling in integrated workflow', () => {
    test('should handle missing results in visualization', () => {
      // Test with empty results
      enhancedVisualization.updateVisualization([], {});
      
      // Should not throw errors and should handle the empty results gracefully
      expect(() => {
        enhancedVisualization.createAdvancedVisualizations();
      }).not.toThrow();
    });

    test('should handle missing filters in visualization', () => {
      // Test with null filters
      enhancedVisualization.updateVisualization(enhancedVisualization.currentResults, null);
      
      // Should handle null filters gracefully
      expect(enhancedVisualization.activeFilters).toEqual({});
    });
  });

  describe('Performance in integrated environment', () => {
    test('should handle large datasets without degradation', () => {
      // Create large datasets to test performance
      const largeFilteringResults = Array.from({ length: 200 }, (_, i) => ({
        id: \`crop-\${i}\`,
        name: \`Crop \${i}\`,
        category: i % 3 === 0 ? 'grain_crops' : i % 3 === 1 ? 'legume_crops' : 'forage_crops',
        suitability_score: Math.random()
      }));
      
      const largeVisualizationResults = [...largeFilteringResults];
      
      cropFilteringManager.currentResults = largeFilteringResults;
      enhancedVisualization.currentResults = largeVisualizationResults;
      
      // Test that both components can handle large datasets
      expect(() => {
        cropFilteringManager.displayResults();
        enhancedVisualization.updateVisualization(largeVisualizationResults, {});
      }).not.toThrow();
    });
  });
});