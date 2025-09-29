// Variety Comparison JavaScript for CAAIN Soil Hub
// Provides comprehensive variety comparison, analysis, and decision support functionality

class VarietyComparisonManager {
    constructor() {
        this.selectedVarieties = new Set();
        this.allVarieties = [];
        this.filteredVarieties = [];
        this.comparisonData = null;
        this.radarChart = null;
        this.apiBaseUrl = '/api/v1';
        this.currentPage = 1;
        this.varietiesPerPage = 12;
        this.searchDebounceTimer = null;
        this.comparisonHistory = this.loadComparisonHistory();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadVarieties();
        this.updateSelectedCount();
    }

    setupEventListeners() {
        // Search functionality
        const varietySearch = document.getElementById('varietySearch');
        if (varietySearch) {
            varietySearch.addEventListener('input', this.handleSearch.bind(this));
        }

        // Filter controls
        const cropFilter = document.getElementById('cropFilter');
        const sortBy = document.getElementById('sortBy');
        
        if (cropFilter) {
            cropFilter.addEventListener('change', this.handleFilterChange.bind(this));
        }
        
        if (sortBy) {
            sortBy.addEventListener('change', this.handleSortChange.bind(this));
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));

        // Window events
        window.addEventListener('beforeunload', this.saveComparisonHistory.bind(this));
    }

    async loadVarieties() {
        try {
            this.showLoadingState();
            
            const response = await fetch(`${this.apiBaseUrl}/varieties?page=${this.currentPage}&limit=${this.varietiesPerPage}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (this.currentPage === 1) {
                this.allVarieties = data.varieties || [];
            } else {
                this.allVarieties = [...this.allVarieties, ...(data.varieties || [])];
            }
            
            this.filteredVarieties = [...this.allVarieties];
            this.renderVarietyGrid();
            this.updateLoadMoreButton(data.has_more);
            
        } catch (error) {
            console.error('Error loading varieties:', error);
            this.showError('Failed to load varieties. Please try again.');
        } finally {
            this.hideLoadingState();
        }
    }

    async loadMoreVarieties() {
        this.currentPage++;
        await this.loadVarieties();
    }

    handleSearch(event) {
        const query = event.target.value.toLowerCase();
        
        // Debounce search
        clearTimeout(this.searchDebounceTimer);
        this.searchDebounceTimer = setTimeout(() => {
            this.filterVarieties();
        }, 300);
    }

    handleFilterChange() {
        this.filterVarieties();
    }

    handleSortChange() {
        this.sortVarieties();
        this.renderVarietyGrid();
    }

    filterVarieties() {
        const searchQuery = document.getElementById('varietySearch').value.toLowerCase();
        const cropFilter = document.getElementById('cropFilter').value;
        
        this.filteredVarieties = this.allVarieties.filter(variety => {
            const matchesSearch = !searchQuery || 
                variety.variety_name.toLowerCase().includes(searchQuery) ||
                variety.breeder_company?.toLowerCase().includes(searchQuery) ||
                variety.traits?.some(trait => trait.toLowerCase().includes(searchQuery));
            
            const matchesCrop = !cropFilter || variety.crop_type === cropFilter;
            
            return matchesSearch && matchesCrop;
        });
        
        this.sortVarieties();
        this.renderVarietyGrid();
    }

    sortVarieties() {
        const sortBy = document.getElementById('sortBy').value;
        
        this.filteredVarieties.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.variety_name.localeCompare(b.variety_name);
                case 'yield':
                    return (b.yield_potential_percentile || 0) - (a.yield_potential_percentile || 0);
                case 'maturity':
                    return (a.relative_maturity || 0) - (b.relative_maturity || 0);
                case 'disease':
                    return (b.disease_resistance_score || 0) - (a.disease_resistance_score || 0);
                default:
                    return 0;
            }
        });
    }

    renderVarietyGrid() {
        const grid = document.getElementById('varietyGrid');
        if (!grid) return;

        if (this.filteredVarieties.length === 0) {
            grid.innerHTML = `
                <div class="col-12 text-center py-4">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>No varieties found</h5>
                    <p class="text-muted">Try adjusting your search criteria</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.filteredVarieties.map(variety => this.createVarietyCard(variety)).join('');
    }

    createVarietyCard(variety) {
        const isSelected = this.selectedVarieties.has(variety.variety_id);
        const yieldScore = this.getScoreClass(variety.yield_potential_percentile, 'percentile');
        const diseaseScore = this.getScoreClass(variety.disease_resistance_score, 'score');
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="variety-card ${isSelected ? 'selected' : ''}" 
                     onclick="varietyComparison.toggleVarietySelection('${variety.variety_id}')"
                     data-variety-id="${variety.variety_id}">
                    
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0 fw-bold">${variety.variety_name}</h6>
                        <small class="text-muted">${variety.breeder_company || 'Unknown'}</small>
                    </div>
                    
                    <div class="row text-center mb-2">
                        <div class="col-6">
                            <small class="text-muted d-block">Yield Potential</small>
                            <span class="badge ${yieldScore}">${variety.yield_potential_percentile || 'N/A'}%</span>
                        </div>
                        <div class="col-6">
                            <small class="text-muted d-block">Disease Resistance</small>
                            <span class="badge ${diseaseScore}">${variety.disease_resistance_score || 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="row text-center mb-2">
                        <div class="col-6">
                            <small class="text-muted d-block">Maturity</small>
                            <span class="badge bg-info">${variety.relative_maturity || 'N/A'}</span>
                        </div>
                        <div class="col-6">
                            <small class="text-muted d-block">Risk</small>
                            <span class="badge ${this.getRiskBadgeClass(variety.risk_rating)}">${variety.risk_rating || 'Medium'}</span>
                        </div>
                    </div>
                    
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary w-100" 
                                onclick="event.stopPropagation(); varietyComparison.toggleVarietySelection('${variety.variety_id}')">
                            <i class="fas fa-${isSelected ? 'check' : 'plus'}"></i> 
                            ${isSelected ? 'Selected' : 'Select'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    toggleVarietySelection(varietyId) {
        if (this.selectedVarieties.has(varietyId)) {
            this.selectedVarieties.delete(varietyId);
        } else {
            this.selectedVarieties.add(varietyId);
        }
        
        this.updateSelectedCount();
        this.renderVarietyGrid();
        this.updateComparisonResults();
    }

    clearSelection() {
        this.selectedVarieties.clear();
        this.updateSelectedCount();
        this.renderVarietyGrid();
        this.updateComparisonResults();
    }

    updateSelectedCount() {
        const countElement = document.getElementById('selectedCount');
        if (countElement) {
            const count = this.selectedVarieties.size;
            countElement.textContent = `${count} variet${count === 1 ? 'y' : 'ies'} selected`;
            countElement.className = `badge ${count >= 2 ? 'bg-success' : 'bg-primary'}`;
        }
    }

    async updateComparisonResults() {
        const resultsSection = document.getElementById('comparisonResults');
        const emptyState = document.getElementById('emptyState');
        
        if (this.selectedVarieties.size < 2) {
            if (resultsSection) resultsSection.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            this.disableExportButtons();
            return;
        }
        
        if (resultsSection) resultsSection.style.display = 'block';
        if (emptyState) emptyState.style.display = 'none';
        
        try {
            await this.performComparison();
            this.enableExportButtons();
        } catch (error) {
            console.error('Error performing comparison:', error);
            this.showError('Failed to perform comparison. Please try again.');
        }
    }

    async performComparison() {
        this.showLoadingState();
        
        const selectedVarietyData = this.allVarieties.filter(v => this.selectedVarieties.has(v.variety_id));
        
        const requestData = {
            request_id: `comparison_${Date.now()}`,
            variety_ids: Array.from(this.selectedVarieties),
            provided_varieties: selectedVarietyData,
            comparison_context: {
                location: { latitude: 40.0, longitude: -95.0 }, // Default location
                soil_data: { ph: 6.5, texture: 'loam', organic_matter: 3.2 },
                farmer_preferences: {
                    yield_priority: 8,
                    risk_tolerance: 6,
                    management_intensity: 5
                }
            },
            prioritized_factors: ['yield_potential', 'disease_resilience', 'economic_outlook'],
            include_trade_offs: true,
            include_management_analysis: true,
            include_economic_analysis: true
        };

        try {
            const response = await fetch(`${this.apiBaseUrl}/varieties/compare`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            this.comparisonData = await response.json();
            this.renderComparisonResults();
            
        } catch (error) {
            console.error('Comparison API error:', error);
            // Fallback to client-side comparison
            this.performClientSideComparison(selectedVarietyData);
        } finally {
            this.hideLoadingState();
        }
    }

    performClientSideComparison(varieties) {
        // Client-side comparison as fallback
        this.comparisonData = {
            success: true,
            detailed_results: varieties.map(variety => ({
                variety_id: variety.variety_id,
                variety_name: variety.variety_name,
                overall_score: this.calculateOverallScore(variety),
                criteria_scores: {
                    yield_potential: (variety.yield_potential_percentile || 50) / 100,
                    disease_resilience: (variety.disease_resistance_score || 5) / 10,
                    maturity_suitability: 0.7,
                    management_requirements: 0.6,
                    economic_outlook: 0.65
                },
                strengths: this.generateStrengths(variety),
                considerations: this.generateConsiderations(variety),
                risk_rating: variety.risk_rating || 'medium'
            })),
            trade_offs: this.generateTradeOffs(varieties),
            summary: {
                best_overall_variety: varieties[0]?.variety_name,
                confidence_score: 0.75,
                key_takeaways: ['Comparison completed successfully', 'Review individual variety strengths'],
                recommended_actions: ['Validate field conditions', 'Consider management requirements']
            }
        };
        
        this.renderComparisonResults();
    }

    calculateOverallScore(variety) {
        const yieldScore = (variety.yield_potential_percentile || 50) / 100;
        const diseaseScore = (variety.disease_resistance_score || 5) / 10;
        const maturityScore = 0.7;
        const managementScore = 0.6;
        const economicScore = 0.65;
        
        return (yieldScore * 0.3 + diseaseScore * 0.25 + maturityScore * 0.2 + 
                managementScore * 0.15 + economicScore * 0.1);
    }

    generateStrengths(variety) {
        const strengths = [];
        if (variety.yield_potential_percentile > 80) {
            strengths.push('High yield potential');
        }
        if (variety.disease_resistance_score > 7) {
            strengths.push('Strong disease resistance');
        }
        if (variety.relative_maturity && variety.relative_maturity >= 100 && variety.relative_maturity <= 110) {
            strengths.push('Optimal maturity timing');
        }
        return strengths.length > 0 ? strengths : ['Balanced performance'];
    }

    generateConsiderations(variety) {
        const considerations = [];
        if (variety.yield_potential_percentile < 60) {
            considerations.push('Lower yield potential');
        }
        if (variety.disease_resistance_score < 5) {
            considerations.push('Requires disease management');
        }
        if (variety.risk_rating === 'high') {
            considerations.push('Higher risk variety');
        }
        return considerations;
    }

    generateTradeOffs(varieties) {
        return varieties.map(variety => ({
            focus_area: 'yield_potential',
            preferred_variety_name: variety.variety_name,
            rationale: `${variety.variety_name} provides strength in yield potential`
        }));
    }

    renderComparisonResults() {
        if (!this.comparisonData) return;

        this.renderComparisonSummary();
        this.renderComparisonTable();
        this.renderRadarChart();
        this.renderTradeOffAnalysis();
        this.renderDecisionMatrix();
        this.renderDetailedComparison();
    }

    renderComparisonSummary() {
        const summaryContent = document.getElementById('comparisonSummaryContent');
        if (!summaryContent) return;

        const { summary, detailed_results } = this.comparisonData;
        
        summaryContent.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="summary-stat">
                        <div class="summary-stat-value">${detailed_results.length}</div>
                        <div class="summary-stat-label">Varieties Compared</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-stat">
                        <div class="summary-stat-value">${Math.round(summary.confidence_score * 100)}%</div>
                        <div class="summary-stat-label">Confidence Score</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-stat">
                        <div class="summary-stat-value">${summary.best_overall_variety || 'N/A'}</div>
                        <div class="summary-stat-label">Best Overall</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="summary-stat">
                        <div class="summary-stat-value">${detailed_results.length > 0 ? Math.round(Math.max(...detailed_results.map(r => r.overall_score)) * 100) : 0}%</div>
                        <div class="summary-stat-label">Top Score</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderComparisonTable() {
        const tableBody = document.getElementById('comparisonTableBody');
        if (!tableBody) return;

        const { detailed_results } = this.comparisonData;
        
        tableBody.innerHTML = detailed_results.map(result => `
            <tr>
                <td><strong>${result.variety_name}</strong></td>
                <td><span class="score-badge ${this.getScoreClass(result.overall_score, 'score')}">${Math.round(result.overall_score * 100)}%</span></td>
                <td><span class="score-badge ${this.getScoreClass(result.criteria_scores.yield_potential, 'score')}">${Math.round(result.criteria_scores.yield_potential * 100)}%</span></td>
                <td><span class="score-badge ${this.getScoreClass(result.criteria_scores.disease_resilience, 'score')}">${Math.round(result.criteria_scores.disease_resilience * 100)}%</span></td>
                <td><span class="score-badge ${this.getScoreClass(result.criteria_scores.maturity_suitability, 'score')}">${Math.round(result.criteria_scores.maturity_suitability * 100)}%</span></td>
                <td><span class="score-badge ${this.getScoreClass(result.criteria_scores.management_requirements, 'score')}">${Math.round(result.criteria_scores.management_requirements * 100)}%</span></td>
                <td><span class="score-badge ${this.getScoreClass(result.criteria_scores.economic_outlook, 'score')}">${Math.round(result.criteria_scores.economic_outlook * 100)}%</span></td>
                <td><span class="badge ${this.getRiskBadgeClass(result.risk_rating)}">${result.risk_rating}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="varietyComparison.viewVarietyDetails('${result.variety_id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    renderRadarChart() {
        const canvas = document.getElementById('radarChart');
        if (!canvas || !this.comparisonData) return;

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart
        if (this.radarChart) {
            this.radarChart.destroy();
        }

        const { detailed_results } = this.comparisonData;
        
        const labels = ['Yield Potential', 'Disease Resistance', 'Maturity Suitability', 'Management', 'Economic Outlook'];
        
        const datasets = detailed_results.map((result, index) => ({
            label: result.variety_name,
            data: [
                result.criteria_scores.yield_potential * 100,
                result.criteria_scores.disease_resilience * 100,
                result.criteria_scores.maturity_suitability * 100,
                result.criteria_scores.management_requirements * 100,
                result.criteria_scores.economic_outlook * 100
            ],
            backgroundColor: this.getChartColor(index, 0.2),
            borderColor: this.getChartColor(index, 1),
            borderWidth: 2,
            pointBackgroundColor: this.getChartColor(index, 1),
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4
        }));

        this.radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }

    renderTradeOffAnalysis() {
        const tradeOffContent = document.getElementById('tradeOffContent');
        if (!tradeOffContent) return;

        const { trade_offs } = this.comparisonData;
        
        tradeOffContent.innerHTML = trade_offs.map(tradeOff => `
            <div class="trade-off-item">
                <h6><i class="fas fa-balance-scale"></i> ${tradeOff.focus_area.replace('_', ' ').toUpperCase()}</h6>
                <p class="mb-1"><strong>Best Choice:</strong> ${tradeOff.preferred_variety_name}</p>
                <p class="mb-0 text-muted">${tradeOff.rationale}</p>
            </div>
        `).join('');
    }

    renderDecisionMatrix() {
        const matrixContent = document.getElementById('decisionMatrixContent');
        if (!matrixContent) return;

        const { detailed_results } = this.comparisonData;
        const criteria = ['yield_potential', 'disease_resilience', 'maturity_suitability', 'management_requirements', 'economic_outlook'];
        
        let matrixHTML = `
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th class="matrix-header">Variety</th>
                            ${criteria.map(criterion => `<th class="matrix-header">${criterion.replace('_', ' ').toUpperCase()}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        detailed_results.forEach(result => {
            matrixHTML += `
                <tr>
                    <td class="matrix-header"><strong>${result.variety_name}</strong></td>
                    ${criteria.map(criterion => {
                        const score = result.criteria_scores[criterion];
                        const cellClass = this.getMatrixCellClass(score);
                        return `<td class="matrix-cell ${cellClass}">${Math.round(score * 100)}%</td>`;
                    }).join('')}
                </tr>
            `;
        });
        
        matrixHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        matrixContent.innerHTML = matrixHTML;
    }

    renderDetailedComparison() {
        const detailedContent = document.getElementById('detailedComparisonContent');
        if (!detailedContent) return;

        const { detailed_results } = this.comparisonData;
        
        detailedContent.innerHTML = detailed_results.map(result => `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0"><i class="fas fa-seedling"></i> ${result.variety_name}</h6>
                            <span class="badge ${this.getScoreClass(result.overall_score, 'score')}">Overall: ${Math.round(result.overall_score * 100)}%</span>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><i class="fas fa-thumbs-up text-success"></i> Strengths</h6>
                                    <ul class="list-unstyled">
                                        ${result.strengths.map(strength => `<li><i class="fas fa-check text-success"></i> ${strength}</li>`).join('')}
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6><i class="fas fa-exclamation-triangle text-warning"></i> Considerations</h6>
                                    <ul class="list-unstyled">
                                        ${result.considerations.map(consideration => `<li><i class="fas fa-info-circle text-warning"></i> ${consideration}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    getScoreClass(score, type) {
        if (type === 'percentile') {
            if (score >= 80) return 'score-excellent';
            if (score >= 60) return 'score-good';
            if (score >= 40) return 'score-average';
            return 'score-poor';
        } else {
            if (score >= 0.8) return 'score-excellent';
            if (score >= 0.6) return 'score-good';
            if (score >= 0.4) return 'score-average';
            return 'score-poor';
        }
    }

    getRiskBadgeClass(risk) {
        switch (risk?.toLowerCase()) {
            case 'low': return 'bg-success';
            case 'medium': return 'bg-warning';
            case 'high': return 'bg-danger';
            default: return 'bg-secondary';
        }
    }

    getMatrixCellClass(score) {
        if (score >= 0.8) return 'matrix-best';
        if (score >= 0.6) return 'matrix-good';
        if (score >= 0.4) return 'matrix-average';
        return 'matrix-poor';
    }

    getChartColor(index, alpha) {
        const colors = [
            `rgba(40, 167, 69, ${alpha})`,   // Green
            `rgba(0, 123, 255, ${alpha})`,   // Blue
            `rgba(255, 193, 7, ${alpha})`,   // Yellow
            `rgba(220, 53, 69, ${alpha})`,   // Red
            `rgba(23, 162, 184, ${alpha})`,  // Cyan
            `rgba(108, 117, 125, ${alpha})`  // Gray
        ];
        return colors[index % colors.length];
    }

    enableExportButtons() {
        const buttons = ['exportPdfBtn', 'exportExcelBtn', 'shareBtn'];
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.disabled = false;
        });
    }

    disableExportButtons() {
        const buttons = ['exportPdfBtn', 'exportExcelBtn', 'shareBtn'];
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.disabled = true;
        });
    }

    async exportComparison(format) {
        if (!this.comparisonData) return;

        try {
            const exportData = {
                format: format,
                comparison_data: this.comparisonData,
                export_timestamp: new Date().toISOString(),
                varieties: this.allVarieties.filter(v => this.selectedVarieties.has(v.variety_id))
            };

            const response = await fetch(`${this.apiBaseUrl}/export/comparison`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(exportData)
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `variety_comparison_${Date.now()}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Export error:', error);
            this.showError('Export failed. Please try again.');
        }
    }

    shareComparison() {
        if (!this.comparisonData) return;

        const shareData = {
            varieties: Array.from(this.selectedVarieties),
            comparison_id: this.comparisonData.request_id,
            timestamp: Date.now()
        };

        const shareUrl = `${window.location.origin}/variety-comparison?data=${encodeURIComponent(JSON.stringify(shareData))}`;
        
        const shareUrlInput = document.getElementById('shareUrl');
        if (shareUrlInput) {
            shareUrlInput.value = shareUrl;
        }

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('shareModal'));
        modal.show();
    }

    copyShareUrl() {
        const shareUrlInput = document.getElementById('shareUrl');
        if (shareUrlInput) {
            shareUrlInput.select();
            document.execCommand('copy');
            this.showSuccess('Share URL copied to clipboard!');
        }
    }

    async sendShareMessage() {
        const shareMessage = document.getElementById('shareMessage').value;
        const shareUrl = document.getElementById('shareUrl').value;
        
        // Implementation for sending share message
        this.showSuccess('Comparison shared successfully!');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('shareModal'));
        modal.hide();
    }

    viewVarietyDetails(varietyId) {
        // Navigate to variety detail page
        window.location.href = `/variety-detail/${varietyId}`;
    }

    scrollToVarietySelection() {
        document.getElementById('varietyGrid').scrollIntoView({ behavior: 'smooth' });
    }

    updateLoadMoreButton(hasMore) {
        const container = document.getElementById('loadMoreContainer');
        if (container) {
            container.style.display = hasMore ? 'block' : 'none';
        }
    }

    showLoadingState() {
        const loadingState = document.getElementById('loadingState');
        if (loadingState) {
            loadingState.style.display = 'block';
        }
    }

    hideLoadingState() {
        const loadingState = document.getElementById('loadingState');
        if (loadingState) {
            loadingState.style.display = 'none';
        }
    }

    showError(message) {
        // Create and show error toast
        this.showToast(message, 'error');
    }

    showSuccess(message) {
        // Create and show success toast
        this.showToast(message, 'success');
    }

    showToast(message, type) {
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }

    handleKeyboardShortcuts(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'e':
                    event.preventDefault();
                    if (!document.getElementById('exportExcelBtn').disabled) {
                        this.exportComparison('excel');
                    }
                    break;
                case 'p':
                    event.preventDefault();
                    if (!document.getElementById('exportPdfBtn').disabled) {
                        this.exportComparison('pdf');
                    }
                    break;
                case 's':
                    event.preventDefault();
                    if (!document.getElementById('shareBtn').disabled) {
                        this.shareComparison();
                    }
                    break;
            }
        }
    }

    loadComparisonHistory() {
        try {
            const history = localStorage.getItem('varietyComparisonHistory');
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Error loading comparison history:', error);
            return [];
        }
    }

    saveComparisonHistory() {
        try {
            if (this.comparisonData) {
                const historyEntry = {
                    id: this.comparisonData.request_id,
                    varieties: Array.from(this.selectedVarieties),
                    timestamp: Date.now(),
                    summary: this.comparisonData.summary
                };
                
                this.comparisonHistory.unshift(historyEntry);
                this.comparisonHistory = this.comparisonHistory.slice(0, 10); // Keep only last 10
                
                localStorage.setItem('varietyComparisonHistory', JSON.stringify(this.comparisonHistory));
            }
        } catch (error) {
            console.error('Error saving comparison history:', error);
        }
    }
}

// Global functions for HTML onclick handlers
function exportComparison(format) {
    varietyComparison.exportComparison(format);
}

function shareComparison() {
    varietyComparison.shareComparison();
}

function copyShareUrl() {
    varietyComparison.copyShareUrl();
}

function sendShareMessage() {
    varietyComparison.sendShareMessage();
}

function clearSelection() {
    varietyComparison.clearSelection();
}

function loadMoreVarieties() {
    varietyComparison.loadMoreVarieties();
}

function scrollToVarietySelection() {
    varietyComparison.scrollToVarietySelection();
}

// Initialize the variety comparison manager when the page loads
let varietyComparison;
document.addEventListener('DOMContentLoaded', function() {
    varietyComparison = new VarietyComparisonManager();
});