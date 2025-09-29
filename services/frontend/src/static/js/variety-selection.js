// Variety Selection JavaScript for CAAIN Soil Hub
// Provides comprehensive variety selection, filtering, comparison, and recommendation functionality

class VarietySelectionManager {
    constructor() {
        this.currentStep = 1;
        this.selectedCrop = null;
        this.selectedVarieties = new Set();
        this.varietyRecommendations = [];
        this.filteredVarieties = [];
        this.comparisonMode = false;
        this.farmData = {};
        this.userPreferences = {};
        this.searchDebounceTimer = null;
        this.apiBaseUrl = '/api/v1';
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCropSuggestions();
        this.initializeCharts();
    }

    setupEventListeners() {
        // Crop search functionality
        const cropSearch = document.getElementById('cropSearch');
        if (cropSearch) {
            cropSearch.addEventListener('input', this.handleCropSearch.bind(this));
            cropSearch.addEventListener('focus', this.showCropSuggestions.bind(this));
            cropSearch.addEventListener('blur', this.hideCropSuggestions.bind(this));
        }

        // Filter controls
        const filterInputs = ['maturityMin', 'maturityMax', 'yieldFilter', 'diseaseResistance', 'seedCompany'];
        filterInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.addEventListener('change', this.handleFilterChange.bind(this));
            }
        });

        // Variety selection
        document.addEventListener('click', this.handleVarietySelection.bind(this));

        // Keyboard navigation
        document.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
    }

    // Wizard Navigation Methods
    nextStep(stepNumber) {
        if (this.validateCurrentStep()) {
            this.currentStep = stepNumber;
            this.updateWizardDisplay();
            this.updateProgressBar();
        }
    }

    prevStep(stepNumber) {
        this.currentStep = stepNumber;
        this.updateWizardDisplay();
        this.updateProgressBar();
    }

    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.validateFarmInformation();
            case 2:
                return this.validateCropSelection();
            case 3:
                return this.validatePreferences();
            default:
                return true;
        }
    }

    validateFarmInformation() {
        const location = document.getElementById('farmLocation').value;
        const farmSize = document.getElementById('farmSize').value;
        const soilType = document.getElementById('soilType').value;

        if (!location || !farmSize || !soilType) {
            this.showAlert('Please fill in all farm information fields.', 'warning');
            return false;
        }

        // Store farm data
        this.farmData = {
            location: location,
            farmSize: parseInt(farmSize),
            soilType: soilType,
            irrigation: document.getElementById('irrigation').value === 'true'
        };

        return true;
    }

    validateCropSelection() {
        if (!this.selectedCrop) {
            this.showAlert('Please select a crop before proceeding.', 'warning');
            return false;
        }
        return true;
    }

    validatePreferences() {
        // Store user preferences
        this.userPreferences = {
            yieldPriority: parseInt(document.getElementById('yieldPriority').value),
            qualityFocus: document.getElementById('qualityFocus').value,
            riskTolerance: document.getElementById('riskTolerance').value,
            managementIntensity: document.getElementById('managementIntensity').value
        };
        return true;
    }

    updateWizardDisplay() {
        // Hide all steps
        document.querySelectorAll('.wizard-step').forEach(step => {
            step.classList.remove('active');
        });

        // Show current step
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
    }

    updateProgressBar() {
        const progress = (this.currentStep / 3) * 100;
        const progressBar = document.getElementById('wizardProgress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    // Crop Selection Methods
    async handleCropSearch(event) {
        const query = event.target.value;
        
        if (query.length < 2) {
            this.hideCropSuggestions();
            return;
        }

        // Debounce search
        clearTimeout(this.searchDebounceTimer);
        this.searchDebounceTimer = setTimeout(() => {
            this.searchCrops(query);
        }, 300);
    }

    async searchCrops(query) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/crops/search?query=${encodeURIComponent(query)}&limit=10`);
            if (response.ok) {
                const crops = await response.json();
                this.displayCropSuggestions(crops);
            } else {
                // Fallback to demo data
                this.displayCropSuggestions(this.getDemoCrops(query));
            }
        } catch (error) {
            console.warn('Crop search failed, using demo data:', error);
            this.displayCropSuggestions(this.getDemoCrops(query));
        }
    }

    displayCropSuggestions(crops) {
        const suggestionsContainer = document.getElementById('cropSuggestions');
        if (!suggestionsContainer) return;

        if (crops.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        suggestionsContainer.innerHTML = crops.map(crop => `
            <div class="suggestion-item" onclick="selectCropFromSuggestion('${crop.id}', '${crop.name}')">
                <strong>${crop.name}</strong>
                <br>
                <small class="text-muted">${crop.scientific_name || ''}</small>
            </div>
        `).join('');

        suggestionsContainer.style.display = 'block';
    }

    selectCropFromSuggestion(cropId, cropName) {
        this.selectedCrop = { id: cropId, name: cropName };
        document.getElementById('cropSearch').value = cropName;
        this.hideCropSuggestions();
        this.updateCropGrid();
        this.enableStep2Next();
    }

    hideCropSuggestions() {
        const suggestionsContainer = document.getElementById('cropSuggestions');
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    }

    showCropSuggestions() {
        const query = document.getElementById('cropSearch').value;
        if (query.length >= 2) {
            this.searchCrops(query);
        }
    }

    async showAllCrops() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/crops?limit=50`);
            if (response.ok) {
                const crops = await response.json();
                this.displayCropGrid(crops);
            } else {
                // Fallback to demo data
                this.displayCropGrid(this.getDemoCrops());
            }
        } catch (error) {
            console.warn('Failed to load crops, using demo data:', error);
            this.displayCropGrid(this.getDemoCrops());
        }
    }

    displayCropGrid(crops) {
        const cropGrid = document.getElementById('cropGrid');
        if (!cropGrid) return;

        cropGrid.innerHTML = crops.map(crop => `
            <div class="col-md-4 mb-3">
                <div class="card h-100 crop-card" onclick="selectCrop('${crop.id}', '${crop.name}')">
                    <div class="card-body text-center">
                        <i class="fas fa-seedling fa-3x text-success mb-3"></i>
                        <h6>${crop.name}</h6>
                        <small class="text-muted">${crop.scientific_name || ''}</small>
                        <br>
                        <small class="text-muted">${crop.category || ''}</small>
                    </div>
                </div>
            </div>
        `).join('');
    }

    selectCrop(cropId, cropName) {
        this.selectedCrop = { id: cropId, name: cropName };
        document.getElementById('cropSearch').value = cropName;
        this.updateCropGrid();
        this.enableStep2Next();
    }

    updateCropGrid() {
        // Highlight selected crop
        document.querySelectorAll('.crop-card').forEach(card => {
            card.classList.remove('border-success', 'bg-light');
        });

        if (this.selectedCrop) {
            const selectedCard = document.querySelector(`[onclick*="${this.selectedCrop.id}"]`);
            if (selectedCard) {
                selectedCard.classList.add('border-success', 'bg-light');
            }
        }
    }

    enableStep2Next() {
        const step2Next = document.getElementById('step2Next');
        if (step2Next) {
            step2Next.disabled = false;
        }
    }

    // Variety Recommendation Methods
    async getVarietyRecommendations() {
        if (!this.selectedCrop) {
            this.showAlert('Please select a crop first.', 'warning');
            return;
        }

        this.showLoadingState();

        try {
            const requestData = {
                crop_id: this.selectedCrop.id,
                farm_data: this.farmData,
                user_preferences: this.userPreferences,
                max_recommendations: 20
            };

            const response = await fetch(`${this.apiBaseUrl}/varieties/recommend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const recommendations = await response.json();
                this.varietyRecommendations = recommendations;
                this.filteredVarieties = [...recommendations];
                this.displayVarietyRecommendations();
            } else {
                throw new Error('Failed to get variety recommendations');
            }
        } catch (error) {
            console.warn('Variety recommendation failed, using demo data:', error);
            this.varietyRecommendations = this.getDemoVarietyRecommendations();
            this.filteredVarieties = [...this.varietyRecommendations];
            this.displayVarietyRecommendations();
        } finally {
            this.hideLoadingState();
        }
    }

    displayVarietyRecommendations() {
        this.showResultsSection();
        this.showFilterPanel();
        this.renderVarietyGrid();
        this.generateExplanation();
    }

    renderVarietyGrid() {
        const varietyGrid = document.getElementById('varietyGrid');
        if (!varietyGrid) return;

        varietyGrid.innerHTML = this.filteredVarieties.map(variety => this.createVarietyCard(variety)).join('');
    }

    createVarietyCard(variety) {
        const confidenceClass = variety.confidence >= 0.8 ? 'confidence-high' : 
                               variety.confidence >= 0.6 ? 'confidence-medium' : 'confidence-low';
        
        const traits = variety.traits || [];
        const traitBadges = traits.map(trait => `
            <span class="trait-badge ${trait.category || ''}">${trait.name}</span>
        `).join('');

        return `
            <div class="variety-card" data-variety-id="${variety.id}" onclick="toggleVarietySelection('${variety.id}')">
                <div class="row">
                    <div class="col-md-8">
                        <h5><i class="fas fa-seedling text-success"></i> ${variety.name}</h5>
                        <p class="text-muted mb-2">${variety.company || 'Unknown Company'}</p>
                        <p class="mb-3">${variety.description || 'No description available'}</p>
                        
                        <div class="row mb-3">
                            <div class="col-sm-6">
                                <small class="text-muted">Yield Potential:</small><br>
                                <strong>${variety.yield_potential || 'N/A'}</strong>
                            </div>
                            <div class="col-sm-6">
                                <small class="text-muted">Maturity:</small><br>
                                <strong>${variety.maturity_days || 'N/A'} days</strong>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <small class="text-muted">Key Traits:</small><br>
                            ${traitBadges || '<small class="text-muted">No traits specified</small>'}
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="mb-3">
                            <span class="badge bg-${variety.confidence >= 0.8 ? 'success' : variety.confidence >= 0.6 ? 'warning' : 'secondary'} mb-2">
                                ${variety.suitability || 'Good'}
                            </span>
                        </div>
                        <div class="confidence-meter mb-2">
                            <div class="confidence-fill ${confidenceClass}" 
                                 style="width: ${variety.confidence * 100}%"></div>
                        </div>
                        <small class="text-muted">Confidence: ${Math.round(variety.confidence * 100)}%</small>
                        
                        <div class="mt-3">
                            <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); viewVarietyDetails('${variety.id}')">
                                <i class="fas fa-info-circle"></i> Details
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Filtering Methods
    handleFilterChange() {
        this.applyFilters();
    }

    applyFilters() {
        const maturityMin = document.getElementById('maturityMin').value;
        const maturityMax = document.getElementById('maturityMax').value;
        const yieldFilter = document.getElementById('yieldFilter').value;
        const diseaseResistance = document.getElementById('diseaseResistance').value;
        const seedCompany = document.getElementById('seedCompany').value;

        this.filteredVarieties = this.varietyRecommendations.filter(variety => {
            // Maturity filter
            if (maturityMin && variety.maturity_days < parseInt(maturityMin)) return false;
            if (maturityMax && variety.maturity_days > parseInt(maturityMax)) return false;

            // Yield filter
            if (yieldFilter) {
                const yieldValue = parseFloat(variety.yield_potential) || 0;
                switch (yieldFilter) {
                    case 'high':
                        if (yieldValue < 90) return false;
                        break;
                    case 'medium':
                        if (yieldValue < 70 || yieldValue > 90) return false;
                        break;
                    case 'low':
                        if (yieldValue > 70) return false;
                        break;
                }
            }

            // Disease resistance filter
            if (diseaseResistance) {
                const resistanceLevel = variety.disease_resistance || 'low';
                if (resistanceLevel !== diseaseResistance) return false;
            }

            // Seed company filter
            if (seedCompany && variety.company && !variety.company.toLowerCase().includes(seedCompany.toLowerCase())) {
                return false;
            }

            return true;
        });

        this.renderVarietyGrid();
    }

    clearFilters() {
        document.getElementById('maturityMin').value = '';
        document.getElementById('maturityMax').value = '';
        document.getElementById('yieldFilter').value = '';
        document.getElementById('diseaseResistance').value = '';
        document.getElementById('seedCompany').value = '';

        this.filteredVarieties = [...this.varietyRecommendations];
        this.renderVarietyGrid();
    }

    // Comparison Methods
    toggleVarietySelection(varietyId) {
        if (this.selectedVarieties.has(varietyId)) {
            this.selectedVarieties.delete(varietyId);
        } else {
            this.selectedVarieties.add(varietyId);
        }

        this.updateVarietySelectionDisplay();
    }

    updateVarietySelectionDisplay() {
        document.querySelectorAll('.variety-card').forEach(card => {
            const varietyId = card.dataset.varietyId;
            if (this.selectedVarieties.has(varietyId)) {
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }

    toggleComparisonMode() {
        if (this.selectedVarieties.size < 2) {
            this.showAlert('Please select at least 2 varieties to compare.', 'warning');
            return;
        }

        this.comparisonMode = !this.comparisonMode;
        this.updateComparisonDisplay();
    }

    updateComparisonDisplay() {
        const varietyGrid = document.getElementById('varietyGrid');
        const comparisonTable = document.getElementById('comparisonTable');

        if (this.comparisonMode) {
            varietyGrid.style.display = 'none';
            comparisonTable.style.display = 'block';
            this.renderComparisonTable();
        } else {
            varietyGrid.style.display = 'grid';
            comparisonTable.style.display = 'none';
        }
    }

    renderComparisonTable() {
        const comparisonTableBody = document.getElementById('comparisonTableBody');
        if (!comparisonTableBody) return;

        const selectedVarieties = this.varietyRecommendations.filter(v => this.selectedVarieties.has(v.id));

        comparisonTableBody.innerHTML = selectedVarieties.map(variety => `
            <tr>
                <td>
                    <strong>${variety.name}</strong><br>
                    <small class="text-muted">${variety.company || 'Unknown'}</small>
                </td>
                <td>${variety.yield_potential || 'N/A'}</td>
                <td>${variety.maturity_days || 'N/A'} days</td>
                <td>
                    <span class="badge bg-${variety.disease_resistance === 'high' ? 'success' : variety.disease_resistance === 'medium' ? 'warning' : 'secondary'}">
                        ${variety.disease_resistance || 'Unknown'}
                    </span>
                </td>
                <td>
                    <div class="confidence-meter">
                        <div class="confidence-fill ${variety.confidence >= 0.8 ? 'confidence-high' : variety.confidence >= 0.6 ? 'confidence-medium' : 'confidence-low'}" 
                             style="width: ${variety.confidence * 100}%"></div>
                    </div>
                    <small>${Math.round(variety.confidence * 100)}%</small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeFromComparison('${variety.id}')">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    removeFromComparison(varietyId) {
        this.selectedVarieties.delete(varietyId);
        this.updateVarietySelectionDisplay();
        
        if (this.selectedVarieties.size < 2) {
            this.comparisonMode = false;
            this.updateComparisonDisplay();
        } else {
            this.renderComparisonTable();
        }
    }

    // Explanation Generation
    async generateExplanation() {
        try {
            const requestData = {
                crop_id: this.selectedCrop.id,
                farm_data: this.farmData,
                user_preferences: this.userPreferences,
                recommendations: this.varietyRecommendations.slice(0, 5) // Top 5 recommendations
            };

            const response = await fetch(`${this.apiBaseUrl}/varieties/explain`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            if (response.ok) {
                const explanation = await response.json();
                this.displayExplanation(explanation);
            } else {
                throw new Error('Failed to get explanation');
            }
        } catch (error) {
            console.warn('Explanation generation failed, using demo explanation:', error);
            this.displayExplanation(this.getDemoExplanation());
        }
    }

    displayExplanation(explanation) {
        const explanationPanel = document.getElementById('explanationPanel');
        const explanationContent = document.getElementById('explanationContent');
        
        if (explanationPanel && explanationContent) {
            explanationContent.innerHTML = `
                <div class="mb-3">
                    <h6><i class="fas fa-lightbulb"></i> Why These Varieties?</h6>
                    <p>${explanation.summary || 'These varieties were selected based on your farm conditions and preferences.'}</p>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-map-marker-alt"></i> Regional Adaptation</h6>
                        <p>${explanation.regional_adaptation || 'Varieties are well-suited to your local climate and soil conditions.'}</p>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-chart-line"></i> Performance Factors</h6>
                        <p>${explanation.performance_factors || 'Selected based on yield potential, disease resistance, and quality traits.'}</p>
                    </div>
                </div>
                
                <div class="mt-3">
                    <h6><i class="fas fa-exclamation-triangle"></i> Important Considerations</h6>
                    <ul>
                        ${(explanation.considerations || ['Monitor soil conditions regularly', 'Consider weather patterns', 'Plan for pest management']).map(consideration => `<li>${consideration}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-info" onclick="varietyManager.showComprehensiveExplanation()">
                        <i class="fas fa-microscope"></i> View Detailed Analysis
                    </button>
                </div>
            `;
            
            explanationPanel.style.display = 'block';
        }
    }

    async showComprehensiveExplanation() {
        if (!this.varietyRecommendations || this.varietyRecommendations.length === 0) {
            this.showAlert('No variety recommendations available for detailed analysis.', 'warning');
            return;
        }

        // Show comprehensive explanation panel
        const comprehensivePanel = document.getElementById('comprehensiveExplanationPanel');
        if (comprehensivePanel) {
            comprehensivePanel.style.display = 'block';
        }

        // Generate comprehensive explanation for the top variety
        const topVariety = this.varietyRecommendations[0];
        const varietyData = {
            variety_id: topVariety.id || 'demo-variety-1',
            variety_name: topVariety.name || 'Demo Variety',
            request_id: `comprehensive_${Date.now()}`,
            overall_score: topVariety.score || 0.85,
            scores: {
                yield_potential: topVariety.yield_potential || 0.88,
                disease_resistance: topVariety.disease_resistance || 0.92,
                soil_compatibility: topVariety.soil_compatibility || 0.85,
                market_acceptance: topVariety.market_acceptance || 0.80
            },
            data_completeness: 0.9,
            testing_years: 4,
            trial_yield: topVariety.trial_yield || 185,
            trial_years: 3,
            farmer_satisfaction: topVariety.farmer_satisfaction || 87,
            resistant_diseases: topVariety.resistant_diseases || ['Northern Corn Leaf Blight', 'Gray Leaf Spot'],
            disease_cost_savings: 35,
            strengths: topVariety.strengths || ['High yield potential', 'Strong disease resistance'],
            considerations: topVariety.considerations || ['Higher seed cost', 'Requires careful management'],
            risk_level: 'low',
            risk_factors: [
                {factor: 'Weather Sensitivity', level: 'Low', description: 'Good stability across conditions'},
                {factor: 'Management Risk', level: 'Medium', description: 'Requires attention to nitrogen management'}
            ],
            mitigation_strategies: ['Precision nitrogen management', 'Regular monitoring'],
            estimated_roi: 1.35,
            break_even_yield: 165.5,
            premium_potential: 0.15,
            cost_analysis: {
                seed_cost_per_acre: 145.00,
                additional_inputs: 25.00,
                total_investment: 170.00
            },
            planting_recommendations: [
                'Plant when soil temperature reaches 50°F',
                'Optimal planting depth: 1.5-2 inches'
            ],
            fertilizer_recommendations: [
                'Apply nitrogen in split applications',
                'Monitor soil phosphorus levels'
            ],
            pest_recommendations: [
                'Monitor for early season insects',
                'Scout regularly for disease symptoms'
            ]
        };

        const context = {
            location: {latitude: 41.8781, longitude: -87.6298},
            soil_data: {
                ph: parseFloat(document.getElementById('soilType')?.value === 'clay' ? 6.2 : 6.5) || 6.5,
                organic_matter: 3.2,
                texture: document.getElementById('soilType')?.value || 'loam'
            },
            climate_zone: '5b',
            region: 'Midwest',
            soil_type: document.getElementById('soilType')?.value || 'loam',
            regional_data_quality: 0.8
        };

        // Generate comprehensive explanation
        await window.explanationManager.generateComprehensiveExplanation(varietyData, context);
    }

    // Utility Methods
    showLoadingState() {
        const loadingState = document.getElementById('loadingState');
        const resultsSection = document.getElementById('resultsSection');
        
        if (loadingState) loadingState.style.display = 'block';
        if (resultsSection) resultsSection.style.display = 'none';
    }

    hideLoadingState() {
        const loadingState = document.getElementById('loadingState');
        if (loadingState) loadingState.style.display = 'none';
    }

    showResultsSection() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) resultsSection.style.display = 'block';
    }

    showFilterPanel() {
        const filterPanel = document.getElementById('filterPanel');
        if (filterPanel) filterPanel.style.display = 'block';
    }

    showAlert(message, type = 'info') {
        // Create and show Bootstrap alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    handleKeyboardNavigation(event) {
        if (event.key === 'Escape') {
            this.hideCropSuggestions();
        }
    }

    // Demo Data Methods (for development/testing)
    getDemoCrops(query = '') {
        const allCrops = [
            { id: 'corn', name: 'Corn', scientific_name: 'Zea mays', category: 'Grain' },
            { id: 'soybean', name: 'Soybean', scientific_name: 'Glycine max', category: 'Legume' },
            { id: 'wheat', name: 'Wheat', scientific_name: 'Triticum aestivum', category: 'Grain' },
            { id: 'cotton', name: 'Cotton', scientific_name: 'Gossypium hirsutum', category: 'Fiber' },
            { id: 'rice', name: 'Rice', scientific_name: 'Oryza sativa', category: 'Grain' }
        ];

        if (query) {
            return allCrops.filter(crop => 
                crop.name.toLowerCase().includes(query.toLowerCase()) ||
                crop.scientific_name.toLowerCase().includes(query.toLowerCase())
            );
        }

        return allCrops;
    }

    getDemoVarietyRecommendations() {
        return [
            {
                id: 'pioneer-1197',
                name: 'Pioneer P1197AM',
                company: 'Pioneer',
                description: 'High-yielding corn hybrid with excellent disease resistance and drought tolerance.',
                yield_potential: '185 bu/acre',
                maturity_days: 105,
                confidence: 0.92,
                suitability: 'Excellent',
                disease_resistance: 'high',
                traits: [
                    { name: 'Drought Tolerance', category: 'resistance' },
                    { name: 'High Yield', category: 'yield' },
                    { name: 'Premium Quality', category: 'quality' }
                ]
            },
            {
                id: 'asgrow-2834',
                name: 'Asgrow AG2834',
                company: 'Asgrow',
                description: 'Reliable soybean variety with strong yield potential and good disease package.',
                yield_potential: '58 bu/acre',
                maturity_days: 95,
                confidence: 0.88,
                suitability: 'Very Good',
                disease_resistance: 'medium',
                traits: [
                    { name: 'SDS Resistance', category: 'resistance' },
                    { name: 'High Protein', category: 'quality' },
                    { name: 'Good Standability', category: 'quality' }
                ]
            },
            {
                id: 'syngenta-monument',
                name: 'AgriPro SY Monument',
                company: 'Syngenta',
                description: 'Winter wheat variety with excellent winter hardiness and disease resistance.',
                yield_potential: '65 bu/acre',
                maturity_days: 280,
                confidence: 0.75,
                suitability: 'Good',
                disease_resistance: 'high',
                traits: [
                    { name: 'Winter Hardiness', category: 'resistance' },
                    { name: 'Fusarium Resistance', category: 'resistance' },
                    { name: 'Good Test Weight', category: 'quality' }
                ]
            }
        ];
    }

    getDemoExplanation() {
        return {
            summary: 'These varieties were selected based on your farm\'s soil conditions, climate zone, and your preferences for high yield potential with moderate risk tolerance.',
            regional_adaptation: 'All recommended varieties are well-adapted to your region\'s growing conditions, including temperature ranges and precipitation patterns.',
            performance_factors: 'Selection prioritized yield potential, disease resistance, and quality traits that align with your management intensity and market goals.',
            considerations: [
                'Monitor soil moisture levels during critical growth stages',
                'Implement integrated pest management practices',
                'Consider crop rotation to maintain soil health',
                'Plan for timely harvest to maximize quality'
            ]
        };
    }

    // Export functionality
    exportRecommendations() {
        const data = {
            farm_data: this.farmData,
            user_preferences: this.userPreferences,
            selected_crop: this.selectedCrop,
            recommendations: this.varietyRecommendations,
            selected_varieties: Array.from(this.selectedVarieties),
            export_date: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `variety-recommendations-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Chart initialization
    initializeCharts() {
        // Initialize any charts if needed
    }
}

// Global functions for HTML onclick handlers
function nextStep(stepNumber) {
    varietyManager.nextStep(stepNumber);
}

function prevStep(stepNumber) {
    varietyManager.prevStep(stepNumber);
}

function selectCrop(cropId, cropName) {
    varietyManager.selectCrop(cropId, cropName);
}

function selectCropFromSuggestion(cropId, cropName) {
    varietyManager.selectCropFromSuggestion(cropId, cropName);
}

function showAllCrops() {
    varietyManager.showAllCrops();
}

function getVarietyRecommendations() {
    varietyManager.getVarietyRecommendations();
}

function applyFilters() {
    varietyManager.applyFilters();
}

function clearFilters() {
    varietyManager.clearFilters();
}

function toggleVarietySelection(varietyId) {
    varietyManager.toggleVarietySelection(varietyId);
}

function toggleComparisonMode() {
    varietyManager.toggleComparisonMode();
}

function removeFromComparison(varietyId) {
    varietyManager.removeFromComparison(varietyId);
}

function viewVarietyDetails(varietyId) {
    // Navigate to variety detail page
    window.location.href = `/variety-detail/${varietyId}`;
}

function exportRecommendations() {
    varietyManager.exportRecommendations();
}

function goToComparison() {
    // Navigate to variety comparison page
    window.location.href = '/variety-comparison';
}

// Initialize the variety selection manager when the page loads
let varietyManager;
document.addEventListener('DOMContentLoaded', function() {
    varietyManager = new VarietySelectionManager();
});