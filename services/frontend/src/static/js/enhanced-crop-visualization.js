// Enhanced Crop Filtering Visualization for CAAIN Soil Hub
// Provides advanced interactive visualization features for crop filter results

class EnhancedCropVisualization {
    constructor() {
        this.charts = {};
        this.currentResults = [];
        this.activeFilters = {};
        this.init();
    }

    init() {
        this.bindVisualizationEvents();
        this.setupInteractiveCharts();
        console.log('Enhanced Crop Visualization initialized');
    }

    bindVisualizationEvents() {
        // Bind export buttons for each chart
        document.querySelectorAll('.export-chart-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const chartId = e.target.dataset.chart;
                this.exportChartAsImage(chartId);
            });
        });

        // Bind download data buttons
        document.querySelectorAll('.download-data-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const dataType = e.target.dataset.type;
                this.downloadData(dataType);
            });
        });

        // Advanced filter interactions
        document.getElementById('visualization-panel')?.addEventListener('click', (e) => {
            if (e.target.classList.contains('chart-toggle')) {
                this.toggleChart(e.target.dataset.chart);
            }
        });
    }

    setupInteractiveCharts() {
        // Set up advanced interactive charts when data is available
        if (this.currentResults && this.currentResults.length > 0) {
            this.createAdvancedVisualizations();
        }
    }

    createAdvancedVisualizations() {
        // Create additional visualization charts beyond the basic ones
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
        const minYield = this.currentResults.slice(0, 10).map(crop => crop.yield_potential?.min || 0);
        const maxYield = this.currentResults.slice(0, 10).map(crop => crop.yield_potential?.max || 0);

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

        // Group results by planting season
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

    // Enhanced visualization with drill-down capabilities
    createDrillDownVisualization() {
        // Add event listeners for drill-down functionality on charts
        if (this.charts.categoryChart) {
            this.charts.categoryChart.options.plugins.tooltip.callbacks = {
                title: (items) => {
                    return items[0].label;
                },
                label: (context) => {
                    const label = context.label;
                    const value = context.parsed;
                    const total = this.calculateTotalForLabel(label);
                    const percentage = ((value / total) * 100).toFixed(2);
                    
                    return `${label}: ${value} crops (${percentage}%)`;
                }
            };
            
            this.charts.categoryChart.update();
        }
    }

    calculateTotalForLabel(label) {
        // Calculate total for percentage calculation
        const total = this.currentResults.length;
        return total;
    }

    // Export functionality for charts
    exportChartAsImage(chartId) {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
            console.error(`Chart with ID ${chartId} not found`);
            return;
        }

        // Create a temporary link element
        const link = document.createElement('a');
        link.download = `${chartId.replace(/-/g, '_')}_chart.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }

    // Export visualization data
    downloadData(dataType) {
        if (!this.currentResults || this.currentResults.length === 0) {
            alert('No data available to download');
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
                console.error('Unknown data type for export');
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

    exportResultsAsCSV() {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance\n';
        
        this.currentResults.forEach(crop => {
            const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
            csvContent += `"${crop.name}","${crop.scientific_name}","${crop.category.replace(/_/g, ' ')}",` +
                         `"${crop.suitability_score}","${climateZones}","${crop.ph_range?.min || ''}",` +
                         `"${crop.ph_range?.max || ''}","${crop.maturity_days || ''}","${crop.drought_tolerance || ''}"\n`;
        });
        
        return csvContent;
    }

    exportSummaryAsCSV() {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Category,Count,Percentage,Top Crops\n';
        
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
                
            csvContent += `"${category}","${count}","${percentage}%","${topCrops}"\n`;
        });
        
        return csvContent;
    }

    exportDetailedAsCSV() {
        let csvContent = 'data:text/csv;charset=utf-8,';
        csvContent += 'Name,Scientific Name,Category,Suitability Score,Climate Zones,pH Min,pH Max,Maturity Days,Drought Tolerance,Management Complexity,Tags\n';
        
        this.currentResults.forEach(crop => {
            const climateZones = crop.climate_zones ? crop.climate_zones.join(';') : '';
            const tags = crop.tags ? crop.tags.join('; ') : '';
            csvContent += `"${crop.name}","${crop.scientific_name}","${crop.category.replace(/_/g, ' ')}",` +
                         `"${crop.suitability_score}","${climateZones}","${crop.ph_range?.min || ''}",` +
                         `"${crop.ph_range?.max || ''}","${crop.maturity_days || ''}","${crop.drought_tolerance || ''}",` +
                         `"${crop.management_complexity || ''}","${tags}"\n`;
        });
        
        return csvContent;
    }

    // Toggle chart visibility
    toggleChart(chartId) {
        const chart = document.getElementById(chartId);
        if (chart) {
            if (chart.style.display === 'none') {
                chart.style.display = 'block';
            } else {
                chart.style.display = 'none';
            }
        }
    }

    // Update visualization with new results
    updateVisualization(results, filters) {
        this.currentResults = results || [];
        this.activeFilters = filters || {};
        
        // Re-render all charts with new data
        this.createAdvancedVisualizations();
        this.createDrillDownVisualization();
    }

    // Create heat map visualization for complex multi-dimensional data
    createHeatMapVisualization() {
        // Implementation for creating heat map visualization
        // This would show relationships between different filtering dimensions
    }

    // Create network graph for crop relationships
    createNetworkGraphVisualization() {
        // Implementation for creating network graph showing relationships between crops
        // based on similar requirements or characteristics
    }

    // Add animation effects to charts
    addChartAnimations() {
        // Add subtle animations to make charts more engaging
        Object.values(this.charts).forEach(chart => {
            if (chart.options.animation === undefined) {
                chart.options.animation = {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                };
            }
        });
    }

    // Add responsive design features for charts
    makeChartsResponsive() {
        // Implement responsive design for charts that adapt to container size
        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => {
                chart.resize();
            });
        });
    }
}

// Initialize the enhanced visualization when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        window.enhancedCropVisualization = new EnhancedCropVisualization();
        
        // Listen for updates from the main crop filtering system
        if (window.cropFilteringManager) {
            // Hook into the filtering system to update visualizations when results change
            const originalDisplayResults = window.cropFilteringManager.displayResults;
            window.cropFilteringManager.displayResults = function() {
                originalDisplayResults.apply(this, arguments);
                // Update the enhanced visualization after results are displayed
                if (window.enhancedCropVisualization) {
                    window.enhancedCropVisualization.updateVisualization(
                        this.currentResults, 
                        this.currentFilters
                    );
                }
            };
        }
    } else {
        console.error('Chart.js library not loaded. Visualization features will not be available.');
    }
});