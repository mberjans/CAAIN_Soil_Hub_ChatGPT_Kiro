/**
 * Comprehensive Explanation and Reasoning Display System
 * 
 * This module provides interactive explanation components with expandable sections,
 * evidence display, confidence visualization, and educational content integration.
 */

class ComprehensiveExplanationManager {
    constructor() {
        this.apiBaseUrl = '/api/v1/explanations';
        this.currentExplanation = null;
        this.expandedSections = new Set();
        this.activeEvidence = null;
        this.accessibilityMode = false;
        this.highContrastMode = false;
        
        this.initializeEventListeners();
        this.initializeAccessibility();
    }

    /**
     * Generate comprehensive explanation for a variety recommendation
     */
    async generateComprehensiveExplanation(varietyData, context, options = {}) {
        try {
            this.showLoadingState();
            
            const requestData = {
                variety_data: varietyData,
                context: context,
                explanation_options: {
                    include_detailed_reasoning: true,
                    include_evidence: true,
                    include_trade_offs: true,
                    include_risk_analysis: true,
                    include_economic_analysis: true,
                    include_management_guidance: true,
                    explanation_style: "comprehensive",
                    max_sections: 7,
                    ...options
                }
            };

            const response = await fetch(`${this.apiBaseUrl}/comprehensive`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const explanation = await response.json();
                this.currentExplanation = explanation;
                this.displayComprehensiveExplanation(explanation);
                this.announceToScreenReader("Comprehensive explanation loaded with multiple sections");
            } else {
                throw new Error('Failed to generate comprehensive explanation');
            }
        } catch (error) {
            console.error('Error generating comprehensive explanation:', error);
            this.showError('Failed to generate comprehensive explanation. Please try again.');
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Display comprehensive explanation with all sections
     */
    displayComprehensiveExplanation(explanation) {
        const container = document.getElementById('comprehensiveExplanationContainer');
        if (!container) {
            console.error('Comprehensive explanation container not found');
            return;
        }

        container.innerHTML = this.createExplanationHTML(explanation);
        this.initializeInteractiveElements();
        this.setupAccessibilityFeatures(explanation.accessibility_features);
    }

    /**
     * Create HTML structure for comprehensive explanation
     */
    createExplanationHTML(explanation) {
        const confidenceColor = this.getConfidenceColor(explanation.overall_confidence);
        
        return `
            <div class="comprehensive-explanation" role="main" aria-label="Comprehensive variety recommendation explanation">
                <!-- Header Section -->
                <div class="explanation-header">
                    <div class="variety-info">
                        <h2 class="variety-name">${explanation.variety_name}</h2>
                        <div class="confidence-meter">
                            <div class="confidence-label">Overall Confidence</div>
                            <div class="confidence-bar">
                                <div class="confidence-fill ${confidenceColor}" 
                                     style="width: ${explanation.overall_confidence * 100}%"
                                     aria-label="Confidence level: ${Math.round(explanation.overall_confidence * 100)}%">
                                </div>
                            </div>
                            <div class="confidence-value">${Math.round(explanation.overall_confidence * 100)}%</div>
                        </div>
                    </div>
                    <div class="explanation-controls">
                        <button class="btn btn-outline-secondary" onclick="explanationManager.toggleAllSections()">
                            <i class="fas fa-expand-arrows-alt"></i> Toggle All
                        </button>
                        <button class="btn btn-outline-info" onclick="explanationManager.toggleAccessibilityMode()">
                            <i class="fas fa-universal-access"></i> Accessibility
                        </button>
                        <button class="btn btn-outline-dark" onclick="explanationManager.toggleHighContrast()">
                            <i class="fas fa-adjust"></i> High Contrast
                        </button>
                    </div>
                </div>

                <!-- Summary Section -->
                <div class="explanation-summary">
                    <h3><i class="fas fa-lightbulb"></i> Recommendation Summary</h3>
                    <p class="summary-text">${explanation.summary}</p>
                    
                    <div class="key-insights">
                        <h4>Key Insights</h4>
                        <ul>
                            ${explanation.key_insights.map(insight => `<li>${insight}</li>`).join('')}
                        </ul>
                    </div>
                </div>

                <!-- Explanation Sections -->
                <div class="explanation-sections" role="region" aria-label="Detailed explanation sections">
                    ${explanation.sections.map(section => this.createSectionHTML(section)).join('')}
                </div>

                <!-- Recommendations Section -->
                <div class="recommendations-section">
                    <h3><i class="fas fa-tasks"></i> Actionable Recommendations</h3>
                    <ul class="recommendations-list">
                        ${explanation.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>

                <!-- Educational Resources -->
                <div class="educational-resources">
                    <h3><i class="fas fa-graduation-cap"></i> Educational Resources</h3>
                    <div class="resources-grid">
                        ${explanation.educational_resources.map(resource => `
                            <div class="resource-card">
                                <h5>${resource.title}</h5>
                                <p class="resource-type">${resource.type}</p>
                                <a href="${resource.url}" class="btn btn-outline-primary" target="_blank">
                                    <i class="fas fa-external-link-alt"></i> Learn More
                                </a>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create HTML for individual explanation section
     */
    createSectionHTML(section) {
        const isExpanded = this.expandedSections.has(section.section_id);
        const confidenceColor = this.getConfidenceColor(section.confidence_level);
        const expandableClass = section.expandable ? 'expandable' : '';
        
        return `
            <div class="explanation-section ${expandableClass}" 
                 id="section-${section.section_id}"
                 role="region" 
                 aria-label="${section.title} section">
                
                <!-- Section Header -->
                <div class="section-header" 
                     ${section.expandable ? `onclick="explanationManager.toggleSection('${section.section_id}')"` : ''}
                     ${section.expandable ? 'tabindex="0" role="button"' : ''}
                     aria-expanded="${isExpanded}">
                    
                    <div class="section-title">
                        <h4>${section.title}</h4>
                        <div class="section-confidence">
                            <span class="confidence-badge ${confidenceColor}">${section.confidence_level}</span>
                        </div>
                    </div>
                    
                    ${section.expandable ? `
                        <div class="section-toggle">
                            <i class="fas fa-chevron-${isExpanded ? 'up' : 'down'}"></i>
                        </div>
                    ` : ''}
                </div>

                <!-- Section Content -->
                <div class="section-content ${isExpanded ? 'expanded' : 'collapsed'}" 
                     aria-hidden="${!isExpanded}">
                    
                    <!-- Main Content -->
                    <div class="section-main-content">
                        ${section.content}
                    </div>

                    <!-- Evidence Items -->
                    ${section.evidence_items.length > 0 ? `
                        <div class="evidence-section">
                            <h5><i class="fas fa-clipboard-check"></i> Supporting Evidence</h5>
                            <div class="evidence-grid">
                                ${section.evidence_items.map(evidence => this.createEvidenceHTML(evidence)).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Interactive Elements -->
                    ${section.interactive_elements.length > 0 ? `
                        <div class="interactive-elements">
                            <h5><i class="fas fa-mouse-pointer"></i> Interactive Features</h5>
                            <div class="interactive-buttons">
                                ${section.interactive_elements.map(element => `
                                    <button class="btn btn-sm btn-outline-primary" 
                                            onclick="explanationManager.handleInteractiveElement('${element.type}', '${section.section_id}')">
                                        <i class="fas fa-${this.getInteractiveIcon(element.type)}"></i> ${element.title}
                                    </button>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}

                    <!-- Educational Content -->
                    ${section.educational_content ? `
                        <div class="educational-content">
                            <button class="btn btn-sm btn-outline-info" 
                                    onclick="explanationManager.toggleEducationalContent('${section.section_id}')">
                                <i class="fas fa-info-circle"></i> Learn More
                            </button>
                            <div class="educational-text" id="edu-${section.section_id}" style="display: none;">
                                <p>${section.educational_content}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Create HTML for evidence item
     */
    createEvidenceHTML(evidence) {
        const confidenceColor = this.getConfidenceColor(evidence.confidence);
        
        return `
            <div class="evidence-item" 
                 onclick="explanationManager.showEvidenceDetails('${evidence.title}')"
                 tabindex="0" 
                 role="button"
                 aria-label="Evidence item: ${evidence.title}">
                
                <div class="evidence-header">
                    <h6>${evidence.title}</h6>
                    <span class="evidence-confidence ${confidenceColor}">
                        ${Math.round(evidence.confidence * 100)}%
                    </span>
                </div>
                
                <div class="evidence-description">
                    <p>${evidence.description}</p>
                </div>
                
                <div class="evidence-meta">
                    <span class="evidence-source">
                        <i class="fas fa-source"></i> ${evidence.source}
                    </span>
                    <span class="evidence-type">
                        <i class="fas fa-tag"></i> ${evidence.data_type}
                    </span>
                </div>
                
                ${evidence.supporting_data ? `
                    <div class="evidence-data">
                        <button class="btn btn-sm btn-outline-secondary" 
                                onclick="explanationManager.showSupportingData('${evidence.title}', event)">
                            <i class="fas fa-chart-bar"></i> View Data
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Toggle section expansion
     */
    toggleSection(sectionId) {
        const section = document.getElementById(`section-${sectionId}`);
        const content = section.querySelector('.section-content');
        const toggle = section.querySelector('.section-toggle i');
        const header = section.querySelector('.section-header');
        
        if (this.expandedSections.has(sectionId)) {
            this.expandedSections.delete(sectionId);
            content.classList.remove('expanded');
            content.classList.add('collapsed');
            toggle.className = 'fas fa-chevron-down';
            header.setAttribute('aria-expanded', 'false');
            content.setAttribute('aria-hidden', 'true');
        } else {
            this.expandedSections.add(sectionId);
            content.classList.remove('collapsed');
            content.classList.add('expanded');
            toggle.className = 'fas fa-chevron-up';
            header.setAttribute('aria-expanded', 'true');
            content.setAttribute('aria-hidden', 'false');
        }
        
        this.announceToScreenReader(`Section ${sectionId} ${this.expandedSections.has(sectionId) ? 'expanded' : 'collapsed'}`);
    }

    /**
     * Toggle all sections
     */
    toggleAllSections() {
        const allExpanded = this.expandedSections.size === this.currentExplanation.sections.length;
        
        this.currentExplanation.sections.forEach(section => {
            if (section.expandable) {
                if (allExpanded) {
                    this.expandedSections.delete(section.section_id);
                } else {
                    this.expandedSections.add(section.section_id);
                }
            }
        });
        
        // Re-render to update all sections
        this.displayComprehensiveExplanation(this.currentExplanation);
        this.announceToScreenReader(`All sections ${allExpanded ? 'collapsed' : 'expanded'}`);
    }

    /**
     * Show evidence details in modal
     */
    showEvidenceDetails(evidenceTitle) {
        if (!this.currentExplanation) return;
        
        // Find evidence item
        let evidenceItem = null;
        for (const section of this.currentExplanation.sections) {
            evidenceItem = section.evidence_items.find(e => e.title === evidenceTitle);
            if (evidenceItem) break;
        }
        
        if (!evidenceItem) return;
        
        // Create and show modal
        const modal = this.createEvidenceModal(evidenceItem);
        document.body.appendChild(modal);
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Clean up when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    /**
     * Create evidence details modal
     */
    createEvidenceModal(evidence) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${evidence.title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="evidence-details">
                            <div class="evidence-description">
                                <h6>Description</h6>
                                <p>${evidence.description}</p>
                            </div>
                            
                            <div class="evidence-meta">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Source</h6>
                                        <p>${evidence.source}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Data Type</h6>
                                        <p>${evidence.data_type}</p>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Confidence</h6>
                                        <div class="confidence-bar">
                                            <div class="confidence-fill ${this.getConfidenceColor(evidence.confidence)}" 
                                                 style="width: ${evidence.confidence * 100}%">
                                            </div>
                                        </div>
                                        <span>${Math.round(evidence.confidence * 100)}%</span>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Relevance Score</h6>
                                        <div class="confidence-bar">
                                            <div class="confidence-fill ${this.getConfidenceColor(evidence.relevance_score)}" 
                                                 style="width: ${evidence.relevance_score * 100}%">
                                            </div>
                                        </div>
                                        <span>${Math.round(evidence.relevance_score * 100)}%</span>
                                    </div>
                                </div>
                            </div>
                            
                            ${evidence.supporting_data ? `
                                <div class="evidence-supporting-data">
                                    <h6>Supporting Data</h6>
                                    <div class="data-display">
                                        ${Object.entries(evidence.supporting_data).map(([key, value]) => `
                                            <div class="data-item">
                                                <strong>${key.replace('_', ' ').toUpperCase()}:</strong> ${value}
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    /**
     * Handle interactive element clicks
     */
    handleInteractiveElement(elementType, sectionId) {
        switch (elementType) {
            case 'roi_calculator':
                this.showROICalculator(sectionId);
                break;
            case 'cost_comparison':
                this.showCostComparison(sectionId);
                break;
            case 'risk_calculator':
                this.showRiskCalculator(sectionId);
                break;
            case 'management_calendar':
                this.showManagementCalendar(sectionId);
                break;
            default:
                console.log(`Interactive element ${elementType} clicked for section ${sectionId}`);
        }
    }

    /**
     * Show ROI calculator modal
     */
    showROICalculator(sectionId) {
        const modal = this.createROICalculatorModal(sectionId);
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    /**
     * Create ROI calculator modal
     */
    createROICalculatorModal(sectionId) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">ROI Calculator</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="roi-calculator">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Expected Yield (bushels/acre)</label>
                                        <input type="number" class="form-control" id="expectedYield" value="180">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Expected Price ($/bushel)</label>
                                        <input type="number" class="form-control" id="expectedPrice" value="5.50" step="0.01">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Seed Cost ($/acre)</label>
                                        <input type="number" class="form-control" id="seedCost" value="145" step="0.01">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Additional Inputs ($/acre)</label>
                                        <input type="number" class="form-control" id="additionalInputs" value="25" step="0.01">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Premium Potential (%)</label>
                                        <input type="number" class="form-control" id="premiumPotential" value="15" step="0.1">
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Acres</label>
                                        <input type="number" class="form-control" id="acres" value="100">
                                    </div>
                                </div>
                            </div>
                            <div class="roi-results">
                                <h6>ROI Calculation Results</h6>
                                <div class="results-grid">
                                    <div class="result-item">
                                        <span class="result-label">Total Revenue:</span>
                                        <span class="result-value" id="totalRevenue">$0</span>
                                    </div>
                                    <div class="result-item">
                                        <span class="result-label">Total Costs:</span>
                                        <span class="result-value" id="totalCosts">$0</span>
                                    </div>
                                    <div class="result-item">
                                        <span class="result-label">Net Profit:</span>
                                        <span class="result-value" id="netProfit">$0</span>
                                    </div>
                                    <div class="result-item">
                                        <span class="result-label">ROI:</span>
                                        <span class="result-value" id="roi">0%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" onclick="explanationManager.calculateROI()">
                            Calculate ROI
                        </button>
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    /**
     * Calculate ROI
     */
    calculateROI() {
        const yield = parseFloat(document.getElementById('expectedYield').value) || 0;
        const price = parseFloat(document.getElementById('expectedPrice').value) || 0;
        const seedCost = parseFloat(document.getElementById('seedCost').value) || 0;
        const additionalInputs = parseFloat(document.getElementById('additionalInputs').value) || 0;
        const premiumPotential = parseFloat(document.getElementById('premiumPotential').value) || 0;
        const acres = parseFloat(document.getElementById('acres').value) || 0;
        
        const adjustedPrice = price * (1 + premiumPotential / 100);
        const totalRevenue = yield * adjustedPrice * acres;
        const totalCosts = (seedCost + additionalInputs) * acres;
        const netProfit = totalRevenue - totalCosts;
        const roi = totalCosts > 0 ? (netProfit / totalCosts) * 100 : 0;
        
        document.getElementById('totalRevenue').textContent = `$${totalRevenue.toLocaleString()}`;
        document.getElementById('totalCosts').textContent = `$${totalCosts.toLocaleString()}`;
        document.getElementById('netProfit').textContent = `$${netProfit.toLocaleString()}`;
        document.getElementById('roi').textContent = `${roi.toFixed(1)}%`;
    }

    /**
     * Toggle educational content
     */
    toggleEducationalContent(sectionId) {
        const eduContent = document.getElementById(`edu-${sectionId}`);
        if (eduContent) {
            const isVisible = eduContent.style.display !== 'none';
            eduContent.style.display = isVisible ? 'none' : 'block';
        }
    }

    /**
     * Toggle accessibility mode
     */
    toggleAccessibilityMode() {
        this.accessibilityMode = !this.accessibilityMode;
        document.body.classList.toggle('accessibility-mode', this.accessibilityMode);
        
        if (this.accessibilityMode) {
            this.announceToScreenReader("Accessibility mode enabled");
        } else {
            this.announceToScreenReader("Accessibility mode disabled");
        }
    }

    /**
     * Toggle high contrast mode
     */
    toggleHighContrast() {
        this.highContrastMode = !this.highContrastMode;
        document.body.classList.toggle('high-contrast-mode', this.highContrastMode);
        
        if (this.highContrastMode) {
            this.announceToScreenReader("High contrast mode enabled");
        } else {
            this.announceToScreenReader("High contrast mode disabled");
        }
    }

    /**
     * Initialize interactive elements
     */
    initializeInteractiveElements() {
        // Add click handlers for expandable sections
        document.querySelectorAll('.section-header[role="button"]').forEach(header => {
            header.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    header.click();
                }
            });
        });
        
        // Add click handlers for evidence items
        document.querySelectorAll('.evidence-item[role="button"]').forEach(item => {
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    item.click();
                }
            });
        });
    }

    /**
     * Setup accessibility features
     */
    setupAccessibilityFeatures(accessibilityFeatures) {
        // Add ARIA labels
        Object.entries(accessibilityFeatures.aria_labels || {}).forEach(([sectionId, label]) => {
            const section = document.getElementById(`section-${sectionId}`);
            if (section) {
                section.setAttribute('aria-label', label);
            }
        });
        
        // Setup keyboard navigation
        const sections = accessibilityFeatures.keyboard_navigation?.sections || [];
        sections.forEach((sectionId, index) => {
            const section = document.getElementById(`section-${sectionId}`);
            if (section) {
                section.setAttribute('tabindex', '0');
                section.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowDown' && index < sections.length - 1) {
                        e.preventDefault();
                        document.getElementById(`section-${sections[index + 1]}`)?.focus();
                    } else if (e.key === 'ArrowUp' && index > 0) {
                        e.preventDefault();
                        document.getElementById(`section-${sections[index - 1]}`)?.focus();
                    }
                });
            }
        });
    }

    /**
     * Initialize accessibility features
     */
    initializeAccessibility() {
        // Create screen reader announcement area
        const announcementArea = document.createElement('div');
        announcementArea.id = 'screen-reader-announcements';
        announcementArea.setAttribute('aria-live', 'polite');
        announcementArea.setAttribute('aria-atomic', 'true');
        announcementArea.style.position = 'absolute';
        announcementArea.style.left = '-10000px';
        announcementArea.style.width = '1px';
        announcementArea.style.height = '1px';
        announcementArea.style.overflow = 'hidden';
        document.body.appendChild(announcementArea);
    }

    /**
     * Announce message to screen readers
     */
    announceToScreenReader(message) {
        const announcementArea = document.getElementById('screen-reader-announcements');
        if (announcementArea) {
            announcementArea.textContent = message;
        }
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'a':
                        e.preventDefault();
                        this.toggleAccessibilityMode();
                        break;
                    case 'h':
                        e.preventDefault();
                        this.toggleHighContrast();
                        break;
                    case 'e':
                        e.preventDefault();
                        this.toggleAllSections();
                        break;
                }
            }
        });
    }

    /**
     * Get confidence color class
     */
    getConfidenceColor(confidence) {
        if (typeof confidence === 'string') {
            return confidence.toLowerCase().replace('_', '-');
        }
        
        if (confidence >= 0.8) return 'high';
        if (confidence >= 0.6) return 'medium';
        if (confidence >= 0.4) return 'low';
        return 'very-low';
    }

    /**
     * Get interactive element icon
     */
    getInteractiveIcon(elementType) {
        const icons = {
            'roi_calculator': 'calculator',
            'cost_comparison': 'balance-scale',
            'risk_calculator': 'exclamation-triangle',
            'management_calendar': 'calendar',
            'expandable_evidence': 'expand',
            'evidence_filter': 'filter',
            'confidence_meter': 'chart-line',
            'pros_cons_toggle': 'toggle-on',
            'cost_calculator': 'calculator',
            'profit_projector': 'chart-bar',
            'mitigation_planner': 'clipboard-list',
            'task_reminder': 'bell',
            'best_practices': 'book'
        };
        return icons[elementType] || 'cog';
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const container = document.getElementById('comprehensiveExplanationContainer');
        if (container) {
            container.innerHTML = `
                <div class="loading-state text-center">
                    <div class="spinner-border text-success" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Generating comprehensive explanation...</p>
                </div>
            `;
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        // Loading state will be replaced by explanation content
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('comprehensiveExplanationContainer');
        if (container) {
            container.innerHTML = `
                <div class="error-state">
                    <div class="alert alert-danger" role="alert">
                        <h4 class="alert-heading">Error</h4>
                        <p>${message}</p>
                        <hr>
                        <p class="mb-0">Please try again or contact support if the problem persists.</p>
                    </div>
                </div>
            `;
        }
    }
}

// Initialize global instance
window.explanationManager = new ComprehensiveExplanationManager();