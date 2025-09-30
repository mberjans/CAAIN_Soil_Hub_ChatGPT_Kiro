/**
 * Enhanced Mobile Location Input JavaScript
 * TICKET-008_farm-location-input-11.1 - Comprehensive Mobile-Responsive Location Interface
 */

class EnhancedMobileLocationInput {
    constructor() {
        this.currentMapType = 'street';
        this.hapticEnabled = false;
        this.gestureRecognizer = null;
        this.offlineStorage = null;
        this.performanceMonitor = null;
        this.accessibilityManager = null;
        this.init();
    }

    init() {
        this.setupEnhancedFeatures();
        this.setupHapticFeedback();
        this.setupKeyboardOptimization();
        this.setupGestureRecognition();
        this.setupOfflineStorage();
        this.setupPerformanceMonitoring();
        this.setupAccessibilityFeatures();
        this.setupProgressiveWebApp();
    }

    setupEnhancedFeatures() {
        this.setupGPSButtonEnhancements();
        this.setupMapControlEnhancements();
        this.setupInputValidationEnhancements();
    }

    setupGPSButtonEnhancements() {
        const gpsButton = document.querySelector('.gps-button-enhanced');
        if (gpsButton) {
            gpsButton.addEventListener('click', () => {
                this.showGPSButtonLoading();
            });
        }
    }

    showGPSButtonLoading() {
        const gpsButton = document.querySelector('.gps-button-enhanced');
        if (gpsButton) {
            gpsButton.classList.add('loading');
            setTimeout(() => {
                gpsButton.classList.remove('loading');
            }, 3000);
        }
    }

    setupMapControlEnhancements() {
        this.setupMapTypeSwitching();
    }

    setupMapTypeSwitching() {
        const mapTypeButtons = document.querySelectorAll('.map-type-btn');
        mapTypeButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const mapType = e.currentTarget.dataset.type;
                this.setMapType(mapType);
            });
        });
    }

    setMapType(mapType) {
        this.currentMapType = mapType;
        document.querySelectorAll('.map-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${mapType}"]`).classList.add('active');
        this.triggerHapticFeedback('light');
    }

    setupInputValidationEnhancements() {
        this.setupCoordinateValidation();
    }

    setupCoordinateValidation() {
        const latInput = document.getElementById('latitudeInput');
        const lngInput = document.getElementById('longitudeInput');
        const validationDiv = document.getElementById('coordinateValidation');
        
        if (latInput && lngInput && validationDiv) {
            const validateCoordinates = () => {
                const lat = parseFloat(latInput.value);
                const lng = parseFloat(lngInput.value);
                
                if (!isNaN(lat) && !isNaN(lng)) {
                    const isValid = this.validateCoordinateRange(lat, lng);
                    this.showCoordinateValidation(isValid);
                } else {
                    validationDiv.style.display = 'none';
                }
            };
            
            latInput.addEventListener('input', validateCoordinates);
            lngInput.addEventListener('input', validateCoordinates);
        }
    }

    validateCoordinateRange(lat, lng) {
        return lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
    }

    showCoordinateValidation(isValid) {
        const validationDiv = document.getElementById('coordinateValidation');
        const statusDiv = validationDiv.querySelector('.validation-status');
        
        if (validationDiv && statusDiv) {
            validationDiv.style.display = 'block';
            
            if (isValid) {
                statusDiv.innerHTML = '<i class="fas fa-check-circle text-success"></i><span>Valid coordinates</span>';
                validationDiv.className = 'coordinate-validation success-state';
            } else {
                statusDiv.innerHTML = '<i class="fas fa-exclamation-triangle text-warning"></i><span>Invalid coordinate range</span>';
                validationDiv.className = 'coordinate-validation error-state';
            }
        }
    }

    setupHapticFeedback() {
        if ('vibrate' in navigator) {
            this.hapticEnabled = true;
        }
    }

    triggerHapticFeedback(type) {
        if (!this.hapticEnabled) return;
        
        const patterns = {
            light: [10],
            medium: [20],
            heavy: [30],
            success: [10, 10, 10],
            error: [50, 50, 50]
        };
        
        const pattern = patterns[type] || patterns.light;
        navigator.vibrate(pattern);
    }

    setupKeyboardOptimization() {
        const inputs = document.querySelectorAll('.mobile-input');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                this.optimizeMobileKeyboard(input);
            });
        });
    }

    optimizeMobileKeyboard(input) {
        if (input.type === 'number') {
            input.setAttribute('inputmode', 'decimal');
        } else if (input.type === 'text') {
            input.setAttribute('inputmode', 'text');
        }
        input.style.fontSize = '16px';
    }

    setupGestureRecognition() {
        this.gestureRecognizer = new MobileGestureRecognizer();
        this.gestureRecognizer.init();
    }

    setupOfflineStorage() {
        this.offlineStorage = new OfflineLocationStorage();
        this.offlineStorage.init();
    }

    setupPerformanceMonitoring() {
        this.performanceMonitor = new MobilePerformanceMonitor();
        this.performanceMonitor.init();
    }

    setupAccessibilityFeatures() {
        this.accessibilityManager = new MobileAccessibilityManager();
        this.accessibilityManager.init();
    }

    setupProgressiveWebApp() {
        this.setupServiceWorker();
        this.setupAppManifest();
        this.setupInstallPrompt();
    }

    setupServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    setupAppManifest() {
        // Check if app is already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            document.body.classList.add('pwa-installed');
        }
    }

    setupInstallPrompt() {
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            this.showInstallButton(deferredPrompt);
        });

        window.addEventListener('appinstalled', () => {
            console.log('PWA was installed');
            document.body.classList.add('pwa-installed');
        });
    }

    showInstallButton(deferredPrompt) {
        const installButton = document.createElement('button');
        installButton.className = 'btn btn-primary mobile-btn-enhanced';
        installButton.innerHTML = '<i class="fas fa-download me-2"></i>Install App';
        installButton.onclick = () => this.installApp(deferredPrompt);
        
        const actionButtons = document.querySelector('.action-buttons-enhanced');
        if (actionButtons) {
            actionButtons.appendChild(installButton);
        }
    }

    installApp(deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the install prompt');
            }
            deferredPrompt = null;
        });
    }
}

class MobileGestureRecognizer {
    constructor() {
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.touchEndX = 0;
        this.touchEndY = 0;
        this.minSwipeDistance = 50;
        this.maxSwipeTime = 300;
        this.touchStartTime = 0;
    }

    init() {
        this.setupSwipeGestures();
        this.setupPinchGestures();
        this.setupLongPressGestures();
    }

    setupSwipeGestures() {
        const gestureAreas = document.querySelectorAll('.gesture-area');
        
        gestureAreas.forEach(area => {
            area.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: true });
            area.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: true });
        });
    }

    handleTouchStart(e) {
        this.touchStartTime = Date.now();
        this.touchStartX = e.touches[0].clientX;
        this.touchStartY = e.touches[0].clientY;
    }

    handleTouchEnd(e) {
        this.touchEndX = e.changedTouches[0].clientX;
        this.touchEndY = e.changedTouches[0].clientY;
        
        const touchDuration = Date.now() - this.touchStartTime;
        const swipeDistanceX = this.touchEndX - this.touchStartX;
        const swipeDistanceY = this.touchEndY - this.touchStartY;
        
        if (touchDuration < this.maxSwipeTime) {
            if (Math.abs(swipeDistanceX) > this.minSwipeDistance) {
                if (swipeDistanceX > 0) {
                    this.handleSwipeRight();
                } else {
                    this.handleSwipeLeft();
                }
            }
            
            if (Math.abs(swipeDistanceY) > this.minSwipeDistance) {
                if (swipeDistanceY > 0) {
                    this.handleSwipeDown();
                } else {
                    this.handleSwipeUp();
                }
            }
        }
    }

    handleSwipeLeft() {
        this.showSwipeIndicator('left');
        this.switchToNextMethod();
        this.triggerHapticFeedback('light');
    }

    handleSwipeRight() {
        this.showSwipeIndicator('right');
        this.switchToPreviousMethod();
        this.triggerHapticFeedback('light');
    }

    handleSwipeUp() {
        // Could be used for quick actions or navigation
        this.triggerHapticFeedback('light');
    }

    handleSwipeDown() {
        // Could be used for closing modals or going back
        this.triggerHapticFeedback('light');
    }

    showSwipeIndicator(direction) {
        const indicator = document.querySelector(`.swipe-indicator.${direction}`);
        if (indicator) {
            indicator.classList.add('active');
            setTimeout(() => {
                indicator.classList.remove('active');
            }, 300);
        }
    }

    switchToNextMethod() {
        const methods = ['gps', 'map', 'manual'];
        const currentMethod = document.querySelector('.method-card.active').id.replace('-method', '');
        const currentIndex = methods.indexOf(currentMethod);
        const nextIndex = (currentIndex + 1) % methods.length;
        this.switchMethod(methods[nextIndex]);
    }

    switchToPreviousMethod() {
        const methods = ['gps', 'map', 'manual'];
        const currentMethod = document.querySelector('.method-card.active').id.replace('-method', '');
        const currentIndex = methods.indexOf(currentMethod);
        const prevIndex = currentIndex === 0 ? methods.length - 1 : currentIndex - 1;
        this.switchMethod(methods[prevIndex]);
    }

    switchMethod(method) {
        // Remove active class from all methods
        document.querySelectorAll('.method-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Add active class to selected method
        const methodCard = document.getElementById(`${method}-method`);
        if (methodCard) {
            methodCard.classList.add('active');
        }
    }

    setupPinchGestures() {
        // Pinch gestures for map zoom
        const mapContainer = document.getElementById('mobileMap');
        if (mapContainer) {
            let initialDistance = 0;
            let initialZoom = 0;
            
            mapContainer.addEventListener('touchstart', (e) => {
                if (e.touches.length === 2) {
                    initialDistance = this.getDistance(e.touches[0], e.touches[1]);
                    initialZoom = window.mobileMap ? window.mobileMap.getZoom() : 10;
                }
            }, { passive: true });
            
            mapContainer.addEventListener('touchmove', (e) => {
                if (e.touches.length === 2) {
                    e.preventDefault();
                    const currentDistance = this.getDistance(e.touches[0], e.touches[1]);
                    const scale = currentDistance / initialDistance;
                    const newZoom = initialZoom + Math.log2(scale);
                    
                    if (window.mobileMap) {
                        window.mobileMap.setZoom(Math.max(1, Math.min(18, newZoom)));
                    }
                }
            }, { passive: false });
        }
    }

    getDistance(touch1, touch2) {
        const dx = touch1.clientX - touch2.clientX;
        const dy = touch1.clientY - touch2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    setupLongPressGestures() {
        let longPressTimer = null;
        const longPressDelay = 500;
        
        document.addEventListener('touchstart', (e) => {
            longPressTimer = setTimeout(() => {
                this.handleLongPress(e);
            }, longPressDelay);
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (longPressTimer) {
                clearTimeout(longPressTimer);
                longPressTimer = null;
            }
        }, { passive: true });
        
        document.addEventListener('touchmove', () => {
            if (longPressTimer) {
                clearTimeout(longPressTimer);
                longPressTimer = null;
            }
        }, { passive: true });
    }

    handleLongPress(e) {
        this.triggerHapticFeedback('medium');
        this.showContextMenu(e);
    }

    showContextMenu(e) {
        // Could show context menu for location actions
        console.log('Long press detected at:', e.touches[0].clientX, e.touches[0].clientY);
    }

    triggerHapticFeedback(type) {
        if ('vibrate' in navigator) {
            const patterns = {
                light: [10],
                medium: [20],
                heavy: [30],
                success: [10, 10, 10],
                error: [50, 50, 50]
            };
            
            const pattern = patterns[type] || patterns.light;
            navigator.vibrate(pattern);
        }
    }
}

class OfflineLocationStorage {
    constructor() {
        this.storageKey = 'mobile_location_data';
        this.maxStorageSize = 5 * 1024 * 1024; // 5MB
    }

    init() {
        this.setupStorageMonitoring();
        this.loadStoredData();
    }

    setupStorageMonitoring() {
        window.addEventListener('online', () => {
            this.handleOnlineStatus();
        });
        
        window.addEventListener('offline', () => {
            this.handleOfflineStatus();
        });
    }

    handleOnlineStatus() {
        document.getElementById('offlineIndicator').classList.remove('show');
        this.syncStoredData();
    }

    handleOfflineStatus() {
        document.getElementById('offlineIndicator').classList.add('show');
    }

    storeLocationData(locationData) {
        try {
            const existingData = this.getStoredData();
            existingData.locations = existingData.locations || [];
            
            // Add timestamp and unique ID
            locationData.id = Date.now().toString();
            locationData.timestamp = new Date().toISOString();
            locationData.synced = false;
            
            existingData.locations.unshift(locationData);
            
            // Keep only last 50 locations
            if (existingData.locations.length > 50) {
                existingData.locations = existingData.locations.slice(0, 50);
            }
            
            localStorage.setItem(this.storageKey, JSON.stringify(existingData));
            this.updateStorageUsage();
        } catch (error) {
            console.error('Failed to store location data:', error);
        }
    }

    getStoredData() {
        try {
            const data = localStorage.getItem(this.storageKey);
            return data ? JSON.parse(data) : { locations: [] };
        } catch (error) {
            console.error('Failed to get stored data:', error);
            return { locations: [] };
        }
    }

    loadStoredData() {
        const data = this.getStoredData();
        this.populateLocationHistory(data.locations);
    }

    populateLocationHistory(locations) {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;
        
        historyList.innerHTML = '';
        
        locations.forEach(location => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="history-content">
                    <div class="history-coords">
                        ${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}
                    </div>
                    <div class="history-time">
                        ${new Date(location.timestamp).toLocaleString()}
                    </div>
                    ${location.synced ? '' : '<div class="sync-indicator"><i class="fas fa-cloud-upload-alt"></i></div>'}
                </div>
                <div class="history-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="useHistoryLocation('${location.id}')">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteHistoryLocation('${location.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            historyList.appendChild(historyItem);
        });
    }

    syncStoredData() {
        const data = this.getStoredData();
        const unsyncedLocations = data.locations.filter(location => !location.synced);
        
        unsyncedLocations.forEach(location => {
            this.syncLocationToServer(location);
        });
    }

    async syncLocationToServer(location) {
        try {
            const response = await fetch('/api/v1/locations/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(location)
            });
            
            if (response.ok) {
                location.synced = true;
                this.updateStoredLocation(location);
            }
        } catch (error) {
            console.error('Failed to sync location:', error);
        }
    }

    updateStoredLocation(updatedLocation) {
        const data = this.getStoredData();
        const index = data.locations.findIndex(loc => loc.id === updatedLocation.id);
        if (index !== -1) {
            data.locations[index] = updatedLocation;
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        }
    }

    updateStorageUsage() {
        const data = localStorage.getItem(this.storageKey);
        const size = new Blob([data]).size;
        
        if (size > this.maxStorageSize) {
            this.cleanupOldData();
        }
    }

    cleanupOldData() {
        const data = this.getStoredData();
        data.locations = data.locations.slice(0, 25); // Keep only 25 most recent
        localStorage.setItem(this.storageKey, JSON.stringify(data));
    }
}

class MobilePerformanceMonitor {
    constructor() {
        this.metrics = {
            loadTime: 0,
            interactionDelay: 0,
            memoryUsage: 0
        };
    }

    init() {
        this.measureLoadTime();
        this.setupPerformanceObserver();
        this.monitorMemoryUsage();
    }

    measureLoadTime() {
        window.addEventListener('load', () => {
            this.metrics.loadTime = performance.now();
            this.reportMetrics();
        });
    }

    setupPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'measure') {
                        this.metrics.interactionDelay = entry.duration;
                    }
                }
            });
            
            observer.observe({ entryTypes: ['measure'] });
        }
    }

    monitorMemoryUsage() {
        if ('memory' in performance) {
            setInterval(() => {
                this.metrics.memoryUsage = performance.memory.usedJSHeapSize;
            }, 5000);
        }
    }

    reportMetrics() {
        // Could send metrics to analytics service
        console.log('Performance metrics:', this.metrics);
    }
}

class MobileAccessibilityManager {
    constructor() {
        this.announcer = null;
        this.focusManager = null;
    }

    init() {
        this.setupScreenReader();
        this.setupFocusManagement();
        this.setupKeyboardNavigation();
        this.setupHighContrast();
    }

    setupScreenReader() {
        this.announcer = document.createElement('div');
        this.announcer.setAttribute('aria-live', 'polite');
        this.announcer.setAttribute('aria-atomic', 'true');
        this.announcer.className = 'sr-only-mobile';
        document.body.appendChild(this.announcer);
    }

    announce(message) {
        if (this.announcer) {
            this.announcer.textContent = message;
        }
    }

    setupFocusManagement() {
        // Trap focus within modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                this.trapFocus(modal);
            });
        });
    }

    trapFocus(element) {
        const focusableElements = element.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        element.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        lastElement.focus();
                        e.preventDefault();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        firstElement.focus();
                        e.preventDefault();
                    }
                }
            }
        });
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Escape key to close modals
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal.show');
                if (openModal) {
                    const modal = bootstrap.Modal.getInstance(openModal);
                    if (modal) {
                        modal.hide();
                    }
                }
            }
            
            // Arrow keys for method switching
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                if (e.target.classList.contains('method-card')) {
                    e.preventDefault();
                    if (e.key === 'ArrowLeft') {
                        this.switchToPreviousMethod();
                    } else {
                        this.switchToNextMethod();
                    }
                }
            }
        });
    }

    switchToPreviousMethod() {
        // Implementation similar to gesture recognizer
        const methods = ['gps', 'map', 'manual'];
        const currentMethod = document.querySelector('.method-card.active').id.replace('-method', '');
        const currentIndex = methods.indexOf(currentMethod);
        const prevIndex = currentIndex === 0 ? methods.length - 1 : currentIndex - 1;
        this.switchMethod(methods[prevIndex]);
    }

    switchToNextMethod() {
        const methods = ['gps', 'map', 'manual'];
        const currentMethod = document.querySelector('.method-card.active').id.replace('-method', '');
        const currentIndex = methods.indexOf(currentMethod);
        const nextIndex = (currentIndex + 1) % methods.length;
        this.switchMethod(methods[nextIndex]);
    }

    switchMethod(method) {
        document.querySelectorAll('.method-card').forEach(card => {
            card.classList.remove('active');
        });
        
        const methodCard = document.getElementById(`${method}-method`);
        if (methodCard) {
            methodCard.classList.add('active');
            methodCard.focus();
            this.announce(`Switched to ${method} method`);
        }
    }

    setupHighContrast() {
        // Check for high contrast preference
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.body.classList.add('high-contrast');
        }
        
        // Listen for changes
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            if (e.matches) {
                document.body.classList.add('high-contrast');
            } else {
                document.body.classList.remove('high-contrast');
            }
        });
    }
}

function initializeEnhancedMobileFeatures() {
    window.enhancedMobileLocationInput = new EnhancedMobileLocationInput();
}

// Global functions for HTML onclick handlers
function useHistoryLocation(locationId) {
    if (window.enhancedMobileLocationInput && window.enhancedMobileLocationInput.offlineStorage) {
        const data = window.enhancedMobileLocationInput.offlineStorage.getStoredData();
        const location = data.locations.find(loc => loc.id === locationId);
        if (location) {
            // Use the location data
            document.getElementById('latitudeInput').value = location.latitude;
            document.getElementById('longitudeInput').value = location.longitude;
            window.enhancedMobileLocationInput.accessibilityManager.announce('Location loaded from history');
        }
    }
}

function deleteHistoryLocation(locationId) {
    if (window.enhancedMobileLocationInput && window.enhancedMobileLocationInput.offlineStorage) {
        const data = window.enhancedMobileLocationInput.offlineStorage.getStoredData();
        data.locations = data.locations.filter(loc => loc.id !== locationId);
        localStorage.setItem('mobile_location_data', JSON.stringify(data));
        window.enhancedMobileLocationInput.offlineStorage.loadStoredData();
        window.enhancedMobileLocationInput.accessibilityManager.announce('Location deleted from history');
    }
}
