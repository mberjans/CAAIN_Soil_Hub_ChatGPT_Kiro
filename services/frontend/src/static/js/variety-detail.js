/**
 * Variety Detail Page JavaScript
 * 
 * Handles interactive functionality for the variety detail page including
 * charts, sharing, comparison, and user interactions.
 */

class VarietyDetailManager {
    constructor() {
        this.varietyId = this.getVarietyIdFromUrl();
        this.varietyData = null;
        this.charts = {};
        
        this.init();
    }
    
    init() {
        this.loadVarietyData();
        this.initializeCharts();
        this.setupEventListeners();
        this.setupSocialSharing();
    }
    
    getVarietyIdFromUrl() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }
    
    async loadVarietyData() {
        try {
            const response = await fetch(`/api/v1/varieties/${this.varietyId}`);
            if (response.ok) {
                this.varietyData = await response.json();
                this.updatePageData();
            } else {
                console.error('Failed to load variety data');
                this.showError('Failed to load variety data');
            }
        } catch (error) {
            console.error('Error loading variety data:', error);
            this.showError('Error loading variety data');
        }
    }
    
    updatePageData() {
        // Update page title and meta tags
        document.title = `${this.varietyData.name} - Variety Details - AFAS`;
        
        // Update any dynamic content that wasn't rendered server-side
        this.updateDynamicContent();
    }
    
    updateDynamicContent() {
        // Update any content that needs to be dynamically updated
        const varietyNameElement = document.querySelector('.variety-name');
        if (varietyNameElement && this.varietyData.name) {
            varietyNameElement.textContent = this.varietyData.name;
        }
    }
    
    initializeCharts() {
        this.createOverviewChart();
        this.createYieldChart();
        this.createPerformanceChart();
        this.createRegionalChart();
        this.createROIChart();
        this.createYieldCostChart();
    }
    
    createOverviewChart() {
        const ctx = document.getElementById('overviewChart');
        if (!ctx) return;
        
        this.charts.overview = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Yield Potential', 'Disease Resistance', 'Standability', 'Market Acceptance'],
                datasets: [{
                    data: [85, 90, 80, 88],
                    backgroundColor: [
                        '#28a745',
                        '#20c997',
                        '#ffc107',
                        '#007bff'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    createYieldChart() {
        const ctx = document.getElementById('yieldChart');
        if (!ctx) return;
        
        this.charts.yield = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['2019', '2020', '2021', '2022', '2023'],
                datasets: [{
                    label: 'Yield (bu/acre)',
                    data: [185, 192, 188, 201, 195],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 150,
                        max: 220
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    createPerformanceChart() {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        this.charts.performance = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Yield', 'Disease Resistance', 'Standability', 'Maturity', 'Quality', 'Market Acceptance'],
                datasets: [{
                    label: this.varietyData?.name || 'This Variety',
                    data: [85, 90, 80, 75, 88, 92],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderWidth: 2
                }, {
                    label: 'Industry Average',
                    data: [75, 70, 70, 70, 75, 78],
                    borderColor: '#6c757d',
                    backgroundColor: 'rgba(108, 117, 125, 0.2)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    createRegionalChart() {
        const ctx = document.getElementById('regionalChart');
        if (!ctx) return;
        
        this.charts.regional = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Midwest', 'Great Plains', 'Northeast', 'Southeast', 'Southwest'],
                datasets: [{
                    label: 'Performance Index',
                    data: [92, 88, 85, 78, 82],
                    backgroundColor: [
                        '#28a745',
                        '#20c997',
                        '#17a2b8',
                        '#ffc107',
                        '#fd7e14'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    createROIChart() {
        const ctx = document.getElementById('roiChart');
        if (!ctx) return;
        
        this.charts.roi = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
                datasets: [{
                    label: 'Cumulative ROI',
                    data: [15, 35, 58, 85, 115],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'ROI (%)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    createYieldCostChart() {
        const ctx = document.getElementById('yieldCostChart');
        if (!ctx) return;
        
        this.charts.yieldCost = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Yield vs Cost',
                    data: [
                        {x: 180, y: 280},
                        {x: 185, y: 285},
                        {x: 192, y: 290},
                        {x: 188, y: 295},
                        {x: 201, y: 300},
                        {x: 195, y: 305}
                    ],
                    backgroundColor: '#28a745',
                    borderColor: '#28a745',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Yield (bu/acre)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Cost ($/acre)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    setupEventListeners() {
        // Tab change events
        const tabButtons = document.querySelectorAll('[data-bs-toggle="pill"]');
        tabButtons.forEach(button => {
            button.addEventListener('shown.bs.tab', (event) => {
                this.handleTabChange(event.target.getAttribute('data-bs-target'));
            });
        });
        
        // Chart resize events
        window.addEventListener('resize', () => {
            this.resizeCharts();
        });
    }
    
    handleTabChange(targetTab) {
        // Handle tab-specific functionality
        if (targetTab === '#performance') {
            this.updatePerformanceCharts();
        } else if (targetTab === '#regional') {
            this.updateRegionalData();
        } else if (targetTab === '#economic') {
            this.updateEconomicData();
        }
    }
    
    updatePerformanceCharts() {
        // Update performance charts with latest data
        if (this.charts.yield) {
            this.charts.yield.update();
        }
        if (this.charts.performance) {
            this.charts.performance.update();
        }
    }
    
    updateRegionalData() {
        // Update regional data and charts
        if (this.charts.regional) {
            this.charts.regional.update();
        }
    }
    
    updateEconomicData() {
        // Update economic analysis data
        if (this.charts.roi) {
            this.charts.roi.update();
        }
        if (this.charts.yieldCost) {
            this.charts.yieldCost.update();
        }
    }
    
    resizeCharts() {
        // Resize all charts when window is resized
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }
    
    setupSocialSharing() {
        // Setup social media sharing functionality
        this.shareUrls = {
            facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(window.location.href)}`,
            twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(window.location.href)}&text=${encodeURIComponent(`Check out ${this.varietyData?.name || 'this variety'} on AFAS`)}`,
            linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`
        };
    }
    
    // Action Methods
    shareVariety(platform) {
        if (this.shareUrls[platform]) {
            window.open(this.shareUrls[platform], '_blank', 'width=600,height=400');
        }
    }
    
    copyLink() {
        navigator.clipboard.writeText(window.location.href).then(() => {
            this.showNotification('Link copied to clipboard!', 'success');
        }).catch(() => {
            this.showNotification('Failed to copy link', 'error');
        });
    }
    
    addToComparison() {
        // Add variety to comparison list
        const comparisonData = {
            varietyId: this.varietyId,
            varietyName: this.varietyData?.name || 'Unknown Variety',
            addedAt: new Date().toISOString()
        };
        
        let comparisonList = JSON.parse(localStorage.getItem('varietyComparison') || '[]');
        
        // Check if already in comparison
        if (!comparisonList.find(item => item.varietyId === this.varietyId)) {
            comparisonList.push(comparisonData);
            localStorage.setItem('varietyComparison', JSON.stringify(comparisonList));
            this.showNotification('Variety added to comparison!', 'success');
        } else {
            this.showNotification('Variety already in comparison list', 'info');
        }
    }
    
    saveVariety() {
        // Save variety to user's saved list
        const savedData = {
            varietyId: this.varietyId,
            varietyName: this.varietyData?.name || 'Unknown Variety',
            savedAt: new Date().toISOString()
        };
        
        let savedList = JSON.parse(localStorage.getItem('savedVarieties') || '[]');
        
        // Check if already saved
        if (!savedList.find(item => item.varietyId === this.varietyId)) {
            savedList.push(savedData);
            localStorage.setItem('savedVarieties', JSON.stringify(savedList));
            this.showNotification('Variety saved to your list!', 'success');
        } else {
            this.showNotification('Variety already saved', 'info');
        }
    }
    
    getRecommendations() {
        // Get personalized recommendations based on this variety
        this.showNotification('Generating personalized recommendations...', 'info');
        
        // Simulate API call
        setTimeout(() => {
            window.location.href = '/variety-selection?recommendations=true&base_variety=' + this.varietyId;
        }, 1000);
    }
    
    contactSupplier() {
        // Open contact supplier modal or redirect
        const supplierEmail = this.varietyData?.supplier_email || 'info@afas.com';
        const subject = `Inquiry about ${this.varietyData?.name || 'variety'}`;
        const body = `Hello,\n\nI'm interested in learning more about ${this.varietyData?.name || 'this variety'}.\n\nPlease provide more information about:\n- Availability\n- Pricing\n- Delivery options\n\nThank you!`;
        
        const mailtoUrl = `mailto:${supplierEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.location.href = mailtoUrl;
    }
    
    loadMoreReviews() {
        // Load additional reviews
        this.showNotification('Loading more reviews...', 'info');
        
        // Simulate loading more reviews
        setTimeout(() => {
            this.showNotification('More reviews loaded!', 'success');
        }, 1000);
    }
    
    // Utility Methods
    showNotification(message, type = 'info') {
        // Create and show notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    // Export functionality
    exportVarietyData() {
        const exportData = {
            variety: this.varietyData,
            exportDate: new Date().toISOString(),
            source: 'AFAS Variety Detail Page'
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `${this.varietyData?.name || 'variety'}_data.json`;
        link.click();
    }
}

// Global functions for HTML onclick handlers
function shareVariety(platform) {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.shareVariety(platform);
    }
}

function copyLink() {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.copyLink();
    }
}

function addToComparison() {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.addToComparison();
    }
}

function saveVariety() {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.saveVariety();
    }
}

function getRecommendations() {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.getRecommendations();
    }
}

function contactSupplier() {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.contactSupplier();
    }
}

function loadMoreReviews() {
    if (window.varietyDetailManager) {
        window.varietyDetailManager.loadMoreReviews();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.varietyDetailManager = new VarietyDetailManager();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (window.varietyDetailManager && !document.hidden) {
        // Page became visible, refresh data if needed
        window.varietyDetailManager.resizeCharts();
    }
});