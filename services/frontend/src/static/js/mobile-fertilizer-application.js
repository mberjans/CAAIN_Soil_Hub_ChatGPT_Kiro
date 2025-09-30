// Mobile Fertilizer Application JavaScript for CAAIN Soil Hub
// Provides mobile-optimized fertilizer application with device integration and field-ready functionality

class MobileFertilizerApplicationManager {
    constructor() {
        this.currentStep = 1;
        this.selectedMethod = null;
        this.applicationData = {};
        this.fieldData = {};
        this.fertilizerData = {};
        this.equipmentData = {};
        this.isApplicationActive = false;
        this.applicationStartTime = null;
        this.monitoringInterval = null;
        this.apiBaseUrl = '/api/v1';
        this.voiceRecognition = null;
        this.geolocation = null;
        this.isOnline = navigator.onLine;
        this.offlineData = [];
        this.fieldPhotos = [];
        this.voiceNotes = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeVoiceRecognition();
        this.initializeGeolocation();
        this.setupServiceWorker();
        this.setupTouchGestures();
        this.updateOnlineStatus();
        this.loadWeatherData();
        this.setupPushNotifications();
    }

    setupEventListeners() {
        // Field location input
        const fieldLocation = document.getElementById('fieldLocation');
        if (fieldLocation) {
            fieldLocation.addEventListener('input', this.handleLocationSearch.bind(this));
            fieldLocation.addEventListener('focus', this.showLocationSuggestions.bind(this));
            fieldLocation.addEventListener('blur', this.hideLocationSuggestions.bind(this));
        }

        // Form validation
        const formInputs = document.querySelectorAll('input, select');
        formInputs.forEach(input => {
            input.addEventListener('change', this.validateCurrentStep.bind(this));
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

        // Application date default to today
        const applicationDate = document.getElementById('applicationDate');
        if (applicationDate) {
            applicationDate.value = new Date().toISOString().split('T')[0];
        }
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

        // Long press for method details
        let longPressTimer = null;
        document.addEventListener('touchstart', (e) => {
            if (e.target.closest('.method-card')) {
                longPressTimer = setTimeout(() => {
                    this.showMethodDetails(e.target.closest('.method-card'));
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
                this.handleVoiceNote(transcript);
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
            navigator.serviceWorker.register('/static/sw-fertilizer.js')
                .then((registration) => {
                    console.log('Service Worker registered:', registration);
                })
                .catch((error) => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    setupPushNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('Push notifications enabled');
                }
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
            
            // Load step-specific data
            this.loadStepData(stepNumber);
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
        this.loadStepData(stepNumber);
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
            const progress = (this.currentStep / 5) * 100;
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

    loadStepData(stepNumber) {
        switch (stepNumber) {
            case 4:
                this.loadWeatherData();
                break;
            case 5:
                this.generateApplicationSummary();
                break;
        }
    }

    // Validation Methods
    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.validateFieldInformation();
            case 2:
                return this.validateFertilizerSelection();
            case 3:
                return this.validateMethodSelection();
            case 4:
                return this.validateEquipmentAndTiming();
            default:
                return true;
        }
    }

    validateFieldInformation() {
        const location = document.getElementById('fieldLocation').value.trim();
        const fieldSize = document.getElementById('fieldSize').value;
        const soilType = document.getElementById('soilType').value;
        const cropType = document.getElementById('cropType').value;
        const growthStage = document.getElementById('growthStage').value;

        if (!location || !fieldSize || !soilType || !cropType || !growthStage) {
            this.showToast('Please fill in all field information fields.', 'warning');
            return false;
        }

        if (parseFloat(fieldSize) < 0.1 || parseFloat(fieldSize) > 10000) {
            this.showToast('Please enter a valid field size between 0.1 and 10,000 acres.', 'warning');
            return false;
        }

        // Store field data
        this.fieldData = {
            location: location,
            fieldSize: parseFloat(fieldSize),
            soilType: soilType,
            cropType: cropType,
            growthStage: growthStage
        };

        return true;
    }

    validateFertilizerSelection() {
        const fertilizerType = document.getElementById('fertilizerType').value;
        const fertilizerForm = document.querySelector('.toggle-btn.active[data-value]')?.dataset.value;
        const applicationRate = document.getElementById('applicationRate').value;
        const fertilizerCost = document.getElementById('fertilizerCost').value;

        if (!fertilizerType || !fertilizerForm || !applicationRate || !fertilizerCost) {
            this.showToast('Please fill in all fertilizer information fields.', 'warning');
            return false;
        }

        if (parseFloat(applicationRate) <= 0 || parseFloat(applicationRate) > 1000) {
            this.showToast('Please enter a valid application rate between 0 and 1000 lbs/acre.', 'warning');
            return false;
        }

        if (parseFloat(fertilizerCost) <= 0 || parseFloat(fertilizerCost) > 1000) {
            this.showToast('Please enter a valid cost between $0 and $1000 per unit.', 'warning');
            return false;
        }

        // Store fertilizer data
        this.fertilizerData = {
            type: fertilizerType,
            form: fertilizerForm,
            applicationRate: parseFloat(applicationRate),
            costPerUnit: parseFloat(fertilizerCost)
        };

        return true;
    }

    validateMethodSelection() {
        if (!this.selectedMethod) {
            this.showToast('Please select an application method to continue.', 'warning');
            return false;
        }
        return true;
    }

    validateEquipmentAndTiming() {
        const equipmentType = document.getElementById('equipmentType').value;
        const applicationDate = document.getElementById('applicationDate').value;

        if (!equipmentType || !applicationDate) {
            this.showToast('Please select equipment type and application date.', 'warning');
            return false;
        }

        // Store equipment data
        this.equipmentData = {
            type: equipmentType,
            applicationDate: applicationDate
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
            
            document.getElementById('fieldLocation').value = location;
            this.fieldData.coordinates = { latitude, longitude };
            
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
        document.getElementById('fieldLocation').value = address;
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

    // Method Selection
    selectMethod(methodId) {
        // Remove previous selection
        document.querySelectorAll('.method-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Add selection to clicked card
        document.querySelector(`[data-method="${methodId}"]`).classList.add('selected');

        this.selectedMethod = methodId;
        
        // Enable next button
        const nextButton = document.getElementById('step3Next');
        if (nextButton) {
            nextButton.disabled = false;
        }

        this.showToast(`${this.getMethodName(methodId)} selected!`, 'success');
    }

    getMethodName(methodId) {
        const methodNames = {
            'broadcast': 'Broadcast Application',
            'band': 'Band Application',
            'foliar': 'Foliar Application',
            'injection': 'Soil Injection'
        };
        return methodNames[methodId] || methodId;
    }

    showMethodDetails(cardElement) {
        const methodId = cardElement.dataset.method;
        const methodName = this.getMethodName(methodId);
        this.showToast(`Long press detected for ${methodName}`, 'info');
        // TODO: Implement detailed method view
    }

    // Weather Methods
    async loadWeatherData() {
        if (!this.fieldData.coordinates) {
            return;
        }

        try {
            const { latitude, longitude } = this.fieldData.coordinates;
            const response = await fetch(`/api/v1/weather/current?latitude=${latitude}&longitude=${longitude}`);
            const weatherData = await response.json();
            
            this.displayWeatherData(weatherData);
        } catch (error) {
            console.error('Error loading weather data:', error);
            this.showToast('Unable to load weather data.', 'warning');
        }
    }

    displayWeatherData(weatherData) {
        const temperature = document.getElementById('temperature');
        const windSpeed = document.getElementById('windSpeed');
        const rainChance = document.getElementById('rainChance');

        if (temperature) temperature.textContent = weatherData.temperature_fahrenheit || '--';
        if (windSpeed) windSpeed.textContent = weatherData.wind_speed_mph || '--';
        if (rainChance) rainChance.textContent = weatherData.precipitation_probability || '--';
    }

    // Camera and Voice Methods
    async takeFieldPhoto() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showToast('Camera is not supported on this device.', 'error');
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            // Create camera interface
            this.showCameraInterface(video, stream);
        } catch (error) {
            console.error('Camera error:', error);
            this.showToast('Unable to access camera. Please check permissions.', 'error');
        }
    }

    showCameraInterface(video, stream) {
        const cameraModal = document.createElement('div');
        cameraModal.className = 'camera-modal';
        cameraModal.innerHTML = `
            <div class="camera-overlay">
                <div class="camera-container">
                    <video id="cameraVideo" autoplay></video>
                    <div class="camera-controls">
                        <button class="btn btn-danger" onclick="closeCamera()">
                            <i class="fas fa-times"></i>
                        </button>
                        <button class="btn btn-success" onclick="capturePhoto()">
                            <i class="fas fa-camera"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(cameraModal);
        document.getElementById('cameraVideo').srcObject = stream;
    }

    capturePhoto() {
        const video = document.getElementById('cameraVideo');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);

        const photoData = canvas.toDataURL('image/jpeg');
        this.fieldPhotos.push({
            data: photoData,
            timestamp: new Date().toISOString(),
            location: this.fieldData.coordinates
        });

        this.displayFieldNotes();
        this.closeCamera();
        this.showToast('Photo captured successfully!', 'success');
    }

    closeCamera() {
        const cameraModal = document.querySelector('.camera-modal');
        if (cameraModal) {
            cameraModal.remove();
        }
    }

    recordVoiceNote() {
        if (!this.voiceRecognition) {
            this.showToast('Voice recognition is not supported on this device.', 'error');
            return;
        }

        this.voiceRecognition.start();
        this.showToast('Listening... Speak now.', 'info');
    }

    handleVoiceNote(transcript) {
        this.voiceNotes.push({
            transcript: transcript,
            timestamp: new Date().toISOString(),
            location: this.fieldData.coordinates
        });

        this.displayFieldNotes();
        this.showToast(`Voice note recorded: ${transcript}`, 'success');
    }

    displayFieldNotes() {
        const container = document.getElementById('fieldNotes');
        if (!container) return;

        const allNotes = [...this.fieldPhotos, ...this.voiceNotes].sort((a, b) => 
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        container.innerHTML = allNotes.map(note => {
            if (note.data) {
                // Photo note
                return `
                    <div class="field-note">
                        <i class="fas fa-camera"></i>
                        <div class="field-note-content">
                            <div>Field photo captured</div>
                            <div class="field-note-time">${new Date(note.timestamp).toLocaleTimeString()}</div>
                        </div>
                    </div>
                `;
            } else {
                // Voice note
                return `
                    <div class="field-note">
                        <i class="fas fa-microphone"></i>
                        <div class="field-note-content">
                            <div>${note.transcript}</div>
                            <div class="field-note-time">${new Date(note.timestamp).toLocaleTimeString()}</div>
                        </div>
                    </div>
                `;
            }
        }).join('');
    }

    // Application Summary and Monitoring
    generateApplicationSummary() {
        const summary = {
            field: this.fieldData,
            fertilizer: this.fertilizerData,
            method: this.selectedMethod,
            equipment: this.equipmentData
        };

        this.displayApplicationSummary(summary);
        this.displayCostBreakdown(summary);
    }

    displayApplicationSummary(summary) {
        const container = document.getElementById('applicationSummary');
        if (!container) return;

        container.innerHTML = `
            <div class="summary-item">
                <div class="summary-label">Field Size</div>
                <div class="summary-value">${summary.field.fieldSize} acres</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Crop Type</div>
                <div class="summary-value">${summary.field.cropType}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Fertilizer</div>
                <div class="summary-value">${summary.fertilizer.type}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Application Rate</div>
                <div class="summary-value">${summary.fertilizer.applicationRate} lbs/ac</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Method</div>
                <div class="summary-value">${this.getMethodName(summary.method)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Equipment</div>
                <div class="summary-value">${summary.equipment.type}</div>
            </div>
        `;
    }

    displayCostBreakdown(summary) {
        const container = document.getElementById('costBreakdown');
        if (!container) return;

        const totalFertilizer = summary.field.fieldSize * summary.fertilizer.applicationRate;
        const totalCost = totalFertilizer * summary.fertilizer.costPerUnit;
        const applicationCost = summary.field.fieldSize * 35; // Estimated application cost
        const totalApplicationCost = totalCost + applicationCost;

        container.innerHTML = `
            <div class="cost-item">
                <div class="cost-label">Fertilizer Cost</div>
                <div class="cost-value">$${totalCost.toFixed(2)}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Application Cost</div>
                <div class="cost-value">$${applicationCost.toFixed(2)}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Total Cost</div>
                <div class="cost-value">$${totalApplicationCost.toFixed(2)}</div>
            </div>
            <div class="cost-item">
                <div class="cost-label">Cost per Acre</div>
                <div class="cost-value">$${(totalApplicationCost / summary.field.fieldSize).toFixed(2)}</div>
            </div>
        `;
    }

    // Application Monitoring
    startApplication() {
        this.isApplicationActive = true;
        this.applicationStartTime = new Date();
        
        document.getElementById('startBtn').disabled = true;
        document.getElementById('pauseBtn').disabled = false;
        document.getElementById('stopBtn').disabled = false;

        this.startMonitoring();
        this.showToast('Application started!', 'success');
        this.sendPushNotification('Application Started', 'Fertilizer application has begun.');
    }

    pauseApplication() {
        this.isApplicationActive = false;
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;

        this.stopMonitoring();
        this.showToast('Application paused.', 'warning');
    }

    stopApplication() {
        this.isApplicationActive = false;
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('pauseBtn').disabled = true;
        document.getElementById('stopBtn').disabled = true;

        this.stopMonitoring();
        this.showToast('Application stopped.', 'info');
        this.sendPushNotification('Application Completed', 'Fertilizer application has been completed.');
    }

    startMonitoring() {
        this.monitoringInterval = setInterval(() => {
            this.updateMonitoringStats();
        }, 1000);
    }

    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }

    updateMonitoringStats() {
        const container = document.getElementById('monitoringStats');
        if (!container) return;

        const elapsedTime = Math.floor((new Date() - this.applicationStartTime) / 1000);
        const hours = Math.floor(elapsedTime / 3600);
        const minutes = Math.floor((elapsedTime % 3600) / 60);
        const seconds = elapsedTime % 60;

        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // Simulate application progress
        const progress = Math.min((elapsedTime / 3600) * 100, 100); // Assume 1 hour for full application
        const acresCompleted = (progress / 100) * this.fieldData.fieldSize;

        container.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${timeString}</div>
                <div class="stat-label">Elapsed Time</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${progress.toFixed(1)}%</div>
                <div class="stat-label">Progress</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${acresCompleted.toFixed(1)}</div>
                <div class="stat-label">Acres Completed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${(this.fieldData.fieldSize - acresCompleted).toFixed(1)}</div>
                <div class="stat-label">Acres Remaining</div>
            </div>
        `;
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
        const indicator = document.getElementById('offlineIndicator');
        
        if (indicator) {
            if (this.isOnline) {
                indicator.classList.remove('show');
            } else {
                indicator.classList.add('show');
            }
        }
    }

    sendPushNotification(title, body) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: '/static/images/icon-192x192.png',
                badge: '/static/images/badge-72x72.png'
            });
        }
    }

    async saveApplicationPlan() {
        const applicationPlan = {
            fieldData: this.fieldData,
            fertilizerData: this.fertilizerData,
            method: this.selectedMethod,
            equipmentData: this.equipmentData,
            fieldPhotos: this.fieldPhotos,
            voiceNotes: this.voiceNotes,
            timestamp: new Date().toISOString()
        };

        try {
            if (this.isOnline) {
                const response = await fetch('/api/v1/fertilizer-application/save-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(applicationPlan)
                });

                if (response.ok) {
                    this.showToast('Application plan saved successfully!', 'success');
                } else {
                    throw new Error('Failed to save plan');
                }
            } else {
                // Store offline
                this.offlineData.push(applicationPlan);
                localStorage.setItem('fertilizer_offline_data', JSON.stringify(this.offlineData));
                this.showToast('Application plan saved offline. Will sync when online.', 'info');
            }
        } catch (error) {
            console.error('Error saving application plan:', error);
            this.showToast('Unable to save application plan. Please try again.', 'error');
        }
    }

    showFieldMap() {
        // TODO: Implement field map display
        this.showToast('Field map feature coming soon!', 'info');
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
    mobileFertilizerManager.getCurrentLocation();
}

function selectLocation(address) {
    mobileFertilizerManager.selectLocation(address);
}

function selectMethod(methodId) {
    mobileFertilizerManager.selectMethod(methodId);
}

function toggleFertilizerForm(button) {
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
}

function nextStep(stepNumber) {
    mobileFertilizerManager.nextStep(stepNumber);
}

function prevStep(stepNumber) {
    mobileFertilizerManager.prevStep(stepNumber);
}

function showStep(stepNumber) {
    mobileFertilizerManager.showStep(stepNumber);
}

function takeFieldPhoto() {
    mobileFertilizerManager.takeFieldPhoto();
}

function recordVoiceNote() {
    mobileFertilizerManager.recordVoiceNote();
}

function capturePhoto() {
    mobileFertilizerManager.capturePhoto();
}

function closeCamera() {
    mobileFertilizerManager.closeCamera();
}

function startApplication() {
    mobileFertilizerManager.startApplication();
}

function pauseApplication() {
    mobileFertilizerManager.pauseApplication();
}

function stopApplication() {
    mobileFertilizerManager.stopApplication();
}

function saveApplicationPlan() {
    mobileFertilizerManager.saveApplicationPlan();
}

function showFieldMap() {
    mobileFertilizerManager.showFieldMap();
}

// Initialize the mobile fertilizer application manager when the page loads
let mobileFertilizerManager;
document.addEventListener('DOMContentLoaded', () => {
    mobileFertilizerManager = new MobileFertilizerApplicationManager();
});