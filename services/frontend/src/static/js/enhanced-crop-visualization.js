// Enhanced Crop Visualization JavaScript
// Provides advanced visualization capabilities for crop data

class EnhancedCropVisualization {
    constructor() {
        this.charts = {};
        this.currentData = null;
        this.init();
    }

    init() {
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeVisualizations());
        } else {
            this.initializeVisualizations();
        }
    }

    initializeVisualizations() {
        // Set up event listeners for visualization controls
        this.setupEventListeners();
        
        // Initialize any charts that should be loaded immediately
        this.initializeDefaultCharts();
    }

    setupEventListeners() {
        // Listen for tab changes to initialize charts when they become visible
        const tabTriggers = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabTriggers.forEach(trigger => {
            trigger.addEventListener('shown.bs.tab', (event) => {
                const targetPanel = event.target.getAttribute('href');
                this.handleTabChange(targetPanel);
            });
        });

        // Listen for export chart buttons
        const exportButtons = document.querySelectorAll('.export-chart-btn');
        exportButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const chartId = event.target.getAttribute('data-chart');
                this.exportChartAsImage(chartId);
            });
        });

        // Listen for download data buttons
        const downloadButtons = document.querySelectorAll('.download-data-btn');
        downloadButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const dataType = event.target.getAttribute('data-type');
                this.exportResultsByType(dataType);
            });
        });
    }

    handleTabChange(panelId) {
        // Initialize charts when their tab becomes active
        switch(panelId) {
            case '#visualization-panel':
                this.initializeVisualizationCharts();
                break;
            case '#comparison-panel':
                this.initializeComparisonCharts();
                break;
        }
    }

    initializeDefaultCharts() {
        // Initialize any charts that should be visible on page load
        // For example, if there are summary charts in the main content area
        if (document.getElementById('filterImpactChart')) {
            this.initializeFilterImpactChart();
        }
    }

    initializeVisualizationCharts() {
        // Initialize all visualization charts
        this.initializeFilterImpactChart();
        this.initializeCategoryDistributionChart();
        this.initializeDroughtToleranceChart();
        this.initializeYieldPotentialChart();
        this.initializeCostAnalysisChart();
        this.initializeGeographicDistributionChart();
        this.initializeSeasonalTrendChart();
        this.initializeSuitabilityDistributionChart();
        this.initializeManagementComplexityChart();
    }

    initializeComparisonCharts() {
        // Initialize comparison charts when the comparison tab is activated
        // This would be called when the user switches to the comparison tab
        console.log('Initializing comparison charts...');
    }

    initializeFilterImpactChart() {
        const ctx = document.getElementById('filterImpactChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.filterImpactChart) {
            this.charts.filterImpactChart.destroy();
        }

        // Create a sample chart - in a real implementation this would use actual data
        this.charts.filterImpactChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Climate Zone', 'Soil pH', 'Maturity Days', 'Drought Tolerance', 'Management Complexity'],
                datasets: [{
                    label: 'Number of Filter Values Applied',
                    data: [15, 8, 12, 6, 4],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Filter Impact Analysis'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Values'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Filter Types'
                        }
                    }
                }
            }
        });
    }

    initializeCategoryDistributionChart() {
        const ctx = document.getElementById('categoryDistributionChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.categoryChart) {
            this.charts.categoryChart.destroy();
        }

        // Create a sample chart
        this.charts.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Grain Crops', 'Oilseed Crops', 'Legume Crops', 'Forage Crops', 'Cover Crops'],
                datasets: [{
                    label: 'Crop Categories',
                    data: [35, 20, 15, 10, 20],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)'
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
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initializeDroughtToleranceChart() {
        const ctx = document.getElementById('droughtToleranceChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.droughtChart) {
            this.charts.droughtChart.destroy();
        }

        // Create a sample chart
        this.charts.droughtChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Low', 'Moderate', 'High', 'Very High'],
                datasets: [{
                    label: 'Drought Tolerance Levels',
                    data: [25, 35, 25, 15],
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
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initializeYieldPotentialChart() {
        const ctx = document.getElementById('yield-potential-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.yieldChart) {
            this.charts.yieldChart.destroy();
        }

        // Create a sample chart
        this.charts.yieldChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Wheat', 'Corn', 'Soybean', 'Alfalfa', 'Oats'],
                datasets: [
                    {
                        label: 'Min Yield Potential',
                        data: [80, 120, 40, 3, 60],
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Max Yield Potential',
                        data: [150, 200, 60, 8, 100],
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
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Yield Potential'
                        }
                    }
                }
            }
        });
    }

    initializeCostAnalysisChart() {
        const ctx = document.getElementById('cost-analysis-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.costChart) {
            this.charts.costChart.destroy();
        }

        // Create a sample chart
        this.charts.costChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Wheat', 'Corn', 'Soybean', 'Alfalfa', 'Oats'],
                datasets: [
                    {
                        label: 'Establishment Cost ($/acre)',
                        data: [150, 200, 120, 80, 100],
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Maintenance Cost ($/acre)',
                        data: [75, 100, 60, 40, 50],
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
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Cost ($/acre)'
                        }
                    }
                }
            }
        });
    }

    initializeGeographicDistributionChart() {
        const ctx = document.getElementById('geographic-distribution-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.geoChart) {
            this.charts.geoChart.destroy();
        }

        // Create a sample chart using radar chart
        this.charts.geoChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Zone 3a', 'Zone 4a', 'Zone 5a', 'Zone 5b', 'Zone 6a', 'Zone 6b', 'Zone 7a'],
                datasets: [{
                    label: 'Crops per Zone',
                    data: [12, 25, 45, 52, 48, 35, 18],
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    pointBackgroundColor: 'rgba(153, 102, 255, 1)',
                    pointBorderColor: '#fff'
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

    initializeSeasonalTrendChart() {
        const ctx = document.getElementById('seasonal-trend-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.seasonalChart) {
            this.charts.seasonalChart.destroy();
        }

        // Create a sample chart
        this.charts.seasonalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Spring', 'Summer', 'Fall', 'Winter'],
                datasets: [{
                    label: 'Number of Suitable Crops by Season',
                    data: [35, 42, 28, 15],
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

    initializeSuitabilityDistributionChart() {
        const ctx = document.getElementById('suitability-distribution-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.suitabilityDistributionChart) {
            this.charts.suitabilityDistributionChart.destroy();
        }

        // Create a sample chart
        this.charts.suitabilityDistributionChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['0-20%', '21-40%', '41-60%', '61-80%', '81-100%'],
                datasets: [{
                    label: 'Number of Crops',
                    data: [5, 12, 25, 38, 20],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.6)',
                        'rgba(255, 193, 7, 0.6)',
                        'rgba(255, 193, 7, 0.6)',
                        'rgba(40, 167, 69, 0.6)',
                        'rgba(40, 167, 69, 0.6)'
                    ],
                    borderColor: [
                        'rgba(220, 53, 69, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(40, 167, 69, 1)',
                        'rgba(40, 167, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Suitability Score Distribution'
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

    initializeManagementComplexityChart() {
        const ctx = document.getElementById('management-complexity-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.managementComplexityChart) {
            this.charts.managementComplexityChart.destroy();
        }

        // Create a sample chart
        this.charts.managementComplexityChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Low', 'Moderate', 'High'],
                datasets: [{
                    label: 'Management Complexity',
                    data: [40, 35, 25],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Management Complexity Distribution'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    exportChartAsImage(chartId) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Chart with ID ${chartId} not found`);
            alert(`Chart with ID ${chartId} not found`);
            return;
        }

        const imageLink = document.createElement('a');
        const filename = chartId.replace(/-/g, '_') + '_chart.png';
        imageLink.download = filename;
        imageLink.href = canvas.toDataURL('image/png');
        imageLink.click();
    }

    exportResultsByType(dataType) {
        // In a real implementation, this would export actual data
        // For now, we'll just show an alert
        alert(`Exporting ${dataType} data... (In a real implementation, this would download the actual data)`);
    }

    // Method to update charts with new data
    updateChartsWithData(newData) {
        this.currentData = newData;
        
        // Update all charts with new data
        // This would be called when new filter results are received
        console.log('Updating charts with new data:', newData);
    }

    // Method to destroy all charts (useful for cleanup)
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Initialize the visualization system
document.addEventListener('DOMContentLoaded', function() {
    window.enhancedCropVisualization = new EnhancedCropVisualization();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedCropVisualization;
}