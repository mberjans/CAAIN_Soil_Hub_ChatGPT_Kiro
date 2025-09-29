/**
 * Mobile Camera-Based Crop Identification
 * 
 * Provides camera functionality for crop identification and analysis
 * using computer vision and machine learning capabilities.
 */

class MobileCameraCropIdentification {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.context = null;
        this.stream = null;
        this.isCapturing = false;
        this.capturedImage = null;
        this.analysisResults = null;
        this.deviceIntegration = null;
        
        this.init();
    }

    async init() {
        this.deviceIntegration = new MobileDeviceIntegration();
        
        // Wait for device integration to initialize
        await new Promise(resolve => {
            const checkInit = () => {
                if (this.deviceIntegration && this.deviceIntegration.isFeatureAvailable('camera')) {
                    resolve();
                } else {
                    setTimeout(checkInit, 100);
                }
            };
            checkInit();
        });

        this.setupCameraElements();
        this.setupEventListeners();
    }

    /**
     * Setup camera elements
     */
    setupCameraElements() {
        this.video = document.getElementById('videoElement');
        this.canvas = document.getElementById('canvasElement');
        
        if (this.canvas) {
            this.context = this.canvas.getContext('2d');
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Camera capture button
        const captureBtn = document.getElementById('captureBtn');
        if (captureBtn) {
            captureBtn.addEventListener('click', this.capturePhoto.bind(this));
        }

        // Retake button
        const retakeBtn = document.getElementById('retakeBtn');
        if (retakeBtn) {
            retakeBtn.addEventListener('click', this.retakePhoto.bind(this));
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', this.analyzePhoto.bind(this));
        }

        // Camera preview tap
        const cameraPreview = document.getElementById('cameraPreview');
        if (cameraPreview) {
            cameraPreview.addEventListener('click', this.startCamera.bind(this));
        }

        // Device orientation changes
        document.addEventListener('mobileDevice:orientationChange', this.handleOrientationChange.bind(this));
    }

    /**
     * Start camera
     */
    async startCamera() {
        if (!this.deviceIntegration.hasPermission('camera')) {
            this.showError('Camera permission is required for crop identification');
            return;
        }

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment', // Use back camera
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                    aspectRatio: { ideal: 16/9 }
                }
            });

            if (this.video) {
                this.video.srcObject = this.stream;
                this.video.play();
                
                // Show video element
                this.video.style.display = 'block';
                
                // Hide camera preview
                const cameraPreview = document.getElementById('cameraPreview');
                if (cameraPreview) {
                    cameraPreview.style.display = 'none';
                }
            }

            this.showSuccess('Camera started successfully');
        } catch (error) {
            console.error('Error starting camera:', error);
            this.showError('Failed to start camera: ' + error.message);
        }
    }

    /**
     * Stop camera
     */
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.video) {
            this.video.srcObject = null;
            this.video.style.display = 'none';
        }

        // Show camera preview
        const cameraPreview = document.getElementById('cameraPreview');
        if (cameraPreview) {
            cameraPreview.style.display = 'flex';
        }
    }

    /**
     * Capture photo
     */
    async capturePhoto() {
        if (!this.video || !this.canvas || !this.context) {
            this.showError('Camera elements not available');
            return;
        }

        try {
            // Set canvas dimensions to match video
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;

            // Draw video frame to canvas
            this.context.drawImage(this.video, 0, 0);

            // Get image data
            this.capturedImage = this.canvas.toDataURL('image/jpeg', 0.8);

            // Stop camera
            this.stopCamera();

            // Show captured image
            this.showCapturedImage();

            // Show retake and analyze buttons
            this.showActionButtons();

            this.showSuccess('Photo captured successfully');
        } catch (error) {
            console.error('Error capturing photo:', error);
            this.showError('Failed to capture photo: ' + error.message);
        }
    }

    /**
     * Show captured image
     */
    showCapturedImage() {
        const cameraPreview = document.getElementById('cameraPreview');
        if (cameraPreview && this.capturedImage) {
            cameraPreview.innerHTML = `
                <img src="${this.capturedImage}" alt="Captured crop photo" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">
            `;
            cameraPreview.style.display = 'flex';
        }
    }

    /**
     * Show action buttons
     */
    showActionButtons() {
        const retakeBtn = document.getElementById('retakeBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const captureBtn = document.getElementById('captureBtn');

        if (retakeBtn) retakeBtn.style.display = 'inline-block';
        if (analyzeBtn) analyzeBtn.style.display = 'inline-block';
        if (captureBtn) captureBtn.style.display = 'none';
    }

    /**
     * Hide action buttons
     */
    hideActionButtons() {
        const retakeBtn = document.getElementById('retakeBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const captureBtn = document.getElementById('captureBtn');

        if (retakeBtn) retakeBtn.style.display = 'none';
        if (analyzeBtn) analyzeBtn.style.display = 'none';
        if (captureBtn) captureBtn.style.display = 'inline-block';
    }

    /**
     * Retake photo
     */
    retakePhoto() {
        this.capturedImage = null;
        this.analysisResults = null;
        
        // Reset camera preview
        const cameraPreview = document.getElementById('cameraPreview');
        if (cameraPreview) {
            cameraPreview.innerHTML = `
                <i class="fas fa-camera fa-3x text-muted mb-2"></i>
                <p class="text-muted mb-0">Tap to capture crop photo</p>
            `;
        }

        this.hideActionButtons();
        this.startCamera();
    }

    /**
     * Analyze photo for crop identification
     */
    async analyzePhoto() {
        if (!this.capturedImage) {
            this.showError('No photo to analyze');
            return;
        }

        try {
            this.showLoading('Analyzing crop photo...');

            // Convert data URL to blob
            const blob = await this.dataURLToBlob(this.capturedImage);

            // Create form data
            const formData = new FormData();
            formData.append('image', blob, 'crop-photo.jpg');
            formData.append('analysis_type', 'crop_identification');

            // Send to analysis API
            const response = await fetch('/api/v1/crop-analysis/identify', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            this.analysisResults = await response.json();
            this.displayAnalysisResults();

            this.showSuccess('Crop analysis completed');
        } catch (error) {
            console.error('Error analyzing photo:', error);
            this.showError('Failed to analyze photo: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Display analysis results
     */
    displayAnalysisResults() {
        if (!this.analysisResults) return;

        const resultsContainer = document.getElementById('analysisResults');
        if (!resultsContainer) return;

        const { crop_type, confidence, characteristics, recommendations } = this.analysisResults;

        resultsContainer.innerHTML = `
            <div class="analysis-result">
                <h5><i class="fas fa-seedling"></i> Crop Identification</h5>
                <div class="result-item">
                    <strong>Crop Type:</strong> ${crop_type || 'Unknown'}
                </div>
                <div class="result-item">
                    <strong>Confidence:</strong> ${Math.round((confidence || 0) * 100)}%
                </div>
                
                ${characteristics ? `
                    <h6 class="mt-3">Characteristics:</h6>
                    <ul class="characteristics-list">
                        ${characteristics.map(char => `<li>${char}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${recommendations ? `
                    <h6 class="mt-3">Recommendations:</h6>
                    <ul class="recommendations-list">
                        ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>
        `;

        resultsContainer.style.display = 'block';
    }

    /**
     * Convert data URL to blob
     */
    dataURLToBlob(dataURL) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob(resolve, 'image/jpeg', 0.8);
            };
            
            img.src = dataURL;
        });
    }

    /**
     * Handle device orientation changes
     */
    handleOrientationChange(event) {
        const { orientation } = event.detail;
        
        // Adjust camera constraints based on orientation
        if (orientation.includes('landscape')) {
            this.adjustCameraForLandscape();
        } else {
            this.adjustCameraForPortrait();
        }
    }

    /**
     * Adjust camera for landscape orientation
     */
    adjustCameraForLandscape() {
        // Adjust video element for landscape
        if (this.video) {
            this.video.style.width = '100%';
            this.video.style.height = 'auto';
        }
    }

    /**
     * Adjust camera for portrait orientation
     */
    adjustCameraForPortrait() {
        // Adjust video element for portrait
        if (this.video) {
            this.video.style.width = '100%';
            this.video.style.height = '100%';
        }
    }

    /**
     * Show loading indicator
     */
    showLoading(message = 'Loading...') {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.innerHTML = `
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>${message}</span>
                </div>
            `;
            loadingElement.style.display = 'block';
        }
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        if (this.deviceIntegration) {
            this.deviceIntegration.showNotification(message, { type: 'success' });
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.deviceIntegration) {
            this.deviceIntegration.showNotification(message, { type: 'error' });
        }
    }

    /**
     * Get captured image data
     */
    getCapturedImage() {
        return this.capturedImage;
    }

    /**
     * Get analysis results
     */
    getAnalysisResults() {
        return this.analysisResults;
    }

    /**
     * Clear all data
     */
    clearData() {
        this.capturedImage = null;
        this.analysisResults = null;
        this.stopCamera();
        this.hideActionButtons();
        
        // Reset camera preview
        const cameraPreview = document.getElementById('cameraPreview');
        if (cameraPreview) {
            cameraPreview.innerHTML = `
                <i class="fas fa-camera fa-3x text-muted mb-2"></i>
                <p class="text-muted mb-0">Tap to capture crop photo</p>
            `;
        }

        // Hide results
        const resultsContainer = document.getElementById('analysisResults');
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
    }
}

// Export for use in other modules
window.MobileCameraCropIdentification = MobileCameraCropIdentification;

// CSS for camera interface
const cameraStyles = `
.camera-container {
    position: relative;
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.camera-preview {
    width: 100%;
    height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    cursor: pointer;
    transition: all 0.3s ease;
}

.camera-preview:hover {
    background: linear-gradient(135deg, #e9ecef, #dee2e6);
}

.camera-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

#videoElement {
    width: 100%;
    height: 300px;
    object-fit: cover;
}

#canvasElement {
    display: none;
}

.action-button {
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    margin: 0.25rem;
}

.btn-camera {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
}

.btn-retake {
    background: linear-gradient(135deg, #ffc107, #fd7e14);
    color: white;
}

.btn-analyze {
    background: linear-gradient(135deg, #007bff, #6610f2);
    color: white;
}

.action-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.loading-spinner {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    color: #6c757d;
}

.loading-spinner i {
    margin-right: 0.5rem;
    font-size: 1.2rem;
}

.analysis-result {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.result-item {
    margin-bottom: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f8f9fa;
}

.characteristics-list,
.recommendations-list {
    margin: 0;
    padding-left: 1.5rem;
}

.characteristics-list li,
.recommendations-list li {
    margin-bottom: 0.5rem;
    color: #495057;
}

@media (max-width: 768px) {
    .camera-preview {
        height: 250px;
    }
    
    #videoElement {
        height: 250px;
    }
    
    .action-button {
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
    }
}
`;

// Inject styles
const cameraStyleSheet = document.createElement('style');
cameraStyleSheet.textContent = cameraStyles;
document.head.appendChild(cameraStyleSheet);