"""
Tests for Variety Economic Analysis Service

Comprehensive tests for the economic viability scoring system including:
- Economic analysis calculations
- Market price integration
- Cost factor analysis
- Government program integration
- Risk assessment
- API endpoint functionality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from decimal import Decimal

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.variety_economics import (
    VarietyEconomicAnalysisService,
    EconomicAnalysisResult,
    CostFactors,
    RevenueFactors
)
from src.models.crop_variety_models import (
    EnhancedCropVariety,
    MarketAttributes,
    YieldPotential
)
from src.models.service_models import ConfidenceLevel


class TestVarietyEconomicAnalysisService:
    """Test suite for VarietyEconomicAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return VarietyEconomicAnalysisService()
    
    @pytest.fixture
    def mock_variety(self):
        """Create mock variety for testing."""
        return EnhancedCropVariety(
            id="test_variety_001",
            variety_name="Test Corn Variety",
            crop_name="corn",
            yield_potential=YieldPotential(
                expected_yield_per_acre=180.0,
                relative_yield_potential=1.1
            ),
            market_attributes=MarketAttributes(
                premium_potential=4,
                market_class="food_grade"
            ),
            disease_resistance_profile=None,
            risk_level="medium"
        )
    
    @pytest.fixture
    def regional_context(self):
        """Create regional context for testing."""
        return {
            "region": "Iowa",
            "climate_zone": "5a",
            "soil_type": "clay_loam",
            "yield_multiplier": 1.0,
            "price_volatility": 0.15,
            "market_data_source": "test"
        }
    
    @pytest.fixture
    def farmer_preferences(self):
        """Create farmer preferences for testing."""
        return {
            "risk_tolerance": "medium",
            "profit_priority": "high",
            "sustainability_goals": True
        }
    
    @pytest.mark.asyncio
    async def test_analyze_variety_economics_success(self, service, mock_variety, regional_context, farmer_preferences):
        """Test successful economic analysis."""
        
        # Mock market data
        with patch.object(service, '_get_market_data', return_value={
            'price_per_unit': 4.25,
            'volatility': 0.15,
            'source': 'test',
            'confidence': 0.9
        }):
            result = await service.analyze_variety_economics(
                mock_variety, regional_context, farmer_preferences
            )
        
        # Verify result structure
        assert isinstance(result, EconomicAnalysisResult)
        assert result.variety_id == "test_variety_001"
        assert result.variety_name == "Test Corn Variety"
        
        # Verify financial metrics
        assert isinstance(result.net_present_value, float)
        assert isinstance(result.internal_rate_of_return, float)
        assert isinstance(result.payback_period_years, float)
        assert isinstance(result.break_even_yield, float)
        assert isinstance(result.break_even_price, float)
        
        # Verify cost analysis
        assert result.total_seed_cost_per_acre > 0
        assert result.total_input_costs_per_acre > 0
        assert result.total_operating_costs_per_acre > 0
        
        # Verify revenue analysis
        assert result.expected_revenue_per_acre > 0
        assert isinstance(result.profit_margin_percent, float)
        
        # Verify risk analysis
        assert isinstance(result.risk_adjusted_return, float)
        assert 0 <= result.volatility_score <= 1
        assert 0 <= result.downside_risk <= 1
        
        # Verify economic viability score
        assert 0 <= result.economic_viability_score <= 1
        
        # Verify confidence level
        assert isinstance(result.confidence_level, ConfidenceLevel)
        
        # Verify metadata
        assert isinstance(result.analysis_date, datetime)
        assert result.market_data_source == "test"
        assert isinstance(result.assumptions_used, dict)
    
    @pytest.mark.asyncio
    async def test_cost_factors_calculation(self, service, mock_variety, regional_context):
        """Test cost factors calculation."""
        
        cost_factors = await service._calculate_cost_factors(mock_variety, regional_context)
        
        assert isinstance(cost_factors, CostFactors)
        assert cost_factors.seed_cost_per_unit > 0
        assert cost_factors.seeding_rate_per_acre > 0
        assert cost_factors.fertilizer_cost_per_acre > 0
        assert cost_factors.pesticide_cost_per_acre > 0
        assert cost_factors.fuel_cost_per_acre > 0
        assert cost_factors.labor_cost_per_acre > 0
        assert cost_factors.equipment_cost_per_acre > 0
        assert cost_factors.insurance_cost_per_acre > 0
        assert cost_factors.other_inputs_cost_per_acre > 0
        
        # Test total cost calculation
        total_cost = cost_factors.total_cost_per_acre()
        assert total_cost > 0
        assert total_cost == (
            cost_factors.seed_cost_per_unit * cost_factors.seeding_rate_per_acre +
            cost_factors.fertilizer_cost_per_acre +
            cost_factors.pesticide_cost_per_acre +
            cost_factors.fuel_cost_per_acre +
            cost_factors.labor_cost_per_acre +
            cost_factors.equipment_cost_per_acre +
            cost_factors.insurance_cost_per_acre +
            cost_factors.other_inputs_cost_per_acre
        )
    
    @pytest.mark.asyncio
    async def test_revenue_factors_calculation(self, service, mock_variety, regional_context):
        """Test revenue factors calculation."""
        
        market_data = {
            'price_per_unit': 4.25,
            'volatility': 0.15,
            'source': 'test',
            'confidence': 0.9
        }
        
        with patch.object(service, '_calculate_expected_yield', return_value=180.0):
            with patch.object(service, '_calculate_government_subsidies', return_value=25.0):
                revenue_factors = await service._calculate_revenue_factors(
                    mock_variety, regional_context, market_data
                )
        
        assert isinstance(revenue_factors, RevenueFactors)
        assert revenue_factors.expected_yield_per_acre == 180.0
        assert revenue_factors.market_price_per_unit == 4.25
        assert revenue_factors.government_subsidies_per_acre == 25.0
        
        # Test total revenue calculation
        total_revenue = revenue_factors.total_revenue_per_acre()
        assert total_revenue > 0
        assert total_revenue == (180.0 * 4.25) + 25.0  # Base revenue + subsidies
    
    def test_npv_calculation(self, service):
        """Test NPV calculation."""
        cost_factors = CostFactors(
            seed_cost_per_unit=0.35,
            seeding_rate_per_acre=32000,
            fertilizer_cost_per_acre=120.0,
            pesticide_cost_per_acre=45.0,
            fuel_cost_per_acre=25.0,
            labor_cost_per_acre=15.0,
            equipment_cost_per_acre=35.0,
            insurance_cost_per_acre=12.0,
            other_inputs_cost_per_acre=20.0
        )
        
        revenue_factors = RevenueFactors(
            expected_yield_per_acre=180.0,
            market_price_per_unit=4.25,
            government_subsidies_per_acre=25.0
        )
        
        npv = service._calculate_npv(cost_factors, revenue_factors)
        
        assert isinstance(npv, float)
        # NPV should be positive for profitable scenario
        assert npv > 0
    
    def test_irr_calculation(self, service):
        """Test IRR calculation."""
        cost_factors = CostFactors(
            seed_cost_per_unit=0.35,
            seeding_rate_per_acre=32000,
            fertilizer_cost_per_acre=120.0,
            pesticide_cost_per_acre=45.0,
            fuel_cost_per_acre=25.0,
            labor_cost_per_acre=15.0,
            equipment_cost_per_acre=35.0,
            insurance_cost_per_acre=12.0,
            other_inputs_cost_per_acre=20.0
        )
        
        revenue_factors = RevenueFactors(
            expected_yield_per_acre=180.0,
            market_price_per_unit=4.25,
            government_subsidies_per_acre=25.0
        )
        
        irr = service._calculate_irr(cost_factors, revenue_factors)
        
        assert isinstance(irr, float)
        assert irr >= 0
        assert irr <= 50.0  # Capped at 50%
    
    def test_payback_period_calculation(self, service):
        """Test payback period calculation."""
        cost_factors = CostFactors(
            seed_cost_per_unit=0.35,
            seeding_rate_per_acre=32000,
            fertilizer_cost_per_acre=120.0,
            pesticide_cost_per_acre=45.0,
            fuel_cost_per_acre=25.0,
            labor_cost_per_acre=15.0,
            equipment_cost_per_acre=35.0,
            insurance_cost_per_acre=12.0,
            other_inputs_cost_per_acre=20.0
        )
        
        revenue_factors = RevenueFactors(
            expected_yield_per_acre=180.0,
            market_price_per_unit=4.25,
            government_subsidies_per_acre=25.0
        )
        
        payback_period = service._calculate_payback_period(cost_factors, revenue_factors)
        
        assert isinstance(payback_period, float)
        assert payback_period > 0
        assert payback_period < 10.0  # Should be reasonable payback period
    
    def test_break_even_calculations(self, service):
        """Test break-even calculations."""
        cost_factors = CostFactors(
            seed_cost_per_unit=0.35,
            seeding_rate_per_acre=32000,
            fertilizer_cost_per_acre=120.0,
            pesticide_cost_per_acre=45.0,
            fuel_cost_per_acre=25.0,
            labor_cost_per_acre=15.0,
            equipment_cost_per_acre=35.0,
            insurance_cost_per_acre=12.0,
            other_inputs_cost_per_acre=20.0
        )
        
        revenue_factors = RevenueFactors(
            expected_yield_per_acre=180.0,
            market_price_per_unit=4.25,
            government_subsidies_per_acre=25.0
        )
        
        market_data = {'price_per_unit': 4.25}
        
        break_even_yield = service._calculate_break_even_yield(cost_factors, market_data)
        break_even_price = service._calculate_break_even_price(cost_factors, revenue_factors)
        
        assert isinstance(break_even_yield, float)
        assert isinstance(break_even_price, float)
        assert break_even_yield > 0
        assert break_even_price > 0
    
    def test_risk_calculations(self, service):
        """Test risk calculation methods."""
        revenue_factors = RevenueFactors(
            expected_yield_per_acre=180.0,
            market_price_per_unit=4.25,
            government_subsidies_per_acre=25.0
        )
        
        regional_context = {'price_volatility': 0.15}
        market_data = {'volatility': 0.15}
        
        risk_adjusted_return = service._calculate_risk_adjusted_return(revenue_factors, regional_context)
        volatility_score = service._calculate_volatility_score(market_data)
        
        assert isinstance(risk_adjusted_return, float)
        assert isinstance(volatility_score, float)
        assert 0 <= volatility_score <= 1
    
    @pytest.mark.asyncio
    async def test_government_subsidies_calculation(self, service, mock_variety, regional_context):
        """Test government subsidies calculation."""
        
        subsidies = await service._calculate_government_subsidies(mock_variety, regional_context)
        
        assert isinstance(subsidies, float)
        assert subsidies >= 0
    
    def test_economic_viability_score_calculation(self, service):
        """Test economic viability score calculation."""
        
        npv = 1000.0
        irr = 15.0
        payback_period = 2.5
        risk_adjusted_return = 800.0
        volatility_score = 0.8
        
        score = service._calculate_economic_viability_score(
            npv, irr, payback_period, risk_adjusted_return, volatility_score
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_confidence_level_determination(self, service, mock_variety, regional_context):
        """Test confidence level determination."""
        
        market_data = {'confidence': 0.9, 'source': 'test'}
        
        confidence_level = service._determine_confidence_level(market_data, mock_variety, regional_context)
        
        assert isinstance(confidence_level, ConfidenceLevel)
        assert confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
    
    @pytest.mark.asyncio
    async def test_compare_varieties_economics(self, service, regional_context, farmer_preferences):
        """Test comparative economic analysis."""
        
        # Create multiple mock varieties
        varieties = [
            EnhancedCropVariety(
                id="variety_001",
                variety_name="Variety 1",
                crop_name="corn",
                yield_potential=YieldPotential(expected_yield_per_acre=180.0, relative_yield_potential=1.1),
                market_attributes=MarketAttributes(premium_potential=4),
                risk_level="medium"
            ),
            EnhancedCropVariety(
                id="variety_002", 
                variety_name="Variety 2",
                crop_name="corn",
                yield_potential=YieldPotential(expected_yield_per_acre=175.0, relative_yield_potential=1.0),
                market_attributes=MarketAttributes(premium_potential=3),
                risk_level="low"
            )
        ]
        
        # Mock market data
        with patch.object(service, '_get_market_data', return_value={
            'price_per_unit': 4.25,
            'volatility': 0.15,
            'source': 'test',
            'confidence': 0.9
        }):
            results = await service.compare_varieties_economics(
                varieties, regional_context, farmer_preferences
            )
        
        assert isinstance(results, list)
        assert len(results) == 2
        
        # Results should be sorted by economic viability score (descending)
        for i in range(len(results) - 1):
            assert results[i][1].economic_viability_score >= results[i + 1][1].economic_viability_score
    
    def test_cost_factor_adjustments(self, service):
        """Test cost factor adjustment methods."""
        
        # Test seed cost adjustment
        base_cost = 0.35
        variety = EnhancedCropVariety(
            id="test",
            variety_name="Test",
            crop_name="corn",
            relative_seed_cost="premium"
        )
        
        adjusted_cost = service._adjust_seed_cost(variety, base_cost)
        assert adjusted_cost > base_cost  # Premium should increase cost
        
        # Test pesticide cost adjustment
        variety.disease_resistance_profile = MagicMock()  # Mock resistance profile
        adjusted_pesticide_cost = service._adjust_pesticide_cost(variety, 45.0)
        assert isinstance(adjusted_pesticide_cost, float)
        assert adjusted_pesticide_cost > 0
    
    def test_default_cost_factors(self, service):
        """Test default cost factors for different crops."""
        
        # Test corn cost factors
        corn_costs = service.default_cost_factors['corn']
        assert isinstance(corn_costs, CostFactors)
        assert corn_costs.seed_cost_per_unit > 0
        assert corn_costs.seeding_rate_per_acre > 0
        
        # Test soybean cost factors
        soybean_costs = service.default_cost_factors['soybean']
        assert isinstance(soybean_costs, CostFactors)
        assert soybean_costs.seed_cost_per_unit > 0
        assert soybean_costs.seeding_rate_per_acre > 0
        
        # Test wheat cost factors
        wheat_costs = service.default_cost_factors['wheat']
        assert isinstance(wheat_costs, CostFactors)
        assert wheat_costs.seed_cost_per_unit > 0
        assert wheat_costs.seeding_rate_per_acre > 0
    
    def test_government_programs_data(self, service):
        """Test government programs data structure."""
        
        # Test corn programs
        corn_programs = service.government_programs['corn']
        assert isinstance(corn_programs, dict)
        assert 'price_loss_coverage' in corn_programs
        assert 'agricultural_risk_coverage' in corn_programs
        
        # Test soybean programs
        soybean_programs = service.government_programs['soybean']
        assert isinstance(soybean_programs, dict)
        assert 'price_loss_coverage' in soybean_programs
        
        # Test wheat programs
        wheat_programs = service.government_programs['wheat']
        assert isinstance(wheat_programs, dict)
        assert 'price_loss_coverage' in wheat_programs


class TestEconomicAnalysisIntegration:
    """Integration tests for economic analysis with variety recommendation service."""
    
    @pytest.mark.asyncio
    async def test_variety_recommendation_service_integration(self):
        """Test integration with variety recommendation service."""
        
        try:
            from ..services.variety_recommendation_service import VarietyRecommendationService
            from ..models.crop_taxonomy_models import ComprehensiveCropData
            
            # Create service instance
            service = VarietyRecommendationService()
            
            # Verify economic analysis service is initialized
            assert hasattr(service, 'economic_analysis_service')
            assert service.economic_analysis_service is not None
            
            # Verify economic viability is in scoring weights
            assert 'economic_viability' in service.scoring_weights
            assert service.scoring_weights['economic_viability'] > 0
            
            # Verify economic viability scoring method exists
            assert hasattr(service, '_score_economic_viability')
            
        except ImportError:
            pytest.skip("Variety recommendation service not available for integration test")
    
    @pytest.mark.asyncio
    async def test_api_endpoints_availability(self):
        """Test that API endpoints are properly defined."""
        
        try:
            from ..api.economic_analysis_routes import router
            
            # Verify router is created
            assert router is not None
            assert router.prefix == "/api/v1/economic-analysis"
            
            # Verify key endpoints exist
            routes = [route.path for route in router.routes]
            assert "/analyze" in routes
            assert "/compare" in routes
            assert "/score" in routes
            assert "/health" in routes
            
        except ImportError:
            pytest.skip("Economic analysis API routes not available for integration test")


class TestEconomicAnalysisPerformance:
    """Performance tests for economic analysis service."""
    
    @pytest.mark.asyncio
    async def test_analysis_performance(self):
        """Test that economic analysis completes within reasonable time."""
        import time
        
        service = VarietyEconomicAnalysisService()
        
        variety = EnhancedCropVariety(
            id="perf_test",
            variety_name="Performance Test Variety",
            crop_name="corn",
            yield_potential=YieldPotential(expected_yield_per_acre=180.0),
            market_attributes=MarketAttributes(premium_potential=3)
        )
        
        regional_context = {
            "region": "Iowa",
            "climate_zone": "5a",
            "soil_type": "clay_loam"
        }
        
        start_time = time.time()
        
        result = await service.analyze_variety_economics(variety, regional_context)
        
        elapsed_time = time.time() - start_time
        
        # Analysis should complete within 5 seconds
        assert elapsed_time < 5.0
        assert result is not None
        assert isinstance(result, EconomicAnalysisResult)
    
    @pytest.mark.asyncio
    async def test_batch_analysis_performance(self):
        """Test performance of batch economic analysis."""
        import time
        
        service = VarietyEconomicAnalysisService()
        
        # Create multiple varieties
        varieties = []
        for i in range(5):
            variety = EnhancedCropVariety(
                id=f"batch_test_{i}",
                variety_name=f"Batch Test Variety {i}",
                crop_name="corn",
                yield_potential=YieldPotential(expected_yield_per_acre=180.0 + i),
                market_attributes=MarketAttributes(premium_potential=3)
            )
            varieties.append(variety)
        
        regional_context = {
            "region": "Iowa",
            "climate_zone": "5a",
            "soil_type": "clay_loam"
        }
        
        start_time = time.time()
        
        results = await service.compare_varieties_economics(varieties, regional_context)
        
        elapsed_time = time.time() - start_time
        
        # Batch analysis should complete within 10 seconds
        assert elapsed_time < 10.0
        assert len(results) == 5
        assert all(isinstance(result[1], EconomicAnalysisResult) for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])