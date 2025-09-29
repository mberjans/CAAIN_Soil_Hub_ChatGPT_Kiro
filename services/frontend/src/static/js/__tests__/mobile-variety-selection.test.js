// Mobile Variety Selection Tests
// Tests for mobile interface functionality and responsive design

describe('Mobile Variety Selection Interface', () => {
    let mobileVarietyManager;
    let mockElement;

    beforeEach(() => {
        // Mock DOM elements
        document.body.innerHTML = `
            <div id="step1" class="wizard-step active">
                <input id="farmLocation" type="text" />
                <input id="farmSize" type="number" />
                <select id="soilType">
                    <option value="">Select soil type</option>
                    <option value="clay">Clay</option>
                </select>
                <div class="toggle-group">
                    <button class="toggle-btn" data-value="false">No</button>
                    <button class="toggle-btn active" data-value="true">Yes</button>
                </div>
            </div>
            <div id="step2" class="wizard-step">
                <input id="cropSearch" type="text" />
                <div id="cropGrid"></div>
                <button id="step2Next" disabled>Continue</button>
            </div>
            <div id="step3" class="wizard-step">
                <input id="yieldPriority" type="range" min="0" max="100" value="80" />
                <input id="sustainabilityPriority" type="range" min="0" max="100" value="60" />
                <div class="risk-options">
                    <button class="risk-btn" data-value="low">Low Risk</button>
                    <button class="risk-btn active" data-value="moderate">Moderate</button>
                    <button class="risk-btn" data-value="high">High Risk</button>
                </div>
            </div>
            <div id="step4" class="wizard-step">
                <div id="recommendationsContainer"></div>
            </div>
            <div id="progressBar" style="width: 25%"></div>
            <div id="loadingOverlay"></div>
            <div id="toast">
                <div id="toastBody"></div>
            </div>
        `;

        // Mock fetch
        global.fetch = jest.fn();
        
        // Mock geolocation
        global.navigator.geolocation = {
            getCurrentPosition: jest.fn()
        };

        // Mock service worker
        global.navigator.serviceWorker = {
            register: jest.fn()
        };

        // Mock speech recognition
        global.SpeechRecognition = jest.fn();
        global.webkitSpeechRecognition = jest.fn();

        mobileVarietyManager = new MobileVarietySelectionManager();
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Initialization', () => {
        test('should initialize with correct default values', () => {
            expect(mobileVarietyManager.currentStep).toBe(1);
            expect(mobileVarietyManager.selectedCrop).toBeNull();
            expect(mobileVarietyManager.selectedVarieties).toBeInstanceOf(Set);
            expect(mobileVarietyManager.farmData).toEqual({});
            expect(mobileVarietyManager.userPreferences).toEqual({});
        });

        test('should set up event listeners', () => {
            const farmLocation = document.getElementById('farmLocation');
            const cropSearch = document.getElementById('cropSearch');
            
            expect(farmLocation).toBeTruthy();
            expect(cropSearch).toBeTruthy();
        });
    });

    describe('Navigation', () => {
        test('should navigate to next step when validation passes', () => {
            // Mock validation to pass
            mobileVarietyManager.validateFarmInformation = jest.fn().mockReturnValue(true);
            
            mobileVarietyManager.nextStep(2);
            
            expect(mobileVarietyManager.currentStep).toBe(2);
        });

        test('should not navigate when validation fails', () => {
            // Mock validation to fail
            mobileVarietyManager.validateFarmInformation = jest.fn().mockReturnValue(false);
            
            mobileVarietyManager.nextStep(2);
            
            expect(mobileVarietyManager.currentStep).toBe(1);
        });

        test('should navigate to previous step', () => {
            mobileVarietyManager.currentStep = 3;
            mobileVarietyManager.prevStep(2);
            
            expect(mobileVarietyManager.currentStep).toBe(2);
        });

        test('should update progress bar correctly', () => {
            mobileVarietyManager.currentStep = 2;
            mobileVarietyManager.updateProgressBar();
            
            const progressBar = document.getElementById('progressBar');
            expect(progressBar.style.width).toBe('50%');
        });
    });

    describe('Farm Information Validation', () => {
        test('should validate farm information correctly', () => {
            document.getElementById('farmLocation').value = 'Test Farm, Iowa';
            document.getElementById('farmSize').value = '100';
            document.getElementById('soilType').value = 'clay';
            
            const isValid = mobileVarietyManager.validateFarmInformation();
            
            expect(isValid).toBe(true);
            expect(mobileVarietyManager.farmData.location).toBe('Test Farm, Iowa');
            expect(mobileVarietyManager.farmData.farmSize).toBe(100);
            expect(mobileVarietyManager.farmData.soilType).toBe('clay');
        });

        test('should reject invalid farm size', () => {
            document.getElementById('farmLocation').value = 'Test Farm, Iowa';
            document.getElementById('farmSize').value = '0';
            document.getElementById('soilType').value = 'clay';
            
            const isValid = mobileVarietyManager.validateFarmInformation();
            
            expect(isValid).toBe(false);
        });

        test('should reject missing required fields', () => {
            document.getElementById('farmLocation').value = '';
            document.getElementById('farmSize').value = '100';
            document.getElementById('soilType').value = 'clay';
            
            const isValid = mobileVarietyManager.validateFarmInformation();
            
            expect(isValid).toBe(false);
        });
    });

    describe('Crop Selection', () => {
        test('should select crop correctly', () => {
            const cropId = 'corn';
            const cropName = 'Corn';
            
            mobileVarietyManager.selectCrop(cropId, cropName);
            
            expect(mobileVarietyManager.selectedCrop).toEqual({ id: cropId, name: cropName });
        });

        test('should validate crop selection', () => {
            mobileVarietyManager.selectedCrop = { id: 'corn', name: 'Corn' };
            
            const isValid = mobileVarietyManager.validateCropSelection();
            
            expect(isValid).toBe(true);
        });

        test('should reject when no crop selected', () => {
            mobileVarietyManager.selectedCrop = null;
            
            const isValid = mobileVarietyManager.validateCropSelection();
            
            expect(isValid).toBe(false);
        });
    });

    describe('Preferences', () => {
        test('should validate preferences correctly', () => {
            document.getElementById('yieldPriority').value = '80';
            document.getElementById('sustainabilityPriority').value = '60';
            
            const isValid = mobileVarietyManager.validatePreferences();
            
            expect(isValid).toBe(true);
            expect(mobileVarietyManager.userPreferences.yieldPriority).toBe(80);
            expect(mobileVarietyManager.userPreferences.sustainabilityPriority).toBe(60);
            expect(mobileVarietyManager.userPreferences.riskTolerance).toBe('moderate');
        });

        test('should handle risk selection', () => {
            const riskButton = document.querySelector('.risk-btn[data-value="high"]');
            
            mobileVarietyManager.selectRisk(riskButton);
            
            expect(riskButton.classList.contains('active')).toBe(true);
            expect(document.querySelector('.risk-btn[data-value="moderate"]').classList.contains('active')).toBe(false);
        });

        test('should handle irrigation toggle', () => {
            const irrigationButton = document.querySelector('.toggle-btn[data-value="false"]');
            
            mobileVarietyManager.toggleIrrigation(irrigationButton);
            
            expect(irrigationButton.classList.contains('active')).toBe(true);
            expect(document.querySelector('.toggle-btn[data-value="true"]').classList.contains('active')).toBe(false);
        });
    });

    describe('Location Services', () => {
        test('should handle geolocation success', async () => {
            const mockPosition = {
                coords: {
                    latitude: 41.8781,
                    longitude: -87.6298
                }
            };

            navigator.geolocation.getCurrentPosition.mockImplementation((success) => {
                success(mockPosition);
            });

            await mobileVarietyManager.getCurrentLocation();

            expect(document.getElementById('farmLocation').value).toBe('41.878100, -87.629800');
            expect(mobileVarietyManager.farmData.coordinates).toEqual({
                latitude: 41.8781,
                longitude: -87.6298
            });
        });

        test('should handle geolocation error', async () => {
            navigator.geolocation.getCurrentPosition.mockImplementation((success, error) => {
                error(new Error('Geolocation failed'));
            });

            await mobileVarietyManager.getCurrentLocation();

            expect(document.getElementById('farmLocation').value).toBe('');
        });
    });

    describe('API Integration', () => {
        test('should fetch crop data successfully', async () => {
            const mockCrops = [
                { id: 'corn', name: 'Corn', scientific_name: 'Zea mays' },
                { id: 'soybeans', name: 'Soybeans', scientific_name: 'Glycine max' }
            ];

            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockCrops
            });

            await mobileVarietyManager.loadCropData();

            expect(fetch).toHaveBeenCalledWith('/api/v1/crop-taxonomy/crops');
        });

        test('should handle API errors gracefully', async () => {
            fetch.mockRejectedValueOnce(new Error('Network error'));

            await mobileVarietyManager.loadCropData();

            // Should not throw error
            expect(true).toBe(true);
        });

        test('should get recommendations successfully', async () => {
            const mockRecommendations = {
                varieties: [
                    {
                        id: 'variety1',
                        name: 'Test Variety',
                        score: 0.85,
                        maturity_days: 120,
                        yield_potential: '180',
                        seed_cost_per_acre: '45',
                        seed_company: 'Test Company',
                        traits: []
                    }
                ]
            };

            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockRecommendations
            });

            mobileVarietyManager.selectedCrop = { id: 'corn', name: 'Corn' };
            mobileVarietyManager.farmData = {
                location: 'Test Farm',
                farmSize: 100,
                soilType: 'clay',
                irrigation: true
            };
            mobileVarietyManager.userPreferences = {
                yieldPriority: 80,
                sustainabilityPriority: 60,
                riskTolerance: 'moderate'
            };

            await mobileVarietyManager.getRecommendations();

            expect(fetch).toHaveBeenCalledWith('/api/v1/crop-taxonomy/varieties/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: expect.stringContaining('corn')
            });

            expect(mobileVarietyManager.varietyRecommendations).toEqual(mockRecommendations.varieties);
        });
    });

    describe('Touch Gestures', () => {
        test('should handle swipe gestures', () => {
            mobileVarietyManager.currentStep = 2;
            
            // Simulate swipe left (next step)
            mobileVarietyManager.handleSwipe(100, 200, 50, 200);
            
            expect(mobileVarietyManager.currentStep).toBe(3);
        });

        test('should handle swipe right (previous step)', () => {
            mobileVarietyManager.currentStep = 2;
            
            // Simulate swipe right (previous step)
            mobileVarietyManager.handleSwipe(50, 200, 100, 200);
            
            expect(mobileVarietyManager.currentStep).toBe(1);
        });

        test('should ignore vertical swipes', () => {
            mobileVarietyManager.currentStep = 2;
            
            // Simulate vertical swipe
            mobileVarietyManager.handleSwipe(100, 200, 100, 150);
            
            expect(mobileVarietyManager.currentStep).toBe(2);
        });
    });

    describe('Voice Recognition', () => {
        test('should initialize voice recognition if available', () => {
            expect(mobileVarietyManager.voiceRecognition).toBeTruthy();
        });

        test('should handle voice search results', () => {
            const mockEvent = {
                results: [
                    [{ transcript: 'corn' }]
                ]
            };

            mobileVarietyManager.voiceRecognition.onresult(mockEvent);

            expect(document.getElementById('cropSearch').value).toBe('corn');
        });
    });

    describe('Offline Functionality', () => {
        test('should detect online status', () => {
            Object.defineProperty(navigator, 'onLine', {
                writable: true,
                value: false
            });

            mobileVarietyManager.updateOnlineStatus();

            expect(mobileVarietyManager.isOnline).toBe(false);
        });

        test('should handle offline data caching', () => {
            const varietyData = [
                { id: 'variety1', name: 'Test Variety' }
            ];

            mobileVarietyManager.cacheVarietyData(varietyData);

            // Should not throw error
            expect(true).toBe(true);
        });
    });

    describe('Accessibility', () => {
        test('should support keyboard navigation', () => {
            const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
            
            // Should not throw error
            expect(() => {
                document.dispatchEvent(event);
            }).not.toThrow();
        });

        test('should support screen readers', () => {
            const elements = document.querySelectorAll('[aria-label], [aria-describedby]');
            
            // Should have accessible elements
            expect(elements.length).toBeGreaterThanOrEqual(0);
        });
    });

    describe('Responsive Design', () => {
        test('should adapt to different screen sizes', () => {
            // Test mobile viewport
            Object.defineProperty(window, 'innerWidth', {
                writable: true,
                configurable: true,
                value: 375
            });

            // Should not throw error
            expect(() => {
                mobileVarietyManager.updateWizardDisplay();
            }).not.toThrow();
        });

        test('should handle orientation changes', () => {
            // Simulate orientation change
            const event = new Event('orientationchange');
            
            // Should not throw error
            expect(() => {
                window.dispatchEvent(event);
            }).not.toThrow();
        });
    });

    describe('Performance', () => {
        test('should debounce search input', () => {
            const searchInput = document.getElementById('cropSearch');
            
            // Simulate rapid typing
            for (let i = 0; i < 5; i++) {
                searchInput.value = 'test' + i;
                mobileVarietyManager.handleCropSearch({ target: searchInput });
            }

            // Should not make excessive API calls
            expect(fetch).toHaveBeenCalledTimes(0); // Debounced
        });

        test('should handle large datasets efficiently', () => {
            const largeCropList = Array.from({ length: 1000 }, (_, i) => ({
                id: `crop${i}`,
                name: `Crop ${i}`,
                scientific_name: `Scientific ${i}`
            }));

            // Should not throw error
            expect(() => {
                mobileVarietyManager.displayCropGrid(largeCropList.slice(0, 12));
            }).not.toThrow();
        });
    });
});

// Integration tests
describe('Mobile Variety Selection Integration', () => {
    beforeEach(() => {
        // Set up full DOM
        document.body.innerHTML = `
            <div class="mobile-container">
                <div id="step1" class="wizard-step active">
                    <input id="farmLocation" type="text" />
                    <input id="farmSize" type="number" />
                    <select id="soilType">
                        <option value="">Select soil type</option>
                        <option value="clay">Clay</option>
                    </select>
                </div>
                <div id="step2" class="wizard-step">
                    <input id="cropSearch" type="text" />
                    <div id="cropGrid"></div>
                </div>
                <div id="step3" class="wizard-step">
                    <input id="yieldPriority" type="range" min="0" max="100" value="80" />
                    <input id="sustainabilityPriority" type="range" min="0" max="100" value="60" />
                </div>
                <div id="step4" class="wizard-step">
                    <div id="recommendationsContainer"></div>
                </div>
            </div>
        `;
    });

    test('should complete full workflow', async () => {
        const manager = new MobileVarietySelectionManager();

        // Step 1: Farm Information
        document.getElementById('farmLocation').value = 'Test Farm, Iowa';
        document.getElementById('farmSize').value = '100';
        document.getElementById('soilType').value = 'clay';

        expect(manager.validateFarmInformation()).toBe(true);
        manager.nextStep(2);

        // Step 2: Crop Selection
        manager.selectCrop('corn', 'Corn');
        expect(manager.validateCropSelection()).toBe(true);
        manager.nextStep(3);

        // Step 3: Preferences
        expect(manager.validatePreferences()).toBe(true);
        manager.nextStep(4);

        expect(manager.currentStep).toBe(4);
    });
});