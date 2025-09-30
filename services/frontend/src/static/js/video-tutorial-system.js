/**
 * Video Tutorial Integration System
 * TICKET-008_farm-location-input-14.2: Add comprehensive user guidance and support
 */

class VideoTutorialSystem {
    constructor() {
        this.videoTutorials = this.initializeVideoTutorials();
        this.currentVideo = null;
        this.playbackHistory = [];
        this.userProgress = this.loadUserProgress();
        
        this.initializeVideoPlayer();
        this.initializeEventListeners();
    }

    initializeVideoTutorials() {
        return [
            {
                id: 'gps-location-basics',
                title: 'GPS Location Input Basics',
                description: 'Learn how to use GPS location input for accurate farm location entry',
                duration: '3:45',
                thumbnail: '/static/images/video-thumbnails/gps-basics.jpg',
                videoUrl: '/static/videos/gps-location-basics.mp4',
                transcript: [
                    { time: '0:00', text: 'Welcome to GPS location input tutorial' },
                    { time: '0:15', text: 'First, ensure location services are enabled' },
                    { time: '0:30', text: 'Go outdoors with a clear view of the sky' },
                    { time: '0:45', text: 'Tap the GPS button to start location detection' },
                    { time: '1:00', text: 'Wait for GPS to acquire satellites' },
                    { time: '1:15', text: 'Check the accuracy indicator' },
                    { time: '1:30', text: 'Tap to confirm your location' },
                    { time: '1:45', text: 'Review the location details' },
                    { time: '2:00', text: 'Save your farm location' }
                ],
                tags: ['gps', 'location', 'basics', 'mobile'],
                difficulty: 'beginner',
                category: 'location-input'
            },
            {
                id: 'coordinate-input-guide',
                title: 'Manual Coordinate Entry Guide',
                description: 'Step-by-step guide for entering coordinates manually',
                duration: '4:20',
                thumbnail: '/static/images/video-thumbnails/coordinate-input.jpg',
                videoUrl: '/static/videos/coordinate-input-guide.mp4',
                transcript: [
                    { time: '0:00', text: 'Manual coordinate entry tutorial' },
                    { time: '0:15', text: 'Understanding latitude and longitude' },
                    { time: '0:30', text: 'Decimal degrees format explained' },
                    { time: '0:45', text: 'Entering latitude values' },
                    { time: '1:00', text: 'Entering longitude values' },
                    { time: '1:15', text: 'Coordinate validation' },
                    { time: '1:30', text: 'Alternative coordinate formats' },
                    { time: '1:45', text: 'UTM coordinate system' },
                    { time: '2:00', text: 'MGRS coordinate format' },
                    { time: '2:15', text: 'Converting between formats' },
                    { time: '2:30', text: 'Common coordinate mistakes' },
                    { time: '2:45', text: 'Verifying your coordinates' }
                ],
                tags: ['coordinates', 'latitude', 'longitude', 'manual-input'],
                difficulty: 'intermediate',
                category: 'location-input'
            },
            {
                id: 'address-input-rural',
                title: 'Rural Address Input Tips',
                description: 'Special techniques for entering rural farm addresses',
                duration: '3:15',
                thumbnail: '/static/images/video-thumbnails/rural-address.jpg',
                videoUrl: '/static/videos/address-input-rural.mp4',
                transcript: [
                    { time: '0:00', text: 'Rural address input tutorial' },
                    { time: '0:15', text: 'Understanding rural addressing systems' },
                    { time: '0:30', text: 'Rural Route (RR) format' },
                    { time: '0:45', text: 'Highway Contract (HC) format' },
                    { time: '1:00', text: 'Box number conventions' },
                    { time: '1:15', text: 'County and state information' },
                    { time: '1:30', text: 'Using landmarks and intersections' },
                    { time: '1:45', text: 'Address autocomplete features' },
                    { time: '2:00', text: 'Verifying address suggestions' },
                    { time: '2:15', text: 'Alternative address formats' },
                    { time: '2:30', text: 'Troubleshooting address issues' }
                ],
                tags: ['address', 'rural', 'farm', 'location'],
                difficulty: 'beginner',
                category: 'location-input'
            },
            {
                id: 'map-selection-mobile',
                title: 'Mobile Map Selection',
                description: 'Using interactive maps on mobile devices for location selection',
                duration: '4:50',
                thumbnail: '/static/images/video-thumbnails/map-selection.jpg',
                videoUrl: '/static/videos/map-selection-mobile.mp4',
                transcript: [
                    { time: '0:00', text: 'Mobile map selection tutorial' },
                    { time: '0:15', text: 'Opening the interactive map' },
                    { time: '0:30', text: 'Map navigation gestures' },
                    { time: '0:45', text: 'Pinch to zoom functionality' },
                    { time: '1:00', text: 'Pan and drag movements' },
                    { time: '1:15', text: 'Finding your farm location' },
                    { time: '1:30', text: 'Using map search features' },
                    { time: '1:45', text: 'Satellite view vs street view' },
                    { time: '2:00', text: 'Precise location selection' },
                    { time: '2:15', text: 'Adjusting map zoom level' },
                    { time: '2:30', text: 'Confirming your selection' },
                    { time: '2:45', text: 'Reviewing selected coordinates' },
                    { time: '3:00', text: 'Mobile-specific tips' },
                    { time: '3:15', text: 'Battery optimization' },
                    { time: '3:30', text: 'Offline map usage' }
                ],
                tags: ['map', 'mobile', 'selection', 'interactive'],
                difficulty: 'beginner',
                category: 'location-input'
            },
            {
                id: 'troubleshooting-common-issues',
                title: 'Troubleshooting Common Issues',
                description: 'Solutions for common location input problems',
                duration: '5:30',
                thumbnail: '/static/images/video-thumbnails/troubleshooting.jpg',
                videoUrl: '/static/videos/troubleshooting-common-issues.mp4',
                transcript: [
                    { time: '0:00', text: 'Troubleshooting location input issues' },
                    { time: '0:15', text: 'GPS not working problems' },
                    { time: '0:30', text: 'Location services settings' },
                    { time: '0:45', text: 'High accuracy mode setup' },
                    { time: '1:00', text: 'Outdoor vs indoor GPS' },
                    { time: '1:15', text: 'Invalid coordinate errors' },
                    { time: '1:30', text: 'Coordinate range validation' },
                    { time: '1:45', text: 'Address not found issues' },
                    { time: '2:00', text: 'Rural address alternatives' },
                    { time: '2:15', text: 'Network connectivity problems' },
                    { time: '2:30', text: 'Slow loading solutions' },
                    { time: '2:45', text: 'Offline mode usage' },
                    { time: '3:00', text: 'Browser compatibility' },
                    { time: '3:15', text: 'Mobile device optimization' },
                    { time: '3:30', text: 'Cache and storage issues' },
                    { time: '3:45', text: 'When to contact support' }
                ],
                tags: ['troubleshooting', 'gps', 'coordinates', 'address', 'issues'],
                difficulty: 'intermediate',
                category: 'troubleshooting'
            }
        ];
    }

    initializeVideoPlayer() {
        // Create video player container
        this.videoContainer = document.createElement('div');
        this.videoContainer.className = 'video-tutorial-container';
        this.videoContainer.innerHTML = `
            <div class="video-player-wrapper">
                <video id="tutorialVideo" class="tutorial-video" controls preload="metadata">
                    <source src="" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="video-controls-overlay">
                    <div class="video-info">
                        <h5 id="videoTitle"></h5>
                        <p id="videoDescription"></p>
                    </div>
                    <div class="video-progress">
                        <div class="progress">
                            <div class="progress-bar" id="videoProgressBar" style="width: 0%"></div>
                        </div>
                        <div class="video-time">
                            <span id="currentTime">0:00</span> / <span id="totalTime">0:00</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="video-transcript">
                <h6><i class="fas fa-closed-captioning me-2"></i>Transcript</h6>
                <div class="transcript-content" id="transcriptContent"></div>
            </div>
        `;
    }

    initializeEventListeners() {
        // Video player events
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-video-tutorial]')) {
                const videoId = e.target.getAttribute('data-video-tutorial');
                this.playVideo(videoId);
            }
        });

        // Video progress tracking
        document.addEventListener('timeupdate', (e) => {
            if (e.target.id === 'tutorialVideo') {
                this.updateVideoProgress(e.target);
            }
        });

        // Video completion tracking
        document.addEventListener('ended', (e) => {
            if (e.target.id === 'tutorialVideo') {
                this.handleVideoCompletion();
            }
        });
    }

    showVideoTutorials() {
        const modal = this.createVideoTutorialModal();
        document.body.appendChild(modal);
        
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Clean up when modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    createVideoTutorialModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'videoTutorialModal';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-play-circle me-2"></i>
                            Video Tutorials
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="video-tutorials-grid">
                            ${this.renderVideoTutorials()}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="showInteractiveTutorial()">
                            <i class="fas fa-graduation-cap me-2"></i>
                            Try Interactive Tutorial
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    renderVideoTutorials() {
        return this.videoTutorials.map(tutorial => `
            <div class="video-tutorial-card" data-video-tutorial="${tutorial.id}">
                <div class="video-thumbnail">
                    <img src="${tutorial.thumbnail}" alt="${tutorial.title}" 
                         onerror="this.src='/static/images/video-thumbnails/default.jpg'">
                    <div class="play-button">
                        <i class="fas fa-play"></i>
                    </div>
                    <div class="video-duration">${tutorial.duration}</div>
                </div>
                <div class="video-info">
                    <h6 class="video-title">${tutorial.title}</h6>
                    <p class="video-description">${tutorial.description}</p>
                    <div class="video-meta">
                        <span class="badge bg-${this.getDifficultyColor(tutorial.difficulty)}">${tutorial.difficulty}</span>
                        <span class="video-category">${tutorial.category}</span>
                    </div>
                    <div class="video-progress-indicator">
                        ${this.renderProgressIndicator(tutorial.id)}
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderProgressIndicator(videoId) {
        const progress = this.userProgress[videoId] || 0;
        if (progress === 0) {
            return '<small class="text-muted">Not started</small>';
        } else if (progress === 100) {
            return '<small class="text-success"><i class="fas fa-check-circle me-1"></i>Completed</small>';
        } else {
            return `
                <div class="progress" style="height: 4px;">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>
                <small class="text-muted">${progress}% watched</small>
            `;
        }
    }

    getDifficultyColor(difficulty) {
        const colors = {
            'beginner': 'success',
            'intermediate': 'warning',
            'advanced': 'danger'
        };
        return colors[difficulty] || 'secondary';
    }

    playVideo(videoId) {
        const tutorial = this.videoTutorials.find(t => t.id === videoId);
        if (!tutorial) return;

        this.currentVideo = tutorial;
        
        // Create video player modal
        const videoModal = this.createVideoPlayerModal(tutorial);
        document.body.appendChild(videoModal);
        
        const bootstrapModal = new bootstrap.Modal(videoModal);
        bootstrapModal.show();
        
        // Load video
        const video = videoModal.querySelector('#tutorialVideo');
        video.src = tutorial.videoUrl;
        video.load();
        
        // Load transcript
        this.loadTranscript(tutorial);
        
        // Track video start
        this.trackVideoEvent('start', tutorial.id);
        
        // Clean up when modal is hidden
        videoModal.addEventListener('hidden.bs.modal', () => {
            videoModal.remove();
            this.currentVideo = null;
        });
    }

    createVideoPlayerModal(tutorial) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'videoPlayerModal';
        modal.setAttribute('tabindex', '-1');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-dark text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-play-circle me-2"></i>
                            ${tutorial.title}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body p-0">
                        <div class="video-player-container">
                            <video id="tutorialVideo" class="tutorial-video" controls preload="metadata">
                                <source src="${tutorial.videoUrl}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                        <div class="video-info-panel">
                            <div class="row">
                                <div class="col-md-8">
                                    <h6>Description</h6>
                                    <p>${tutorial.description}</p>
                                    <div class="video-meta">
                                        <span class="badge bg-${this.getDifficultyColor(tutorial.difficulty)} me-2">${tutorial.difficulty}</span>
                                        <span class="text-muted">Duration: ${tutorial.duration}</span>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <h6>Transcript</h6>
                                    <div class="transcript-content" id="transcriptContent" style="max-height: 200px; overflow-y: auto;">
                                        <!-- Transcript will be loaded here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="showRelatedTutorials('${tutorial.id}')">
                            <i class="fas fa-list me-2"></i>
                            More Tutorials
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    loadTranscript(tutorial) {
        const transcriptContent = document.getElementById('transcriptContent');
        if (!transcriptContent) return;

        transcriptContent.innerHTML = tutorial.transcript.map(item => `
            <div class="transcript-item" data-time="${item.time}">
                <small class="text-muted">${item.time}</small>
                <p class="mb-1">${item.text}</p>
            </div>
        `).join('');
    }

    updateVideoProgress(video) {
        if (!this.currentVideo) return;

        const progress = (video.currentTime / video.duration) * 100;
        this.userProgress[this.currentVideo.id] = Math.round(progress);
        
        // Save progress
        this.saveUserProgress();
        
        // Update progress bar if visible
        const progressBar = document.getElementById('videoProgressBar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    handleVideoCompletion() {
        if (!this.currentVideo) return;

        // Mark as completed
        this.userProgress[this.currentVideo.id] = 100;
        this.saveUserProgress();
        
        // Track completion
        this.trackVideoEvent('complete', this.currentVideo.id);
        
        // Show completion message
        this.showCompletionMessage();
        
        // Suggest next video
        this.suggestNextVideo();
    }

    showCompletionMessage() {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.top = '20px';
        alert.style.right = '20px';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            Great job! You've completed "${this.currentVideo.title}". 
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    suggestNextVideo() {
        const nextVideo = this.getNextVideo();
        if (!nextVideo) return;

        const suggestion = document.createElement('div');
        suggestion.className = 'alert alert-info alert-dismissible fade show position-fixed';
        suggestion.style.top = '80px';
        suggestion.style.right = '20px';
        suggestion.style.zIndex = '9999';
        suggestion.innerHTML = `
            <i class="fas fa-lightbulb me-2"></i>
            <strong>Next:</strong> ${nextVideo.title}
            <button type="button" class="btn btn-sm btn-primary ms-2" onclick="playVideo('${nextVideo.id}')">
                Watch Now
            </button>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(suggestion);
        
        setTimeout(() => {
            suggestion.remove();
        }, 10000);
    }

    getNextVideo() {
        const currentIndex = this.videoTutorials.findIndex(t => t.id === this.currentVideo.id);
        if (currentIndex < this.videoTutorials.length - 1) {
            return this.videoTutorials[currentIndex + 1];
        }
        return null;
    }

    trackVideoEvent(event, videoId) {
        // In a real implementation, this would send analytics data
        console.log('Video event tracked:', event, videoId);
        
        // Store locally for demo purposes
        const events = JSON.parse(localStorage.getItem('videoTutorialEvents') || '[]');
        events.push({
            event: event,
            videoId: videoId,
            timestamp: new Date().toISOString()
        });
        localStorage.setItem('videoTutorialEvents', JSON.stringify(events));
    }

    loadUserProgress() {
        return JSON.parse(localStorage.getItem('videoTutorialProgress') || '{}');
    }

    saveUserProgress() {
        localStorage.setItem('videoTutorialProgress', JSON.stringify(this.userProgress));
    }

    getVideoRecommendations() {
        // Return videos based on user progress and preferences
        const completedVideos = Object.keys(this.userProgress).filter(id => this.userProgress[id] === 100);
        const inProgressVideos = Object.keys(this.userProgress).filter(id => this.userProgress[id] > 0 && this.userProgress[id] < 100);
        
        return {
            continue: inProgressVideos.map(id => this.videoTutorials.find(t => t.id === id)),
            next: this.videoTutorials.filter(t => !this.userProgress[t.id] || this.userProgress[t.id] === 0),
            completed: completedVideos.map(id => this.videoTutorials.find(t => t.id === id))
        };
    }
}

// Global functions for HTML onclick handlers
let videoTutorialSystem;

function initializeVideoTutorialSystem() {
    videoTutorialSystem = new VideoTutorialSystem();
}

function showVideoTutorials() {
    if (videoTutorialSystem) {
        videoTutorialSystem.showVideoTutorials();
    }
}

function playVideo(videoId) {
    if (videoTutorialSystem) {
        videoTutorialSystem.playVideo(videoId);
    }
}

function showRelatedTutorials(currentVideoId) {
    if (videoTutorialSystem) {
        // Close current modal and show tutorial list
        const currentModal = bootstrap.Modal.getInstance(document.getElementById('videoPlayerModal'));
        if (currentModal) {
            currentModal.hide();
        }
        
        setTimeout(() => {
            videoTutorialSystem.showVideoTutorials();
        }, 300);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeVideoTutorialSystem);