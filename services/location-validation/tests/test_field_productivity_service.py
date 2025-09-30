"""
Field Productivity Service Tests
CAAIN Soil Hub - TICKET-008_farm-location-input-10.2

Comprehensive tests for field productivity analysis service including:
- Soil productivity analysis tests
- Climate suitability analysis tests
- Field accessibility analysis tests
- Layout optimization tests
- Equipment efficiency analysis tests
- Integration tests
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.field_productivity_service import (
    FieldProductivityService,
    FieldProductivityRequest,
    FieldProductivityResult,
    SoilProductivityAnalysis,
    ClimateSuitabilityAnalysis,
    AccessibilityAnalysis,
    FieldLayoutOptimization,
    EquipmentEfficiencyAnalysis,
    FieldProductivityError,
    ProductivityLevel,
    OptimizationPriority,
    Coordinates
)


class TestFieldProductivityService:
    """Test suite for FieldProductivityService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FieldProductivityService()

    @pytest.fixture
    def sample_request(self):
        """Create sample field productivity request."""
        return FieldProductivityRequest(
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
            accessibility="good"
        )

    @pytest.fixture
    def mock_soil_data(self):
        """Mock soil data for testing."""
        return {
            'soil_series': 'Clarion',
            'texture': 'Clay loam',
            'ph_range': '6.0-7.0',
            'organic_matter': '2-4%',
            'cec': '15-25 meq/100g',
            'drainage_class': 'Well drained'
        }

    @pytest.fixture
    def mock_climate_data(self):
        """Mock climate data for testing."""
        return {
            'avg_temp': 12.5,
            'precipitation': 850,
            'growing_season_days': 180,
            'frost_free_days': 160,
            'drought_frequency': 'moderate'
        }

    @pytest.fixture
    def mock_road_data(self):
        """Mock road data for testing."""
        return {
            'nearest_roads': [
                {'type': 'County Road', 'distance': 0.3},
                {'type': 'State Highway', 'distance': 2.1}
            ],
            'road_quality': 'Good'
        }

    @pytest.mark.asyncio
    async def test_analyze_field_productivity_success(self, service, sample_request):
        """Test successful field productivity analysis."""
        with patch.object(service, 'analyze_soil_productivity', return_value=SoilProductivityAnalysis(
            soil_quality_score=7.5,
            productivity_potential=ProductivityLevel.HIGH,
            soil_limitations=[],
            fertility_status="High fertility",
            improvement_recommendations=["Add organic matter"]
        )):
            with patch.object(service, 'analyze_climate_suitability', return_value=ClimateSuitabilityAnalysis(
                climate_score=8.0,
                growing_season_length=180,
                frost_risk_level="Low",
                drought_risk_level="Moderate",
                suitable_crops=["corn", "soybeans"],
                climate_limitations=[],
                adaptation_recommendations=["Use drought-tolerant varieties"]
            )):
                with patch.object(service, 'analyze_field_accessibility', return_value=AccessibilityAnalysis(
                    accessibility_score=7.0,
                    road_access_quality="Good",
                    equipment_accessibility="Good",
                    field_entrance_quality="Good",
                    operational_efficiency="Good",
                    improvement_opportunities=[]
                )):
                    with patch.object(service, 'optimize_field_layout', return_value=FieldLayoutOptimization(
                        current_layout_score=6.5,
                        optimized_layout_score=8.0,
                        layout_improvements=["Optimize field boundaries"],
                        access_road_recommendations=["Install perimeter road"],
                        field_subdivision_suggestions=[],
                        efficiency_gains={"operational_efficiency_gain": 20.0},
                        implementation_priority=OptimizationPriority.HIGH
                    )):
                        with patch.object(service, 'analyze_equipment_efficiency', return_value=EquipmentEfficiencyAnalysis(
                            equipment_efficiency_score=7.5,
                            recommended_equipment=["Medium tractors"],
                            operational_constraints=[],
                            efficiency_optimizations=["Use GPS guidance"],
                            cost_benefit_analysis={"roi_percentage": 25.0}
                        )):
                            result = await service.analyze_field_productivity(sample_request)
                            
                            assert isinstance(result, FieldProductivityResult)
                            assert result.field_id == sample_request.field_id
                            assert result.field_name == sample_request.field_name
                            assert 0 <= result.overall_productivity_score <= 10
                            assert isinstance(result.productivity_level, ProductivityLevel)
                            assert len(result.optimization_priorities) > 0
                            assert len(result.implementation_roadmap) > 0

    @pytest.mark.asyncio
    async def test_analyze_soil_productivity(self, service, sample_request):
        """Test soil productivity analysis."""
        with patch.object(service, '_get_soil_data', return_value={
            'soil_series': 'Clarion',
            'texture': 'Clay loam',
            'ph_range': '6.0-7.0',
            'organic_matter': '2-4%',
            'cec': '15-25 meq/100g',
            'drainage_class': 'Well drained'
        }):
            result = await service.analyze_soil_productivity(sample_request)
            
            assert isinstance(result, SoilProductivityAnalysis)
            assert 0 <= result.soil_quality_score <= 10
            assert isinstance(result.productivity_potential, ProductivityLevel)
            assert isinstance(result.soil_limitations, list)
            assert isinstance(result.fertility_status, str)
            assert isinstance(result.improvement_recommendations, list)

    @pytest.mark.asyncio
    async def test_analyze_climate_suitability(self, service, sample_request):
        """Test climate suitability analysis."""
        with patch.object(service, '_get_climate_data', return_value={
            'avg_temp': 12.5,
            'precipitation': 850,
            'growing_season_days': 180,
            'frost_free_days': 160,
            'drought_frequency': 'moderate'
        }):
            result = await service.analyze_climate_suitability(sample_request)
            
            assert isinstance(result, ClimateSuitabilityAnalysis)
            assert 0 <= result.climate_score <= 10
            assert isinstance(result.growing_season_length, int)
            assert result.growing_season_length > 0
            assert isinstance(result.frost_risk_level, str)
            assert isinstance(result.drought_risk_level, str)
            assert isinstance(result.suitable_crops, list)
            assert isinstance(result.climate_limitations, list)
            assert isinstance(result.adaptation_recommendations, list)

    @pytest.mark.asyncio
    async def test_analyze_field_accessibility(self, service, sample_request):
        """Test field accessibility analysis."""
        with patch.object(service, '_get_road_network_data', return_value={
            'nearest_roads': [
                {'type': 'County Road', 'distance': 0.3},
                {'type': 'State Highway', 'distance': 2.1}
            ],
            'road_quality': 'Good'
        }):
            result = await service.analyze_field_accessibility(sample_request)
            
            assert isinstance(result, AccessibilityAnalysis)
            assert 0 <= result.accessibility_score <= 10
            assert isinstance(result.road_access_quality, str)
            assert isinstance(result.equipment_accessibility, str)
            assert isinstance(result.field_entrance_quality, str)
            assert isinstance(result.operational_efficiency, str)
            assert isinstance(result.improvement_opportunities, list)

    @pytest.mark.asyncio
    async def test_optimize_field_layout(self, service, sample_request):
        """Test field layout optimization."""
        result = await service.optimize_field_layout(sample_request)
        
        assert isinstance(result, FieldLayoutOptimization)
        assert 0 <= result.current_layout_score <= 10
        assert 0 <= result.optimized_layout_score <= 10
        assert isinstance(result.layout_improvements, list)
        assert isinstance(result.access_road_recommendations, list)
        assert isinstance(result.field_subdivision_suggestions, list)
        assert isinstance(result.efficiency_gains, dict)
        assert isinstance(result.implementation_priority, OptimizationPriority)

    @pytest.mark.asyncio
    async def test_analyze_equipment_efficiency(self, service, sample_request):
        """Test equipment efficiency analysis."""
        result = await service.analyze_equipment_efficiency(sample_request)
        
        assert isinstance(result, EquipmentEfficiencyAnalysis)
        assert 0 <= result.equipment_efficiency_score <= 10
        assert isinstance(result.recommended_equipment, list)
        assert isinstance(result.operational_constraints, list)
        assert isinstance(result.efficiency_optimizations, list)
        assert isinstance(result.cost_benefit_analysis, dict)

    def test_calculate_soil_quality_score(self, service):
        """Test soil quality score calculation."""
        # Test with good soil characteristics
        score = service._calculate_soil_quality_score(
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.0,
            organic_matter_percent=3.5,
            soil_data={}
        )
        assert 0 <= score <= 10
        assert score > 5.0  # Should be good with these characteristics

        # Test with poor soil characteristics
        score_poor = service._calculate_soil_quality_score(
            soil_type="clay",
            drainage_class="poorly_drained",
            slope_percent=15.0,
            organic_matter_percent=1.0,
            soil_data={}
        )
        assert 0 <= score_poor <= 10
        assert score_poor < score  # Should be lower than good characteristics

    def test_determine_soil_productivity_potential(self, service):
        """Test soil productivity potential determination."""
        assert service._determine_soil_productivity_potential(9.0) == ProductivityLevel.VERY_HIGH
        assert service._determine_soil_productivity_potential(7.5) == ProductivityLevel.HIGH
        assert service._determine_soil_productivity_potential(6.0) == ProductivityLevel.MEDIUM
        assert service._determine_soil_productivity_potential(4.5) == ProductivityLevel.LOW
        assert service._determine_soil_productivity_potential(2.0) == ProductivityLevel.VERY_LOW

    def test_identify_soil_limitations(self, service):
        """Test soil limitations identification."""
        limitations = service._identify_soil_limitations(
            soil_type="clay",
            drainage_class="poorly_drained",
            slope_percent=12.0,
            organic_matter_percent=1.0,
            soil_data={}
        )
        
        assert isinstance(limitations, list)
        assert len(limitations) > 0  # Should identify limitations with poor characteristics

    def test_calculate_climate_score(self, service):
        """Test climate score calculation."""
        climate_data = {
            'avg_temp': 15.0,
            'precipitation': 800,
            'growing_season_days': 180
        }
        
        score = service._calculate_climate_score(climate_data)
        assert 0 <= score <= 10

    def test_assess_frost_risk(self, service):
        """Test frost risk assessment."""
        climate_data = {'frost_free_days': 180}
        risk = service._assess_frost_risk(climate_data)
        assert risk in ["Low", "Moderate", "High"]

    def test_assess_drought_risk(self, service):
        """Test drought risk assessment."""
        climate_data = {'drought_frequency': 'low'}
        risk = service._assess_drought_risk(climate_data)
        assert risk in ["Low", "Moderate", "High"]

    def test_identify_suitable_crops(self, service):
        """Test suitable crops identification."""
        climate_data = {
            'growing_season_days': 150,
            'avg_temp': 15.0
        }
        crops = service._identify_suitable_crops(climate_data, "loam")
        
        assert isinstance(crops, list)
        assert len(crops) > 0

    def test_calculate_accessibility_score(self, service):
        """Test accessibility score calculation."""
        road_data = {
            'nearest_roads': [{'type': 'County Road', 'distance': 0.5}]
        }
        boundary = {"type": "Polygon", "coordinates": []}
        
        score = service._calculate_accessibility_score(
            accessibility="good",
            area_acres=100.0,
            road_data=road_data,
            boundary=boundary
        )
        
        assert 0 <= score <= 10

    def test_calculate_overall_productivity_score(self, service):
        """Test overall productivity score calculation."""
        soil_analysis = SoilProductivityAnalysis(
            soil_quality_score=7.0,
            productivity_potential=ProductivityLevel.HIGH,
            soil_limitations=[],
            fertility_status="Good",
            improvement_recommendations=[]
        )
        
        climate_analysis = ClimateSuitabilityAnalysis(
            climate_score=8.0,
            growing_season_length=180,
            frost_risk_level="Low",
            drought_risk_level="Moderate",
            suitable_crops=["corn"],
            climate_limitations=[],
            adaptation_recommendations=[]
        )
        
        accessibility_analysis = AccessibilityAnalysis(
            accessibility_score=7.5,
            road_access_quality="Good",
            equipment_accessibility="Good",
            field_entrance_quality="Good",
            operational_efficiency="Good",
            improvement_opportunities=[]
        )
        
        layout_optimization = FieldLayoutOptimization(
            current_layout_score=6.0,
            optimized_layout_score=8.0,
            layout_improvements=[],
            access_road_recommendations=[],
            field_subdivision_suggestions=[],
            efficiency_gains={},
            implementation_priority=OptimizationPriority.MEDIUM
        )
        
        equipment_analysis = EquipmentEfficiencyAnalysis(
            equipment_efficiency_score=7.0,
            recommended_equipment=[],
            operational_constraints=[],
            efficiency_optimizations=[],
            cost_benefit_analysis={}
        )
        
        score = service._calculate_overall_productivity_score(
            soil_analysis, climate_analysis, accessibility_analysis,
            layout_optimization, equipment_analysis
        )
        
        assert 0 <= score <= 10

    def test_determine_productivity_level(self, service):
        """Test productivity level determination."""
        assert service._determine_productivity_level(9.0) == ProductivityLevel.VERY_HIGH
        assert service._determine_productivity_level(7.5) == ProductivityLevel.HIGH
        assert service._determine_productivity_level(6.0) == ProductivityLevel.MEDIUM
        assert service._determine_productivity_level(4.5) == ProductivityLevel.LOW
        assert service._determine_productivity_level(2.0) == ProductivityLevel.VERY_LOW

    def test_generate_optimization_priorities(self, service):
        """Test optimization priorities generation."""
        soil_analysis = SoilProductivityAnalysis(
            soil_quality_score=4.0,  # Low score
            productivity_potential=ProductivityLevel.LOW,
            soil_limitations=[],
            fertility_status="Poor",
            improvement_recommendations=[]
        )
        
        climate_analysis = ClimateSuitabilityAnalysis(
            climate_score=8.0,  # High score
            growing_season_length=180,
            frost_risk_level="Low",
            drought_risk_level="Moderate",
            suitable_crops=["corn"],
            climate_limitations=[],
            adaptation_recommendations=[]
        )
        
        accessibility_analysis = AccessibilityAnalysis(
            accessibility_score=7.5,  # Good score
            road_access_quality="Good",
            equipment_accessibility="Good",
            field_entrance_quality="Good",
            operational_efficiency="Good",
            improvement_opportunities=[]
        )
        
        layout_optimization = FieldLayoutOptimization(
            current_layout_score=5.0,  # Medium score
            optimized_layout_score=8.0,
            layout_improvements=[],
            access_road_recommendations=[],
            field_subdivision_suggestions=[],
            efficiency_gains={},
            implementation_priority=OptimizationPriority.MEDIUM
        )
        
        equipment_analysis = EquipmentEfficiencyAnalysis(
            equipment_efficiency_score=6.0,  # Medium score
            recommended_equipment=[],
            operational_constraints=[],
            efficiency_optimizations=[],
            cost_benefit_analysis={}
        )
        
        priorities = service._generate_optimization_priorities(
            soil_analysis, climate_analysis, accessibility_analysis,
            layout_optimization, equipment_analysis
        )
        
        assert isinstance(priorities, list)
        assert len(priorities) > 0
        # Should prioritize soil health since it has the lowest score
        assert any("Soil Health" in priority for priority in priorities)

    def test_create_implementation_roadmap(self, service):
        """Test implementation roadmap creation."""
        priorities = ["Improve Soil Health (Current Score: 4.0)", "Improve Layout Optimization (Current Score: 5.0)"]
        roadmap = service._create_implementation_roadmap(priorities)
        
        assert isinstance(roadmap, list)
        assert len(roadmap) > 0

    @pytest.mark.asyncio
    async def test_analyze_field_productivity_error_handling(self, service, sample_request):
        """Test error handling in field productivity analysis."""
        with patch.object(service, 'analyze_soil_productivity', side_effect=Exception("Soil analysis failed")):
            with pytest.raises(FieldProductivityError):
                await service.analyze_field_productivity(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_soil_productivity_error_handling(self, service, sample_request):
        """Test error handling in soil productivity analysis."""
        with patch.object(service, '_get_soil_data', side_effect=Exception("Soil data unavailable")):
            with pytest.raises(FieldProductivityError):
                await service.analyze_soil_productivity(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_climate_suitability_error_handling(self, service, sample_request):
        """Test error handling in climate suitability analysis."""
        with patch.object(service, '_get_climate_data', side_effect=Exception("Climate data unavailable")):
            with pytest.raises(FieldProductivityError):
                await service.analyze_climate_suitability(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_field_accessibility_error_handling(self, service, sample_request):
        """Test error handling in field accessibility analysis."""
        with patch.object(service, '_get_road_network_data', side_effect=Exception("Road data unavailable")):
            with pytest.raises(FieldProductivityError):
                await service.analyze_field_accessibility(sample_request)

    @pytest.mark.asyncio
    async def test_service_close(self, service):
        """Test service cleanup."""
        # Mock session
        service.session = AsyncMock()
        await service.close()
        service.session.close.assert_called_once()


class TestFieldProductivityRequest:
    """Test suite for FieldProductivityRequest model."""

    def test_field_productivity_request_creation(self):
        """Test FieldProductivityRequest creation."""
        request = FieldProductivityRequest(
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
            accessibility="excellent"
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

    def test_field_productivity_request_minimal(self):
        """Test FieldProductivityRequest with minimal data."""
        request = FieldProductivityRequest(
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


class TestProductivityModels:
    """Test suite for productivity analysis models."""

    def test_soil_productivity_analysis(self):
        """Test SoilProductivityAnalysis model."""
        analysis = SoilProductivityAnalysis(
            soil_quality_score=7.5,
            productivity_potential=ProductivityLevel.HIGH,
            soil_limitations=["Low organic matter"],
            fertility_status="Good",
            improvement_recommendations=["Add compost"]
        )
        
        assert analysis.soil_quality_score == 7.5
        assert analysis.productivity_potential == ProductivityLevel.HIGH
        assert len(analysis.soil_limitations) == 1
        assert analysis.fertility_status == "Good"
        assert len(analysis.improvement_recommendations) == 1
        assert isinstance(analysis.analysis_timestamp, datetime)

    def test_climate_suitability_analysis(self):
        """Test ClimateSuitabilityAnalysis model."""
        analysis = ClimateSuitabilityAnalysis(
            climate_score=8.0,
            growing_season_length=180,
            frost_risk_level="Low",
            drought_risk_level="Moderate",
            suitable_crops=["corn", "soybeans"],
            climate_limitations=[],
            adaptation_recommendations=["Use drought-tolerant varieties"]
        )
        
        assert analysis.climate_score == 8.0
        assert analysis.growing_season_length == 180
        assert analysis.frost_risk_level == "Low"
        assert analysis.drought_risk_level == "Moderate"
        assert len(analysis.suitable_crops) == 2
        assert len(analysis.climate_limitations) == 0
        assert len(analysis.adaptation_recommendations) == 1

    def test_accessibility_analysis(self):
        """Test AccessibilityAnalysis model."""
        analysis = AccessibilityAnalysis(
            accessibility_score=7.0,
            road_access_quality="Good",
            equipment_accessibility="Good",
            field_entrance_quality="Good",
            operational_efficiency="Good",
            improvement_opportunities=["Improve field roads"]
        )
        
        assert analysis.accessibility_score == 7.0
        assert analysis.road_access_quality == "Good"
        assert analysis.equipment_accessibility == "Good"
        assert analysis.field_entrance_quality == "Good"
        assert analysis.operational_efficiency == "Good"
        assert len(analysis.improvement_opportunities) == 1

    def test_field_layout_optimization(self):
        """Test FieldLayoutOptimization model."""
        optimization = FieldLayoutOptimization(
            current_layout_score=6.0,
            optimized_layout_score=8.0,
            layout_improvements=["Optimize boundaries"],
            access_road_recommendations=["Install perimeter road"],
            field_subdivision_suggestions=["Subdivide large field"],
            efficiency_gains={"operational_efficiency_gain": 25.0},
            implementation_priority=OptimizationPriority.HIGH
        )
        
        assert optimization.current_layout_score == 6.0
        assert optimization.optimized_layout_score == 8.0
        assert len(optimization.layout_improvements) == 1
        assert len(optimization.access_road_recommendations) == 1
        assert len(optimization.field_subdivision_suggestions) == 1
        assert optimization.efficiency_gains["operational_efficiency_gain"] == 25.0
        assert optimization.implementation_priority == OptimizationPriority.HIGH

    def test_equipment_efficiency_analysis(self):
        """Test EquipmentEfficiencyAnalysis model."""
        analysis = EquipmentEfficiencyAnalysis(
            equipment_efficiency_score=7.5,
            recommended_equipment=["Medium tractors", "GPS guidance"],
            operational_constraints=["Steep slopes"],
            efficiency_optimizations=["Use precision agriculture"],
            cost_benefit_analysis={"roi_percentage": 30.0, "payback_period_years": 3.0}
        )
        
        assert analysis.equipment_efficiency_score == 7.5
        assert len(analysis.recommended_equipment) == 2
        assert len(analysis.operational_constraints) == 1
        assert len(analysis.efficiency_optimizations) == 1
        assert analysis.cost_benefit_analysis["roi_percentage"] == 30.0
        assert analysis.cost_benefit_analysis["payback_period_years"] == 3.0

    def test_field_productivity_result(self):
        """Test FieldProductivityResult model."""
        soil_analysis = SoilProductivityAnalysis(
            soil_quality_score=7.0,
            productivity_potential=ProductivityLevel.HIGH,
            soil_limitations=[],
            fertility_status="Good",
            improvement_recommendations=[]
        )
        
        climate_analysis = ClimateSuitabilityAnalysis(
            climate_score=8.0,
            growing_season_length=180,
            frost_risk_level="Low",
            drought_risk_level="Moderate",
            suitable_crops=["corn"],
            climate_limitations=[],
            adaptation_recommendations=[]
        )
        
        accessibility_analysis = AccessibilityAnalysis(
            accessibility_score=7.5,
            road_access_quality="Good",
            equipment_accessibility="Good",
            field_entrance_quality="Good",
            operational_efficiency="Good",
            improvement_opportunities=[]
        )
        
        layout_optimization = FieldLayoutOptimization(
            current_layout_score=6.0,
            optimized_layout_score=8.0,
            layout_improvements=[],
            access_road_recommendations=[],
            field_subdivision_suggestions=[],
            efficiency_gains={},
            implementation_priority=OptimizationPriority.MEDIUM
        )
        
        equipment_analysis = EquipmentEfficiencyAnalysis(
            equipment_efficiency_score=7.0,
            recommended_equipment=[],
            operational_constraints=[],
            efficiency_optimizations=[],
            cost_benefit_analysis={}
        )
        
        result = FieldProductivityResult(
            field_id="test-field",
            field_name="Test Field",
            overall_productivity_score=7.5,
            productivity_level=ProductivityLevel.HIGH,
            soil_analysis=soil_analysis,
            climate_analysis=climate_analysis,
            accessibility_analysis=accessibility_analysis,
            layout_optimization=layout_optimization,
            equipment_analysis=equipment_analysis,
            optimization_priorities=["Improve soil health"],
            implementation_roadmap=["Phase 1: Address critical limitations"]
        )
        
        assert result.field_id == "test-field"
        assert result.field_name == "Test Field"
        assert result.overall_productivity_score == 7.5
        assert result.productivity_level == ProductivityLevel.HIGH
        assert len(result.optimization_priorities) == 1
        assert len(result.implementation_roadmap) == 1


if __name__ == "__main__":
    pytest.main([__file__])