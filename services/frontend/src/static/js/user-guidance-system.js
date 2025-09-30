/**
 * Comprehensive User Guidance and Support System
 * TICKET-008_farm-location-input-14.2: Add comprehensive user guidance and support
 */

class UserGuidanceSystem {
    constructor() {
        this.currentTutorialStep = 0;
        this.totalTutorialSteps = 5;
        this.tutorialData = this.initializeTutorialData();
        this.chatMessages = [];
        this.chatOpen = false;
        this.supportTickets = [];
        
        this.initializeEventListeners();
        this.initializeContextualHelp();
        this.initializeSearchFunctionality();
    }

    initializeTutorialData() {
        return [
            {
                title: "Getting Started",
                content: `
                    <div class="tutorial-step active">
                        <h5><i class="fas fa-play-circle me-2"></i>Welcome to Location Input</h5>
                        <div class="step-content">
                            <p>This tutorial will guide you through the different ways to input your farm location. 
                            You can use GPS, coordinates, address, or map selection.</p>
                            <div class="step-demo">
                                <i class="fas fa-map-marker-alt fa-3x text-primary mb-3"></i>
                                <p>Let's start by learning about GPS location input.</p>
                            </div>
                        </div>
                    </div>
                `
            },
            {
                title: "GPS Location",
                content: `
                    <div class="tutorial-step">
                        <h5><i class="fas fa-satellite me-2"></i>Using GPS Location</h5>
                        <div class="step-content">
                            <p>GPS location is the most accurate method when you're physically at your farm.</p>
                            <div class="step-tips">
                                <h6><i class="fas fa-lightbulb me-2"></i>Best Practices:</h6>
                                <ul>
                                    <li>Enable high accuracy mode in your device settings</li>
                                    <li>Go outdoors with a clear view of the sky</li>
                                    <li>Wait for GPS to acquire satellites (10-30 seconds)</li>
                                    <li>Check the accuracy indicator before proceeding</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `
            },
            {
                title: "Coordinate Input",
                content: `
                    <div class="tutorial-step">
                        <h5><i class="fas fa-keyboard me-2"></i>Manual Coordinate Entry</h5>
                        <div class="step-content">
                            <p>If GPS isn't available, you can enter coordinates manually.</p>
                            <div class="step-tips">
                                <h6><i class="fas fa-info-circle me-2"></i>Supported Formats:</h6>
                                <ul>
                                    <li><strong>Decimal Degrees:</strong> 40.7128, -74.0060</li>
                                    <li><strong>Degrees Minutes Seconds:</strong> 40°42'46"N, 74°0'22"W</li>
                                    <li><strong>UTM Coordinates:</strong> Zone 18T, 583000E, 4507000N</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `
            },
            {
                title: "Address Input",
                content: `
                    <div class="tutorial-step">
                        <h5><i class="fas fa-home me-2"></i>Address-Based Input</h5>
                        <div class="step-content">
                            <p>Enter your farm address for automatic coordinate conversion.</p>
                            <div class="step-tips">
                                <h6><i class="fas fa-search me-2"></i>Tips for Rural Addresses:</h6>
                                <ul>
                                    <li>Try "RR 1 Box 123" for rural routes</li>
                                    <li>Use "HC 1 Box 456" for highway contracts</li>
                                    <li>Include county and state information</li>
                                    <li>Use nearby landmarks if address is unclear</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `
            },
            {
                title: "Map Selection",
                content: `
                    <div class="tutorial-step">
                        <h5><i class="fas fa-map me-2"></i>Interactive Map Selection</h5>
                        <div class="step-content">
                            <p>Use the interactive map to pinpoint your exact farm location.</p>
                            <div class="step-tips">
                                <h6><i class="fas fa-hand-pointer me-2"></i>Map Controls:</h6>
                                <ul>
                                    <li><strong>Tap:</strong> Select location on map</li>
                                    <li><strong>Pinch:</strong> Zoom in/out for precision</li>
                                    <li><strong>Drag:</strong> Pan around the map</li>
                                    <li><strong>Search:</strong> Find your area quickly</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                `
            }
        ];
    }

    initializeEventListeners() {
        // Tutorial navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-tutorial-action]')) {
                const action = e.target.getAttribute('data-tutorial-action');
                this.handleTutorialAction(action);
            }
        });

        // Contextual help triggers
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('[data-help-trigger]')) {
                this.showContextualHelp(e.target);
            }
        });

        document.addEventListener('mouseleave', (e) => {
            if (e.target.matches('[data-help-trigger]')) {
                setTimeout(() => this.hideContextualHelp(), 100);
            }
        });

        // Search functionality
        const searchInputs = document.querySelectorAll('#troubleshootingSearch, #faqSearch');
        searchInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.performSearch(e.target.value, e.target.id);
            });
        });

        // Chat functionality
        document.addEventListener('keypress', (e) => {
            if (e.target.id === 'chatInput' && e.key === 'Enter') {
                this.sendChatMessage();
            }
        });
    }

    initializeContextualHelp() {
        // Add help triggers to form elements
        const formElements = document.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            if (!element.hasAttribute('data-help-trigger')) {
                element.setAttribute('data-help-trigger', 'true');
                element.setAttribute('data-help-content', this.getContextualHelpContent(element));
            }
        });
    }

    getContextualHelpContent(element) {
        const helpContent = {
            'address-input': 'Enter your farm address. Try rural route format (RR 1 Box 123) for rural addresses.',
            'latitude-input': 'Enter latitude in decimal degrees (e.g., 40.7128). Must be between -90 and 90.',
            'longitude-input': 'Enter longitude in decimal degrees (e.g., -74.0060). Must be between -180 and 180.',
            'mgrs-coordinate': 'Enter MGRS coordinate in format: Zone Grid Easting Northing (e.g., 18T VK 83000 5070000)',
            'gps-accuracy': 'GPS accuracy in meters. Lower numbers are more accurate. Aim for under 10 meters.',
            'farm-name': 'Enter a descriptive name for your farm location (e.g., "Main Farm", "North Field")'
        };

        return helpContent[element.id] || 'This field is used to specify your farm location.';
    }

    initializeSearchFunctionality() {
        // Initialize search with common terms
        this.searchIndex = this.buildSearchIndex();
    }

    buildSearchIndex() {
        return {
            'gps': ['gps', 'location', 'satellite', 'accuracy', 'coordinates'],
            'coordinates': ['coordinates', 'latitude', 'longitude', 'decimal', 'degrees', 'utm', 'mgrs'],
            'address': ['address', 'rural', 'route', 'rr', 'hc', 'highway', 'contract'],
            'map': ['map', 'selection', 'pinch', 'zoom', 'pan', 'tap'],
            'troubleshooting': ['error', 'problem', 'issue', 'not working', 'invalid', 'failed'],
            'accuracy': ['accurate', 'precision', 'meters', 'feet', 'distance']
        };
    }

    // Tutorial Methods
    showInteractiveTutorial() {
        const modal = new bootstrap.Modal(document.getElementById('interactiveTutorialModal'));
        this.currentTutorialStep = 0;
        this.updateTutorialDisplay();
        modal.show();
    }

    nextTutorialStep() {
        if (this.currentTutorialStep < this.totalTutorialSteps - 1) {
            this.currentTutorialStep++;
            this.updateTutorialDisplay();
        } else {
            this.completeTutorial();
        }
    }

    previousTutorialStep() {
        if (this.currentTutorialStep > 0) {
            this.currentTutorialStep--;
            this.updateTutorialDisplay();
        }
    }

    updateTutorialDisplay() {
        const progressBar = document.getElementById('tutorialProgress');
        const currentStepSpan = document.getElementById('currentStep');
        const totalStepsSpan = document.getElementById('totalSteps');
        const tutorialTitle = document.getElementById('tutorialTitle');
        const tutorialContent = document.getElementById('tutorialContent');
        const prevBtn = document.getElementById('prevStepBtn');
        const nextBtn = document.getElementById('nextStepBtn');

        // Update progress
        const progress = ((this.currentTutorialStep + 1) / this.totalTutorialSteps) * 100;
        progressBar.style.width = `${progress}%`;

        // Update step indicators
        currentStepSpan.textContent = this.currentTutorialStep + 1;
        totalStepsSpan.textContent = this.totalTutorialSteps;

        // Update content
        const stepData = this.tutorialData[this.currentTutorialStep];
        tutorialTitle.textContent = stepData.title;
        tutorialContent.innerHTML = stepData.content;

        // Update navigation buttons
        prevBtn.disabled = this.currentTutorialStep === 0;
        
        if (this.currentTutorialStep === this.totalTutorialSteps - 1) {
            nextBtn.innerHTML = 'Complete <i class="fas fa-check ms-1"></i>';
        } else {
            nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right ms-1"></i>';
        }
    }

    completeTutorial() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('interactiveTutorialModal'));
        modal.hide();
        
        // Show completion message
        this.showSuccessMessage('Tutorial completed! You\'re now ready to input your farm location.');
        
        // Track tutorial completion
        this.trackEvent('tutorial_completed', {
            steps_completed: this.totalTutorialSteps,
            completion_time: Date.now()
        });
    }

    // Contextual Help Methods
    showContextualHelp(element) {
        const tooltip = document.getElementById('contextualHelpTooltip');
        const tooltipTitle = document.getElementById('tooltipTitle');
        const tooltipBody = document.getElementById('tooltipBody');
        
        const helpContent = element.getAttribute('data-help-content') || 'Help information';
        const fieldName = element.getAttribute('data-help-title') || element.name || element.id || 'Field';
        
        tooltipTitle.textContent = fieldName;
        tooltipBody.textContent = helpContent;
        
        // Position tooltip
        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left}px`;
        tooltip.style.top = `${rect.bottom + 10}px`;
        tooltip.style.display = 'block';
        
        // Add active class to element
        element.classList.add('help-active');
    }

    hideContextualHelp() {
        const tooltip = document.getElementById('contextualHelpTooltip');
        tooltip.style.display = 'none';
        
        // Remove active class from all elements
        document.querySelectorAll('.help-active').forEach(el => {
            el.classList.remove('help-active');
        });
    }

    showFullHelp() {
        this.hideContextualHelp();
        this.showInteractiveTutorial();
    }

    // Troubleshooting Methods
    showTroubleshooting() {
        const modal = new bootstrap.Modal(document.getElementById('troubleshootingModal'));
        modal.show();
    }

    toggleTroubleshootingSection(issueType) {
        const section = document.querySelector(`[data-issue="${issueType}"]`);
        const content = section.querySelector('.issue-content');
        const header = section.querySelector('.issue-header');
        const icon = header.querySelector('.fa-chevron-down');
        
        const isActive = content.classList.contains('active');
        
        // Close all other sections
        document.querySelectorAll('.issue-content.active').forEach(el => {
            el.classList.remove('active');
            el.parentElement.querySelector('.fa-chevron-down').style.transform = 'rotate(0deg)';
        });
        
        if (!isActive) {
            content.classList.add('active');
            icon.style.transform = 'rotate(180deg)';
        }
    }

    performSearch(query, searchType) {
        if (!query.trim()) {
            this.clearSearchResults(searchType);
            return;
        }

        const searchTerms = query.toLowerCase().split(' ');
        let results = [];

        if (searchType === 'troubleshootingSearch') {
            results = this.searchTroubleshooting(searchTerms);
        } else if (searchType === 'faqSearch') {
            results = this.searchFAQ(searchTerms);
        }

        this.displaySearchResults(results, searchType);
    }

    searchTroubleshooting(searchTerms) {
        const sections = document.querySelectorAll('.troubleshooting-section');
        const results = [];

        sections.forEach(section => {
            const issueType = section.getAttribute('data-issue');
            const header = section.querySelector('.issue-header h6').textContent.toLowerCase();
            const solutions = Array.from(section.querySelectorAll('.solution-item')).map(el => 
                el.querySelector('h6').textContent.toLowerCase()
            );

            const relevance = this.calculateRelevance(searchTerms, [header, ...solutions]);
            if (relevance > 0) {
                results.push({ section, relevance, issueType });
            }
        });

        return results.sort((a, b) => b.relevance - a.relevance);
    }

    searchFAQ(searchTerms) {
        const items = document.querySelectorAll('.faq-item');
        const results = [];

        items.forEach(item => {
            const question = item.querySelector('.faq-question h6').textContent.toLowerCase();
            const answer = item.querySelector('.faq-answer').textContent.toLowerCase();

            const relevance = this.calculateRelevance(searchTerms, [question, answer]);
            if (relevance > 0) {
                results.push({ item, relevance });
            }
        });

        return results.sort((a, b) => b.relevance - a.relevance);
    }

    calculateRelevance(searchTerms, content) {
        let relevance = 0;
        content.forEach(text => {
            searchTerms.forEach(term => {
                if (text.includes(term)) {
                    relevance += 1;
                }
            });
        });
        return relevance;
    }

    displaySearchResults(results, searchType) {
        if (searchType === 'troubleshootingSearch') {
            this.highlightTroubleshootingResults(results);
        } else if (searchType === 'faqSearch') {
            this.highlightFAQResults(results);
        }
    }

    highlightTroubleshootingResults(results) {
        // Hide all sections first
        document.querySelectorAll('.troubleshooting-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show relevant sections
        results.forEach(result => {
            result.section.style.display = 'block';
            result.section.classList.add('search-highlight');
        });

        if (results.length === 0) {
            this.showNoResultsMessage('troubleshooting');
        }
    }

    highlightFAQResults(results) {
        // Hide all items first
        document.querySelectorAll('.faq-item').forEach(item => {
            item.style.display = 'none';
        });

        // Show relevant items
        results.forEach(result => {
            result.item.style.display = 'block';
            result.item.classList.add('search-highlight');
        });

        if (results.length === 0) {
            this.showNoResultsMessage('faq');
        }
    }

    clearSearchResults(searchType) {
        if (searchType === 'troubleshootingSearch') {
            document.querySelectorAll('.troubleshooting-section').forEach(section => {
                section.style.display = 'block';
                section.classList.remove('search-highlight');
            });
        } else if (searchType === 'faqSearch') {
            document.querySelectorAll('.faq-item').forEach(item => {
                item.style.display = 'block';
                item.classList.remove('search-highlight');
            });
        }
    }

    showNoResultsMessage(type) {
        const message = document.createElement('div');
        message.className = 'alert alert-info';
        message.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            No results found. Try different keywords or contact support for assistance.
        `;
        
        const container = type === 'troubleshooting' ? 
            document.querySelector('.troubleshooting-sections') : 
            document.querySelector('.faq-categories');
        
        container.appendChild(message);
        
        setTimeout(() => message.remove(), 5000);
    }

    // FAQ Methods
    showFAQ() {
        const modal = new bootstrap.Modal(document.getElementById('faqModal'));
        modal.show();
    }

    toggleFaqCategory(category) {
        const items = document.getElementById(`faq-${category}`);
        const title = document.querySelector(`[onclick="toggleFaqCategory('${category}')"]`);
        const icon = title.querySelector('.fa-chevron-down');
        
        const isActive = items.classList.contains('active');
        
        // Close all other categories
        document.querySelectorAll('.faq-items.active').forEach(el => {
            el.classList.remove('active');
            el.parentElement.querySelector('.fa-chevron-down').style.transform = 'rotate(0deg)';
        });
        
        if (!isActive) {
            items.classList.add('active');
            icon.style.transform = 'rotate(180deg)';
        }
    }

    toggleFaqItem(itemId) {
        const answer = document.getElementById(itemId);
        const question = answer.previousElementSibling;
        const icon = question.querySelector('.fa-chevron-down');
        
        const isActive = answer.classList.contains('active');
        
        // Close all other items in the same category
        const category = answer.closest('.faq-items');
        category.querySelectorAll('.faq-answer.active').forEach(el => {
            el.classList.remove('active');
            el.previousElementSibling.querySelector('.fa-chevron-down').style.transform = 'rotate(0deg)';
        });
        
        if (!isActive) {
            answer.classList.add('active');
            icon.style.transform = 'rotate(180deg)';
        }
    }

    // Support Ticket Methods
    showSupportTicket() {
        const modal = new bootstrap.Modal(document.getElementById('supportTicketModal'));
        modal.show();
    }

    submitSupportTicket() {
        const form = document.getElementById('supportTicketForm');
        const formData = new FormData(form);
        
        const ticket = {
            id: Date.now(),
            category: formData.get('supportCategory'),
            priority: formData.get('supportPriority'),
            subject: formData.get('supportSubject'),
            description: formData.get('supportDescription'),
            contact: formData.get('supportContact'),
            attachLogs: formData.get('supportAttachLogs') === 'on',
            timestamp: new Date().toISOString(),
            status: 'open'
        };

        this.supportTickets.push(ticket);
        
        // Simulate API call
        this.simulateTicketSubmission(ticket);
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('supportTicketModal'));
        modal.hide();
        
        // Reset form
        form.reset();
        
        // Show success message
        this.showSuccessMessage(`Support ticket #${ticket.id} has been submitted successfully. We'll contact you at ${ticket.contact} within 24 hours.`);
        
        // Track event
        this.trackEvent('support_ticket_submitted', {
            category: ticket.category,
            priority: ticket.priority
        });
    }

    simulateTicketSubmission(ticket) {
        // Simulate API call delay
        setTimeout(() => {
            console.log('Support ticket submitted:', ticket);
            // In a real implementation, this would make an API call
        }, 1000);
    }

    // Live Chat Methods
    showChatWidget() {
        const widget = document.getElementById('liveChatWidget');
        const toggleBtn = document.getElementById('chatToggleBtn');
        
        widget.style.display = 'flex';
        toggleBtn.style.display = 'none';
        this.chatOpen = true;
        
        // Focus on chat input
        setTimeout(() => {
            document.getElementById('chatInput').focus();
        }, 100);
    }

    toggleChatWindow() {
        const window = document.getElementById('chatWindow');
        const isVisible = window.style.display !== 'none';
        window.style.display = isVisible ? 'none' : 'flex';
    }

    minimizeChat() {
        const window = document.getElementById('chatWindow');
        window.style.display = 'none';
    }

    closeChat() {
        const widget = document.getElementById('liveChatWidget');
        const toggleBtn = document.getElementById('chatToggleBtn');
        
        widget.style.display = 'none';
        toggleBtn.style.display = 'flex';
        this.chatOpen = false;
    }

    sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addChatMessage(message, 'user');
        input.value = '';
        
        // Simulate bot response
        setTimeout(() => {
            const response = this.generateBotResponse(message);
            this.addChatMessage(response, 'bot');
        }, 1000);
    }

    addChatMessage(message, sender) {
        const messagesContainer = document.getElementById('chatMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${sender}-message`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageElement.innerHTML = `
            <div class="message-content">
                <p>${message}</p>
            </div>
            <div class="message-time">${timeString}</div>
        `;
        
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        this.chatMessages.push({ message, sender, timestamp: now });
    }

    generateBotResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        if (message.includes('gps') || message.includes('location')) {
            return "For GPS issues, try enabling high accuracy mode in your device settings and ensure you're outdoors with a clear view of the sky. Is your GPS not working at all, or is it inaccurate?";
        } else if (message.includes('coordinate') || message.includes('latitude') || message.includes('longitude')) {
            return "For coordinate input, make sure latitude is between -90 and 90, and longitude is between -180 and 180. Are you getting an 'invalid coordinates' error?";
        } else if (message.includes('address') || message.includes('rural')) {
            return "For rural addresses, try using 'RR 1 Box 123' format for rural routes or 'HC 1 Box 456' for highway contracts. Include county and state information for better results.";
        } else if (message.includes('map') || message.includes('selection')) {
            return "For map selection, tap on the map to select your location. Use pinch gestures to zoom in/out and drag to pan around. Are you having trouble with the map loading?";
        } else if (message.includes('help') || message.includes('support')) {
            return "I'm here to help! You can also check our FAQ section or submit a support ticket for more detailed assistance. What specific issue are you experiencing?";
        } else {
            return "I understand you're having an issue. Could you provide more details about what's not working? I can help with GPS, coordinates, address input, or map selection problems.";
        }
    }

    handleChatKeyPress(event) {
        if (event.key === 'Enter') {
            this.sendChatMessage();
        }
    }

    // Utility Methods
    showSuccessMessage(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    showErrorMessage(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    trackEvent(eventName, data) {
        // In a real implementation, this would send analytics data
        console.log('Event tracked:', eventName, data);
        
        // Store locally for demo purposes
        const events = JSON.parse(localStorage.getItem('userGuidanceEvents') || '[]');
        events.push({
            event: eventName,
            data: data,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('userGuidanceEvents', JSON.stringify(events));
    }

    handleTutorialAction(action) {
        switch (action) {
            case 'start':
                this.showInteractiveTutorial();
                break;
            case 'next':
                this.nextTutorialStep();
                break;
            case 'previous':
                this.previousTutorialStep();
                break;
            case 'complete':
                this.completeTutorial();
                break;
        }
    }
}

// Global functions for HTML onclick handlers
let userGuidanceSystem;

function initializeUserGuidanceSystem() {
    userGuidanceSystem = new UserGuidanceSystem();
}

function showInteractiveTutorial() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showInteractiveTutorial();
    }
}

function showTroubleshooting() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showTroubleshooting();
    }
}

function showFAQ() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showFAQ();
    }
}

function showSupportTicket() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showSupportTicket();
    }
}

function contactSupport() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showSupportTicket();
    }
}

function submitSupportTicket() {
    if (userGuidanceSystem) {
        userGuidanceSystem.submitSupportTicket();
    }
}

function showChatWidget() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showChatWidget();
    }
}

function toggleChatWindow() {
    if (userGuidanceSystem) {
        userGuidanceSystem.toggleChatWindow();
    }
}

function minimizeChat() {
    if (userGuidanceSystem) {
        userGuidanceSystem.minimizeChat();
    }
}

function closeChat() {
    if (userGuidanceSystem) {
        userGuidanceSystem.closeChat();
    }
}

function sendChatMessage() {
    if (userGuidanceSystem) {
        userGuidanceSystem.sendChatMessage();
    }
}

function handleChatKeyPress(event) {
    if (userGuidanceSystem) {
        userGuidanceSystem.handleChatKeyPress(event);
    }
}

function nextTutorialStep() {
    if (userGuidanceSystem) {
        userGuidanceSystem.nextTutorialStep();
    }
}

function previousTutorialStep() {
    if (userGuidanceSystem) {
        userGuidanceSystem.previousTutorialStep();
    }
}

function toggleTroubleshootingSection(issueType) {
    if (userGuidanceSystem) {
        userGuidanceSystem.toggleTroubleshootingSection(issueType);
    }
}

function toggleFaqCategory(category) {
    if (userGuidanceSystem) {
        userGuidanceSystem.toggleFaqCategory(category);
    }
}

function toggleFaqItem(itemId) {
    if (userGuidanceSystem) {
        userGuidanceSystem.toggleFaqItem(itemId);
    }
}

function hideContextualHelp() {
    if (userGuidanceSystem) {
        userGuidanceSystem.hideContextualHelp();
    }
}

function showFullHelp() {
    if (userGuidanceSystem) {
        userGuidanceSystem.showFullHelp();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeUserGuidanceSystem);