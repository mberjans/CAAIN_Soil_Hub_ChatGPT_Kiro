// Mobile Fertilizer Strategy Interface Controller
// Provides mobile-optimized fertilizer strategy planning with offline support

(function () {
    "use strict";

    function MobileFertilizerStrategyApp() {
        this.dom = {};
        this.state = {
            summary: null,
            recommendations: [],
            marketSignals: [],
            alerts: [],
            alertSummary: {
                total: 0,
                high: 0,
                medium: 0
            },
            field: {
                name: "No field selected",
                coordinates: null
            },
            offlineQueue: 0,
            lastPriceUpdate: null,
            lastAlertUpdate: null,
            strategyId: null,
            strategyVersion: 1,
            trackingEntries: [],
            trackingStats: {
                progressPercent: 0,
                lastSyncedAt: null
            }
        };
        this.userId = "mobile-operator";
        this.deviceIntegration = null;
        this.offlineDatabase = null;
        this.chart = null;
        this.cameraStream = null;
        this.cameraOverlay = null;
        this.chartData = {
            profitability: [0, 0, 0],
            sustainability: [0, 0, 0],
            risk: [0, 0, 0],
            logistics: [0, 0, 0]
        };
        this.autoRefreshTimer = null;
        this.queueRefreshTimer = null;

        this.init();
    }

    MobileFertilizerStrategyApp.prototype.init = function () {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", this.initialize.bind(this));
        } else {
            this.initialize();
        }
    };

    MobileFertilizerStrategyApp.prototype.initialize = async function () {
        this.cacheDom();
        this.bindEvents();
        this.initializeTrackingDefaults();
        await this.setupIntegrations();
        this.initializeChart();
        this.updateNetworkIndicators(navigator.onLine);
        await this.loadInitialData();
        this.startAutoRefresh();
        this.startQueueMonitoring();
    };

    MobileFertilizerStrategyApp.prototype.cacheDom = function () {
        this.dom.sectionToggles = document.querySelectorAll(".section-toggle");
        this.dom.quickActions = {
            gps: document.getElementById("captureGpsButton"),
            camera: document.getElementById("captureImageButton"),
            refresh: document.getElementById("refreshStrategyButton"),
            saveOffline: document.getElementById("saveOfflineButton")
        };
        this.dom.sectionMap = {
            summary: document.getElementById("strategySummarySection"),
            market: document.getElementById("marketSignalsSection"),
            actions: document.getElementById("fieldActionsSection"),
            insights: document.getElementById("analysisSection")
        };
        this.dom.summaryCards = {
            projectedRoi: document.getElementById("summaryProjectedRoi"),
            profitStatus: document.getElementById("summaryProfitStatus"),
            strategyCost: document.getElementById("summaryStrategyCost"),
            costStatus: document.getElementById("summaryCostStatus"),
            yieldImpact: document.getElementById("summaryYieldImpact"),
            yieldStatus: document.getElementById("summaryYieldStatus"),
            sustainability: document.getElementById("summarySustainability"),
            sustainabilityStatus: document.getElementById("summarySustainabilityStatus")
        };
        this.dom.recommendationList = document.getElementById("recommendationList");
        this.dom.priceList = document.getElementById("priceTrendList");
        this.dom.priceLastUpdatedLabel = document.getElementById("priceLastUpdatedLabel");
        this.dom.priceRefreshButton = document.getElementById("priceRefreshButton");
        this.dom.priceAlertList = document.getElementById("mobilePriceAlertList");
        this.dom.priceAlertPlaceholder = document.getElementById("priceAlertPlaceholder");
        this.dom.priceAlertLastUpdatedLabel = document.getElementById("priceAlertLastUpdatedLabel");
        this.dom.refreshPriceAlertsButton = document.getElementById("refreshPriceAlertsButton");
        this.dom.alertSummaryTotal = document.getElementById("alertSummaryTotal");
        this.dom.alertSummaryHigh = document.getElementById("alertSummaryHigh");
        this.dom.alertSummaryMedium = document.getElementById("alertSummaryMedium");
        this.dom.syncStatusDot = document.getElementById("syncStatusDot");
        this.dom.syncStatusLabel = document.getElementById("syncStatusLabel");
        this.dom.networkBanner = document.getElementById("networkBanner");
        this.dom.networkBannerMessage = document.getElementById("networkBannerMessage");
        this.dom.activeFieldName = document.getElementById("activeFieldName");
        this.dom.nextActionDue = document.getElementById("nextActionDue");
        this.dom.nextActionDescription = document.getElementById("nextActionDescription");
        this.dom.markActionCompleteButton = document.getElementById("markActionCompleteButton");
        this.dom.rescheduleActionButton = document.getElementById("rescheduleActionButton");
        this.dom.analysisChips = document.querySelectorAll(".analysis-chip");
        this.dom.analysisSummary = document.getElementById("analysisSummary");
        this.dom.analysisChart = document.getElementById("analysisChart");
        this.dom.bottomNavItems = document.querySelectorAll(".bottom-nav-item");
        this.dom.offlineQueueCount = document.getElementById("offlineQueueCount");
        this.dom.gpsStatus = document.getElementById("gpsStatus");
        this.dom.gpsDetail = document.getElementById("gpsDetail");
        this.dom.cameraPreview = document.getElementById("cameraPreview");
        this.dom.photoCanvas = document.getElementById("photoCanvas");
        this.dom.photoCount = document.getElementById("photoCount");
        this.dom.trackingPanel = document.getElementById("trackingPanel");
        this.dom.trackingForm = document.getElementById("trackingForm");
        this.dom.trackingActivityType = document.getElementById("trackingActivityType");
        this.dom.trackingStatus = document.getElementById("trackingStatus");
        this.dom.trackingCostInput = document.getElementById("trackingCostInput");
        this.dom.trackingYieldInput = document.getElementById("trackingYieldInput");
        this.dom.trackingNotesInput = document.getElementById("trackingNotesInput");
        this.dom.trackingSubmitButton = document.getElementById("trackingSubmitButton");
        this.dom.syncNowButton = document.getElementById("syncNowButton");
        this.dom.activityTimeline = document.getElementById("activityTimeline");
        this.dom.lastSyncLabel = document.getElementById("lastSyncLabel");
        this.dom.pendingTrackingCount = document.getElementById("pendingTrackingCount");
        this.dom.trackingProgressLabel = document.getElementById("trackingProgressLabel");
        this.dom.trackingPhotoHint = document.getElementById("trackingPhotoHint");
    };

    MobileFertilizerStrategyApp.prototype.bindEvents = function () {
        var index;

        for (index = 0; index < this.dom.sectionToggles.length; index++) {
            var toggle = this.dom.sectionToggles[index];
            toggle.addEventListener("click", this.handleSectionToggle.bind(this));
        }

        if (this.dom.quickActions.gps) {
            this.dom.quickActions.gps.addEventListener("click", this.handleGpsCapture.bind(this));
        }

        if (this.dom.quickActions.camera) {
            this.dom.quickActions.camera.addEventListener("click", this.handleCameraCapture.bind(this));
        }

        if (this.dom.quickActions.refresh) {
            this.dom.quickActions.refresh.addEventListener("click", this.refreshStrategyData.bind(this));
        }

        if (this.dom.quickActions.saveOffline) {
            this.dom.quickActions.saveOffline.addEventListener("click", this.saveStrategyOffline.bind(this));
        }

        if (this.dom.priceRefreshButton) {
            this.dom.priceRefreshButton.addEventListener("click", this.fetchPriceSignals.bind(this));
        }

        if (this.dom.refreshPriceAlertsButton) {
            this.dom.refreshPriceAlertsButton.addEventListener("click", this.fetchMobilePriceAlerts.bind(this));
        }

        if (this.dom.markActionCompleteButton) {
            this.dom.markActionCompleteButton.addEventListener("click", this.handleActionCompleted.bind(this));
        }

        if (this.dom.rescheduleActionButton) {
            this.dom.rescheduleActionButton.addEventListener("click", this.handleActionReschedule.bind(this));
        }

        for (index = 0; index < this.dom.analysisChips.length; index++) {
            var chip = this.dom.analysisChips[index];
            chip.addEventListener("click", this.handleAnalysisSelection.bind(this));
        }

        for (index = 0; index < this.dom.bottomNavItems.length; index++) {
            var navItem = this.dom.bottomNavItems[index];
            navItem.addEventListener("click", this.handleBottomNavigation.bind(this));
        }

        if (this.dom.trackingForm) {
            this.dom.trackingForm.addEventListener("submit", this.handleTrackingSubmit.bind(this));
        }

        if (this.dom.syncNowButton) {
            this.dom.syncNowButton.addEventListener("click", this.handleSyncNow.bind(this));
        }

        window.addEventListener("online", this.handleOnline.bind(this));
        window.addEventListener("offline", this.handleOffline.bind(this));

        document.addEventListener("mobileDevice:networkChange", this.handleDeviceNetworkChange.bind(this));
        document.addEventListener("mobileDevice:visibilityChange", this.handleVisibilityChange.bind(this));
    };

    MobileFertilizerStrategyApp.prototype.initializeTrackingDefaults = function () {
        if (this.dom.trackingActivityType) {
            this.dom.trackingActivityType.value = "application";
        }
        if (this.dom.trackingStatus) {
            this.dom.trackingStatus.value = "completed";
        }
        if (this.dom.trackingCostInput) {
            this.dom.trackingCostInput.value = "";
        }
        if (this.dom.trackingYieldInput) {
            this.dom.trackingYieldInput.value = "";
        }
        if (this.dom.trackingNotesInput) {
            this.dom.trackingNotesInput.value = "";
        }
        this.updatePhotoHint();
    };

    MobileFertilizerStrategyApp.prototype.setupIntegrations = async function () {
        this.deviceIntegration = new MobileDeviceIntegration();
        this.offlineDatabase = new MobileOfflineDatabase();

        await this.waitFor(function () {
            return window.MobileDeviceIntegration !== undefined;
        });

        var self = this;
        await this.waitFor(function () {
            return self.offlineDatabase && self.offlineDatabase.db;
        });
    };

    MobileFertilizerStrategyApp.prototype.waitFor = function (predicate) {
        return new Promise(function (resolve) {
            function checkCondition() {
                if (predicate()) {
                    resolve();
                } else {
                    setTimeout(checkCondition, 80);
                }
            }
            checkCondition();
        });
    };

    MobileFertilizerStrategyApp.prototype.initializeChart = function () {
        if (!window.Chart || !this.dom.analysisChart) {
            return;
        }

        var context = this.dom.analysisChart.getContext("2d");
        this.chart = new Chart(context, {
            type: "radar",
            data: {
                labels: ["Profitability", "Sustainability", "Risk"],
                datasets: [{
                    label: "Strategy",
                    data: [0, 0, 0],
                    backgroundColor: "rgba(40, 167, 69, 0.2)",
                    borderColor: "rgba(23, 99, 49, 0.9)",
                    borderWidth: 2,
                    pointBackgroundColor: "rgba(23, 99, 49, 1)"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: {
                            stepSize: 20,
                            display: false
                        },
                        grid: {
                            circular: true
                        },
                        pointLabels: {
                            font: {
                                size: 12
                            },
                            color: "#2f3438"
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    };

    MobileFertilizerStrategyApp.prototype.loadInitialData = async function () {
        await this.fetchStrategySummary();
        await this.fetchPriceSignals();
        await this.fetchMobilePriceAlerts();
        this.updateOfflineQueueCount();
        await this.fetchTrackingSummary();
    };

    MobileFertilizerStrategyApp.prototype.fetchStrategySummary = async function () {
        var summaryData = null;

        try {
            var response = await fetch("/api/v1/strategies/compare?field_id=mobile_field&time_horizon_days=120&include_roi=true");
            if (response.ok) {
                var apiData = await response.json();
                summaryData = this.transformStrategySummary(apiData);
            }
        } catch (error) {
            console.warn("Strategy summary fetch failed:", error);
        }

        if (!summaryData) {
            summaryData = this.buildSampleSummary();
        }

        this.state.summary = summaryData;
        if (summaryData.strategyId) {
            this.state.strategyId = summaryData.strategyId;
        }
        if (summaryData.versionNumber) {
            this.state.strategyVersion = summaryData.versionNumber;
        }
        if (summaryData.fieldId) {
            this.state.field.fieldId = summaryData.fieldId;
        }
        if (summaryData.userId) {
            this.userId = summaryData.userId;
        }
        this.renderSummary(summaryData);
        this.renderNextAction(summaryData.nextAction);
        this.renderRecommendations(summaryData.recommendations);
        this.updateAnalysisData(summaryData.analysis);
    };

    MobileFertilizerStrategyApp.prototype.transformStrategySummary = function (apiData) {
        var summary = {
            projectedRoi: "--",
            profitStatus: "Awaiting analysis",
            strategyCost: "--",
            costStatus: "Awaiting data",
            yieldImpact: "--",
            yieldStatus: "Pending analysis",
            sustainability: "--",
            sustainabilityStatus: "Monitoring",
            nextAction: null,
            recommendations: [],
            analysis: {
                profitability: 0,
                sustainability: 0,
                risk: 0
            }
        };

        try {
            if (apiData && apiData.comparisons && apiData.comparisons.length > 0) {
                var firstComparison = apiData.comparisons[0];
                if (firstComparison.projected_roi) {
                    summary.projectedRoi = (firstComparison.projected_roi * 100).toFixed(1) + "%";
                    summary.profitStatus = firstComparison.recommendation || "ROI projection updated";
                }
                if (firstComparison.total_cost) {
                    summary.strategyCost = "$" + firstComparison.total_cost.toFixed(2);
                    summary.costStatus = "Includes product and logistics costs";
                }
                if (firstComparison.yield_projection) {
                    summary.yieldImpact = "+" + firstComparison.yield_projection.toFixed(1) + "%";
                    summary.yieldStatus = "Compared to baseline";
                }
                if (firstComparison.sustainability_score) {
                    summary.sustainability = firstComparison.sustainability_score.toFixed(0) + "/100";
                    summary.sustainabilityStatus = "Sustainability index";
                }
                summary.nextAction = {
                    label: "Apply " + (firstComparison.primary_product || "fertilizer blend"),
                    due: firstComparison.next_application_date || "Review schedule",
                    detail: firstComparison.operational_guidance || "Follow equipment calibration and safety guidelines."
                };

                if (apiData.recommendations && apiData.recommendations.length > 0) {
                    summary.recommendations = apiData.recommendations.slice(0, 4);
                }

                summary.analysis = {
                    profitability: firstComparison.profitability_score || 72,
                    sustainability: firstComparison.sustainability_score || 65,
                    risk: firstComparison.risk_score ? 100 - firstComparison.risk_score : 58
                };
                summary.strategyId = firstComparison.strategy_id || firstComparison.strategyId || firstComparison.id || "mobile-strategy-demo";
                summary.versionNumber = firstComparison.version_number || firstComparison.versionNumber || 1;
                summary.fieldId = firstComparison.field_id || firstComparison.fieldId || null;
                summary.userId = firstComparison.user_id || firstComparison.userId || this.userId;
            }
        } catch (error) {
            console.warn("Unable to transform strategy summary:", error);
        }

        return summary;
    };

    MobileFertilizerStrategyApp.prototype.buildSampleSummary = function () {
        return {
            projectedRoi: "+18.4%",
            profitStatus: "ROI exceeds seasonal target",
            strategyCost: "$42,180",
            costStatus: "Includes nitrogen, phosphorus, potash, logistics",
            yieldImpact: "+6.3%",
            yieldStatus: "Projected yield increase vs baseline",
            sustainability: "82/100",
            sustainabilityStatus: "Reduced runoff & carbon footprint",
            nextAction: {
                label: "Apply sidedress nitrogen",
                due: "In 4 days",
                detail: "Apply 32% UAN at 150 lbs N/acre with Y-drop system."
            },
            recommendations: [
                {
                    title: "Lock in nitrogen price opportunity",
                    detail: "Forward purchase 40% of remaining nitrogen while price is 6% below seasonal average."
                },
                {
                    title: "Integrate cover crop nutrient credit",
                    detail: "Apply credit of 25 lbs N/acre from cereal rye termination to reduce input cost."
                },
                {
                    title: "Monitor rainfall window",
                    detail: "Rain probability 60% in 72 hours. Delay broadcast if soil moisture exceeds 85% saturation."
                },
                {
                    title: "Capture field imagery",
                    detail: "Document pre-application crop condition using mobile camera for compliance records."
                }
            ],
            analysis: {
                profitability: 78,
                sustainability: 82,
                risk: 62
            },
            strategyId: "mobile-strategy-demo",
            versionNumber: 1,
            fieldId: "field-demo",
            userId: this.userId
        };
    };

    MobileFertilizerStrategyApp.prototype.fetchTrackingSummary = async function () {
        if (!this.offlineDatabase) {
            return;
        }

        var strategyId = this.state.strategyId;
        if (!strategyId) {
            return;
        }

        var versionNumber = this.state.strategyVersion || 1;
        var requestUrl = "/api/v1/mobile-strategy/summary?strategy_id=" + encodeURIComponent(strategyId) + "&version_number=" + versionNumber + "&limit=10";
        var summary = null;

        try {
            var response = await fetch(requestUrl);
            if (response.ok) {
                summary = await response.json();
            }
        } catch (error) {
            console.warn("Mobile tracking summary fetch failed:", error);
        }

        if (summary && summary.recent_activities) {
            var mappedActivities = this.mapTrackingActivities(summary.recent_activities, false);
            this.state.trackingEntries = mappedActivities;
            this.renderTrackingTimeline(mappedActivities);
            this.updateTrackingStats(summary);
        } else {
            var offlineEntries = await this.offlineDatabase.getPendingStrategyTrackingEntries();
            var mappedOffline = this.mapTrackingActivities(offlineEntries, true);
            this.state.trackingEntries = mappedOffline;
            this.renderTrackingTimeline(mappedOffline);
            this.updateTrackingStats(null);
        }
    };

    MobileFertilizerStrategyApp.prototype.mapTrackingActivities = function (activities, pendingOnly) {
        var mapped = [];
        if (!activities) {
            return mapped;
        }

        var index = 0;
        while (index < activities.length) {
            var record = activities[index];
            if (record) {
                var pendingFlag = pendingOnly;
                if (record.synced === false) {
                    pendingFlag = true;
                }
                var entry = this.buildTimelineEntryFromRecord(record, pendingFlag);
                mapped.push(entry);
            }
            index += 1;
        }

        mapped.sort(function (a, b) {
            if (a.timestamp < b.timestamp) {
                return 1;
            }
            if (a.timestamp > b.timestamp) {
                return -1;
            }
            return 0;
        });

        return mapped;
    };

    MobileFertilizerStrategyApp.prototype.buildTimelineEntryFromRecord = function (record, pendingFlag) {
        var entryId = record.activity_id || record.client_event_id || this.generateTimelineId();
        var timestampValue = record.recorded_at || record.activity_timestamp || record.created_at || record.updated_at;
        var normalizedTimestamp = this.normalizeTimestamp(timestampValue);
        var timestampDate = new Date(normalizedTimestamp);

        var activityType = record.activity_type || record.activityType || "activity";
        var status = record.status || "recorded";
        var iconInfo = this.resolveActivityIcon(activityType, status, pendingFlag);
        var notes = this.buildNotesFromRecord(record);
        var costLabel = this.buildCostLabel(record.cost_summary || record.costSummary || null);
        var yieldLabel = this.buildYieldLabel(record.yield_summary || record.yieldSummary || null);

        return {
            id: entryId,
            activityType: activityType,
            status: status,
            title: this.formatActivityTitle(activityType, status),
            timestamp: timestampDate,
            timestampLabel: this.formatTimestamp(timestampDate),
            notes: notes,
            costLabel: costLabel,
            yieldLabel: yieldLabel,
            pending: pendingFlag,
            iconClass: iconInfo.background,
            icon: iconInfo.icon
        };
    };

    MobileFertilizerStrategyApp.prototype.resolveActivityIcon = function (activityType, status, pendingFlag) {
        var icon = "fa-clipboard";
        var background = "timeline-icon-default";
        var normalizedType = activityType ? activityType.toLowerCase() : "";
        var normalizedStatus = status ? status.toLowerCase() : "";

        if (normalizedType === "application") {
            icon = "fa-tractor";
            background = "timeline-icon-success";
        } else if (normalizedType === "scouting") {
            icon = "fa-binoculars";
            background = "timeline-icon-info";
        } else if (normalizedType === "cost_update") {
            icon = "fa-dollar-sign";
            background = "timeline-icon-warning";
        } else if (normalizedType === "yield_check") {
            icon = "fa-seedling";
            background = "timeline-icon-success";
        } else if (normalizedType === "photo_capture") {
            icon = "fa-camera";
            background = "timeline-icon-info";
        }

        if (normalizedStatus === "delayed") {
            background = "timeline-icon-warning";
        } else if (normalizedStatus === "scheduled" || normalizedStatus === "in_progress") {
            background = "timeline-icon-info";
        } else if (normalizedStatus === "completed") {
            background = "timeline-icon-success";
        }

        if (pendingFlag) {
            background = "timeline-icon-pending";
        }

        return {
            icon: icon,
            background: background
        };
    };

    MobileFertilizerStrategyApp.prototype.formatActivityTitle = function (activityType, status) {
        var baseTitle = "Field Activity";
        var normalizedType = activityType ? activityType.toLowerCase() : "";

        if (normalizedType === "application") {
            baseTitle = "Application";
        } else if (normalizedType === "scouting") {
            baseTitle = "Scouting";
        } else if (normalizedType === "cost_update") {
            baseTitle = "Cost Update";
        } else if (normalizedType === "yield_check") {
            baseTitle = "Yield Check";
        } else if (normalizedType === "photo_capture") {
            baseTitle = "Photo Capture";
        }

        var statusLabel = this.formatStatusLabel(status);
        if (statusLabel) {
            return baseTitle + " • " + statusLabel;
        }
        return baseTitle;
    };

    MobileFertilizerStrategyApp.prototype.formatStatusLabel = function (status) {
        if (!status) {
            return "";
        }

        var cleaned = "";
        var index = 0;
        while (index < status.length) {
            var character = status.charAt(index);
            if (character === "_") {
                cleaned += " ";
            } else {
                cleaned += character;
            }
            index += 1;
        }

        cleaned = cleaned.trim();
        if (cleaned.length === 0) {
            return "";
        }

        var parts = cleaned.split(" ");
        var formattedParts = [];
        var partIndex = 0;
        while (partIndex < parts.length) {
            var word = parts[partIndex];
            if (word.length > 0) {
                var formatted = word.charAt(0).toUpperCase() + word.slice(1);
                formattedParts.push(formatted);
            }
            partIndex += 1;
        }

        return formattedParts.join(" ");
    };

    MobileFertilizerStrategyApp.prototype.formatTimestamp = function (date) {
        if (!(date instanceof Date) || isNaN(date.getTime())) {
            return "Recorded";
        }

        var options = {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        };

        try {
            return date.toLocaleString(undefined, options);
        } catch (error) {
            return date.toISOString();
        }
    };

    MobileFertilizerStrategyApp.prototype.renderTrackingTimeline = function (entries) {
        if (!this.dom.activityTimeline) {
            return;
        }

        this.dom.activityTimeline.innerHTML = "";

        if (!entries || entries.length === 0) {
            var placeholder = document.createElement("li");
            placeholder.className = "timeline-placeholder";
            placeholder.textContent = "Log field activities to build your mobile strategy timeline.";
            this.dom.activityTimeline.appendChild(placeholder);
            return;
        }

        var index = 0;
        while (index < entries.length) {
            var entry = entries[index];
            var item = document.createElement("li");
            var itemClass = "timeline-item";
            if (entry.pending) {
                itemClass += " pending";
            }
            item.className = itemClass;

            var iconWrapper = document.createElement("div");
            iconWrapper.className = "timeline-icon " + entry.iconClass;
            iconWrapper.innerHTML = "<i class=\"fas " + entry.icon + "\"></i>";

            var body = document.createElement("div");
            body.className = "timeline-body";

            var title = document.createElement("p");
            title.className = "timeline-title";
            title.textContent = entry.title;
            body.appendChild(title);

            var meta = document.createElement("p");
            meta.className = "timeline-meta";
            var metaText = entry.timestampLabel;
            if (entry.pending) {
                metaText += " • Pending sync";
            }
            meta.textContent = metaText;
            body.appendChild(meta);

            if (entry.costLabel) {
                var costLine = document.createElement("p");
                costLine.className = "timeline-metric";
                costLine.textContent = "Cost: " + entry.costLabel;
                body.appendChild(costLine);
            }

            if (entry.yieldLabel) {
                var yieldLine = document.createElement("p");
                yieldLine.className = "timeline-metric";
                yieldLine.textContent = "Yield: " + entry.yieldLabel;
                body.appendChild(yieldLine);
            }

            if (entry.notes) {
                var noteLine = document.createElement("p");
                noteLine.className = "timeline-notes";
                noteLine.textContent = entry.notes;
                body.appendChild(noteLine);
            }

            item.appendChild(iconWrapper);
            item.appendChild(body);
            this.dom.activityTimeline.appendChild(item);
            index += 1;
        }
    };

    MobileFertilizerStrategyApp.prototype.prependTrackingEntry = function (entry) {
        if (!this.state.trackingEntries) {
            this.state.trackingEntries = [];
        }
        this.state.trackingEntries.unshift(entry);
        if (this.state.trackingEntries.length > 20) {
            this.state.trackingEntries.pop();
        }
        this.renderTrackingTimeline(this.state.trackingEntries);
    };

    MobileFertilizerStrategyApp.prototype.updateTrackingStats = function (summary) {
        var progressPercent = 0;
        if (summary && typeof summary.progress_percent === "number") {
            progressPercent = summary.progress_percent;
        } else if (this.state.trackingStats && typeof this.state.trackingStats.progressPercent === "number") {
            progressPercent = this.state.trackingStats.progressPercent;
        }

        this.state.trackingStats.progressPercent = progressPercent;

        var lastSyncedAt = null;
        if (summary && summary.performance_snapshot && summary.performance_snapshot.last_synced_at) {
            lastSyncedAt = summary.performance_snapshot.last_synced_at;
        } else if (summary && summary.progress_percent !== undefined) {
            lastSyncedAt = new Date().toISOString();
        } else if (this.state.trackingStats && this.state.trackingStats.lastSyncedAt) {
            lastSyncedAt = this.state.trackingStats.lastSyncedAt;
        }

        this.state.trackingStats.lastSyncedAt = lastSyncedAt;

        if (this.dom.trackingProgressLabel) {
            var progressText = "Progress: " + progressPercent.toFixed(0) + "%";
            this.dom.trackingProgressLabel.textContent = progressText;
        }

        if (this.dom.lastSyncLabel) {
            var syncLabel = "Last sync: --";
            if (lastSyncedAt) {
                var syncDate = new Date(lastSyncedAt);
                syncLabel = "Last sync: " + this.formatTimestamp(syncDate);
            }
            this.dom.lastSyncLabel.textContent = syncLabel;
        }

        this.updatePendingTrackingCount();
    };

    MobileFertilizerStrategyApp.prototype.updatePendingTrackingCount = async function () {
        if (!this.offlineDatabase) {
            return;
        }

        try {
            var pendingEntries = await this.offlineDatabase.getPendingStrategyTrackingEntries();
            if (this.dom.pendingTrackingCount) {
                this.dom.pendingTrackingCount.textContent = "Pending: " + pendingEntries.length;
            }
        } catch (error) {
            console.warn("Unable to update pending tracking count:", error);
        }
    };

    MobileFertilizerStrategyApp.prototype.handleTrackingSubmit = async function (event) {
        event.preventDefault();
        if (!this.state.strategyId) {
            this.showNotification("Strategy data unavailable - refresh data first", { type: "warning" });
            return;
        }

        var payload = this.buildTrackingPayload();
        await this.recordStrategyProgress(payload);
    };

    MobileFertilizerStrategyApp.prototype.buildTrackingPayload = function () {
        var payload = {};
        payload.strategy_id = this.state.strategyId || "mobile-strategy-demo";
        payload.version_number = this.state.strategyVersion || 1;
        payload.user_id = this.userId;
        payload.field_id = this.state.field.fieldId || null;
        payload.activity_type = this.dom.trackingActivityType ? this.dom.trackingActivityType.value : "application";
        payload.status = this.dom.trackingStatus ? this.dom.trackingStatus.value : "completed";
        payload.activity_timestamp = new Date().toISOString();
        payload.captured_offline = !navigator.onLine;
        payload.notes = this.dom.trackingNotesInput ? this.dom.trackingNotesInput.value : null;

        if (this.state.field && this.state.field.coordinates) {
            payload.gps = {
                latitude: this.state.field.coordinates.latitude,
                longitude: this.state.field.coordinates.longitude,
                accuracy: this.state.field.coordinates.accuracy
            };
        }

        if (this.dom.trackingCostInput && this.dom.trackingCostInput.value) {
            var costValue = parseFloat(this.dom.trackingCostInput.value);
            if (!isNaN(costValue)) {
                payload.cost_summary = {
                    total_cost: costValue,
                    currency: "USD"
                };
            }
        }

        if (this.dom.trackingYieldInput && this.dom.trackingYieldInput.value) {
            var yieldValue = parseFloat(this.dom.trackingYieldInput.value);
            if (!isNaN(yieldValue)) {
                payload.yield_summary = {
                    observed_yield: yieldValue,
                    yield_unit: "bu/ac"
                };
            }
        }

        payload.photos = [];
        return payload;
    };

    MobileFertilizerStrategyApp.prototype.buildQuickTrackingPayload = function (activityType, status, notes) {
        var payload = {
            strategy_id: this.state.strategyId || "mobile-strategy-demo",
            version_number: this.state.strategyVersion || 1,
            user_id: this.userId,
            field_id: this.state.field.fieldId || null,
            activity_type: activityType,
            status: status,
            activity_timestamp: new Date().toISOString(),
            captured_offline: !navigator.onLine,
            notes: notes,
            photos: []
        };

        if (this.state.field && this.state.field.coordinates) {
            payload.gps = {
                latitude: this.state.field.coordinates.latitude,
                longitude: this.state.field.coordinates.longitude,
                accuracy: this.state.field.coordinates.accuracy
            };
        }

        return payload;
    };

    MobileFertilizerStrategyApp.prototype.recordStrategyProgress = async function (payload) {
        if (!this.offlineDatabase) {
            this.showNotification("Offline storage unavailable", { type: "error" });
            return;
        }

        try {
            var storedEntry = await this.offlineDatabase.queueStrategyProgress(payload);
            var timelineEntry = this.buildTimelineEntryFromRecord(storedEntry, !storedEntry.synced);
            this.prependTrackingEntry(timelineEntry);
            this.showNotification("Activity saved for tracking", { type: "success" });
            this.resetTrackingForm();
            this.updateOfflineQueueCount();

            if (navigator.onLine) {
                await this.fetchTrackingSummary();
            }
        } catch (error) {
            console.error("Failed to record strategy progress:", error);
            this.showNotification("Unable to save activity", { type: "error" });
        }
    };

    MobileFertilizerStrategyApp.prototype.handleSyncNow = async function () {
        if (!this.offlineDatabase) {
            return;
        }

        this.showNotification("Synchronizing activities...", { type: "info" });
        try {
            await this.offlineDatabase.syncOfflineData();
            await this.fetchTrackingSummary();
            await this.updateOfflineQueueCount();
            this.showNotification("Sync complete", { type: "success" });
        } catch (error) {
            console.error("Manual sync failed:", error);
            this.showNotification("Sync failed - will retry later", { type: "error" });
        }
    };

    MobileFertilizerStrategyApp.prototype.resetTrackingForm = function () {
        if (this.dom.trackingForm) {
            this.dom.trackingForm.reset();
        }
        this.initializeTrackingDefaults();
    };

    MobileFertilizerStrategyApp.prototype.buildCostLabel = function (summary) {
        if (!summary) {
            return null;
        }

        if (typeof summary.total_cost === "number" && !isNaN(summary.total_cost)) {
            return "$" + summary.total_cost.toFixed(2);
        }

        if (typeof summary.input_cost === "number" && !isNaN(summary.input_cost)) {
            return "$" + summary.input_cost.toFixed(2);
        }

        if (typeof summary.labor_cost === "number" && !isNaN(summary.labor_cost)) {
            return "$" + summary.labor_cost.toFixed(2);
        }

        return null;
    };

    MobileFertilizerStrategyApp.prototype.buildYieldLabel = function (summary) {
        if (!summary) {
            return null;
        }

        if (typeof summary.observed_yield === "number" && !isNaN(summary.observed_yield)) {
            return summary.observed_yield.toFixed(1) + " bu/ac";
        }

        if (typeof summary.expected_yield === "number" && !isNaN(summary.expected_yield)) {
            return summary.expected_yield.toFixed(1) + " bu/ac";
        }

        return null;
    };

    MobileFertilizerStrategyApp.prototype.buildNotesFromRecord = function (record) {
        if (record.notes && typeof record.notes === "string" && record.notes.trim().length > 0) {
            return record.notes.trim();
        }
        if (record.attachments && record.attachments.notes && typeof record.attachments.notes === "string") {
            var attachmentNote = record.attachments.notes.trim();
            if (attachmentNote.length > 0) {
                return attachmentNote;
            }
        }
        if (record.observations && typeof record.observations === "string" && record.observations.trim().length > 0) {
            return record.observations.trim();
        }
        return null;
    };

    MobileFertilizerStrategyApp.prototype.generateTimelineId = function () {
        return "timeline_" + Date.now().toString(36) + Math.floor(Math.random() * 1000).toString(36);
    };

    MobileFertilizerStrategyApp.prototype.updatePhotoHint = function () {
        if (!this.dom.trackingPhotoHint) {
            return;
        }

        var photoCountText = "Photos captured: 0";
        if (this.dom.photoCount && this.dom.photoCount.textContent) {
            var parsed = parseInt(this.dom.photoCount.textContent, 10);
            if (!isNaN(parsed)) {
                photoCountText = "Photos captured: " + parsed;
            }
        }
        this.dom.trackingPhotoHint.textContent = photoCountText;
    };

    MobileFertilizerStrategyApp.prototype.normalizeTimestamp = function (value) {
        if (!value) {
            return new Date().toISOString();
        }

        if (value instanceof Date) {
            return value.toISOString();
        }

        if (typeof value === "number") {
            return new Date(value).toISOString();
        }

        if (typeof value === "string") {
            var parsed = Date.parse(value);
            if (!isNaN(parsed)) {
                return new Date(parsed).toISOString();
            }
        }

        return new Date().toISOString();
    };

    MobileFertilizerStrategyApp.prototype.renderSummary = function (summary) {
        if (!summary) {
            return;
        }

        if (this.dom.summaryCards.projectedRoi) {
            this.dom.summaryCards.projectedRoi.textContent = summary.projectedRoi;
        }
        if (this.dom.summaryCards.profitStatus) {
            this.dom.summaryCards.profitStatus.textContent = summary.profitStatus;
        }
        if (this.dom.summaryCards.strategyCost) {
            this.dom.summaryCards.strategyCost.textContent = summary.strategyCost;
        }
        if (this.dom.summaryCards.costStatus) {
            this.dom.summaryCards.costStatus.textContent = summary.costStatus;
        }
        if (this.dom.summaryCards.yieldImpact) {
            this.dom.summaryCards.yieldImpact.textContent = summary.yieldImpact;
        }
        if (this.dom.summaryCards.yieldStatus) {
            this.dom.summaryCards.yieldStatus.textContent = summary.yieldStatus;
        }
        if (this.dom.summaryCards.sustainability) {
            this.dom.summaryCards.sustainability.textContent = summary.sustainability;
        }
        if (this.dom.summaryCards.sustainabilityStatus) {
            this.dom.summaryCards.sustainabilityStatus.textContent = summary.sustainabilityStatus;
        }
    };

    MobileFertilizerStrategyApp.prototype.renderNextAction = function (action) {
        if (!action) {
            return;
        }

        if (this.dom.nextActionDue) {
            this.dom.nextActionDue.textContent = action.due || "Schedule pending";
        }
        if (this.dom.nextActionDescription) {
            this.dom.nextActionDescription.textContent = action.detail || "";
        }
    };

    MobileFertilizerStrategyApp.prototype.renderRecommendations = function (recommendations) {
        if (!this.dom.recommendationList) {
            return;
        }

        this.dom.recommendationList.innerHTML = "";

        if (!recommendations || recommendations.length === 0) {
            var placeholder = document.createElement("article");
            placeholder.className = "recommendation-card";
            placeholder.innerHTML = "" +
                "<div class=\"recommendation-icon bg-success\">" +
                "<i class=\"fas fa-info-circle\"></i>" +
                "</div>" +
                "<div class=\"recommendation-body\">" +
                "<p class=\"recommendation-title\">No recommendations available</p>" +
                "<p class=\"recommendation-detail\">Sync strategy data to populate field-ready actions.</p>" +
                "</div>";
            this.dom.recommendationList.appendChild(placeholder);
            return;
        }

        for (var index = 0; index < recommendations.length; index++) {
            var item = recommendations[index];
            var card = document.createElement("article");
            card.className = "recommendation-card";

            var iconClass = "bg-success";
            if (item.priority === "high") {
                iconClass = "bg-danger";
            } else if (item.priority === "medium") {
                iconClass = "bg-warning";
            } else if (item.priority === "watch") {
                iconClass = "bg-info";
            }

            var actionButton = document.createElement("button");
            actionButton.className = "btn btn-outline-success btn-sm";
            actionButton.textContent = "Track";
            actionButton.addEventListener("click", this.handleRecommendationTrack.bind(this, item));

            var iconWrapper = document.createElement("div");
            iconWrapper.className = "recommendation-icon " + iconClass;
            iconWrapper.innerHTML = "<i class=\"fas fa-lightbulb\"></i>";

            var bodyWrapper = document.createElement("div");
            bodyWrapper.className = "recommendation-body";

            var title = document.createElement("p");
            title.className = "recommendation-title";
            title.textContent = item.title || "Strategy update";
            bodyWrapper.appendChild(title);

            var detail = document.createElement("p");
            detail.className = "recommendation-detail";
            detail.textContent = item.detail || "Review recommendation detail in dashboard.";
            bodyWrapper.appendChild(detail);

            var actionWrapper = document.createElement("div");
            actionWrapper.className = "recommendation-action";
            actionWrapper.appendChild(actionButton);

            card.appendChild(iconWrapper);
            card.appendChild(bodyWrapper);
            card.appendChild(actionWrapper);

            this.dom.recommendationList.appendChild(card);
        }
    };

    MobileFertilizerStrategyApp.prototype.updateAnalysisData = function (analysis) {
        if (!analysis) {
            return;
        }

        this.chartData.profitability = analysis.profitability || 0;
        this.chartData.sustainability = analysis.sustainability || 0;
        this.chartData.risk = analysis.risk || 0;
        this.refreshAnalysisChart("profitability");
    };

    MobileFertilizerStrategyApp.prototype.fetchPriceSignals = async function () {
        if (this.dom.priceRefreshButton) {
            this.dom.priceRefreshButton.disabled = true;
        }

        var priceEntries = null;

        try {
            var response = await fetch("/api/v1/prices/fertilizer-current");
            if (response.ok) {
                var priceData = await response.json();
                if (priceData && priceData.prices && priceData.prices.length > 0) {
                    priceEntries = [];
                    for (var index = 0; index < priceData.prices.length; index++) {
                        var item = priceData.prices[index];
                        var entry = {
                            product: item.fertilizer_type || item.product || "Fertilizer",
                            price: item.price_per_unit || item.price || 0,
                            change: item.trend_7d || item.change_percent || 0,
                            region: item.region || "Region input pending",
                            unit: item.unit || "$/ton"
                        };
                        priceEntries.push(entry);
                    }
                }
            }
        } catch (error) {
            console.warn("Price fetch failed:", error);
        }

        if (!priceEntries) {
            priceEntries = this.buildSamplePrices();
        }

        this.state.marketSignals = priceEntries;
        this.state.lastPriceUpdate = new Date();
        this.renderPriceSignals(priceEntries);

        if (this.dom.priceRefreshButton) {
            this.dom.priceRefreshButton.disabled = false;
        }
    };

    MobileFertilizerStrategyApp.prototype.buildSamplePrices = function () {
        return [
            {
                product: "Urea (46-0-0)",
                price: 482.50,
                change: -4.6,
                region: "Midwest",
                unit: "$/ton"
            },
            {
                product: "Anhydrous Ammonia",
                price: 834.00,
                change: 2.1,
                region: "Corn Belt",
                unit: "$/ton"
            },
            {
                product: "Potash (0-0-60)",
                price: 375.20,
                change: 0.0,
                region: "Great Plains",
                unit: "$/ton"
            },
            {
                product: "DAP (18-46-0)",
                price: 642.75,
                change: -1.3,
                region: "Southeast",
                unit: "$/ton"
            }
        ];
    };

    MobileFertilizerStrategyApp.prototype.renderPriceSignals = function (prices) {
        if (!this.dom.priceList) {
            return;
        }

        this.dom.priceList.innerHTML = "";

        if (!prices || prices.length === 0) {
            var emptyMessage = document.createElement("li");
            emptyMessage.className = "price-item";
            emptyMessage.textContent = "No price data available";
            this.dom.priceList.appendChild(emptyMessage);
            return;
        }

        for (var index = 0; index < prices.length; index++) {
            var price = prices[index];
            var listItem = document.createElement("li");
            listItem.className = "price-item";

            var header = document.createElement("div");
            header.className = "price-header";
            var productLabel = document.createElement("span");
            productLabel.className = "price-product";
            productLabel.textContent = price.product;
            header.appendChild(productLabel);

            var priceValue = document.createElement("span");
            priceValue.className = "price-value";
            priceValue.textContent = "$" + price.price.toFixed(2) + " " + price.unit;
            header.appendChild(priceValue);

            var footer = document.createElement("div");
            footer.className = "price-footer";
            var regionLabel = document.createElement("span");
            regionLabel.className = "price-region";
            regionLabel.textContent = price.region;
            footer.appendChild(regionLabel);

            var changeLabel = document.createElement("span");
            changeLabel.className = "price-change";
            var changeValue = price.change || 0;
            if (changeValue > 0) {
                changeLabel.classList.add("up");
                changeLabel.textContent = "+" + changeValue.toFixed(1) + "%";
            } else if (changeValue < 0) {
                changeLabel.classList.add("down");
                changeLabel.textContent = changeValue.toFixed(1) + "%";
            } else {
                changeLabel.classList.add("neutral");
                changeLabel.textContent = "0%";
            }
            footer.appendChild(changeLabel);

            listItem.appendChild(header);
            listItem.appendChild(footer);

            this.dom.priceList.appendChild(listItem);
        }

        if (this.dom.priceLastUpdatedLabel && this.state.lastPriceUpdate) {
            this.dom.priceLastUpdatedLabel.textContent = "Last updated: " + this.state.lastPriceUpdate.toLocaleTimeString();
        }
    };

    MobileFertilizerStrategyApp.prototype.fetchMobilePriceAlerts = async function () {
        if (this.dom.refreshPriceAlertsButton) {
            this.dom.refreshPriceAlertsButton.disabled = true;
        }

        var alertPackage = null;
        var payload = {
            user_id: "mobile_strategy_user",
            max_alerts: 5,
            history_days: 21,
            include_price_details: true,
            include_recommendations: true,
            fertilizer_types: ["nitrogen", "phosphorus", "potassium"],
            alert_types: ["price_threshold", "opportunity", "timing", "risk"]
        };

        if (this.state.field && this.state.field.coordinates) {
            var coords = this.state.field.coordinates;
            payload.latitude = coords.latitude;
            payload.longitude = coords.longitude;
            if (coords.accuracy) {
                payload.location_accuracy = coords.accuracy;
            }
        }

        try {
            var response = await fetch("/api/v1/alerts/mobile-price", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                var apiData = await response.json();
                alertPackage = this.transformMobilePriceAlerts(apiData);
            }
        } catch (error) {
            console.warn("Price alerts fetch failed:", error);
        }

        if (!alertPackage) {
            alertPackage = this.buildSampleAlerts();
        }

        this.state.alerts = alertPackage.alerts;
        this.state.alertSummary = alertPackage.summary;
        this.state.lastAlertUpdate = alertPackage.generatedAt;

        this.renderPriceAlerts(alertPackage.alerts);
        this.renderAlertSummary(alertPackage.summary);
        this.updateAlertTimestamp(alertPackage.generatedAt);
        this.notifyPriceAlerts(alertPackage.alerts);

        if (this.dom.refreshPriceAlertsButton) {
            this.dom.refreshPriceAlertsButton.disabled = false;
        }
    };

    MobileFertilizerStrategyApp.prototype.transformMobilePriceAlerts = function (apiData) {
        if (!apiData) {
            return null;
        }

        var transformed = {
            alerts: [],
            summary: {
                total: 0,
                high: 0,
                medium: 0
            },
            generatedAt: new Date(),
            recommendations: []
        };

        if (apiData.generated_at) {
            transformed.generatedAt = new Date(apiData.generated_at);
        }

        if (apiData.recommendations && apiData.recommendations.length > 0) {
            transformed.recommendations = apiData.recommendations;
        }

        if (apiData.alerts && apiData.alerts.length > 0) {
            for (var index = 0; index < apiData.alerts.length; index++) {
                var alertData = apiData.alerts[index];
                var priority = alertData.priority || "medium";
                var normalizedPriority = priority.toLowerCase();

                transformed.summary.total += 1;
                if (normalizedPriority === "high") {
                    transformed.summary.high += 1;
                } else if (normalizedPriority === "medium") {
                    transformed.summary.medium += 1;
                }

                var actions = [];
                if (alertData.recommended_actions && alertData.recommended_actions.length > 0) {
                    for (var actionIndex = 0; actionIndex < alertData.recommended_actions.length; actionIndex++) {
                        var actionText = alertData.recommended_actions[actionIndex];
                        if (typeof actionText === "string" && actionText.trim().length > 0) {
                            actions.push(actionText);
                        }
                    }
                }
                if (actions.length === 0 && alertData.details && alertData.details.recommendation) {
                    actions.push(alertData.details.recommendation);
                }

                var alert = {
                    id: alertData.alert_id || "mobile_alert_" + index,
                    title: alertData.title || "Market alert",
                    summary: alertData.summary || alertData.message || "Market change detected.",
                    priority: normalizedPriority,
                    alertType: alertData.alert_type || "price_threshold",
                    price: alertData.price_per_unit || null,
                    unit: alertData.price_unit || "$/ton",
                    priceChange: alertData.price_change_percent,
                    region: alertData.region || apiData.region || "US",
                    recommendedActions: actions,
                    requiresAction: alertData.requires_action === true,
                    confidence: alertData.confidence_score || 0,
                    actionDeadline: alertData.action_deadline ? new Date(alertData.action_deadline) : null,
                    createdAt: alertData.created_at ? new Date(alertData.created_at) : transformed.generatedAt
                };

                transformed.alerts.push(alert);
            }
        }

        return transformed;
    };

    MobileFertilizerStrategyApp.prototype.renderPriceAlerts = function (alerts) {
        if (!this.dom.priceAlertList) {
            return;
        }

        this.dom.priceAlertList.innerHTML = "";

        if (!alerts || alerts.length === 0) {
            if (this.dom.priceAlertPlaceholder) {
                this.dom.priceAlertPlaceholder.classList.remove("d-none");
                this.dom.priceAlertPlaceholder.textContent = "No active price alerts. Capture GPS to personalize alerts.";
                this.dom.priceAlertList.appendChild(this.dom.priceAlertPlaceholder);
            }
            return;
        }

        if (this.dom.priceAlertPlaceholder && this.dom.priceAlertPlaceholder.parentNode === this.dom.priceAlertList) {
            this.dom.priceAlertPlaceholder.remove();
        }

        for (var index = 0; index < alerts.length; index++) {
            var alert = alerts[index];

            var listItem = document.createElement("li");
            listItem.className = "price-alert-card " + alert.priority;

            var title = document.createElement("p");
            title.className = "price-alert-title";
            title.textContent = alert.title;
            listItem.appendChild(title);

            var summary = document.createElement("p");
            summary.className = "price-alert-summary";
            summary.textContent = alert.summary;
            listItem.appendChild(summary);

            var meta = document.createElement("div");
            meta.className = "price-alert-meta";

            var leftMeta = document.createElement("span");
            if (alert.price !== null && alert.price !== undefined) {
                leftMeta.textContent = "$" + alert.price.toFixed(2) + " " + alert.unit;
            } else {
                leftMeta.textContent = "Price pending";
            }
            meta.appendChild(leftMeta);

            var rightMeta = document.createElement("span");
            var changeLabel = "--";
            if (alert.priceChange !== null && alert.priceChange !== undefined) {
                var sign = alert.priceChange >= 0 ? "+" : "";
                changeLabel = sign + alert.priceChange.toFixed(1) + "%";
            }
            rightMeta.textContent = changeLabel + " • " + (alert.region || "Region pending");
            meta.appendChild(rightMeta);

            listItem.appendChild(meta);

            if (alert.recommendedActions && alert.recommendedActions.length > 0) {
                var actionsWrapper = document.createElement("div");
                actionsWrapper.className = "price-alert-actions";

                for (var actionIndex = 0; actionIndex < alert.recommendedActions.length; actionIndex++) {
                    var actionText = alert.recommendedActions[actionIndex];
                    var actionPill = document.createElement("span");
                    actionPill.className = "price-alert-pill";
                    actionPill.textContent = actionText;
                    actionsWrapper.appendChild(actionPill);
                }

                listItem.appendChild(actionsWrapper);
            }

            this.dom.priceAlertList.appendChild(listItem);
        }
    };

    MobileFertilizerStrategyApp.prototype.renderAlertSummary = function (summary) {
        if (!summary) {
            return;
        }

        if (this.dom.alertSummaryTotal) {
            this.dom.alertSummaryTotal.textContent = summary.total + " alerts";
        }

        if (this.dom.alertSummaryHigh) {
            this.dom.alertSummaryHigh.textContent = summary.high + " high";
        }

        if (this.dom.alertSummaryMedium) {
            this.dom.alertSummaryMedium.textContent = summary.medium + " medium";
        }
    };

    MobileFertilizerStrategyApp.prototype.updateAlertTimestamp = function (generatedAt) {
        if (!this.dom.priceAlertLastUpdatedLabel) {
            return;
        }

        if (!generatedAt) {
            this.dom.priceAlertLastUpdatedLabel.textContent = "Last checked: --";
            return;
        }

        this.dom.priceAlertLastUpdatedLabel.textContent = "Last checked: " + generatedAt.toLocaleTimeString();
    };

    MobileFertilizerStrategyApp.prototype.buildSampleAlerts = function () {
        var now = new Date();
        var alerts = [];

        alerts.push({
            id: "sample_high",
            title: "Nitrogen pricing up 7.4%",
            summary: "Nitrogen prices increased sharply this week. Lock in quotes before weekend trading.",
            priority: "high",
            alertType: "price_threshold",
            price: 642.75,
            unit: "$/ton",
            priceChange: 7.4,
            region: "Corn Belt",
            recommendedActions: [
                "Confirm supplier availability",
                "Revisit sidedress timing plan"
            ],
            requiresAction: true,
            confidence: 0.82,
            actionDeadline: new Date(now.getTime() + 6 * 60 * 60 * 1000),
            createdAt: now
        });

        alerts.push({
            id: "sample_medium",
            title: "Phosphorus purchase opportunity",
            summary: "DAP pricing dipped slightly versus 30-day average. Consider filling fall inventory.",
            priority: "medium",
            alertType: "opportunity",
            price: 598.10,
            unit: "$/ton",
            priceChange: -2.1,
            region: "Great Plains",
            recommendedActions: [
                "Compare dealer quotes",
                "Coordinate delivery timing"
            ],
            requiresAction: false,
            confidence: 0.68,
            actionDeadline: null,
            createdAt: now
        });

        var summary = {
            total: alerts.length,
            high: 1,
            medium: 1
        };

        return {
            alerts: alerts,
            summary: summary,
            generatedAt: now,
            recommendations: []
        };
    };

    MobileFertilizerStrategyApp.prototype.notifyPriceAlerts = function (alerts) {
        if (!alerts || alerts.length === 0) {
            return;
        }

        var hasShownNotification = false;

        for (var index = 0; index < alerts.length; index++) {
            var alert = alerts[index];
            if (alert.priority === "high" && alert.requiresAction) {
                this.showNotification("High priority price alert: " + alert.title, {
                    type: "warning",
                    duration: 6000
                });

                if (typeof window !== "undefined" && "Notification" in window) {
                    if (Notification.permission === "granted") {
                        try {
                            new Notification(alert.title, {
                                body: alert.summary,
                                tag: alert.id
                            });
                        } catch (notificationError) {
                            console.debug("Native notification skipped:", notificationError);
                        }
                    }
                }

                hasShownNotification = true;
                break;
            }
        }

        if (!hasShownNotification) {
            var firstAlert = alerts[0];
            this.showNotification(firstAlert.title, { type: "info", duration: 4000 });
        }
    };

    MobileFertilizerStrategyApp.prototype.refreshStrategyData = async function () {
        this.showNotification("Refreshing strategy data...", { type: "info" });
        await this.fetchStrategySummary();
        await this.fetchPriceSignals();
        await this.fetchMobilePriceAlerts();
        this.showNotification("Strategy data refreshed", { type: "success" });
    };

    MobileFertilizerStrategyApp.prototype.handleSectionToggle = function (event) {
        var target = event.currentTarget;
        var contentId = target.getAttribute("data-target");
        var contentElement = document.getElementById(contentId);

        if (!contentElement) {
            return;
        }

        if (contentElement.classList.contains("hidden")) {
            contentElement.classList.remove("hidden");
            target.classList.remove("rotate");
        } else {
            contentElement.classList.add("hidden");
            target.classList.add("rotate");
        }
    };

    MobileFertilizerStrategyApp.prototype.handleGpsCapture = async function () {
        if (!navigator.geolocation) {
            this.showNotification("GPS not supported on this device", { type: "error" });
            return;
        }

        this.showNotification("Capturing GPS location...", { type: "info" });

        var self = this;
        navigator.geolocation.getCurrentPosition(
            async function (position) {
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                self.state.field.coordinates = {
                    latitude: latitude,
                    longitude: longitude,
                    accuracy: position.coords.accuracy
                };
                self.state.field.name = "Field @ " + latitude.toFixed(4) + ", " + longitude.toFixed(4);

                if (self.dom.activeFieldName) {
                    self.dom.activeFieldName.textContent = self.state.field.name;
                }
                if (self.dom.gpsStatus) {
                    self.dom.gpsStatus.textContent = latitude.toFixed(4) + ", " + longitude.toFixed(4);
                }
                if (self.dom.gpsDetail) {
                    self.dom.gpsDetail.textContent = "Accuracy ±" + Math.round(position.coords.accuracy) + " m";
                }

                if (self.offlineDatabase) {
                    await self.offlineDatabase.saveFieldData({
                        id: "mobile_strategy_field",
                        coordinates: self.state.field.coordinates,
                        name: self.state.field.name,
                        updated_from: "mobile-strategy"
                    });
                }

                self.showNotification("GPS captured successfully", { type: "success" });
                self.updateOfflineQueueCount();
                await self.fetchMobilePriceAlerts();
            },
            function (error) {
                self.showNotification("Unable to capture location: " + error.message, { type: "error" });
            },
            {
                enableHighAccuracy: true,
                timeout: 8000,
                maximumAge: 30000
            }
        );
    };

    MobileFertilizerStrategyApp.prototype.handleCameraCapture = function () {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.showNotification("Camera not supported on this device", { type: "error" });
            return;
        }

        var self = this;
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
            .then(function (stream) {
                self.cameraStream = stream;
                self.openCameraOverlay(stream);
            })
            .catch(function (error) {
                console.error("Camera error:", error);
                self.showNotification("Unable to access camera: " + error.message, { type: "error" });
            });
    };

    MobileFertilizerStrategyApp.prototype.openCameraOverlay = function (stream) {
        if (this.cameraOverlay) {
            this.closeCameraOverlay();
        }

        this.cameraOverlay = document.createElement("div");
        this.cameraOverlay.className = "camera-overlay";
        this.cameraOverlay.innerHTML = "" +
            "<div class=\"camera-modal\">" +
            "  <video id=\"mobileStrategyCameraVideo\" autoplay playsinline></video>" +
            "  <div class=\"camera-controls\">" +
            "    <button class=\"btn btn-danger\" id=\"mobileCameraClose\"><i class=\"fas fa-times\"></i></button>" +
            "    <button class=\"btn btn-success\" id=\"mobileCameraCapture\"><i class=\"fas fa-camera\"></i></button>" +
            "  </div>" +
            "</div>";

        document.body.appendChild(this.cameraOverlay);

        var videoElement = document.getElementById("mobileStrategyCameraVideo");
        videoElement.srcObject = stream;

        var closeButton = document.getElementById("mobileCameraClose");
        var captureButton = document.getElementById("mobileCameraCapture");

        closeButton.addEventListener("click", this.closeCameraOverlay.bind(this));
        captureButton.addEventListener("click", this.capturePhotoFrame.bind(this));
    };

    MobileFertilizerStrategyApp.prototype.capturePhotoFrame = function () {
        if (!this.dom.photoCanvas || !this.cameraStream) {
            this.showNotification("Camera not ready", { type: "error" });
            return;
        }

        var videoElement = document.getElementById("mobileStrategyCameraVideo");
        if (!videoElement) {
            this.showNotification("Camera preview missing", { type: "error" });
            return;
        }

        var canvas = this.dom.photoCanvas;
        var context = canvas.getContext("2d");

        canvas.classList.remove("d-none");
        canvas.width = videoElement.videoWidth || 1280;
        canvas.height = videoElement.videoHeight || 720;
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        var self = this;
        canvas.toBlob(function (blob) {
            if (!blob) {
                self.showNotification("Unable to capture photo", { type: "error" });
                return;
            }

            if (self.dom.cameraPreview) {
                var imageUrl = URL.createObjectURL(blob);
                self.dom.cameraPreview.srcObject = null;
                self.dom.cameraPreview.innerHTML = "";
                var imageElement = document.createElement("img");
                imageElement.src = imageUrl;
                imageElement.alt = "Captured field photo";
                imageElement.style.width = "100%";
                imageElement.style.height = "100%";
                imageElement.style.objectFit = "cover";
                imageElement.style.borderRadius = "12px";
                self.dom.cameraPreview.appendChild(imageElement);
            }

            if (self.offlineDatabase) {
                var metadata = {
                    location: self.state.field.coordinates,
                    captured_at: new Date().toISOString(),
                    type: "fertilizer-strategy"
                };
                self.offlineDatabase.savePhoto({
                    blob: blob,
                    metadata: metadata
                }).then(function () {
                    self.showNotification("Photo saved for sync", { type: "success" });
                    self.incrementPhotoCounter();
                    self.updateOfflineQueueCount();
                }).catch(function (error) {
                    console.error("Photo save failed:", error);
                    self.showNotification("Failed to store photo offline", { type: "error" });
                });
            }

            self.closeCameraOverlay();
        }, "image/jpeg", 0.85);
    };

    MobileFertilizerStrategyApp.prototype.incrementPhotoCounter = function () {
        if (!this.dom.photoCount) {
            return;
        }

        var current = parseInt(this.dom.photoCount.textContent, 10);
        if (isNaN(current)) {
            current = 0;
        }
        current += 1;
        this.dom.photoCount.textContent = current + " stored";
        this.updatePhotoHint();
    };

    MobileFertilizerStrategyApp.prototype.closeCameraOverlay = function () {
        if (this.cameraOverlay && this.cameraOverlay.parentNode) {
            this.cameraOverlay.parentNode.removeChild(this.cameraOverlay);
        }
        this.cameraOverlay = null;

        if (this.cameraStream) {
            var tracks = this.cameraStream.getTracks();
            for (var index = 0; index < tracks.length; index++) {
                tracks[index].stop();
            }
        }
        this.cameraStream = null;
    };

    MobileFertilizerStrategyApp.prototype.saveStrategyOffline = async function () {
        if (!this.offlineDatabase || !this.state.summary) {
            this.showNotification("Nothing to store offline yet", { type: "warning" });
            return;
        }

        var strategyPayload = {
            id: "mobile_strategy_snapshot",
            summary: this.state.summary,
            marketSignals: this.state.marketSignals,
            field: this.state.field,
            saved_at: new Date().toISOString(),
            source: "mobile-strategy-interface"
        };

        try {
            await this.offlineDatabase.saveFieldData(strategyPayload);
            this.showNotification("Strategy snapshot stored offline", { type: "success" });
            this.updateOfflineQueueCount();
        } catch (error) {
            console.error("Offline save failed:", error);
            this.showNotification("Failed to store strategy offline", { type: "error" });
        }
    };

    MobileFertilizerStrategyApp.prototype.handleAnalysisSelection = function (event) {
        var chip = event.currentTarget;
        var analysisType = chip.getAttribute("data-analysis");

        for (var index = 0; index < this.dom.analysisChips.length; index++) {
            this.dom.analysisChips[index].classList.remove("active");
        }
        chip.classList.add("active");

        this.refreshAnalysisChart(analysisType);
        this.updateAnalysisSummary(analysisType);
    };

    MobileFertilizerStrategyApp.prototype.refreshAnalysisChart = function (analysisType) {
        if (!this.chart) {
            return;
        }

        var data = [0, 0, 0];
        if (analysisType === "profitability") {
            data[0] = this.chartData.profitability;
            data[1] = this.chartData.sustainability;
            data[2] = this.chartData.risk;
        } else if (analysisType === "sustainability") {
            data[0] = this.chartData.sustainability;
            data[1] = this.chartData.profitability;
            data[2] = 100 - this.chartData.risk;
        } else if (analysisType === "risk") {
            data[0] = 100 - this.chartData.risk;
            data[1] = this.chartData.profitability;
            data[2] = this.chartData.sustainability;
        } else if (analysisType === "logistics") {
            data[0] = Math.min(100, this.chartData.profitability + 5);
            data[1] = Math.min(100, this.chartData.sustainability + 3);
            data[2] = Math.max(0, this.chartData.risk - 10);
        }

        this.chart.data.datasets[0].data = data;
        this.chart.update();
    };

    MobileFertilizerStrategyApp.prototype.updateAnalysisSummary = function (analysisType) {
        if (!this.dom.analysisSummary) {
            return;
        }

        var message = "Strategy analysis available.";
        if (analysisType === "profitability") {
            message = "Projected ROI exceeds baseline by " + this.state.summary.projectedRoi + ". Review price hedging opportunities.";
        } else if (analysisType === "sustainability") {
            message = "Sustainability index at " + this.state.summary.sustainability + ". Maintain cover crop integration for nutrient credits.";
        } else if (analysisType === "risk") {
            message = "Risk-adjusted score suggests medium exposure. Monitor price volatility and weather windows.";
        } else if (analysisType === "logistics") {
            message = "Logistics readiness strong. Verify equipment calibration and product inventory before field operations.";
        }

        this.dom.analysisSummary.textContent = message;
    };

    MobileFertilizerStrategyApp.prototype.handleRecommendationTrack = function (recommendation) {
        if (!recommendation) {
            return;
        }

        this.showNotification("Tracking recommendation: " + (recommendation.title || "Strategy item"), { type: "info" });

        if (this.dom.trackingActivityType) {
            this.dom.trackingActivityType.value = "application";
        }
        if (this.dom.trackingStatus) {
            this.dom.trackingStatus.value = "scheduled";
        }
        if (this.dom.trackingNotesInput) {
            this.dom.trackingNotesInput.value = recommendation.detail || recommendation.title || "";
        }
        if (this.dom.trackingPanel && this.dom.trackingPanel.scrollIntoView) {
            this.dom.trackingPanel.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    MobileFertilizerStrategyApp.prototype.handleBottomNavigation = function (event) {
        var target = event.currentTarget;
        var view = target.getAttribute("data-view");
        this.setActiveNavigation(view);
        this.scrollToSection(view);
    };

    MobileFertilizerStrategyApp.prototype.setActiveNavigation = function (view) {
        for (var index = 0; index < this.dom.bottomNavItems.length; index++) {
            var item = this.dom.bottomNavItems[index];
            item.classList.remove("active");
        }

        for (var navIndex = 0; navIndex < this.dom.bottomNavItems.length; navIndex++) {
            var navItem = this.dom.bottomNavItems[navIndex];
            if (navItem.getAttribute("data-view") === view) {
                navItem.classList.add("active");
            }
        }
    };

    MobileFertilizerStrategyApp.prototype.scrollToSection = function (view) {
        var section = null;
        if (view === "summary") {
            section = this.dom.sectionMap.summary;
        } else if (view === "market") {
            section = this.dom.sectionMap.market;
        } else if (view === "actions") {
            section = this.dom.sectionMap.actions;
        } else if (view === "insights") {
            section = this.dom.sectionMap.insights;
        }

        if (section && section.scrollIntoView) {
            section.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    };

    MobileFertilizerStrategyApp.prototype.handleActionCompleted = async function () {
        this.showNotification("Marked action as completed", { type: "success" });
        var notes = null;
        if (this.dom.nextActionDescription) {
            this.dom.nextActionDescription.textContent = "Action recorded. Awaiting new recommendation.";
            notes = this.dom.nextActionDescription.textContent;
        }
        var payload = this.buildQuickTrackingPayload("application", "completed", notes);
        await this.recordStrategyProgress(payload);
    };

    MobileFertilizerStrategyApp.prototype.handleActionReschedule = function () {
        this.showNotification("Reschedule request saved", { type: "info" });
        if (this.dom.nextActionDue) {
            this.dom.nextActionDue.textContent = "Rescheduling pending";
        }
    };

    MobileFertilizerStrategyApp.prototype.handleOnline = function () {
        this.updateNetworkIndicators(true);
        this.showNotification("Connection restored", { type: "success" });
        this.updateOfflineQueueCount();
        this.fetchTrackingSummary();
    };

    MobileFertilizerStrategyApp.prototype.handleOffline = function () {
        this.updateNetworkIndicators(false);
        this.showNotification("Offline mode activated", { type: "warning" });
    };

    MobileFertilizerStrategyApp.prototype.handleDeviceNetworkChange = function (event) {
        if (!event || !event.detail) {
            return;
        }

        var info = event.detail;
        if (info.saveData) {
            this.showNotification("Data saving mode enabled", { type: "info" });
        }
        if (info.effectiveType === "2g" || info.effectiveType === "slow-2g") {
            this.showNotification("Network is slow - some features limited", { type: "warning" });
        }
    };

    MobileFertilizerStrategyApp.prototype.handleVisibilityChange = function (event) {
        if (!event || !event.detail) {
            return;
        }

        if (event.detail.visible) {
            this.refreshStrategyData();
        }
    };

    MobileFertilizerStrategyApp.prototype.updateNetworkIndicators = function (isOnline) {
        if (this.dom.syncStatusDot) {
            this.dom.syncStatusDot.style.backgroundColor = isOnline ? "#4caf50" : "#ffc107";
        }
        if (this.dom.syncStatusLabel) {
            this.dom.syncStatusLabel.textContent = isOnline ? "Online" : "Offline mode";
        }

        if (this.dom.networkBanner) {
            if (isOnline) {
                this.dom.networkBanner.classList.remove("show");
            } else {
                this.dom.networkBannerMessage.textContent = "Offline mode - changes will sync when online";
                this.dom.networkBanner.classList.add("show");
            }
        }
    };

    MobileFertilizerStrategyApp.prototype.updateOfflineQueueCount = async function () {
        if (!this.offlineDatabase || !this.dom.offlineQueueCount) {
            return;
        }

        try {
            var stats = await this.offlineDatabase.getDatabaseStats();
            var queueSize = stats.syncQueue || 0;
            this.state.offlineQueue = queueSize;
            this.dom.offlineQueueCount.textContent = queueSize.toString();
            await this.updatePendingTrackingCount();
        } catch (error) {
            console.error("Offline queue update failed:", error);
        }
    };

    MobileFertilizerStrategyApp.prototype.startAutoRefresh = function () {
        var self = this;
        this.autoRefreshTimer = setInterval(function () {
            self.refreshStrategyData();
        }, 60000);
    };

    MobileFertilizerStrategyApp.prototype.startQueueMonitoring = function () {
        var self = this;
        this.queueRefreshTimer = setInterval(function () {
            self.updateOfflineQueueCount();
        }, 15000);
    };

    MobileFertilizerStrategyApp.prototype.showNotification = function (message, options) {
        var config = options || {};
        if (this.deviceIntegration && this.deviceIntegration.showNotification) {
            this.deviceIntegration.showNotification(message, config);
        } else {
            console.log("Notification:", message);
        }
    };

    document.addEventListener("visibilitychange", function () {
        if (document.hidden === false) {
            window.dispatchEvent(new Event("resize"));
        }
    });

    new MobileFertilizerStrategyApp();
}());
