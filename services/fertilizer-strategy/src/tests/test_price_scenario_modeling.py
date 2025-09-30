"""
Comprehensive tests for price scenario modeling service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
import uuid

from ..services.price_scenario_modeling_service import PriceScenarioModelingService
from ..models.price_scenario_models import (
    PriceScenarioModelingRequest, PriceScenarioModelingResponse,
    ScenarioType, MarketCondition, RiskLevel, PriceForecast,
    MonteCarloSimulation, StochasticModel, SensitivityAnalysis,
    DecisionTreeNode, ProbabilityDistribution, RiskAssessment
)
from ..models.price_models import FertilizerPriceData, FertilizerProduct, PriceSource


class TestPriceScenarioModelingService:
    """Comprehensive test suite for price scenario modeling service."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return PriceScenarioModelingService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample request for testing."""
        return PriceScenarioModelingRequest(
            analysis_name="Test Analysis",
            field_size_acres=100.0,
            crop_type="corn",
            expected_yield_bu_per_acre=180.0,
            crop_price_per_bu=5.50,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "type": "nitrogen",
                    "rate_lbs_per_acre": 150,
                    "application_method": "broadcast"
                },
                {
                    "product": "DAP",
                    "type": "phosphorus",
                    "rate_lbs_per_acre": 100,
                    "application_method": "broadcast"
                }
            ],
            analysis_horizon_days=365,
            confidence_level=0.95,
            monte_carlo_iterations=1000  # Reduced for testing
        )
    
    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data."""
        return {
            'current_prices': {
                'urea': FertilizerPriceData(
                    product=FertilizerProduct(name="urea", fertilizer_type="nitrogen"),
                    price_per_unit=500.0,
                    unit="ton",
                    region="US",
                    source=PriceSource.USDA_NASS,
                    price_date=date.today(),
                    created_at=datetime.utcnow()
                ),
                'DAP': FertilizerPriceData(
                    product=FertilizerProduct(name="DAP", fertilizer_type="phosphorus"),
                    price_per_unit=600.0,
                    unit="ton",
                    region="US",
                    source=PriceSource.USDA_NASS,
                    price_date=date.today(),
                    created_at=datetime.utcnow()
                )
            },
            'historical_data': {
                'urea': [FertilizerPriceData(
                    product=FertilizerProduct(name="urea", fertilizer_type="nitrogen"),
                    price_per_unit=480.0,
                    unit="ton",
                    region="US",
                    source=PriceSource.USDA_NASS,
                    price_date=date.today(),
                    created_at=datetime.utcnow()
                )],
                'DAP': [FertilizerPriceData(
                    product=FertilizerProduct(name="DAP", fertilizer_type="phosphorus"),
                    price_per_unit=580.0,
                    unit="ton",
                    region="US",
                    source=PriceSource.USDA_NASS,
                    price_date=date.today(),
                    created_at=datetime.utcnow()
                )]
            },
            'market_conditions': {},
            'economic_indicators': {
                'commodity_prices': {
                    'corn': 5.50,
                    'soybeans': 12.00,
                    'wheat': 7.00
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_comprehensive_scenario_model_success(self, service, sample_request, mock_market_data):
        """Test successful comprehensive scenario model creation."""
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            with patch.object(service, '_generate_all_scenarios') as mock_generate_scenarios:
                with patch.object(service, '_perform_monte_carlo_simulation') as mock_monte_carlo:
                    with patch.object(service, '_perform_stochastic_modeling') as mock_stochastic:
                        with patch.object(service, '_perform_sensitivity_analysis') as mock_sensitivity:
                            with patch.object(service, '_create_decision_tree') as mock_decision_tree:
                                with patch.object(service, '_generate_scenario_recommendations') as mock_recommendations:
                                    
                                    # Mock return values
                                    mock_scenarios = [MagicMock()]
                                    mock_monte_carlo_result = MonteCarloSimulation(
                                        simulation_id=str(uuid.uuid4()),
                                        iterations=1000,
                                        confidence_levels=[0.95],
                                        scenario_results=[],
                                        overall_statistics={},
                                        created_at=datetime.utcnow()
                                    )
                                    mock_stochastic_result = StochasticModel(
                                        model_id=str(uuid.uuid4()),
                                        model_type="geometric_brownian_motion",
                                        scenarios=[],
                                        model_parameters={},
                                        created_at=datetime.utcnow()
                                    )
                                    mock_sensitivity_result = SensitivityAnalysis(
                                        analysis_id=str(uuid.uuid4()),
                                        price_change_percentages=[-10, 0, 10],
                                        scenario_results=[],
                                        sensitivity_metrics={},
                                        created_at=datetime.utcnow()
                                    )
                                    mock_decision_tree_result = DecisionTreeNode(
                                        node_id=str(uuid.uuid4()),
                                        node_type="root",
                                        decision_criteria="price_scenario_selection",
                                        description="Select optimal price scenario",
                                        children=[]
                                    )
                                    mock_recommendations_result = ["Test recommendation"]
                                    
                                    mock_generate_scenarios.return_value = mock_scenarios
                                    mock_monte_carlo.return_value = mock_monte_carlo_result
                                    mock_stochastic.return_value = mock_stochastic_result
                                    mock_sensitivity.return_value = mock_sensitivity_result
                                    mock_decision_tree.return_value = mock_decision_tree_result
                                    mock_recommendations.return_value = mock_recommendations_result
                                    
                                    # Execute
                                    result = await service.create_comprehensive_scenario_model(sample_request)
                                    
                                    # Assertions
                                    assert isinstance(result, PriceScenarioModelingResponse)
                                    assert result.analysis_id == sample_request.analysis_id
                                    assert result.scenarios == mock_scenarios
                                    assert result.monte_carlo_simulation == mock_monte_carlo_result
                                    assert result.stochastic_model == mock_stochastic_result
                                    assert result.sensitivity_analysis == mock_sensitivity_result
                                    assert result.decision_tree == mock_decision_tree_result
                                    assert result.recommendations == mock_recommendations_result
                                    assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_get_market_data(self, service, sample_request):
        """Test market data retrieval."""
        with patch.object(service.price_tracking_service, 'get_current_price') as mock_get_price:
            with patch.object(service.price_tracking_service, 'get_price_history') as mock_get_history:
                with patch.object(service.commodity_price_service, 'get_current_prices') as mock_get_commodity:
                    
                    # Mock return values
                    mock_price_data = FertilizerPriceData(
                        product=FertilizerProduct(name="urea", fertilizer_type="nitrogen"),
                        price_per_unit=500.0,
                        unit="ton",
                        region="US",
                        source=PriceSource.USDA_NASS,
                        price_date=date.today(),
                        created_at=datetime.utcnow()
                    )
                    
                    mock_get_price.return_value = mock_price_data
                    mock_get_history.return_value = [mock_price_data]
                    mock_get_commodity.return_value = {'corn': 5.50}
                    
                    # Execute
                    result = await service._get_market_data(sample_request)
                    
                    # Assertions
                    assert 'current_prices' in result
                    assert 'historical_data' in result
                    assert 'market_conditions' in result
                    assert 'economic_indicators' in result
                    assert len(result['current_prices']) == 2  # urea and DAP
    
    @pytest.mark.asyncio
    async def test_generate_all_scenarios(self, service, sample_request, mock_market_data):
        """Test scenario generation."""
        with patch.object(service, '_generate_scenario') as mock_generate_scenario:
            with patch.object(service, '_generate_custom_scenario') as mock_generate_custom:
                
                # Mock scenario
                mock_scenario = MagicMock()
                mock_generate_scenario.return_value = mock_scenario
                mock_generate_custom.return_value = mock_scenario
                
                # Execute
                result = await service._generate_all_scenarios(sample_request, mock_market_data)
                
                # Assertions
                assert len(result) == len(service.scenario_types)
                assert all(isinstance(scenario, type(mock_scenario)) for scenario in result)
    
    @pytest.mark.asyncio
    async def test_generate_scenario(self, service, sample_request, mock_market_data):
        """Test individual scenario generation."""
        with patch.object(service, '_generate_price_forecast') as mock_forecast:
            with patch.object(service, '_calculate_scenario_metrics') as mock_metrics:
                with patch.object(service, '_generate_probability_distribution') as mock_prob:
                    with patch.object(service, '_generate_risk_assessment') as mock_risk:
                        
                        # Mock return values
                        mock_forecast_data = PriceForecast(
                            product_name="urea",
                            current_price=500.0,
                            forecasted_price=600.0,
                            price_change_percent=20.0,
                            confidence_level=0.8,
                            forecast_horizon_days=365,
                            volatility_factor=0.2
                        )
                        
                        mock_metrics_data = {
                            'total_fertilizer_cost': 10000.0,
                            'total_crop_revenue': 99000.0,
                            'net_profit': 89000.0,
                            'profit_margin_percent': 89.9,
                            'roi_percent': 890.0
                        }
                        
                        mock_prob_data = ProbabilityDistribution(
                            mean_probability=0.2,
                            standard_deviation=0.05,
                            confidence_intervals={'0.95': 0.25}
                        )
                        
                        mock_risk_data = RiskAssessment(
                            overall_risk_level=RiskLevel.MEDIUM,
                            price_volatility_risk=0.2,
                            supply_chain_risk=0.1,
                            market_demand_risk=0.2,
                            economic_risk=0.1,
                            risk_factors=['High price volatility']
                        )
                        
                        mock_forecast.return_value = mock_forecast_data
                        mock_metrics.return_value = mock_metrics_data
                        mock_prob.return_value = mock_prob_data
                        mock_risk.return_value = mock_risk_data
                        
                        # Execute
                        result = await service._generate_scenario(
                            ScenarioType.BULL_MARKET, sample_request, mock_market_data
                        )
                        
                        # Assertions
                        assert result.scenario_type == ScenarioType.BULL_MARKET
                        assert result.market_condition == MarketCondition.BULL_MARKET
                        assert len(result.price_forecasts) == 2  # urea and DAP
                        assert result.scenario_metrics == mock_metrics_data
                        assert result.probability_distribution == mock_prob_data
                        assert result.risk_assessment == mock_risk_data
    
    @pytest.mark.asyncio
    async def test_perform_monte_carlo_simulation(self, service, sample_request, mock_market_data):
        """Test Monte Carlo simulation."""
        # Create mock scenarios
        mock_scenarios = [MagicMock()]
        mock_scenarios[0].scenario_id = "test-scenario"
        mock_scenarios[0].scenario_name = "Test Scenario"
        mock_scenarios[0].price_forecasts = [
            PriceForecast(
                product_name="urea",
                current_price=500.0,
                forecasted_price=600.0,
                price_change_percent=20.0,
                confidence_level=0.8,
                forecast_horizon_days=365,
                volatility_factor=0.2
            )
        ]
        
        with patch.object(service, '_calculate_profit_for_prices') as mock_calculate_profit:
            mock_calculate_profit.return_value = 1000.0
            
            # Execute
            result = await service._perform_monte_carlo_simulation(
                sample_request, mock_market_data, mock_scenarios
            )
            
            # Assertions
            assert isinstance(result, MonteCarloSimulation)
            assert result.iterations == sample_request.monte_carlo_iterations
            assert len(result.scenario_results) == len(mock_scenarios)
            assert 'overall_statistics' in result.overall_statistics
    
    @pytest.mark.asyncio
    async def test_perform_stochastic_modeling(self, service, sample_request, mock_market_data):
        """Test stochastic modeling."""
        # Create mock scenarios
        mock_scenarios = [MagicMock()]
        mock_scenarios[0].scenario_id = "test-scenario"
        mock_scenarios[0].scenario_name = "Test Scenario"
        mock_scenarios[0].scenario_type = ScenarioType.BULL_MARKET
        
        # Execute
        result = await service._perform_stochastic_modeling(
            sample_request, mock_market_data, mock_scenarios
        )
        
        # Assertions
        assert isinstance(result, StochasticModel)
        assert result.model_type == "geometric_brownian_motion"
        assert len(result.scenarios) == len(mock_scenarios)
        assert 'model_parameters' in result.model_parameters
    
    @pytest.mark.asyncio
    async def test_perform_sensitivity_analysis(self, service, sample_request, mock_market_data):
        """Test sensitivity analysis."""
        # Create mock scenarios
        mock_scenarios = [MagicMock()]
        mock_scenarios[0].scenario_id = "test-scenario"
        mock_scenarios[0].scenario_name = "Test Scenario"
        mock_scenarios[0].scenario_metrics = {'net_profit': 1000.0}
        mock_scenarios[0].price_forecasts = [
            PriceForecast(
                product_name="urea",
                current_price=500.0,
                forecasted_price=600.0,
                price_change_percent=20.0,
                confidence_level=0.8,
                forecast_horizon_days=365,
                volatility_factor=0.2
            )
        ]
        
        with patch.object(service, '_calculate_profit_for_prices') as mock_calculate_profit:
            mock_calculate_profit.return_value = 1000.0
            
            # Execute
            result = await service._perform_sensitivity_analysis(
                sample_request, mock_market_data, mock_scenarios
            )
            
            # Assertions
            assert isinstance(result, SensitivityAnalysis)
            assert len(result.price_change_percentages) > 0
            assert len(result.scenario_results) == len(mock_scenarios)
            assert 'sensitivity_metrics' in result.sensitivity_metrics
    
    @pytest.mark.asyncio
    async def test_create_decision_tree(self, service, sample_request):
        """Test decision tree creation."""
        # Create mock scenarios and Monte Carlo results
        mock_scenarios = [MagicMock()]
        mock_scenarios[0].scenario_id = "test-scenario"
        mock_scenarios[0].scenario_name = "Test Scenario"
        mock_scenarios[0].scenario_type = ScenarioType.BULL_MARKET
        
        mock_monte_carlo_results = MonteCarloSimulation(
            simulation_id=str(uuid.uuid4()),
            iterations=1000,
            confidence_levels=[0.95],
            scenario_results=[],
            overall_statistics={},
            created_at=datetime.utcnow()
        )
        
        # Execute
        result = await service._create_decision_tree(
            sample_request, mock_scenarios, mock_monte_carlo_results
        )
        
        # Assertions
        assert isinstance(result, DecisionTreeNode)
        assert result.node_type == "root"
        assert result.decision_criteria == "price_scenario_selection"
        assert len(result.children) > 0
    
    def test_get_scenario_multipliers(self, service):
        """Test scenario multiplier calculation."""
        # Test different scenario types
        bull_multipliers = service._get_scenario_multipliers(ScenarioType.BULL_MARKET)
        bear_multipliers = service._get_scenario_multipliers(ScenarioType.BEAR_MARKET)
        baseline_multipliers = service._get_scenario_multipliers(ScenarioType.BASELINE)
        
        # Assertions
        assert bull_multipliers['fertilizer'] > 1.0
        assert bull_multipliers['crop'] > 1.0
        assert bear_multipliers['fertilizer'] < 1.0
        assert bear_multipliers['crop'] < 1.0
        assert baseline_multipliers['fertilizer'] == 1.0
        assert baseline_multipliers['crop'] == 1.0
    
    def test_get_scenario_name(self, service):
        """Test scenario name generation."""
        bull_name = service._get_scenario_name(ScenarioType.BULL_MARKET)
        bear_name = service._get_scenario_name(ScenarioType.BEAR_MARKET)
        baseline_name = service._get_scenario_name(ScenarioType.BASELINE)
        
        # Assertions
        assert "Bull Market" in bull_name
        assert "Bear Market" in bear_name
        assert "Baseline" in baseline_name
    
    def test_get_market_condition(self, service):
        """Test market condition mapping."""
        bull_condition = service._get_market_condition(ScenarioType.BULL_MARKET)
        bear_condition = service._get_market_condition(ScenarioType.BEAR_MARKET)
        baseline_condition = service._get_market_condition(ScenarioType.BASELINE)
        
        # Assertions
        assert bull_condition == MarketCondition.BULL_MARKET
        assert bear_condition == MarketCondition.BEAR_MARKET
        assert baseline_condition == MarketCondition.STABLE
    
    def test_generate_stochastic_price_path(self, service):
        """Test stochastic price path generation."""
        current_price = 500.0
        target_price = 600.0
        volatility = 0.2
        horizon_days = 365
        
        # Execute
        price_path = service._generate_stochastic_price_path(
            current_price, target_price, volatility, horizon_days
        )
        
        # Assertions
        assert len(price_path) == horizon_days + 1  # +1 for initial price
        assert price_path[0] == current_price
        assert all(price > 0 for price in price_path)
    
    def test_calculate_stochastic_metrics(self, service, sample_request):
        """Test stochastic metrics calculation."""
        price_paths = [
            {
                'product_name': 'urea',
                'price_path': [500.0, 510.0, 520.0, 530.0]
            },
            {
                'product_name': 'DAP',
                'price_path': [600.0, 610.0, 620.0, 630.0]
            }
        ]
        
        # Execute
        metrics = service._calculate_stochastic_metrics(price_paths, sample_request)
        
        # Assertions
        assert 'price_paths_count' in metrics
        assert 'average_final_price' in metrics
        assert 'price_volatility' in metrics
        assert 'price_trend' in metrics
        assert metrics['price_paths_count'] == len(price_paths)
    
    def test_calculate_sensitivity_metrics(self, service):
        """Test sensitivity metrics calculation."""
        sensitivity_results = [
            {
                'scenario_id': 'test-1',
                'scenario_name': 'Test Scenario 1',
                'sensitivity_data': [
                    {'price_change_percent': -10, 'profit_change': -100},
                    {'price_change_percent': 0, 'profit_change': 0},
                    {'price_change_percent': 10, 'profit_change': 100}
                ]
            }
        ]
        
        # Execute
        metrics = service._calculate_sensitivity_metrics(sensitivity_results)
        
        # Assertions
        assert 'most_sensitive_scenario' in metrics
        assert 'average_sensitivity' in metrics
        assert 'sensitivity_range' in metrics
        assert metrics['most_sensitive_scenario'] == 'Test Scenario 1'
    
    def test_calculate_confidence_intervals(self, service):
        """Test confidence interval calculation."""
        results = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        
        # Execute
        intervals = service._calculate_confidence_intervals(results)
        
        # Assertions
        assert '0.5' in intervals
        assert '0.95' in intervals
        assert '0.99' in intervals
        
        for confidence, interval in intervals.items():
            assert 'lower' in interval
            assert 'upper' in interval
            assert interval['lower'] <= interval['upper']
    
    def test_get_z_score(self, service):
        """Test z-score calculation."""
        z_95 = service._get_z_score(0.95)
        z_99 = service._get_z_score(0.99)
        
        # Assertions
        assert z_95 == 1.960
        assert z_99 == 2.576
    
    @pytest.mark.asyncio
    async def test_calculate_profit_for_prices(self, service, sample_request):
        """Test profit calculation for given prices."""
        prices = {
            'urea': 500.0,
            'DAP': 600.0
        }
        
        # Execute
        profit = await service._calculate_profit_for_prices(sample_request, prices)
        
        # Assertions
        assert isinstance(profit, float)
        # Profit should be positive for reasonable prices
        assert profit > 0


class TestPriceScenarioModelingIntegration:
    """Integration tests for price scenario modeling."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_scenario_modeling(self):
        """Test end-to-end scenario modeling workflow."""
        service = PriceScenarioModelingService()
        
        request = PriceScenarioModelingRequest(
            analysis_name="Integration Test",
            field_size_acres=50.0,
            crop_type="corn",
            expected_yield_bu_per_acre=160.0,
            crop_price_per_bu=5.00,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "type": "nitrogen",
                    "rate_lbs_per_acre": 120,
                    "application_method": "broadcast"
                }
            ],
            analysis_horizon_days=180,
            confidence_level=0.90,
            monte_carlo_iterations=100  # Small for testing
        )
        
        # Mock external dependencies
        with patch.object(service.price_tracking_service, 'get_current_price') as mock_get_price:
            with patch.object(service.price_tracking_service, 'get_price_history') as mock_get_history:
                with patch.object(service.commodity_price_service, 'get_current_prices') as mock_get_commodity:
                    
                    # Mock return values
                    mock_price_data = FertilizerPriceData(
                        product=FertilizerProduct(name="urea", fertilizer_type="nitrogen"),
                        price_per_unit=450.0,
                        unit="ton",
                        region="US",
                        source=PriceSource.USDA_NASS,
                        price_date=date.today(),
                        created_at=datetime.utcnow()
                    )
                    
                    mock_get_price.return_value = mock_price_data
                    mock_get_history.return_value = [mock_price_data]
                    mock_get_commodity.return_value = {'corn': 5.00}
                    
                    # Execute
                    result = await service.create_comprehensive_scenario_model(request)
                    
                    # Assertions
                    assert isinstance(result, PriceScenarioModelingResponse)
                    assert result.analysis_id == request.analysis_id
                    assert len(result.scenarios) > 0
                    assert isinstance(result.monte_carlo_simulation, MonteCarloSimulation)
                    assert isinstance(result.stochastic_model, StochasticModel)
                    assert isinstance(result.sensitivity_analysis, SensitivityAnalysis)
                    assert isinstance(result.decision_tree, DecisionTreeNode)
                    assert len(result.recommendations) > 0
                    assert result.processing_time_ms > 0


class TestPriceScenarioModelingValidation:
    """Validation tests for price scenario modeling."""
    
    def test_request_validation(self):
        """Test request validation."""
        # Test valid request
        valid_request = PriceScenarioModelingRequest(
            field_size_acres=100.0,
            crop_type="corn",
            expected_yield_bu_per_acre=180.0,
            crop_price_per_bu=5.50,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "type": "nitrogen",
                    "rate_lbs_per_acre": 150,
                    "application_method": "broadcast"
                }
            ]
        )
        
        assert valid_request.field_size_acres > 0
        assert valid_request.crop_price_per_bu > 0
        assert len(valid_request.fertilizer_requirements) > 0
    
    def test_scenario_type_validation(self):
        """Test scenario type validation."""
        # Test all scenario types
        for scenario_type in ScenarioType:
            assert scenario_type in [
                ScenarioType.BULL_MARKET,
                ScenarioType.BEAR_MARKET,
                ScenarioType.VOLATILE_MARKET,
                ScenarioType.SEASONAL_PATTERNS,
                ScenarioType.SUPPLY_DISRUPTION,
                ScenarioType.BASELINE,
                ScenarioType.CUSTOM
            ]
    
    def test_risk_level_validation(self):
        """Test risk level validation."""
        # Test all risk levels
        for risk_level in RiskLevel:
            assert risk_level in [
                RiskLevel.LOW,
                RiskLevel.MEDIUM,
                RiskLevel.HIGH,
                RiskLevel.CRITICAL
            ]
    
    def test_market_condition_validation(self):
        """Test market condition validation."""
        # Test all market conditions
        for condition in MarketCondition:
            assert condition in [
                MarketCondition.BULL_MARKET,
                MarketCondition.BEAR_MARKET,
                MarketCondition.VOLATILE,
                MarketCondition.STABLE,
                MarketCondition.SEASONAL,
                MarketCondition.SUPPLY_DISRUPTION,
                MarketCondition.CUSTOM
            ]


class TestPriceScenarioModelingPerformance:
    """Performance tests for price scenario modeling."""
    
    @pytest.mark.asyncio
    async def test_monte_carlo_performance(self):
        """Test Monte Carlo simulation performance."""
        service = PriceScenarioModelingService()
        
        request = PriceScenarioModelingRequest(
            field_size_acres=100.0,
            crop_type="corn",
            expected_yield_bu_per_acre=180.0,
            crop_price_per_bu=5.50,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "type": "nitrogen",
                    "rate_lbs_per_acre": 150,
                    "application_method": "broadcast"
                }
            ],
            monte_carlo_iterations=1000
        )
        
        mock_market_data = {
            'current_prices': {},
            'historical_data': {},
            'market_conditions': {},
            'economic_indicators': {}
        }
        
        mock_scenarios = [MagicMock()]
        mock_scenarios[0].scenario_id = "test"
        mock_scenarios[0].scenario_name = "Test"
        mock_scenarios[0].price_forecasts = []
        
        with patch.object(service, '_calculate_profit_for_prices', return_value=1000.0):
            import time
            start_time = time.time()
            
            result = await service._perform_monte_carlo_simulation(
                request, mock_market_data, mock_scenarios
            )
            
            elapsed_time = time.time() - start_time
            
            # Performance assertions
            assert elapsed_time < 5.0  # Should complete within 5 seconds
            assert isinstance(result, MonteCarloSimulation)
            assert result.iterations == 1000
    
    @pytest.mark.asyncio
    async def test_stochastic_modeling_performance(self):
        """Test stochastic modeling performance."""
        service = PriceScenarioModelingService()
        
        request = PriceScenarioModelingRequest(
            field_size_acres=100.0,
            crop_type="corn",
            expected_yield_bu_per_acre=180.0,
            crop_price_per_bu=5.50,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "type": "nitrogen",
                    "rate_lbs_per_acre": 150,
                    "application_method": "broadcast"
                }
            ],
            analysis_horizon_days=365
        )
        
        mock_market_data = {
            'current_prices': {},
            'historical_data': {},
            'market_conditions': {},
            'economic_indicators': {}
        }
        
        mock_scenarios = [MagicMock()]
        mock_scenarios[0].scenario_id = "test"
        mock_scenarios[0].scenario_name = "Test"
        mock_scenarios[0].scenario_type = ScenarioType.BULL_MARKET
        mock_scenarios[0].price_forecasts = []
        
        import time
        start_time = time.time()
        
        result = await service._perform_stochastic_modeling(
            request, mock_market_data, mock_scenarios
        )
        
        elapsed_time = time.time() - start_time
        
        # Performance assertions
        assert elapsed_time < 2.0  # Should complete within 2 seconds
        assert isinstance(result, StochasticModel)