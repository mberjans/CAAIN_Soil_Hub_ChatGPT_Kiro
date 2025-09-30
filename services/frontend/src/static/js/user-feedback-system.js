/**
 * User Feedback Collection System
 * TICKET-008_farm-location-input-14.2: Add comprehensive user guidance and support
 */

class UserFeedbackSystem {
    constructor() {
        this.feedbackData = this.loadFeedbackData();
        this.currentSession = this.initializeSession();
        this.feedbackTriggers = this.initializeFeedbackTriggers();
        
        this.initializeEventListeners();
        this.startSessionTracking();
    }

    initializeSession() {
        return {
            sessionId: this.generateSessionId(),
            startTime: Date.now(),
            interactions: [],
            locationInputAttempts: 0,
            successfulInputs: 0,
            errors: [],
            helpUsage: {
                tutorials: 0,
                faq: 0,
                troubleshooting: 0,
                support: 0,
                chat: 0
            },
            userSatisfaction: null,
            feedbackSubmitted: false
        };
    }

    initializeFeedbackTriggers() {
        return {
            // Trigger feedback after successful location input
            onLocationInputSuccess: true,
            // Trigger feedback after multiple failed attempts
            onMultipleFailures: 3,
            // Trigger feedback after help usage
            onHelpUsage: true,
            // Trigger feedback after session duration
            onSessionDuration: 300000, // 5 minutes
            // Trigger feedback on exit
            onExit: true
        };
    }

    initializeEventListeners() {
        // Track location input attempts
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="validateLocation"], [onclick*="saveLocation"], [onclick*="geocodeAddress"]')) {
                this.trackLocationInputAttempt();
            }
        });

        // Track help usage
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="showInteractiveTutorial"]')) {
                this.trackHelpUsage('tutorials');
            } else if (e.target.matches('[onclick*="showFAQ"]')) {
                this.trackHelpUsage('faq');
            } else if (e.target.matches('[onclick*="showTroubleshooting"]')) {
                this.trackHelpUsage('troubleshooting');
            } else if (e.target.matches('[onclick*="showSupportTicket"]')) {
                this.trackHelpUsage('support');
            } else if (e.target.matches('[onclick*="showChatWidget"]')) {
                this.trackHelpUsage('chat');
            }
        });

        // Track errors
        window.addEventListener('error', (e) => {
            this.trackError(e.error);
        });

        // Track page unload for exit feedback
        window.addEventListener('beforeunload', () => {
            this.handleExitFeedback();
        });

        // Track session duration
        setInterval(() => {
            this.checkSessionDuration();
        }, 60000); // Check every minute
    }

    startSessionTracking() {
        // Track user interactions
        document.addEventListener('click', (e) => {
            this.trackInteraction('click', e.target);
        });

        document.addEventListener('input', (e) => {
            this.trackInteraction('input', e.target);
        });

        document.addEventListener('focus', (e) => {
            this.trackInteraction('focus', e.target);
        });
    }

    trackLocationInputAttempt() {
        this.currentSession.locationInputAttempts++;
        this.trackInteraction('location_input_attempt', null);
        
        // Check if we should trigger feedback
        if (this.feedbackTriggers.onLocationInputSuccess) {
            setTimeout(() => {
                this.checkForSuccessFeedback();
            }, 2000);
        }
    }

    trackLocationInputSuccess() {
        this.currentSession.successfulInputs++;
        this.trackInteraction('location_input_success', null);
        
        if (this.feedbackTriggers.onLocationInputSuccess) {
            this.showSuccessFeedback();
        }
    }

    trackLocationInputFailure(error) {
        this.currentSession.errors.push({
            type: 'location_input_failure',
            error: error,
            timestamp: Date.now()
        });
        
        if (this.currentSession.errors.length >= this.feedbackTriggers.onMultipleFailures) {
            this.showFailureFeedback();
        }
    }

    trackHelpUsage(type) {
        this.currentSession.helpUsage[type]++;
        this.trackInteraction('help_usage', { type: type });
        
        if (this.feedbackTriggers.onHelpUsage) {
            setTimeout(() => {
                this.showHelpUsageFeedback(type);
            }, 1000);
        }
    }

    trackError(error) {
        this.currentSession.errors.push({
            type: 'javascript_error',
            error: error.message || error,
            timestamp: Date.now()
        });
    }

    trackInteraction(type, element) {
        this.currentSession.interactions.push({
            type: type,
            element: element ? element.tagName + (element.id ? '#' + element.id : '') : null,
            timestamp: Date.now()
        });
    }

    checkForSuccessFeedback() {
        // Check if location was successfully input
        const locationData = this.getLocationData();
        if (locationData && locationData.latitude && locationData.longitude) {
            this.trackLocationInputSuccess();
        }
    }

    getLocationData() {
        // Try to get location data from various sources
        const latInput = document.getElementById('latitudeInput');
        const lngInput = document.getElementById('longitudeInput');
        const addressInput = document.getElementById('addressInput');
        
        if (latInput && lngInput && latInput.value && lngInput.value) {
            return {
                latitude: parseFloat(latInput.value),
                longitude: parseFloat(lngInput.value),
                method: 'coordinates'
            };
        } else if (addressInput && addressInput.value) {
            return {
                address: addressInput.value,
                method: 'address'
            };
        }
        
        return null;
    }

    checkSessionDuration() {
        const sessionDuration = Date.now() - this.currentSession.startTime;
        if (sessionDuration >= this.feedbackTriggers.onSessionDuration) {
            this.showSessionFeedback();
        }
    }

    handleExitFeedback() {
        if (this.feedbackTriggers.onExit && !this.currentSession.feedbackSubmitted) {
            this.showExitFeedback();
        }
    }

    showSuccessFeedback() {
        if (this.currentSession.feedbackSubmitted) return;
        
        const modal = this.createFeedbackModal('success', {
            title: 'Great job!',
            message: 'You successfully entered your farm location. How was your experience?',
            type: 'success'
        });
        
        this.showFeedbackModal(modal);
    }

    showFailureFeedback() {
        if (this.currentSession.feedbackSubmitted) return;
        
        const modal = this.createFeedbackModal('failure', {
            title: 'Having trouble?',
            message: 'We noticed you\'re having some issues. Let us help improve your experience.',
            type: 'failure'
        });
        
        this.showFeedbackModal(modal);
    }

    showHelpUsageFeedback(helpType) {
        if (this.currentSession.feedbackSubmitted) return;
        
        const modal = this.createFeedbackModal('help_usage', {
            title: 'Was that helpful?',
            message: `You just used our ${helpType} feature. Did it help you with your location input?`,
            type: 'help_usage',
            helpType: helpType
        });
        
        this.showFeedbackModal(modal);
    }

    showSessionFeedback() {
        if (this.currentSession.feedbackSubmitted) return;
        
        const modal = this.createFeedbackModal('session', {
            title: 'How\'s it going?',
            message: 'You\'ve been using the location input for a while. How is your experience so far?',
            type: 'session'
        });
        
        this.showFeedbackModal(modal);
    }

    showExitFeedback() {
        const modal = this.createFeedbackModal('exit', {
            title: 'Quick feedback?',
            message: 'Before you go, how was your experience with the location input?',
            type: 'exit'
        });
        
        this.showFeedbackModal(modal);
    }

    createFeedbackModal(context, options) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'feedbackModal';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-sm">
                <div class="modal-content">
                    <div class="modal-header bg-${this.getContextColor(options.type)} text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-${this.getContextIcon(options.type)} me-2"></i>
                            ${options.title}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">${options.message}</p>
                        
                        <div class="feedback-form">
                            <div class="mb-3">
                                <label class="form-label">Overall Experience</label>
                                <div class="rating-input">
                                    <input type="radio" name="rating" value="5" id="rating5">
                                    <label for="rating5"><i class="fas fa-star"></i></label>
                                    <input type="radio" name="rating" value="4" id="rating4">
                                    <label for="rating4"><i class="fas fa-star"></i></label>
                                    <input type="radio" name="rating" value="3" id="rating3">
                                    <label for="rating3"><i class="fas fa-star"></i></label>
                                    <input type="radio" name="rating" value="2" id="rating2">
                                    <label for="rating2"><i class="fas fa-star"></i></label>
                                    <input type="radio" name="rating" value="1" id="rating1">
                                    <label for="rating1"><i class="fas fa-star"></i></label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">What worked well?</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="easy-to-use" id="positive1">
                                    <label class="form-check-label" for="positive1">Easy to use</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="helpful-guidance" id="positive2">
                                    <label class="form-check-label" for="positive2">Helpful guidance</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="accurate-results" id="positive3">
                                    <label class="form-check-label" for="positive3">Accurate results</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="fast-loading" id="positive4">
                                    <label class="form-check-label" for="positive4">Fast loading</label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">What could be improved?</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="confusing-interface" id="negative1">
                                    <label class="form-check-label" for="negative1">Confusing interface</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="slow-loading" id="negative2">
                                    <label class="form-check-label" for="negative2">Slow loading</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="inaccurate-gps" id="negative3">
                                    <label class="form-check-label" for="negative3">Inaccurate GPS</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="missing-features" id="negative4">
                                    <label class="form-check-label" for="negative4">Missing features</label>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="feedbackComments" class="form-label">Additional comments</label>
                                <textarea class="form-control" id="feedbackComments" rows="3" 
                                          placeholder="Tell us more about your experience..."></textarea>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="allowContact">
                                    <label class="form-check-label" for="allowContact">
                                        Allow us to contact you for follow-up questions
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Skip</button>
                        <button type="button" class="btn btn-primary" onclick="submitFeedback('${context}')">
                            <i class="fas fa-paper-plane me-2"></i>
                            Submit Feedback
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }

    showFeedbackModal(modal) {
        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Clean up when modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    getContextColor(type) {
        const colors = {
            'success': 'success',
            'failure': 'warning',
            'help_usage': 'info',
            'session': 'primary',
            'exit': 'secondary'
        };
        return colors[type] || 'primary';
    }

    getContextIcon(type) {
        const icons = {
            'success': 'check-circle',
            'failure': 'exclamation-triangle',
            'help_usage': 'question-circle',
            'session': 'clock',
            'exit': 'door-open'
        };
        return icons[type] || 'comment';
    }

    submitFeedback(context) {
        const feedback = this.collectFeedbackData(context);
        
        // Store feedback
        this.feedbackData.push(feedback);
        this.saveFeedbackData();
        
        // Mark session as having submitted feedback
        this.currentSession.feedbackSubmitted = true;
        this.currentSession.userSatisfaction = feedback.rating;
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('feedbackModal'));
        if (modal) {
            modal.hide();
        }
        
        // Show thank you message
        this.showThankYouMessage();
        
        // Track feedback submission
        this.trackFeedbackSubmission(feedback);
    }

    collectFeedbackData(context) {
        const rating = document.querySelector('input[name="rating"]:checked')?.value;
        const positives = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .filter(cb => cb.id.startsWith('positive'))
            .map(cb => cb.value);
        const negatives = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .filter(cb => cb.id.startsWith('negative'))
            .map(cb => cb.value);
        const comments = document.getElementById('feedbackComments')?.value;
        const allowContact = document.getElementById('allowContact')?.checked;
        
        return {
            id: this.generateFeedbackId(),
            sessionId: this.currentSession.sessionId,
            context: context,
            timestamp: Date.now(),
            rating: rating ? parseInt(rating) : null,
            positives: positives,
            negatives: negatives,
            comments: comments,
            allowContact: allowContact,
            sessionData: {
                duration: Date.now() - this.currentSession.startTime,
                locationInputAttempts: this.currentSession.locationInputAttempts,
                successfulInputs: this.currentSession.successfulInputs,
                errors: this.currentSession.errors.length,
                helpUsage: this.currentSession.helpUsage,
                interactions: this.currentSession.interactions.length
            }
        };
    }

    showThankYouMessage() {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="fas fa-heart me-2"></i>
            Thank you for your feedback! It helps us improve the experience for all farmers.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    trackFeedbackSubmission(feedback) {
        // In a real implementation, this would send analytics data
        console.log('Feedback submitted:', feedback);
        
        // Store locally for demo purposes
        const submissions = JSON.parse(localStorage.getItem('feedbackSubmissions') || '[]');
        submissions.push(feedback);
        localStorage.setItem('feedbackSubmissions', JSON.stringify(submissions));
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    generateFeedbackId() {
        return 'feedback_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    loadFeedbackData() {
        return JSON.parse(localStorage.getItem('userFeedbackData') || '[]');
    }

    saveFeedbackData() {
        localStorage.setItem('userFeedbackData', JSON.stringify(this.feedbackData));
    }

    getFeedbackAnalytics() {
        const totalFeedback = this.feedbackData.length;
        const averageRating = this.feedbackData.reduce((sum, f) => sum + (f.rating || 0), 0) / totalFeedback;
        
        const positiveCounts = {};
        const negativeCounts = {};
        
        this.feedbackData.forEach(feedback => {
            feedback.positives.forEach(p => {
                positiveCounts[p] = (positiveCounts[p] || 0) + 1;
            });
            feedback.negatives.forEach(n => {
                negativeCounts[n] = (negativeCounts[n] || 0) + 1;
            });
        });
        
        return {
            totalFeedback,
            averageRating,
            positiveCounts,
            negativeCounts,
            recentFeedback: this.feedbackData.slice(-10)
        };
    }
}

// Global functions for HTML onclick handlers
let userFeedbackSystem;

function initializeUserFeedbackSystem() {
    userFeedbackSystem = new UserFeedbackSystem();
}

function submitFeedback(context) {
    if (userFeedbackSystem) {
        userFeedbackSystem.submitFeedback(context);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeUserFeedbackSystem);