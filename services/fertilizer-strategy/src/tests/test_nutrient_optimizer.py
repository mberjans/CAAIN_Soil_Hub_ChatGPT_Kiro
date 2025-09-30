"""
Comprehensive tests for multi-nutrient optimization service.

This module provides tests for:
- Multi-nutrient optimization functionality
- Nutrient interaction modeling
- Constraint handling
- Economic analysis
- Risk assessment
- API endpoint functionality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from uuid import uuid4, UUID
import numpy as np

from ..services.nutrient_optimizer import (
    MultiNutrientOptimizer,
    NutrientOptimizationRequest,
    NutrientOptimizationResult,
    NutrientType,
    SoilTestData,
    CropRequirement,
    EnvironmentalLimit,
    InteractionType
)
from ..models.nutrient_optimization_models import (
    OptimizationRequestModel,
    SoilTestModel,
    CropRequirementModel,
    EnvironmentalLimitModel
)


class TestMultiNutrientOptimizer:
    """Test suite for MultiNutrientOptimizer service."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return MultiNutrientOptimizer()
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_soil_tests(self):
        """Sample soil test data."""
        return [
            SoilTestData(
                nutrient=NutrientType.NITROGEN,
                test_value=25.0,
                test_unit="ppm",
                test_method="KCl extraction",
                test_date=date.today(),
                confidence_level=0.9
            ),
            SoilTestData(
                nutrient=NutrientType.PHOSPHORUS,
                test_value=15.0,
                test_unit="ppm",
                test_method="Bray-1",
                test_date=date.today(),
                confidence_level=0.85
            ),
            SoilTestData(
                nutrient=NutrientType.POTASSIUM,
                test_value=120.0,
                test_unit="ppm",
                test_method="Ammonium acetate",
                test_date=date.today(),
                confidence_level=0.9
            )
        ]
    
    @pytest.fixture
    def sample_crop_requirements(self):
        """Sample crop requirements."""
        return [
            CropRequirement(
                nutrient=NutrientType.NITROGEN,
                minimum_requirement=100.0,
                optimal_range_min=120.0,
                optimal_range_max=180.0,
                maximum_tolerance=200.0,
                uptake_efficiency=0.7,
                critical_stage="vegetative"
            ),
            CropRequirement(
                nutrient=NutrientType.PHOSPHORUS,
                minimum_requirement=30.0,
                optimal_range_min=40.0,
                optimal_range_max=80.0,
                maximum_tolerance=100.0,
                uptake_efficiency=0.6,
                critical_stage="early_vegetative"
            ),
            CropRequirement(
                nutrient=NutrientType.POTASSIUM,
                minimum_requirement=80.0,
                optimal_range_min=100.0,
                optimal_range_max=150.0,
                maximum_tolerance=200.0,
                uptake_efficiency=0.8,
                critical_stage="vegetative"
            )
        ]
    
    @pytest.fixture
    def sample_environmental_limits(self):
        """Sample environmental limits."""
        return [
            EnvironmentalLimit(
                nutrient=NutrientType.NITROGEN,
                max_application_rate=200.0,
                application_unit="lbs/acre",
                environmental_risk="medium",
                regulatory_limit=180.0,
                seasonal_limit=150.0
            ),
            EnvironmentalLimit(
                nutrient=NutrientType.PHOSPHORUS,
                max_application_rate=100.0,
                application_unit="lbs/acre",
                environmental_risk="low",
                regulatory_limit=80.0,
                seasonal_limit=60.0
            ),
            EnvironmentalLimit(
                nutrient=NutrientType.POTASSIUM,
                max_application_rate=200.0,
                application_unit="lbs/acre",
                environmental_risk="low",
                regulatory_limit=None,
                seasonal_limit=None
            )
        ]
    
    @pytest.fixture
    def sample_optimization_request(
        self, 
        sample_field_id, 
        sample_soil_tests, 
        sample_crop_requirements, 
        sample_environmental_limits
    ):
        """Sample optimization request."""
        return NutrientOptimizationRequest(
            field_id=sample_field_id,
            crop_type="corn",
            target_yield=180.0,
            yield_unit="bushels",
            soil_tests=sample_soil_tests,
            crop_requirements=sample_crop_requirements,
            environmental_limits=sample_environmental_limits,
            optimization_objective="balanced",
            budget_constraint=150.0,
            risk_tolerance=0.5,
            field_size_acres=40.0,
            soil_type="loam",
            ph_level=6.5,
            organic_matter_percent=3.0,
            include_interactions=True,
            interaction_model="response_surface"
        )
    
    @pytest.mark.asyncio
    async def test_optimize_nutrients_success(self, optimizer, sample_optimization_request):
        """Test successful nutrient optimization."""
        result = await optimizer.optimize_nutrients(sample_optimization_request)
        
        assert isinstance(result, NutrientOptimizationResult)
        assert result.field_id == sample_optimization_request.field_id
        assert result.crop_type == sample_optimization_request.crop_type
        assert result.optimization_id is not None
        assert len(result.optimal_nutrient_rates) > 0
        assert result.expected_yield > 0
        assert result.total_cost >= 0
        assert result.net_profit is not None
        assert result.roi_percentage is not None
        assert result.optimization_time_seconds > 0
        assert result.created_at is not None
    
    @pytest.mark.asyncio
    async def test_optimize_nutrients_validation_error(self, optimizer, sample_field_id):
        """Test optimization with invalid data."""
        invalid_request = NutrientOptimizationRequest(
            field_id=sample_field_id,
            crop_type="corn",
            target_yield=180.0,
            yield_unit="bushels",
            soil_tests=[],  # Empty soil tests should cause validation error
            crop_requirements=[],
            environmental_limits=[],
            optimization_objective="balanced",
            field_size_acres=40.0,
            soil_type="loam",
            ph_level=6.5
        )
        
        with pytest.raises(ValueError, match="Soil test data is required"):
            await optimizer.optimize_nutrients(invalid_request)
    
    @pytest.mark.asyncio
    async def test_optimize_nutrients_budget_constraint(self, optimizer, sample_optimization_request):
        """Test optimization with budget constraint."""
        sample_optimization_request.budget_constraint = 50.0  # Low budget
        
        result = await optimizer.optimize_nutrients(sample_optimization_request)
        
        assert result.total_cost <= sample_optimization_request.budget_constraint * 1.1  # Allow small tolerance
    
    @pytest.mark.asyncio
    async def test_optimize_nutrients_different_objectives(self, optimizer, sample_optimization_request):
        """Test optimization with different objectives."""
        objectives = ["maximize_profit", "minimize_cost", "maximize_yield", "balanced"]
        
        for objective in objectives:
            sample_optimization_request.optimization_objective = objective
            result = await optimizer.optimize_nutrients(sample_optimization_request)
            
            assert result.optimization_method is not None
            assert result.convergence_status is not None
    
    @pytest.mark.asyncio
    async def test_optimize_nutrients_interaction_models(self, optimizer, sample_optimization_request):
        """Test optimization with different interaction models."""
        models = ["response_surface", "machine_learning", "linear"]
        
        for model in models:
            sample_optimization_request.interaction_model = model
            result = await optimizer.optimize_nutrients(sample_optimization_request)
            
            assert result.optimization_method is not None
            assert result.convergence_status is not None
    
    def test_validate_optimization_request_valid(self, optimizer, sample_optimization_request):
        """Test validation of valid optimization request."""
        # Should not raise any exception
        optimizer._validate_optimization_request(sample_optimization_request)
    
    def test_validate_optimization_request_invalid_soil_tests(self, optimizer, sample_field_id):
        """Test validation with invalid soil tests."""
        invalid_request = NutrientOptimizationRequest(
            field_id=sample_field_id,
            crop_type="corn",
            target_yield=180.0,
            yield_unit="bushels",
            soil_tests=[],  # Empty soil tests
            crop_requirements=[],
            environmental_limits=[],
            field_size_acres=40.0,
            soil_type="loam",
            ph_level=6.5
        )
        
        with pytest.raises(ValueError, match="Soil test data is required"):
            optimizer._validate_optimization_request(invalid_request)
    
    def test_validate_optimization_request_invalid_field_size(self, optimizer, sample_field_id):
        """Test validation with invalid field size."""
        invalid_request = NutrientOptimizationRequest(
            field_id=sample_field_id,
            crop_type="corn",
            target_yield=180.0,
            yield_unit="bushels",
            soil_tests=[
                SoilTestData(
                    nutrient=NutrientType.NITROGEN,
                    test_value=25.0,
                    test_unit="ppm",
                    test_method="KCl extraction",
                    test_date=date.today()
                )
            ],
            crop_requirements=[
                CropRequirement(
                    nutrient=NutrientType.NITROGEN,
                    minimum_requirement=100.0,
                    optimal_range_min=120.0,
                    optimal_range_max=180.0,
                    maximum_tolerance=200.0,
                    uptake_efficiency=0.7
                )
            ],
            environmental_limits=[],
            field_size_acres=0.0,  # Invalid field size
            soil_type="loam",
            ph_level=6.5
        )
        
        with pytest.raises(ValueError, match="Field size must be greater than zero"):
            optimizer._validate_optimization_request(invalid_request)
    
    def test_prepare_optimization_data(self, optimizer, sample_optimization_request):
        """Test preparation of optimization data."""
        data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        assert "nutrient_mapping" in data
        assert "soil_data" in data
        assert "crop_data" in data
        assert "env_limits" in data
        assert "field_size" in data
        assert "target_yield" in data
        assert "ph_level" in data
        assert "organic_matter" in data
        assert "soil_type" in data
        
        # Check nutrient mapping
        assert NutrientType.NITROGEN.value in data["nutrient_mapping"]
        assert NutrientType.PHOSPHORUS.value in data["nutrient_mapping"]
        assert NutrientType.POTASSIUM.value in data["nutrient_mapping"]
        
        # Check soil data
        assert NutrientType.NITROGEN.value in data["soil_data"]
        assert NutrientType.PHOSPHORUS.value in data["soil_data"]
        assert NutrientType.POTASSIUM.value in data["soil_data"]
    
    def test_calculate_yield_response(self, optimizer, sample_optimization_request):
        """Test yield response calculation."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        nutrient_rates = {
            NutrientType.NITROGEN.value: 100.0,
            NutrientType.PHOSPHORUS.value: 50.0,
            NutrientType.POTASSIUM.value: 80.0
        }
        
        yield_response = optimizer._calculate_yield_response(
            nutrient_rates, optimization_data, sample_optimization_request
        )
        
        assert yield_response > 0
        assert yield_response <= sample_optimization_request.target_yield * 1.2  # Cap at 120%
    
    def test_calculate_fertilizer_cost(self, optimizer, sample_optimization_request):
        """Test fertilizer cost calculation."""
        nutrient_rates = {
            NutrientType.NITROGEN.value: 100.0,
            NutrientType.PHOSPHORUS.value: 50.0,
            NutrientType.POTASSIUM.value: 80.0
        }
        
        cost = optimizer._calculate_fertilizer_cost(nutrient_rates, sample_optimization_request)
        
        assert cost > 0
        assert cost == 100.0 * 0.50 + 50.0 * 0.60 + 80.0 * 0.40  # Expected calculation
    
    def test_define_optimization_constraints(self, optimizer, sample_optimization_request):
        """Test constraint definition."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        # Define nutrients to optimize (same as in the service)
        nutrients_to_optimize = []
        for nutrient in [NutrientType.NITROGEN, NutrientType.PHOSPHORUS, NutrientType.POTASSIUM]:
            if nutrient.value in optimization_data["crop_data"]:
                nutrients_to_optimize.append(nutrient.value)
        
        constraints = optimizer._define_optimization_constraints(optimization_data, sample_optimization_request, nutrients_to_optimize)
        
        assert isinstance(constraints, list)
        assert len(constraints) > 0  # Should have budget and minimum requirement constraints
    
    def test_calculate_fallback_rates(self, optimizer, sample_optimization_request):
        """Test fallback rate calculation."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        fallback_rates = optimizer._calculate_fallback_rates(optimization_data, sample_optimization_request)
        
        assert isinstance(fallback_rates, dict)
        assert NutrientType.NITROGEN.value in fallback_rates
        assert NutrientType.PHOSPHORUS.value in fallback_rates
        assert NutrientType.POTASSIUM.value in fallback_rates
        
        # All rates should be non-negative
        for rate in fallback_rates.values():
            assert rate >= 0
    
    def test_calculate_economic_analysis(self, optimizer, sample_optimization_request):
        """Test economic analysis calculation."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        optimal_rates = {
            NutrientType.NITROGEN.value: 100.0,
            NutrientType.PHOSPHORUS.value: 50.0,
            NutrientType.POTASSIUM.value: 80.0
        }
        
        economic_analysis = optimizer._calculate_economic_analysis(
            optimal_rates, sample_optimization_request, optimization_data
        )
        
        assert "total_cost" in economic_analysis
        assert "expected_yield" in economic_analysis
        assert "expected_revenue" in economic_analysis
        assert "net_profit" in economic_analysis
        assert "roi_percentage" in economic_analysis
        
        assert economic_analysis["total_cost"] > 0
        assert economic_analysis["expected_yield"] > 0
        assert economic_analysis["expected_revenue"] > 0
        assert economic_analysis["net_profit"] is not None
        assert economic_analysis["roi_percentage"] is not None
    
    def test_analyze_nutrient_interactions(self, optimizer, sample_optimization_request):
        """Test nutrient interaction analysis."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        optimal_rates = {
            NutrientType.NITROGEN.value: 100.0,
            NutrientType.PHOSPHORUS.value: 50.0,
            NutrientType.POTASSIUM.value: 80.0
        }
        
        interaction_analysis = optimizer._analyze_nutrient_interactions(
            optimal_rates, sample_optimization_request, optimization_data
        )
        
        assert "interactions" in interaction_analysis
        assert "effects" in interaction_analysis
        assert isinstance(interaction_analysis["interactions"], list)
        assert isinstance(interaction_analysis["effects"], dict)
    
    def test_assess_optimization_risks(self, optimizer, sample_optimization_request):
        """Test risk assessment."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        optimal_rates = {
            NutrientType.NITROGEN.value: 100.0,
            NutrientType.PHOSPHORUS.value: 50.0,
            NutrientType.POTASSIUM.value: 80.0
        }
        
        risk_assessment = optimizer._assess_optimization_risks(
            optimal_rates, sample_optimization_request, optimization_data
        )
        
        assert "factors" in risk_assessment
        assert "score" in risk_assessment
        assert isinstance(risk_assessment["factors"], list)
        assert 0.0 <= risk_assessment["score"] <= 1.0
    
    def test_generate_recommendations(self, optimizer, sample_optimization_request):
        """Test recommendation generation."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        optimal_rates = {
            NutrientType.NITROGEN.value: 100.0,
            NutrientType.PHOSPHORUS.value: 50.0,
            NutrientType.POTASSIUM.value: 80.0
        }
        
        risk_assessment = {
            "factors": ["High nitrogen application rate"],
            "score": 0.3
        }
        
        recommendations = optimizer._generate_recommendations(
            optimal_rates, sample_optimization_request, optimization_data, risk_assessment
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_generate_alternative_strategies(self, optimizer, sample_optimization_request):
        """Test alternative strategy generation."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        alternatives = optimizer._generate_alternative_strategies(optimization_data, sample_optimization_request)
        
        assert isinstance(alternatives, list)
        assert len(alternatives) > 0
        
        for alternative in alternatives:
            assert "strategy" in alternative
            assert "description" in alternative
            assert "rates" in alternative
            assert "expected_yield" in alternative
            assert "cost" in alternative
    
    def test_nutrient_interactions_initialization(self, optimizer):
        """Test nutrient interactions initialization."""
        assert len(optimizer.nutrient_interactions) > 0
        
        # Check that we have expected interactions
        interaction_types = [interaction.interaction_type for interaction in optimizer.nutrient_interactions]
        assert InteractionType.SYNERGISTIC in interaction_types
        assert InteractionType.ANTAGONISTIC in interaction_types
    
    @pytest.mark.asyncio
    async def test_ml_optimization_training_data_generation(self, optimizer, sample_optimization_request):
        """Test ML optimization training data generation."""
        optimization_data = optimizer._prepare_optimization_data(sample_optimization_request)
        
        training_data = optimizer._generate_training_data(optimization_data, sample_optimization_request)
        
        assert len(training_data) == 1000  # Expected number of samples
        assert 'N_rate' in training_data.columns
        assert 'P_rate' in training_data.columns
        assert 'K_rate' in training_data.columns
        assert 'yield_response' in training_data.columns
        
        # Check data ranges
        assert training_data['N_rate'].min() >= 0
        assert training_data['P_rate'].min() >= 0
        assert training_data['K_rate'].min() >= 0
        assert training_data['yield_response'].min() >= 0


class TestNutrientOptimizationAPI:
    """Test suite for nutrient optimization API endpoints."""
    
    @pytest.fixture
    def sample_api_request(self):
        """Sample API request model."""
        return OptimizationRequestModel(
            field_id=uuid4(),
            crop_type="corn",
            target_yield=180.0,
            yield_unit="bushels",
            soil_tests=[
                SoilTestModel(
                    nutrient="nitrogen",
                    test_value=25.0,
                    test_unit="ppm",
                    test_method="KCl extraction",
                    test_date=date.today(),
                    confidence_level=0.9
                ),
                SoilTestModel(
                    nutrient="phosphorus",
                    test_value=15.0,
                    test_unit="ppm",
                    test_method="Bray-1",
                    test_date=date.today(),
                    confidence_level=0.85
                ),
                SoilTestModel(
                    nutrient="potassium",
                    test_value=120.0,
                    test_unit="ppm",
                    test_method="Ammonium acetate",
                    test_date=date.today(),
                    confidence_level=0.9
                )
            ],
            crop_requirements=[
                CropRequirementModel(
                    nutrient="nitrogen",
                    minimum_requirement=100.0,
                    optimal_range_min=120.0,
                    optimal_range_max=180.0,
                    maximum_tolerance=200.0,
                    uptake_efficiency=0.7,
                    critical_stage="vegetative"
                ),
                CropRequirementModel(
                    nutrient="phosphorus",
                    minimum_requirement=30.0,
                    optimal_range_min=40.0,
                    optimal_range_max=80.0,
                    maximum_tolerance=100.0,
                    uptake_efficiency=0.6,
                    critical_stage="early_vegetative"
                ),
                CropRequirementModel(
                    nutrient="potassium",
                    minimum_requirement=80.0,
                    optimal_range_min=100.0,
                    optimal_range_max=150.0,
                    maximum_tolerance=200.0,
                    uptake_efficiency=0.8,
                    critical_stage="vegetative"
                )
            ],
            environmental_limits=[
                EnvironmentalLimitModel(
                    nutrient="nitrogen",
                    max_application_rate=200.0,
                    application_unit="lbs/acre",
                    environmental_risk="medium",
                    regulatory_limit=180.0,
                    seasonal_limit=150.0
                ),
                EnvironmentalLimitModel(
                    nutrient="phosphorus",
                    max_application_rate=100.0,
                    application_unit="lbs/acre",
                    environmental_risk="low",
                    regulatory_limit=80.0,
                    seasonal_limit=60.0
                ),
                EnvironmentalLimitModel(
                    nutrient="potassium",
                    max_application_rate=200.0,
                    application_unit="lbs/acre",
                    environmental_risk="low"
                )
            ],
            optimization_objective="balanced",
            budget_constraint=150.0,
            risk_tolerance=0.5,
            field_size_acres=40.0,
            soil_type="loam",
            ph_level=6.5,
            organic_matter_percent=3.0,
            include_interactions=True,
            interaction_model="response_surface"
        )
    
    def test_optimization_request_model_validation(self, sample_api_request):
        """Test API request model validation."""
        # Should not raise any exception
        assert sample_api_request.field_id is not None
        assert sample_api_request.crop_type == "corn"
        assert len(sample_api_request.soil_tests) == 3
        assert len(sample_api_request.crop_requirements) == 3
        assert len(sample_api_request.environmental_limits) == 3
    
    def test_optimization_request_model_invalid_nutrient(self):
        """Test API request model with invalid nutrient."""
        with pytest.raises(ValueError, match="Invalid nutrient type"):
            SoilTestModel(
                nutrient="invalid_nutrient",
                test_value=25.0,
                test_unit="ppm",
                test_method="KCl extraction",
                test_date=date.today()
            )
    
    def test_optimization_request_model_invalid_range(self):
        """Test API request model with invalid optimal range."""
        with pytest.raises(ValueError, match="optimal_range_max must be greater than optimal_range_min"):
            CropRequirementModel(
                nutrient="nitrogen",
                minimum_requirement=100.0,
                optimal_range_min=180.0,  # Min > Max
                optimal_range_max=120.0,
                maximum_tolerance=200.0,
                uptake_efficiency=0.7
            )
    
    def test_optimization_request_model_empty_soil_tests(self):
        """Test API request model with empty soil tests."""
        with pytest.raises(ValueError, match="At least one soil test is required"):
            OptimizationRequestModel(
                field_id=uuid4(),
                crop_type="corn",
                target_yield=180.0,
                soil_tests=[],  # Empty soil tests
                crop_requirements=[
                    CropRequirementModel(
                        nutrient="nitrogen",
                        minimum_requirement=100.0,
                        optimal_range_min=120.0,
                        optimal_range_max=180.0,
                        maximum_tolerance=200.0,
                        uptake_efficiency=0.7
                    )
                ],
                field_size_acres=40.0,
                soil_type="loam",
                ph_level=6.5
            )
    
    def test_optimization_request_model_empty_crop_requirements(self):
        """Test API request model with empty crop requirements."""
        with pytest.raises(ValueError, match="At least one crop requirement is required"):
            OptimizationRequestModel(
                field_id=uuid4(),
                crop_type="corn",
                target_yield=180.0,
                soil_tests=[
                    SoilTestModel(
                        nutrient="nitrogen",
                        test_value=25.0,
                        test_unit="ppm",
                        test_method="KCl extraction",
                        test_date=date.today()
                    )
                ],
                crop_requirements=[],  # Empty crop requirements
                field_size_acres=40.0,
                soil_type="loam",
                ph_level=6.5
            )


class TestNutrientOptimizationIntegration:
    """Integration tests for nutrient optimization service."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization(self):
        """Test end-to-end optimization workflow."""
        optimizer = MultiNutrientOptimizer()
        
        # Create comprehensive test data
        field_id = uuid4()
        
        soil_tests = [
            SoilTestData(
                nutrient=NutrientType.NITROGEN,
                test_value=20.0,
                test_unit="ppm",
                test_method="KCl extraction",
                test_date=date.today(),
                confidence_level=0.9
            ),
            SoilTestData(
                nutrient=NutrientType.PHOSPHORUS,
                test_value=12.0,
                test_unit="ppm",
                test_method="Bray-1",
                test_date=date.today(),
                confidence_level=0.85
            ),
            SoilTestData(
                nutrient=NutrientType.POTASSIUM,
                test_value=100.0,
                test_unit="ppm",
                test_method="Ammonium acetate",
                test_date=date.today(),
                confidence_level=0.9
            )
        ]
        
        crop_requirements = [
            CropRequirement(
                nutrient=NutrientType.NITROGEN,
                minimum_requirement=120.0,
                optimal_range_min=140.0,
                optimal_range_max=200.0,
                maximum_tolerance=220.0,
                uptake_efficiency=0.75,
                critical_stage="vegetative"
            ),
            CropRequirement(
                nutrient=NutrientType.PHOSPHORUS,
                minimum_requirement=40.0,
                optimal_range_min=50.0,
                optimal_range_max=90.0,
                maximum_tolerance=100.0,
                uptake_efficiency=0.65,
                critical_stage="early_vegetative"
            ),
            CropRequirement(
                nutrient=NutrientType.POTASSIUM,
                minimum_requirement=100.0,
                optimal_range_min=120.0,
                optimal_range_max=180.0,
                maximum_tolerance=200.0,
                uptake_efficiency=0.85,
                critical_stage="vegetative"
            )
        ]
        
        environmental_limits = [
            EnvironmentalLimit(
                nutrient=NutrientType.NITROGEN,
                max_application_rate=180.0,
                application_unit="lbs/acre",
                environmental_risk="medium",
                regulatory_limit=160.0,
                seasonal_limit=140.0
            ),
            EnvironmentalLimit(
                nutrient=NutrientType.PHOSPHORUS,
                max_application_rate=80.0,
                application_unit="lbs/acre",
                environmental_risk="low",
                regulatory_limit=70.0,
                seasonal_limit=60.0
            ),
            EnvironmentalLimit(
                nutrient=NutrientType.POTASSIUM,
                max_application_rate=180.0,
                application_unit="lbs/acre",
                environmental_risk="low"
            )
        ]
        
        request = NutrientOptimizationRequest(
            field_id=field_id,
            crop_type="corn",
            target_yield=200.0,
            yield_unit="bushels",
            soil_tests=soil_tests,
            crop_requirements=crop_requirements,
            environmental_limits=environmental_limits,
            optimization_objective="maximize_profit",
            budget_constraint=200.0,
            risk_tolerance=0.4,
            field_size_acres=50.0,
            soil_type="clay_loam",
            ph_level=6.8,
            organic_matter_percent=4.2,
            include_interactions=True,
            interaction_model="response_surface"
        )
        
        # Perform optimization
        result = await optimizer.optimize_nutrients(request)
        
        # Validate results
        assert result.field_id == field_id
        assert result.crop_type == "corn"
        assert result.optimization_id is not None
        assert len(result.optimal_nutrient_rates) == 3
        assert result.expected_yield > 0
        assert result.total_cost > 0
        assert result.net_profit is not None
        assert result.roi_percentage is not None
        assert result.optimization_time_seconds > 0
        assert result.created_at is not None
        
        # Check that rates are within environmental limits
        for nutrient, rate in result.optimal_nutrient_rates.items():
            assert rate >= 0
            # Check against environmental limits
            for limit in environmental_limits:
                if limit.nutrient.value == nutrient:
                    assert rate <= limit.max_application_rate
        
        # Check that cost is within budget
        assert result.total_cost <= request.budget_constraint * 1.1  # Allow small tolerance
        
        # Check recommendations
        assert len(result.recommendations) > 0
        
        # Check alternative strategies
        assert len(result.alternative_strategies) > 0
        
        # Check risk assessment
        assert 0.0 <= result.risk_score <= 1.0
        assert isinstance(result.risk_factors, list)