/**
 * App Shell JavaScript
 * 
 * Provides app shell architecture functionality including:
 * - Loading state management
 * - Skeleton screen rendering
 * - Performance optimization
 * - Resource preloading
 * - Critical path optimization
 */

class AppShell {
    constructor() {
        this.isLoading = true;
        this.loadingStartTime = performance.now();
        this.criticalResources = [];
        this.nonCriticalResources = [];
        this.skeletonElements = new Map();
        
        this.init();
    }

    async init() {
        console.log('Initializing App Shell...');
        
        try {
            await this.setupLoadingStates();
            await this.preloadCriticalResources();
            await this.setupSkeletonScreens();
            await this.optimizePerformance();
            await this.setupResourceHints();
            
            console.log('App Shell initialized successfully');
        } catch (error) {
            console.error('Failed to initialize App Shell:', error);
        }
    }

    /**
     * Setup loading states and indicators
     */
    async setupLoadingStates() {
        // Create loading overlay
        this.createLoadingOverlay();
        
        // Monitor resource loading
        this.monitorResourceLoading();
        
        // Setup loading completion detection
        this.setupLoadingCompletion();
    }

    /**
     * Create loading overlay
     */
    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'app-shell-loading';
        overlay.className = 'app-shell-loading';
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Loading CAAIN Soil Hub...</div>
        `;
        
        document.body.appendChild(overlay);
    }

    /**
     * Monitor resource loading
     */
    monitorResourceLoading() {
        // Monitor critical CSS
        this.monitorCSSLoading();
        
        // Monitor critical JavaScript
        this.monitorJSLoading();
        
        // Monitor images
        this.monitorImageLoading();
        
        // Monitor fonts
        this.monitorFontLoading();
    }

    /**
     * Monitor CSS loading
     */
    monitorCSSLoading() {
        const criticalCSS = [
            '/static/css/mobile-variety-selection.css',
            '/static/css/bootstrap.min.css',
            '/static/css/app-shell.css'
        ];

        criticalCSS.forEach(cssPath => {
            const link = document.querySelector(`link[href="${cssPath}"]`);
            if (link) {
                link.addEventListener('load', () => {
                    this.onCriticalResourceLoaded('css', cssPath);
                });
            }
        });
    }

    /**
     * Monitor JavaScript loading
     */
    monitorJSLoading() {
        const criticalJS = [
            '/static/js/mobile-variety-selection.js',
            '/static/js/mobile-pwa-features.js',
            '/static/js/app-shell.js'
        ];

        criticalJS.forEach(jsPath => {
            const script = document.querySelector(`script[src="${jsPath}"]`);
            if (script) {
                script.addEventListener('load', () => {
                    this.onCriticalResourceLoaded('js', jsPath);
                });
            }
        });
    }

    /**
     * Monitor image loading
     */
    monitorImageLoading() {
        const criticalImages = [
            '/static/icons/icon-192x192.png',
            '/static/icons/icon-512x512.png'
        ];

        criticalImages.forEach(imagePath => {
            const img = new Image();
            img.onload = () => {
                this.onCriticalResourceLoaded('image', imagePath);
            };
            img.src = imagePath;
        });
    }

    /**
     * Monitor font loading
     */
    monitorFontLoading() {
        if ('fonts' in document) {
            document.fonts.ready.then(() => {
                this.onCriticalResourceLoaded('fonts', 'all');
            });
        }
    }

    /**
     * Handle critical resource loaded
     */
    onCriticalResourceLoaded(type, path) {
        console.log(`Critical ${type} loaded: ${path}`);
        
        // Check if all critical resources are loaded
        if (this.areCriticalResourcesLoaded()) {
            this.hideLoadingOverlay();
        }
    }

    /**
     * Check if all critical resources are loaded
     */
    areCriticalResourcesLoaded() {
        // This is a simplified check - in production, you'd track specific resources
        return document.readyState === 'complete' && 
               this.isCriticalCSSLoaded() && 
               this.isCriticalJSLoaded();
    }

    /**
     * Check if critical CSS is loaded
     */
    isCriticalCSSLoaded() {
        const criticalCSS = [
            '/static/css/mobile-variety-selection.css',
            '/static/css/bootstrap.min.css',
            '/static/css/app-shell.css'
        ];

        return criticalCSS.every(cssPath => {
            const link = document.querySelector(`link[href="${cssPath}"]`);
            return link && link.sheet && link.sheet.cssRules.length > 0;
        });
    }

    /**
     * Check if critical JavaScript is loaded
     */
    isCriticalJSLoaded() {
        return typeof window.mobilePWAFeatures !== 'undefined' &&
               typeof window.MobileVarietySelection !== 'undefined';
    }

    /**
     * Hide loading overlay
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('app-shell-loading');
        if (overlay) {
            overlay.classList.add('hidden');
            
            setTimeout(() => {
                overlay.remove();
                this.isLoading = false;
                this.onAppShellReady();
            }, 300);
        }
    }

    /**
     * Handle app shell ready
     */
    onAppShellReady() {
        const loadTime = performance.now() - this.loadingStartTime;
        console.log(`App Shell ready in ${loadTime.toFixed(2)}ms`);
        
        // Report performance metrics
        this.reportPerformanceMetrics(loadTime);
        
        // Initialize lazy loading
        this.initializeLazyLoading();
        
        // Preload non-critical resources
        this.preloadNonCriticalResources();
        
        // Trigger app ready event
        document.dispatchEvent(new CustomEvent('appShellReady', {
            detail: { loadTime }
        }));
    }

    /**
     * Report performance metrics
     */
    reportPerformanceMetrics(loadTime) {
        const metrics = {
            appShellLoadTime: loadTime,
            domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
            firstPaint: this.getFirstPaint(),
            firstContentfulPaint: this.getFirstContentfulPaint()
        };

        console.log('Performance Metrics:', metrics);

        // Send to analytics if available
        if (typeof gtag !== 'undefined') {
            gtag('event', 'app_shell_performance', {
                event_category: 'Performance',
                event_label: 'App Shell',
                value: Math.round(loadTime)
            });
        }
    }

    /**
     * Get first paint metric
     */
    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    /**
     * Get first contentful paint metric
     */
    getFirstContentfulPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        return firstContentfulPaint ? firstContentfulPaint.startTime : null;
    }

    /**
     * Setup skeleton screens
     */
    async setupSkeletonScreens() {
        // Create skeleton screens for main content areas
        this.createSkeletonScreens();
        
        // Setup skeleton to content transitions
        this.setupSkeletonTransitions();
    }

    /**
     * Create skeleton screens
     */
    createSkeletonScreens() {
        const skeletonHTML = `
            <div class="skeleton-screen skeleton-header"></div>
            <div class="skeleton-screen skeleton-card"></div>
            <div class="skeleton-screen skeleton-card"></div>
            <div class="skeleton-screen skeleton-card"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text short"></div>
            <div class="skeleton-text medium"></div>
        `;

        // Add skeleton to main content areas
        const mainContent = document.querySelector('main, .main-content, #main-content');
        if (mainContent) {
            mainContent.innerHTML = skeletonHTML;
        }
    }

    /**
     * Setup skeleton transitions
     */
    setupSkeletonTransitions() {
        // Listen for content loaded events
        document.addEventListener('contentLoaded', (event) => {
            this.replaceSkeletonWithContent(event.detail.content);
        });
    }

    /**
     * Replace skeleton with actual content
     */
    replaceSkeletonWithContent(content) {
        const mainContent = document.querySelector('main, .main-content, #main-content');
        if (mainContent) {
            mainContent.innerHTML = content;
            mainContent.classList.add('loaded');
        }
    }

    /**
     * Preload critical resources
     */
    async preloadCriticalResources() {
        const criticalResources = [
            { href: '/static/css/mobile-variety-selection.css', as: 'style' },
            { href: '/static/css/bootstrap.min.css', as: 'style' },
            { href: '/static/css/app-shell.css', as: 'style' },
            { href: '/static/js/mobile-variety-selection.js', as: 'script' },
            { href: '/static/js/mobile-pwa-features.js', as: 'script' },
            { href: '/static/js/app-shell.js', as: 'script' },
            { href: '/static/icons/icon-192x192.png', as: 'image' },
            { href: '/static/icons/icon-512x512.png', as: 'image' }
        ];

        for (const resource of criticalResources) {
            await this.preloadResource(resource);
        }
    }

    /**
     * Preload a single resource
     */
    async preloadResource(resource) {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource.href;
            link.as = resource.as;
            
            if (resource.as === 'script') {
                link.crossOrigin = 'anonymous';
            }
            
            link.onload = () => resolve();
            link.onerror = () => reject(new Error(`Failed to preload ${resource.href}`));
            
            document.head.appendChild(link);
        });
    }

    /**
     * Preload non-critical resources
     */
    async preloadNonCriticalResources() {
        const nonCriticalResources = [
            { href: '/static/js/mobile-device-integration.js', as: 'script' },
            { href: '/static/js/mobile-camera-crop-id.js', as: 'script' },
            { href: '/static/js/mobile-gps-field-mapping.js', as: 'script' },
            { href: '/static/js/mobile-offline-database.js', as: 'script' },
            { href: '/static/css/font-awesome.min.css', as: 'style' },
            { href: '/static/js/bootstrap.bundle.min.js', as: 'script' }
        ];

        // Preload with lower priority
        setTimeout(() => {
            nonCriticalResources.forEach(resource => {
                this.preloadResource(resource).catch(error => {
                    console.warn(`Failed to preload non-critical resource: ${error.message}`);
                });
            });
        }, 1000);
    }

    /**
     * Setup resource hints
     */
    async setupResourceHints() {
        // DNS prefetch for external domains
        this.addDNSPrefetch('fonts.googleapis.com');
        this.addDNSPrefetch('cdnjs.cloudflare.com');
        
        // Preconnect to critical origins
        this.addPreconnect('https://caain-soil-hub.com');
        
        // Prefetch likely next pages
        this.addPrefetch('/mobile-variety-selection?tab=fields');
        this.addPrefetch('/mobile-variety-selection?tab=recommendations');
    }

    /**
     * Add DNS prefetch
     */
    addDNSPrefetch(domain) {
        const link = document.createElement('link');
        link.rel = 'dns-prefetch';
        link.href = `//${domain}`;
        document.head.appendChild(link);
    }

    /**
     * Add preconnect
     */
    addPreconnect(url) {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = url;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
    }

    /**
     * Add prefetch
     */
    addPrefetch(url) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }

    /**
     * Initialize lazy loading
     */
    initializeLazyLoading() {
        // Setup intersection observer for lazy loading
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadLazyElement(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            });

            // Observe lazy load elements
            document.querySelectorAll('.lazy-load').forEach(element => {
                observer.observe(element);
            });
        }
    }

    /**
     * Load lazy element
     */
    loadLazyElement(element) {
        // Add loaded class for transition
        element.classList.add('loaded');
        
        // Load actual content if it's a placeholder
        if (element.dataset.src) {
            if (element.tagName === 'IMG') {
                element.src = element.dataset.src;
            } else if (element.dataset.content) {
                element.innerHTML = element.dataset.content;
            }
        }
    }

    /**
     * Optimize performance
     */
    async optimizePerformance() {
        // Enable hardware acceleration for animations
        this.enableHardwareAcceleration();
        
        // Optimize scroll performance
        this.optimizeScrollPerformance();
        
        // Setup performance monitoring
        this.setupPerformanceMonitoring();
    }

    /**
     * Enable hardware acceleration
     */
    enableHardwareAcceleration() {
        // Add transform3d to elements that will be animated
        document.querySelectorAll('[data-animation]').forEach(element => {
            element.style.transform = 'translateZ(0)';
            element.style.willChange = 'transform';
        });
    }

    /**
     * Optimize scroll performance
     */
    optimizeScrollPerformance() {
        // Use passive event listeners for scroll events
        let passiveSupported = false;
        try {
            const options = {
                get passive() {
                    passiveSupported = true;
                    return false;
                }
            };
            window.addEventListener('test', null, options);
            window.removeEventListener('test', null, options);
        } catch (err) {
            passiveSupported = false;
        }

        // Add scroll event listeners with passive option
        if (passiveSupported) {
            window.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
        } else {
            window.addEventListener('scroll', this.handleScroll.bind(this));
        }
    }

    /**
     * Handle scroll events
     */
    handleScroll() {
        // Throttle scroll handling
        if (!this.scrollTimeout) {
            this.scrollTimeout = setTimeout(() => {
                this.onScroll();
                this.scrollTimeout = null;
            }, 16); // ~60fps
        }
    }

    /**
     * Handle scroll
     */
    onScroll() {
        // Update scroll position for parallax effects
        const scrollY = window.scrollY;
        document.documentElement.style.setProperty('--scroll-y', `${scrollY}px`);
    }

    /**
     * Setup performance monitoring
     */
    setupPerformanceMonitoring() {
        // Monitor long tasks
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (entry.duration > 50) { // Tasks longer than 50ms
                        console.warn('Long task detected:', entry);
                    }
                });
            });
            
            observer.observe({ entryTypes: ['longtask'] });
        }
    }

    /**
     * Setup loading completion detection
     */
    setupLoadingCompletion() {
        // Listen for DOM content loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.onDOMContentLoaded();
            });
        } else {
            this.onDOMContentLoaded();
        }

        // Listen for window load
        window.addEventListener('load', () => {
            this.onWindowLoad();
        });
    }

    /**
     * Handle DOM content loaded
     */
    onDOMContentLoaded() {
        console.log('DOM content loaded');
        // DOM is ready, but resources may still be loading
    }

    /**
     * Handle window load
     */
    onWindowLoad() {
        console.log('Window loaded');
        // All resources are loaded
        if (this.isLoading) {
            this.hideLoadingOverlay();
        }
    }

    /**
     * Get loading progress
     */
    getLoadingProgress() {
        const totalResources = this.criticalResources.length;
        const loadedResources = this.criticalResources.filter(resource => 
            resource.loaded
        ).length;
        
        return totalResources > 0 ? (loadedResources / totalResources) * 100 : 0;
    }

    /**
     * Show loading progress
     */
    showLoadingProgress() {
        const progress = this.getLoadingProgress();
        const progressElement = document.querySelector('.loading-progress');
        if (progressElement) {
            progressElement.style.width = `${progress}%`;
        }
    }
}

// Initialize App Shell when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.appShell = new AppShell();
    });
} else {
    window.appShell = new AppShell();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AppShell };
}
