"""
Tests for Equipment Optimization and Investment Planning Service

Comprehensive test suite for equipment optimization, investment analysis,
and planning functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, date

from services.drought_management.src.services.equipment_optimization_service import EquipmentOptimizationService
from services.drought_management.src.models.equipment_optimization_models import (
    EquipmentOptimizationRequest,
    EquipmentOptimizationResponse,
    InvestmentAnalysis,
    EquipmentOptimizationPlan,
    OptimizationObjective,
    InvestmentType,
    InvestmentPriority,
    FinancingOption,
    EquipmentCategory,
    InvestmentScenario,
    EquipmentInvestmentOption
)


class TestEquipmentOptimizationService:
    """Test suite for Equipment Optimization Service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return EquipmentOptimizationService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample optimization request."""
        return EquipmentOptimizationRequest(
            scenario_id=str(uuid4()),
            field_id=str(uuid4()),
            optimization_objectives=[
                OptimizationObjective(
                    objective_type="water_conservation",
                    target_value=25.0,
                    weight=0.4,
                    priority="high"
                ),
                OptimizationObjective(
                    objective_type="efficiency_improvement",
                    target_value=20.0,
                    weight=0.3,
                    priority="medium"
                ),
                OptimizationObjective(
                    objective_type="capacity_expansion",
                    target_value=30.0,
                    weight=0.3,
                    priority="medium"
                )
            ],
            budget_constraints={
                "max_investment": 500000,
                "annual_budget": 100000,
                "financing_preference": "bank_loan"
            },
            field_characteristics={
                "acres": 160,
                "soil_type": "clay_loam",
                "crop_type": "corn",
                "irrigation_type": "center_pivot",
                "current_efficiency": 0.75
            },
            investment_timeline_months=12,
            risk_tolerance="medium"
        )
    
    @pytest.fixture
    def sample_investment_option(self):
        """Create sample investment option."""
        return EquipmentInvestmentOption(
            option_id=str(uuid4()),
            scenario_id=str(uuid4()),
            equipment_category="irrigation",
            equipment_name="Variable Rate Irrigation System",
            manufacturer="Lindsay Corporation",
            model="Zimmatic VRI",
            investment_type=InvestmentType.PURCHASE,
            investment_cost=Decimal("200000"),
            financing_option=FinancingOption(
                financing_type="bank_loan",
                interest_rate=5.5,
                loan_term_years=7,
                down_payment_percent=20.0
            ),
            down_payment=Decimal("40000"),
            monthly_payment=Decimal("1904.76"),
            loan_term_months=84,
            interest_rate=5.5,
            capacity_specifications={
                "acres_covered": 160,
                "flow_rate_gpm": 1200,
                "pressure_psi": 60
            },
            efficiency_ratings={
                "water_efficiency": 0.90,
                "energy_efficiency": 0.85,
                "labor_efficiency": 0.90
            },
            water_conservation_features=[
                "Precision application",
                "Zone-based control",
                "Real-time monitoring"
            ],
            drought_resilience_features=[
                "Adaptive scheduling",
                "Water stress detection",
                "Efficient distribution"
            ],
            annual_operating_cost=Decimal("10000"),
            annual_maintenance_cost=Decimal("6000"),
            expected_lifespan_years=15,
            residual_value=Decimal("60000"),
            water_savings_percent=25.0,
            efficiency_improvement_percent=20.0,
            capacity_increase_percent=15.0,
            cost_savings_per_year=Decimal("16000"),
            implementation_timeline_days=30,
            priority_level=InvestmentPriority.HIGH
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.equipment_database is not None
        assert service.financing_options is not None
        assert service.performance_benchmarks is not None
        assert service.risk_criteria is not None
    
    @pytest.mark.asyncio
    async def test_optimize_equipment_investment_success(self, service, sample_request):
        """Test successful equipment optimization."""
        await service.initialize()
        
        response = await service.optimize_equipment_investment(sample_request)
        
        assert response is not None
        assert response.scenario_id == sample_request.scenario_id
        assert response.optimization_plan is not None
        assert response.investment_scenarios is not None
        assert response.overall_metrics is not None
        assert response.risk_assessment is not None
        assert response.recommendations is not None
        assert len(response.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_generate_investment_scenarios(self, service, sample_request):
        """Test investment scenario generation."""
        await service.initialize()
        
        scenarios = await service._generate_investment_scenarios(sample_request)
        
        assert len(scenarios) == 4  # Conservative, Balanced, Aggressive, Phased
        assert all(isinstance(scenario, InvestmentScenario) for scenario in scenarios)
        
        # Check scenario types
        scenario_names = [scenario.scenario_name for scenario in scenarios]
        assert "Conservative Investment" in scenario_names
        assert "Balanced Investment" in scenario_names
        assert "Aggressive Investment" in scenario_names
        assert "Phased Investment" in scenario_names
    
    @pytest.mark.asyncio
    async def test_create_conservative_scenario(self, service, sample_request):
        """Test conservative scenario creation."""
        await service.initialize()
        
        scenario = await service._create_conservative_scenario(sample_request)
        
        assert scenario.scenario_name == "Conservative Investment"
        assert scenario.risk_level == "low"
        assert scenario.expected_return_percent == 8.0
        assert len(scenario.investment_options) > 0
        assert scenario.total_investment_cost > 0
    
    @pytest.mark.asyncio
    async def test_create_balanced_scenario(self, service, sample_request):
        """Test balanced scenario creation."""
        await service.initialize()
        
        scenario = await service._create_balanced_scenario(sample_request)
        
        assert scenario.scenario_name == "Balanced Investment"
        assert scenario.risk_level == "medium"
        assert scenario.expected_return_percent == 12.0
        assert len(scenario.investment_options) > 0
        assert scenario.total_investment_cost > 0
    
    @pytest.mark.asyncio
    async def test_create_aggressive_scenario(self, service, sample_request):
        """Test aggressive scenario creation."""
        await service.initialize()
        
        scenario = await service._create_aggressive_scenario(sample_request)
        
        assert scenario.scenario_name == "Aggressive Investment"
        assert scenario.risk_level == "high"
        assert scenario.expected_return_percent == 18.0
        assert len(scenario.investment_options) > 0
        assert scenario.total_investment_cost > 0
    
    @pytest.mark.asyncio
    async def test_create_phased_scenario(self, service, sample_request):
        """Test phased scenario creation."""
        await service.initialize()
        
        scenario = await service._create_phased_scenario(sample_request)
        
        assert scenario.scenario_name == "Phased Investment"
        assert scenario.risk_level == "low"
        assert scenario.expected_return_percent == 10.0
        assert len(scenario.investment_options) > 0
        assert scenario.total_investment_cost > 0
    
    @pytest.mark.asyncio
    async def test_create_irrigation_investment_option(self, service, sample_request):
        """Test irrigation investment option creation."""
        await service.initialize()
        
        # Test conservative option
        option = await service._create_irrigation_investment_option(sample_request, "conservative")
        
        assert option.equipment_category == "irrigation"
        assert option.equipment_name == "Center Pivot Irrigation System"
        assert option.manufacturer == "Valley Irrigation"
        assert option.investment_cost == Decimal("150000")
        assert option.water_savings_percent == 15.0
        assert option.efficiency_ratings["water_efficiency"] == 0.85
        
        # Test aggressive option
        option = await service._create_irrigation_investment_option(sample_request, "aggressive")
        
        assert option.equipment_name == "Precision Irrigation System"
        assert option.manufacturer == "Netafim"
        assert option.investment_cost == Decimal("300000")
        assert option.water_savings_percent == 35.0
        assert option.efficiency_ratings["water_efficiency"] == 0.95
    
    @pytest.mark.asyncio
    async def test_create_tillage_investment_option(self, service, sample_request):
        """Test tillage investment option creation."""
        await service.initialize()
        
        # Test balanced option
        option = await service._create_tillage_investment_option(sample_request, "balanced")
        
        assert option.equipment_category == "tillage"
        assert option.equipment_name == "Strip Tillage System"
        assert option.manufacturer == "Case IH"
        assert option.investment_cost == Decimal("120000")
        assert option.efficiency_improvement_percent == 30.0
        assert option.capacity_specifications["acres_per_hour"] == 10.0
    
    @pytest.mark.asyncio
    async def test_create_capacity_investment_option(self, service, sample_request):
        """Test capacity investment option creation."""
        await service.initialize()
        
        # Test balanced option
        option = await service._create_capacity_investment_option(sample_request, "balanced")
        
        assert option.equipment_category == "storage"
        assert option.equipment_name == "Grain Storage Bin"
        assert option.manufacturer == "Grain Systems"
        assert option.investment_cost == Decimal("100000")
        assert option.capacity_increase_percent == 50.0
        assert option.capacity_specifications["storage_capacity_bushels"] == 50000
    
    @pytest.mark.asyncio
    async def test_analyze_investment_scenario(self, service, sample_request):
        """Test investment scenario analysis."""
        await service.initialize()
        
        # Create a sample scenario
        scenario = await service._create_conservative_scenario(sample_request)
        
        # Analyze the scenario
        analysis = await service._analyze_investment_scenario(scenario, sample_request)
        
        assert analysis.scenario_id == scenario.scenario_id
        assert analysis.total_investment_cost > 0
        assert analysis.total_annual_savings > 0
        assert analysis.net_present_value is not None
        assert analysis.internal_rate_of_return >= 0
        assert analysis.payback_period_years > 0
        assert analysis.return_on_investment >= 0
        assert 0 <= analysis.risk_score <= 1
        assert 0 <= analysis.financial_feasibility_score <= 1
    
    def test_calculate_npv(self, service):
        """Test NPV calculation."""
        initial_investment = Decimal("100000")
        annual_cash_flow = Decimal("15000")
        discount_rate = 0.08
        years = 10
        
        npv = service._calculate_npv(initial_investment, annual_cash_flow, discount_rate, years)
        
        assert npv is not None
        assert isinstance(npv, Decimal)
        # NPV should be negative for this example (investment > returns)
        assert npv < 0
    
    def test_calculate_irr(self, service):
        """Test IRR calculation."""
        initial_investment = Decimal("100000")
        annual_cash_flow = Decimal("20000")
        years = 10
        
        irr = service._calculate_irr(initial_investment, annual_cash_flow, years)
        
        assert irr >= 0
        assert irr <= 50.0  # Capped at 50%
        assert isinstance(irr, float)
    
    def test_calculate_risk_score(self, service):
        """Test risk score calculation."""
        # Create a sample scenario
        scenario = InvestmentScenario(
            scenario_id=str(uuid4()),
            scenario_name="Test Scenario",
            description="Test scenario",
            investment_options=[],
            total_investment_cost=Decimal("150000"),
            risk_level="medium",
            expected_return_percent=12.0
        )
        
        risk_score = service._calculate_risk_score(scenario)
        
        assert 0 <= risk_score <= 1
        assert isinstance(risk_score, float)
    
    def test_calculate_feasibility_score(self, service):
        """Test feasibility score calculation."""
        npv = Decimal("50000")
        irr = 15.0
        payback_period = 3.5
        
        feasibility_score = service._calculate_feasibility_score(npv, irr, payback_period)
        
        assert 0 <= feasibility_score <= 1
        assert isinstance(feasibility_score, float)
    
    def test_assess_implementation_complexity(self, service):
        """Test implementation complexity assessment."""
        # Low complexity scenario
        low_complexity_scenario = InvestmentScenario(
            scenario_id=str(uuid4()),
            scenario_name="Low Complexity",
            description="Low complexity scenario",
            investment_options=[MagicMock()],
            total_investment_cost=Decimal("50000"),
            risk_level="low",
            expected_return_percent=8.0
        )
        
        complexity = service._assess_implementation_complexity(low_complexity_scenario)
        assert complexity == "low"
        
        # High complexity scenario
        high_complexity_scenario = InvestmentScenario(
            scenario_id=str(uuid4()),
            scenario_name="High Complexity",
            description="High complexity scenario",
            investment_options=[MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            total_investment_cost=Decimal("400000"),
            risk_level="high",
            expected_return_percent=18.0
        )
        
        complexity = service._assess_implementation_complexity(high_complexity_scenario)
        assert complexity == "high"
    
    def test_assess_market_impact(self, service):
        """Test market impact assessment."""
        # Low impact scenario
        low_impact_scenario = InvestmentScenario(
            scenario_id=str(uuid4()),
            scenario_name="Low Impact",
            description="Low impact scenario",
            investment_options=[],
            total_investment_cost=Decimal("50000"),
            risk_level="low",
            expected_return_percent=8.0
        )
        
        impact = service._assess_market_impact(low_impact_scenario)
        assert impact == "low"
        
        # High impact scenario
        high_impact_scenario = InvestmentScenario(
            scenario_id=str(uuid4()),
            scenario_name="High Impact",
            description="High impact scenario",
            investment_options=[],
            total_investment_cost=Decimal("300000"),
            risk_level="high",
            expected_return_percent=18.0
        )
        
        impact = service._assess_market_impact(high_impact_scenario)
        assert impact == "high"
    
    @pytest.mark.asyncio
    async def test_rank_investment_scenarios(self, service, sample_request):
        """Test investment scenario ranking."""
        await service.initialize()
        
        # Create sample scenarios
        scenarios = await service._generate_investment_scenarios(sample_request)
        
        # Analyze scenarios
        analyzed_scenarios = []
        for scenario in scenarios:
            analysis = await service._analyze_investment_scenario(scenario, sample_request)
            analyzed_scenarios.append(analysis)
        
        # Rank scenarios
        ranked_scenarios = await service._rank_investment_scenarios(
            analyzed_scenarios, sample_request.optimization_objectives
        )
        
        assert len(ranked_scenarios) == len(analyzed_scenarios)
        assert all(isinstance(scenario, InvestmentAnalysis) for scenario in ranked_scenarios)
        # Should be sorted by score (highest first)
        assert ranked_scenarios[0].scenario_id is not None
    
    @pytest.mark.asyncio
    async def test_generate_optimization_plan(self, service, sample_request):
        """Test optimization plan generation."""
        await service.initialize()
        
        # Create sample scenarios
        scenarios = await service._generate_investment_scenarios(sample_request)
        
        # Analyze scenarios
        analyzed_scenarios = []
        for scenario in scenarios:
            analysis = await service._analyze_investment_scenario(scenario, sample_request)
            analyzed_scenarios.append(analysis)
        
        # Rank scenarios
        ranked_scenarios = await service._rank_investment_scenarios(
            analyzed_scenarios, sample_request.optimization_objectives
        )
        
        # Generate optimization plan
        plan = await service._generate_optimization_plan(ranked_scenarios, sample_request)
        
        assert plan.scenario_id == sample_request.scenario_id
        assert plan.plan_name is not None
        assert plan.description is not None
        assert len(plan.optimization_objectives) > 0
        assert plan.implementation_timeline_months > 0
        assert plan.total_investment_required > 0
        assert plan.total_annual_savings > 0
        assert plan.net_present_value is not None
        assert plan.internal_rate_of_return >= 0
        assert plan.payback_period_years > 0
        assert plan.return_on_investment >= 0
        assert 0 <= plan.overall_risk_score <= 1
        assert len(plan.risk_factors) >= 0
        assert len(plan.mitigation_strategies) >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_overall_metrics(self, service, sample_request):
        """Test overall metrics calculation."""
        await service.initialize()
        
        # Create sample scenarios
        scenarios = await service._generate_investment_scenarios(sample_request)
        
        # Analyze scenarios
        analyzed_scenarios = []
        for scenario in scenarios:
            analysis = await service._analyze_investment_scenario(scenario, sample_request)
            analyzed_scenarios.append(analysis)
        
        # Calculate overall metrics
        metrics = await service._calculate_overall_metrics(analyzed_scenarios)
        
        assert "average_investment_cost" in metrics
        assert "average_annual_savings" in metrics
        assert "average_npv" in metrics
        assert "average_irr" in metrics
        assert "average_payback_period" in metrics
        assert "average_roi" in metrics
        assert "average_risk_score" in metrics
        assert "scenario_count" in metrics
        assert metrics["scenario_count"] == len(analyzed_scenarios)
    
    @pytest.mark.asyncio
    async def test_assess_investment_risks(self, service, sample_request):
        """Test investment risk assessment."""
        await service.initialize()
        
        # Create sample scenarios
        scenarios = await service._generate_investment_scenarios(sample_request)
        
        # Analyze scenarios
        analyzed_scenarios = []
        for scenario in scenarios:
            analysis = await service._analyze_investment_scenario(scenario, sample_request)
            analyzed_scenarios.append(analysis)
        
        # Assess risks
        risk_assessment = await service._assess_investment_risks(analyzed_scenarios, sample_request)
        
        assert risk_assessment.overall_risk_level in ["low", "medium", "high"]
        assert 0 <= risk_assessment.risk_score <= 1
        assert isinstance(risk_assessment.key_risk_factors, list)
        assert isinstance(risk_assessment.mitigation_strategies, list)
        assert isinstance(risk_assessment.risk_monitoring_recommendations, list)
        assert len(risk_assessment.risk_monitoring_recommendations) > 0
    
    def test_generate_recommendations(self, service, sample_request):
        """Test recommendation generation."""
        # Create sample analysis
        analysis = InvestmentAnalysis(
            analysis_id=str(uuid4()),
            scenario_id=str(uuid4()),
            total_investment_cost=Decimal("200000"),
            total_annual_savings=Decimal("30000"),
            net_present_value=Decimal("50000"),
            internal_rate_of_return=15.0,
            payback_period_years=6.7,
            return_on_investment=15.0,
            water_savings_percent=25.0,
            efficiency_improvement_percent=20.0,
            capacity_increase_percent=30.0,
            risk_score=0.3,
            financial_feasibility_score=0.8,
            implementation_complexity="medium",
            market_conditions_impact="medium"
        )
        
        recommendations = service._generate_recommendations([analysis])
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)
        assert any("ROI" in rec for rec in recommendations)
        assert any("payback" in rec.lower() for rec in recommendations)
        assert any("risk" in rec.lower() for rec in recommendations)
    
    def test_identify_risk_factors(self, service):
        """Test risk factor identification."""
        # High risk analysis
        high_risk_analysis = InvestmentAnalysis(
            analysis_id=str(uuid4()),
            scenario_id=str(uuid4()),
            total_investment_cost=Decimal("500000"),
            total_annual_savings=Decimal("20000"),
            net_present_value=Decimal("-10000"),
            internal_rate_of_return=3.0,
            payback_period_years=25.0,
            return_on_investment=4.0,
            water_savings_percent=10.0,
            efficiency_improvement_percent=5.0,
            capacity_increase_percent=10.0,
            risk_score=0.8,
            financial_feasibility_score=0.2,
            implementation_complexity="high",
            market_conditions_impact="high"
        )
        
        risk_factors = service._identify_risk_factors(high_risk_analysis)
        
        assert len(risk_factors) > 0
        assert all(isinstance(factor, str) for factor in risk_factors)
        assert any("risk" in factor.lower() for factor in risk_factors)
    
    def test_generate_mitigation_strategies(self, service):
        """Test mitigation strategy generation."""
        # High risk analysis
        high_risk_analysis = InvestmentAnalysis(
            analysis_id=str(uuid4()),
            scenario_id=str(uuid4()),
            total_investment_cost=Decimal("500000"),
            total_annual_savings=Decimal("20000"),
            net_present_value=Decimal("-10000"),
            internal_rate_of_return=3.0,
            payback_period_years=25.0,
            return_on_investment=4.0,
            water_savings_percent=10.0,
            efficiency_improvement_percent=5.0,
            capacity_increase_percent=10.0,
            risk_score=0.8,
            financial_feasibility_score=0.2,
            implementation_complexity="high",
            market_conditions_impact="high"
        )
        
        strategies = service._generate_mitigation_strategies(high_risk_analysis)
        
        assert len(strategies) > 0
        assert all(isinstance(strategy, str) for strategy in strategies)
        assert any("phased" in strategy.lower() for strategy in strategies)
        assert any("financing" in strategy.lower() for strategy in strategies)
        assert any("contractors" in strategy.lower() for strategy in strategies)
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, service):
        """Test validation error handling."""
        await service.initialize()
        
        # Create invalid request (missing required fields)
        invalid_request = EquipmentOptimizationRequest(
            scenario_id="",  # Invalid empty ID
            field_id="",  # Invalid empty ID
            optimization_objectives=[],  # Empty objectives
            budget_constraints={},
            field_characteristics={},
            investment_timeline_months=0,  # Invalid timeline
            risk_tolerance="invalid"  # Invalid risk tolerance
        )
        
        # Should handle validation gracefully
        try:
            response = await service.optimize_equipment_investment(invalid_request)
            # If no exception is raised, response should still be valid
            assert response is not None
        except Exception as e:
            # Validation errors should be handled gracefully
            assert "validation" in str(e).lower() or "invalid" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        assert service.initialized is True
        
        await service.cleanup()
        assert service.initialized is False


class TestEquipmentOptimizationAPI:
    """Test suite for Equipment Optimization API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from services.drought_management.src.main import app
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/equipment-optimization/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "equipment-optimization"
        assert "endpoints" in data
    
    def test_financing_options_endpoint(self, client):
        """Test financing options endpoint."""
        response = client.get(
            "/api/v1/equipment-optimization/financing-options",
            params={
                "investment_type": "purchase",
                "equipment_category": "irrigation",
                "investment_amount": 200000
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check first financing option
        option = data[0]
        assert "financing_type" in option
        assert "interest_rate" in option
        assert "loan_term_years" in option
        assert "down_payment_percent" in option
    
    def test_equipment_catalog_endpoint(self, client):
        """Test equipment catalog endpoint."""
        response = client.get(
            "/api/v1/equipment-optimization/equipment-catalog",
            params={
                "category": "irrigation",
                "budget_range": "medium",
                "efficiency_requirement": 0.8
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check first equipment item
        equipment = data[0]
        assert "equipment_id" in equipment
        assert "name" in equipment
        assert "manufacturer" in equipment
        assert "base_cost" in equipment
        assert "efficiency_rating" in equipment
        assert "water_savings_percent" in equipment
    
    def test_performance_benchmarks_endpoint(self, client):
        """Test performance benchmarks endpoint."""
        response = client.get("/api/v1/equipment-optimization/performance-benchmarks")
        assert response.status_code == 200
        
        data = response.json()
        assert "irrigation_efficiency" in data
        assert "fuel_efficiency" in data
        assert "labor_efficiency" in data
        assert "water_conservation" in data
        assert "capacity_utilization" in data
        
        # Check irrigation efficiency benchmarks
        irrigation_benchmarks = data["irrigation_efficiency"]
        assert "excellent" in irrigation_benchmarks
        assert "good" in irrigation_benchmarks
        assert "average" in irrigation_benchmarks
        assert "poor" in irrigation_benchmarks
    
    def test_risk_assessment_criteria_endpoint(self, client):
        """Test risk assessment criteria endpoint."""
        response = client.get("/api/v1/equipment-optimization/risk-assessment-criteria")
        assert response.status_code == 200
        
        data = response.json()
        assert "investment_amount" in data
        assert "payback_period" in data
        assert "technology_maturity" in data
        assert "market_volatility" in data
        assert "implementation_complexity" in data
        
        # Check investment amount criteria
        investment_criteria = data["investment_amount"]
        assert "low_risk_threshold" in investment_criteria
        assert "medium_risk_threshold" in investment_criteria
        assert "high_risk_threshold" in investment_criteria


class TestEquipmentOptimizationIntegration:
    """Integration tests for Equipment Optimization Service."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization_workflow(self):
        """Test complete end-to-end optimization workflow."""
        service = EquipmentOptimizationService()
        await service.initialize()
        
        # Create comprehensive request
        request = EquipmentOptimizationRequest(
            scenario_id=str(uuid4()),
            field_id=str(uuid4()),
            optimization_objectives=[
                OptimizationObjective(
                    objective_type="water_conservation",
                    target_value=30.0,
                    weight=0.5,
                    priority="high"
                ),
                OptimizationObjective(
                    objective_type="efficiency_improvement",
                    target_value=25.0,
                    weight=0.3,
                    priority="high"
                ),
                OptimizationObjective(
                    objective_type="capacity_expansion",
                    target_value=40.0,
                    weight=0.2,
                    priority="medium"
                )
            ],
            budget_constraints={
                "max_investment": 750000,
                "annual_budget": 150000,
                "financing_preference": "equipment_financing"
            },
            field_characteristics={
                "acres": 240,
                "soil_type": "sandy_loam",
                "crop_type": "soybeans",
                "irrigation_type": "drip",
                "current_efficiency": 0.70
            },
            investment_timeline_months=18,
            risk_tolerance="low"
        )
        
        # Execute optimization
        response = await service.optimize_equipment_investment(request)
        
        # Validate response structure
        assert response.scenario_id == request.scenario_id
        assert response.optimization_plan is not None
        assert len(response.investment_scenarios) == 4
        assert response.overall_metrics is not None
        assert response.risk_assessment is not None
        assert len(response.recommendations) > 0
        
        # Validate optimization plan
        plan = response.optimization_plan
        assert plan.total_investment_required > 0
        assert plan.total_annual_savings > 0
        assert plan.implementation_timeline_months > 0
        assert 0 <= plan.overall_risk_score <= 1
        
        # Validate investment scenarios
        for scenario in response.investment_scenarios:
            assert scenario.total_investment_cost > 0
            assert scenario.total_annual_savings > 0
            assert scenario.net_present_value is not None
            assert scenario.internal_rate_of_return >= 0
            assert scenario.payback_period_years > 0
            assert scenario.return_on_investment >= 0
            assert 0 <= scenario.risk_score <= 1
        
        # Validate risk assessment
        risk_assessment = response.risk_assessment
        assert risk_assessment.overall_risk_level in ["low", "medium", "high"]
        assert 0 <= risk_assessment.risk_score <= 1
        assert len(risk_assessment.key_risk_factors) >= 0
        assert len(risk_assessment.mitigation_strategies) >= 0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_different_field_characteristics(self):
        """Test optimization with different field characteristics."""
        service = EquipmentOptimizationService()
        await service.initialize()
        
        # Test with different field sizes
        field_sizes = [80, 160, 320, 640]
        
        for acres in field_sizes:
            request = EquipmentOptimizationRequest(
                scenario_id=str(uuid4()),
                field_id=str(uuid4()),
                optimization_objectives=[
                    OptimizationObjective(
                        objective_type="water_conservation",
                        target_value=20.0,
                        weight=0.6,
                        priority="high"
                    ),
                    OptimizationObjective(
                        objective_type="efficiency_improvement",
                        target_value=15.0,
                        weight=0.4,
                        priority="medium"
                    )
                ],
                budget_constraints={
                    "max_investment": acres * 1000,  # Scale with field size
                    "annual_budget": acres * 200,
                    "financing_preference": "bank_loan"
                },
                field_characteristics={
                    "acres": acres,
                    "soil_type": "clay_loam",
                    "crop_type": "corn",
                    "irrigation_type": "center_pivot",
                    "current_efficiency": 0.75
                },
                investment_timeline_months=12,
                risk_tolerance="medium"
            )
            
            response = await service.optimize_equipment_investment(request)
            
            # Validate that recommendations scale with field size
            assert response.optimization_plan.total_investment_required > 0
            assert response.optimization_plan.total_annual_savings > 0
            
            # Larger fields should generally have higher investment requirements
            if acres > 160:
                assert response.optimization_plan.total_investment_required > 100000
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_different_risk_tolerances(self):
        """Test optimization with different risk tolerances."""
        service = EquipmentOptimizationService()
        await service.initialize()
        
        risk_tolerances = ["low", "medium", "high"]
        
        for risk_tolerance in risk_tolerances:
            request = EquipmentOptimizationRequest(
                scenario_id=str(uuid4()),
                field_id=str(uuid4()),
                optimization_objectives=[
                    OptimizationObjective(
                        objective_type="water_conservation",
                        target_value=25.0,
                        weight=0.5,
                        priority="high"
                    ),
                    OptimizationObjective(
                        objective_type="efficiency_improvement",
                        target_value=20.0,
                        weight=0.5,
                        priority="high"
                    )
                ],
                budget_constraints={
                    "max_investment": 300000,
                    "annual_budget": 60000,
                    "financing_preference": "bank_loan"
                },
                field_characteristics={
                    "acres": 160,
                    "soil_type": "clay_loam",
                    "crop_type": "corn",
                    "irrigation_type": "center_pivot",
                    "current_efficiency": 0.75
                },
                investment_timeline_months=12,
                risk_tolerance=risk_tolerance
            )
            
            response = await service.optimize_equipment_investment(request)
            
            # Validate response
            assert response.optimization_plan is not None
            assert response.risk_assessment is not None
            
            # Risk tolerance should influence recommendations
            risk_score = response.risk_assessment.risk_score
            assert 0 <= risk_score <= 1
            
            # Higher risk tolerance should generally lead to higher potential returns
            if risk_tolerance == "high":
                # Should have some high-return scenarios available
                high_return_scenarios = [
                    s for s in response.investment_scenarios 
                    if s.return_on_investment > 15
                ]
                assert len(high_return_scenarios) > 0
        
        await service.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])