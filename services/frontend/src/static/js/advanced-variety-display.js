/**
 * Advanced Variety Display and Visualization System
 * 
 * Implements advanced ranked variety display with interactive features,
 * performance visualizations, and comprehensive comparison tools.
 */

class AdvancedVarietyDisplay {
    constructor() {
        this.varieties = [];
        this.filteredVarieties = [];
        this.selectedVarieties = new Set();
        this.sortCriteria = 'overall_score';
        this.sortDirection = 'desc';
        this.currentView = 'grid'; // 'grid', 'table', 'comparison'
        this.bookmarkedVarieties = new Set();
        this.expandedVarieties = new Set();
        
        // Performance optimization
        this.virtualScrolling = {
            enabled: true,
            itemHeight: 200,
            visibleItems: 10,
            buffer: 5
        };
        
        this.initializeEventListeners();
        this.loadBookmarks();
    }

    /**
     * Initialize event listeners for interactive features
     */
    initializeEventListeners() {
        // Sort controls
        document.addEventListener('change', (e) => {
            if (e.target.id === 'sort-criteria') {
                this.sortCriteria = e.target.value;
                this.renderVarieties();
            }
            if (e.target.id === 'sort-direction') {
                this.sortDirection = e.target.value;
                this.renderVarieties();
            }
        });

        // View toggle
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('view-toggle')) {
                this.currentView = e.target.dataset.view;
                this.renderVarieties();
            }
        });

        // Filter controls
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('variety-filter')) {
                this.applyFilters();
            }
        });

        // Bookmark toggle
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('bookmark-btn')) {
                const varietyId = e.target.dataset.varietyId;
                this.toggleBookmark(varietyId);
            }
        });

        // Expand/collapse details
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('expand-btn')) {
                const varietyId = e.target.dataset.varietyId;
                this.toggleExpanded(varietyId);
            }
        });

        // Quick comparison
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-compare-btn')) {
                const varietyId = e.target.dataset.varietyId;
                this.addToQuickCompare(varietyId);
            }
        });
    }

    /**
     * Load variety data and render the display
     */
    async loadVarieties(varietyData) {
        this.varieties = varietyData;
        this.filteredVarieties = [...varietyData];
        
        // Sort varieties by overall score initially
        this.sortVarieties();
        
        // Render the display
        this.renderVarieties();
        
        // Initialize visualizations
        this.initializeVisualizations();
    }

    /**
     * Sort varieties based on current criteria
     */
    sortVarieties() {
        this.filteredVarieties.sort((a, b) => {
            let aValue = this.getSortValue(a, this.sortCriteria);
            let bValue = this.getSortValue(b, this.sortCriteria);
            
            if (typeof aValue === 'string') {
                aValue = aValue.toLowerCase();
                bValue = bValue.toLowerCase();
            }
            
            if (this.sortDirection === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });
    }

    /**
     * Get sort value for a variety based on criteria
     */
    getSortValue(variety, criteria) {
        switch (criteria) {
            case 'overall_score':
                return variety.overall_score || 0;
            case 'yield_potential':
                return variety.yield_expectation?.score || 0;
            case 'disease_resistance':
                return variety.disease_resistance_score || 0;
            case 'maturity_days':
                return variety.maturity_days || 0;
            case 'confidence':
                return variety.confidence || 0;
            case 'name':
                return variety.variety_name || variety.name || '';
            default:
                return variety.overall_score || 0;
        }
    }

    /**
     * Apply filters to varieties
     */
    applyFilters() {
        const filters = this.getActiveFilters();
        
        this.filteredVarieties = this.varieties.filter(variety => {
            return this.matchesFilters(variety, filters);
        });
        
        this.sortVarieties();
        this.renderVarieties();
        this.updateFilterStats();
    }

    /**
     * Get active filter values
     */
    getActiveFilters() {
        return {
            minScore: parseFloat(document.getElementById('min-score')?.value || 0),
            maxScore: parseFloat(document.getElementById('max-score')?.value || 1),
            minConfidence: parseFloat(document.getElementById('min-confidence')?.value || 0),
            maxConfidence: parseFloat(document.getElementById('max-confidence')?.value || 1),
            maturityRange: {
                min: parseInt(document.getElementById('min-maturity')?.value || 0),
                max: parseInt(document.getElementById('max-maturity')?.value || 365)
            },
            diseaseResistance: document.getElementById('disease-resistance')?.value || 'all',
            company: document.getElementById('company-filter')?.value || 'all'
        };
    }

    /**
     * Check if variety matches filters
     */
    matchesFilters(variety, filters) {
        const score = variety.overall_score || 0;
        const confidence = variety.confidence || 0;
        const maturity = variety.maturity_days || 0;
        
        return score >= filters.minScore &&
               score <= filters.maxScore &&
               confidence >= filters.minConfidence &&
               confidence <= filters.maxConfidence &&
               maturity >= filters.maturityRange.min &&
               maturity <= filters.maturityRange.max &&
               (filters.diseaseResistance === 'all' || 
                variety.disease_resistance_level === filters.diseaseResistance) &&
               (filters.company === 'all' || 
                variety.company === filters.company);
    }

    /**
     * Render varieties based on current view
     */
    renderVarieties() {
        const container = document.getElementById('variety-display-container');
        if (!container) return;

        switch (this.currentView) {
            case 'grid':
                this.renderGridView(container);
                break;
            case 'table':
                this.renderTableView(container);
                break;
            case 'comparison':
                this.renderComparisonView(container);
                break;
        }

        this.updateViewControls();
        this.updateSelectionStats();
    }

    /**
     * Render grid view with variety cards
     */
    renderGridView(container) {
        const startIndex = this.virtualScrolling.enabled ? 
            Math.max(0, this.getScrollIndex() - this.virtualScrolling.buffer) : 0;
        const endIndex = this.virtualScrolling.enabled ?
            Math.min(this.filteredVarieties.length, 
                    startIndex + this.virtualScrolling.visibleItems + this.virtualScrolling.buffer * 2) :
            this.filteredVarieties.length;

        const visibleVarieties = this.filteredVarieties.slice(startIndex, endIndex);

        container.innerHTML = `
            <div class="variety-grid-container">
                ${visibleVarieties.map(variety => this.createVarietyCard(variety)).join('')}
            </div>
            ${this.createPaginationControls()}
        `;

        if (this.virtualScrolling.enabled) {
            this.setupVirtualScrolling(container);
        }
    }

    /**
     * Create variety card with advanced features
     */
    createVarietyCard(variety) {
        const isExpanded = this.expandedVarieties.has(variety.id);
        const isBookmarked = this.bookmarkedVarieties.has(variety.id);
        const isSelected = this.selectedVarieties.has(variety.id);
        
        const scoreBreakdown = this.createScoreBreakdown(variety);
        const confidenceIndicator = this.createConfidenceIndicator(variety);
        const performanceChart = this.createPerformanceChart(variety);
        
        return `
            <div class="variety-card advanced ${isSelected ? 'selected' : ''}" 
                 data-variety-id="${variety.id}">
                <div class="variety-card-header">
                    <div class="variety-title">
                        <h5>${variety.variety_name || variety.name}</h5>
                        <span class="variety-company">${variety.company || 'Unknown'}</span>
                    </div>
                    <div class="variety-actions">
                        <button class="btn btn-sm btn-outline-primary bookmark-btn ${isBookmarked ? 'active' : ''}" 
                                data-variety-id="${variety.id}" title="Bookmark">
                            <i class="fas fa-bookmark"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success quick-compare-btn" 
                                data-variety-id="${variety.id}" title="Quick Compare">
                            <i class="fas fa-balance-scale"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-info expand-btn" 
                                data-variety-id="${variety.id}" title="Expand Details">
                            <i class="fas fa-${isExpanded ? 'compress' : 'expand'}"></i>
                        </button>
                    </div>
                </div>
                
                <div class="variety-score-section">
                    <div class="overall-score">
                        <span class="score-label">Overall Score</span>
                        <span class="score-value">${(variety.overall_score * 100).toFixed(1)}%</span>
                    </div>
                    ${confidenceIndicator}
                </div>
                
                <div class="variety-metrics">
                    <div class="metric">
                        <span class="metric-label">Yield</span>
                        <span class="metric-value">${variety.yield_expectation?.score || 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Maturity</span>
                        <span class="metric-value">${variety.maturity_days || 'N/A'} days</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Disease Res.</span>
                        <span class="metric-value">${variety.disease_resistance_level || 'N/A'}</span>
                    </div>
                </div>
                
                ${isExpanded ? `
                    <div class="variety-details-expanded">
                        ${scoreBreakdown}
                        ${performanceChart}
                        <div class="variety-description">
                            <p>${variety.description || 'No description available'}</p>
                        </div>
                        <div class="variety-traits">
                            <h6>Key Traits:</h6>
                            <div class="trait-tags">
                                ${(variety.traits || []).map(trait => 
                                    `<span class="trait-tag ${trait.category}">${trait.name}</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <div class="variety-card-footer">
                    <button class="btn btn-primary btn-sm select-variety-btn" 
                            data-variety-id="${variety.id}">
                        ${isSelected ? 'Selected' : 'Select'}
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Create score breakdown visualization
     */
    createScoreBreakdown(variety) {
        const scores = variety.individual_scores || {};
        const maxScore = Math.max(...Object.values(scores), 1);
        
        return `
            <div class="score-breakdown">
                <h6>Score Breakdown</h6>
                <div class="score-bars">
                    ${Object.entries(scores).map(([key, value]) => `
                        <div class="score-bar">
                            <span class="score-label">${this.formatScoreLabel(key)}</span>
                            <div class="score-bar-container">
                                <div class="score-bar-fill" style="width: ${(value / maxScore) * 100}%"></div>
                                <span class="score-value">${(value * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Create confidence indicator
     */
    createConfidenceIndicator(variety) {
        const confidence = variety.confidence || 0;
        const confidenceClass = confidence >= 0.8 ? 'high' : 
                               confidence >= 0.6 ? 'medium' : 'low';
        
        return `
            <div class="confidence-indicator ${confidenceClass}">
                <span class="confidence-label">Confidence</span>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${confidence * 100}%"></div>
                </div>
                <span class="confidence-value">${(confidence * 100).toFixed(1)}%</span>
            </div>
        `;
    }

    /**
     * Create performance chart (mini radar chart)
     */
    createPerformanceChart(variety) {
        const scores = variety.individual_scores || {};
        const chartId = `chart-${variety.id}`;
        
        return `
            <div class="performance-chart">
                <h6>Performance Profile</h6>
                <canvas id="${chartId}" width="150" height="150"></canvas>
            </div>
            <script>
                setTimeout(() => {
                    this.createRadarChart('${chartId}', ${JSON.stringify(scores)});
                }, 100);
            </script>
        `;
    }

    /**
     * Create radar chart for variety performance
     */
    createRadarChart(canvasId, scores) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid circles
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;
        for (let i = 1; i <= 5; i++) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI);
            ctx.stroke();
        }
        
        // Draw axes
        const labels = Object.keys(scores);
        labels.forEach((label, index) => {
            const angle = (2 * Math.PI * index) / labels.length - Math.PI / 2;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.stroke();
            
            // Draw label
            ctx.fillStyle = '#666';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(this.formatScoreLabel(label), x, y + 15);
        });
        
        // Draw data polygon
        ctx.strokeStyle = '#007bff';
        ctx.fillStyle = 'rgba(0, 123, 255, 0.2)';
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        labels.forEach((label, index) => {
            const angle = (2 * Math.PI * index) / labels.length - Math.PI / 2;
            const value = scores[label] || 0;
            const x = centerX + Math.cos(angle) * radius * value;
            const y = centerY + Math.sin(angle) * radius * value;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }

    /**
     * Render table view
     */
    renderTableView(container) {
        container.innerHTML = `
            <div class="variety-table-container">
                <table class="table table-hover variety-table">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="select-all-varieties"></th>
                            <th>Variety</th>
                            <th>Company</th>
                            <th>Overall Score</th>
                            <th>Yield</th>
                            <th>Maturity</th>
                            <th>Disease Res.</th>
                            <th>Confidence</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.filteredVarieties.map(variety => this.createTableRow(variety)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    /**
     * Create table row for variety
     */
    createTableRow(variety) {
        const isSelected = this.selectedVarieties.has(variety.id);
        const isBookmarked = this.bookmarkedVarieties.has(variety.id);
        
        return `
            <tr class="variety-row ${isSelected ? 'selected' : ''}" data-variety-id="${variety.id}">
                <td>
                    <input type="checkbox" class="variety-checkbox" 
                           data-variety-id="${variety.id}" ${isSelected ? 'checked' : ''}>
                </td>
                <td>
                    <div class="variety-name">
                        <strong>${variety.variety_name || variety.name}</strong>
                        <small class="text-muted d-block">${variety.description?.substring(0, 50)}...</small>
                    </div>
                </td>
                <td>${variety.company || 'Unknown'}</td>
                <td>
                    <div class="score-display">
                        <span class="score-value">${(variety.overall_score * 100).toFixed(1)}%</span>
                        <div class="score-bar-mini">
                            <div class="score-bar-fill" style="width: ${variety.overall_score * 100}%"></div>
                        </div>
                    </div>
                </td>
                <td>${variety.yield_expectation?.score || 'N/A'}</td>
                <td>${variety.maturity_days || 'N/A'} days</td>
                <td>
                    <span class="badge badge-${variety.disease_resistance_level || 'secondary'}">
                        ${variety.disease_resistance_level || 'N/A'}
                    </span>
                </td>
                <td>
                    <div class="confidence-display">
                        <span class="confidence-value">${(variety.confidence * 100).toFixed(1)}%</span>
                        <div class="confidence-bar-mini">
                            <div class="confidence-fill" style="width: ${variety.confidence * 100}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-outline-primary bookmark-btn ${isBookmarked ? 'active' : ''}" 
                                data-variety-id="${variety.id}" title="Bookmark">
                            <i class="fas fa-bookmark"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success quick-compare-btn" 
                                data-variety-id="${variety.id}" title="Quick Compare">
                            <i class="fas fa-balance-scale"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * Render comparison view
     */
    renderComparisonView(container) {
        const selectedVarieties = Array.from(this.selectedVarieties);
        
        if (selectedVarieties.length < 2) {
            container.innerHTML = `
                <div class="comparison-placeholder">
                    <h5>Select at least 2 varieties to compare</h5>
                    <p>Use the checkboxes or quick compare buttons to select varieties for comparison.</p>
                </div>
            `;
            return;
        }
        
        const varietiesToCompare = this.varieties.filter(v => selectedVarieties.includes(v.id));
        
        container.innerHTML = `
            <div class="comparison-container">
                <div class="comparison-header">
                    <h5>Variety Comparison</h5>
                    <button class="btn btn-outline-secondary" onclick="this.clearComparison()">
                        Clear Comparison
                    </button>
                </div>
                <div class="comparison-table-container">
                    ${this.createComparisonTable(varietiesToCompare)}
                </div>
                <div class="comparison-charts">
                    ${this.createComparisonCharts(varietiesToCompare)}
                </div>
            </div>
        `;
    }

    /**
     * Create comparison table
     */
    createComparisonTable(varieties) {
        const criteria = ['overall_score', 'yield_potential', 'disease_resistance', 'maturity_days', 'confidence'];
        
        return `
            <table class="table table-bordered comparison-table">
                <thead>
                    <tr>
                        <th>Criteria</th>
                        ${varieties.map(v => `<th>${v.variety_name || v.name}</th>`).join('')}
                    </tr>
                </thead>
                <tbody>
                    ${criteria.map(criterion => `
                        <tr>
                            <td><strong>${this.formatScoreLabel(criterion)}</strong></td>
                            ${varieties.map(variety => `
                                <td>
                                    ${this.formatComparisonValue(variety, criterion)}
                                </td>
                            `).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    /**
     * Create comparison charts
     */
    createComparisonCharts(varieties) {
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container">
                        <h6>Score Comparison</h6>
                        <canvas id="comparison-bar-chart" width="400" height="300"></canvas>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <h6>Performance Radar</h6>
                        <canvas id="comparison-radar-chart" width="400" height="300"></canvas>
                    </div>
                </div>
            </div>
            <script>
                setTimeout(() => {
                    this.createComparisonBarChart(${JSON.stringify(varieties)});
                    this.createComparisonRadarChart(${JSON.stringify(varieties)});
                }, 100);
            </script>
        `;
    }

    /**
     * Create comparison bar chart
     */
    createComparisonBarChart(varieties) {
        const canvas = document.getElementById('comparison-bar-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const labels = varieties.map(v => v.variety_name || v.name);
        const scores = varieties.map(v => v.overall_score * 100);
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width - 100) / varieties.length;
        const maxScore = Math.max(...scores);
        
        varieties.forEach((variety, index) => {
            const barHeight = (variety.overall_score * 100 / maxScore) * (canvas.height - 100);
            const x = 50 + index * barWidth;
            const y = canvas.height - 50 - barHeight;
            
            // Draw bar
            ctx.fillStyle = '#007bff';
            ctx.fillRect(x, y, barWidth - 10, barHeight);
            
            // Draw score text
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`${(variety.overall_score * 100).toFixed(1)}%`, 
                        x + barWidth/2, y - 5);
            
            // Draw variety name
            ctx.fillText(variety.variety_name || variety.name, 
                        x + barWidth/2, canvas.height - 30);
        });
    }

    /**
     * Create comparison radar chart
     */
    createComparisonRadarChart(varieties) {
        const canvas = document.getElementById('comparison-radar-chart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 40;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw grid
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;
        for (let i = 1; i <= 5; i++) {
            ctx.beginPath();
            ctx.arc(centerX, centerY, (radius * i) / 5, 0, 2 * Math.PI);
            ctx.stroke();
        }
        
        // Draw axes
        const criteria = ['yield_potential', 'disease_resistance', 'climate_adaptation', 'market_desirability'];
        criteria.forEach((criterion, index) => {
            const angle = (2 * Math.PI * index) / criteria.length - Math.PI / 2;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.stroke();
            
            // Draw label
            ctx.fillStyle = '#666';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(this.formatScoreLabel(criterion), x, y + 15);
        });
        
        // Draw variety polygons
        const colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6f42c1'];
        
        varieties.forEach((variety, varietyIndex) => {
            const color = colors[varietyIndex % colors.length];
            ctx.strokeStyle = color;
            ctx.fillStyle = color + '20';
            ctx.lineWidth = 2;
            
            ctx.beginPath();
            criteria.forEach((criterion, index) => {
                const angle = (2 * Math.PI * index) / criteria.length - Math.PI / 2;
                const value = variety.individual_scores?.[criterion] || 0;
                const x = centerX + Math.cos(angle) * radius * value;
                const y = centerY + Math.sin(angle) * radius * value;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        });
    }

    /**
     * Format score label for display
     */
    formatScoreLabel(label) {
        return label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Format comparison value
     */
    formatComparisonValue(variety, criterion) {
        switch (criterion) {
            case 'overall_score':
                return `${(variety.overall_score * 100).toFixed(1)}%`;
            case 'yield_potential':
                return variety.yield_expectation?.score || 'N/A';
            case 'disease_resistance':
                return variety.disease_resistance_level || 'N/A';
            case 'maturity_days':
                return `${variety.maturity_days || 'N/A'} days`;
            case 'confidence':
                return `${(variety.confidence * 100).toFixed(1)}%`;
            default:
                return variety[criterion] || 'N/A';
        }
    }

    /**
     * Toggle bookmark for variety
     */
    toggleBookmark(varietyId) {
        if (this.bookmarkedVarieties.has(varietyId)) {
            this.bookmarkedVarieties.delete(varietyId);
        } else {
            this.bookmarkedVarieties.add(varietyId);
        }
        
        this.saveBookmarks();
        this.renderVarieties();
    }

    /**
     * Toggle expanded details for variety
     */
    toggleExpanded(varietyId) {
        if (this.expandedVarieties.has(varietyId)) {
            this.expandedVarieties.delete(varietyId);
        } else {
            this.expandedVarieties.add(varietyId);
        }
        
        this.renderVarieties();
    }

    /**
     * Add variety to quick compare
     */
    addToQuickCompare(varietyId) {
        if (this.selectedVarieties.has(varietyId)) {
            this.selectedVarieties.delete(varietyId);
        } else {
            this.selectedVarieties.add(varietyId);
        }
        
        this.renderVarieties();
    }

    /**
     * Clear comparison selection
     */
    clearComparison() {
        this.selectedVarieties.clear();
        this.renderVarieties();
    }

    /**
     * Save bookmarks to localStorage
     */
    saveBookmarks() {
        localStorage.setItem('variety-bookmarks', JSON.stringify(Array.from(this.bookmarkedVarieties)));
    }

    /**
     * Load bookmarks from localStorage
     */
    loadBookmarks() {
        const saved = localStorage.getItem('variety-bookmarks');
        if (saved) {
            this.bookmarkedVarieties = new Set(JSON.parse(saved));
        }
    }

    /**
     * Update filter statistics
     */
    updateFilterStats() {
        const totalVarieties = this.varieties.length;
        const filteredVarieties = this.filteredVarieties.length;
        const reductionPercentage = totalVarieties > 0 ? 
            ((totalVarieties - filteredVarieties) / totalVarieties * 100).toFixed(1) : 0;
        
        const statsElement = document.getElementById('filter-stats');
        if (statsElement) {
            statsElement.innerHTML = `
                <div class="filter-stats">
                    <span class="stat-item">
                        <strong>${filteredVarieties}</strong> of <strong>${totalVarieties}</strong> varieties
                    </span>
                    <span class="stat-item">
                        <strong>${reductionPercentage}%</strong> filtered out
                    </span>
                </div>
            `;
        }
    }

    /**
     * Update view controls
     */
    updateViewControls() {
        const viewControls = document.querySelector('.view-controls');
        if (viewControls) {
            viewControls.innerHTML = `
                <div class="btn-group" role="group">
                    <button class="btn btn-outline-primary view-toggle ${this.currentView === 'grid' ? 'active' : ''}" 
                            data-view="grid">
                        <i class="fas fa-th"></i> Grid
                    </button>
                    <button class="btn btn-outline-primary view-toggle ${this.currentView === 'table' ? 'active' : ''}" 
                            data-view="table">
                        <i class="fas fa-table"></i> Table
                    </button>
                    <button class="btn btn-outline-primary view-toggle ${this.currentView === 'comparison' ? 'active' : ''}" 
                            data-view="comparison">
                        <i class="fas fa-balance-scale"></i> Compare
                    </button>
                </div>
            `;
        }
    }

    /**
     * Update selection statistics
     */
    updateSelectionStats() {
        const selectedCount = this.selectedVarieties.size;
        const statsElement = document.getElementById('selection-stats');
        if (statsElement) {
            statsElement.innerHTML = `
                <div class="selection-stats">
                    <span class="stat-item">
                        <strong>${selectedCount}</strong> varieties selected
                    </span>
                    ${selectedCount >= 2 ? `
                        <button class="btn btn-sm btn-primary" onclick="this.showComparison()">
                            Compare Selected
                        </button>
                    ` : ''}
                </div>
            `;
        }
    }

    /**
     * Show comparison view
     */
    showComparison() {
        this.currentView = 'comparison';
        this.renderVarieties();
    }

    /**
     * Create pagination controls
     */
    createPaginationControls() {
        if (!this.virtualScrolling.enabled) return '';
        
        const totalPages = Math.ceil(this.filteredVarieties.length / this.virtualScrolling.visibleItems);
        const currentPage = Math.floor(this.getScrollIndex() / this.virtualScrolling.visibleItems) + 1;
        
        return `
            <div class="pagination-controls">
                <button class="btn btn-outline-primary" onclick="this.previousPage()" 
                        ${currentPage <= 1 ? 'disabled' : ''}>
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
                <span class="page-info">
                    Page ${currentPage} of ${totalPages}
                </span>
                <button class="btn btn-outline-primary" onclick="this.nextPage()" 
                        ${currentPage >= totalPages ? 'disabled' : ''}>
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        `;
    }

    /**
     * Setup virtual scrolling
     */
    setupVirtualScrolling(container) {
        const scrollContainer = container.querySelector('.variety-grid-container');
        if (!scrollContainer) return;
        
        scrollContainer.addEventListener('scroll', () => {
            this.renderVarieties();
        });
    }

    /**
     * Get current scroll index
     */
    getScrollIndex() {
        const scrollContainer = document.querySelector('.variety-grid-container');
        if (!scrollContainer) return 0;
        
        const scrollTop = scrollContainer.scrollTop;
        return Math.floor(scrollTop / this.virtualScrolling.itemHeight);
    }

    /**
     * Initialize visualizations
     */
    initializeVisualizations() {
        // Initialize any global charts or visualizations
        this.updateFilterStats();
        this.updateSelectionStats();
    }

    /**
     * Export variety data
     */
    exportVarieties(format = 'json') {
        const data = {
            varieties: this.filteredVarieties,
            filters: this.getActiveFilters(),
            sortCriteria: this.sortCriteria,
            sortDirection: this.sortDirection,
            timestamp: new Date().toISOString()
        };
        
        if (format === 'json') {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `variety-recommendations-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        } else if (format === 'csv') {
            const csv = this.convertToCSV(data.varieties);
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `variety-recommendations-${Date.now()}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        }
    }

    /**
     * Convert variety data to CSV
     */
    convertToCSV(varieties) {
        const headers = ['Name', 'Company', 'Overall Score', 'Yield', 'Maturity', 'Disease Resistance', 'Confidence'];
        const rows = varieties.map(variety => [
            variety.variety_name || variety.name,
            variety.company || 'Unknown',
            (variety.overall_score * 100).toFixed(1),
            variety.yield_expectation?.score || 'N/A',
            variety.maturity_days || 'N/A',
            variety.disease_resistance_level || 'N/A',
            (variety.confidence * 100).toFixed(1)
        ]);
        
        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }
}

// Initialize the advanced variety display when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.advancedVarietyDisplay = new AdvancedVarietyDisplay();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedVarietyDisplay;
}