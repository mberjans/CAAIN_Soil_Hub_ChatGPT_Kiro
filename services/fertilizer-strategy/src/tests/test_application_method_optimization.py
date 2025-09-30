"""
Comprehensive Tests for Application Method Optimization Service

This module contains comprehensive tests for the application method optimization service,
including unit tests, integration tests, and agricultural validation tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from typing import List, Dict, Any

from ..models.application_method_optimization_models import (
    ApplicationMethodOptimizationRequest,
    ApplicationMethodOptimizationResult,
    ApplicationMethodComparisonRequest,
    ApplicationMethodComparisonResult,
    ApplicationMethodSummary,
    ApplicationMethod,
    FertilizerForm,
    EquipmentType,
    SoilCondition,
    ApplicationConstraints,
    ApplicationEfficiency,
    ApplicationCosts
)
from ..services.application_method_optimization_service import ApplicationMethodOptimizer


class TestApplicationMethodOptimizer:
    """Comprehensive test suite for application method optimization service."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return ApplicationMethodOptimizer()
    
    @pytest.fixture
    def sample_optimization_request(self):
        """Create sample optimization request for testing."""
        return ApplicationMethodOptimizationRequest(
            field_id="test_field_001",
            crop_type="corn",
            field_size_acres=40.0,
            fertilizer_requirements={
                "nitrogen": 150.0,
                "phosphorus": 60.0,
                "potassium": 80.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
            soil_type="clay_loam",
            soil_ph=6.5,
            organic_matter_percent=3.2,
            cation_exchange_capacity=15.0,
            drainage_class="moderate",
            slope_percent=2.0,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR,
                    EquipmentType.SPRAYER
                ],
                labor_availability=0.8,
                budget_constraints=50.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.9
            ),
            optimize_for_yield=True,
            optimize_for_cost=True,
            optimize_for_efficiency=True,
            optimize_for_environment=False
        )
    
    @pytest.fixture
    def sample_comparison_request(self):
        """Create sample comparison request for testing."""
        return ApplicationMethodComparisonRequest(
            methods_to_compare=[
                ApplicationMethod.BROADCAST,
                ApplicationMethod.BANDED,
                ApplicationMethod.SIDE_DRESS
            ],
            field_id="test_field_001",
            crop_type="corn",
            field_size_acres=40.0,
            fertilizer_requirements={
                "nitrogen": 150.0,
                "phosphorus": 60.0,
                "potassium": 80.0
            },
            soil_type="clay_loam",
            soil_ph=6.5,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR
                ],
                labor_availability=0.8,
                budget_constraints=50.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.9
            )
        )
    
    @pytest.mark.asyncio
    async def test_optimize_application_methods_success(self, optimizer, sample_optimization_request):
        """Test successful application method optimization."""
        result = await optimizer.optimize_application_methods(sample_optimization_request)
        
        # Verify result structure
        assert isinstance(result, ApplicationMethodOptimizationResult)
        assert result.request_id == sample_optimization_request.request_id
        assert len(result.recommendations) > 0
        assert result.best_method is not None
        assert result.total_methods_evaluated > 0
        assert result.feasible_methods > 0
        assert result.processing_time_ms > 0
        
        # Verify recommendations are ranked
        for i, rec in enumerate(result.recommendations):
            assert rec.ranking == i + 1
            assert rec.overall_score >= 0.0
            assert rec.overall_score <= 1.0
        
        # Verify best method is first recommendation
        assert result.best_method == result.recommendations[0]
    
    @pytest.mark.asyncio
    async def test_optimize_application_methods_with_preferences(self, optimizer):
        """Test optimization with preferred methods."""
        request = ApplicationMethodOptimizationRequest(
            field_id="test_field_002",
            crop_type="soybean",
            field_size_acres=80.0,
            fertilizer_requirements={"nitrogen": 50.0, "phosphorus": 40.0},
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="sandy_loam",
            soil_ph=6.8,
            organic_matter_percent=2.5,
            cation_exchange_capacity=12.0,
            constraints=ApplicationConstraints(
                available_equipment=[EquipmentType.BROADCASTER, EquipmentType.PLANTER_MOUNTED],
                labor_availability=0.6,
                budget_constraints=30.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.8
            ),
            preferred_methods=[ApplicationMethod.BROADCAST, ApplicationMethod.BANDED],
            avoid_methods=[ApplicationMethod.INJECTION]
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify preferred methods are prioritized
        preferred_in_results = [rec.method for rec in result.recommendations[:2]]
        assert ApplicationMethod.BROADCAST in preferred_in_results or ApplicationMethod.BANDED in preferred_in_results
        
        # Verify avoided methods are not in results
        avoided_methods = [rec.method for rec in result.recommendations]
        assert ApplicationMethod.INJECTION not in avoided_methods
    
    @pytest.mark.asyncio
    async def test_optimize_application_methods_no_feasible_methods(self, optimizer):
        """Test optimization when no methods are feasible."""
        request = ApplicationMethodOptimizationRequest(
            field_id="test_field_003",
            crop_type="wheat",
            field_size_acres=100.0,
            fertilizer_requirements={"nitrogen": 120.0},
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="clay",
            soil_ph=5.5,
            organic_matter_percent=1.5,
            cation_exchange_capacity=20.0,
            constraints=ApplicationConstraints(
                available_equipment=[],  # No equipment available
                labor_availability=0.1,
                budget_constraints=5.0,  # Very low budget
                soil_conditions=SoilCondition.FROZEN,
                field_accessibility=0.1
            )
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify no feasible methods
        assert result.feasible_methods == 0
        assert len(result.recommendations) == 0
        assert result.best_method is None
    
    @pytest.mark.asyncio
    async def test_compare_application_methods_success(self, optimizer, sample_comparison_request):
        """Test successful application method comparison."""
        result = await optimizer.compare_application_methods(sample_comparison_request)
        
        # Verify result structure
        assert isinstance(result, ApplicationMethodComparisonResult)
        assert result.request_id == sample_comparison_request.request_id
        assert len(result.method_comparisons) == len(sample_comparison_request.methods_to_compare)
        
        # Verify all requested methods are compared
        compared_methods = [rec.method for rec in result.method_comparisons]
        for method in sample_comparison_request.methods_to_compare:
            assert method in compared_methods
        
        # Verify comparison data
        assert len(result.yield_comparison) > 0
        assert len(result.cost_comparison) > 0
        assert len(result.efficiency_comparison) > 0
        assert len(result.environmental_comparison) > 0
        
        # Verify rankings
        assert len(result.method_rankings) > 0
        assert result.best_method_overall is not None
    
    @pytest.mark.asyncio
    async def test_get_application_method_summary(self, optimizer):
        """Test getting application method summary."""
        summary = await optimizer.get_application_method_summary(
            "test_optimization_001",
            "test_field_001",
            "corn"
        )
        
        # Verify summary structure
        assert isinstance(summary, ApplicationMethodSummary)
        assert summary.optimization_id == "test_optimization_001"
        assert summary.field_id == "test_field_001"
        assert summary.crop_type == "corn"
        assert summary.best_method is not None
        assert summary.best_method_score >= 0.0
        assert summary.best_method_score <= 1.0
        assert summary.expected_yield_impact > 0.0
        assert summary.total_cost_per_acre > 0.0
        assert len(summary.key_benefits) > 0
        assert len(summary.key_risks) > 0
    
    def test_filter_feasible_methods(self, optimizer, sample_optimization_request):
        """Test filtering of feasible methods."""
        all_methods = list(ApplicationMethod)
        feasible_methods = optimizer._filter_feasible_methods(sample_optimization_request, all_methods)
        
        # Verify feasible methods are returned
        assert len(feasible_methods) > 0
        assert len(feasible_methods) <= len(all_methods)
        
        # Verify all feasible methods have required equipment
        for method in feasible_methods:
            required_equipment = optimizer.equipment_compatibility.get(method.value, [])
            assert any(EquipmentType(eq) in sample_optimization_request.constraints.available_equipment 
                      for eq in required_equipment)
    
    def test_calculate_fertilizer_cost(self, optimizer, sample_optimization_request):
        """Test fertilizer cost calculation."""
        cost = optimizer._calculate_fertilizer_cost(sample_optimization_request)
        
        # Verify cost calculation
        assert cost > 0.0
        
        # Verify cost is reasonable (should be around $200-300 for this example)
        expected_cost = (
            150.0 * 0.65 +  # nitrogen
            60.0 * 0.85 +   # phosphorus
            80.0 * 0.45     # potassium
        )
        assert abs(cost - expected_cost) < 1.0
    
    def test_calculate_yield_impact(self, optimizer, sample_optimization_request):
        """Test yield impact calculation."""
        efficiency = ApplicationEfficiency(
            nutrient_use_efficiency=0.85,
            application_uniformity=0.90,
            volatilization_loss=0.05,
            leaching_loss=0.15,
            runoff_loss=0.05,
            denitrification_loss=0.03,
            overall_efficiency=0.82
        )
        
        yield_impact = optimizer._calculate_yield_impact(
            sample_optimization_request,
            ApplicationMethod.BANDED,
            efficiency
        )
        
        # Verify yield impact calculation
        assert yield_impact > 0.0
        assert yield_impact <= 20.0  # Reasonable upper bound
    
    def test_calculate_environmental_score(self, optimizer):
        """Test environmental score calculation."""
        efficiency = ApplicationEfficiency(
            nutrient_use_efficiency=0.85,
            application_uniformity=0.90,
            volatilization_loss=0.05,
            leaching_loss=0.15,
            runoff_loss=0.05,
            denitrification_loss=0.03,
            overall_efficiency=0.82
        )
        
        env_score = optimizer._calculate_environmental_score(ApplicationMethod.BANDED, efficiency)
        
        # Verify environmental score
        assert env_score >= 0.0
        assert env_score <= 1.0
    
    def test_calculate_feasibility_score(self, optimizer, sample_optimization_request):
        """Test feasibility score calculation."""
        feasibility_score = optimizer._calculate_feasibility_score(
            sample_optimization_request,
            ApplicationMethod.BROADCAST
        )
        
        # Verify feasibility score
        assert feasibility_score >= 0.0
        assert feasibility_score <= 1.0
    
    def test_check_constraint_violations(self, optimizer, sample_optimization_request):
        """Test constraint violation checking."""
        violations = optimizer._check_constraint_violations(
            sample_optimization_request,
            ApplicationMethod.BROADCAST
        )
        
        # Verify violations list
        assert isinstance(violations, list)
        
        # Test with method that exceeds budget
        expensive_request = sample_optimization_request.copy()
        expensive_request.constraints.budget_constraints = 5.0  # Very low budget
        
        violations = optimizer._check_constraint_violations(
            expensive_request,
            ApplicationMethod.INJECTION  # Expensive method
        )
        
        # Should have budget violation
        assert len(violations) > 0
        assert any("budget constraint" in violation.lower() for violation in violations)
    
    def test_calculate_overall_score(self, optimizer, sample_optimization_request):
        """Test overall score calculation."""
        efficiency = ApplicationEfficiency(
            nutrient_use_efficiency=0.85,
            application_uniformity=0.90,
            volatilization_loss=0.05,
            leaching_loss=0.15,
            runoff_loss=0.05,
            denitrification_loss=0.03,
            overall_efficiency=0.82
        )
        
        costs = ApplicationCosts(
            fertilizer_cost_per_acre=200.0,
            application_cost_per_acre=15.0,
            equipment_cost_per_acre=8.0,
            labor_cost_per_acre=5.0,
            fuel_cost_per_acre=3.0,
            total_cost_per_acre=231.0
        )
        
        overall_score = optimizer._calculate_overall_score(
            sample_optimization_request,
            ApplicationMethod.BANDED,
            efficiency,
            costs,
            12.5,  # yield_impact
            0.8,   # environmental_score
            0.9    # feasibility_score
        )
        
        # Verify overall score
        assert overall_score >= 0.0
        assert overall_score <= 1.0
    
    def test_determine_fertilizer_form(self, optimizer, sample_optimization_request):
        """Test fertilizer form determination."""
        form = optimizer._determine_fertilizer_form(
            sample_optimization_request,
            ApplicationMethod.BROADCAST
        )
        
        # Verify fertilizer form
        assert form == FertilizerForm.GRANULAR
        
        # Test liquid form for foliar application
        form = optimizer._determine_fertilizer_form(
            sample_optimization_request,
            ApplicationMethod.FOLIAR
        )
        assert form == FertilizerForm.LIQUID
    
    def test_determine_equipment_type(self, optimizer):
        """Test equipment type determination."""
        equipment = optimizer._determine_equipment_type(ApplicationMethod.BROADCAST)
        assert equipment == EquipmentType.BROADCASTER
        
        equipment = optimizer._determine_equipment_type(ApplicationMethod.BANDED)
        assert equipment == EquipmentType.PLANTER_MOUNTED
        
        equipment = optimizer._determine_equipment_type(ApplicationMethod.FOLIAR)
        assert equipment == EquipmentType.SPRAYER
    
    def test_generate_method_comparison(self, optimizer):
        """Test method comparison generation."""
        # Create sample recommendations
        recommendations = [
            optimizer._create_sample_recommendation(ApplicationMethod.BROADCAST, 0.8),
            optimizer._create_sample_recommendation(ApplicationMethod.BANDED, 0.9),
            optimizer._create_sample_recommendation(ApplicationMethod.SIDE_DRESS, 0.85)
        ]
        
        comparison = optimizer._generate_method_comparison(recommendations)
        
        # Verify comparison structure
        assert len(comparison) == 3
        assert ApplicationMethod.BROADCAST.value in comparison
        assert ApplicationMethod.BANDED.value in comparison
        assert ApplicationMethod.SIDE_DRESS.value in comparison
        
        # Verify comparison data
        for method_data in comparison.values():
            assert "overall_score" in method_data
            assert "yield_impact" in method_data
            assert "total_cost" in method_data
            assert "efficiency" in method_data
    
    def test_generate_key_insights(self, optimizer, sample_optimization_request):
        """Test key insights generation."""
        recommendations = [
            optimizer._create_sample_recommendation(ApplicationMethod.BROADCAST, 0.8),
            optimizer._create_sample_recommendation(ApplicationMethod.BANDED, 0.9),
            optimizer._create_sample_recommendation(ApplicationMethod.SIDE_DRESS, 0.85)
        ]
        
        insights = optimizer._generate_key_insights(recommendations, sample_optimization_request)
        
        # Verify insights
        assert len(insights) > 0
        assert any("Best method" in insight for insight in insights)
        assert any("Cost range" in insight for insight in insights)
        assert any("Efficiency range" in insight for insight in insights)
    
    def test_generate_implementation_notes(self, optimizer, sample_optimization_request):
        """Test implementation notes generation."""
        best_method = optimizer._create_sample_recommendation(ApplicationMethod.BANDED, 0.9)
        
        notes = optimizer._generate_implementation_notes(best_method, sample_optimization_request)
        
        # Verify implementation notes
        assert len(notes) > 0
        assert any("Required equipment" in note for note in notes)
        assert any("Optimal timing" in note for note in notes)
        assert any("Total cost" in note for note in notes)
    
    def _create_sample_recommendation(self, method: ApplicationMethod, score: float):
        """Create sample recommendation for testing."""
        from ..models.application_method_optimization_models import ApplicationMethodRecommendation
        
        efficiency = ApplicationEfficiency(
            nutrient_use_efficiency=0.85,
            application_uniformity=0.90,
            volatilization_loss=0.05,
            leaching_loss=0.15,
            runoff_loss=0.05,
            denitrification_loss=0.03,
            overall_efficiency=0.82
        )
        
        costs = ApplicationCosts(
            fertilizer_cost_per_acre=200.0,
            application_cost_per_acre=15.0,
            equipment_cost_per_acre=8.0,
            labor_cost_per_acre=5.0,
            fuel_cost_per_acre=3.0,
            total_cost_per_acre=231.0
        )
        
        return ApplicationMethodRecommendation(
            method=method,
            fertilizer_form=FertilizerForm.GRANULAR,
            equipment_type=EquipmentType.BROADCASTER,
            efficiency=efficiency,
            costs=costs,
            expected_yield_impact=12.5,
            nutrient_availability=0.85,
            application_timing="Pre-plant",
            environmental_score=0.8,
            runoff_risk=0.05,
            volatilization_risk=0.05,
            feasibility_score=0.9,
            constraint_violations=[],
            overall_score=score,
            ranking=1
        )


class TestAgriculturalValidation:
    """Agricultural validation tests for application method optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return ApplicationMethodOptimizer()
    
    @pytest.mark.asyncio
    async def test_corn_field_optimization(self, optimizer):
        """Test optimization for corn field with realistic parameters."""
        request = ApplicationMethodOptimizationRequest(
            field_id="corn_field_001",
            crop_type="corn",
            field_size_acres=160.0,
            fertilizer_requirements={
                "nitrogen": 180.0,
                "phosphorus": 80.0,
                "potassium": 100.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
            soil_type="silt_loam",
            soil_ph=6.2,
            organic_matter_percent=4.5,
            cation_exchange_capacity=18.0,
            drainage_class="well",
            slope_percent=1.5,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR,
                    EquipmentType.SPRAYER
                ],
                labor_availability=0.9,
                budget_constraints=80.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.95
            ),
            optimize_for_yield=True,
            optimize_for_cost=True,
            optimize_for_efficiency=True
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify agricultural validity
        assert result.feasible_methods > 0
        assert result.best_method is not None
        
        # Verify best method is agriculturally sound
        best_method = result.best_method
        assert best_method.expected_yield_impact > 0.0
        assert best_method.efficiency.overall_efficiency > 0.5
        assert best_method.costs.total_cost_per_acre > 0.0
        
        # Verify recommendations are realistic for corn
        for rec in result.recommendations:
            assert rec.expected_yield_impact <= 25.0  # Realistic upper bound for corn
            assert rec.costs.total_cost_per_acre <= 150.0  # Realistic cost upper bound
    
    @pytest.mark.asyncio
    async def test_soybean_field_optimization(self, optimizer):
        """Test optimization for soybean field with realistic parameters."""
        request = ApplicationMethodOptimizationRequest(
            field_id="soybean_field_001",
            crop_type="soybean",
            field_size_acres=200.0,
            fertilizer_requirements={
                "nitrogen": 20.0,  # Low N for soybeans
                "phosphorus": 60.0,
                "potassium": 80.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="clay_loam",
            soil_ph=6.8,
            organic_matter_percent=3.8,
            cation_exchange_capacity=16.0,
            drainage_class="moderate",
            slope_percent=3.0,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED
                ],
                labor_availability=0.7,
                budget_constraints=40.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.85
            ),
            optimize_for_yield=True,
            optimize_for_cost=True
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify agricultural validity for soybeans
        assert result.feasible_methods > 0
        assert result.best_method is not None
        
        # Verify recommendations are realistic for soybeans
        for rec in result.recommendations:
            assert rec.expected_yield_impact <= 15.0  # Realistic upper bound for soybeans
            assert rec.costs.total_cost_per_acre <= 100.0  # Realistic cost upper bound
    
    @pytest.mark.asyncio
    async def test_wheat_field_optimization(self, optimizer):
        """Test optimization for wheat field with realistic parameters."""
        request = ApplicationMethodOptimizationRequest(
            field_id="wheat_field_001",
            crop_type="wheat",
            field_size_acres=120.0,
            fertilizer_requirements={
                "nitrogen": 120.0,
                "phosphorus": 50.0,
                "potassium": 60.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="sandy_loam",
            soil_ph=7.1,
            organic_matter_percent=2.2,
            cation_exchange_capacity=12.0,
            drainage_class="excessive",
            slope_percent=5.0,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.SPRAYER
                ],
                labor_availability=0.6,
                budget_constraints=35.0,
                soil_conditions=SoilCondition.DRY,
                field_accessibility=0.8
            ),
            optimize_for_yield=True,
            optimize_for_efficiency=True
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify agricultural validity for wheat
        assert result.feasible_methods > 0
        assert result.best_method is not None
        
        # Verify recommendations are realistic for wheat
        for rec in result.recommendations:
            assert rec.expected_yield_impact <= 18.0  # Realistic upper bound for wheat
            assert rec.costs.total_cost_per_acre <= 80.0  # Realistic cost upper bound
    
    @pytest.mark.asyncio
    async def test_high_ph_soil_optimization(self, optimizer):
        """Test optimization for high pH soil conditions."""
        request = ApplicationMethodOptimizationRequest(
            field_id="high_ph_field_001",
            crop_type="corn",
            field_size_acres=80.0,
            fertilizer_requirements={
                "nitrogen": 160.0,
                "phosphorus": 70.0,
                "potassium": 90.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
            soil_type="clay",
            soil_ph=8.2,  # High pH
            organic_matter_percent=2.8,
            cation_exchange_capacity=22.0,
            drainage_class="poor",
            slope_percent=1.0,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR
                ],
                labor_availability=0.8,
                budget_constraints=60.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.9
            ),
            optimize_for_yield=True,
            optimize_for_efficiency=True
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify optimization handles high pH appropriately
        assert result.feasible_methods > 0
        assert result.best_method is not None
        
        # Verify yield impact accounts for high pH
        best_method = result.best_method
        assert best_method.expected_yield_impact > 0.0
        # High pH should reduce yield potential
        assert best_method.expected_yield_impact <= 15.0
    
    @pytest.mark.asyncio
    async def test_low_organic_matter_optimization(self, optimizer):
        """Test optimization for low organic matter soil."""
        request = ApplicationMethodOptimizationRequest(
            field_id="low_om_field_001",
            crop_type="corn",
            field_size_acres=100.0,
            fertilizer_requirements={
                "nitrogen": 200.0,  # Higher N requirement for low OM
                "phosphorus": 80.0,
                "potassium": 100.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="sandy",
            soil_ph=6.0,
            organic_matter_percent=1.2,  # Low organic matter
            cation_exchange_capacity=8.0,
            drainage_class="excessive",
            slope_percent=2.0,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR
                ],
                labor_availability=0.9,
                budget_constraints=70.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.95
            ),
            optimize_for_yield=True,
            optimize_for_efficiency=True
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Verify optimization handles low organic matter appropriately
        assert result.feasible_methods > 0
        assert result.best_method is not None
        
        # Verify yield impact accounts for low organic matter
        best_method = result.best_method
        assert best_method.expected_yield_impact > 0.0
        # Low OM should reduce yield potential
        assert best_method.expected_yield_impact <= 18.0


class TestPerformanceValidation:
    """Performance validation tests for application method optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return ApplicationMethodOptimizer()
    
    @pytest.mark.asyncio
    async def test_optimization_response_time(self, optimizer):
        """Test that optimization completes within acceptable time."""
        request = ApplicationMethodOptimizationRequest(
            field_id="perf_test_field",
            crop_type="corn",
            field_size_acres=1000.0,  # Large field
            fertilizer_requirements={
                "nitrogen": 180.0,
                "phosphorus": 80.0,
                "potassium": 100.0
            },
            fertilizer_forms=[FertilizerForm.GRANULAR, FertilizerForm.LIQUID],
            soil_type="clay_loam",
            soil_ph=6.5,
            organic_matter_percent=3.5,
            cation_exchange_capacity=16.0,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR,
                    EquipmentType.SPRAYER,
                    EquipmentType.IRRIGATION_SYSTEM,
                    EquipmentType.INJECTION_SYSTEM
                ],
                labor_availability=0.9,
                budget_constraints=100.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.95
            ),
            optimize_for_yield=True,
            optimize_for_cost=True,
            optimize_for_efficiency=True,
            optimize_for_environment=True
        )
        
        import time
        start_time = time.time()
        
        result = await optimizer.optimize_application_methods(request)
        
        elapsed_time = time.time() - start_time
        
        # Verify response time is acceptable (< 5 seconds)
        assert elapsed_time < 5.0
        assert result.processing_time_ms < 5000.0
    
    @pytest.mark.asyncio
    async def test_comparison_response_time(self, optimizer):
        """Test that comparison completes within acceptable time."""
        request = ApplicationMethodComparisonRequest(
            methods_to_compare=[
                ApplicationMethod.BROADCAST,
                ApplicationMethod.BROADCAST_INCORPORATED,
                ApplicationMethod.BANDED,
                ApplicationMethod.SIDE_DRESS,
                ApplicationMethod.FOLIAR,
                ApplicationMethod.FERTIGATION,
                ApplicationMethod.INJECTION
            ],
            field_id="perf_test_field",
            crop_type="corn",
            field_size_acres=500.0,
            fertilizer_requirements={
                "nitrogen": 180.0,
                "phosphorus": 80.0,
                "potassium": 100.0
            },
            soil_type="clay_loam",
            soil_ph=6.5,
            constraints=ApplicationConstraints(
                available_equipment=[
                    EquipmentType.BROADCASTER,
                    EquipmentType.PLANTER_MOUNTED,
                    EquipmentType.SIDE_DRESS_BAR,
                    EquipmentType.SPRAYER,
                    EquipmentType.IRRIGATION_SYSTEM,
                    EquipmentType.INJECTION_SYSTEM
                ],
                labor_availability=0.9,
                budget_constraints=100.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.95
            )
        )
        
        import time
        start_time = time.time()
        
        result = await optimizer.compare_application_methods(request)
        
        elapsed_time = time.time() - start_time
        
        # Verify response time is acceptable (< 3 seconds)
        assert elapsed_time < 3.0
        assert result.processing_time_ms < 3000.0


class TestEdgeCases:
    """Edge case tests for application method optimization."""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return ApplicationMethodOptimizer()
    
    @pytest.mark.asyncio
    async def test_extreme_budget_constraints(self, optimizer):
        """Test optimization with extreme budget constraints."""
        request = ApplicationMethodOptimizationRequest(
            field_id="extreme_budget_field",
            crop_type="corn",
            field_size_acres=50.0,
            fertilizer_requirements={"nitrogen": 150.0},
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="clay_loam",
            soil_ph=6.5,
            organic_matter_percent=3.0,
            cation_exchange_capacity=15.0,
            constraints=ApplicationConstraints(
                available_equipment=[EquipmentType.BROADCASTER],
                labor_availability=0.5,
                budget_constraints=1.0,  # Extremely low budget
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.8
            )
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Should handle extreme constraints gracefully
        assert result.feasible_methods >= 0
        if result.feasible_methods > 0:
            assert result.best_method is not None
            # All recommendations should have constraint violations
            for rec in result.recommendations:
                assert len(rec.constraint_violations) > 0
    
    @pytest.mark.asyncio
    async def test_no_equipment_available(self, optimizer):
        """Test optimization with no equipment available."""
        request = ApplicationMethodOptimizationRequest(
            field_id="no_equipment_field",
            crop_type="corn",
            field_size_acres=100.0,
            fertilizer_requirements={"nitrogen": 150.0},
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="clay_loam",
            soil_ph=6.5,
            organic_matter_percent=3.0,
            cation_exchange_capacity=15.0,
            constraints=ApplicationConstraints(
                available_equipment=[],  # No equipment
                labor_availability=0.8,
                budget_constraints=50.0,
                soil_conditions=SoilCondition.MOIST,
                field_accessibility=0.9
            )
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Should have no feasible methods
        assert result.feasible_methods == 0
        assert len(result.recommendations) == 0
        assert result.best_method is None
    
    @pytest.mark.asyncio
    async def test_extreme_field_conditions(self, optimizer):
        """Test optimization with extreme field conditions."""
        request = ApplicationMethodOptimizationRequest(
            field_id="extreme_conditions_field",
            crop_type="corn",
            field_size_acres=200.0,
            fertilizer_requirements={"nitrogen": 150.0},
            fertilizer_forms=[FertilizerForm.GRANULAR],
            soil_type="clay",
            soil_ph=4.0,  # Very low pH
            organic_matter_percent=0.5,  # Very low OM
            cation_exchange_capacity=5.0,  # Very low CEC
            drainage_class="poor",
            slope_percent=15.0,  # High slope
            constraints=ApplicationConstraints(
                available_equipment=[EquipmentType.BROADCASTER],
                labor_availability=0.3,
                budget_constraints=20.0,
                soil_conditions=SoilCondition.WET,
                field_accessibility=0.2
            )
        )
        
        result = await optimizer.optimize_application_methods(request)
        
        # Should handle extreme conditions gracefully
        assert result.feasible_methods >= 0
        if result.feasible_methods > 0:
            assert result.best_method is not None
            # Yield impact should be reduced due to poor conditions
            assert result.best_method.expected_yield_impact <= 10.0