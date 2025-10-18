/**
 * Tests for Fertilizer Strategy Visualization System
 * Validates initialization, fallback handling, and interactive controls.
 */

const buildDashboardDom = () => `
  <div id="app-root">
    <button id="refreshDashboardBtn"></button>
    <span id="lastUpdatedLabel"></span>
    <span id="priceRefreshLabel"></span>

    <div id="roiValue"></div>
    <div id="roiTrend"></div>
    <div id="costValue"></div>
    <div id="costTrend"></div>
    <div id="yieldValue"></div>
    <div id="yieldTrend"></div>
    <div id="impactValue"></div>
    <div id="impactTrend"></div>

    <span id="optimizationStatus"></span>
    <table><tbody id="summaryTableBody"></tbody></table>
    <div id="recommendationsList"></div>

    <canvas id="performanceTrendChart"></canvas>
    <canvas id="costBreakdownChart"></canvas>
    <canvas id="yieldContributionChart"></canvas>
    <canvas id="scenarioComparisonChart"></canvas>
    <canvas id="yieldResponseChart"></canvas>

    <div id="scenarioControlPanel">
      <span class="analysis-chip active" data-scenario="baseline"></span>
      <span class="analysis-chip" data-scenario="optimistic"></span>
      <span class="analysis-chip" data-scenario="pessimistic"></span>
    </div>
    <table><tbody id="scenarioSummaryBody"></tbody></table>
    <p id="yieldResponseSummary"></p>

    <div id="sensitivityAnalysisChart"></div>
    <div id="environmentalImpactMap"></div>

    <div id="tradeoffControlPanel">
      <span class="analysis-chip active" data-metric="profit"></span>
      <span class="analysis-chip" data-metric="cost"></span>
    </div>
    <table>
      <tbody id="tradeoffTableBody"></tbody>
    </table>

    <div id="sustainabilityList"></div>
    <div id="priceRows"></div>
    <div id="alertsContainer"></div>
    <div id="activityLog"></div>
  </div>
`;

const flushPromises = () => new Promise((resolve) => setTimeout(resolve, 0));

describe("Fertilizer Strategy Visualization", () => {
    let originalConsoleWarn;
    let originalConsoleError;
    let originalConsoleLog;

    beforeEach(() => {
        jest.resetModules();

        document.body.innerHTML = buildDashboardDom();
        Object.defineProperty(document, "readyState", {
            configurable: true,
            value: "complete"
        });

        originalConsoleWarn = console.warn;
        originalConsoleError = console.error;
        originalConsoleLog = console.log;
        console.warn = jest.fn();
        console.error = jest.fn();
        console.log = jest.fn();

        global.fetch = jest.fn().mockRejectedValue(new Error("network failure"));
        global.Chart = jest.fn(() => ({ destroy: jest.fn() }));
        global.Chart.defaults = {
            font: {},
            plugins: {
                legend: { labels: {} },
                tooltip: {}
            }
        };
        global.d3 = null;
        global.setInterval = jest.fn();
        window.setInterval = global.setInterval;

        jest.isolateModules(() => {
            require("../fertilizer-strategy-visualizations.js");
        });
    });

    afterEach(() => {
        console.warn = originalConsoleWarn;
        console.error = originalConsoleError;
        console.log = originalConsoleLog;
        delete window.FertilizerStrategyVisualization;
        jest.clearAllMocks();
    });

    test("loads fallback metrics when API requests fail", async () => {
        await flushPromises();
        expect(document.getElementById("roiValue").textContent).toBe("18.4%");
        expect(document.getElementById("priceRows").children.length).toBeGreaterThan(0);
        expect(console.warn).toHaveBeenCalled();
    });

    test("updates scenario selection chips and summary", async () => {
        await flushPromises();
        const optimisticChip = document.querySelector('[data-scenario="optimistic"]');
        optimisticChip.dispatchEvent(new window.Event("click", { bubbles: true }));
        expect(optimisticChip.classList.contains("active")).toBe(true);
        expect(document.querySelector('[data-scenario="baseline"]').classList.contains("active")).toBe(false);
        expect(document.getElementById("scenarioSummaryBody").textContent).toContain("Net Profit");
    });

    test("highlights selected trade-off metric row", async () => {
        await flushPromises();
        const costChip = document.querySelector('[data-metric="cost"]');
        costChip.dispatchEvent(new window.Event("click", { bubbles: true }));
        const rows = document.getElementById("tradeoffTableBody").querySelectorAll("tr");
        const highlightedRows = Array.from(rows).filter((row) => row.classList.contains("table-success"));
        expect(highlightedRows.length).toBe(1);
        expect(highlightedRows[0].textContent).toContain("Advance purchase 40% nitrogen");
    });

    test("displays placeholders when D3 is unavailable", async () => {
        await flushPromises();
        const sensitivityPlaceholder = document.getElementById("sensitivityAnalysisChart").textContent;
        const envPlaceholder = document.getElementById("environmentalImpactMap").textContent;
        expect(sensitivityPlaceholder).toContain("D3.js is required");
        expect(envPlaceholder).toContain("D3.js is required");
    });
});
