"""
Comprehensive tests for price impact analysis system.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from ..models.price_impact_models import (
    PriceImpactAnalysisRequest, AnalysisType, ScenarioType,
    PriceImpactAnalysisResponse, PriceImpactMetrics, PriceImpactAnalysisResult
)
from ..services.price_impact_analysis_service import PriceImpactAnalysisService
from ..database.price_impact_db import PriceImpactAnalysisRepository


class TestPriceImpactAnalysisService:
    """Test suite for PriceImpactAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return PriceImpactAnalysisService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample analysis request."""
        return PriceImpactAnalysisRequest(
            analysis_type=AnalysisType.SENSITIVITY,
            field_size_acres=100.0,
            crop_type="corn",
            expected_yield_bu_per_acre=180.0,
            crop_price_per_bu=5.50,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "rate_lbs_per_acre": 150,
                    "fertilizer_type": "nitrogen",
                    "n_content": 46
                },
                {
                    "product": "dap",
                    "rate_lbs_per_acre": 100,
                    "fertilizer_type": "phosphorus",
                    "p_content": 46
                }
            ],
            price_change_percentages=[-25, -10, 0, 10, 25],
            created_by="test_user"
        )
    
    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data."""
        return {
            'fertilizer_prices': {
                'urea': MagicMock(
                    price_per_unit=500.0,
                    unit_conversion_factor=2000,  # $500/ton = $0.25/lb
                    product_name="urea"
                ),
                'dap': MagicMock(
                    price_per_unit=600.0,
                    unit_conversion_factor=2000,  # $600/ton = $0.30/lb
                    product_name="dap"
                )
            },
            'commodity_prices': {
                'corn': MagicMock(
                    price_per_unit=5.50,
                    unit_conversion_factor=1
                )
            },
            'price_trends': {},
            'volatility_metrics': {}
        }
    
    @pytest.mark.asyncio
    async def test_analyze_price_impact_success(self, service, sample_request, mock_market_data):
        """Test successful price impact analysis."""
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            with patch.object(service, '_validate_request', return_value=None):
                result = await service.analyze_price_impact(sample_request)
                
                assert result.success is True
                assert result.analysis_result is not None
                assert result.analysis_result.analysis_id == sample_request.analysis_id
                assert result.analysis_result.analysis_type == AnalysisType.SENSITIVITY
                assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_analyze_price_impact_validation_error(self, service, sample_request):
        """Test analysis with validation error."""
        # Create invalid request
        invalid_request = sample_request.copy()
        invalid_request.field_size_acres = -10  # Invalid field size
        
        result = await service.analyze_price_impact(invalid_request)
        
        assert result.success is False
        assert result.error_message is not None
        assert "Field size must be positive" in result.error_message
    
    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, service, sample_request, mock_market_data):
        """Test sensitivity analysis functionality."""
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service._perform_sensitivity_analysis(sample_request, mock_market_data)
            
            assert result.analysis_type == AnalysisType.SENSITIVITY
            assert result.baseline_metrics is not None
            assert result.sensitivity_results is not None
            assert len(result.sensitivity_results) >= 2  # At least fertilizer and crop price sensitivity
            
            # Check sensitivity results structure
            for sensitivity_result in result.sensitivity_results:
                assert sensitivity_result.parameter_name in ["fertilizer_price", "crop_price", "yield"]
                assert len(sensitivity_result.parameter_values) > 0
                assert len(sensitivity_result.impact_values) > 0
                assert sensitivity_result.elasticity is not None
                assert sensitivity_result.sensitivity_score >= 0
    
    @pytest.mark.asyncio
    async def test_scenario_analysis(self, service, sample_request, mock_market_data):
        """Test scenario analysis functionality."""
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service._perform_scenario_analysis(sample_request, mock_market_data)
            
            assert result.analysis_type == AnalysisType.SCENARIO
            assert result.baseline_metrics is not None
            assert result.scenarios is not None
            assert len(result.scenarios) >= 4  # Baseline, optimistic, pessimistic, volatile
            
            # Check scenario structure
            for scenario in result.scenarios:
                assert 'scenario_type' in scenario
                assert 'scenario_name' in scenario
                assert 'net_profit' in scenario
                assert 'profit_change_percent' in scenario
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, service, sample_request, mock_market_data):
        """Test risk assessment functionality."""
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service._perform_risk_assessment(sample_request, mock_market_data)
            
            assert result.analysis_type == AnalysisType.RISK_ASSESSMENT
            assert result.baseline_metrics is not None
            assert result.risk_assessment is not None
            
            # Check risk assessment structure
            risk_assessment = result.risk_assessment
            assert risk_assessment.overall_risk_level is not None
            assert 0 <= risk_assessment.risk_score <= 1
            assert 0 <= risk_assessment.price_volatility_risk <= 1
            assert 0 <= risk_assessment.market_timing_risk <= 1
            assert 0 <= risk_assessment.supply_chain_risk <= 1
            assert 0 <= risk_assessment.weather_risk <= 1
            assert len(risk_assessment.recommended_actions) > 0
    
    @pytest.mark.asyncio
    async def test_baseline_metrics_calculation(self, service, sample_request, mock_market_data):
        """Test baseline metrics calculation."""
        metrics = await service._calculate_baseline_metrics(sample_request, mock_market_data)
        
        # Check financial metrics
        assert metrics.total_fertilizer_cost > 0
        assert metrics.total_crop_revenue > 0
        assert metrics.net_profit is not None
        assert metrics.profit_margin_percent is not None
        
        # Check per-unit metrics
        assert metrics.fertilizer_cost_per_acre > 0
        assert metrics.fertilizer_cost_per_bu > 0
        assert metrics.crop_revenue_per_acre > 0
        
        # Check impact metrics (should be 0 for baseline)
        assert metrics.price_impact_percent == 0
        assert metrics.profitability_change_percent == 0
    
    @pytest.mark.asyncio
    async def test_fertilizer_price_sensitivity(self, service, sample_request, mock_market_data):
        """Test fertilizer price sensitivity analysis."""
        result = await service._analyze_fertilizer_price_sensitivity(
            sample_request, mock_market_data, [-25, 0, 25]
        )
        
        assert result.parameter_name == "fertilizer_price"
        assert len(result.parameter_values) == 3
        assert len(result.impact_values) == 3
        assert result.elasticity is not None
        assert result.sensitivity_score >= 0
        
        # Check that higher fertilizer prices lead to lower profits
        baseline_idx = result.parameter_values.index(0)
        baseline_impact = result.impact_values[baseline_idx]
        
        # Find positive price change (25%)
        positive_idx = result.parameter_values.index(25)
        positive_impact = result.impact_values[positive_idx]
        
        assert positive_impact < baseline_impact  # Higher prices = lower profit
    
    @pytest.mark.asyncio
    async def test_crop_price_sensitivity(self, service, sample_request, mock_market_data):
        """Test crop price sensitivity analysis."""
        result = await service._analyze_crop_price_sensitivity(
            sample_request, mock_market_data, [-25, 0, 25]
        )
        
        assert result.parameter_name == "crop_price"
        assert len(result.parameter_values) == 3
        assert len(result.impact_values) == 3
        assert result.elasticity is not None
        assert result.sensitivity_score >= 0
        
        # Check that higher crop prices lead to higher profits
        baseline_idx = result.parameter_values.index(0)
        baseline_impact = result.impact_values[baseline_idx]
        
        # Find positive price change (25%)
        positive_idx = result.parameter_values.index(25)
        positive_impact = result.impact_values[positive_idx]
        
        assert positive_impact > baseline_impact  # Higher prices = higher profit
    
    @pytest.mark.asyncio
    async def test_yield_sensitivity(self, service, sample_request, mock_market_data):
        """Test yield sensitivity analysis."""
        result = await service._analyze_yield_sensitivity(
            sample_request, mock_market_data, [-25, 0, 25]
        )
        
        assert result.parameter_name == "yield"
        assert len(result.parameter_values) == 3
        assert len(result.impact_values) == 3
        assert result.elasticity is not None
        assert result.sensitivity_score >= 0
        
        # Check that higher yields lead to higher profits
        baseline_idx = result.parameter_values.index(0)
        baseline_impact = result.impact_values[baseline_idx]
        
        # Find positive yield change (25%)
        positive_idx = result.parameter_values.index(25)
        positive_impact = result.impact_values[positive_idx]
        
        assert positive_impact > baseline_impact  # Higher yields = higher profit
    
    @pytest.mark.asyncio
    async def test_scenario_generation(self, service, sample_request, mock_market_data):
        """Test scenario data generation."""
        # Test optimistic scenario
        optimistic_data = await service._generate_scenario_data(
            ScenarioType.OPTIMISTIC, sample_request, mock_market_data
        )
        
        assert optimistic_data['scenario_type'] == 'optimistic'
        assert optimistic_data['fertilizer_multiplier'] == 0.8  # Lower fertilizer prices
        assert optimistic_data['crop_multiplier'] == 1.2  # Higher crop prices
        assert optimistic_data['net_profit'] > 0  # Should be profitable
        
        # Test pessimistic scenario
        pessimistic_data = await service._generate_scenario_data(
            ScenarioType.PESSIMISTIC, sample_request, mock_market_data
        )
        
        assert pessimistic_data['scenario_type'] == 'pessimistic'
        assert pessimistic_data['fertilizer_multiplier'] == 1.3  # Higher fertilizer prices
        assert pessimistic_data['crop_multiplier'] == 0.8  # Lower crop prices
    
    @pytest.mark.asyncio
    async def test_risk_factors_assessment(self, service, sample_request, mock_market_data):
        """Test risk factors assessment."""
        risk_factors = await service._assess_risk_factors(sample_request, mock_market_data)
        
        assert 'price_volatility' in risk_factors
        assert 'market_timing' in risk_factors
        assert 'supply_chain' in risk_factors
        assert 'weather' in risk_factors
        
        # Check risk factor ranges
        for factor, score in risk_factors.items():
            assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_overall_risk_calculation(self, service):
        """Test overall risk calculation."""
        risk_factors = {
            'price_volatility': 0.8,
            'market_timing': 0.6,
            'supply_chain': 0.4,
            'weather': 0.7
        }
        
        overall_risk = service._calculate_overall_risk(risk_factors)
        
        assert 'level' in overall_risk
        assert 'score' in overall_risk
        assert 0 <= overall_risk['score'] <= 1
        assert overall_risk['level'] in ['low', 'medium', 'high', 'critical']
    
    @pytest.mark.asyncio
    async def test_elasticity_calculation(self, service):
        """Test elasticity calculation."""
        # Test positive elasticity (normal case)
        parameter_values = [-25, 0, 25]
        impact_values = [-50, 0, 50]  # Linear relationship
        
        elasticity = service._calculate_elasticity(parameter_values, impact_values)
        assert elasticity > 0  # Should be positive
        
        # Test negative elasticity with asymmetric values
        parameter_values = [0, 25, 50]  # Start from baseline
        impact_values = [0, -25, -50]  # Inverse relationship
        
        elasticity = service._calculate_elasticity(parameter_values, impact_values)
        assert elasticity < 0  # Should be negative
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self, service, sample_request, mock_market_data):
        """Test comprehensive analysis functionality."""
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service._perform_comprehensive_analysis(sample_request, mock_market_data)
            
            assert result.baseline_metrics is not None
            assert result.scenarios is not None
            assert result.sensitivity_results is not None
            assert result.risk_assessment is not None
            assert len(result.recommendations) > 0
            
            # Check that all analysis components are present
            assert len(result.scenarios) >= 4  # All default scenarios
            assert len(result.sensitivity_results) >= 2  # At least fertilizer and crop price
    
    @pytest.mark.asyncio
    async def test_recommendation_generation(self, service):
        """Test recommendation generation methods."""
        # Test sensitivity recommendations
        sensitivity_results = [
            MagicMock(
                parameter_name="fertilizer_price",
                sensitivity_score=3.0,
                critical_threshold=-20.0
            )
        ]
        
        recommendations = service._generate_sensitivity_recommendations(sensitivity_results)
        assert len(recommendations) > 0
        assert any("fertilizer_price" in rec for rec in recommendations)
        
        # Test scenario recommendations
        scenario_results = [
            {
                'scenario_name': 'Optimistic',
                'net_profit': 10000
            },
            {
                'scenario_name': 'Pessimistic',
                'net_profit': -1000
            }
        ]
        
        recommendations = service._generate_scenario_recommendations(scenario_results)
        assert len(recommendations) > 0
        assert any("Optimistic" in rec for rec in recommendations)
        assert any("Pessimistic" in rec for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service, sample_request):
        """Test error handling in analysis."""
        # Test with invalid market data
        invalid_market_data = {}
        
        with patch.object(service, '_get_market_data', return_value=invalid_market_data):
            result = await service.analyze_price_impact(sample_request)
            
            # Should handle gracefully
            assert result.success is False or result.analysis_result is not None
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_request, mock_market_data):
        """Test that analysis meets performance requirements."""
        import time
        
        start_time = time.time()
        
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service.analyze_price_impact(sample_request)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_time < 5.0, f"Analysis took {elapsed_time:.2f}s, exceeds 5s requirement"
        assert result.processing_time_ms < 5000, f"Processing time {result.processing_time_ms}ms exceeds 5s requirement"


class TestPriceImpactAnalysisRepository:
    """Test suite for PriceImpactAnalysisRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create repository instance for testing."""
        return PriceImpactAnalysisRepository("sqlite:///:memory:")
    
    @pytest.fixture
    def sample_request(self):
        """Create sample analysis request."""
        return PriceImpactAnalysisRequest(
            analysis_type=AnalysisType.SENSITIVITY,
            field_size_acres=100.0,
            crop_type="corn",
            expected_yield_bu_per_acre=180.0,
            crop_price_per_bu=5.50,
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "rate_lbs_per_acre": 150
                }
            ],
            created_by="test_user"
        )
    
    @pytest.fixture
    def sample_response(self):
        """Create sample analysis response."""
        # Create a proper PriceImpactAnalysisResult
        analysis_result = PriceImpactAnalysisResult(
            analysis_id="test-analysis-123",
            analysis_type=AnalysisType.SENSITIVITY,
            baseline_metrics=PriceImpactMetrics(
                total_fertilizer_cost=1000.0,
                total_crop_revenue=5000.0,
                net_profit=4000.0,
                profit_margin_percent=80.0,
                fertilizer_cost_per_acre=10.0,
                fertilizer_cost_per_bu=2.0,
                crop_revenue_per_acre=50.0,
                price_impact_percent=0.0,
                profitability_change_percent=0.0
            ),
            confidence_score=0.85,
            data_quality_score=0.90,
            processing_time_ms=1000.0
        )
        
        return PriceImpactAnalysisResponse(
            success=True,
            analysis_result=analysis_result,
            processing_time_ms=1000.0,
            data_sources_used=["fertilizer_prices", "commodity_prices"]
        )
    
    @pytest.mark.asyncio
    async def test_save_analysis_request(self, repository, sample_request, sample_response):
        """Test saving analysis request and response."""
        analysis_id = await repository.save_analysis_request(sample_request, sample_response)
        
        assert analysis_id is not None
        
        # Verify the record was saved
        saved_record = await repository.get_analysis_by_id(sample_request.analysis_id)
        assert saved_record is not None
        assert saved_record.analysis_id == sample_request.analysis_id
        assert saved_record.success == sample_response.success
        assert saved_record.processing_time_ms == sample_response.processing_time_ms
    
    @pytest.mark.asyncio
    async def test_get_analysis_by_id(self, repository, sample_request, sample_response):
        """Test retrieving analysis by ID."""
        await repository.save_analysis_request(sample_request, sample_response)
        
        retrieved_record = await repository.get_analysis_by_id(sample_request.analysis_id)
        
        assert retrieved_record is not None
        assert retrieved_record.analysis_id == sample_request.analysis_id
        assert retrieved_record.crop_type == sample_request.crop_type
        assert retrieved_record.field_size_acres == sample_request.field_size_acres
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_farm(self, repository, sample_request, sample_response):
        """Test retrieving analyses by farm ID."""
        sample_request.farm_id = "test-farm-123"
        await repository.save_analysis_request(sample_request, sample_response)
        
        analyses = await repository.get_analyses_by_farm("test-farm-123")
        
        assert len(analyses) == 1
        assert analyses[0].farm_id == "test-farm-123"
    
    @pytest.mark.asyncio
    async def test_get_analyses_by_field(self, repository, sample_request, sample_response):
        """Test retrieving analyses by field ID."""
        sample_request.field_id = "test-field-123"
        await repository.save_analysis_request(sample_request, sample_response)
        
        analyses = await repository.get_analyses_by_field("test-field-123")
        
        assert len(analyses) == 1
        assert analyses[0].field_id == "test-field-123"
    
    @pytest.mark.asyncio
    async def test_delete_analysis(self, repository, sample_request, sample_response):
        """Test deleting analysis."""
        await repository.save_analysis_request(sample_request, sample_response)
        
        # Verify it exists
        record = await repository.get_analysis_by_id(sample_request.analysis_id)
        assert record is not None
        
        # Delete it
        success = await repository.delete_analysis(sample_request.analysis_id)
        assert success is True
        
        # Verify it's deleted
        record = await repository.get_analysis_by_id(sample_request.analysis_id)
        assert record is None
    
    @pytest.mark.asyncio
    async def test_get_analysis_statistics(self, repository, sample_request, sample_response):
        """Test getting analysis statistics."""
        # Save a successful analysis
        await repository.save_analysis_request(sample_request, sample_response)
        
        # Save a failed analysis
        failed_response = sample_response.copy()
        failed_response.success = False
        failed_response.error_message = "Test error"
        
        failed_request = sample_request.copy()
        failed_request.analysis_id = "failed-analysis-123"
        
        await repository.save_analysis_request(failed_request, failed_response)
        
        stats = await repository.get_analysis_statistics()
        
        assert stats['total_analyses'] == 2
        assert stats['successful_analyses'] == 1
        assert stats['success_rate'] == 0.5
        assert 'analysis_types' in stats


class TestAgriculturalValidation:
    """Agricultural validation tests for price impact analysis."""
    
    @pytest.mark.asyncio
    async def test_corn_belt_profitability_validation(self):
        """Test profitability calculations for corn belt conditions."""
        service = PriceImpactAnalysisService()
        
        # Typical corn belt scenario
        request = PriceImpactAnalysisRequest(
            analysis_type=AnalysisType.SENSITIVITY,
            field_size_acres=160.0,  # Quarter section
            crop_type="corn",
            expected_yield_bu_per_acre=200.0,  # Good corn yield
            crop_price_per_bu=5.00,  # Typical corn price
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "rate_lbs_per_acre": 180,  # Typical N rate
                    "fertilizer_type": "nitrogen",
                    "n_content": 46
                },
                {
                    "product": "dap",
                    "rate_lbs_per_acre": 80,  # Typical P rate
                    "fertilizer_type": "phosphorus",
                    "p_content": 46
                }
            ],
            created_by="agricultural_validator"
        )
        
        mock_market_data = {
            'fertilizer_prices': {
                'urea': MagicMock(price_per_unit=500.0, unit_conversion_factor=2000),
                'dap': MagicMock(price_per_unit=600.0, unit_conversion_factor=2000)
            },
            'commodity_prices': {'corn': MagicMock(price_per_unit=5.00, unit_conversion_factor=1)},
            'price_trends': {},
            'volatility_metrics': {}
        }
        
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service.analyze_price_impact(request)
            
            assert result.success is True
            assert result.analysis_result is not None
            
            baseline_metrics = result.analysis_result.baseline_metrics
            
            # Validate realistic profitability ranges
            assert baseline_metrics.profit_margin_percent > 10, "Profit margin should be reasonable for corn"
            assert baseline_metrics.fertilizer_cost_per_acre > 50, "Fertilizer cost should be realistic"
            assert baseline_metrics.fertilizer_cost_per_acre < 200, "Fertilizer cost should not be excessive"
            assert baseline_metrics.crop_revenue_per_acre > 800, "Crop revenue should be realistic"
    
    @pytest.mark.asyncio
    async def test_fertilizer_rate_sensitivity_validation(self):
        """Test that fertilizer rate changes produce realistic sensitivity."""
        service = PriceImpactAnalysisService()
        
        request = PriceImpactAnalysisRequest(
            analysis_type=AnalysisType.SENSITIVITY,
            field_size_acres=100.0,
            crop_type="soybeans",
            expected_yield_bu_per_acre=50.0,
            crop_price_per_bu=12.00,
            fertilizer_requirements=[
                {
                    "product": "potash",
                    "rate_lbs_per_acre": 100,
                    "fertilizer_type": "potassium",
                    "k_content": 60
                }
            ],
            price_change_percentages=[-50, -25, 0, 25, 50],
            created_by="agricultural_validator"
        )
        
        mock_market_data = {
            'fertilizer_prices': {
                'potash': MagicMock(price_per_unit=400.0, unit_conversion_factor=2000)
            },
            'commodity_prices': {'soybeans': MagicMock(price_per_unit=12.00, unit_conversion_factor=1)},
            'price_trends': {},
            'volatility_metrics': {}
        }
        
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service.analyze_price_impact(request)
            
            assert result.success is True
            sensitivity_results = result.analysis_result.sensitivity_results
            
            # Find fertilizer price sensitivity
            fertilizer_sensitivity = next(
                (s for s in sensitivity_results if s.parameter_name == "fertilizer_price"),
                None
            )
            
            assert fertilizer_sensitivity is not None
            
            # Validate sensitivity makes agricultural sense
            # Higher fertilizer prices should reduce profitability
            baseline_idx = fertilizer_sensitivity.parameter_values.index(0)
            baseline_impact = fertilizer_sensitivity.impact_values[baseline_idx]
            
            # Find 25% price increase
            high_price_idx = fertilizer_sensitivity.parameter_values.index(25)
            high_price_impact = fertilizer_sensitivity.impact_values[high_price_idx]
            
            assert high_price_impact < baseline_impact, "Higher fertilizer prices should reduce profitability"
            
            # Validate elasticity is reasonable (not too extreme)
            assert abs(fertilizer_sensitivity.elasticity) < 5.0, "Elasticity should be reasonable"
    
    @pytest.mark.asyncio
    async def test_scenario_analysis_agricultural_validity(self):
        """Test that scenario analysis produces agriculturally valid results."""
        service = PriceImpactAnalysisService()
        
        request = PriceImpactAnalysisRequest(
            analysis_type=AnalysisType.SCENARIO,
            field_size_acres=80.0,
            crop_type="wheat",
            expected_yield_bu_per_acre=70.0,
            crop_price_per_bu=7.00,
            fertilizer_requirements=[
                {
                    "product": "ammonium_nitrate",
                    "rate_lbs_per_acre": 120,
                    "fertilizer_type": "nitrogen",
                    "n_content": 34
                }
            ],
            created_by="agricultural_validator"
        )
        
        mock_market_data = {
            'fertilizer_prices': {
                'ammonium_nitrate': MagicMock(price_per_unit=450.0, unit_conversion_factor=2000)
            },
            'commodity_prices': {'wheat': MagicMock(price_per_unit=7.00, unit_conversion_factor=1)},
            'price_trends': {},
            'volatility_metrics': {}
        }
        
        with patch.object(service, '_get_market_data', return_value=mock_market_data):
            result = await service.analyze_price_impact(request)
            
            assert result.success is True
            scenarios = result.analysis_result.scenarios
            
            # Validate scenario results
            for scenario in scenarios:
                assert scenario['net_profit'] is not None
                assert scenario['profit_change_percent'] is not None
                
                # Optimistic scenario should be most profitable
                if scenario['scenario_type'] == 'optimistic':
                    assert scenario['net_profit'] > 0, "Optimistic scenario should be profitable"
                
                # Pessimistic scenario might be less profitable but should be realistic
                if scenario['scenario_type'] == 'pessimistic':
                    # Should not be catastrophically unprofitable
                    assert scenario['net_profit'] > -10000, "Pessimistic scenario should not be catastrophically unprofitable"