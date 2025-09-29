// CAAIN Soil Hub - Mobile Drought Management JavaScript
// Mobile-optimized drought management system with offline capability, GPS, camera, and push notifications

class MobileDroughtManagementSystem {
    constructor() {
        this.apiBaseUrl = '/api/v1/drought';
        this.currentAssessment = null;
        this.currentStep = 1;
        this.totalSteps = 3;
        this.fields = [];
        this.photos = [];
        this.voiceNotes = [];
        this.isOnline = navigator.onLine;
        this.offlineData = this.loadOfflineData();
        this.mediaRecorder = null;
        this.recordingChunks = [];
        this.isRecording = false;
        this.currentLocation = null;
        this.notificationPermission = 'default';
        
        // Initialize the system
        this.init();
    }

    init() {
        this.bindEventListeners();
        this.setupOfflineDetection();
        this.setupServiceWorker();
        this.requestLocationPermission();
        this.requestNotificationPermission();
        this.loadInitialData();
        this.setupPushNotifications();
        this.updateOnlineStatus();
    }

    bindEventListeners() {
        // Online/offline detection
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // App visibility changes
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());

        // Touch events for better mobile interaction
        this.setupTouchEvents();

        // Form validation
        this.setupFormValidation();
    }

    setupOfflineDetection() {
        // Check online status periodically
        setInterval(() => {
            this.updateOnlineStatus();
        }, 30000); // Check every 30 seconds
    }

    updateOnlineStatus() {
        const wasOnline = this.isOnline;
        this.isOnline = navigator.onLine;
        
        if (wasOnline !== this.isOnline) {
            if (this.isOnline) {
                this.handleOnline();
            } else {
                this.handleOffline();
            }
        }
    }

    handleOnline() {
        this.isOnline = true;
        this.hideOfflineIndicator();
        this.syncOfflineData();
        this.showMessage('Connection restored - syncing data', 'success');
    }

    handleOffline() {
        this.isOnline = false;
        this.showOfflineIndicator();
        this.showMessage('You\'re offline - data will sync when connection is restored', 'warning');
    }

    showOfflineIndicator() {
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.classList.add('show');
        }
    }

    hideOfflineIndicator() {
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.classList.remove('show');
        }
    }

    // Service Worker Setup
    async setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw-drought.js');
                console.log('Service Worker registered:', registration);
                
                // Listen for service worker updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showMessage('App update available - refresh to update', 'info');
                        }
                    });
                });
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        }
    }

    // GPS and Location Services
    async requestLocationPermission() {
        if ('geolocation' in navigator) {
            try {
                const position = await this.getCurrentPosition();
                this.currentLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
                console.log('Current location:', this.currentLocation);
            } catch (error) {
                console.log('Location access denied or failed:', error);
            }
        }
    }

    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                resolve,
                reject,
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 minutes
                }
            );
        });
    }

    // Push Notifications
    async requestNotificationPermission() {
        if ('Notification' in window) {
            this.notificationPermission = await Notification.requestPermission();
            console.log('Notification permission:', this.notificationPermission);
        }
    }

    async setupPushNotifications() {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            try {
                const registration = await navigator.serviceWorker.ready;
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
                });
                
                // Send subscription to server
                await this.apiCall('/notifications/subscribe', 'POST', {
                    subscription: subscription
                });
            } catch (error) {
                console.error('Push notification setup failed:', error);
            }
        }
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    // Camera Integration
    async takePhoto() {
        try {
            // Check if camera is available
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                this.showMessage('Camera not available on this device', 'error');
                return;
            }

            // Request camera permission
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment', // Use back camera
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } 
            });

            // Create video element for camera preview
            const video = document.createElement('video');
            video.srcObject = stream;
            video.play();

            // Create modal for camera interface
            this.showCameraModal(video, stream);
        } catch (error) {
            console.error('Camera access failed:', error);
            this.showMessage('Camera access denied or failed', 'error');
        }
    }

    showCameraModal(video, stream) {
        const modal = document.createElement('div');
        modal.className = 'camera-modal';
        modal.innerHTML = `
            <div class="camera-modal-content">
                <div class="camera-header">
                    <h5>Take Field Photo</h5>
                    <button class="btn-close" onclick="mobileDroughtSystem.closeCameraModal()">&times;</button>
                </div>
                <div class="camera-preview-container">
                    <video id="cameraVideo" autoplay playsinline></video>
                </div>
                <div class="camera-controls">
                    <button class="btn btn-primary" onclick="mobileDroughtSystem.capturePhoto()">
                        <i class="fas fa-camera"></i> Capture
                    </button>
                    <button class="btn btn-secondary" onclick="mobileDroughtSystem.closeCameraModal()">
                        Cancel
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        
        // Set video source
        const videoElement = modal.querySelector('#cameraVideo');
        videoElement.srcObject = stream;
        
        // Store stream for cleanup
        modal.stream = stream;
    }

    async capturePhoto() {
        const video = document.querySelector('#cameraVideo');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);
        
        // Convert to blob
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
        
        // Create photo object
        const photo = {
            id: Date.now(),
            blob: blob,
            timestamp: new Date(),
            location: this.currentLocation,
            fieldId: document.getElementById('fieldSelect')?.value || 'unknown'
        };
        
        this.photos.push(photo);
        this.displayPhotos();
        this.saveOfflineData();
        
        this.closeCameraModal();
        this.showMessage('Photo captured successfully', 'success');
    }

    closeCameraModal() {
        const modal = document.querySelector('.camera-modal');
        if (modal) {
            // Stop camera stream
            if (modal.stream) {
                modal.stream.getTracks().forEach(track => track.stop());
            }
            modal.remove();
        }
    }

    displayPhotos() {
        const photoList = document.getElementById('photoList');
        if (!photoList) return;

        photoList.innerHTML = this.photos.map(photo => `
            <div class="photo-item">
                <img src="${URL.createObjectURL(photo.blob)}" alt="Field photo">
                <div class="photo-info">
                    <div class="photo-name">Field Photo</div>
                    <div class="photo-time">${photo.timestamp.toLocaleString()}</div>
                </div>
                <button class="btn btn-sm btn-outline-danger" onclick="mobileDroughtSystem.removePhoto(${photo.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');
    }

    removePhoto(photoId) {
        this.photos = this.photos.filter(photo => photo.id !== photoId);
        this.displayPhotos();
        this.saveOfflineData();
    }

    // Voice Notes
    async toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.recordingChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.recordingChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.recordingChunks, { type: 'audio/webm' });
                this.saveVoiceNote(blob);
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateRecordingUI();
        } catch (error) {
            console.error('Microphone access failed:', error);
            this.showMessage('Microphone access denied or failed', 'error');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateRecordingUI();
        }
    }

    updateRecordingUI() {
        const voiceBtn = document.getElementById('voiceBtn');
        const status = document.getElementById('recordingStatus');
        const timer = document.getElementById('recordingTimer');

        if (this.isRecording) {
            voiceBtn.classList.add('recording');
            status.style.display = 'none';
            timer.style.display = 'block';
            this.startRecordingTimer();
        } else {
            voiceBtn.classList.remove('recording');
            status.style.display = 'block';
            timer.style.display = 'none';
            this.stopRecordingTimer();
        }
    }

    startRecordingTimer() {
        let seconds = 0;
        this.recordingInterval = setInterval(() => {
            seconds++;
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            document.getElementById('recordingTimer').textContent = 
                `Recording... ${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopRecordingTimer() {
        if (this.recordingInterval) {
            clearInterval(this.recordingInterval);
            this.recordingInterval = null;
        }
    }

    saveVoiceNote(blob) {
        const voiceNote = {
            id: Date.now(),
            blob: blob,
            timestamp: new Date(),
            duration: this.getRecordingDuration(),
            fieldId: document.getElementById('fieldSelect')?.value || 'unknown'
        };

        this.voiceNotes.push(voiceNote);
        this.displayVoiceNotes();
        this.saveOfflineData();
        this.showMessage('Voice note recorded successfully', 'success');
    }

    getRecordingDuration() {
        // Calculate duration based on recording chunks
        return this.recordingChunks.length > 0 ? 'Unknown' : '0:00';
    }

    displayVoiceNotes() {
        const voiceNotesList = document.getElementById('voiceNotesList');
        if (!voiceNotesList) return;

        voiceNotesList.innerHTML = this.voiceNotes.map(note => `
            <div class="voice-note-item">
                <i class="fas fa-microphone text-primary"></i>
                <div class="note-info">
                    <div class="note-duration">Voice Note</div>
                    <div class="note-time">${note.timestamp.toLocaleString()}</div>
                </div>
                <div class="note-controls">
                    <button class="btn btn-sm btn-outline-primary" onclick="mobileDroughtSystem.playVoiceNote(${note.id})">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="mobileDroughtSystem.removeVoiceNote(${note.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    playVoiceNote(noteId) {
        const note = this.voiceNotes.find(n => n.id === noteId);
        if (note) {
            const audio = new Audio(URL.createObjectURL(note.blob));
            audio.play();
        }
    }

    removeVoiceNote(noteId) {
        this.voiceNotes = this.voiceNotes.filter(note => note.id !== noteId);
        this.displayVoiceNotes();
        this.saveOfflineData();
    }

    // Assessment Wizard
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
                this.showMessage(`Please fill in all required fields`, 'error');
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
                stepElement.classList.remove('active');
            }
        }

        // Show current step
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.add('active');
        }

        // Update step indicators
        document.querySelectorAll('.step-dot').forEach((dot, index) => {
            dot.classList.remove('active', 'completed');
            if (index + 1 < this.currentStep) {
                dot.classList.add('completed');
            } else if (index + 1 === this.currentStep) {
                dot.classList.add('active');
            }
        });

        // Update navigation buttons
        const prevButton = document.getElementById('prevStepBtn');
        const nextButton = document.getElementById('nextStepBtn');
        const submitButton = document.getElementById('submitBtn');

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

    async submitAssessment() {
        if (!this.validateCurrentStep()) {
            return;
        }

        const assessmentData = this.collectAssessmentData();
        
        try {
            this.showLoadingState('submitBtn');
            
            if (this.isOnline) {
                const assessment = await this.apiCall('/assessment', 'POST', assessmentData);
                this.currentAssessment = assessment;
                this.displayAssessmentResults(assessment);
                this.showMessage('Assessment completed successfully!', 'success');
            } else {
                // Save for offline sync
                this.saveOfflineAssessment(assessmentData);
                this.showMessage('Assessment saved offline - will sync when online', 'info');
            }
            
            this.showResults();
            
        } catch (error) {
            console.error('Assessment submission failed:', error);
            this.showMessage('Failed to complete assessment. Please try again.', 'error');
        } finally {
            this.hideLoadingState('submitBtn');
        }
    }

    collectAssessmentData() {
        return {
            field_id: document.getElementById('fieldSelect').value,
            assessment_type: document.getElementById('assessmentType').value,
            soil_moisture_level: document.getElementById('soilMoisture').value,
            crop_stage: document.getElementById('cropStage').value,
            weather_conditions: document.getElementById('weatherConditions').value,
            additional_notes: document.getElementById('additionalNotes').value,
            photos: this.photos.map(photo => ({
                id: photo.id,
                timestamp: photo.timestamp,
                location: photo.location,
                field_id: photo.fieldId
            })),
            voice_notes: this.voiceNotes.map(note => ({
                id: note.id,
                timestamp: note.timestamp,
                duration: note.duration,
                field_id: note.fieldId
            })),
            location: this.currentLocation,
            timestamp: new Date()
        };
    }

    displayAssessmentResults(assessment) {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        resultsSection.innerHTML = `
            <div class="results-section">
                <h5><i class="fas fa-chart-pie me-2"></i>Assessment Results</h5>
                
                <div class="result-card ${assessment.risk_level}">
                    <div class="result-title">Risk Level: ${assessment.risk_level.toUpperCase()}</div>
                    <div class="result-description">${assessment.risk_description}</div>
                    <div class="result-actions">
                        <button class="result-action-btn" onclick="mobileDroughtSystem.viewRecommendations()">
                            View Recommendations
                        </button>
                        <button class="result-action-btn secondary" onclick="mobileDroughtSystem.shareResults()">
                            Share Results
                        </button>
                    </div>
                </div>

                <div class="result-card">
                    <div class="result-title">Water Conservation Potential</div>
                    <div class="result-description">
                        Potential savings: ${assessment.water_savings} gallons/acre/year
                    </div>
                </div>

                <div class="result-card">
                    <div class="result-title">Recommended Actions</div>
                    <div class="result-description">
                        ${assessment.recommendations.map(rec => `• ${rec.practice_name}`).join('<br>')}
                    </div>
                </div>
            </div>
        `;
    }

    showResults() {
        document.getElementById('assessmentWizard').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
    }

    // Quick Actions
    async startQuickAssessment() {
        try {
            this.showLoadingState('quickAssessment');
            
            const quickData = {
                field_id: this.fields[0]?.id || 'default',
                assessment_type: 'quick',
                location: this.currentLocation,
                timestamp: new Date()
            };

            if (this.isOnline) {
                const assessment = await this.apiCall('/assess', 'POST', quickData);
                this.displayAssessmentResults(assessment);
            } else {
                this.saveOfflineAssessment(quickData);
                this.showMessage('Quick assessment saved offline', 'info');
            }
            
        } catch (error) {
            console.error('Quick assessment failed:', error);
            this.showMessage('Quick assessment failed', 'error');
        } finally {
            this.hideLoadingState('quickAssessment');
        }
    }

    showEmergencyProtocol() {
        this.showMessage('Emergency protocols will be displayed here', 'info');
        // Implement emergency protocol display
    }

    openMonitoring() {
        this.showMessage('Opening monitoring dashboard...', 'info');
        // Implement monitoring dashboard
    }

    generateReport() {
        this.showMessage('Generating report...', 'info');
        // Implement report generation
    }

    // Navigation
    showDashboard() {
        this.updateNavigation('dashboard');
        this.loadFieldStatusCards();
    }

    showAssessment() {
        this.updateNavigation('assessment');
        document.getElementById('assessmentWizard').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
    }

    showMonitoring() {
        this.updateNavigation('monitoring');
        this.showMessage('Monitoring dashboard will be implemented', 'info');
    }

    showPractices() {
        this.updateNavigation('practices');
        this.showMessage('Conservation practices will be displayed', 'info');
    }

    showSettings() {
        this.updateNavigation('settings');
        this.showMessage('Settings panel will be implemented', 'info');
    }

    updateNavigation(activeTab) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeItem = document.querySelector(`[onclick*="${activeTab}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    // Data Management
    async loadInitialData() {
        try {
            if (this.isOnline) {
                await this.loadFields();
                await this.loadFieldStatus();
            } else {
                this.loadOfflineFields();
            }
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    async loadFields() {
        try {
            const fields = await this.apiCall('/fields');
            this.fields = fields;
            this.populateFieldSelect();
        } catch (error) {
            console.error('Failed to load fields:', error);
        }
    }

    populateFieldSelect() {
        const fieldSelect = document.getElementById('fieldSelect');
        if (fieldSelect) {
            fieldSelect.innerHTML = '<option value="">Select Field</option>' +
                this.fields.map(field => `<option value="${field.id}">${field.name}</option>`).join('');
        }
    }

    async loadFieldStatus() {
        try {
            const statusData = await this.apiCall('/field-status');
            this.displayFieldStatusCards(statusData);
        } catch (error) {
            console.error('Failed to load field status:', error);
        }
    }

    displayFieldStatusCards(statusData) {
        const container = document.getElementById('fieldStatusCards');
        if (!container) return;

        container.innerHTML = statusData.map(field => `
            <div class="field-status-card ${field.risk_level}">
                <div class="field-header">
                    <div class="field-name">${field.name}</div>
                    <div class="field-moisture ${field.moisture_level}">${field.moisture_percent}%</div>
                </div>
                <div class="field-details">
                    <span>Risk: ${field.risk_level}</span>
                    <span>Last updated: ${new Date(field.last_updated).toLocaleString()}</span>
                </div>
            </div>
        `).join('');
    }

    loadFieldStatusCards() {
        // Load field status cards - implement based on your data structure
        const mockData = [
            { name: 'Field A', moisture_percent: 65, moisture_level: 'moderate', risk_level: 'moderate', last_updated: new Date() },
            { name: 'Field B', moisture_percent: 45, moisture_level: 'low', risk_level: 'high', last_updated: new Date() },
            { name: 'Field C', moisture_percent: 80, moisture_level: 'moderate', risk_level: 'low', last_updated: new Date() }
        ];
        
        this.displayFieldStatusCards(mockData);
    }

    // Offline Data Management
    loadOfflineData() {
        try {
            const data = localStorage.getItem('drought-offline-data');
            return data ? JSON.parse(data) : {
                assessments: [],
                fields: [],
                photos: [],
                voiceNotes: []
            };
        } catch (error) {
            console.error('Failed to load offline data:', error);
            return { assessments: [], fields: [], photos: [], voiceNotes: [] };
        }
    }

    saveOfflineData() {
        try {
            const data = {
                assessments: this.offlineData.assessments,
                fields: this.fields,
                photos: this.photos,
                voiceNotes: this.voiceNotes,
                lastSync: new Date()
            };
            localStorage.setItem('drought-offline-data', JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save offline data:', error);
        }
    }

    saveOfflineAssessment(assessmentData) {
        this.offlineData.assessments.push({
            ...assessmentData,
            id: Date.now(),
            synced: false
        });
        this.saveOfflineData();
    }

    async syncOfflineData() {
        if (!this.isOnline) return;

        try {
            // Sync assessments
            for (const assessment of this.offlineData.assessments) {
                if (!assessment.synced) {
                    await this.apiCall('/assessment', 'POST', assessment);
                    assessment.synced = true;
                }
            }

            // Sync photos
            for (const photo of this.photos) {
                await this.uploadPhoto(photo);
            }

            // Sync voice notes
            for (const note of this.voiceNotes) {
                await this.uploadVoiceNote(note);
            }

            this.saveOfflineData();
            this.showMessage('Offline data synced successfully', 'success');
        } catch (error) {
            console.error('Failed to sync offline data:', error);
            this.showMessage('Failed to sync some offline data', 'error');
        }
    }

    async uploadPhoto(photo) {
        const formData = new FormData();
        formData.append('photo', photo.blob);
        formData.append('metadata', JSON.stringify({
            field_id: photo.fieldId,
            location: photo.location,
            timestamp: photo.timestamp
        }));

        await fetch(`${this.apiBaseUrl}/photos`, {
            method: 'POST',
            body: formData
        });
    }

    async uploadVoiceNote(note) {
        const formData = new FormData();
        formData.append('audio', note.blob);
        formData.append('metadata', JSON.stringify({
            field_id: note.fieldId,
            duration: note.duration,
            timestamp: note.timestamp
        }));

        await fetch(`${this.apiBaseUrl}/voice-notes`, {
            method: 'POST',
            body: formData
        });
    }

    loadOfflineFields() {
        // Load fields from offline storage
        this.fields = this.offlineData.fields || [];
        this.populateFieldSelect();
    }

    // API Integration
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
            throw error;
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

    showMessage(message, type = 'info') {
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

    // Touch Events
    setupTouchEvents() {
        // Add touch feedback to interactive elements
        document.addEventListener('touchstart', (e) => {
            if (e.target.classList.contains('btn') || e.target.classList.contains('nav-item')) {
                e.target.style.transform = 'scale(0.95)';
            }
        });

        document.addEventListener('touchend', (e) => {
            if (e.target.classList.contains('btn') || e.target.classList.contains('nav-item')) {
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 150);
            }
        });
    }

    // Form Validation
    setupFormValidation() {
        // Real-time form validation
        document.addEventListener('input', (e) => {
            if (e.target.hasAttribute('required')) {
                this.validateField(e.target);
            }
        });
    }

    validateField(field) {
        const isValid = field.value.trim() !== '';
        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid);
    }

    // App Lifecycle
    handleVisibilityChange() {
        if (document.hidden) {
            // App is hidden - pause non-essential operations
            this.pauseNonEssentialOperations();
        } else {
            // App is visible - resume operations
            this.resumeOperations();
        }
    }

    pauseNonEssentialOperations() {
        // Pause real-time updates, etc.
        console.log('App hidden - pausing non-essential operations');
    }

    resumeOperations() {
        // Resume real-time updates, sync data, etc.
        console.log('App visible - resuming operations');
        if (this.isOnline) {
            this.syncOfflineData();
        }
    }

    // Utility Functions
    viewRecommendations() {
        this.showMessage('Recommendations will be displayed here', 'info');
    }

    shareResults() {
        if (navigator.share) {
            navigator.share({
                title: 'Drought Assessment Results',
                text: 'Check out my drought assessment results from CAAIN Soil Hub',
                url: window.location.href
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(window.location.href);
            this.showMessage('Link copied to clipboard', 'success');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Global instance for easy access
    window.mobileDroughtSystem = new MobileDroughtManagementSystem();
});