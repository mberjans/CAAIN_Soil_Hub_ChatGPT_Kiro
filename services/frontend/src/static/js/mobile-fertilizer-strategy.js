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
            field: {
                name: "No field selected",
                coordinates: null
            },
            offlineQueue: 0,
            lastPriceUpdate: null
        };
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

        window.addEventListener("online", this.handleOnline.bind(this));
        window.addEventListener("offline", this.handleOffline.bind(this));

        document.addEventListener("mobileDevice:networkChange", this.handleDeviceNetworkChange.bind(this));
        document.addEventListener("mobileDevice:visibilityChange", this.handleVisibilityChange.bind(this));
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
        this.updateOfflineQueueCount();
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
            }
        };
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

    MobileFertilizerStrategyApp.prototype.refreshStrategyData = async function () {
        this.showNotification("Refreshing strategy data...", { type: "info" });
        await this.fetchStrategySummary();
        await this.fetchPriceSignals();
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
        this.showNotification("Tracking recommendation: " + (recommendation.title || "Strategy item"), { type: "info" });
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

    MobileFertilizerStrategyApp.prototype.handleActionCompleted = function () {
        this.showNotification("Marked action as completed", { type: "success" });
        if (this.dom.nextActionDescription) {
            this.dom.nextActionDescription.textContent = "Action recorded. Awaiting new recommendation.";
        }
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
