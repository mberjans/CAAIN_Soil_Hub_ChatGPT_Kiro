/**
 * Help Analytics System
 * TICKET-008_farm-location-input-14.2: Add comprehensive user guidance and support
 */

class HelpAnalyticsSystem {
    constructor() {
        this.analyticsData = this.loadAnalyticsData();
        this.sessionMetrics = this.initializeSessionMetrics();
        this.helpUsagePatterns = this.initializeHelpUsagePatterns();
        
        this.initializeEventTracking();
        this.startPeriodicReporting();
    }

    initializeSessionMetrics() {
        return {
            sessionId: this.generateSessionId(),
            startTime: Date.now(),
            helpInteractions: [],
            userJourney: [],
            errorEvents: [],
            performanceMetrics: {
                pageLoadTime: 0,
                helpModalOpenTime: 0,
                searchResponseTime: 0,
                videoLoadTime: 0
            },
            userBehavior: {
                helpButtonClicks: 0,
                tutorialStarts: 0,
                tutorialCompletions: 0,
                faqSearches: 0,
                troubleshootingSearches: 0,
                supportTicketSubmissions: 0,
                chatInteractions: 0,
                videoPlays: 0,
                videoCompletions: 0
            }
        };
    }

    initializeHelpUsagePatterns() {
        return {
            commonIssues: new Map(),
            helpEffectiveness: new Map(),
            userPaths: [],
            searchTerms: new Map(),
            timeToResolution: [],
            abandonmentPoints: []
        };
    }

    initializeEventTracking() {
        // Track help button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="showInteractiveTutorial"]')) {
                this.trackHelpInteraction('tutorial_start', { method: 'button_click' });
            } else if (e.target.matches('[onclick*="showVideoTutorials"]')) {
                this.trackHelpInteraction('video_tutorial_start', { method: 'button_click' });
            } else if (e.target.matches('[onclick*="showFAQ"]')) {
                this.trackHelpInteraction('faq_open', { method: 'button_click' });
            } else if (e.target.matches('[onclick*="showTroubleshooting"]')) {
                this.trackHelpInteraction('troubleshooting_open', { method: 'button_click' });
            } else if (e.target.matches('[onclick*="showSupportTicket"]')) {
                this.trackHelpInteraction('support_ticket_start', { method: 'button_click' });
            } else if (e.target.matches('[onclick*="showChatWidget"]')) {
                this.trackHelpInteraction('chat_start', { method: 'button_click' });
            }
        });

        // Track search interactions
        document.addEventListener('input', (e) => {
            if (e.target.matches('#troubleshootingSearch, #faqSearch')) {
                this.trackSearchInteraction(e.target.id, e.target.value);
            }
        });

        // Track modal interactions
        document.addEventListener('shown.bs.modal', (e) => {
            this.trackModalOpen(e.target.id);
        });

        document.addEventListener('hidden.bs.modal', (e) => {
            this.trackModalClose(e.target.id);
        });

        // Track video interactions
        document.addEventListener('play', (e) => {
            if (e.target.matches('#tutorialVideo')) {
                this.trackVideoInteraction('play', e.target);
            }
        });

        document.addEventListener('ended', (e) => {
            if (e.target.matches('#tutorialVideo')) {
                this.trackVideoInteraction('complete', e.target);
            }
        });

        // Track tutorial progress
        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="nextTutorialStep"]')) {
                this.trackTutorialProgress('next');
            } else if (e.target.matches('[onclick*="previousTutorialStep"]')) {
                this.trackTutorialProgress('previous');
            }
        });

        // Track contextual help usage
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('[data-help-trigger]')) {
                this.trackContextualHelp('hover', e.target);
            }
        });

        document.addEventListener('click', (e) => {
            if (e.target.matches('[onclick*="showFullHelp"]')) {
                this.trackContextualHelp('click_through', e.target);
            }
        });

        // Track errors
        window.addEventListener('error', (e) => {
            this.trackError(e.error, e.filename, e.lineno);
        });

        // Track performance
        window.addEventListener('load', () => {
            this.trackPerformanceMetrics();
        });
    }

    trackHelpInteraction(type, data = {}) {
        const interaction = {
            type: type,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionMetrics.startTime,
            data: data
        };

        this.sessionMetrics.helpInteractions.push(interaction);
        this.sessionMetrics.userBehavior[this.getBehaviorKey(type)]++;

        // Track user journey
        this.trackUserJourney(type, data);

        // Store in analytics data
        this.analyticsData.helpInteractions.push(interaction);
    }

    trackSearchInteraction(searchType, query) {
        if (!query.trim()) return;

        const searchInteraction = {
            type: 'search',
            searchType: searchType,
            query: query,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionMetrics.startTime
        };

        this.sessionMetrics.helpInteractions.push(searchInteraction);
        this.sessionMetrics.userBehavior[searchType === 'troubleshootingSearch' ? 'troubleshootingSearches' : 'faqSearches']++;

        // Track search terms
        const terms = query.toLowerCase().split(' ');
        terms.forEach(term => {
            const count = this.helpUsagePatterns.searchTerms.get(term) || 0;
            this.helpUsagePatterns.searchTerms.set(term, count + 1);
        });

        this.analyticsData.searchInteractions = this.analyticsData.searchInteractions || [];
        this.analyticsData.searchInteractions.push(searchInteraction);
    }

    trackModalOpen(modalId) {
        const openTime = Date.now();
        this.sessionMetrics.performanceMetrics.helpModalOpenTime = openTime;
        
        this.trackHelpInteraction('modal_open', { modalId: modalId });
    }

    trackModalClose(modalId) {
        const closeTime = Date.now();
        const openTime = this.sessionMetrics.performanceMetrics.helpModalOpenTime;
        const duration = openTime ? closeTime - openTime : 0;
        
        this.trackHelpInteraction('modal_close', { 
            modalId: modalId, 
            duration: duration 
        });
    }

    trackVideoInteraction(action, videoElement) {
        const videoData = {
            action: action,
            currentTime: videoElement.currentTime,
            duration: videoElement.duration,
            timestamp: Date.now()
        };

        this.trackHelpInteraction('video_interaction', videoData);
        
        if (action === 'play') {
            this.sessionMetrics.userBehavior.videoPlays++;
        } else if (action === 'complete') {
            this.sessionMetrics.userBehavior.videoCompletions++;
        }
    }

    trackTutorialProgress(action) {
        this.trackHelpInteraction('tutorial_progress', { action: action });
    }

    trackContextualHelp(action, element) {
        const helpData = {
            action: action,
            element: element.tagName + (element.id ? '#' + element.id : ''),
            helpContent: element.getAttribute('data-help-content'),
            timestamp: Date.now()
        };

        this.trackHelpInteraction('contextual_help', helpData);
    }

    trackUserJourney(action, data) {
        const journeyStep = {
            action: action,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionMetrics.startTime,
            data: data
        };

        this.sessionMetrics.userJourney.push(journeyStep);
    }

    trackError(error, filename, lineno) {
        const errorEvent = {
            type: 'javascript_error',
            error: error.message || error,
            filename: filename,
            lineno: lineno,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionMetrics.startTime
        };

        this.sessionMetrics.errorEvents.push(errorEvent);
        this.analyticsData.errors = this.analyticsData.errors || [];
        this.analyticsData.errors.push(errorEvent);

        // Track common issues
        const errorKey = error.message || error;
        const count = this.helpUsagePatterns.commonIssues.get(errorKey) || 0;
        this.helpUsagePatterns.commonIssues.set(errorKey, count + 1);
    }

    trackPerformanceMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
        
        this.sessionMetrics.performanceMetrics.pageLoadTime = loadTime;
        
        this.trackHelpInteraction('performance_metric', {
            type: 'page_load',
            loadTime: loadTime
        });
    }

    trackHelpEffectiveness(helpType, resolved) {
        const effectiveness = {
            helpType: helpType,
            resolved: resolved,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionMetrics.startTime
        };

        this.helpUsagePatterns.helpEffectiveness.set(helpType, effectiveness);
        this.analyticsData.helpEffectiveness = this.analyticsData.helpEffectiveness || [];
        this.analyticsData.helpEffectiveness.push(effectiveness);
    }

    trackAbandonmentPoint(point, reason) {
        const abandonment = {
            point: point,
            reason: reason,
            timestamp: Date.now(),
            sessionTime: Date.now() - this.sessionMetrics.startTime
        };

        this.helpUsagePatterns.abandonmentPoints.push(abandonment);
        this.analyticsData.abandonmentPoints = this.analyticsData.abandonmentPoints || [];
        this.analyticsData.abandonmentPoints.push(abandonment);
    }

    getBehaviorKey(interactionType) {
        const keyMap = {
            'tutorial_start': 'tutorialStarts',
            'tutorial_complete': 'tutorialCompletions',
            'faq_open': 'faqSearches',
            'troubleshooting_open': 'troubleshootingSearches',
            'support_ticket_start': 'supportTicketSubmissions',
            'chat_start': 'chatInteractions',
            'video_tutorial_start': 'videoPlays'
        };
        return keyMap[interactionType] || 'helpButtonClicks';
    }

    startPeriodicReporting() {
        // Report analytics every 5 minutes
        setInterval(() => {
            this.generateAnalyticsReport();
        }, 300000);

        // Report on page unload
        window.addEventListener('beforeunload', () => {
            this.generateFinalReport();
        });
    }

    generateAnalyticsReport() {
        const report = {
            timestamp: Date.now(),
            sessionId: this.sessionMetrics.sessionId,
            sessionDuration: Date.now() - this.sessionMetrics.startTime,
            metrics: this.sessionMetrics,
            patterns: this.helpUsagePatterns,
            insights: this.generateInsights()
        };

        this.analyticsData.reports = this.analyticsData.reports || [];
        this.analyticsData.reports.push(report);
        
        this.saveAnalyticsData();
        
        // In a real implementation, this would send data to analytics service
        console.log('Analytics report generated:', report);
    }

    generateFinalReport() {
        this.generateAnalyticsReport();
        
        // Track session completion
        this.trackHelpInteraction('session_end', {
            duration: Date.now() - this.sessionMetrics.startTime,
            totalInteractions: this.sessionMetrics.helpInteractions.length,
            userBehavior: this.sessionMetrics.userBehavior
        });
    }

    generateInsights() {
        const insights = {
            mostCommonIssues: this.getMostCommonIssues(),
            mostEffectiveHelp: this.getMostEffectiveHelp(),
            commonSearchTerms: this.getCommonSearchTerms(),
            userJourneyPatterns: this.getUserJourneyPatterns(),
            performanceIssues: this.getPerformanceIssues(),
            recommendations: this.getRecommendations()
        };

        return insights;
    }

    getMostCommonIssues() {
        const issues = Array.from(this.helpUsagePatterns.commonIssues.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([issue, count]) => ({ issue, count }));

        return issues;
    }

    getMostEffectiveHelp() {
        const effectiveness = Array.from(this.helpUsagePatterns.helpEffectiveness.entries())
            .map(([type, data]) => ({ type, ...data }));

        return effectiveness;
    }

    getCommonSearchTerms() {
        const terms = Array.from(this.helpUsagePatterns.searchTerms.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .map(([term, count]) => ({ term, count }));

        return terms;
    }

    getUserJourneyPatterns() {
        // Analyze common user paths through help system
        const paths = this.sessionMetrics.userJourney.map(step => step.action);
        return {
            commonPaths: this.findCommonPaths(paths),
            averageJourneyLength: paths.length,
            commonAbandonmentPoints: this.helpUsagePatterns.abandonmentPoints
        };
    }

    getPerformanceIssues() {
        const metrics = this.sessionMetrics.performanceMetrics;
        const issues = [];

        if (metrics.pageLoadTime > 3000) {
            issues.push('Slow page load time');
        }
        if (metrics.helpModalOpenTime > 1000) {
            issues.push('Slow help modal opening');
        }
        if (metrics.searchResponseTime > 500) {
            issues.push('Slow search response');
        }

        return issues;
    }

    getRecommendations() {
        const recommendations = [];
        const behavior = this.sessionMetrics.userBehavior;

        if (behavior.troubleshootingSearches > behavior.faqSearches) {
            recommendations.push('Consider improving FAQ content or making it more discoverable');
        }

        if (behavior.tutorialStarts > behavior.tutorialCompletions * 2) {
            recommendations.push('Tutorial completion rate is low - consider shortening or improving tutorials');
        }

        if (behavior.supportTicketSubmissions > 0) {
            recommendations.push('Monitor support tickets for common issues that could be prevented');
        }

        const commonIssues = this.getMostCommonIssues();
        if (commonIssues.length > 0) {
            recommendations.push(`Address top issue: ${commonIssues[0].issue}`);
        }

        return recommendations;
    }

    findCommonPaths(paths) {
        // Simple path analysis - in a real implementation, this would be more sophisticated
        const pathCounts = new Map();
        
        for (let i = 0; i < paths.length - 1; i++) {
            const path = `${paths[i]} -> ${paths[i + 1]}`;
            pathCounts.set(path, (pathCounts.get(path) || 0) + 1);
        }

        return Array.from(pathCounts.entries())
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([path, count]) => ({ path, count }));
    }

    generateSessionId() {
        return 'analytics_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    loadAnalyticsData() {
        return JSON.parse(localStorage.getItem('helpAnalyticsData') || '{"helpInteractions": [], "searchInteractions": [], "errors": [], "helpEffectiveness": [], "abandonmentPoints": [], "reports": []}');
    }

    saveAnalyticsData() {
        localStorage.setItem('helpAnalyticsData', JSON.stringify(this.analyticsData));
    }

    getAnalyticsDashboard() {
        return {
            sessionMetrics: this.sessionMetrics,
            helpUsagePatterns: this.helpUsagePatterns,
            insights: this.generateInsights(),
            rawData: this.analyticsData
        };
    }

    exportAnalytics() {
        const data = {
            exportDate: new Date().toISOString(),
            analyticsData: this.analyticsData,
            sessionMetrics: this.sessionMetrics,
            helpUsagePatterns: Object.fromEntries(this.helpUsagePatterns.commonIssues),
            searchTerms: Object.fromEntries(this.helpUsagePatterns.searchTerms)
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `help-analytics-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Global functions for HTML onclick handlers
let helpAnalyticsSystem;

function initializeHelpAnalyticsSystem() {
    helpAnalyticsSystem = new HelpAnalyticsSystem();
}

function trackHelpEffectiveness(helpType, resolved) {
    if (helpAnalyticsSystem) {
        helpAnalyticsSystem.trackHelpEffectiveness(helpType, resolved);
    }
}

function trackAbandonmentPoint(point, reason) {
    if (helpAnalyticsSystem) {
        helpAnalyticsSystem.trackAbandonmentPoint(point, reason);
    }
}

function exportAnalytics() {
    if (helpAnalyticsSystem) {
        helpAnalyticsSystem.exportAnalytics();
    }
}

function getAnalyticsDashboard() {
    if (helpAnalyticsSystem) {
        return helpAnalyticsSystem.getAnalyticsDashboard();
    }
    return null;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeHelpAnalyticsSystem);