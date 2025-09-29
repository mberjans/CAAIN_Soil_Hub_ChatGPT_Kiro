// Mobile Variety Selection JavaScript for CAAIN Soil Hub
// Provides mobile-optimized variety selection with touch interactions and device integration

class MobileVarietySelectionManager {
    constructor() {
        this.currentStep = 1;
        this.selectedCrop = null;
        this.selectedVarieties = new Set();
        this.varietyRecommendations = [];
        this.filteredVarieties = [];
        this.farmData = {};
        this.userPreferences = {};
        this.searchDebounceTimer = null;
        this.apiBaseUrl = '/api/v1';
        this.voiceRecognition = null;
        this.geolocation = null;
        this.isOnline = navigator.onLine;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeVoiceRecognition();
        this.initializeGeolocation();
        this.loadCropData();
        this.setupServiceWorker();
        this.setupTouchGestures();
        this.updateOnlineStatus();
    }

    setupEventListeners() {
        // Farm location input
        const farmLocation = document.getElementById('farmLocation');
        if (farmLocation) {
            farmLocation.addEventListener('input', this.handleLocationSearch.bind(this));
            farmLocation.addEventListener('focus', this.showLocationSuggestions.bind(this));
            farmLocation.addEventListener('blur', this.hideLocationSuggestions.bind(this));
        }

        // Crop search functionality
        const cropSearch = document.getElementById('cropSearch');
        if (cropSearch) {
            cropSearch.addEventListener('input', this.handleCropSearch.bind(this));
            cropSearch.addEventListener('focus', this.showCropSuggestions.bind(this));
            cropSearch.addEventListener('blur', this.hideCropSuggestions.bind(this));
        }

        // Preference sliders
        const sliders = ['yieldPriority', 'sustainabilityPriority'];
        sliders.forEach(sliderId => {
            const slider = document.getElementById(sliderId);
            if (slider) {
                slider.addEventListener('input', this.handlePreferenceChange.bind(this));
            }
        });

        // Online/offline status
        window.addEventListener('online', () => this.updateOnlineStatus());
        window.addEventListener('offline', () => this.updateOnlineStatus());

        // Prevent zoom on double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (event) => {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }

    setupTouchGestures() {
        // Swipe gestures for navigation
        let startX = 0;
        let startY = 0;
        let endX = 0;
        let endY = 0;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            this.handleSwipe(startX, startY, endX, endY);
        });

        // Long press for variety details
        let longPressTimer = null;
        document.addEventListener('touchstart', (e) => {
            if (e.target.closest('.variety-card')) {
                longPressTimer = setTimeout(() => {
                    this.showVarietyDetails(e.target.closest('.variety-card'));
                }, 500);
            }
        });

        document.addEventListener('touchend', () => {
            if (longPressTimer) {
                clearTimeout(longPressTimer);
                longPressTimer = null;
            }
        });

        document.addEventListener('touchmove', () => {
            if (longPressTimer) {
                clearTimeout(longPressTimer);
                longPressTimer = null;
            }
        });
    }

    handleSwipe(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 50;

        // Horizontal swipe
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
                // Swipe right - go to previous step
                this.prevStep(this.currentStep - 1);
            } else {
                // Swipe left - go to next step
                this.nextStep(this.currentStep + 1);
            }
        }
    }

    initializeVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.voiceRecognition = new SpeechRecognition();
            this.voiceRecognition.continuous = false;
            this.voiceRecognition.interimResults = false;
            this.voiceRecognition.lang = 'en-US';

            this.voiceRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                this.handleVoiceSearch(transcript);
            };

            this.voiceRecognition.onerror = (event) => {
                console.error('Voice recognition error:', event.error);
                this.showToast('Voice recognition failed. Please try again.', 'error');
            };
        }
    }

    initializeGeolocation() {
        if ('geolocation' in navigator) {
            this.geolocation = navigator.geolocation;
        }
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then((registration) => {
                    console.log('Service Worker registered:', registration);
                })
                .catch((error) => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    // Navigation Methods
    nextStep(stepNumber) {
        if (this.validateCurrentStep()) {
            this.currentStep = stepNumber;
            this.updateWizardDisplay();
            this.updateProgressBar();
            this.updateBottomNavigation();
            this.scrollToTop();
        }
    }

    prevStep(stepNumber) {
        if (stepNumber >= 1) {
            this.currentStep = stepNumber;
            this.updateWizardDisplay();
            this.updateProgressBar();
            this.updateBottomNavigation();
            this.scrollToTop();
        }
    }

    showStep(stepNumber) {
        this.currentStep = stepNumber;
        this.updateWizardDisplay();
        this.updateProgressBar();
        this.updateBottomNavigation();
        this.scrollToTop();
    }

    updateWizardDisplay() {
        // Hide all steps
        const steps = document.querySelectorAll('.wizard-step');
        steps.forEach(step => step.classList.remove('active'));

        // Show current step
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }
    }

    updateProgressBar() {
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            const progress = (this.currentStep / 4) * 100;
            progressBar.style.width = `${progress}%`;
        }
    }

    updateBottomNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach((item, index) => {
            item.classList.toggle('active', index + 1 === this.currentStep);
        });
    }

    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Validation Methods
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
        const location = document.getElementById('farmLocation').value.trim();
        const farmSize = document.getElementById('farmSize').value;
        const soilType = document.getElementById('soilType').value;

        if (!location || !farmSize || !soilType) {
            this.showToast('Please fill in all farm information fields.', 'warning');
            return false;
        }

        if (parseInt(farmSize) < 1 || parseInt(farmSize) > 10000) {
            this.showToast('Please enter a valid farm size between 1 and 10,000 acres.', 'warning');
            return false;
        }

        // Store farm data
        this.farmData = {
            location: location,
            farmSize: parseInt(farmSize),
            soilType: soilType,
            irrigation: document.querySelector('.toggle-btn.active[data-value]').dataset.value === 'true'
        };

        return true;
    }

    validateCropSelection() {
        if (!this.selectedCrop) {
            this.showToast('Please select a crop to continue.', 'warning');
            return false;
        }
        return true;
    }

    validatePreferences() {
        const yieldPriority = document.getElementById('yieldPriority').value;
        const sustainabilityPriority = document.getElementById('sustainabilityPriority').value;
        const riskTolerance = document.querySelector('.risk-btn.active').dataset.value;

        this.userPreferences = {
            yieldPriority: parseInt(yieldPriority),
            sustainabilityPriority: parseInt(sustainabilityPriority),
            riskTolerance: riskTolerance
        };

        return true;
    }

    // Location Methods
    async getCurrentLocation() {
        if (!this.geolocation) {
            this.showToast('Geolocation is not supported on this device.', 'error');
            return;
        }

        this.showLoading('Getting your location...');

        try {
            const position = await new Promise((resolve, reject) => {
                this.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                });
            });

            const { latitude, longitude } = position.coords;
            const location = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
            
            document.getElementById('farmLocation').value = location;
            this.farmData.coordinates = { latitude, longitude };
            
            this.hideLoading();
            this.showToast('Location detected successfully!', 'success');
        } catch (error) {
            this.hideLoading();
            this.showToast('Unable to get your location. Please enter it manually.', 'error');
        }
    }

    async handleLocationSearch(event) {
        const query = event.target.value.trim();
        if (query.length < 3) {
            this.hideLocationSuggestions();
            return;
        }

        try {
            const response = await fetch(`/api/v1/locations/search?q=${encodeURIComponent(query)}`);
            const suggestions = await response.json();
            this.displayLocationSuggestions(suggestions);
        } catch (error) {
            console.error('Location search error:', error);
        }
    }

    displayLocationSuggestions(suggestions) {
        const container = document.getElementById('locationSuggestions');
        if (!container) return;

        if (suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = suggestions.map(suggestion => `
            <div class="location-suggestion" onclick="selectLocation('${suggestion.address}')">
                <div class="fw-bold">${suggestion.name}</div>
                <div class="small text-muted">${suggestion.address}</div>
            </div>
        `).join('');

        container.style.display = 'block';
    }

    selectLocation(address) {
        document.getElementById('farmLocation').value = address;
        this.hideLocationSuggestions();
    }

    showLocationSuggestions() {
        const container = document.getElementById('locationSuggestions');
        if (container && container.children.length > 0) {
            container.style.display = 'block';
        }
    }

    hideLocationSuggestions() {
        setTimeout(() => {
            const container = document.getElementById('locationSuggestions');
            if (container) {
                container.style.display = 'none';
            }
        }, 200);
    }

    // Crop Methods
    async loadCropData() {
        try {
            const response = await fetch('/api/v1/crop-taxonomy/crops');
            const crops = await response.json();
            this.displayCropGrid(crops.slice(0, 12)); // Show first 12 popular crops
        } catch (error) {
            console.error('Error loading crop data:', error);
            this.showToast('Unable to load crop data. Please check your connection.', 'error');
        }
    }

    displayCropGrid(crops) {
        const cropGrid = document.getElementById('cropGrid');
        if (!cropGrid) return;

        cropGrid.innerHTML = crops.map(crop => `
            <div class="crop-card" onclick="selectCrop('${crop.id}', '${crop.name}')">
                <i class="fas fa-seedling"></i>
                <h4>${crop.name}</h4>
                <p>${crop.scientific_name || ''}</p>
            </div>
        `).join('');
    }

    selectCrop(cropId, cropName) {
        // Remove previous selection
        document.querySelectorAll('.crop-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selection to clicked card
        event.target.closest('.crop-card').classList.add('selected');

        this.selectedCrop = { id: cropId, name: cropName };
        
        // Enable next button
        const nextButton = document.getElementById('step2Next');
        if (nextButton) {
            nextButton.disabled = false;
        }

        this.showToast(`${cropName} selected!`, 'success');
    }

    async handleCropSearch(event) {
        const query = event.target.value.trim();
        
        if (this.searchDebounceTimer) {
            clearTimeout(this.searchDebounceTimer);
        }

        this.searchDebounceTimer = setTimeout(async () => {
            if (query.length < 2) {
                this.hideCropSuggestions();
                return;
            }

            try {
                const response = await fetch(`/api/v1/crop-taxonomy/crops/search?q=${encodeURIComponent(query)}`);
                const crops = await response.json();
                this.displayCropSuggestions(crops);
            } catch (error) {
                console.error('Crop search error:', error);
            }
        }, 300);
    }

    displayCropSuggestions(crops) {
        const container = document.getElementById('cropSuggestions');
        if (!container) return;

        if (crops.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = crops.map(crop => `
            <div class="search-suggestion" onclick="selectCropFromSearch('${crop.id}', '${crop.name}')">
                <div class="fw-bold">${crop.name}</div>
                <div class="small text-muted">${crop.scientific_name || ''}</div>
            </div>
        `).join('');

        container.style.display = 'block';
    }

    selectCropFromSearch(cropId, cropName) {
        document.getElementById('cropSearch').value = cropName;
        this.hideCropSuggestions();
        this.selectCrop(cropId, cropName);
    }

    showCropSuggestions() {
        const container = document.getElementById('cropSuggestions');
        if (container && container.children.length > 0) {
            container.style.display = 'block';
        }
    }

    hideCropSuggestions() {
        setTimeout(() => {
            const container = document.getElementById('cropSuggestions');
            if (container) {
                container.style.display = 'none';
            }
        }, 200);
    }

    // Voice Search
    startVoiceSearch() {
        if (!this.voiceRecognition) {
            this.showToast('Voice recognition is not supported on this device.', 'error');
            return;
        }

        this.voiceRecognition.start();
        this.showToast('Listening... Speak now.', 'info');
    }

    handleVoiceSearch(transcript) {
        document.getElementById('cropSearch').value = transcript;
        this.handleCropSearch({ target: { value: transcript } });
        this.showToast(`Searching for: ${transcript}`, 'info');
    }

    // Preference Methods
    handlePreferenceChange(event) {
        const slider = event.target;
        const value = slider.value;
        const label = slider.previousElementSibling;
        
        if (label) {
            const text = label.textContent;
            label.textContent = text.replace(/\d+/, value);
        }
    }

    selectRisk(button) {
        document.querySelectorAll('.risk-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }

    toggleIrrigation(button) {
        document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
    }

    // Recommendation Methods
    async getRecommendations() {
        if (!this.validatePreferences()) {
            return;
        }

        this.showLoading('Getting personalized recommendations...');

        try {
            const requestData = {
                crop_id: this.selectedCrop.id,
                farm_context: {
                    location: this.farmData.location,
                    farm_size_acres: this.farmData.farmSize,
                    soil_type: this.farmData.soilType,
                    irrigation_available: this.farmData.irrigation,
                    coordinates: this.farmData.coordinates
                },
                farmer_preferences: this.userPreferences,
                recommendation_count: 5
            };

            const response = await fetch('/api/v1/crop-taxonomy/varieties/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const recommendations = await response.json();
            this.varietyRecommendations = recommendations.varieties || [];
            
            this.displayRecommendations();
            this.nextStep(4);
            this.hideLoading();
            
        } catch (error) {
            this.hideLoading();
            console.error('Error getting recommendations:', error);
            this.showToast('Unable to get recommendations. Please try again.', 'error');
        }
    }

    displayRecommendations() {
        const container = document.getElementById('recommendationsContainer');
        if (!container) return;

        if (this.varietyRecommendations.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                    <h4>No Recommendations Found</h4>
                    <p class="text-muted">Try adjusting your preferences or selecting a different crop.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.varietyRecommendations.map((variety, index) => `
            <div class="variety-card" onclick="selectVariety('${variety.id}', ${index})">
                <div class="variety-header">
                    <h3 class="variety-name">${variety.name}</h3>
                    <span class="variety-score">${Math.round(variety.score * 100)}%</span>
                </div>
                
                <div class="variety-details">
                    <div class="variety-detail">
                        <i class="fas fa-calendar"></i>
                        <span>${variety.maturity_days || 'N/A'} days</span>
                    </div>
                    <div class="variety-detail">
                        <i class="fas fa-chart-line"></i>
                        <span>${variety.yield_potential || 'N/A'} bu/ac</span>
                    </div>
                    <div class="variety-detail">
                        <i class="fas fa-dollar-sign"></i>
                        <span>$${variety.seed_cost_per_acre || 'N/A'}/ac</span>
                    </div>
                    <div class="variety-detail">
                        <i class="fas fa-building"></i>
                        <span>${variety.seed_company || 'N/A'}</span>
                    </div>
                </div>

                <div class="variety-traits">
                    ${(variety.traits || []).map(trait => `
                        <span class="trait-badge ${trait.category}">${trait.name}</span>
                    `).join('')}
                </div>

                <div class="variety-actions">
                    <button class="btn btn-outline-primary btn-sm" onclick="event.stopPropagation(); compareVariety('${variety.id}')">
                        <i class="fas fa-balance-scale"></i> Compare
                    </button>
                    <button class="btn btn-outline-success btn-sm" onclick="event.stopPropagation(); saveVariety('${variety.id}')">
                        <i class="fas fa-bookmark"></i> Save
                    </button>
                </div>
            </div>
        `).join('');
    }

    selectVariety(varietyId, index) {
        const variety = this.varietyRecommendations[index];
        
        // Toggle selection
        if (this.selectedVarieties.has(varietyId)) {
            this.selectedVarieties.delete(varietyId);
            event.target.closest('.variety-card').classList.remove('selected');
        } else {
            this.selectedVarieties.add(varietyId);
            event.target.closest('.variety-card').classList.add('selected');
        }

        this.showToast(`${variety.name} ${this.selectedVarieties.has(varietyId) ? 'selected' : 'deselected'}`, 'info');
    }

    showVarietyDetails(cardElement) {
        const varietyName = cardElement.querySelector('.variety-name').textContent;
        this.showToast(`Long press detected for ${varietyName}`, 'info');
        // TODO: Implement detailed variety view
    }

    // Utility Methods
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = overlay.querySelector('.loading-text');
        if (overlay && text) {
            text.textContent = message;
            overlay.classList.add('show');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastBody = document.getElementById('toastBody');
        const toastHeader = toast.querySelector('.toast-header i');
        
        if (toast && toastBody && toastHeader) {
            toastBody.textContent = message;
            
            // Update icon based on type
            toastHeader.className = `fas me-2`;
            switch (type) {
                case 'success':
                    toastHeader.classList.add('fa-check-circle', 'text-success');
                    break;
                case 'error':
                    toastHeader.classList.add('fa-exclamation-circle', 'text-danger');
                    break;
                case 'warning':
                    toastHeader.classList.add('fa-exclamation-triangle', 'text-warning');
                    break;
                default:
                    toastHeader.classList.add('fa-info-circle', 'text-primary');
            }
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }

    updateOnlineStatus() {
        this.isOnline = navigator.onLine;
        const status = this.isOnline ? 'online' : 'offline';
        this.showToast(`You are now ${status}`, 'info');
    }

    async saveRecommendations() {
        if (this.selectedVarieties.size === 0) {
            this.showToast('Please select at least one variety to save.', 'warning');
            return;
        }

        try {
            const selectedVarietyData = this.varietyRecommendations.filter(v => 
                this.selectedVarieties.has(v.id)
            );

            const response = await fetch('/api/v1/recommendations/variety/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    crop_id: this.selectedCrop.id,
                    farm_context: this.farmData,
                    farmer_preferences: this.userPreferences,
                    selected_varieties: selectedVarietyData,
                    recommendation_session_id: Date.now().toString()
                })
            });

            if (response.ok) {
                this.showToast('Recommendations saved successfully!', 'success');
            } else {
                throw new Error('Failed to save recommendations');
            }
        } catch (error) {
            console.error('Error saving recommendations:', error);
            this.showToast('Unable to save recommendations. Please try again.', 'error');
        }
    }
}

// Global functions for HTML onclick handlers
function goBack() {
    if (window.history.length > 1) {
        window.history.back();
    } else {
        window.location.href = '/dashboard';
    }
}

function showMenu() {
    // TODO: Implement mobile menu
    console.log('Show menu');
}

function getCurrentLocation() {
    mobileVarietyManager.getCurrentLocation();
}

function selectLocation(address) {
    mobileVarietyManager.selectLocation(address);
}

function selectCrop(cropId, cropName) {
    mobileVarietyManager.selectCrop(cropId, cropName);
}

function selectCropFromSearch(cropId, cropName) {
    mobileVarietyManager.selectCropFromSearch(cropId, cropName);
}

function startVoiceSearch() {
    mobileVarietyManager.startVoiceSearch();
}

function selectRisk(button) {
    mobileVarietyManager.selectRisk(button);
}

function toggleIrrigation(button) {
    mobileVarietyManager.toggleIrrigation(button);
}

function nextStep(stepNumber) {
    mobileVarietyManager.nextStep(stepNumber);
}

function prevStep(stepNumber) {
    mobileVarietyManager.prevStep(stepNumber);
}

function showStep(stepNumber) {
    mobileVarietyManager.showStep(stepNumber);
}

function getRecommendations() {
    mobileVarietyManager.getRecommendations();
}

function selectVariety(varietyId, index) {
    mobileVarietyManager.selectVariety(varietyId, index);
}

function compareVariety(varietyId) {
    // TODO: Implement variety comparison
    console.log('Compare variety:', varietyId);
}

function saveVariety(varietyId) {
    // TODO: Implement variety saving
    console.log('Save variety:', varietyId);
}

function saveRecommendations() {
    mobileVarietyManager.saveRecommendations();
}

// Initialize the mobile variety selection manager when the page loads
let mobileVarietyManager;
document.addEventListener('DOMContentLoaded', () => {
    mobileVarietyManager = new MobileVarietySelectionManager();
});