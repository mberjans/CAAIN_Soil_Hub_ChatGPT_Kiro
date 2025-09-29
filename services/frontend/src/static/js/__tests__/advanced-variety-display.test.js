/**
 * Advanced Variety Display Test Suite
 * 
 * Comprehensive tests for the advanced variety display and visualization system.
 */

// Mock DOM environment for testing
const { JSDOM } = require('jsdom');

// Create a mock DOM environment
const dom = new JSDOM(`
<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
</head>
<body>
    <div id="variety-display-container"></div>
    <div id="filter-stats"></div>
    <div id="selection-stats"></div>
    <div class="view-controls"></div>
    <select id="sort-criteria">
        <option value="overall_score">Overall Score</option>
        <option value="yield_potential">Yield Potential</option>
        <option value="disease_resistance">Disease Resistance</option>
        <option value="maturity_days">Maturity Days</option>
        <option value="confidence">Confidence</option>
        <option value="name">Name</option>
    </select>
    <select id="sort-direction">
        <option value="desc">High to Low</option>
        <option value="asc">Low to High</option>
    </select>
    <input type="range" id="min-score" min="0" max="1" step="0.01" value="0">
    <input type="range" id="max-score" min="0" max="1" step="0.01" value="1">
    <input type="range" id="min-confidence" min="0" max="1" step="0.01" value="0">
    <input type="range" id="max-confidence" min="0" max="1" step="0.01" value="1">
    <input type="range" id="min-maturity" min="0" max="365" step="1" value="0">
    <input type="range" id="max-maturity" min="0" max="365" step="1" value="365">
    <select id="disease-resistance">
        <option value="all">All Levels</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
    </select>
    <select id="company-filter">
        <option value="all">All Companies</option>
        <option value="Pioneer">Pioneer</option>
        <option value="Monsanto">Monsanto</option>
    </select>
</body>
</html>
`, {
    url: 'http://localhost',
    pretendToBeVisual: true,
    resources: 'usable'
});

global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;

// Mock localStorage
global.localStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
};

// Mock Chart.js
global.Chart = jest.fn().mockImplementation(() => ({
    destroy: jest.fn(),
    update: jest.fn(),
    render: jest.fn()
}));

// Load the AdvancedVarietyDisplay class
const AdvancedVarietyDisplay = require('../advanced-variety-display.js');

describe('AdvancedVarietyDisplay', () => {
    let display;
    let mockVarieties;

    beforeEach(() => {
        // Reset DOM
        document.body.innerHTML = `
            <div id="variety-display-container"></div>
            <div id="filter-stats"></div>
            <div id="selection-stats"></div>
            <div class="view-controls"></div>
            <select id="sort-criteria">
                <option value="overall_score">Overall Score</option>
                <option value="yield_potential">Yield Potential</option>
                <option value="disease_resistance">Disease Resistance</option>
                <option value="maturity_days">Maturity Days</option>
                <option value="confidence">Confidence</option>
                <option value="name">Name</option>
            </select>
            <select id="sort-direction">
                <option value="desc">High to Low</option>
                <option value="asc">Low to High</option>
            </select>
            <input type="range" id="min-score" min="0" max="1" step="0.01" value="0">
            <input type="range" id="max-score" min="0" max="1" step="0.01" value="1">
            <input type="range" id="min-confidence" min="0" max="1" step="0.01" value="0">
            <input type="range" id="max-confidence" min="0" max="1" step="0.01" value="1">
            <input type="range" id="min-maturity" min="0" max="365" step="1" value="0">
            <input type="range" id="max-maturity" min="0" max="365" step="1" value="365">
            <select id="disease-resistance">
                <option value="all">All Levels</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <select id="company-filter">
                <option value="all">All Companies</option>
                <option value="Pioneer">Pioneer</option>
                <option value="Monsanto">Monsanto</option>
            </select>
        `;

        // Reset localStorage mock
        localStorage.getItem.mockReturnValue(null);
        localStorage.setItem.mockClear();

        // Create new instance
        display = new AdvancedVarietyDisplay();

        // Mock variety data
        mockVarieties = [
            {
                id: '1',
                variety_name: 'Pioneer P1234',
                name: 'Pioneer P1234',
                company: 'Pioneer',
                overall_score: 0.92,
                confidence: 0.88,
                yield_expectation: { score: 'High' },
                maturity_days: 115,
                disease_resistance_level: 'high',
                disease_resistance_score: 0.85,
                individual_scores: {
                    yield_potential: 0.95,
                    disease_resistance: 0.85,
                    climate_adaptation: 0.90,
                    market_desirability: 0.88,
                    management_ease: 0.85,
                    risk_tolerance: 0.90
                },
                traits: [
                    { name: 'High Yield', category: 'yield' },
                    { name: 'Disease Resistant', category: 'disease' },
                    { name: 'Early Maturity', category: 'quality' }
                ],
                description: 'High-yielding corn variety with excellent disease resistance and early maturity.'
            },
            {
                id: '2',
                variety_name: 'Monsanto M5678',
                name: 'Monsanto M5678',
                company: 'Monsanto',
                overall_score: 0.87,
                confidence: 0.82,
                yield_expectation: { score: 'High' },
                maturity_days: 125,
                disease_resistance_level: 'medium',
                disease_resistance_score: 0.75,
                individual_scores: {
                    yield_potential: 0.90,
                    disease_resistance: 0.75,
                    climate_adaptation: 0.85,
                    market_desirability: 0.90,
                    management_ease: 0.80,
                    risk_tolerance: 0.85
                },
                traits: [
                    { name: 'High Yield', category: 'yield' },
                    { name: 'Market Preferred', category: 'market' },
                    { name: 'Drought Tolerant', category: 'quality' }
                ],
                description: 'Premium corn variety with high market desirability and drought tolerance.'
            },
            {
                id: '3',
                variety_name: 'Syngenta S9012',
                name: 'Syngenta S9012',
                company: 'Syngenta',
                overall_score: 0.79,
                confidence: 0.75,
                yield_expectation: { score: 'Medium' },
                maturity_days: 110,
                disease_resistance_level: 'high',
                disease_resistance_score: 0.90,
                individual_scores: {
                    yield_potential: 0.75,
                    disease_resistance: 0.90,
                    climate_adaptation: 0.80,
                    market_desirability: 0.70,
                    management_ease: 0.85,
                    risk_tolerance: 0.75
                },
                traits: [
                    { name: 'Disease Resistant', category: 'disease' },
                    { name: 'Easy Management', category: 'quality' },
                    { name: 'Early Maturity', category: 'quality' }
                ],
                description: 'Reliable corn variety with excellent disease resistance and easy management.'
            }
        ];
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Initialization', () => {
        test('should initialize with default values', () => {
            expect(display.varieties).toEqual([]);
            expect(display.filteredVarieties).toEqual([]);
            expect(display.selectedVarieties).toEqual(new Set());
            expect(display.sortCriteria).toBe('overall_score');
            expect(display.sortDirection).toBe('desc');
            expect(display.currentView).toBe('grid');
            expect(display.bookmarkedVarieties).toEqual(new Set());
            expect(display.expandedVarieties).toEqual(new Set());
        });

        test('should load bookmarks from localStorage', () => {
            localStorage.getItem.mockReturnValue('["1", "2"]');
            const newDisplay = new AdvancedVarietyDisplay();
            expect(newDisplay.bookmarkedVarieties).toEqual(new Set(['1', '2']));
        });

        test('should handle empty bookmarks in localStorage', () => {
            localStorage.getItem.mockReturnValue('[]');
            const newDisplay = new AdvancedVarietyDisplay();
            expect(newDisplay.bookmarkedVarieties).toEqual(new Set());
        });
    });

    describe('Data Loading', () => {
        test('should load varieties and render display', async () => {
            await display.loadVarieties(mockVarieties);
            
            expect(display.varieties).toEqual(mockVarieties);
            expect(display.filteredVarieties).toEqual(mockVarieties);
            expect(document.getElementById('variety-display-container').innerHTML).toContain('variety-grid-container');
        });

        test('should sort varieties by overall score initially', async () => {
            await display.loadVarieties(mockVarieties);
            
            const sortedVarieties = display.filteredVarieties;
            expect(sortedVarieties[0].overall_score).toBeGreaterThanOrEqual(sortedVarieties[1].overall_score);
            expect(sortedVarieties[1].overall_score).toBeGreaterThanOrEqual(sortedVarieties[2].overall_score);
        });
    });

    describe('Sorting', () => {
        beforeEach(async () => {
            await display.loadVarieties(mockVarieties);
        });

        test('should sort by overall score', () => {
            display.sortCriteria = 'overall_score';
            display.sortDirection = 'desc';
            display.sortVarieties();
            
            const sortedVarieties = display.filteredVarieties;
            expect(sortedVarieties[0].overall_score).toBe(0.92);
            expect(sortedVarieties[1].overall_score).toBe(0.87);
            expect(sortedVarieties[2].overall_score).toBe(0.79);
        });

        test('should sort by yield potential', () => {
            display.sortCriteria = 'yield_potential';
            display.sortDirection = 'desc';
            display.sortVarieties();
            
            const sortedVarieties = display.filteredVarieties;
            expect(sortedVarieties[0].individual_scores.yield_potential).toBe(0.95);
            expect(sortedVarieties[1].individual_scores.yield_potential).toBe(0.90);
            expect(sortedVarieties[2].individual_scores.yield_potential).toBe(0.75);
        });

        test('should sort by maturity days', () => {
            display.sortCriteria = 'maturity_days';
            display.sortDirection = 'asc';
            display.sortVarieties();
            
            const sortedVarieties = display.filteredVarieties;
            expect(sortedVarieties[0].maturity_days).toBe(110);
            expect(sortedVarieties[1].maturity_days).toBe(115);
            expect(sortedVarieties[2].maturity_days).toBe(125);
        });

        test('should sort by name alphabetically', () => {
            display.sortCriteria = 'name';
            display.sortDirection = 'asc';
            display.sortVarieties();
            
            const sortedVarieties = display.filteredVarieties;
            expect(sortedVarieties[0].variety_name).toBe('Monsanto M5678');
            expect(sortedVarieties[1].variety_name).toBe('Pioneer P1234');
            expect(sortedVarieties[2].variety_name).toBe('Syngenta S9012');
        });
    });

    describe('Filtering', () => {
        beforeEach(async () => {
            await display.loadVarieties(mockVarieties);
        });

        test('should filter by overall score range', () => {
            document.getElementById('min-score').value = '0.8';
            document.getElementById('max-score').value = '0.9';
            
            display.applyFilters();
            
            const filteredVarieties = display.filteredVarieties;
            expect(filteredVarieties).toHaveLength(1);
            expect(filteredVarieties[0].overall_score).toBe(0.87);
        });

        test('should filter by confidence range', () => {
            document.getElementById('min-confidence').value = '0.8';
            document.getElementById('max-confidence').value = '1.0';
            
            display.applyFilters();
            
            const filteredVarieties = display.filteredVarieties;
            expect(filteredVarieties).toHaveLength(2);
            expect(filteredVarieties.every(v => v.confidence >= 0.8)).toBe(true);
        });

        test('should filter by maturity days range', () => {
            document.getElementById('min-maturity').value = '110';
            document.getElementById('max-maturity').value = '120';
            
            display.applyFilters();
            
            const filteredVarieties = display.filteredVarieties;
            expect(filteredVarieties).toHaveLength(2);
            expect(filteredVarieties.every(v => v.maturity_days >= 110 && v.maturity_days <= 120)).toBe(true);
        });

        test('should filter by disease resistance level', () => {
            document.getElementById('disease-resistance').value = 'high';
            
            display.applyFilters();
            
            const filteredVarieties = display.filteredVarieties;
            expect(filteredVarieties).toHaveLength(2);
            expect(filteredVarieties.every(v => v.disease_resistance_level === 'high')).toBe(true);
        });

        test('should filter by company', () => {
            document.getElementById('company-filter').value = 'Pioneer';
            
            display.applyFilters();
            
            const filteredVarieties = display.filteredVarieties;
            expect(filteredVarieties).toHaveLength(1);
            expect(filteredVarieties[0].company).toBe('Pioneer');
        });

        test('should apply multiple filters simultaneously', () => {
            document.getElementById('min-score').value = '0.8';
            document.getElementById('max-score').value = '0.9';
            document.getElementById('min-confidence').value = '0.8';
            document.getElementById('max-confidence').value = '1.0';
            
            display.applyFilters();
            
            const filteredVarieties = display.filteredVarieties;
            expect(filteredVarieties).toHaveLength(1);
            expect(filteredVarieties[0].overall_score).toBe(0.87);
            expect(filteredVarieties[0].confidence).toBe(0.82);
        });
    });

    describe('View Rendering', () => {
        beforeEach(async () => {
            await display.loadVarieties(mockVarieties);
        });

        test('should render grid view by default', () => {
            display.renderVarieties();
            
            const container = document.getElementById('variety-display-container');
            expect(container.innerHTML).toContain('variety-grid-container');
            expect(container.innerHTML).toContain('variety-card');
        });

        test('should render table view', () => {
            display.currentView = 'table';
            display.renderVarieties();
            
            const container = document.getElementById('variety-display-container');
            expect(container.innerHTML).toContain('variety-table-container');
            expect(container.innerHTML).toContain('table');
        });

        test('should render comparison view when varieties are selected', () => {
            display.selectedVarieties.add('1');
            display.selectedVarieties.add('2');
            display.currentView = 'comparison';
            display.renderVarieties();
            
            const container = document.getElementById('variety-display-container');
            expect(container.innerHTML).toContain('comparison-container');
            expect(container.innerHTML).toContain('comparison-table');
        });

        test('should show placeholder when no varieties selected for comparison', () => {
            display.currentView = 'comparison';
            display.renderVarieties();
            
            const container = document.getElementById('variety-display-container');
            expect(container.innerHTML).toContain('comparison-placeholder');
        });
    });

    describe('Variety Card Creation', () => {
        beforeEach(async () => {
            await display.loadVarieties(mockVarieties);
        });

        test('should create variety card with all required elements', () => {
            const variety = mockVarieties[0];
            const cardHTML = display.createVarietyCard(variety);
            
            expect(cardHTML).toContain('variety-card');
            expect(cardHTML).toContain(variety.variety_name);
            expect(cardHTML).toContain(variety.company);
            expect(cardHTML).toContain('overall-score');
            expect(cardHTML).toContain('confidence-indicator');
            expect(cardHTML).toContain('variety-metrics');
        });

        test('should show expanded details when variety is expanded', () => {
            display.expandedVarieties.add('1');
            const variety = mockVarieties[0];
            const cardHTML = display.createVarietyCard(variety);
            
            expect(cardHTML).toContain('variety-details-expanded');
            expect(cardHTML).toContain('score-breakdown');
            expect(cardHTML).toContain('performance-chart');
        });

        test('should show bookmark button as active when variety is bookmarked', () => {
            display.bookmarkedVarieties.add('1');
            const variety = mockVarieties[0];
            const cardHTML = display.createVarietyCard(variety);
            
            expect(cardHTML).toContain('bookmark-btn active');
        });

        test('should show selected state when variety is selected', () => {
            display.selectedVarieties.add('1');
            const variety = mockVarieties[0];
            const cardHTML = display.createVarietyCard(variety);
            
            expect(cardHTML).toContain('variety-card advanced selected');
        });
    });

    describe('Score Breakdown', () => {
        test('should create score breakdown visualization', () => {
            const variety = mockVarieties[0];
            const breakdownHTML = display.createScoreBreakdown(variety);
            
            expect(breakdownHTML).toContain('score-breakdown');
            expect(breakdownHTML).toContain('score-bars');
            expect(breakdownHTML).toContain('yield_potential');
            expect(breakdownHTML).toContain('disease_resistance');
        });

        test('should format score labels correctly', () => {
            expect(display.formatScoreLabel('yield_potential')).toBe('Yield Potential');
            expect(display.formatScoreLabel('disease_resistance')).toBe('Disease Resistance');
            expect(display.formatScoreLabel('climate_adaptation')).toBe('Climate Adaptation');
        });
    });

    describe('Confidence Indicator', () => {
        test('should create high confidence indicator', () => {
            const variety = { ...mockVarieties[0], confidence: 0.9 };
            const indicatorHTML = display.createConfidenceIndicator(variety);
            
            expect(indicatorHTML).toContain('confidence-indicator high');
            expect(indicatorHTML).toContain('90.0%');
        });

        test('should create medium confidence indicator', () => {
            const variety = { ...mockVarieties[0], confidence: 0.7 };
            const indicatorHTML = display.createConfidenceIndicator(variety);
            
            expect(indicatorHTML).toContain('confidence-indicator medium');
            expect(indicatorHTML).toContain('70.0%');
        });

        test('should create low confidence indicator', () => {
            const variety = { ...mockVarieties[0], confidence: 0.5 };
            const indicatorHTML = display.createConfidenceIndicator(variety);
            
            expect(indicatorHTML).toContain('confidence-indicator low');
            expect(indicatorHTML).toContain('50.0%');
        });
    });

    describe('Bookmarking', () => {
        test('should toggle bookmark for variety', () => {
            display.toggleBookmark('1');
            expect(display.bookmarkedVarieties.has('1')).toBe(true);
            
            display.toggleBookmark('1');
            expect(display.bookmarkedVarieties.has('1')).toBe(false);
        });

        test('should save bookmarks to localStorage', () => {
            display.toggleBookmark('1');
            display.toggleBookmark('2');
            
            expect(localStorage.setItem).toHaveBeenCalledWith(
                'variety-bookmarks',
                JSON.stringify(['1', '2'])
            );
        });
    });

    describe('Expansion', () => {
        test('should toggle expanded state for variety', () => {
            display.toggleExpanded('1');
            expect(display.expandedVarieties.has('1')).toBe(true);
            
            display.toggleExpanded('1');
            expect(display.expandedVarieties.has('1')).toBe(false);
        });
    });

    describe('Quick Comparison', () => {
        test('should add variety to quick compare', () => {
            display.addToQuickCompare('1');
            expect(display.selectedVarieties.has('1')).toBe(true);
            
            display.addToQuickCompare('1');
            expect(display.selectedVarieties.has('1')).toBe(false);
        });

        test('should clear comparison selection', () => {
            display.selectedVarieties.add('1');
            display.selectedVarieties.add('2');
            
            display.clearComparison();
            expect(display.selectedVarieties.size).toBe(0);
        });
    });

    describe('Export Functionality', () => {
        beforeEach(async () => {
            await display.loadVarieties(mockVarieties);
        });

        test('should export varieties as JSON', () => {
            // Mock URL.createObjectURL and URL.revokeObjectURL
            global.URL = {
                createObjectURL: jest.fn().mockReturnValue('blob:mock-url'),
                revokeObjectURL: jest.fn()
            };
            
            // Mock document.createElement
            const mockAnchor = {
                href: '',
                download: '',
                click: jest.fn()
            };
            document.createElement = jest.fn().mockReturnValue(mockAnchor);
            
            display.exportVarieties('json');
            
            expect(global.URL.createObjectURL).toHaveBeenCalled();
            expect(mockAnchor.download).toContain('variety-recommendations');
            expect(mockAnchor.download).toContain('.json');
            expect(mockAnchor.click).toHaveBeenCalled();
        });

        test('should export varieties as CSV', () => {
            // Mock URL.createObjectURL and URL.revokeObjectURL
            global.URL = {
                createObjectURL: jest.fn().mockReturnValue('blob:mock-url'),
                revokeObjectURL: jest.fn()
            };
            
            // Mock document.createElement
            const mockAnchor = {
                href: '',
                download: '',
                click: jest.fn()
            };
            document.createElement = jest.fn().mockReturnValue(mockAnchor);
            
            display.exportVarieties('csv');
            
            expect(global.URL.createObjectURL).toHaveBeenCalled();
            expect(mockAnchor.download).toContain('variety-recommendations');
            expect(mockAnchor.download).toContain('.csv');
            expect(mockAnchor.click).toHaveBeenCalled();
        });

        test('should convert variety data to CSV format', () => {
            const csv = display.convertToCSV(mockVarieties);
            const lines = csv.split('\n');
            
            expect(lines[0]).toBe('Name,Company,Overall Score,Yield,Maturity,Disease Resistance,Confidence');
            expect(lines[1]).toContain('Pioneer P1234');
            expect(lines[1]).toContain('Pioneer');
            expect(lines[1]).toContain('92.0');
        });
    });

    describe('Performance Optimization', () => {
        test('should enable virtual scrolling for large datasets', () => {
            expect(display.virtualScrolling.enabled).toBe(true);
            expect(display.virtualScrolling.itemHeight).toBe(200);
            expect(display.virtualScrolling.visibleItems).toBe(10);
        });

        test('should calculate scroll index correctly', () => {
            const scrollContainer = document.createElement('div');
            scrollContainer.className = 'variety-grid-container';
            scrollContainer.scrollTop = 1000;
            document.body.appendChild(scrollContainer);
            
            const scrollIndex = display.getScrollIndex();
            expect(scrollIndex).toBe(5); // 1000 / 200 = 5
        });
    });

    describe('Statistics Updates', () => {
        beforeEach(async () => {
            await display.loadVarieties(mockVarieties);
        });

        test('should update filter statistics', () => {
            display.updateFilterStats();
            
            const statsElement = document.getElementById('filter-stats');
            expect(statsElement.innerHTML).toContain('3');
            expect(statsElement.innerHTML).toContain('varieties');
        });

        test('should update selection statistics', () => {
            display.selectedVarieties.add('1');
            display.selectedVarieties.add('2');
            display.updateSelectionStats();
            
            const statsElement = document.getElementById('selection-stats');
            expect(statsElement.innerHTML).toContain('2');
            expect(statsElement.innerHTML).toContain('selected');
        });
    });

    describe('Error Handling', () => {
        test('should handle empty variety data gracefully', async () => {
            await display.loadVarieties([]);
            
            expect(display.varieties).toEqual([]);
            expect(display.filteredVarieties).toEqual([]);
        });

        test('should handle missing variety properties', () => {
            const incompleteVariety = {
                id: '1',
                variety_name: 'Test Variety'
                // Missing other properties
            };
            
            const cardHTML = display.createVarietyCard(incompleteVariety);
            expect(cardHTML).toContain('Test Variety');
            expect(cardHTML).toContain('N/A');
        });
    });
});

// Integration tests
describe('AdvancedVarietyDisplay Integration', () => {
    let display;

    beforeEach(() => {
        display = new AdvancedVarietyDisplay();
    });

    test('should handle complete workflow from loading to export', async () => {
        const mockVarieties = [
            {
                id: '1',
                variety_name: 'Test Variety',
                name: 'Test Variety',
                company: 'Test Company',
                overall_score: 0.85,
                confidence: 0.80,
                yield_expectation: { score: 'High' },
                maturity_days: 120,
                disease_resistance_level: 'high',
                individual_scores: {
                    yield_potential: 0.90,
                    disease_resistance: 0.85,
                    climate_adaptation: 0.80
                },
                traits: [{ name: 'High Yield', category: 'yield' }],
                description: 'Test variety description'
            }
        ];

        // Load varieties
        await display.loadVarieties(mockVarieties);
        expect(display.varieties).toHaveLength(1);

        // Apply filters
        document.getElementById('min-score').value = '0.8';
        display.applyFilters();
        expect(display.filteredVarieties).toHaveLength(1);

        // Sort varieties
        display.sortCriteria = 'confidence';
        display.sortVarieties();
        expect(display.filteredVarieties[0].confidence).toBe(0.80);

        // Bookmark variety
        display.toggleBookmark('1');
        expect(display.bookmarkedVarieties.has('1')).toBe(true);

        // Select for comparison
        display.addToQuickCompare('1');
        expect(display.selectedVarieties.has('1')).toBe(true);

        // Expand details
        display.toggleExpanded('1');
        expect(display.expandedVarieties.has('1')).toBe(true);

        // Render in different views
        display.currentView = 'table';
        display.renderVarieties();
        expect(document.getElementById('variety-display-container').innerHTML).toContain('table');

        display.currentView = 'comparison';
        display.renderVarieties();
        expect(document.getElementById('variety-display-container').innerHTML).toContain('comparison-container');
    });
});