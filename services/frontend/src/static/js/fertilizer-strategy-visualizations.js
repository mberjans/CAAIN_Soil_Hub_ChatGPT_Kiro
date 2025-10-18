// Fertilizer Strategy Visualization System
// Provides comprehensive visualization and analysis features for fertilizer strategy dashboard

(function () {
    "use strict";

    class FertilizerStrategyVisualization {
        constructor() {
            this.charts = {};
            this.state = {
                isRefreshing: false,
                lastUpdated: null,
                activeScenario: "baseline",
                activeMetric: "profit",
                data: null
            };
            this.sampleData = this.buildSampleData();
            this.chartDefaultsConfigured = false;
            this.initializeWhenReady();
        }

        initializeWhenReady() {
            if (document.readyState === "loading") {
                document.addEventListener("DOMContentLoaded", () => this.initialize());
            } else {
                this.initialize();
            }
        }

        initialize() {
            this.cacheDom();
            this.configureChartDefaults();
            this.bindEvents();
            this.refreshData();
            this.startAutoRefresh();
        }

        cacheDom() {
            this.elements = {
                refreshButton: document.getElementById("refreshDashboardBtn"),
                lastUpdatedLabel: document.getElementById("lastUpdatedLabel"),
                priceRefreshLabel: document.getElementById("priceRefreshLabel"),
                scenarioControlPanel: document.getElementById("scenarioControlPanel"),
                scenarioSummaryBody: document.getElementById("scenarioSummaryBody"),
                yieldResponseSummary: document.getElementById("yieldResponseSummary"),
                tradeoffControlPanel: document.getElementById("tradeoffControlPanel"),
                tradeoffTableBody: document.getElementById("tradeoffTableBody"),
                alertsContainer: document.getElementById("alertsContainer"),
                activityLog: document.getElementById("activityLog"),
                priceRows: document.getElementById("priceRows"),
                sustainabilityList: document.getElementById("sustainabilityList"),
                optimizationStatus: document.getElementById("optimizationStatus"),
                summaryTableBody: document.getElementById("summaryTableBody"),
                recommendationsList: document.getElementById("recommendationsList")
            };
        }

        configureChartDefaults() {
            if (this.chartDefaultsConfigured || !window.Chart) {
                return;
            }

            const chart = window.Chart;
            chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
            chart.defaults.plugins.legend.labels.usePointStyle = true;
            chart.defaults.plugins.tooltip.backgroundColor = "rgba(33, 37, 41, 0.9)";
            chart.defaults.plugins.tooltip.titleFont = { weight: "600" };
            chart.defaults.plugins.tooltip.padding = 12;
            this.chartDefaultsConfigured = true;
        }

        bindEvents() {
            if (this.elements.refreshButton) {
                this.elements.refreshButton.addEventListener("click", () => {
                    if (!this.state.isRefreshing) {
                        this.refreshData();
                    }
                });
            }

            if (this.elements.scenarioControlPanel) {
                this.elements.scenarioControlPanel.addEventListener("click", (event) => {
                    const target = event.target.closest(".analysis-chip");
                    if (!target) {
                        return;
                    }
                    this.handleScenarioSelection(target.dataset.scenario);
                });
            }

            if (this.elements.tradeoffControlPanel) {
                this.elements.tradeoffControlPanel.addEventListener("click", (event) => {
                    const target = event.target.closest(".analysis-chip");
                    if (!target) {
                        return;
                    }
                    this.handleMetricSelection(target.dataset.metric);
                });
            }
        }

        async refreshData() {
            this.state.isRefreshing = true;
            this.setPriceRefreshLabel("Refreshing...");

            try {
                const dashboardData = await this.loadDashboardData();
                this.state.data = dashboardData;
                this.updateDashboard(dashboardData);
                this.markRefreshSuccess();
            } catch (error) {
                console.warn("Dashboard refresh failed, using sample data:", error);
                this.state.data = this.sampleData;
                this.updateDashboard(this.sampleData);
                this.setPriceRefreshLabel("Live data unavailable - showing scenario data");
            } finally {
                this.state.isRefreshing = false;
            }
        }

        startAutoRefresh() {
            window.setInterval(() => {
                if (!this.state.isRefreshing) {
                    this.refreshData();
                }
            }, 60000);
        }

        async loadDashboardData() {
            const requests = [
                this.fetchJson("/api/v1/prices/fertilizer-current"),
                this.fetchScenarioAnalysis(),
                this.fetchTradeoffInsights()
            ];

            const [priceData, scenarioData, tradeoffData] = await Promise.all(requests);

            const merged = JSON.parse(JSON.stringify(this.sampleData));

            if (priceData && Array.isArray(priceData.prices)) {
                merged.prices = priceData.prices.map((item) => {
                    const productName = item.fertilizer_type || item.product || "Fertilizer";
                    const unitLabel = item.unit || "$/ton";
                     return {
                        product: productName,
                        region: item.region || "Region",
                        price: item.price_per_unit || item.price || 0,
                        change: item.trend_7d || 0,
                        unit: unitLabel
                    };
                });
            }

            if (scenarioData && scenarioData.analysis_result) {
                merged.analysis = this.transformAnalysisResult(scenarioData.analysis_result);
            }

            if (tradeoffData && tradeoffData.insights) {
                merged.tradeoffs = tradeoffData.insights;
            }

            return merged;
        }

        async fetchJson(url) {
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error("Request failed");
                }
                return response.json();
            } catch (error) {
                throw error;
            }
        }

        async fetchScenarioAnalysis() {
            const payload = {
                analysis_type: "scenario",
                field_size_acres: 640,
                crop_type: "Corn",
                expected_yield_bu_per_acre: 195,
                crop_price_per_bu: 5.1,
                fertilizer_requirements: [
                    { product: "Urea (46-0-0)", fertilizer_type: "nitrogen", rate_lbs_per_acre: 175, n_content: 46 },
                    { product: "DAP (18-46-0)", fertilizer_type: "phosphorus", rate_lbs_per_acre: 35, p_content: 46 },
                    { product: "Potash (0-0-60)", fertilizer_type: "potassium", rate_lbs_per_acre: 40, k_content: 60 }
                ],
                scenarios: ["baseline", "optimistic", "pessimistic", "volatile"],
                analysis_horizon_days: 365,
                confidence_level: 0.95
            };

            try {
                const response = await fetch("/api/v1/price-impact/analyze/scenario", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error("Scenario analysis request failed");
                }

                return response.json();
            } catch (error) {
                return null;
            }
        }

        async fetchTradeoffInsights() {
            try {
                const response = await fetch("/api/v1/price-impact/capabilities");
                if (!response.ok) {
                    throw new Error("Tradeoff insights unavailable");
                }
                const capabilities = await response.json();
                if (capabilities && capabilities.capabilities) {
                    return { insights: this.sampleData.tradeoffs };
                }
                return null;
            } catch (error) {
                return null;
            }
        }

        transformAnalysisResult(analysis) {
            const scenarios = [];
            if (Array.isArray(analysis.scenarios)) {
                analysis.scenarios.forEach((scenario) => {
                    const name = scenario.scenario_name || scenario.scenario_type || "Scenario";
                    const metrics = scenario.metrics || {};
                    scenarios.push({
                        name,
                        keyAdjustment: scenario.assumptions && scenario.assumptions.adjustment ? scenario.assumptions.adjustment : "No adjustment provided",
                        netProfit: metrics.net_profit || analysis.baseline_metrics.net_profit,
                        fertilizerCost: metrics.total_fertilizer_cost || analysis.baseline_metrics.total_fertilizer_cost,
                        revenue: metrics.total_crop_revenue || analysis.baseline_metrics.total_crop_revenue,
                        margin: metrics.profit_margin_percent || analysis.baseline_metrics.profit_margin_percent,
                        riskLevel: scenario.risk_level || "medium",
                        confidence: metrics.confidence || analysis.confidence_score || 0.85,
                        horizon: scenario.assumptions && scenario.assumptions.horizon ? scenario.assumptions.horizon : "Seasonal"
                    });
                });
            }

            const sensitivity = [];
            if (Array.isArray(analysis.sensitivity_results)) {
                analysis.sensitivity_results.forEach((item) => {
                    sensitivity.push({
                        parameter: item.parameter_name,
                        impact: item.elasticity,
                        details: {
                            criticalThreshold: item.critical_threshold,
                            sensitivityScore: item.sensitivity_score
                        }
                    });
                });
            }

            return {
                scenarios,
                sensitivity,
                baseline: analysis.baseline_metrics
            };
        }

        updateDashboard(data) {
            if (!data) {
                return;
            }
            this.updateHeadlineMetrics(data);
            this.populateOptimizationSnapshot(data.optimization);
            this.renderPerformanceChart(data.charts.performance);
            this.renderCostBreakdownChart(data.charts.costBreakdown);
            this.renderYieldContributionChart(data.charts.yieldContribution);
            this.populateSustainability(data.charts.sustainability);
            this.populatePriceRows(data.prices);
            this.populateAlerts(data.alerts);
            this.populateActivityLog(data.activityLog);
            this.renderScenarioComparison(data);
            this.renderYieldResponseChart(data);
            this.renderSensitivityChart(data);
            this.renderEnvironmentalMap(data);
            this.populateTradeoffTable(data);
            this.setLastUpdated();
        }

        updateHeadlineMetrics(data) {
            this.setMetric("roiValue", data.roi.value.toFixed(1) + "%");
            this.setTrend("roiTrend", data.roi.trend);

            this.setMetric("costValue", this.formatCurrency(data.cost.value));
            this.setTrend("costTrend", data.cost.trend);

            this.setMetric("yieldValue", data.yield.value.toFixed(0) + " bu/ac");
            this.setTrend("yieldTrend", data.yield.trend);

            this.setMetric("impactValue", data.impact.value.toFixed(1));
            this.setTrend("impactTrend", data.impact.trend);
        }

        setMetric(elementId, value) {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = value;
            }
        }

        setTrend(elementId, trendValue) {
            const element = document.getElementById(elementId);
            if (!element) {
                return;
            }
            const trend = trendValue || 0;
            const className = trend >= 0 ? "trend-positive" : "trend-negative";
            const icon = trend >= 0 ? "fa-arrow-up" : "fa-arrow-down";
            element.className = "metric-trend " + className;
            element.innerHTML = `<i class="fas ${icon}"></i> ${trend.toFixed(1)} pts`;
        }

        populateOptimizationSnapshot(optimization) {
            if (!optimization || !this.elements.summaryTableBody || !this.elements.recommendationsList) {
                return;
            }

            this.elements.summaryTableBody.innerHTML = "";
            optimization.summary.forEach((item) => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${item.label}</td><td class="text-end">${item.value}<div class="text-muted small">${item.detail}</div></td>`;
                this.elements.summaryTableBody.appendChild(row);
            });

            this.elements.recommendationsList.innerHTML = "";
            optimization.recommendations.forEach((item) => {
                const priorityClass = item.priority === "High" ? "text-danger" : "text-warning";
                const recommendation = document.createElement("div");
                recommendation.className = "recommendation-item";
                recommendation.innerHTML = `<span>${item.action}</span><span class="${priorityClass}">${item.priority} priority</span>`;
                this.elements.recommendationsList.appendChild(recommendation);
            });

            if (this.elements.optimizationStatus) {
                this.elements.optimizationStatus.textContent = optimization.status || "Evaluating";
            }
        }

        renderPerformanceChart(data) {
            const ctx = document.getElementById("performanceTrendChart");
            if (!ctx || !window.Chart) {
                return;
            }

            if (this.charts.performanceTrend) {
                this.charts.performanceTrend.destroy();
            }

            const labels = [];
            const roiValues = [];
            const costValues = [];
            const impactValues = [];
            data.forEach((item) => {
                labels.push(item.month);
                roiValues.push(item.roi);
                costValues.push(item.cost);
                impactValues.push(item.impact);
            });

            this.charts.performanceTrend = new window.Chart(ctx, {
                type: "line",
                data: {
                    labels,
                    datasets: [
                        {
                            label: "ROI",
                            data: roiValues,
                            borderColor: "#198754",
                            backgroundColor: "rgba(25, 135, 84, 0.1)",
                            fill: true,
                            tension: 0.35,
                            yAxisID: "yROI"
                        },
                        {
                            label: "Cost",
                            data: costValues,
                            borderColor: "#ffc107",
                            backgroundColor: "rgba(255, 193, 7, 0.12)",
                            fill: true,
                            tension: 0.35,
                            yAxisID: "yCost"
                        },
                        {
                            label: "Impact Score",
                            data: impactValues,
                            borderColor: "#20c997",
                            borderDash: [6, 4],
                            tension: 0.3,
                            yAxisID: "yROI"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: "index"
                    },
                    scales: {
                        yROI: {
                            type: "linear",
                            position: "left",
                            title: { display: true, text: "ROI / Impact" }
                        },
                        yCost: {
                            type: "linear",
                            position: "right",
                            grid: { drawOnChartArea: false },
                            title: { display: true, text: "Cost ($)" },
                            ticks: {
                                callback: (value) => this.formatNumber(value)
                            }
                        }
                    }
                }
            });
        }

        renderCostBreakdownChart(data) {
            const ctx = document.getElementById("costBreakdownChart");
            if (!ctx || !window.Chart) {
                return;
            }

            if (this.charts.costBreakdown) {
                this.charts.costBreakdown.destroy();
            }

            const labels = [];
            const values = [];
            data.forEach((item) => {
                labels.push(item.nutrient);
                values.push(item.value);
            });

            this.charts.costBreakdown = new window.Chart(ctx, {
                type: "doughnut",
                data: {
                    labels,
                    datasets: [{
                        data: values,
                        backgroundColor: [
                            "rgba(25, 135, 84, 0.85)",
                            "rgba(13, 110, 253, 0.85)",
                            "rgba(255, 193, 7, 0.85)",
                            "rgba(32, 201, 151, 0.85)"
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "bottom" }
                    }
                }
            });
        }

        renderYieldContributionChart(data) {
            const ctx = document.getElementById("yieldContributionChart");
            if (!ctx || !window.Chart) {
                return;
            }

            if (this.charts.yieldContribution) {
                this.charts.yieldContribution.destroy();
            }

            const labels = [];
            const values = [];
            data.forEach((item) => {
                labels.push(item.program);
                values.push(item.value);
            });

            this.charts.yieldContribution = new window.Chart(ctx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [{
                        label: "Yield Contribution",
                        data: values,
                        backgroundColor: "rgba(13, 110, 253, 0.7)",
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 50,
                            ticks: { stepSize: 10 }
                        }
                    }
                }
            });
        }

        renderScenarioComparison(data) {
            const ctx = document.getElementById("scenarioComparisonChart");
            if (!ctx || !window.Chart) {
                return;
            }

            const scenarios = this.getScenarioData(data);
            if (this.charts.scenarioComparison) {
                this.charts.scenarioComparison.destroy();
            }

            const labels = [];
            const netProfit = [];
            const fertilizerCost = [];
            const revenue = [];
            scenarios.forEach((item) => {
                labels.push(item.name);
                netProfit.push(item.netProfit);
                fertilizerCost.push(item.fertilizerCost);
                revenue.push(item.revenue);
            });

            this.charts.scenarioComparison = new window.Chart(ctx, {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        {
                            label: "Net Profit",
                            data: netProfit,
                            backgroundColor: "rgba(25, 135, 84, 0.75)"
                        },
                        {
                            label: "Fertilizer Cost",
                            data: fertilizerCost,
                            backgroundColor: "rgba(255, 193, 7, 0.75)"
                        },
                        {
                            label: "Crop Revenue",
                            data: revenue,
                            backgroundColor: "rgba(13, 110, 253, 0.75)"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: "index"
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => this.formatNumber(value)
                            }
                        }
                    }
                }
            });

            this.updateScenarioSummary(scenarios);
        }

        getScenarioData(data) {
            if (data.analysis && data.analysis.scenarios && data.analysis.scenarios.length > 0) {
                return data.analysis.scenarios;
            }
            return this.sampleData.analysis.scenarios;
        }

        updateScenarioSummary(scenarios) {
            if (!this.elements.scenarioSummaryBody) {
                return;
            }
            const active = scenarios.find((item) => item.name.toLowerCase().includes(this.state.activeScenario)) || scenarios[0];
            if (!active) {
                return;
            }

            this.elements.scenarioSummaryBody.innerHTML = "";
            const rows = [
                { label: "Net Profit", value: this.formatCurrency(active.netProfit) },
                { label: "Margin Shift", value: active.margin.toFixed(1) + "%" },
                { label: "Risk Level", value: this.toTitleCase(active.riskLevel || "medium") },
                { label: "Confidence", value: (active.confidence * 100).toFixed(0) + "%" },
                { label: "Time Horizon", value: active.horizon || "Seasonal" }
            ];

            rows.forEach((row) => {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${row.label}</td><td class="text-end">${row.value}</td>`;
                this.elements.scenarioSummaryBody.appendChild(tr);
            });
        }

        renderYieldResponseChart(data) {
            const ctx = document.getElementById("yieldResponseChart");
            if (!ctx || !window.Chart) {
                return;
            }

            if (this.charts.yieldResponse) {
                this.charts.yieldResponse.destroy();
            }

            const responseData = data.yieldResponse || this.sampleData.yieldResponse;
            const labels = responseData.rates;

            this.charts.yieldResponse = new window.Chart(ctx, {
                type: "line",
                data: {
                    labels,
                    datasets: [
                        {
                            label: "Nitrogen Response",
                            data: responseData.nitrogen,
                            borderColor: "#198754",
                            backgroundColor: "rgba(25, 135, 84, 0.1)",
                            fill: true,
                            tension: 0.35
                        },
                        {
                            label: "Phosphorus Response",
                            data: responseData.phosphorus,
                            borderColor: "#0d6efd",
                            backgroundColor: "rgba(13, 110, 253, 0.1)",
                            fill: true,
                            tension: 0.35
                        },
                        {
                            label: "Potassium Response",
                            data: responseData.potassium,
                            borderColor: "#ffc107",
                            backgroundColor: "rgba(255, 193, 7, 0.1)",
                            fill: true,
                            tension: 0.35
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        intersect: false,
                        mode: "index"
                    },
                    scales: {
                        y: {
                            title: { display: true, text: "Yield (bu/ac)" },
                            ticks: { stepSize: 10 }
                        },
                        x: {
                            title: { display: true, text: "Nutrient Rate (lbs/ac)" }
                        }
                    }
                }
            });

            if (this.elements.yieldResponseSummary) {
                this.elements.yieldResponseSummary.textContent = "Nitrogen rate of 175 lbs/ac is projected to maximize yield with minimal environmental penalty.";
            }
        }

        renderSensitivityChart(data) {
            const container = document.getElementById("sensitivityAnalysisChart");
            if (!container) {
                return;
            }

            const d3 = window.d3;
            if (!d3) {
                this.showPlaceholder(container, "D3.js is required to render sensitivity analysis.");
                return;
            }

            container.innerHTML = "";
            const chartData = this.getSensitivityData(data);
            if (chartData.length === 0) {
                this.showPlaceholder(container, "No sensitivity analysis data available.");
                return;
            }

            const width = container.clientWidth || container.offsetWidth || 500;
            const height = container.clientHeight || 280;
            const margin = { top: 20, right: 40, bottom: 30, left: 160 };

            const svg = d3.select(container)
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            const xScale = d3.scaleLinear()
                .domain([
                    d3.min(chartData, (d) => d.impact),
                    d3.max(chartData, (d) => d.impact)
                ])
                .range([margin.left, width - margin.right]);

            const yScale = d3.scaleBand()
                .domain(chartData.map((d) => d.parameter))
                .range([margin.top, height - margin.bottom])
                .padding(0.25);

            const zeroX = xScale(0);

            svg.append("line")
                .attr("x1", zeroX)
                .attr("x2", zeroX)
                .attr("y1", margin.top)
                .attr("y2", height - margin.bottom)
                .attr("stroke", "#adb5bd")
                .attr("stroke-dasharray", "4 3");

            svg.selectAll(".bar")
                .data(chartData)
                .enter()
                .append("rect")
                .attr("class", "bar")
                .attr("x", (d) => Math.min(xScale(d.impact), zeroX))
                .attr("y", (d) => yScale(d.parameter))
                .attr("width", (d) => Math.abs(xScale(d.impact) - zeroX))
                .attr("height", yScale.bandwidth())
                .attr("fill", (d) => d.impact >= 0 ? "#198754" : "#dc3545")
                .attr("rx", 4)
                .attr("ry", 4);

            svg.append("g")
                .attr("transform", `translate(0, ${height - margin.bottom})`)
                .call(d3.axisBottom(xScale).ticks(5).tickFormat((value) => value.toFixed(2)))
                .selectAll("text")
                .style("font-size", "12px");

            svg.append("g")
                .attr("transform", `translate(${margin.left - 10}, 0)`)
                .call(d3.axisLeft(yScale))
                .selectAll("text")
                .style("font-size", "12px")
                .call((selection) => selection.each((d, i, nodes) => {
                    const textElement = nodes[i];
                    const parameter = chartData[i];
                    textElement.setAttribute("data-detail", parameter.details ? JSON.stringify(parameter.details) : "{}");
                }));
        }

        getSensitivityData(data) {
            if (data.analysis && data.analysis.sensitivity && data.analysis.sensitivity.length > 0) {
                return data.analysis.sensitivity;
            }
            return this.sampleData.analysis.sensitivity;
        }

        renderEnvironmentalMap(data) {
            const container = document.getElementById("environmentalImpactMap");
            if (!container) {
                return;
            }
            const d3 = window.d3;
            if (!d3) {
                this.showPlaceholder(container, "D3.js is required to render environmental impact map.");
                return;
            }

            container.innerHTML = "";
            const impactData = data.environmentalImpact || this.sampleData.environmentalImpact;
            if (!impactData || impactData.length === 0) {
                this.showPlaceholder(container, "No environmental impact data available.");
                return;
            }

            const width = container.clientWidth || container.offsetWidth || 500;
            const height = container.clientHeight || 320;
            const padding = 20;

            const svg = d3.select(container)
                .append("svg")
                .attr("width", width)
                .attr("height", height);

            const xScale = d3.scaleLinear()
                .domain(d3.extent(impactData, (d) => d.coordinates.lng))
                .range([padding, width - padding]);

            const yScale = d3.scaleLinear()
                .domain(d3.extent(impactData, (d) => d.coordinates.lat))
                .range([height - padding, padding]);

            const colorScale = d3.scaleLinear()
                .domain([0, 0.5, 1])
                .range(["#198754", "#ffc107", "#dc3545"]);

            svg.selectAll(".impact-circle")
                .data(impactData)
                .enter()
                .append("circle")
                .attr("class", "impact-circle")
                .attr("cx", (d) => xScale(d.coordinates.lng))
                .attr("cy", (d) => yScale(d.coordinates.lat))
                .attr("r", (d) => 18 + (d.impactScore * 12))
                .attr("fill", (d) => colorScale(d.impactScore))
                .attr("fill-opacity", 0.82)
                .attr("stroke", "rgba(33, 37, 41, 0.25)")
                .attr("stroke-width", 1.2);

            svg.selectAll(".impact-label")
                .data(impactData)
                .enter()
                .append("text")
                .attr("class", "impact-label")
                .attr("x", (d) => xScale(d.coordinates.lng))
                .attr("y", (d) => yScale(d.coordinates.lat) - 24)
                .attr("text-anchor", "middle")
                .attr("fill", "#212529")
                .attr("font-size", "0.75rem")
                .attr("font-weight", "600")
                .text((d) => d.field);

            svg.selectAll(".impact-detail")
                .data(impactData)
                .enter()
                .append("text")
                .attr("class", "impact-detail")
                .attr("x", (d) => xScale(d.coordinates.lng))
                .attr("y", (d) => yScale(d.coordinates.lat) + 34)
                .attr("text-anchor", "middle")
                .attr("fill", "#495057")
                .attr("font-size", "0.7rem")
                .text((d) => `Runoff risk: ${d.runoffRisk}`);
        }

        populateTradeoffTable(data) {
            if (!this.elements.tradeoffTableBody) {
                return;
            }

            const scenarios = (data && data.tradeoffs) ? data.tradeoffs : this.sampleData.tradeoffs;
            if (!scenarios || scenarios.length === 0) {
                this.elements.tradeoffTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No trade-off analysis available.</td></tr>`;
                return;
            }

            this.elements.tradeoffTableBody.innerHTML = "";
            scenarios.forEach((item) => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.scenario}</td>
                    <td>${item.adjustment}</td>
                    <td class="text-end">${item.expectedImpact}</td>
                    <td class="text-end">${item.confidence}</td>
                    <td class="text-end">${item.horizon}</td>
                `;
                if (item.metric === this.state.activeMetric) {
                    row.classList.add("table-success");
                }
                this.elements.tradeoffTableBody.appendChild(row);
            });
        }

        populateSustainability(items) {
            if (!this.elements.sustainabilityList) {
                return;
            }
            this.elements.sustainabilityList.innerHTML = "";
            items.forEach((item) => {
                const li = document.createElement("li");
                li.className = "mb-3";
                li.innerHTML = `<div class='d-flex justify-content-between align-items-center'><div><strong>${item.label}</strong><div class='text-muted small'>${item.detail}</div></div><span class='badge bg-success-subtle text-success'>${item.value}</span></div>`;
                this.elements.sustainabilityList.appendChild(li);
            });
        }

        populatePriceRows(prices) {
            if (!this.elements.priceRows) {
                return;
            }
            this.elements.priceRows.innerHTML = "";
            prices.forEach((price) => {
                const row = document.createElement("div");
                row.className = "price-row";
                const changeClass = price.change >= 0 ? "text-danger" : "text-success";
                const changeIcon = price.change >= 0 ? "fa-arrow-up" : "fa-arrow-down";
                const changeValue = Math.abs(price.change);
                row.innerHTML = `
                    <div class='d-flex justify-content-between align-items-center'>
                        <div>
                            <h6 class='mb-0'>${price.product}</h6>
                            <small class='text-muted'>${price.region}</small>
                        </div>
                        <div class='text-end'>
                            <div class='price-indicator'>${this.formatCurrency(price.price)} <small class='text-muted'>${price.unit}</small></div>
                            <div class='${changeClass} small'><i class='fas ${changeIcon}'></i> ${changeValue} (${price.change >= 0 ? "+" : "-"} weekly)</div>
                        </div>
                    </div>
                `;
                this.elements.priceRows.appendChild(row);
            });
        }

        populateAlerts(alerts) {
            if (!this.elements.alertsContainer) {
                return;
            }
            this.elements.alertsContainer.innerHTML = "";
            if (!alerts || alerts.length === 0) {
                this.elements.alertsContainer.innerHTML = "<div class='alert alert-secondary'>No active alerts.</div>";
                return;
            }

            alerts.forEach((alert) => {
                const card = document.createElement("div");
                card.className = "alert-card";
                const isHigh = alert.severity === "high";
                const severityClass = isHigh ? "bg-danger" : "bg-warning";
                const severityLabel = isHigh ? "High Priority" : "Medium Priority";
                card.innerHTML = `
                    <div class='d-flex justify-content-between align-items-center mb-1'>
                        <h6 class='mb-0'>${alert.title}</h6>
                        <span class='badge ${severityClass}'>${severityLabel}</span>
                    </div>
                    <p class='mb-2 text-muted'>${alert.detail}</p>
                    <small class='text-secondary'>${alert.timestamp}</small>
                `;
                this.elements.alertsContainer.appendChild(card);
            });
        }

        populateActivityLog(entries) {
            if (!this.elements.activityLog) {
                return;
            }
            this.elements.activityLog.innerHTML = "";
            entries.forEach((entry) => {
                const item = document.createElement("div");
                item.className = "list-group-item list-group-item-action d-flex justify-content-between align-items-start";
                item.innerHTML = `<div class='ms-2 me-auto'><div class='fw-bold'>${entry.title}</div>${entry.detail}</div><span class='badge bg-light text-muted'>${entry.timestamp}</span>`;
                this.elements.activityLog.appendChild(item);
            });
        }

        handleScenarioSelection(scenario) {
            if (!scenario || scenario === this.state.activeScenario) {
                return;
            }
            this.state.activeScenario = scenario;
            this.updateActiveChip(this.elements.scenarioControlPanel, scenario);
            if (this.state.data) {
                this.renderScenarioComparison(this.state.data);
            }
        }

        handleMetricSelection(metric) {
            if (!metric || metric === this.state.activeMetric) {
                return;
            }
            this.state.activeMetric = metric;
            this.updateActiveChip(this.elements.tradeoffControlPanel, metric);
            if (this.state.data) {
                this.populateTradeoffTable(this.state.data);
            }
        }

        updateActiveChip(container, activeKey) {
            if (!container) {
                return;
            }
            const chips = container.querySelectorAll(".analysis-chip");
            chips.forEach((chip) => {
                if (chip.dataset.metric) {
                    chip.classList.toggle("active", chip.dataset.metric === activeKey);
                } else {
                    chip.classList.toggle("active", chip.dataset.scenario === activeKey);
                }
            });
        }

        showPlaceholder(container, message) {
            container.innerHTML = `<div class="d3-placeholder">${message}</div>`;
        }

        setLastUpdated() {
            this.state.lastUpdated = new Date();
            if (this.elements.lastUpdatedLabel) {
                this.elements.lastUpdatedLabel.textContent = "Updated " + this.state.lastUpdated.toLocaleTimeString();
            }
            this.setPriceRefreshLabel("Updated " + this.state.lastUpdated.toLocaleTimeString());
        }

        setPriceRefreshLabel(text) {
            if (this.elements.priceRefreshLabel) {
                this.elements.priceRefreshLabel.textContent = text;
            }
        }

        markRefreshSuccess() {
            this.setPriceRefreshLabel("Live data refreshed");
        }

        formatCurrency(value) {
            const formatter = new Intl.NumberFormat("en-US", {
                style: "currency",
                currency: "USD",
                maximumFractionDigits: 0
            });
            return formatter.format(value);
        }

        formatNumber(value) {
            const formatter = new Intl.NumberFormat("en-US", {
                maximumFractionDigits: 0
            });
            return formatter.format(value);
        }

        toTitleCase(value) {
            if (!value) {
                return "";
            }
            const text = String(value);
            return text.charAt(0).toUpperCase() + text.slice(1);
        }

        buildSampleData() {
            return {
                roi: { value: 18.4, trend: 2.6 },
                cost: { value: 48250, trend: -3.4 },
                yield: { value: 196, trend: 3.1 },
                impact: { value: 8.6, trend: 0.8 },
                optimization: {
                    status: "Optimal",
                    summary: [
                        { label: "Recommended Nitrogen Rate", value: "175 lbs/ac", detail: "Split application (V4 + V10)" },
                        { label: "Phosphorus Strategy", value: "Maintenance (35 lbs/ac)", detail: "Build-up deferred to next season" },
                        { label: "Potassium Program", value: "Supplemental (40 lbs/ac)", detail: "Targeted to low-testing zones" },
                        { label: "Estimated Total Cost", value: "$48,250", detail: "Blended fertilizer pricing active" },
                        { label: "Projected Net Profit", value: "$139,200", detail: "Based on $5.10/bu corn" }
                    ],
                    recommendations: [
                        { action: "Schedule sidedress nitrogen for next moisture window", priority: "High" },
                        { action: "Monitor DAP pricing - smaller lots trending downward", priority: "Medium" },
                        { action: "Validate yield monitor calibration before harvest", priority: "High" }
                    ]
                },
                charts: {
                    performance: [
                        { month: "Apr", roi: 12, cost: 51000, impact: 7.4 },
                        { month: "May", roi: 14, cost: 50500, impact: 7.9 },
                        { month: "Jun", roi: 15.6, cost: 50000, impact: 8.1 },
                        { month: "Jul", roi: 17.2, cost: 49500, impact: 8.3 },
                        { month: "Aug", roi: 18.4, cost: 48250, impact: 8.6 }
                    ],
                    costBreakdown: [
                        { nutrient: "Nitrogen", value: 58 },
                        { nutrient: "Phosphorus", value: 24 },
                        { nutrient: "Potassium", value: 14 },
                        { nutrient: "Sulfur", value: 4 }
                    ],
                    yieldContribution: [
                        { program: "N Timing Optimization", value: 38 },
                        { program: "Soil Health Practices", value: 22 },
                        { program: "Micro-Nutrient Support", value: 16 },
                        { program: "In-Season Monitoring", value: 24 }
                    ],
                    sustainability: [
                        { label: "Nutrient Efficiency", value: "92%", detail: "On track with NRCS guidelines" },
                        { label: "Runoff Risk", value: "Low", detail: "Buffer zones & cover crop adoption" },
                        { label: "Soil Health Score", value: "8.3 / 10", detail: "Maintaining organic matter gains" },
                        { label: "Carbon Intensity", value: "-0.8%", detail: "Year-over-year reduction" }
                    ]
                },
                prices: [
                    { product: "Urea (46-0-0)", region: "Midwest", price: 468, change: -8, unit: "$/ton" },
                    { product: "DAP (18-46-0)", region: "Midwest", price: 612, change: -4, unit: "$/ton" },
                    { product: "Potash (0-0-60)", region: "Midwest", price: 415, change: 6, unit: "$/ton" },
                    { product: "AMS (21-0-0-24S)", region: "Midwest", price: 365, change: 0, unit: "$/ton" }
                ],
                alerts: [
                    {
                        title: "Nitrogen sidedress window approaching",
                        detail: "Forecast shows favorable conditions in 3 days. Confirm equipment readiness.",
                        severity: "high",
                        timestamp: "Today, 08:15"
                    },
                    {
                        title: "DAP inventory surplus reported",
                        detail: "Regional dealers signal potential price drop within 10-14 days.",
                        severity: "medium",
                        timestamp: "Yesterday, 17:40"
                    },
                    {
                        title: "Monitor field 12B for K uptake",
                        detail: "Tissue tests indicated marginal potassium levels last season.",
                        severity: "medium",
                        timestamp: "Yesterday, 09:05"
                    }
                ],
                activityLog: [
                    {
                        title: "Strategy re-optimized with latest soil tests",
                        detail: "Adjusted phosphorus maintenance rate and recalibrated ROI forecast.",
                        timestamp: "Aug 24, 07:20"
                    },
                    {
                        title: "Imported fertilizer price feed",
                        detail: "Automated update from USDA NASS and dealer network.",
                        timestamp: "Aug 23, 18:05"
                    },
                    {
                        title: "Environmental compliance check passed",
                        detail: "Runoff risk assessment aligned with state watershed guidelines.",
                        timestamp: "Aug 22, 14:12"
                    }
                ],
                yieldResponse: {
                    rates: [90, 120, 150, 175, 190, 210],
                    nitrogen: [165, 178, 186, 196, 198, 197],
                    phosphorus: [152, 165, 178, 189, 191, 190],
                    potassium: [148, 160, 174, 183, 186, 185]
                },
                analysis: {
                    scenarios: [
                        {
                            name: "Baseline",
                            keyAdjustment: "Current pricing",
                            netProfit: 139200,
                            fertilizerCost: 48250,
                            revenue: 187450,
                            margin: 22.4,
                            riskLevel: "medium",
                            confidence: 0.88,
                            horizon: "Seasonal"
                        },
                        {
                            name: "Optimistic",
                            keyAdjustment: "Prices down 8%",
                            netProfit: 152900,
                            fertilizerCost: 44680,
                            revenue: 189600,
                            margin: 24.1,
                            riskLevel: "low",
                            confidence: 0.82,
                            horizon: "Seasonal"
                        },
                        {
                            name: "Pessimistic",
                            keyAdjustment: "Prices up 12%",
                            netProfit: 118400,
                            fertilizerCost: 52960,
                            revenue: 183200,
                            margin: 18.7,
                            riskLevel: "high",
                            confidence: 0.76,
                            horizon: "Seasonal"
                        },
                        {
                            name: "Volatile",
                            keyAdjustment: "High price swings",
                            netProfit: 129100,
                            fertilizerCost: 50300,
                            revenue: 186400,
                            margin: 20.5,
                            riskLevel: "medium",
                            confidence: 0.68,
                            horizon: "Monthly review"
                        },
                        {
                            name: "Custom Hedge Strategy",
                            keyAdjustment: "Lock 60% of nitrogen",
                            netProfit: 136800,
                            fertilizerCost: 47200,
                            revenue: 186000,
                            margin: 21.7,
                            riskLevel: "medium",
                            confidence: 0.74,
                            horizon: "Bi-seasonal"
                        }
                    ],
                    sensitivity: [
                        { parameter: "Urea Price Change", impact: -0.42, details: { criticalThreshold: 0.18, sensitivityScore: 0.76 } },
                        { parameter: "Corn Market Price", impact: 0.58, details: { criticalThreshold: 0.12, sensitivityScore: 0.84 } },
                        { parameter: "Yield Variability", impact: 0.36, details: { criticalThreshold: 0.15, sensitivityScore: 0.63 } },
                        { parameter: "Fuel Cost Trend", impact: -0.18, details: { criticalThreshold: 0.22, sensitivityScore: 0.51 } },
                        { parameter: "Nitrogen Rate Adjustment", impact: 0.27, details: { criticalThreshold: 0.1, sensitivityScore: 0.58 } }
                    ],
                    baseline: {
                        net_profit: 139200,
                        total_fertilizer_cost: 48250,
                        total_crop_revenue: 187450,
                        profit_margin_percent: 22.4
                    }
                },
                tradeoffs: [
                    {
                        scenario: "Baseline Strategy",
                        adjustment: "Maintain split nitrogen application",
                        expectedImpact: "+2.5% net margin",
                        confidence: "88%",
                        horizon: "Seasonal",
                        metric: "profit"
                    },
                    {
                        scenario: "Market Opportunity",
                        adjustment: "Advance purchase 40% nitrogen",
                        expectedImpact: "-6.2% cost per acre",
                        confidence: "72%",
                        horizon: "45 days",
                        metric: "cost"
                    },
                    {
                        scenario: "Yield Optimization",
                        adjustment: "Boost late-season nitrogen in responsive zones",
                        expectedImpact: "+6 bu/ac yield gain",
                        confidence: "64%",
                        horizon: "In-season",
                        metric: "yield"
                    },
                    {
                        scenario: "Environmental Guardrails",
                        adjustment: "Expand buffer strip monitoring",
                        expectedImpact: "-12% runoff risk",
                        confidence: "79%",
                        horizon: "Annual",
                        metric: "impact"
                    },
                    {
                        scenario: "Risk Hedging",
                        adjustment: "Use staggered purchasing blocks",
                        expectedImpact: "-18% price exposure",
                        confidence: "67%",
                        horizon: "Seasonal",
                        metric: "risk"
                    }
                ],
                environmentalImpact: [
                    {
                        field: "North 40",
                        impactScore: 0.38,
                        runoffRisk: "Low",
                        coordinates: { lat: 41.72, lng: -93.57 }
                    },
                    {
                        field: "East Pivot",
                        impactScore: 0.62,
                        runoffRisk: "Moderate",
                        coordinates: { lat: 41.69, lng: -93.51 }
                    },
                    {
                        field: "South Ridge",
                        impactScore: 0.81,
                        runoffRisk: "Elevated",
                        coordinates: { lat: 41.65, lng: -93.55 }
                    },
                    {
                        field: "West Basin",
                        impactScore: 0.47,
                        runoffRisk: "Low",
                        coordinates: { lat: 41.67, lng: -93.6 }
                    }
                ]
            };
        }
    }

    window.FertilizerStrategyVisualization = FertilizerStrategyVisualization;
    new FertilizerStrategyVisualization();
})();
