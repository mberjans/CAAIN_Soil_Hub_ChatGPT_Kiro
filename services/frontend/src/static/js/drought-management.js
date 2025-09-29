// CAAIN Soil Hub - Drought Management JavaScript
// Comprehensive drought management system with API integration and interactive features

class DroughtManagementSystem {
    constructor() {
        this.apiBaseUrl = '/api/v1/drought';
        this.currentAssessment = null;
        this.currentStep = 1;
        this.totalSteps = 3;
        this.chartInstances = {};
        this.fieldMap = null;
        this.alertSettings = {
            threshold: 'moderate',
            emailAlerts: true,
            smsAlerts: false,
            pushAlerts: true
        };
        this.practices = [];
        this.selectedPractices = [];
        this.monitoringData = {};
        
        // Initialize the system
        this.init();
    }

    init() {
        this.bindEventListeners();
        this.loadInitialData();
        this.initializeCharts();
        this.setupLocationServices();
        this.loadFarmLocations();
        this.loadPractices();
        this.setupFieldMap();
    }

    bindEventListeners() {
        // Form submissions
        const assessmentForm = document.getElementById('droughtAssessmentForm');
        if (assessmentForm) {
            assessmentForm.addEventListener('submit', (e) => this.handleAssessmentSubmission(e));
        }

        const alertSettingsForm = document.getElementById('alertSettingsForm');
        if (alertSettingsForm) {
            alertSettingsForm.addEventListener('submit', (e) => this.handleAlertSettings(e));
        }

        // Tab switching
        const tabButtons = document.querySelectorAll('#droughtTabs button');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (e) => this.handleTabSwitch(e));
        });

        // Range slider updates
        const goalSlider = document.getElementById('waterConservationGoal');
        if (goalSlider) {
            goalSlider.addEventListener('input', (e) => {
                document.getElementById('goalValue').textContent = e.target.value + '%';
            });
        }

        // Real-time updates
        this.setupRealTimeUpdates();
    }

    // API Integration Methods
    async apiCall(endpoint, method = 'GET', data = null) {
        try {
            const config = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            };

            if (data && method !== 'GET') {
                config.body = JSON.stringify(data);
            }

            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            this.showErrorMessage(`API Error: ${error.message}`);
            throw error;
        }
    }

    // Assessment Wizard Functions
    nextStep() {
        if (this.validateCurrentStep()) {
            this.currentStep++;
            this.updateStepDisplay();
        }
    }

    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
        }
    }

    validateCurrentStep() {
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        
        for (let field of requiredFields) {
            if (!field.value.trim()) {
                this.showErrorMessage(`Please fill in all required fields in step ${this.currentStep}`);
                field.focus();
                return false;
            }
        }
        return true;
    }

    updateStepDisplay() {
        // Hide all steps
        for (let i = 1; i <= this.totalSteps; i++) {
            const stepElement = document.getElementById(`step${i}`);
            if (stepElement) {
                stepElement.style.display = 'none';
            }
        }

        // Show current step
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.style.display = 'block';
        }

        // Update navigation buttons
        const prevButton = document.getElementById('prevStep');
        const nextButton = document.getElementById('nextStep');
        const submitButton = document.getElementById('submitAssessment');

        if (prevButton) {
            prevButton.style.display = this.currentStep > 1 ? 'block' : 'none';
        }

        if (nextButton) {
            nextButton.style.display = this.currentStep < this.totalSteps ? 'block' : 'none';
        }

        if (submitButton) {
            submitButton.style.display = this.currentStep === this.totalSteps ? 'block' : 'none';
        }
    }

    async handleAssessmentSubmission(e) {
        e.preventDefault();
        
        if (!this.validateCurrentStep()) {
            return;
        }

        const formData = this.collectAssessmentData();
        
        try {
            this.showLoadingState('submitAssessment');
            
            const assessment = await this.apiCall('/assessment', 'POST', formData);
            this.currentAssessment = assessment;
            
            this.displayAssessmentResults(assessment);
            this.showSuccessMessage('Assessment completed successfully!');
            
            // Switch to dashboard tab to show results
            const dashboardTab = document.getElementById('dashboard-tab');
            if (dashboardTab) {
                dashboardTab.click();
            }
            
        } catch (error) {
            console.error('Assessment submission failed:', error);
            this.showErrorMessage('Failed to complete assessment. Please try again.');
        } finally {
            this.hideLoadingState('submitAssessment');
        }
    }

    collectAssessmentData() {
        return {
            farm_location_id: document.getElementById('farmLocation').value,
            assessment_type: document.getElementById('assessmentType').value,
            crop_type: document.getElementById('cropType').value,
            field_size_acres: parseFloat(document.getElementById('fieldSize').value),
            soil_moisture_level: document.getElementById('soilMoisture').value,
            irrigation_available: document.getElementById('irrigationAvailable').value,
            current_practices: Array.from(document.getElementById('currentPractices').selectedOptions).map(option => option.value),
            soil_type: document.getElementById('soilType').value,
            water_conservation_goal: parseInt(document.getElementById('waterConservationGoal').value),
            budget_constraint: document.getElementById('budgetConstraint').value,
            priority_areas: Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value)
        };
    }

    displayAssessmentResults(assessment) {
        // Update risk level
        const riskLevel = assessment.risk_assessment.risk_level;
        const riskElement = document.getElementById('currentRiskLevel');
        if (riskElement) {
            riskElement.textContent = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);
            riskElement.className = `badge ${this.getRiskBadgeClass(riskLevel)} fs-6`;
        }

        // Update risk meter
        this.updateRiskMeter(assessment.risk_assessment.risk_score);

        // Update water savings
        const totalSavings = assessment.water_savings_analysis.total_potential_savings;
        const savingsElement = document.getElementById('totalSavings');
        if (savingsElement) {
            savingsElement.textContent = totalSavings.toLocaleString();
        }

        // Display detailed results in preview
        this.updateAssessmentPreview(assessment);
    }

    updateRiskMeter(riskScore) {
        const indicator = document.getElementById('riskIndicator');
        if (indicator) {
            // Convert risk score (0-100) to percentage position
            const position = Math.min(Math.max(riskScore, 0), 100);
            indicator.style.left = `${position}%`;
        }
    }

    getRiskBadgeClass(riskLevel) {
        const classes = {
            'low': 'bg-success',
            'moderate': 'bg-warning',
            'high': 'bg-danger',
            'severe': 'bg-danger',
            'extreme': 'bg-dark'
        };
        return classes[riskLevel] || 'bg-secondary';
    }

    updateAssessmentPreview(assessment) {
        const previewElement = document.getElementById('assessmentPreview');
        if (previewElement) {
            previewElement.innerHTML = `
                <div class="mb-3">
                    <h6>Risk Assessment</h6>
                    <span class="badge ${this.getRiskBadgeClass(assessment.risk_assessment.risk_level)}">
                        ${assessment.risk_assessment.risk_level.toUpperCase()}
                    </span>
                    <p class="small text-muted mt-1">Score: ${assessment.risk_assessment.risk_score}/100</p>
                </div>
                <div class="mb-3">
                    <h6>Key Recommendations</h6>
                    <ul class="small">
                        ${assessment.recommendations.slice(0, 3).map(rec => `<li>${rec.practice_name}</li>`).join('')}
                    </ul>
                </div>
                <div class="mb-3">
                    <h6>Water Savings Potential</h6>
                    <p class="small text-success">
                        <strong>${assessment.water_savings_analysis.total_potential_savings.toLocaleString()} gallons/acre/year</strong>
                    </p>
                </div>
            `;
        }
    }

    // Practice Management Functions
    async loadPractices() {
        try {
            const practices = await this.apiCall('/practices');
            this.practices = practices;
            this.displayPractices();
        } catch (error) {
            console.error('Failed to load practices:', error);
            this.showErrorMessage('Failed to load conservation practices');
        }
    }

    displayPractices() {
        const practicesGrid = document.getElementById('practicesGrid');
        if (!practicesGrid) return;

        practicesGrid.innerHTML = this.practices.map(practice => `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="practice-card" data-practice-id="${practice.id}" onclick="droughtSystem.selectPractice('${practice.id}')">
                    <div class="practice-icon ${practice.icon_class}">
                        <i class="fas ${practice.icon}"></i>
                    </div>
                    <h6>${practice.name}</h6>
                    <p class="small text-muted">${practice.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-primary">${practice.water_savings_percent}% water savings</span>
                        <span class="small text-muted">$${practice.cost_per_acre}/acre</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    selectPractice(practiceId) {
        const practiceCard = document.querySelector(`[data-practice-id="${practiceId}"]`);
        const practice = this.practices.find(p => p.id === practiceId);
        
        if (!practice) return;

        if (this.selectedPractices.includes(practiceId)) {
            // Deselect practice
            this.selectedPractices = this.selectedPractices.filter(id => id !== practiceId);
            practiceCard.classList.remove('selected');
        } else {
            // Select practice
            this.selectedPractices.push(practiceId);
            practiceCard.classList.add('selected');
        }

        this.updatePracticeComparison();
    }

    updatePracticeComparison() {
        const comparisonElement = document.getElementById('practiceComparison');
        if (!comparisonElement) return;

        if (this.selectedPractices.length === 0) {
            comparisonElement.innerHTML = '<p class="text-muted">Select practices to compare their effectiveness</p>';
            return;
        }

        const selectedPracticeData = this.selectedPractices.map(id => 
            this.practices.find(p => p.id === id)
        );

        comparisonElement.innerHTML = `
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Practice</th>
                            <th>Water Savings</th>
                            <th>Cost/Acre</th>
                            <th>Implementation Time</th>
                            <th>Effectiveness</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${selectedPracticeData.map(practice => `
                            <tr>
                                <td>${practice.name}</td>
                                <td>${practice.water_savings_percent}%</td>
                                <td>$${practice.cost_per_acre}</td>
                                <td>${practice.implementation_time}</td>
                                <td>
                                    <div class="progress" style="height: 20px;">
                                        <div class="progress-bar" style="width: ${practice.effectiveness_score}%">
                                            ${practice.effectiveness_score}%
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    // Monitoring Functions
    async loadMonitoringData() {
        try {
            const monitoringData = await this.apiCall('/monitoring');
            this.monitoringData = monitoringData;
            this.updateMonitoringCharts();
        } catch (error) {
            console.error('Failed to load monitoring data:', error);
        }
    }

    updateMonitoringCharts() {
        this.updateMoistureChart();
        this.updatePrecipitationChart();
        this.updateTemperatureChart();
        this.updateDroughtIndexChart();
    }

    updateMoistureChart() {
        const ctx = document.getElementById('moistureChart');
        if (!ctx || !this.monitoringData.soil_moisture) return;

        if (this.chartInstances.moistureChart) {
            this.chartInstances.moistureChart.destroy();
        }

        this.chartInstances.moistureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.monitoringData.soil_moisture.dates,
                datasets: [{
                    label: 'Soil Moisture (%)',
                    data: this.monitoringData.soil_moisture.values,
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Soil Moisture Trends'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    updatePrecipitationChart() {
        const ctx = document.getElementById('precipitationChart');
        if (!ctx || !this.monitoringData.precipitation) return;

        if (this.chartInstances.precipitationChart) {
            this.chartInstances.precipitationChart.destroy();
        }

        this.chartInstances.precipitationChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.monitoringData.precipitation.dates,
                datasets: [{
                    label: 'Precipitation (inches)',
                    data: this.monitoringData.precipitation.values,
                    backgroundColor: '#17a2b8',
                    borderColor: '#17a2b8',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Precipitation History'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateTemperatureChart() {
        const ctx = document.getElementById('temperatureChart');
        if (!ctx || !this.monitoringData.temperature) return;

        if (this.chartInstances.temperatureChart) {
            this.chartInstances.temperatureChart.destroy();
        }

        this.chartInstances.temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.monitoringData.temperature.dates,
                datasets: [{
                    label: 'Average Temperature (°F)',
                    data: this.monitoringData.temperature.values,
                    borderColor: '#fd7e14',
                    backgroundColor: 'rgba(253, 126, 20, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Temperature Trends'
                    }
                }
            }
        });
    }

    updateDroughtIndexChart() {
        const ctx = document.getElementById('droughtIndexChart');
        if (!ctx || !this.monitoringData.drought_index) return;

        if (this.chartInstances.droughtIndexChart) {
            this.chartInstances.droughtIndexChart.destroy();
        }

        this.chartInstances.droughtIndexChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.monitoringData.drought_index.dates,
                datasets: [{
                    label: 'Drought Index',
                    data: this.monitoringData.drought_index.values,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Drought Index Trends'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10
                    }
                }
            }
        });
    }

    // Field Map Functions
    setupFieldMap() {
        const mapContainer = document.getElementById('fieldMap');
        if (!mapContainer) return;

        this.fieldMap = L.map('fieldMap').setView([40.0, -95.0], 6);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.fieldMap);

        // Add field markers (this would be populated with real field data)
        this.addFieldMarkers();
    }

    addFieldMarkers() {
        // Example field markers - in production, this would come from API
        const fields = [
            { id: 1, name: 'Field A', lat: 40.0, lng: -95.0, moisture: 65, risk: 'moderate' },
            { id: 2, name: 'Field B', lat: 40.1, lng: -95.1, moisture: 45, risk: 'high' },
            { id: 3, name: 'Field C', lat: 39.9, lng: -94.9, moisture: 80, risk: 'low' }
        ];

        fields.forEach(field => {
            const marker = L.marker([field.lat, field.lng]).addTo(this.fieldMap);
            marker.bindPopup(`
                <strong>${field.name}</strong><br>
                Soil Moisture: ${field.moisture}%<br>
                Risk Level: <span class="badge ${this.getRiskBadgeClass(field.risk)}">${field.risk}</span>
            `);
        });
    }

    // Alert Management Functions
    async handleAlertSettings(e) {
        e.preventDefault();
        
        const settings = {
            threshold: document.getElementById('alertThreshold').value,
            email_alerts: document.getElementById('emailAlerts').checked,
            sms_alerts: document.getElementById('smsAlerts').checked,
            push_alerts: document.getElementById('pushAlerts').checked
        };

        try {
            await this.apiCall('/alerts/subscribe', 'POST', settings);
            this.alertSettings = settings;
            this.showSuccessMessage('Alert settings saved successfully!');
        } catch (error) {
            console.error('Failed to save alert settings:', error);
            this.showErrorMessage('Failed to save alert settings');
        }
    }

    // Planning Functions
    generateImplementationTimeline() {
        const timelineElement = document.getElementById('implementationTimeline');
        if (!timelineElement) return;

        const timeline = [
            { phase: 'Phase 1', duration: '1-2 weeks', tasks: ['Soil testing', 'Equipment preparation'] },
            { phase: 'Phase 2', duration: '2-4 weeks', tasks: ['Practice implementation', 'Initial monitoring'] },
            { phase: 'Phase 3', duration: 'Ongoing', tasks: ['Monitoring', 'Adjustments', 'Evaluation'] }
        ];

        timelineElement.innerHTML = timeline.map(phase => `
            <div class="card mb-2">
                <div class="card-body">
                    <h6>${phase.phase}</h6>
                    <p class="small text-muted mb-1">Duration: ${phase.duration}</p>
                    <ul class="small mb-0">
                        ${phase.tasks.map(task => `<li>${task}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `).join('');
    }

    generateCostBenefitAnalysis() {
        const analysisElement = document.getElementById('costBenefitAnalysis');
        if (!analysisElement) return;

        const analysis = {
            total_cost: 2500,
            annual_savings: 1800,
            payback_period: 1.4,
            roi_percentage: 72
        };

        analysisElement.innerHTML = `
            <div class="row text-center">
                <div class="col-6">
                    <div class="card">
                        <div class="card-body">
                            <h6>Total Cost</h6>
                            <span class="text-danger">$${analysis.total_cost}</span>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="card">
                        <div class="card-body">
                            <h6>Annual Savings</h6>
                            <span class="text-success">$${analysis.annual_savings}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row text-center mt-2">
                <div class="col-6">
                    <div class="card">
                        <div class="card-body">
                            <h6>Payback Period</h6>
                            <span class="text-info">${analysis.payback_period} years</span>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="card">
                        <div class="card-body">
                            <h6>ROI</h6>
                            <span class="text-success">${analysis.roi_percentage}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    generateActionItems() {
        const actionItemsElement = document.getElementById('actionItems');
        if (!actionItemsElement) return;

        const actionItems = [
            { task: 'Schedule soil moisture testing', priority: 'high', due: 'This week' },
            { task: 'Order cover crop seeds', priority: 'medium', due: 'Next week' },
            { task: 'Install soil moisture sensors', priority: 'high', due: 'This month' },
            { task: 'Review irrigation system efficiency', priority: 'medium', due: 'Next month' }
        ];

        actionItemsElement.innerHTML = actionItems.map(item => `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <span class="badge ${item.priority === 'high' ? 'bg-danger' : 'bg-warning'} me-2">${item.priority}</span>
                    ${item.task}
                </div>
                <small class="text-muted">${item.due}</small>
            </div>
        `).join('');
    }

    // Utility Functions
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadFarmLocations(),
                this.loadPractices(),
                this.loadMonitoringData()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    async loadFarmLocations() {
        try {
            const locations = await this.apiCall('/locations');
            const locationSelect = document.getElementById('farmLocation');
            if (locationSelect) {
                locationSelect.innerHTML = '<option value="">Select Farm Location</option>' +
                    locations.map(loc => `<option value="${loc.id}">${loc.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Failed to load farm locations:', error);
        }
    }

    initializeCharts() {
        // Charts will be initialized when monitoring data is loaded
    }

    setupLocationServices() {
        // Setup GPS and location services if available
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log('Current location:', position.coords);
                },
                (error) => {
                    console.log('Location access denied:', error);
                }
            );
        }
    }

    setupRealTimeUpdates() {
        // Setup real-time updates for monitoring data
        setInterval(() => {
            this.loadMonitoringData();
        }, 300000); // Update every 5 minutes
    }

    handleTabSwitch(e) {
        const tabId = e.target.getAttribute('data-bs-target');
        
        switch (tabId) {
            case '#monitoring':
                this.loadMonitoringData();
                break;
            case '#planning':
                this.generateImplementationTimeline();
                this.generateCostBenefitAnalysis();
                this.generateActionItems();
                break;
        }
    }

    // Quick Action Functions
    async runQuickAssessment() {
        try {
            this.showLoadingState('quickAssessment');
            const assessment = await this.apiCall('/assess', 'POST', {
                farm_location_id: document.getElementById('farmLocation').value || 'default',
                assessment_type: 'quick'
            });
            this.displayAssessmentResults(assessment);
            this.showSuccessMessage('Quick assessment completed!');
        } catch (error) {
            console.error('Quick assessment failed:', error);
            this.showErrorMessage('Quick assessment failed');
        } finally {
            this.hideLoadingState('quickAssessment');
        }
    }

    viewRecommendations() {
        const practicesTab = document.getElementById('practices-tab');
        if (practicesTab) {
            practicesTab.click();
        }
    }

    setupMonitoring() {
        const monitoringTab = document.getElementById('monitoring-tab');
        if (monitoringTab) {
            monitoringTab.click();
        }
    }

    // Export Functions
    async exportReport(format) {
        try {
            const reportData = {
                assessment: this.currentAssessment,
                practices: this.selectedPractices,
                monitoring_data: this.monitoringData,
                format: format
            };

            const response = await this.apiCall('/export-report', 'POST', reportData);
            
            // Create download link
            const blob = new Blob([response.data], { type: response.content_type });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `drought-management-report.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            this.showSuccessMessage(`Report exported as ${format.toUpperCase()}`);
        } catch (error) {
            console.error('Export failed:', error);
            this.showErrorMessage('Failed to export report');
        }
    }

    // UI Helper Functions
    showLoadingState(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.classList.add('btn-loading');
            button.disabled = true;
        }
    }

    hideLoadingState(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'danger');
    }

    showMessage(message, type) {
        // Create toast notification
        const toastContainer = document.getElementById('toastContainer') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
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
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Global instance for easy access
    window.droughtSystem = new DroughtManagementSystem();
});