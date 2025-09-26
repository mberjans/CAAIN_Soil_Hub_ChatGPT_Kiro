// CAAIN Soil Hub - pH Management JavaScript
// Comprehensive pH management system with API integration and interactive features

class PHManagementSystem {
    constructor() {
        this.apiBaseUrl = '/api/v1/ph';
        this.currentPhData = {};
        this.chartInstances = {};
        this.alertSettings = {
            criticalLow: 5.0,
            criticalHigh: 8.0,
            emailAlerts: true,
            smsAlerts: false,
            pushAlerts: true
        };
        this.fieldData = [];
        this.monitoringSchedule = [];
        this.historyData = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        
        // Initialize the system
        this.init();
    }

    init() {
        this.bindEventListeners();
        this.loadInitialData();
        this.initializeCharts();
        this.setupLocationServices();
        this.loadAlertSettings();
    }

    bindEventListeners() {
        // Form submissions
        const phAnalysisForm = document.getElementById('phAnalysisForm');
        if (phAnalysisForm) {
            phAnalysisForm.addEventListener('submit', (e) => this.handlePhAnalysis(e));
        }

        const limeCalculatorForm = document.getElementById('limeCalculatorForm');
        if (limeCalculatorForm) {
            limeCalculatorForm.addEventListener('submit', (e) => this.handleLimeCalculation(e));
        }

        const alertConfigForm = document.getElementById('alertConfigForm');
        if (alertConfigForm) {
            alertConfigForm.addEventListener('submit', (e) => this.handleAlertConfig(e));
        }

        const monitoringSetupForm = document.getElementById('monitoringSetupForm');
        if (monitoringSetupForm) {
            monitoringSetupForm.addEventListener('submit', (e) => this.handleMonitoringSetup(e));
        }

        const recordTestForm = document.getElementById('recordTestForm');
        if (recordTestForm) {
            recordTestForm.addEventListener('submit', (e) => this.handleRecordTest(e));
        }

        // Tab switching
        const tabButtons = document.querySelectorAll('#phTabs button');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (e) => this.handleTabSwitch(e));
        });

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

    // pH Analysis Functions
    async handlePhAnalysis(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const analysisData = {
            farm_id: formData.get('farmId'),
            field_id: formData.get('fieldId'),
            crop_type: formData.get('cropType'),
            ph_value: parseFloat(formData.get('phValue')),
            organic_matter: parseFloat(formData.get('organicMatter')),
            phosphorus: parseInt(formData.get('phosphorus')),
            potassium: parseInt(formData.get('potassium'))
        };

        try {
            this.showLoadingState(event.target);
            const results = await this.apiCall('/analyze', 'POST', analysisData);
            this.displayAnalysisResults(results);
            this.updateCropRequirements(analysisData.crop_type);
        } catch (error) {
            this.showErrorMessage('Failed to analyze pH data. Please try again.');
        } finally {
            this.hideLoadingState(event.target);
        }
    }

    displayAnalysisResults(results) {
        const analysisResults = document.getElementById('analysisResults');
        const analysisContent = document.getElementById('analysisContent');
        
        if (!analysisResults || !analysisContent) return;

        const statusClass = this.getPhStatusClass(results.ph_status);
        const recommendations = results.recommendations || [];
        
        analysisContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="field-card ${statusClass}">
                        <h6><i class="fas fa-vial"></i> pH Analysis Summary</h6>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>pH Level:</span>
                            <strong>${results.ph_value}</strong>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>Status:</span>
                            <span class="status-badge status-${statusClass}">${results.ph_status}</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>Crop Suitability:</span>
                            <strong>${results.crop_suitability_score || 'N/A'}/10</strong>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <span>Nutrient Availability:</span>
                            <strong>${results.nutrient_availability || 'Good'}</strong>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="monitoring-widget">
                        <h6><i class="fas fa-lightbulb"></i> Recommendations</h6>
                        <ul class="list-unstyled">
                            ${recommendations.map(rec => `
                                <li class="mb-2">
                                    <i class="fas fa-check-circle text-success"></i>
                                    ${rec}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            </div>
            
            ${results.nutrient_analysis ? `
            <div class="row mt-3">
                <div class="col-12">
                    <div class="economics-table">
                        <table class="table mb-0">
                            <thead>
                                <tr>
                                    <th>Nutrient</th>
                                    <th>Current Level</th>
                                    <th>Optimal Range</th>
                                    <th>Status</th>
                                    <th>Impact</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${this.generateNutrientTable(results.nutrient_analysis)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            ` : ''}
        `;
        
        analysisResults.style.display = 'block';
    }

    generateNutrientTable(nutrientAnalysis) {
        const nutrients = ['phosphorus', 'potassium', 'nitrogen', 'calcium', 'magnesium'];
        
        return nutrients.map(nutrient => {
            const data = nutrientAnalysis[nutrient];
            if (!data) return '';
            
            return `
                <tr>
                    <td class="text-capitalize">${nutrient}</td>
                    <td>${data.current_level}</td>
                    <td>${data.optimal_range}</td>
                    <td>
                        <span class="status-badge status-${data.status.toLowerCase()}">
                            ${data.status}
                        </span>
                    </td>
                    <td class="small">${data.impact}</td>
                </tr>
            `;
        }).join('');
    }

    // Lime Calculator Functions
    async handleLimeCalculation(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const calculationData = {
            current_ph: parseFloat(formData.get('currentPh')),
            target_ph: parseFloat(formData.get('targetPh')),
            buffer_ph: parseFloat(formData.get('bufferPh')) || null,
            soil_texture: formData.get('soilTexture'),
            organic_matter: parseFloat(formData.get('organicMatterCalc')),
            field_size: parseFloat(formData.get('fieldSize'))
        };

        try {
            this.showLoadingState(event.target);
            const results = await this.apiCall('/calculate-lime', 'POST', calculationData);
            this.displayLimeRecommendations(results);
            this.displayEconomicAnalysis(results.economic_analysis);
        } catch (error) {
            this.showErrorMessage('Failed to calculate lime requirements. Please try again.');
        } finally {
            this.hideLoadingState(event.target);
        }
    }

    displayLimeRecommendations(results) {
        const limeRecommendations = document.getElementById('limeRecommendations');
        const limeRecommendationsList = document.getElementById('limeRecommendationsList');
        
        if (!limeRecommendations || !limeRecommendationsList) return;

        const recommendations = results.lime_recommendations || [];
        
        limeRecommendationsList.innerHTML = recommendations.map((rec, index) => `
            <div class="lime-recommendation ${index === 0 ? 'recommended' : 'alternative'}">
                ${index === 0 ? '<div class="recommendation-badge">Recommended</div>' : ''}
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 class="mb-1">${rec.lime_type}</h6>
                        <p class="text-muted small mb-0">${rec.description}</p>
                    </div>
                    <div class="text-end">
                        <div class="h4 text-success mb-0">${rec.rate_per_acre} tons/acre</div>
                        <small class="text-muted">Total: ${rec.total_tons} tons</small>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-4">
                        <div class="text-center">
                            <div class="h6 text-primary">${rec.cost_per_acre}</div>
                            <small class="text-muted">Cost per acre</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <div class="h6 text-info">${rec.application_method}</div>
                            <small class="text-muted">Application</small>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="text-center">
                            <div class="h6 text-warning">${rec.effectiveness_months} months</div>
                            <small class="text-muted">Effectiveness</small>
                        </div>
                    </div>
                </div>
                
                ${rec.notes ? `
                <div class="mt-2 p-2 bg-light rounded">
                    <small><i class="fas fa-info-circle"></i> ${rec.notes}</small>
                </div>
                ` : ''}
            </div>
        `).join('');
        
        limeRecommendations.style.display = 'block';
    }

    displayEconomicAnalysis(economicData) {
        const economicAnalysis = document.getElementById('economicAnalysis');
        const economicsTableBody = document.getElementById('economicsTableBody');
        
        if (!economicAnalysis || !economicsTableBody || !economicData) return;

        const agricultural = economicData.agricultural_lime || {};
        const hydrated = economicData.hydrated_lime || {};
        
        economicsTableBody.innerHTML = `
            <tr>
                <td><strong>Material Cost</strong></td>
                <td>${AgriculturalUtils.formatCurrency(agricultural.material_cost || 0)}</td>
                <td>${AgriculturalUtils.formatCurrency(hydrated.material_cost || 0)}</td>
            </tr>
            <tr>
                <td><strong>Application Cost</strong></td>
                <td>${AgriculturalUtils.formatCurrency(agricultural.application_cost || 0)}</td>
                <td>${AgriculturalUtils.formatCurrency(hydrated.application_cost || 0)}</td>
            </tr>
            <tr>
                <td><strong>Total Cost</strong></td>
                <td><strong>${AgriculturalUtils.formatCurrency(agricultural.total_cost || 0)}</strong></td>
                <td><strong>${AgriculturalUtils.formatCurrency(hydrated.total_cost || 0)}</strong></td>
            </tr>
            <tr>
                <td><strong>Expected Yield Increase</strong></td>
                <td>${agricultural.yield_increase || 0}%</td>
                <td>${hydrated.yield_increase || 0}%</td>
            </tr>
            <tr>
                <td><strong>ROI (3 years)</strong></td>
                <td class="${agricultural.roi > 0 ? 'roi-positive' : 'roi-negative'}">
                    ${AgriculturalUtils.formatPercentage(agricultural.roi || 0, 1)}
                </td>
                <td class="${hydrated.roi > 0 ? 'roi-positive' : 'roi-negative'}">
                    ${AgriculturalUtils.formatPercentage(hydrated.roi || 0, 1)}
                </td>
            </tr>
        `;
        
        economicAnalysis.style.display = 'block';
    }

    // Data Loading and Management
    async loadInitialData() {
        try {
            await Promise.all([
                this.loadDashboardData(),
                this.loadFieldData(),
                this.loadMonitoringSchedule(),
                this.loadHistoryData()
            ]);
            this.updateLastUpdated();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showErrorMessage('Failed to load some dashboard data. Please refresh the page.');
        }
    }

    async loadDashboardData() {
        try {
            const dashboardData = await this.apiCall('/dashboard');
            this.updateDashboardStats(dashboardData);
            this.updatePhMeter(dashboardData.average_ph);
            this.loadRecentAlerts(dashboardData.recent_alerts);
        } catch (error) {
            console.error('Dashboard data load failed:', error);
        }
    }

    updateDashboardStats(data) {
        const stats = {
            totalFields: data.total_fields || 0,
            averagePh: data.average_ph || 0,
            fieldsNeedingAction: data.fields_needing_action || 0,
            activeAlerts: data.active_alerts || 0
        };

        Object.entries(stats).forEach(([key, value]) => {
            const element = document.getElementById(key);
            if (element) {
                if (key === 'averagePh') {
                    element.textContent = value.toFixed(1);
                } else {
                    element.textContent = value;
                }
            }
        });
    }

    updatePhMeter(phValue) {
        const indicator = document.getElementById('phIndicator');
        const currentPhValueElement = document.getElementById('currentPhValue');
        
        if (indicator && phValue) {
            // Calculate position (pH scale from 3.0 to 10.0)
            const position = ((phValue - 3.0) / 7.0) * 100;
            indicator.style.left = `${Math.max(0, Math.min(100, position))}%`;
        }
        
        if (currentPhValueElement) {
            currentPhValueElement.textContent = phValue ? phValue.toFixed(1) : '--';
        }
    }

    async loadFieldData() {
        try {
            const fieldsData = await this.apiCall('/fields');
            this.fieldData = fieldsData.fields || [];
            this.renderFieldCards();
        } catch (error) {
            console.error('Field data load failed:', error);
        }
    }

    renderFieldCards() {
        const container = document.getElementById('fieldStatusCards');
        if (!container) return;

        container.innerHTML = this.fieldData.map(field => `
            <div class="col-lg-4 col-md-6">
                <div class="field-card ${this.getPhStatusClass(field.ph_status)}" 
                     onclick="showFieldDetails('${field.field_id}')">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h6 class="mb-1">${field.field_name}</h6>
                            <small class="text-muted">${field.field_id}</small>
                        </div>
                        <span class="status-badge status-${this.getPhStatusClass(field.ph_status)}">
                            ${field.ph_status}
                        </span>
                    </div>
                    
                    <div class="row">
                        <div class="col-6">
                            <div class="mb-2">
                                <strong class="h5">${field.current_ph}</strong>
                                <small class="text-muted d-block">Current pH</small>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="mb-2">
                                <strong class="h6">${field.acres} acres</strong>
                                <small class="text-muted d-block">Field Size</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-6">
                            <small class="text-muted">Last Test:</small>
                            <div class="small">${this.formatDate(field.last_test_date)}</div>
                        </div>
                        <div class="col-6">
                            <small class="text-muted">Crop:</small>
                            <div class="small text-capitalize">${field.current_crop || 'Not set'}</div>
                        </div>
                    </div>
                    
                    ${field.lime_recommendation ? `
                    <div class="mt-2 p-2 bg-light rounded">
                        <small><i class="fas fa-leaf"></i> ${field.lime_recommendation}</small>
                    </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    // Monitoring and Alerts
    async handleMonitoringSetup(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const monitoringData = {
            field_id: formData.get('monitoringFieldId'),
            frequency: formData.get('monitoringFrequency'),
            alert_thresholds: {
                low_ph: this.alertSettings.criticalLow,
                high_ph: this.alertSettings.criticalHigh
            }
        };

        try {
            this.showLoadingState(event.target);
            await this.apiCall('/monitoring/setup', 'POST', monitoringData);
            this.showSuccessMessage('Monitoring setup successfully!');
            event.target.reset();
            this.loadMonitoringSchedule();
        } catch (error) {
            this.showErrorMessage('Failed to setup monitoring. Please try again.');
        } finally {
            this.hideLoadingState(event.target);
        }
    }

    async loadMonitoringSchedule() {
        try {
            const scheduleData = await this.apiCall('/monitoring/schedule');
            this.monitoringSchedule = scheduleData.schedule || [];
            this.renderMonitoringSchedule();
        } catch (error) {
            console.error('Monitoring schedule load failed:', error);
        }
    }

    renderMonitoringSchedule() {
        const tableBody = document.getElementById('monitoringScheduleTable');
        if (!tableBody) return;

        tableBody.innerHTML = this.monitoringSchedule.map(item => `
            <tr>
                <td>
                    <strong>${item.field_name}</strong>
                    <br><small class="text-muted">${item.field_id}</small>
                </td>
                <td>
                    <span class="badge bg-info">${item.test_type}</span>
                </td>
                <td>${this.formatDate(item.due_date)}</td>
                <td>
                    <span class="badge bg-${this.getStatusBadgeColor(item.status)}">
                        ${item.status}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary" onclick="completeTest('${item.id}')">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-outline-secondary" onclick="rescheduleTest('${item.id}')">
                            <i class="fas fa-calendar-alt"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Alert Configuration
    async handleAlertConfig(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        this.alertSettings = {
            criticalLow: parseFloat(formData.get('criticalLowPh')),
            criticalHigh: parseFloat(formData.get('criticalHighPh')),
            emailAlerts: formData.get('emailAlerts') === 'on',
            smsAlerts: formData.get('smsAlerts') === 'on',
            pushAlerts: formData.get('pushAlerts') === 'on'
        };

        try {
            await this.apiCall('/alerts/config', 'POST', this.alertSettings);
            this.showSuccessMessage('Alert settings saved successfully!');
            this.saveAlertSettings();
        } catch (error) {
            this.showErrorMessage('Failed to save alert settings. Please try again.');
        }
    }

    loadRecentAlerts(alerts) {
        const container = document.getElementById('recentAlerts');
        if (!container || !alerts) return;

        if (alerts.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No recent alerts</p>';
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="d-flex align-items-center p-2 border-bottom">
                <div class="me-3">
                    <i class="fas fa-${this.getAlertIcon(alert.type)} text-${this.getAlertColor(alert.severity)}"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="fw-bold">${alert.field_name}</div>
                    <small class="text-muted">${alert.message}</small>
                </div>
                <div class="text-end">
                    <small class="text-muted">${this.formatDate(alert.timestamp)}</small>
                </div>
            </div>
        `).join('');
    }

    // History Management
    async loadHistoryData() {
        try {
            const historyData = await this.apiCall(`/historical/all?page=${this.currentPage}&limit=${this.itemsPerPage}`);
            this.historyData = historyData.records || [];
            this.renderHistoryTable();
            this.renderHistoryPagination(historyData.total_pages, historyData.current_page);
            this.renderHistorySummary(historyData.summary);
        } catch (error) {
            console.error('History data load failed:', error);
        }
    }

    renderHistoryTable() {
        const tableBody = document.getElementById('historyTable');
        if (!tableBody) return;

        tableBody.innerHTML = this.historyData.map(record => `
            <tr>
                <td>${this.formatDate(record.test_date)}</td>
                <td>
                    <strong>${record.field_name}</strong>
                    <br><small class="text-muted">${record.field_id}</small>
                </td>
                <td>
                    <strong class="text-${this.getPhColor(record.ph_value)}">
                        ${record.ph_value}
                    </strong>
                </td>
                <td>${record.buffer_ph || '--'}</td>
                <td>
                    <span class="badge bg-secondary">${record.test_method}</span>
                </td>
                <td>
                    <span class="status-badge status-${this.getPhStatusClass(record.ph_status)}">
                        ${record.ph_status}
                    </span>
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-info" onclick="viewTestDetails('${record.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-primary" onclick="downloadTestReport('${record.id}')">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Chart Initialization and Management
    initializeCharts() {
        this.initializeTrendChart();
        this.initializeHistoryPieChart();
    }

    initializeTrendChart() {
        const canvas = document.getElementById('phTrendChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.chartInstances.trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'pH Level',
                    data: [],
                    borderColor: 'rgb(40, 167, 69)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.1,
                    fill: true
                }, {
                    label: 'Optimal Range Min',
                    data: [],
                    borderColor: 'rgba(255, 193, 7, 0.5)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                }, {
                    label: 'Optimal Range Max',
                    data: [],
                    borderColor: 'rgba(255, 193, 7, 0.5)',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: '-1',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'pH Trends Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 3,
                        max: 10,
                        title: {
                            display: true,
                            text: 'pH Value'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });
    }

    initializeHistoryPieChart() {
        const canvas = document.getElementById('historyPieChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.chartInstances.historyPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Optimal', 'Acidic', 'Alkaline', 'Critical'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    async updateTrendChart(fieldId = 'all') {
        try {
            const trendData = await this.apiCall(`/trends/${fieldId}`);
            const chart = this.chartInstances.trendChart;
            
            if (chart && trendData) {
                chart.data.labels = trendData.dates;
                chart.data.datasets[0].data = trendData.ph_values;
                chart.data.datasets[1].data = new Array(trendData.dates.length).fill(6.0);
                chart.data.datasets[2].data = new Array(trendData.dates.length).fill(7.0);
                chart.update();
            }
        } catch (error) {
            console.error('Failed to update trend chart:', error);
        }
    }

    // Record pH Test
    async handleRecordTest(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const testData = {
            farm_id: formData.get('testFarmId'),
            field_id: formData.get('testFieldId'),
            ph_value: parseFloat(formData.get('testPhValue')),
            buffer_ph: parseFloat(formData.get('testBufferPh')) || null,
            test_method: formData.get('testMethod'),
            lab_name: formData.get('testLabName') || null,
            notes: formData.get('testNotes') || null,
            test_date: new Date().toISOString(),
            location: await this.getCurrentLocation()
        };

        try {
            this.showLoadingState(event.target);
            await this.apiCall('/record', 'POST', testData);
            this.showSuccessMessage('pH test recorded successfully!');
            
            // Close modal and refresh data
            const modal = bootstrap.Modal.getInstance(document.getElementById('recordTestModal'));
            if (modal) modal.hide();
            
            event.target.reset();
            this.loadInitialData();
        } catch (error) {
            this.showErrorMessage('Failed to record pH test. Please try again.');
        } finally {
            this.hideLoadingState(event.target);
        }
    }

    // Utility Functions
    getPhStatusClass(status) {
        const statusMap = {
            'optimal': 'optimal',
            'good': 'optimal',
            'acidic': 'warning',
            'very_acidic': 'critical',
            'alkaline': 'alkaline',
            'very_alkaline': 'critical',
            'critical': 'critical'
        };
        return statusMap[status] || 'warning';
    }

    getPhColor(phValue) {
        if (phValue >= 6.0 && phValue <= 7.0) return 'success';
        if (phValue >= 5.5 && phValue <= 7.5) return 'warning';
        return 'danger';
    }

    getStatusBadgeColor(status) {
        const colorMap = {
            'pending': 'warning',
            'completed': 'success',
            'overdue': 'danger',
            'scheduled': 'info'
        };
        return colorMap[status] || 'secondary';
    }

    getAlertIcon(type) {
        const iconMap = {
            'ph_critical': 'exclamation-triangle',
            'monitoring_due': 'calendar-check',
            'lime_needed': 'leaf',
            'system': 'cog'
        };
        return iconMap[type] || 'bell';
    }

    getAlertColor(severity) {
        const colorMap = {
            'high': 'danger',
            'medium': 'warning',
            'low': 'info'
        };
        return colorMap[severity] || 'secondary';
    }

    formatDate(dateString) {
        if (!dateString) return '--';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // Location Services
    setupLocationServices() {
        if ('geolocation' in navigator) {
            this.locationAvailable = true;
        }
    }

    async getCurrentLocation() {
        if (!this.locationAvailable) return null;
        
        return new Promise((resolve) => {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                () => resolve(null),
                { timeout: 5000, enableHighAccuracy: true }
            );
        });
    }

    // Local Storage Management
    saveAlertSettings() {
        localStorage.setItem('phAlertSettings', JSON.stringify(this.alertSettings));
    }

    loadAlertSettings() {
        const saved = localStorage.getItem('phAlertSettings');
        if (saved) {
            this.alertSettings = { ...this.alertSettings, ...JSON.parse(saved) };
            this.updateAlertSettingsUI();
        }
    }

    updateAlertSettingsUI() {
        const criticalLowSlider = document.getElementById('criticalLowPh');
        const criticalHighSlider = document.getElementById('criticalHighPh');
        const emailCheckbox = document.getElementById('emailAlerts');
        const smsCheckbox = document.getElementById('smsAlerts');
        const pushCheckbox = document.getElementById('pushAlerts');

        if (criticalLowSlider) {
            criticalLowSlider.value = this.alertSettings.criticalLow;
            this.updateThresholdValue('criticalLowValue', this.alertSettings.criticalLow);
        }
        
        if (criticalHighSlider) {
            criticalHighSlider.value = this.alertSettings.criticalHigh;
            this.updateThresholdValue('criticalHighValue', this.alertSettings.criticalHigh);
        }
        
        if (emailCheckbox) emailCheckbox.checked = this.alertSettings.emailAlerts;
        if (smsCheckbox) smsCheckbox.checked = this.alertSettings.smsAlerts;
        if (pushCheckbox) pushCheckbox.checked = this.alertSettings.pushAlerts;
    }

    updateThresholdValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = parseFloat(value).toFixed(1);
        }
    }

    // UI State Management
    showLoadingState(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        }
    }

    hideLoadingState(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = false;
            const originalText = submitButton.dataset.originalText || 'Submit';
            submitButton.innerHTML = originalText;
        }
    }

    showSuccessMessage(message) {
        AgriculturalUtils.displayAlert(message, 'success');
    }

    showErrorMessage(message) {
        AgriculturalUtils.displayAlert(message, 'danger');
    }

    updateLastUpdated() {
        const element = document.getElementById('lastUpdated');
        if (element) {
            element.textContent = new Date().toLocaleTimeString();
        }
    }

    // Tab Management
    handleTabSwitch(event) {
        const tabId = event.target.getAttribute('data-bs-target');
        
        switch (tabId) {
            case '#monitoring':
                this.updateTrendChart();
                break;
            case '#history':
                this.loadHistoryData();
                break;
        }
    }

    // Real-time Updates
    setupRealTimeUpdates() {
        // Update dashboard every 5 minutes
        setInterval(() => {
            this.loadDashboardData();
        }, 300000);
        
        // Update last updated timestamp every minute
        setInterval(() => {
            this.updateLastUpdated();
        }, 60000);
    }

    // Export Functions
    async exportToCSV() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/export/csv`, {
                method: 'GET',
                headers: { 'Accept': 'text/csv' }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'ph-history.csv', 'text/csv');
            }
        } catch (error) {
            this.showErrorMessage('Failed to export CSV. Please try again.');
        }
    }

    async exportToPDF() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/export/pdf`, {
                method: 'GET',
                headers: { 'Accept': 'application/pdf' }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'ph-report.pdf', 'application/pdf');
            }
        } catch (error) {
            this.showErrorMessage('Failed to export PDF. Please try again.');
        }
    }

    async exportToExcel() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/export/excel`, {
                method: 'GET',
                headers: { 'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                this.downloadFile(blob, 'ph-data.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
            }
        } catch (error) {
            this.showErrorMessage('Failed to export Excel. Please try again.');
        }
    }

    downloadFile(blob, filename, mimeType) {
        const url = window.URL.createObjectURL(new Blob([blob], { type: mimeType }));
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
}

// Global Functions (called from HTML)
let phManagement;

function initializePHManagement() {
    phManagement = new PHManagementSystem();
}

function refreshAllData() {
    if (phManagement) {
        phManagement.loadInitialData();
    }
}

function showRecordTestModal() {
    const modal = new bootstrap.Modal(document.getElementById('recordTestModal'));
    modal.show();
}

function savePhTest() {
    const form = document.getElementById('recordTestForm');
    if (form) {
        form.dispatchEvent(new Event('submit'));
    }
}

function calculateLimeRequirements() {
    const calculatorTab = document.getElementById('calculator-tab');
    if (calculatorTab) {
        calculatorTab.click();
    }
}

function scheduleMonitoring() {
    const monitoringTab = document.getElementById('monitoring-tab');
    if (monitoringTab) {
        monitoringTab.click();
    }
}

function generateReport() {
    if (phManagement) {
        phManagement.exportToPDF();
    }
}

function showFieldDetails(fieldId) {
    if (phManagement) {
        phManagement.updatePhMeter(phManagement.fieldData.find(f => f.field_id === fieldId)?.current_ph);
    }
}

function updateTrendChart() {
    if (phManagement) {
        const fieldSelector = document.getElementById('fieldSelector');
        const selectedField = fieldSelector ? fieldSelector.value : 'all';
        phManagement.updateTrendChart(selectedField);
    }
}

function updateThresholdValue(elementId, value) {
    if (phManagement) {
        phManagement.updateThresholdValue(elementId, value);
    }
}

function filterHistory() {
    if (phManagement) {
        phManagement.loadHistoryData();
    }
}

function exportToCSV() {
    if (phManagement) {
        phManagement.exportToCSV();
    }
}

function exportToPDF() {
    if (phManagement) {
        phManagement.exportToPDF();
    }
}

function exportToExcel() {
    if (phManagement) {
        phManagement.exportToExcel();
    }
}

function completeTest(testId) {
    // Implementation for completing a test
    console.log('Complete test:', testId);
}

function rescheduleTest(testId) {
    // Implementation for rescheduling a test
    console.log('Reschedule test:', testId);
}

function viewTestDetails(recordId) {
    // Implementation for viewing test details
    console.log('View test details:', recordId);
}

function downloadTestReport(recordId) {
    // Implementation for downloading test report
    console.log('Download test report:', recordId);
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PHManagementSystem;
}