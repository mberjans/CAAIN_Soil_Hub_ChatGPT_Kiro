// Setup file for Jest tests
// This file is run before each test file to set up the testing environment

// Mock global objects that are normally available in browser environment
global.Chart = jest.fn().mockImplementation(() => ({
  destroy: jest.fn(),
  update: jest.fn(),
  resize: jest.fn()
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
  removeItem: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
  removeItem: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock URL and Blob for export functionality
global.URL = {
  createObjectURL: jest.fn(() => 'mock-url'),
};

global.Blob = jest.fn((content, options) => ({
  content,
  options
}));

// Mock console for error tracking
global.console = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
};

// Set up a basic DOM environment
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
  <canvas id="geographic-distribution-chart"></canvas>
  <canvas id="seasonal-trend-chart"></canvas>
  <select id="sort-options">
    <option value="suitability_score">Suitability Score</option>
    <option value="name">Alphabetical</option>
  </select>
  <div id="visualization-panel">
    <div id="comparison-results"></div>
    <select id="crop-comparison-select"></select>
    <button id="compare-selected-btn"></button>
    <div id="total-results-count">0</div>
    <div id="active-filters-count">0</div>
    <div id="reduction-percentage">0%</div>
    <div id="avg-suitability-score">0.00</div>
  </div>
  <div class="export-chart-btn" data-chart="filterImpactChart"></div>
  <div class="export-chart-btn" data-chart="categoryDistributionChart"></div>
  <div class="download-data-btn" data-type="results"></div>
  <div class="download-data-btn" data-type="summary"></div>
  <div class="download-data-btn" data-type="detailed"></div>
`;