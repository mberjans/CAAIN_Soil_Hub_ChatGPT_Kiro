"""
Comprehensive test suite for crop diversification and risk management functionality.

Tests cover all aspects of the diversification service including:
- Portfolio optimization algorithms
- Risk assessment calculations
- Market risk analysis
- Economic impact assessment
- API endpoint functionality
- Data validation and error handling
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

from src.models.crop_diversification_models import (
    DiversificationRequest,
    DiversificationResponse,
    DiversificationRecommendation,
    DiversificationPortfolio,
    CropRiskProfile,
    MarketRiskAssessment,
    RiskLevel,
    DiversificationStrategy,
    CropCategory,
    DroughtToleranceLevel,
    MarketRiskType
)
from src.services.crop_diversification_service import CropDiversificationService

logger = logging.getLogger(__name__)

class TestCropDiversificationService:
    """Test suite for CropDiversificationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return CropDiversificationService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample diversification request."""
        return DiversificationRequest(
            farm_id=uuid4(),
            field_ids=[uuid4(), uuid4()],
            total_acres=100.0,
            current_crops=["corn", "soybeans"],
            risk_tolerance=RiskLevel.MODERATE,
            diversification_goals=["drought_resilience", "soil_health"],
            budget_constraints=Decimal("5000.00"),
            equipment_available=["tractor", "planter"],
            irrigation_capacity=400.0,
            soil_types=["clay_loam", "sandy_loam"],
            climate_zone="6a",
            market_preferences=["local", "organic"],
            sustainability_goals=["soil_health", "water_conservation"]
        )
    
    @pytest.fixture
    def sample_portfolio(self):
        """Create sample diversification portfolio."""
        crops = [
            CropRiskProfile(
                crop_id=uuid4(),
                crop_name="corn",
                crop_category=CropCategory.GRAINS,
                drought_tolerance=DroughtToleranceLevel.MODERATE,
                water_requirement_mm=500,
                yield_stability_score=0.7,
                market_price_volatility=0.6,
                disease_susceptibility=0.5,
                pest_susceptibility=0.6,
                soil_health_contribution=0.3,
                nitrogen_fixation=False,
                root_depth_cm=120,
                maturity_days=120
            ),
            CropRiskProfile(
                crop_id=uuid4(),
                crop_name="soybeans",
                crop_category=CropCategory.LEGUMES,
                drought_tolerance=DroughtToleranceLevel.MODERATE,
                water_requirement_mm=450,
                yield_stability_score=0.8,
                market_price_volatility=0.7,
                disease_susceptibility=0.4,
                pest_susceptibility=0.5,
                soil_health_contribution=0.8,
                nitrogen_fixation=True,
                root_depth_cm=100,
                maturity_days=110
            )
        ]
        
        return DiversificationPortfolio(
            portfolio_id=uuid4(),
            farm_id=uuid4(),
            portfolio_name="Test Portfolio",
            crops=crops,
            total_acres=100.0,
            crop_allocation={"corn": 60.0, "soybeans": 40.0},
            diversification_index=0.5,
            risk_score=0.65,
            expected_yield=150.0,
            expected_revenue=Decimal("600.00"),
            water_efficiency_score=0.7,
            soil_health_score=0.6
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert not service.initialized
        
        await service.initialize()
        assert service.initialized
        
        await service.cleanup()
        assert not service.initialized
    
    @pytest.mark.asyncio
    async def test_analyze_diversification_options(self, service, sample_request):
        """Test comprehensive diversification analysis."""
        await service.initialize()
        
        response = await service.analyze_diversification_options(sample_request)
        
        assert isinstance(response, DiversificationResponse)
        assert response.farm_id == sample_request.farm_id
        assert response.request_id is not None
        assert response.analysis_date is not None
        assert isinstance(response.current_risk_assessment, dict)
        assert isinstance(response.diversification_recommendations, list)
        assert isinstance(response.risk_comparison, dict)
        assert isinstance(response.economic_analysis, dict)
        assert isinstance(response.implementation_priority, list)
        assert isinstance(response.monitoring_plan, dict)
        assert response.next_review_date is not None
        assert 0 <= response.confidence_score <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_optimize_crop_portfolio(self, service, sample_request):
        """Test crop portfolio optimization."""
        await service.initialize()
        
        portfolio = await service.optimize_crop_portfolio(sample_request)
        
        assert isinstance(portfolio, DiversificationPortfolio)
        assert portfolio.farm_id == sample_request.farm_id
        assert portfolio.total_acres == sample_request.total_acres
        assert isinstance(portfolio.crops, list)
        assert len(portfolio.crops) > 0
        assert isinstance(portfolio.crop_allocation, dict)
        assert abs(sum(portfolio.crop_allocation.values()) - 100.0) < 0.01
        assert 0 <= portfolio.diversification_index <= 1
        assert 0 <= portfolio.risk_score <= 1
        assert portfolio.expected_yield > 0
        assert portfolio.expected_revenue > 0
        assert 0 <= portfolio.water_efficiency_score <= 1
        assert 0 <= portfolio.soil_health_score <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_assess_drought_risk_reduction(self, service, sample_portfolio):
        """Test drought risk reduction assessment."""
        await service.initialize()
        
        assessment = await service.assess_drought_risk_reduction(sample_portfolio)
        
        assert isinstance(assessment, dict)
        assert "water_efficiency_score" in assessment
        assert "yield_stability_score" in assessment
        assert "soil_health_score" in assessment
        assert "temporal_risk_score" in assessment
        assert "overall_drought_resilience" in assessment
        assert "risk_reduction_percent" in assessment
        assert "recommendations" in assessment
        
        # Validate score ranges
        for score_key in ["water_efficiency_score", "yield_stability_score", "soil_health_score", "temporal_risk_score", "overall_drought_resilience"]:
            assert 0 <= assessment[score_key] <= 1
        
        assert 0 <= assessment["risk_reduction_percent"] <= 100
        assert isinstance(assessment["recommendations"], list)
        
        await service.cleanup()
    
    def test_build_crop_database(self, service):
        """Test crop database building."""
        database = service._build_crop_database()
        
        assert isinstance(database, dict)
        assert len(database) > 0
        
        # Test required crops are present
        required_crops = ["corn", "soybeans", "wheat", "sorghum"]
        for crop in required_crops:
            assert crop in database
            assert isinstance(database[crop], dict)
            
            # Validate crop data structure
            crop_data = database[crop]
            assert "category" in crop_data
            assert "drought_tolerance" in crop_data
            assert "water_requirement_mm" in crop_data
            assert "yield_stability_score" in crop_data
            assert "market_price_volatility" in crop_data
            assert "disease_susceptibility" in crop_data
            assert "pest_susceptibility" in crop_data
            assert "soil_health_contribution" in crop_data
            assert "nitrogen_fixation" in crop_data
            assert "root_depth_cm" in crop_data
            assert "maturity_days" in crop_data
            
            # Validate score ranges
            assert 0 <= crop_data["yield_stability_score"] <= 1
            assert 0 <= crop_data["market_price_volatility"] <= 1
            assert 0 <= crop_data["disease_susceptibility"] <= 1
            assert 0 <= crop_data["pest_susceptibility"] <= 1
            assert 0 <= crop_data["soil_health_contribution"] <= 1
            assert crop_data["water_requirement_mm"] > 0
            assert crop_data["root_depth_cm"] > 0
            assert crop_data["maturity_days"] > 0
    
    def test_build_compatibility_matrix(self, service):
        """Test compatibility matrix building."""
        matrix = service._build_compatibility_matrix()
        
        assert isinstance(matrix, CropCompatibilityMatrix)
        assert isinstance(matrix.crop_pairs, dict)
        assert isinstance(matrix.rotation_benefits, dict)
        assert isinstance(matrix.intercropping_potential, dict)
        assert isinstance(matrix.soil_health_benefits, dict)
        assert isinstance(matrix.pest_disease_interactions, dict)
        
        # Validate compatibility scores
        for pair, score in matrix.crop_pairs.items():
            assert isinstance(pair, tuple)
            assert len(pair) == 2
            assert 0 <= score <= 1
        
        # Validate soil health benefits
        for crop, score in matrix.soil_health_benefits.items():
            assert isinstance(crop, str)
            assert 0 <= score <= 1
    
    def test_build_market_risk_data(self, service):
        """Test market risk data building."""
        market_data = service._build_market_risk_data()
        
        assert isinstance(market_data, dict)
        assert len(market_data) > 0
        
        for crop_name, risk_assessment in market_data.items():
            assert isinstance(risk_assessment, MarketRiskAssessment)
            assert isinstance(risk_assessment.risk_types, list)
            assert 0 <= risk_assessment.price_volatility_score <= 1
            assert 0 <= risk_assessment.demand_stability_score <= 1
            assert 0 <= risk_assessment.supply_chain_risk_score <= 1
            assert 0 <= risk_assessment.weather_sensitivity_score <= 1
            assert 0 <= risk_assessment.policy_risk_score <= 1
            assert 0 <= risk_assessment.overall_market_risk <= 1
            assert isinstance(risk_assessment.risk_mitigation_strategies, list)
    
    def test_build_drought_tolerance_data(self, service):
        """Test drought tolerance data building."""
        tolerance_data = service._build_drought_tolerance_data()
        
        assert isinstance(tolerance_data, dict)
        
        tolerance_levels = ["very_high", "high", "moderate", "low"]
        for level in tolerance_levels:
            assert level in tolerance_data
            level_data = tolerance_data[level]
            assert isinstance(level_data, dict)
            assert "water_efficiency" in level_data
            assert "drought_recovery" in level_data
            assert "deep_rooting" in level_data
            assert "water_storage" in level_data
            
            # Validate score ranges
            for score in level_data.values():
                assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_assess_current_risk(self, service, sample_request):
        """Test current risk assessment."""
        await service.initialize()
        
        risk_assessment = await service._assess_current_risk(sample_request)
        
        assert isinstance(risk_assessment, dict)
        assert "diversification_index" in risk_assessment
        assert "drought_risk" in risk_assessment
        assert "market_risk" in risk_assessment
        assert "yield_stability" in risk_assessment
        assert "soil_health_risk" in risk_assessment
        assert "current_crops" in risk_assessment
        
        # Validate score ranges
        assert 0 <= risk_assessment["diversification_index"] <= 1
        assert 0 <= risk_assessment["drought_risk"] <= 1
        assert 0 <= risk_assessment["market_risk"] <= 1
        assert 0 <= risk_assessment["yield_stability"] <= 1
        assert 0 <= risk_assessment["soil_health_risk"] <= 1
        
        assert isinstance(risk_assessment["current_crops"], list)
        
        await service.cleanup()
    
    def test_get_drought_tolerance_score(self, service):
        """Test drought tolerance score conversion."""
        # Test all tolerance levels
        tolerance_scores = {
            DroughtToleranceLevel.VERY_HIGH: 0.9,
            DroughtToleranceLevel.HIGH: 0.8,
            DroughtToleranceLevel.MODERATE: 0.6,
            DroughtToleranceLevel.LOW: 0.4
        }
        
        for level, expected_score in tolerance_scores.items():
            score = service._get_drought_tolerance_score(level)
            assert score == expected_score
    
    @pytest.mark.asyncio
    async def test_generate_diversification_strategies(self, service, sample_request):
        """Test diversification strategy generation."""
        await service.initialize()
        
        strategies = await service._generate_diversification_strategies(sample_request)
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        
        # Should always include crop rotation
        assert DiversificationStrategy.CROP_ROTATION in strategies
        
        # Should include temporal diversification
        assert DiversificationStrategy.TEMPORAL_DIVERSIFICATION in strategies
        
        # Should include spatial diversification for multiple fields
        assert DiversificationStrategy.SPATIAL_DIVERSIFICATION in strategies
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_get_available_crops(self, service, sample_request):
        """Test available crops retrieval."""
        await service.initialize()
        
        available_crops = await service._get_available_crops(sample_request)
        
        assert isinstance(available_crops, list)
        assert len(available_crops) > 0
        
        for crop in available_crops:
            assert isinstance(crop, CropRiskProfile)
            assert crop.crop_id is not None
            assert isinstance(crop.crop_name, str)
            assert isinstance(crop.crop_category, CropCategory)
            assert isinstance(crop.drought_tolerance, DroughtToleranceLevel)
            assert crop.water_requirement_mm > 0
            assert 0 <= crop.yield_stability_score <= 1
            assert 0 <= crop.market_price_volatility <= 1
            assert 0 <= crop.disease_susceptibility <= 1
            assert 0 <= crop.pest_susceptibility <= 1
            assert 0 <= crop.soil_health_contribution <= 1
            assert isinstance(crop.nitrogen_fixation, bool)
            assert crop.root_depth_cm > 0
            assert crop.maturity_days > 0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_filter_crops_by_constraints(self, service, sample_request):
        """Test crop filtering by constraints."""
        await service.initialize()
        
        # Get available crops first
        available_crops = await service._get_available_crops(sample_request)
        
        # Filter by constraints
        filtered_crops = await service._filter_crops_by_constraints(available_crops, sample_request)
        
        assert isinstance(filtered_crops, list)
        assert len(filtered_crops) <= len(available_crops)
        
        # All filtered crops should meet constraints
        for crop in filtered_crops:
            # Check irrigation capacity constraint
            if sample_request.irrigation_capacity:
                assert crop.water_requirement_mm <= sample_request.irrigation_capacity
            
            # Check risk tolerance constraint
            if sample_request.risk_tolerance == RiskLevel.LOW:
                assert crop.market_price_volatility <= 0.7
            
            # Check sustainability goals constraint
            if "soil_health" in sample_request.sustainability_goals:
                assert crop.soil_health_contribution >= 0.5
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_calculate_diversification_scores(self, service, sample_request):
        """Test diversification score calculation."""
        await service.initialize()
        
        # Get available crops
        available_crops = await service._get_available_crops(sample_request)
        
        # Calculate scores
        scores = await service._calculate_diversification_scores(available_crops)
        
        assert isinstance(scores, dict)
        assert len(scores) == len(available_crops)
        
        for crop_name, score in scores.items():
            assert isinstance(crop_name, str)
            assert 0 <= score <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_optimize_allocation(self, service, sample_request):
        """Test crop allocation optimization."""
        await service.initialize()
        
        # Get available crops
        available_crops = await service._get_available_crops(sample_request)
        
        # Calculate scores
        scores = await service._calculate_diversification_scores(available_crops)
        
        # Optimize allocation
        allocation = await service._optimize_allocation(available_crops, scores, sample_request)
        
        assert isinstance(allocation, dict)
        assert len(allocation) > 0
        
        # Check allocation sums to 100%
        total_allocation = sum(allocation.values())
        assert abs(total_allocation - 100.0) < 0.01
        
        # Check all allocations are positive
        for crop_name, allocation_percent in allocation.items():
            assert isinstance(crop_name, str)
            assert allocation_percent > 0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_calculate_water_efficiency(self, service, sample_portfolio):
        """Test water efficiency calculation."""
        await service.initialize()
        
        efficiency = await service._calculate_water_efficiency(sample_portfolio)
        
        assert isinstance(efficiency, float)
        assert 0 <= efficiency <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_calculate_yield_stability(self, service, sample_portfolio):
        """Test yield stability calculation."""
        await service.initialize()
        
        stability = await service._calculate_yield_stability(sample_portfolio)
        
        assert isinstance(stability, float)
        assert 0 <= stability <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_calculate_soil_health_benefits(self, service, sample_portfolio):
        """Test soil health benefits calculation."""
        await service.initialize()
        
        benefits = await service._calculate_soil_health_benefits(sample_portfolio)
        
        assert isinstance(benefits, float)
        assert 0 <= benefits <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_assess_temporal_risk_distribution(self, service, sample_portfolio):
        """Test temporal risk distribution assessment."""
        await service.initialize()
        
        temporal_score = await service._assess_temporal_risk_distribution(sample_portfolio)
        
        assert isinstance(temporal_score, float)
        assert 0 <= temporal_score <= 1
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_calculate_drought_resilience(self, service):
        """Test drought resilience calculation."""
        await service.initialize()
        
        resilience = await service._calculate_drought_resilience(0.8, 0.7, 0.6, 0.5)
        
        assert isinstance(resilience, float)
        assert 0 <= resilience <= 1
        
        # Test with extreme values
        resilience_max = await service._calculate_drought_resilience(1.0, 1.0, 1.0, 1.0)
        assert resilience_max == 1.0
        
        resilience_min = await service._calculate_drought_resilience(0.0, 0.0, 0.0, 0.0)
        assert resilience_min == 0.0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_calculate_risk_reduction_percent(self, service):
        """Test risk reduction percentage calculation."""
        await service.initialize()
        
        reduction = await service._calculate_risk_reduction_percent(0.8)
        assert reduction == 80.0
        
        reduction_max = await service._calculate_risk_reduction_percent(1.0)
        assert reduction_max == 100.0
        
        reduction_min = await service._calculate_risk_reduction_percent(0.0)
        assert reduction_min == 0.0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_generate_drought_mitigation_recommendations(self, service, sample_portfolio):
        """Test drought mitigation recommendations generation."""
        await service.initialize()
        
        recommendations = await service._generate_drought_mitigation_recommendations(sample_portfolio)
        
        assert isinstance(recommendations, list)
        
        # Check for specific recommendations based on portfolio characteristics
        if sample_portfolio.water_efficiency_score < 0.7:
            assert any("drought-tolerant" in rec.lower() for rec in recommendations)
        
        if sample_portfolio.soil_health_score < 0.6:
            assert any("nitrogen-fixing" in rec.lower() for rec in recommendations)
        
        if sample_portfolio.diversification_index < 0.5:
            assert any("diversity" in rec.lower() for rec in recommendations)
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in service methods."""
        await service.initialize()
        
        # Test with invalid request
        invalid_request = DiversificationRequest(
            farm_id=uuid4(),
            field_ids=[],
            total_acres=0,  # Invalid acres
            risk_tolerance=RiskLevel.MODERATE,
            diversification_goals=[]
        )
        
        with pytest.raises(Exception):
            await service.analyze_diversification_options(invalid_request)
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_request):
        """Test performance requirements."""
        await service.initialize()
        
        import time
        start_time = time.time()
        
        # Test analysis performance
        response = await service.analyze_diversification_options(sample_request)
        
        elapsed_time = time.time() - start_time
        assert elapsed_time < 5.0, f"Analysis took {elapsed_time}s, should be under 5s"
        
        # Test portfolio optimization performance
        start_time = time.time()
        portfolio = await service.optimize_crop_portfolio(sample_request)
        elapsed_time = time.time() - start_time
        assert elapsed_time < 3.0, f"Portfolio optimization took {elapsed_time}s, should be under 3s"
        
        await service.cleanup()

class TestCropDiversificationModels:
    """Test suite for crop diversification data models."""
    
    def test_crop_risk_profile_validation(self):
        """Test CropRiskProfile validation."""
        # Valid profile
        profile = CropRiskProfile(
            crop_id=uuid4(),
            crop_name="corn",
            crop_category=CropCategory.GRAINS,
            drought_tolerance=DroughtToleranceLevel.MODERATE,
            water_requirement_mm=500,
            yield_stability_score=0.7,
            market_price_volatility=0.6,
            disease_susceptibility=0.5,
            pest_susceptibility=0.6,
            soil_health_contribution=0.3,
            nitrogen_fixation=False,
            root_depth_cm=120,
            maturity_days=120
        )
        
        assert profile.crop_name == "corn"
        assert profile.crop_category == CropCategory.GRAINS
        assert profile.drought_tolerance == DroughtToleranceLevel.MODERATE
        
        # Test validation errors
        with pytest.raises(ValueError):
            CropRiskProfile(
                crop_id=uuid4(),
                crop_name="corn",
                crop_category=CropCategory.GRAINS,
                drought_tolerance=DroughtToleranceLevel.MODERATE,
                water_requirement_mm=500,
                yield_stability_score=1.5,  # Invalid score > 1
                market_price_volatility=0.6,
                disease_susceptibility=0.5,
                pest_susceptibility=0.6,
                soil_health_contribution=0.3,
                nitrogen_fixation=False,
                root_depth_cm=120,
                maturity_days=120
            )
    
    def test_diversification_portfolio_validation(self):
        """Test DiversificationPortfolio validation."""
        crops = [
            CropRiskProfile(
                crop_id=uuid4(),
                crop_name="corn",
                crop_category=CropCategory.GRAINS,
                drought_tolerance=DroughtToleranceLevel.MODERATE,
                water_requirement_mm=500,
                yield_stability_score=0.7,
                market_price_volatility=0.6,
                disease_susceptibility=0.5,
                pest_susceptibility=0.6,
                soil_health_contribution=0.3,
                nitrogen_fixation=False,
                root_depth_cm=120,
                maturity_days=120
            )
        ]
        
        # Valid portfolio
        portfolio = DiversificationPortfolio(
            portfolio_id=uuid4(),
            farm_id=uuid4(),
            portfolio_name="Test Portfolio",
            crops=crops,
            total_acres=100.0,
            crop_allocation={"corn": 100.0},
            diversification_index=0.5,
            risk_score=0.65,
            expected_yield=150.0,
            expected_revenue=Decimal("600.00"),
            water_efficiency_score=0.7,
            soil_health_score=0.6
        )
        
        assert portfolio.total_acres == 100.0
        assert portfolio.crop_allocation["corn"] == 100.0
        
        # Test allocation validation
        with pytest.raises(ValueError):
            DiversificationPortfolio(
                portfolio_id=uuid4(),
                farm_id=uuid4(),
                portfolio_name="Test Portfolio",
                crops=crops,
                total_acres=100.0,
                crop_allocation={"corn": 60.0, "soybeans": 50.0},  # Sums to 110%
                diversification_index=0.5,
                risk_score=0.65,
                expected_yield=150.0,
                expected_revenue=Decimal("600.00"),
                water_efficiency_score=0.7,
                soil_health_score=0.6
            )
    
    def test_diversification_request_validation(self):
        """Test DiversificationRequest validation."""
        # Valid request
        request = DiversificationRequest(
            farm_id=uuid4(),
            field_ids=[uuid4()],
            total_acres=100.0,
            risk_tolerance=RiskLevel.MODERATE,
            diversification_goals=["drought_resilience"]
        )
        
        assert request.total_acres == 100.0
        assert request.risk_tolerance == RiskLevel.MODERATE
        
        # Test validation errors
        with pytest.raises(ValueError):
            DiversificationRequest(
                farm_id=uuid4(),
                field_ids=[uuid4()],
                total_acres=0,  # Invalid acres
                risk_tolerance=RiskLevel.MODERATE,
                diversification_goals=["drought_resilience"]
            )
    
    def test_market_risk_assessment_validation(self):
        """Test MarketRiskAssessment validation."""
        # Valid assessment
        assessment = MarketRiskAssessment(
            crop_id=uuid4(),
            risk_types=[MarketRiskType.PRICE_VOLATILITY],
            price_volatility_score=0.6,
            demand_stability_score=0.7,
            supply_chain_risk_score=0.5,
            weather_sensitivity_score=0.6,
            policy_risk_score=0.5,
            overall_market_risk=0.6,
            risk_mitigation_strategies=["diversification"]
        )
        
        assert assessment.price_volatility_score == 0.6
        assert assessment.overall_market_risk == 0.6
        
        # Test validation errors
        with pytest.raises(ValueError):
            MarketRiskAssessment(
                crop_id=uuid4(),
                risk_types=[MarketRiskType.PRICE_VOLATILITY],
                price_volatility_score=1.5,  # Invalid score > 1
                demand_stability_score=0.7,
                supply_chain_risk_score=0.5,
                weather_sensitivity_score=0.6,
                policy_risk_score=0.5,
                overall_market_risk=0.6,
                risk_mitigation_strategies=["diversification"]
            )

class TestCropDiversificationIntegration:
    """Integration tests for crop diversification system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_diversification_analysis(self):
        """Test complete end-to-end diversification analysis."""
        service = CropDiversificationService()
        await service.initialize()
        
        # Create comprehensive request
        request = DiversificationRequest(
            farm_id=uuid4(),
            field_ids=[uuid4(), uuid4(), uuid4()],
            total_acres=500.0,
            current_crops=["corn", "soybeans"],
            risk_tolerance=RiskLevel.MODERATE,
            diversification_goals=["drought_resilience", "soil_health", "market_diversification"],
            budget_constraints=Decimal("25000.00"),
            equipment_available=["tractor", "planter", "harvester"],
            irrigation_capacity=600.0,
            soil_types=["clay_loam", "sandy_loam", "silt_loam"],
            climate_zone="6a",
            market_preferences=["local", "organic", "export"],
            sustainability_goals=["soil_health", "water_conservation", "biodiversity"]
        )
        
        # Perform complete analysis
        response = await service.analyze_diversification_options(request)
        
        # Validate response
        assert isinstance(response, DiversificationResponse)
        assert response.farm_id == request.farm_id
        assert len(response.diversification_recommendations) > 0
        assert response.confidence_score > 0
        
        # Validate recommendations
        for recommendation in response.diversification_recommendations:
            assert isinstance(recommendation, DiversificationRecommendation)
            assert recommendation.farm_id == request.farm_id
            assert recommendation.risk_reduction_percent >= 0
            assert recommendation.yield_stability_improvement >= 0
            assert recommendation.water_savings_percent >= 0
            assert recommendation.soil_health_improvement >= 0
            assert recommendation.implementation_cost >= 0
            assert recommendation.confidence_score > 0
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_portfolio_optimization_with_constraints(self):
        """Test portfolio optimization with various constraints."""
        service = CropDiversificationService()
        await service.initialize()
        
        # Test different risk tolerance levels
        risk_levels = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH]
        
        for risk_level in risk_levels:
            request = DiversificationRequest(
                farm_id=uuid4(),
                field_ids=[uuid4()],
                total_acres=100.0,
                risk_tolerance=risk_level,
                diversification_goals=["drought_resilience"]
            )
            
            portfolio = await service.optimize_crop_portfolio(request)
            
            assert isinstance(portfolio, DiversificationPortfolio)
            assert portfolio.total_acres == request.total_acres
            
            # Validate risk tolerance impact
            if risk_level == RiskLevel.LOW:
                # Should favor stable crops
                assert portfolio.risk_score <= 0.7
            elif risk_level == RiskLevel.HIGH:
                # Can accept higher risk for potential returns
                assert portfolio.risk_score <= 0.9
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_drought_resilience_scoring(self):
        """Test drought resilience scoring across different portfolios."""
        service = CropDiversificationService()
        await service.initialize()
        
        # Create portfolios with different characteristics
        drought_tolerant_crops = [
            CropRiskProfile(
                crop_id=uuid4(),
                crop_name="sorghum",
                crop_category=CropCategory.GRAINS,
                drought_tolerance=DroughtToleranceLevel.VERY_HIGH,
                water_requirement_mm=350,
                yield_stability_score=0.8,
                market_price_volatility=0.6,
                disease_susceptibility=0.3,
                pest_susceptibility=0.3,
                soil_health_contribution=0.5,
                nitrogen_fixation=False,
                root_depth_cm=180,
                maturity_days=90
            )
        ]
        
        drought_sensitive_crops = [
            CropRiskProfile(
                crop_id=uuid4(),
                crop_name="corn",
                crop_category=CropCategory.GRAINS,
                drought_tolerance=DroughtToleranceLevel.LOW,
                water_requirement_mm=600,
                yield_stability_score=0.6,
                market_price_volatility=0.7,
                disease_susceptibility=0.6,
                pest_susceptibility=0.7,
                soil_health_contribution=0.3,
                nitrogen_fixation=False,
                root_depth_cm=100,
                maturity_days=120
            )
        ]
        
        # Create portfolios
        drought_tolerant_portfolio = DiversificationPortfolio(
            portfolio_id=uuid4(),
            farm_id=uuid4(),
            portfolio_name="Drought Tolerant Portfolio",
            crops=drought_tolerant_crops,
            total_acres=100.0,
            crop_allocation={"sorghum": 100.0},
            diversification_index=0.3,
            risk_score=0.4,
            expected_yield=120.0,
            expected_revenue=Decimal("480.00"),
            water_efficiency_score=0.9,
            soil_health_score=0.5
        )
        
        drought_sensitive_portfolio = DiversificationPortfolio(
            portfolio_id=uuid4(),
            farm_id=uuid4(),
            portfolio_name="Drought Sensitive Portfolio",
            crops=drought_sensitive_crops,
            total_acres=100.0,
            crop_allocation={"corn": 100.0},
            diversification_index=0.1,
            risk_score=0.8,
            expected_yield=150.0,
            expected_revenue=Decimal("600.00"),
            water_efficiency_score=0.4,
            soil_health_score=0.3
        )
        
        # Assess drought resilience
        tolerant_assessment = await service.assess_drought_risk_reduction(drought_tolerant_portfolio)
        sensitive_assessment = await service.assess_drought_risk_reduction(drought_sensitive_portfolio)
        
        # Drought tolerant portfolio should have higher resilience
        assert tolerant_assessment["overall_drought_resilience"] > sensitive_assessment["overall_drought_resilience"]
        assert tolerant_assessment["water_efficiency_score"] > sensitive_assessment["water_efficiency_score"]
        assert tolerant_assessment["risk_reduction_percent"] > sensitive_assessment["risk_reduction_percent"]
        
        await service.cleanup()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])