"""
Field Optimization Service Tests
CAAIN Soil Hub - TICKET-008_farm-location-input-10.2

Comprehensive tests for field optimization service including:
- Layout optimization tests
- Access road optimization tests
- Equipment optimization tests
- Economic optimization tests
- Implementation planning tests
- Integration tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.field_optimization_service import (
    FieldOptimizationService,
    FieldOptimizationRequest,
    FieldOptimizationResult,
    LayoutOptimizationRecommendation,
    AccessRoadRecommendation,
    EquipmentOptimizationRecommendation,
    EconomicOptimizationRecommendation,
    ImplementationPlan,
    FieldOptimizationError,
    OptimizationType,
    ImplementationPhase,
    OptimizationPriority,
    Coordinates
)


class TestFieldOptimizationService:
    """Test suite for FieldOptimizationService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FieldOptimizationService()

    @pytest.fixture
    def sample_request(self):
        """Create sample field optimization request."""
        return FieldOptimizationRequest(
            field_id="test-field-1",
            field_name="Test Field",
            coordinates=Coordinates(latitude=40.0, longitude=-95.0),
            boundary={"type": "Polygon", "coordinates": [[[-95.0, 40.0], [-94.9, 40.0], [-94.9, 40.1], [-95.0, 40.1], [-95.0, 40.0]]]},
            area_acres=80.5,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.0,
            organic_matter_percent=3.5,
            irrigation_available=False,
            tile_drainage=True,
            accessibility="good",
            current_equipment=["Standard tractor", "Basic implements"],
            budget_constraints={"annual_budget": 50000, "max_investment": 100000},
            optimization_goals=["efficiency", "cost_reduction", "productivity"]
        )

    @pytest.mark.asyncio
    async def test_optimize_field_success(self, service, sample_request):
        """Test successful field optimization analysis."""
        result = await service.optimize_field(sample_request)
        
        assert isinstance(result, FieldOptimizationResult)
        assert result.field_id == sample_request.field_id
        assert result.field_name == sample_request.field_name
        assert 0 <= result.overall_optimization_score <= 10
        assert isinstance(result.optimization_potential, str)
        assert isinstance(result.layout_recommendations, list)
        assert isinstance(result.access_road_recommendations, list)
        assert isinstance(result.equipment_recommendations, list)
        assert isinstance(result.economic_recommendations, list)
        assert isinstance(result.implementation_plan, list)
        assert result.total_implementation_cost >= 0
        assert result.total_annual_savings >= 0
        assert result.overall_roi_percentage >= 0
        assert result.payback_period_years >= 0
        assert isinstance(result.risk_assessment, str)

    @pytest.mark.asyncio
    async def test_analyze_layout_optimization(self, service, sample_request):
        """Test layout optimization analysis."""
        recommendations = await service._analyze_layout_optimization(sample_request)
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, LayoutOptimizationRecommendation)
            assert isinstance(rec.recommendation_type, str)
            assert isinstance(rec.description, str)
            assert 0 <= rec.current_efficiency <= 100
            assert 0 <= rec.optimized_efficiency <= 100
            assert rec.efficiency_gain >= 0
            assert rec.implementation_cost >= 0
            assert isinstance(rec.implementation_time, str)
            assert isinstance(rec.priority, OptimizationPriority)
            assert isinstance(rec.phase, ImplementationPhase)
            assert isinstance(rec.benefits, list)
            assert isinstance(rec.requirements, list)

    @pytest.mark.asyncio
    async def test_analyze_access_optimization(self, service, sample_request):
        """Test access road optimization analysis."""
        recommendations = await service._analyze_access_optimization(sample_request)
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, AccessRoadRecommendation)
            assert isinstance(rec.road_type, str)
            assert rec.length_feet >= 0
            assert rec.width_feet >= 0
            assert isinstance(rec.surface_type, str)
            assert rec.cost_per_foot >= 0
            assert rec.total_cost >= 0
            assert isinstance(rec.construction_time, str)
            assert rec.maintenance_cost_annual >= 0
            assert isinstance(rec.benefits, list)
            assert isinstance(rec.specifications, dict)

    @pytest.mark.asyncio
    async def test_analyze_equipment_optimization(self, service, sample_request):
        """Test equipment optimization analysis."""
        recommendations = await service._analyze_equipment_optimization(sample_request)
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, EquipmentOptimizationRecommendation)
            assert isinstance(rec.equipment_type, str)
            assert 0 <= rec.current_efficiency <= 100
            assert 0 <= rec.recommended_efficiency <= 100
            assert rec.efficiency_improvement >= 0
            assert rec.equipment_cost >= 0
            assert rec.installation_cost >= 0
            assert rec.annual_operating_cost >= 0
            assert rec.payback_period_years >= 0
            assert rec.roi_percentage >= 0
            assert isinstance(rec.benefits, list)
            assert isinstance(rec.specifications, dict)

    @pytest.mark.asyncio
    async def test_analyze_economic_optimization(self, service, sample_request):
        """Test economic optimization analysis."""
        recommendations = await service._analyze_economic_optimization(sample_request)
        
        assert isinstance(recommendations, list)
        for rec in recommendations:
            assert isinstance(rec, EconomicOptimizationRecommendation)
            assert isinstance(rec.optimization_area, str)
            assert rec.current_cost_per_acre >= 0
            assert rec.optimized_cost_per_acre >= 0
            assert rec.cost_savings_per_acre >= 0
            assert rec.total_cost_savings >= 0
            assert rec.implementation_cost >= 0
            assert rec.net_benefit >= 0
            assert rec.payback_period_years >= 0
            assert rec.roi_percentage >= 0
            assert isinstance(rec.risk_assessment, str)
            assert isinstance(rec.benefits, list)

    def test_create_implementation_plan(self, service):
        """Test implementation plan creation."""
        layout_recommendations = [
            LayoutOptimizationRecommendation(
                recommendation_type="field_shape_optimization",
                description="Optimize field boundaries",
                current_efficiency=70.0,
                optimized_efficiency=85.0,
                efficiency_gain=15.0,
                implementation_cost=4000.0,
                implementation_time="6-12 months",
                priority=OptimizationPriority.HIGH,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Improved efficiency"],
                requirements=["Survey equipment"]
            )
        ]
        
        access_recommendations = [
            AccessRoadRecommendation(
                road_type="Perimeter Access Road",
                length_feet=2000.0,
                width_feet=16.0,
                surface_type="Gravel",
                cost_per_foot=25.0,
                total_cost=50000.0,
                construction_time="2-3 months",
                maintenance_cost_annual=4000.0,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Improved access"],
                specifications={"base_thickness": "6 inches"}
            )
        ]
        
        equipment_recommendations = [
            EquipmentOptimizationRecommendation(
                equipment_type="GPS Guidance System",
                current_efficiency=75.0,
                recommended_efficiency=95.0,
                efficiency_improvement=20.0,
                equipment_cost=15000.0,
                installation_cost=2000.0,
                annual_operating_cost=500.0,
                payback_period_years=2.5,
                roi_percentage=40.0,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Improved precision"],
                specifications={"accuracy": "Sub-inch"}
            )
        ]
        
        economic_recommendations = [
            EconomicOptimizationRecommendation(
                optimization_area="Fuel Efficiency",
                current_cost_per_acre=25.0,
                optimized_cost_per_acre=20.0,
                cost_savings_per_acre=5.0,
                total_cost_savings=400.0,
                implementation_cost=800.0,
                net_benefit=400.0,
                payback_period_years=2.0,
                roi_percentage=50.0,
                risk_assessment="Low risk",
                benefits=["Reduced fuel consumption"]
            )
        ]
        
        implementation_plan = service._create_implementation_plan(
            layout_recommendations, access_recommendations,
            equipment_recommendations, economic_recommendations
        )
        
        assert isinstance(implementation_plan, list)
        for plan in implementation_plan:
            assert isinstance(plan, ImplementationPlan)
            assert isinstance(plan.phase, ImplementationPhase)
            assert plan.duration_months > 0
            assert plan.total_cost >= 0
            assert isinstance(plan.priority_recommendations, list)
            assert isinstance(plan.dependencies, list)
            assert isinstance(plan.resources_required, list)
            assert isinstance(plan.success_metrics, list)
            assert isinstance(plan.timeline, list)

    def test_calculate_field_shape_efficiency(self, service):
        """Test field shape efficiency calculation."""
        boundary = {"type": "Polygon", "coordinates": []}
        
        # Test different field sizes
        efficiency_large = service._calculate_field_shape_efficiency(boundary, 250.0)
        efficiency_medium = service._calculate_field_shape_efficiency(boundary, 100.0)
        efficiency_small = service._calculate_field_shape_efficiency(boundary, 25.0)
        
        assert 0 <= efficiency_large <= 1
        assert 0 <= efficiency_medium <= 1
        assert 0 <= efficiency_small <= 1
        assert efficiency_small >= efficiency_medium >= efficiency_large

    def test_calculate_perimeter_length(self, service):
        """Test perimeter length calculation."""
        boundary = {"type": "Polygon", "coordinates": []}
        length = service._calculate_perimeter_length(boundary)
        
        assert length > 0

    def test_calculate_internal_road_length(self, service):
        """Test internal road length calculation."""
        boundary = {"type": "Polygon", "coordinates": []}
        length = service._calculate_internal_road_length(boundary, 100.0)
        
        assert length > 0
        assert length == 100.0 * 50.0  # 50 feet per acre

    def test_calculate_overall_optimization_score(self, service):
        """Test overall optimization score calculation."""
        layout_recommendations = [
            LayoutOptimizationRecommendation(
                recommendation_type="test",
                description="Test recommendation",
                current_efficiency=70.0,
                optimized_efficiency=85.0,
                efficiency_gain=15.0,
                implementation_cost=1000.0,
                implementation_time="1 month",
                priority=OptimizationPriority.HIGH,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Test benefit"],
                requirements=["Test requirement"]
            )
        ]
        
        access_recommendations = [
            AccessRoadRecommendation(
                road_type="Test Road",
                length_feet=1000.0,
                width_feet=12.0,
                surface_type="Gravel",
                cost_per_foot=20.0,
                total_cost=20000.0,
                construction_time="1 month",
                maintenance_cost_annual=1000.0,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Test benefit"],
                specifications={"test": "value"}
            )
        ]
        
        equipment_recommendations = [
            EquipmentOptimizationRecommendation(
                equipment_type="Test Equipment",
                current_efficiency=75.0,
                recommended_efficiency=90.0,
                efficiency_improvement=15.0,
                equipment_cost=10000.0,
                installation_cost=1000.0,
                annual_operating_cost=500.0,
                payback_period_years=2.0,
                roi_percentage=50.0,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Test benefit"],
                specifications={"test": "value"}
            )
        ]
        
        economic_recommendations = [
            EconomicOptimizationRecommendation(
                optimization_area="Test Area",
                current_cost_per_acre=25.0,
                optimized_cost_per_acre=20.0,
                cost_savings_per_acre=5.0,
                total_cost_savings=400.0,
                implementation_cost=800.0,
                net_benefit=400.0,
                payback_period_years=2.0,
                roi_percentage=50.0,
                risk_assessment="Low risk",
                benefits=["Test benefit"]
            )
        ]
        
        score = service._calculate_overall_optimization_score(
            layout_recommendations, access_recommendations,
            equipment_recommendations, economic_recommendations
        )
        
        assert 0 <= score <= 10

    def test_assess_optimization_potential(self, service):
        """Test optimization potential assessment."""
        assert "Very High" in service._assess_optimization_potential(9.0)
        assert "High" in service._assess_optimization_potential(7.5)
        assert "Medium" in service._assess_optimization_potential(6.0)
        assert "Low" in service._assess_optimization_potential(4.5)
        assert "Very Low" in service._assess_optimization_potential(2.0)

    def test_assess_overall_risk(self, service):
        """Test overall risk assessment."""
        layout_recommendations = [
            LayoutOptimizationRecommendation(
                recommendation_type="test",
                description="Test recommendation",
                current_efficiency=70.0,
                optimized_efficiency=85.0,
                efficiency_gain=15.0,
                implementation_cost=50000.0,  # High cost
                implementation_time="1 month",
                priority=OptimizationPriority.HIGH,
                phase=ImplementationPhase.SHORT_TERM,
                benefits=["Test benefit"],
                requirements=["Test requirement"]
            )
        ]
        
        access_recommendations = []
        equipment_recommendations = []
        economic_recommendations = []
        
        risk = service._assess_overall_risk(
            layout_recommendations, access_recommendations,
            equipment_recommendations, economic_recommendations
        )
        
        assert isinstance(risk, str)
        assert len(risk) > 0

    @pytest.mark.asyncio
    async def test_optimize_field_error_handling(self, service, sample_request):
        """Test error handling in field optimization."""
        with patch.object(service, '_analyze_layout_optimization', side_effect=Exception("Layout analysis failed")):
            with pytest.raises(FieldOptimizationError):
                await service.optimize_field(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_layout_optimization_error_handling(self, service, sample_request):
        """Test error handling in layout optimization analysis."""
        with patch.object(service, '_calculate_field_shape_efficiency', side_effect=Exception("Shape calculation failed")):
            with pytest.raises(FieldOptimizationError):
                await service._analyze_layout_optimization(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_access_optimization_error_handling(self, service, sample_request):
        """Test error handling in access optimization analysis."""
        with patch.object(service, '_calculate_perimeter_length', side_effect=Exception("Perimeter calculation failed")):
            with pytest.raises(FieldOptimizationError):
                await service._analyze_access_optimization(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_equipment_optimization_error_handling(self, service, sample_request):
        """Test error handling in equipment optimization analysis."""
        with patch.object(service, '_calculate_equipment_efficiency_score', side_effect=Exception("Equipment calculation failed")):
            with pytest.raises(FieldOptimizationError):
                await service._analyze_equipment_optimization(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_economic_optimization_error_handling(self, service, sample_request):
        """Test error handling in economic optimization analysis."""
        with patch.object(service, '_analyze_economic_optimization', side_effect=Exception("Economic analysis failed")):
            with pytest.raises(FieldOptimizationError):
                await service._analyze_economic_optimization(sample_request)


class TestFieldOptimizationRequest:
    """Test suite for FieldOptimizationRequest model."""

    def test_field_optimization_request_creation(self):
        """Test FieldOptimizationRequest creation."""
        request = FieldOptimizationRequest(
            field_id="test-field",
            field_name="Test Field",
            coordinates=Coordinates(latitude=40.0, longitude=-95.0),
            boundary={"type": "Polygon", "coordinates": []},
            area_acres=100.0,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.0,
            organic_matter_percent=3.5,
            irrigation_available=True,
            tile_drainage=False,
            accessibility="excellent",
            current_equipment=["GPS system", "Precision planter"],
            budget_constraints={"annual_budget": 100000, "max_investment": 200000},
            optimization_goals=["efficiency", "cost_reduction", "productivity"]
        )
        
        assert request.field_id == "test-field"
        assert request.field_name == "Test Field"
        assert request.coordinates.latitude == 40.0
        assert request.coordinates.longitude == -95.0
        assert request.area_acres == 100.0
        assert request.soil_type == "loam"
        assert request.drainage_class == "well_drained"
        assert request.slope_percent == 2.0
        assert request.organic_matter_percent == 3.5
        assert request.irrigation_available is True
        assert request.tile_drainage is False
        assert request.accessibility == "excellent"
        assert len(request.current_equipment) == 2
        assert request.budget_constraints["annual_budget"] == 100000
        assert len(request.optimization_goals) == 3

    def test_field_optimization_request_minimal(self):
        """Test FieldOptimizationRequest with minimal data."""
        request = FieldOptimizationRequest(
            field_id="test-field",
            field_name="Test Field",
            coordinates=Coordinates(latitude=40.0, longitude=-95.0),
            boundary={"type": "Polygon", "coordinates": []},
            area_acres=100.0
        )
        
        assert request.field_id == "test-field"
        assert request.field_name == "Test Field"
        assert request.area_acres == 100.0
        assert request.soil_type is None
        assert request.drainage_class is None
        assert request.slope_percent is None
        assert request.organic_matter_percent is None
        assert request.irrigation_available is False
        assert request.tile_drainage is False
        assert request.accessibility is None
        assert request.current_equipment is None
        assert request.budget_constraints is None
        assert request.optimization_goals is None


class TestOptimizationModels:
    """Test suite for optimization analysis models."""

    def test_layout_optimization_recommendation(self):
        """Test LayoutOptimizationRecommendation model."""
        recommendation = LayoutOptimizationRecommendation(
            recommendation_type="field_shape_optimization",
            description="Optimize field boundaries for better equipment efficiency",
            current_efficiency=70.0,
            optimized_efficiency=85.0,
            efficiency_gain=15.0,
            implementation_cost=4000.0,
            implementation_time="6-12 months",
            priority=OptimizationPriority.HIGH,
            phase=ImplementationPhase.SHORT_TERM,
            benefits=["Improved equipment efficiency", "Reduced fuel consumption"],
            requirements=["Survey equipment", "Earthmoving equipment"]
        )
        
        assert recommendation.recommendation_type == "field_shape_optimization"
        assert recommendation.description == "Optimize field boundaries for better equipment efficiency"
        assert recommendation.current_efficiency == 70.0
        assert recommendation.optimized_efficiency == 85.0
        assert recommendation.efficiency_gain == 15.0
        assert recommendation.implementation_cost == 4000.0
        assert recommendation.implementation_time == "6-12 months"
        assert recommendation.priority == OptimizationPriority.HIGH
        assert recommendation.phase == ImplementationPhase.SHORT_TERM
        assert len(recommendation.benefits) == 2
        assert len(recommendation.requirements) == 2

    def test_access_road_recommendation(self):
        """Test AccessRoadRecommendation model."""
        recommendation = AccessRoadRecommendation(
            road_type="Perimeter Access Road",
            length_feet=2000.0,
            width_feet=16.0,
            surface_type="Gravel",
            cost_per_foot=25.0,
            total_cost=50000.0,
            construction_time="2-3 months",
            maintenance_cost_annual=4000.0,
            phase=ImplementationPhase.SHORT_TERM,
            benefits=["Improved field access", "Reduced soil compaction"],
            specifications={"base_thickness": "6 inches", "gravel_thickness": "4 inches"}
        )
        
        assert recommendation.road_type == "Perimeter Access Road"
        assert recommendation.length_feet == 2000.0
        assert recommendation.width_feet == 16.0
        assert recommendation.surface_type == "Gravel"
        assert recommendation.cost_per_foot == 25.0
        assert recommendation.total_cost == 50000.0
        assert recommendation.construction_time == "2-3 months"
        assert recommendation.maintenance_cost_annual == 4000.0
        assert len(recommendation.benefits) == 2
        assert len(recommendation.specifications) == 2

    def test_equipment_optimization_recommendation(self):
        """Test EquipmentOptimizationRecommendation model."""
        recommendation = EquipmentOptimizationRecommendation(
            equipment_type="GPS Guidance System",
            current_efficiency=75.0,
            recommended_efficiency=95.0,
            efficiency_improvement=20.0,
            equipment_cost=15000.0,
            installation_cost=2000.0,
            annual_operating_cost=500.0,
            payback_period_years=2.5,
            roi_percentage=40.0,
            phase=ImplementationPhase.SHORT_TERM,
            benefits=["Improved precision", "Reduced overlap"],
            specifications={"accuracy": "Sub-inch", "coverage": "RTK correction"}
        )
        
        assert recommendation.equipment_type == "GPS Guidance System"
        assert recommendation.current_efficiency == 75.0
        assert recommendation.recommended_efficiency == 95.0
        assert recommendation.efficiency_improvement == 20.0
        assert recommendation.equipment_cost == 15000.0
        assert recommendation.installation_cost == 2000.0
        assert recommendation.annual_operating_cost == 500.0
        assert recommendation.payback_period_years == 2.5
        assert recommendation.roi_percentage == 40.0
        assert len(recommendation.benefits) == 2
        assert len(recommendation.specifications) == 2

    def test_economic_optimization_recommendation(self):
        """Test EconomicOptimizationRecommendation model."""
        recommendation = EconomicOptimizationRecommendation(
            optimization_area="Fuel Efficiency",
            current_cost_per_acre=25.0,
            optimized_cost_per_acre=20.0,
            cost_savings_per_acre=5.0,
            total_cost_savings=400.0,
            implementation_cost=800.0,
            net_benefit=400.0,
            payback_period_years=2.0,
            roi_percentage=50.0,
            risk_assessment="Low risk - proven technology",
            benefits=["Reduced fuel consumption", "Lower operating costs"]
        )
        
        assert recommendation.optimization_area == "Fuel Efficiency"
        assert recommendation.current_cost_per_acre == 25.0
        assert recommendation.optimized_cost_per_acre == 20.0
        assert recommendation.cost_savings_per_acre == 5.0
        assert recommendation.total_cost_savings == 400.0
        assert recommendation.implementation_cost == 800.0
        assert recommendation.net_benefit == 400.0
        assert recommendation.payback_period_years == 2.0
        assert recommendation.roi_percentage == 50.0
        assert recommendation.risk_assessment == "Low risk - proven technology"
        assert len(recommendation.benefits) == 2

    def test_implementation_plan(self):
        """Test ImplementationPlan model."""
        plan = ImplementationPlan(
            phase=ImplementationPhase.SHORT_TERM,
            duration_months=9,
            total_cost=50000.0,
            priority_recommendations=["field_shape_optimization", "access_road_construction"],
            dependencies=["Immediate phase completion"],
            resources_required=["Construction equipment", "Permits", "Contractors"],
            success_metrics=["Infrastructure improvements", "Accessibility gains"],
            timeline=[
                {"month": 1, "activities": ["Planning and design", "Permit acquisition"]},
                {"month": 2, "activities": ["Construction start", "Progress monitoring"]}
            ]
        )
        
        assert plan.phase == ImplementationPhase.SHORT_TERM
        assert plan.duration_months == 9
        assert plan.total_cost == 50000.0
        assert len(plan.priority_recommendations) == 2
        assert len(plan.dependencies) == 1
        assert len(plan.resources_required) == 3
        assert len(plan.success_metrics) == 2
        assert len(plan.timeline) == 2

    def test_field_optimization_result(self):
        """Test FieldOptimizationResult model."""
        layout_rec = LayoutOptimizationRecommendation(
            recommendation_type="test",
            description="Test recommendation",
            current_efficiency=70.0,
            optimized_efficiency=85.0,
            efficiency_gain=15.0,
            implementation_cost=1000.0,
            implementation_time="1 month",
            priority=OptimizationPriority.HIGH,
            phase=ImplementationPhase.SHORT_TERM,
            benefits=["Test benefit"],
            requirements=["Test requirement"]
        )
        
        access_rec = AccessRoadRecommendation(
            road_type="Test Road",
            length_feet=1000.0,
            width_feet=12.0,
            surface_type="Gravel",
            cost_per_foot=20.0,
            total_cost=20000.0,
            construction_time="1 month",
            maintenance_cost_annual=1000.0,
            benefits=["Test benefit"],
            specifications={"test": "value"}
        )
        
        equipment_rec = EquipmentOptimizationRecommendation(
            equipment_type="Test Equipment",
            current_efficiency=75.0,
            recommended_efficiency=90.0,
            efficiency_improvement=15.0,
            equipment_cost=10000.0,
            installation_cost=1000.0,
            annual_operating_cost=500.0,
            payback_period_years=2.0,
            roi_percentage=50.0,
            benefits=["Test benefit"],
            specifications={"test": "value"}
        )
        
        economic_rec = EconomicOptimizationRecommendation(
            optimization_area="Test Area",
            current_cost_per_acre=25.0,
            optimized_cost_per_acre=20.0,
            cost_savings_per_acre=5.0,
            total_cost_savings=400.0,
            implementation_cost=800.0,
            net_benefit=400.0,
            payback_period_years=2.0,
            roi_percentage=50.0,
            risk_assessment="Low risk",
            benefits=["Test benefit"]
        )
        
        implementation_plan = ImplementationPlan(
            phase=ImplementationPhase.SHORT_TERM,
            duration_months=6,
            total_cost=10000.0,
            priority_recommendations=["test"],
            dependencies=[],
            resources_required=["test"],
            success_metrics=["test"],
            timeline=[]
        )
        
        result = FieldOptimizationResult(
            field_id="test-field",
            field_name="Test Field",
            overall_optimization_score=7.5,
            optimization_potential="High optimization potential",
            layout_recommendations=[layout_rec],
            access_road_recommendations=[access_rec],
            equipment_recommendations=[equipment_rec],
            economic_recommendations=[economic_rec],
            implementation_plan=[implementation_plan],
            total_implementation_cost=10000.0,
            total_annual_savings=400.0,
            overall_roi_percentage=4.0,
            payback_period_years=25.0,
            risk_assessment="Low risk"
        )
        
        assert result.field_id == "test-field"
        assert result.field_name == "Test Field"
        assert result.overall_optimization_score == 7.5
        assert result.optimization_potential == "High optimization potential"
        assert len(result.layout_recommendations) == 1
        assert len(result.access_road_recommendations) == 1
        assert len(result.equipment_recommendations) == 1
        assert len(result.economic_recommendations) == 1
        assert len(result.implementation_plan) == 1
        assert result.total_implementation_cost == 10000.0
        assert result.total_annual_savings == 400.0
        assert result.overall_roi_percentage == 4.0
        assert result.payback_period_years == 25.0
        assert result.risk_assessment == "Low risk"


if __name__ == "__main__":
    pytest.main([__file__])