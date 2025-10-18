/**
 * Tests for mobile price alert integration.
 */

const buildMobileDom = () => `
    <div id="app-root">
        <button id="captureGpsButton"></button>
        <button id="captureImageButton"></button>
        <button id="refreshStrategyButton"></button>
        <button id="saveOfflineButton"></button>

        <div id="strategySummarySection"></div>
        <div id="marketSignalsSection"></div>
        <div id="fieldActionsSection"></div>
        <div id="analysisSection"></div>

        <span id="summaryProjectedRoi"></span>
        <span id="summaryProfitStatus"></span>
        <span id="summaryStrategyCost"></span>
        <span id="summaryCostStatus"></span>
        <span id="summaryYieldImpact"></span>
        <span id="summaryYieldStatus"></span>
        <span id="summarySustainability"></span>
        <span id="summarySustainabilityStatus"></span>

        <div id="recommendationList"></div>
        <ul id="priceTrendList"></ul>
        <span id="priceLastUpdatedLabel"></span>
        <button id="priceRefreshButton"></button>

        <ul id="mobilePriceAlertList">
            <li id="priceAlertPlaceholder"></li>
        </ul>
        <span id="priceAlertLastUpdatedLabel"></span>
        <button id="refreshPriceAlertsButton"></button>
        <span id="alertSummaryTotal"></span>
        <span id="alertSummaryHigh"></span>
        <span id="alertSummaryMedium"></span>

        <span id="syncStatusDot"></span>
        <span id="syncStatusLabel"></span>
        <div id="networkBanner"></div>
        <span id="networkBannerMessage"></span>
        <span id="activeFieldName"></span>
        <span id="nextActionDue"></span>
        <p id="nextActionDescription"></p>
        <button id="markActionCompleteButton"></button>
        <button id="rescheduleActionButton"></button>

        <div class="analysis-chip" data-analysis="profitability"></div>
        <div class="analysis-chip" data-analysis="sustainability"></div>
        <div id="analysisSummary"></div>
        <canvas id="analysisChart"></canvas>
        <div class="bottom-nav-item" data-target="summary"></div>

        <span id="offlineQueueCount"></span>
        <span id="gpsStatus"></span>
        <span id="gpsDetail"></span>
        <video id="cameraPreview"></video>
        <canvas id="photoCanvas"></canvas>
        <span id="photoCount"></span>
    </div>
`;

const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

const createSuccessFetch = () => {
    const alertPayload = {
        user_id: "mobile_strategy_user",
        region: "Corn Belt",
        generated_at: new Date().toISOString(),
        alerts: [
            {
                alert_id: "api_high",
                title: "API High Priority Alert",
                summary: "Nitrogen prices jumped 6.2% this week.",
                priority: "high",
                alert_type: "price_threshold",
                price_per_unit: 610.25,
                price_unit: "$\/ton",
                price_change_percent: 6.2,
                region: "Corn Belt",
                recommended_actions: [
                    "Coordinate supplier quote",
                    "Review sidedress rates"
                ],
                requires_action: true,
                confidence_score: 0.81,
                action_deadline: new Date(Date.now() + 4 * 3600 * 1000).toISOString(),
                created_at: new Date().toISOString()
            }
        ],
        recommendations: ["Evaluate early purchase options."]
    };

    return jest.fn().mockImplementation((url) => {
        if (typeof url === "string" && url.indexOf("/api/v1/alerts/mobile-price") !== -1) {
            return Promise.resolve({ ok: true, json: async () => alertPayload });
        }
        if (typeof url === "string" && url.indexOf("/api/v1/prices/fertilizer-current") !== -1) {
            return Promise.resolve({
                ok: true,
                json: async () => ({
                    prices: [
                        {
                            product: "Sample Product",
                            price: 500,
                            unit: "$\/ton",
                            trend_7d: 2.5,
                            region: "Test"
                        }
                    ]
                })
            });
        }
        if (typeof url === "string" && url.indexOf("/api/v1/strategies/compare") !== -1) {
            return Promise.resolve({ ok: true, json: async () => ({ comparisons: [], recommendations: [] }) });
        }
        return Promise.reject(new Error("Unhandled request"));
    });
};

const createFallbackFetch = () => {
    return jest.fn().mockImplementation((url) => {
        if (typeof url === "string" && url.indexOf("/api/v1/alerts/mobile-price") !== -1) {
            return Promise.resolve({ ok: false, json: async () => ({}) });
        }
        if (typeof url === "string" && url.indexOf("/api/v1/prices/fertilizer-current") !== -1) {
            return Promise.resolve({ ok: true, json: async () => ({ prices: [] }) });
        }
        if (typeof url === "string" && url.indexOf("/api/v1/strategies/compare") !== -1) {
            return Promise.resolve({ ok: true, json: async () => ({ comparisons: [], recommendations: [] }) });
        }
        return Promise.reject(new Error("Unhandled request"));
    });
};

describe("Mobile price alerts integration", () => {
    let originalConsoleWarn;
    let originalConsoleError;
    let originalConsoleLog;
    let originalNotification;
    let loadModule;
    let originalGetContext;

    beforeEach(() => {
        jest.resetModules();

        document.body.innerHTML = buildMobileDom();
        Object.defineProperty(document, "readyState", {
            configurable: true,
            value: "complete"
        });

        global.navigator = { onLine: true };

        originalConsoleWarn = console.warn;
        originalConsoleError = console.error;
        originalConsoleLog = console.log;
        console.warn = jest.fn();
        console.error = jest.fn();
        console.log = jest.fn();

        originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
            canvas: {}
        }));

        global.Chart = jest.fn(() => ({
            destroy: jest.fn(),
            update: jest.fn(),
            data: {
                datasets: [
                    {
                        data: [0, 0, 0]
                    }
                ]
            }
        }));
        global.Chart.defaults = { font: {}, plugins: { legend: { labels: {} }, tooltip: {} } };
        global.setInterval = jest.fn();
        window.setInterval = global.setInterval;

        class MockMobileDeviceIntegration {
            constructor() {
                this.permissions = { notifications: false };
            }
            showNotification(message) {
                console.log("Mock notification:", message);
            }
        }

        class MockMobileOfflineDatabase {
            constructor() {
                this.db = {};
            }
            saveFieldData() {
                return Promise.resolve();
            }
            savePhoto() {
                return Promise.resolve();
            }
            getDatabaseStats() {
                return Promise.resolve({ pending: 0 });
            }
        }

        global.MobileDeviceIntegration = MockMobileDeviceIntegration;
        window.MobileDeviceIntegration = MockMobileDeviceIntegration;
        global.MobileOfflineDatabase = MockMobileOfflineDatabase;

        originalNotification = global.Notification;
        global.Notification = { permission: "denied" };
        window.Notification = global.Notification;

        loadModule = () => {
            jest.isolateModules(() => {
                require("../mobile-fertilizer-strategy.js");
            });
        };
    });

    afterEach(() => {
        console.warn = originalConsoleWarn;
        console.error = originalConsoleError;
        console.log = originalConsoleLog;
        if (originalNotification === undefined) {
            delete global.Notification;
            delete window.Notification;
        } else {
            global.Notification = originalNotification;
            window.Notification = originalNotification;
        }
        delete global.MobileDeviceIntegration;
        delete window.MobileDeviceIntegration;
        delete global.MobileOfflineDatabase;
        if (originalGetContext) {
            HTMLCanvasElement.prototype.getContext = originalGetContext;
        }
        jest.clearAllMocks();
    });

    test("renders API-driven price alerts and summary", async () => {
        global.fetch = createSuccessFetch();
        loadModule();
        await flushPromises();

        const alertList = document.getElementById("mobilePriceAlertList");
        expect(alertList.children.length).toBeGreaterThan(0);
        expect(alertList.children[0].textContent).toContain("API High Priority Alert");

        const highSummary = document.getElementById("alertSummaryHigh").textContent;
        expect(highSummary).toContain("1");

        const timestamp = document.getElementById("priceAlertLastUpdatedLabel").textContent;
        expect(timestamp).toContain("Last checked:");
    });

    test("falls back to sample alerts when API fails", async () => {
        global.fetch = createFallbackFetch();
        loadModule();
        await flushPromises();

        const alertList = document.getElementById("mobilePriceAlertList");
        expect(alertList.children.length).toBeGreaterThan(0);
        expect(document.getElementById("alertSummaryTotal").textContent).toContain("2");
    });
});
