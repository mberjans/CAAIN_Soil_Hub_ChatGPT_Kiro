/**
 * Enhanced Mobile Location Input JavaScript
 * TICKET-008_farm-location-input-11.2: Add mobile-specific location features and capabilities
 * 
 * Features:
 * - Advanced GPS tracking and field boundary recording
 * - Camera integration for field photos with geotagging
 * - Voice notes functionality for field annotations
 * - Offline field mapping with background synchronization
 * - Enhanced mobile UX with swipe gestures and touch optimization
 */

class EnhancedMobileLocationInput extends MobileLocationInput {
    constructor() {
        super();
        this.fieldBoundaryPoints = [];
        this.isRecordingBoundary = false;
        this.boundaryRecordingId = null;
        this.cameraStream = null;
        this.voiceRecorder = null;
        this.isRecordingVoice = false;
        this.fieldPhotos = [];
        this.voiceNotes = [];
        this.offlineFieldData = [];
        this.backgroundSync = null;
        
        this.initEnhancedFeatures();
    }

    initEnhancedFeatures() {
        this.setupAdvancedGPSTracking();
        this.setupCameraIntegration();
        this.setupVoiceNotes();
        this.setupOfflineFieldMapping();
        this.setupBackgroundSync();
        this.setupEnhancedMobileUX();
    }

    // Advanced GPS Tracking and Field Boundary Recording
    setupAdvancedGPSTracking() {
        this.gpsTrackingOptions = {
            enableHighAccuracy: true,
            timeout: 30000,
            maximumAge: 1000,
            distanceFilter: 1 // Update every 1 meter
        };

        // Add boundary recording controls to GPS method
        this.addBoundaryRecordingControls();
    }

    addBoundaryRecordingControls() {
        const gpsContent = document.querySelector('#gps-method .method-content');
        if (gpsContent) {
            const boundaryControls = document.createElement('div');
            boundaryControls.className = 'boundary-recording-controls';
            boundaryControls.innerHTML = `
                <div class="boundary-section">
                    <h6><i class="fas fa-map-marked-alt me-2"></i>Field Boundary Recording</h6>
                    <div class="boundary-controls">
                        <button class="btn btn-outline-primary btn-sm" id="startBoundaryRecording" onclick="enhancedMobileLocationInput.startBoundaryRecording()">
                            <i class="fas fa-play me-1"></i>Start Recording
                        </button>
                        <button class="btn btn-outline-danger btn-sm" id="stopBoundaryRecording" onclick="enhancedMobileLocationInput.stopBoundaryRecording()" style="display: none;">
                            <i class="fas fa-stop me-1"></i>Stop Recording
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="enhancedMobileLocationInput.clearBoundaryPoints()">
                            <i class="fas fa-trash me-1"></i>Clear Points
                        </button>
                    </div>
                    <div class="boundary-status" id="boundaryStatus">
                        <div class="status-indicator">
                            <i class="fas fa-circle text-muted"></i>
                            <span>Ready to record field boundary</span>
                        </div>
                    </div>
                    <div class="boundary-stats" id="boundaryStats" style="display: none;">
                        <div class="stat-item">
                            <span class="stat-label">Points:</span>
                            <span class="stat-value" id="boundaryPointCount">0</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Area:</span>
                            <span class="stat-value" id="boundaryArea">0 acres</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Perimeter:</span>
                            <span class="stat-value" id="boundaryPerimeter">0 m</span>
                        </div>
                    </div>
                </div>
            `;
            gpsContent.appendChild(boundaryControls);
        }
    }

    async startBoundaryRecording() {
        if (!navigator.geolocation) {
            this.showError('GPS is not available on this device');
            return;
        }

        this.isRecordingBoundary = true;
        this.fieldBoundaryPoints = [];
        
        // Update UI
        document.getElementById('startBoundaryRecording').style.display = 'none';
        document.getElementById('stopBoundaryRecording').style.display = 'inline-block';
        
        const statusElement = document.getElementById('boundaryStatus');
        statusElement.innerHTML = `
            <div class="status-indicator">
                <i class="fas fa-circle text-success fa-pulse"></i>
                <span>Recording field boundary... Walk around your field</span>
            </div>
        `;

        // Start continuous GPS tracking
        this.boundaryRecordingId = navigator.geolocation.watchPosition(
            (position) => this.addBoundaryPoint(position),
            (error) => this.handleBoundaryRecordingError(error),
            this.gpsTrackingOptions
        );

        this.showSuccess('Started recording field boundary. Walk around your field perimeter.');
    }

    addBoundaryPoint(position) {
        const point = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date(),
            altitude: position.coords.altitude || null
        };

        this.fieldBoundaryPoints.push(point);
        this.updateBoundaryStats();
        this.updateMapWithBoundary();
    }

    updateBoundaryStats() {
        const pointCount = this.fieldBoundaryPoints.length;
        document.getElementById('boundaryPointCount').textContent = pointCount;
        
        if (pointCount > 2) {
            const area = this.calculatePolygonArea(this.fieldBoundaryPoints);
            const perimeter = this.calculatePolygonPerimeter(this.fieldBoundaryPoints);
            
            document.getElementById('boundaryArea').textContent = `${area.toFixed(2)} acres`;
            document.getElementById('boundaryPerimeter').textContent = `${perimeter.toFixed(0)} m`;
            document.getElementById('boundaryStats').style.display = 'block';
        }
    }

    calculatePolygonArea(points) {
        if (points.length < 3) return 0;
        
        // Use the shoelace formula for polygon area calculation
        let area = 0;
        const n = points.length;
        
        for (let i = 0; i < n; i++) {
            const j = (i + 1) % n;
            area += points[i].longitude * points[j].latitude;
            area -= points[j].longitude * points[i].latitude;
        }
        
        area = Math.abs(area) / 2;
        
        // Convert from square degrees to acres (approximate)
        // This is a simplified conversion - in production, use proper projection
        const metersPerDegree = 111320; // Approximate meters per degree at equator
        const squareMeters = area * Math.pow(metersPerDegree, 2);
        const acres = squareMeters / 4046.86; // Convert square meters to acres
        
        return acres;
    }

    calculatePolygonPerimeter(points) {
        if (points.length < 2) return 0;
        
        let perimeter = 0;
        for (let i = 0; i < points.length; i++) {
            const j = (i + 1) % points.length;
            const distance = this.calculateDistance(
                points[i].latitude, points[i].longitude,
                points[j].latitude, points[j].longitude
            );
            perimeter += distance;
        }
        
        return perimeter;
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000; // Earth's radius in meters
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    updateMapWithBoundary() {
        if (!this.mobileMap || this.fieldBoundaryPoints.length < 2) return;

        // Remove existing boundary polygon
        if (this.boundaryPolygon) {
            this.mobileMap.removeLayer(this.boundaryPolygon);
        }

        // Create new boundary polygon
        const latLngs = this.fieldBoundaryPoints.map(point => [point.latitude, point.longitude]);
        
        this.boundaryPolygon = L.polygon(latLngs, {
            color: '#28a745',
            weight: 3,
            opacity: 0.8,
            fillColor: '#28a745',
            fillOpacity: 0.2
        }).addTo(this.mobileMap);

        // Add boundary points as markers
        this.fieldBoundaryPoints.forEach((point, index) => {
            L.marker([point.latitude, point.longitude], {
                icon: L.divIcon({
                    className: 'boundary-point-marker',
                    html: `<div class="boundary-point">${index + 1}</div>`,
                    iconSize: [20, 20]
                })
            }).addTo(this.mobileMap);
        });
    }

    stopBoundaryRecording() {
        if (this.boundaryRecordingId) {
            navigator.geolocation.clearWatch(this.boundaryRecordingId);
            this.boundaryRecordingId = null;
        }

        this.isRecordingBoundary = false;
        
        // Update UI
        document.getElementById('startBoundaryRecording').style.display = 'inline-block';
        document.getElementById('stopBoundaryRecording').style.display = 'none';
        
        const statusElement = document.getElementById('boundaryStatus');
        statusElement.innerHTML = `
            <div class="status-indicator">
                <i class="fas fa-check-circle text-success"></i>
                <span>Boundary recording completed (${this.fieldBoundaryPoints.length} points)</span>
            </div>
        `;

        // Save boundary data
        this.saveBoundaryData();
        
        this.showSuccess(`Field boundary recorded with ${this.fieldBoundaryPoints.length} points`);
    }

    clearBoundaryPoints() {
        this.fieldBoundaryPoints = [];
        
        if (this.boundaryPolygon) {
            this.mobileMap.removeLayer(this.boundaryPolygon);
            this.boundaryPolygon = null;
        }

        // Clear boundary markers
        this.mobileMap.eachLayer(layer => {
            if (layer.options && layer.options.icon && layer.options.icon.options && layer.options.icon.options.className === 'boundary-point-marker') {
                this.mobileMap.removeLayer(layer);
            }
        });

        document.getElementById('boundaryStats').style.display = 'none';
        document.getElementById('boundaryPointCount').textContent = '0';
        
        this.showSuccess('Boundary points cleared');
    }

    saveBoundaryData() {
        const boundaryData = {
            id: Date.now(),
            points: this.fieldBoundaryPoints,
            area: this.calculatePolygonArea(this.fieldBoundaryPoints),
            perimeter: this.calculatePolygonPerimeter(this.fieldBoundaryPoints),
            timestamp: new Date(),
            fieldName: document.getElementById('addressInput').value || 'Unnamed Field'
        };

        // Save to local storage
        const savedBoundaries = JSON.parse(localStorage.getItem('fieldBoundaries') || '[]');
        savedBoundaries.push(boundaryData);
        localStorage.setItem('fieldBoundaries', JSON.stringify(savedBoundaries));

        // Save to offline data for sync
        this.offlineFieldData.push({
            type: 'boundary',
            data: boundaryData
        });
    }

    // Camera Integration for Field Photos with Geotagging
    setupCameraIntegration() {
        this.addCameraControls();
    }

    addCameraControls() {
        const mapContent = document.querySelector('#map-method .method-content');
        if (mapContent) {
            const cameraSection = document.createElement('div');
            cameraSection.className = 'camera-integration-section';
            cameraSection.innerHTML = `
                <div class="camera-section">
                    <h6><i class="fas fa-camera me-2"></i>Field Photos</h6>
                    <div class="camera-controls">
                        <button class="btn btn-outline-primary btn-sm" onclick="enhancedMobileLocationInput.openCamera()">
                            <i class="fas fa-camera me-1"></i>Take Field Photo
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="enhancedMobileLocationInput.viewFieldPhotos()">
                            <i class="fas fa-images me-1"></i>View Photos (${this.fieldPhotos.length})
                        </button>
                    </div>
                    <div class="camera-preview" id="cameraPreview" style="display: none;">
                        <video id="cameraVideo" autoplay playsinline style="width: 100%; max-width: 300px;"></video>
                        <div class="camera-controls-overlay">
                            <button class="btn btn-success" onclick="enhancedMobileLocationInput.capturePhoto()">
                                <i class="fas fa-camera"></i>
                            </button>
                            <button class="btn btn-secondary" onclick="enhancedMobileLocationInput.closeCamera()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="field-photos-list" id="fieldPhotosList" style="display: none;">
                        <!-- Field photos will be displayed here -->
                    </div>
                </div>
            `;
            mapContent.appendChild(cameraSection);
        }
    }

    async openCamera() {
        try {
            this.cameraStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' } // Use back camera
            });

            const video = document.getElementById('cameraVideo');
            video.srcObject = this.cameraStream;
            document.getElementById('cameraPreview').style.display = 'block';

            this.showSuccess('Camera opened. Position your device to capture the field.');
        } catch (error) {
            console.error('Camera error:', error);
            this.showError('Unable to access camera. Please check permissions.');
        }
    }

    async capturePhoto() {
        const video = document.getElementById('cameraVideo');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);

        // Convert to blob
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));

        // Create photo with geotagging
        const photo = {
            id: Date.now(),
            blob: blob,
            timestamp: new Date(),
            location: this.currentLocation,
            fieldId: document.getElementById('addressInput').value || 'Unnamed Field',
            geotagged: true,
            accuracy: this.currentLocation ? this.currentLocation.accuracy : null
        };

        this.fieldPhotos.push(photo);
        this.saveFieldPhoto(photo);
        this.closeCamera();
        
        this.showSuccess('Field photo captured and geotagged successfully!');
    }

    closeCamera() {
        if (this.cameraStream) {
            this.cameraStream.getTracks().forEach(track => track.stop());
            this.cameraStream = null;
        }
        
        document.getElementById('cameraPreview').style.display = 'none';
    }

    saveFieldPhoto(photo) {
        // Save to local storage
        const savedPhotos = JSON.parse(localStorage.getItem('fieldPhotos') || '[]');
        savedPhotos.push(photo);
        localStorage.setItem('fieldPhotos', JSON.stringify(savedPhotos));

        // Save to offline data for sync
        this.offlineFieldData.push({
            type: 'photo',
            data: photo
        });
    }

    viewFieldPhotos() {
        const photosList = document.getElementById('fieldPhotosList');
        if (photosList.style.display === 'none') {
            this.displayFieldPhotos();
            photosList.style.display = 'block';
        } else {
            photosList.style.display = 'none';
        }
    }

    displayFieldPhotos() {
        const photosList = document.getElementById('fieldPhotosList');
        photosList.innerHTML = '';

        this.fieldPhotos.forEach(photo => {
            const photoElement = document.createElement('div');
            photoElement.className = 'field-photo-item';
            photoElement.innerHTML = `
                <div class="photo-info">
                    <div class="photo-timestamp">${photo.timestamp.toLocaleString()}</div>
                    <div class="photo-location">
                        ${photo.location ? `${photo.location.latitude.toFixed(6)}, ${photo.location.longitude.toFixed(6)}` : 'No location'}
                    </div>
                    <div class="photo-accuracy">
                        ${photo.accuracy ? `Accuracy: ${Math.round(photo.accuracy)}m` : 'No accuracy data'}
                    </div>
                </div>
                <div class="photo-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="enhancedMobileLocationInput.viewPhoto(${photo.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="enhancedMobileLocationInput.deletePhoto(${photo.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            photosList.appendChild(photoElement);
        });
    }

    // Voice Notes Functionality
    setupVoiceNotes() {
        this.addVoiceNotesControls();
    }

    addVoiceNotesControls() {
        const manualContent = document.querySelector('#manual-method .method-content');
        if (manualContent) {
            const voiceSection = document.createElement('div');
            voiceSection.className = 'voice-notes-section';
            voiceSection.innerHTML = `
                <div class="voice-section">
                    <h6><i class="fas fa-microphone me-2"></i>Voice Notes</h6>
                    <div class="voice-controls">
                        <button class="btn btn-outline-primary btn-sm" id="voiceRecordBtn" onclick="enhancedMobileLocationInput.toggleVoiceRecording()">
                            <i class="fas fa-microphone me-1"></i>Record Note
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="enhancedMobileLocationInput.viewVoiceNotes()">
                            <i class="fas fa-list me-1"></i>View Notes (${this.voiceNotes.length})
                        </button>
                    </div>
                    <div class="voice-recording-status" id="voiceRecordingStatus" style="display: none;">
                        <div class="recording-indicator">
                            <i class="fas fa-circle text-danger fa-pulse"></i>
                            <span>Recording voice note...</span>
                        </div>
                        <div class="recording-timer" id="recordingTimer">00:00</div>
                    </div>
                    <div class="voice-notes-list" id="voiceNotesList" style="display: none;">
                        <!-- Voice notes will be displayed here -->
                    </div>
                </div>
            `;
            manualContent.appendChild(voiceSection);
        }
    }

    async toggleVoiceRecording() {
        if (this.isRecordingVoice) {
            this.stopVoiceRecording();
        } else {
            await this.startVoiceRecording();
        }
    }

    async startVoiceRecording() {
        try {
            this.voiceRecorder = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(this.voiceRecorder);
            this.recordingChunks = [];
            this.recordingStartTime = Date.now();

            this.mediaRecorder.ondataavailable = (event) => {
                this.recordingChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.recordingChunks, { type: 'audio/webm' });
                this.saveVoiceNote(blob);
            };

            this.mediaRecorder.start();
            this.isRecordingVoice = true;

            // Update UI
            document.getElementById('voiceRecordBtn').innerHTML = '<i class="fas fa-stop me-1"></i>Stop Recording';
            document.getElementById('voiceRecordingStatus').style.display = 'block';
            
            // Start recording timer
            this.recordingTimer = setInterval(() => {
                const elapsed = Date.now() - this.recordingStartTime;
                const minutes = Math.floor(elapsed / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);
                document.getElementById('recordingTimer').textContent = 
                    `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }, 1000);

            this.showSuccess('Started recording voice note');
        } catch (error) {
            console.error('Voice recording error:', error);
            this.showError('Unable to access microphone. Please check permissions.');
        }
    }

    stopVoiceRecording() {
        if (this.mediaRecorder && this.isRecordingVoice) {
            this.mediaRecorder.stop();
            this.voiceRecorder.getTracks().forEach(track => track.stop());
            
            this.isRecordingVoice = false;
            clearInterval(this.recordingTimer);

            // Update UI
            document.getElementById('voiceRecordBtn').innerHTML = '<i class="fas fa-microphone me-1"></i>Record Note';
            document.getElementById('voiceRecordingStatus').style.display = 'none';
            
            this.showSuccess('Voice note recorded successfully');
        }
    }

    saveVoiceNote(blob) {
        const voiceNote = {
            id: Date.now(),
            blob: blob,
            timestamp: new Date(),
            duration: this.getRecordingDuration(),
            fieldId: document.getElementById('addressInput').value || 'Unnamed Field',
            location: this.currentLocation
        };

        this.voiceNotes.push(voiceNote);
        
        // Save to local storage
        const savedNotes = JSON.parse(localStorage.getItem('voiceNotes') || '[]');
        savedNotes.push(voiceNote);
        localStorage.setItem('voiceNotes', JSON.stringify(savedNotes));

        // Save to offline data for sync
        this.offlineFieldData.push({
            type: 'voice_note',
            data: voiceNote
        });
    }

    getRecordingDuration() {
        if (this.recordingStartTime) {
            const elapsed = Date.now() - this.recordingStartTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        return '0:00';
    }

    viewVoiceNotes() {
        const notesList = document.getElementById('voiceNotesList');
        if (notesList.style.display === 'none') {
            this.displayVoiceNotes();
            notesList.style.display = 'block';
        } else {
            notesList.style.display = 'none';
        }
    }

    displayVoiceNotes() {
        const notesList = document.getElementById('voiceNotesList');
        notesList.innerHTML = '';

        this.voiceNotes.forEach(note => {
            const noteElement = document.createElement('div');
            noteElement.className = 'voice-note-item';
            noteElement.innerHTML = `
                <div class="note-info">
                    <div class="note-timestamp">${note.timestamp.toLocaleString()}</div>
                    <div class="note-duration">Duration: ${note.duration}</div>
                    <div class="note-location">
                        ${note.location ? `${note.location.latitude.toFixed(6)}, ${note.location.longitude.toFixed(6)}` : 'No location'}
                    </div>
                </div>
                <div class="note-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="enhancedMobileLocationInput.playVoiceNote(${note.id})">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="enhancedMobileLocationInput.deleteVoiceNote(${note.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            notesList.appendChild(noteElement);
        });
    }

    // Offline Field Mapping with Background Synchronization
    setupOfflineFieldMapping() {
        this.setupOfflineStorage();
        this.setupBackgroundSync();
    }

    setupOfflineStorage() {
        // Initialize IndexedDB for offline storage
        if ('indexedDB' in window) {
            this.initIndexedDB();
        } else {
            console.warn('IndexedDB not supported, using localStorage fallback');
        }
    }

    async initIndexedDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('FieldMappingDB', 1);
            
            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create object stores
                if (!db.objectStoreNames.contains('fieldBoundaries')) {
                    db.createObjectStore('fieldBoundaries', { keyPath: 'id' });
                }
                
                if (!db.objectStoreNames.contains('fieldPhotos')) {
                    db.createObjectStore('fieldPhotos', { keyPath: 'id' });
                }
                
                if (!db.objectStoreNames.contains('voiceNotes')) {
                    db.createObjectStore('voiceNotes', { keyPath: 'id' });
                }
                
                if (!db.objectStoreNames.contains('syncQueue')) {
                    db.createObjectStore('syncQueue', { keyPath: 'id' });
                }
            };
        });
    }

    setupBackgroundSync() {
        // Register service worker for background sync
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            navigator.serviceWorker.register('/static/sw.js').then(registration => {
                this.serviceWorkerRegistration = registration;
            });
        }

        // Setup periodic sync
        this.setupPeriodicSync();
    }

    setupPeriodicSync() {
        // Sync every 5 minutes when online
        setInterval(() => {
            if (navigator.onLine) {
                this.syncOfflineData();
            }
        }, 5 * 60 * 1000);
    }

    async syncOfflineData() {
        if (!navigator.onLine || this.offlineFieldData.length === 0) return;

        try {
            for (const item of this.offlineFieldData) {
                await this.syncDataItem(item);
            }
            
            this.offlineFieldData = [];
            this.showSuccess('Offline data synchronized successfully');
        } catch (error) {
            console.error('Sync error:', error);
            this.showError('Failed to sync offline data');
        }
    }

    async syncDataItem(item) {
        const endpoint = this.getSyncEndpoint(item.type);
        if (!endpoint) return;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(item.data)
        });

        if (!response.ok) {
            throw new Error(`Sync failed for ${item.type}`);
        }
    }

    getSyncEndpoint(type) {
        const endpoints = {
            'boundary': '/api/v1/fields/boundaries',
            'photo': '/api/v1/fields/photos',
            'voice_note': '/api/v1/fields/voice-notes'
        };
        return endpoints[type];
    }

    // Enhanced Mobile UX Features
    setupEnhancedMobileUX() {
        this.setupSwipeGestures();
        this.setupTouchOptimization();
        this.setupHapticFeedback();
    }

    setupSwipeGestures() {
        // Enhanced swipe gestures for method switching
        let startX = 0;
        let startY = 0;
        let isScrolling = false;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isScrolling = false;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;

            const diffX = Math.abs(e.touches[0].clientX - startX);
            const diffY = Math.abs(e.touches[0].clientY - startY);

            if (diffY > diffX) {
                isScrolling = true;
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (!startX || !startY || isScrolling) return;

            const diffX = startX - e.changedTouches[0].clientX;
            const threshold = 50;

            if (Math.abs(diffX) > threshold) {
                if (diffX > 0) {
                    this.switchToNextMethod();
                    this.provideHapticFeedback('success');
                } else {
                    this.switchToPreviousMethod();
                    this.provideHapticFeedback('success');
                }
            }

            startX = 0;
            startY = 0;
            isScrolling = false;
        }, { passive: true });
    }

    setupTouchOptimization() {
        // Optimize touch targets for mobile
        const touchTargets = document.querySelectorAll('.btn, .method-header, .history-item');
        touchTargets.forEach(target => {
            target.style.minHeight = '44px';
            target.style.minWidth = '44px';
        });

        // Add touch feedback
        document.addEventListener('touchstart', (e) => {
            if (e.target.classList.contains('btn') || 
                e.target.classList.contains('method-header') ||
                e.target.classList.contains('history-item')) {
                e.target.style.transform = 'scale(0.95)';
                e.target.style.transition = 'transform 0.1s ease';
            }
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (e.target.classList.contains('btn') || 
                e.target.classList.contains('method-header') ||
                e.target.classList.contains('history-item')) {
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 150);
            }
        }, { passive: true });
    }

    setupHapticFeedback() {
        // Check if device supports haptic feedback
        this.hapticSupported = 'vibrate' in navigator;
    }

    provideHapticFeedback(type) {
        if (!this.hapticSupported) return;

        const patterns = {
            'success': [50],
            'error': [100, 50, 100],
            'warning': [100],
            'selection': [25]
        };

        navigator.vibrate(patterns[type] || [25]);
    }

    // Override parent methods to add enhanced functionality
    async saveLocation() {
        // Add enhanced location data
        if (this.currentLocation) {
            this.currentLocation.fieldBoundary = this.fieldBoundaryPoints;
            this.currentLocation.fieldPhotos = this.fieldPhotos;
            this.currentLocation.voiceNotes = this.voiceNotes;
            this.currentLocation.offlineData = this.offlineFieldData;
        }

        await super.saveLocation();
        
        // Provide haptic feedback
        this.provideHapticFeedback('success');
    }

    // Utility methods
    showSuccess(message) {
        super.showSuccess(message);
        this.provideHapticFeedback('success');
    }

    showError(message) {
        super.showError(message);
        this.provideHapticFeedback('error');
    }
}

// Initialize enhanced mobile location input
let enhancedMobileLocationInput;

function initializeEnhancedMobileFeatures() {
    enhancedMobileLocationInput = new EnhancedMobileLocationInput();
}

// Global functions for HTML onclick handlers
function startBoundaryRecording() {
    enhancedMobileLocationInput.startBoundaryRecording();
}

function stopBoundaryRecording() {
    enhancedMobileLocationInput.stopBoundaryRecording();
}

function clearBoundaryPoints() {
    enhancedMobileLocationInput.clearBoundaryPoints();
}

function openCamera() {
    enhancedMobileLocationInput.openCamera();
}

function capturePhoto() {
    enhancedMobileLocationInput.capturePhoto();
}

function closeCamera() {
    enhancedMobileLocationInput.closeCamera();
}

function viewFieldPhotos() {
    enhancedMobileLocationInput.viewFieldPhotos();
}

function toggleVoiceRecording() {
    enhancedMobileLocationInput.toggleVoiceRecording();
}

function viewVoiceNotes() {
    enhancedMobileLocationInput.viewVoiceNotes();
}