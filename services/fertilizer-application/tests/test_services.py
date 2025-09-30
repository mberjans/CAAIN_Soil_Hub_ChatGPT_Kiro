"""
Tests for the fertilizer application services.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.application_method_service import ApplicationMethodService
from src.services.equipment_assessment_service import EquipmentAssessmentService
from src.services.cost_analysis_service import CostAnalysisService
from src.services.guidance_service import GuidanceService
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, FieldConditions, 
    CropRequirements, FertilizerSpecification, EquipmentSpecification
)
from src.models.equipment_models import Equipment, EquipmentCategory, EquipmentStatus


class TestApplicationMethodService:
    """Test cases for ApplicationMethodService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ApplicationMethodService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample application request."""
        return ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=100.0,
                soil_type="loam",
                drainage_class="well_drained",
                slope_percent=2.5,
                irrigation_available=True
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="vegetative",
                target_yield=180.0,
                nutrient_requirements={"nitrogen": 150.0}
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="liquid",
                npk_ratio="28-0-0",
                form="liquid",
                cost_per_unit=0.85,
                unit="lbs"
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_type="sprayer",
                    capacity=500.0,
                    capacity_unit="gallons"
                )
            ]
        )
    
    @pytest.mark.asyncio
    async def test_select_application_methods(self, service, sample_request):
        """Test application method selection."""
        response = await service.select_application_methods(sample_request)
        
        assert isinstance(response, ApplicationResponse)
        assert response.request_id is not None
        assert len(response.recommended_methods) > 0
        assert response.primary_recommendation is not None
        assert response.processing_time_ms > 0
    
    def test_categorize_field_size(self, service):
        """Test field size categorization."""
        assert service._categorize_field_size(5.0) == "small"
        assert service._categorize_field_size(50.0) == "medium"
        assert service._categorize_field_size(500.0) == "large"
        assert service._categorize_field_size(2000.0) == "very_large"
    
    def test_assess_soil_suitability(self, service):
        """Test soil suitability assessment."""
        clay_suitability = service._assess_soil_suitability("clay")
        assert "broadcast" in clay_suitability
        assert "band" in clay_suitability
        assert "injection" in clay_suitability
        assert "drip" in clay_suitability
    
    def test_calculate_field_size_score(self, service):
        """Test field size score calculation."""
        score = service._calculate_field_size_score("medium", (1, 100))
        assert score == 1.0
        
        score = service._calculate_field_size_score("small", (100, 1000))
        assert score == 0.5
    
    def test_calculate_equipment_compatibility_score(self, service):
        """Test equipment compatibility score calculation."""
        score = service._calculate_equipment_compatibility_score(
            ["sprayer"], ["sprayer", "spreader"]
        )
        assert score == 1.0
        
        score = service._calculate_equipment_compatibility_score(
            ["sprayer", "spreader"], ["sprayer"]
        )
        assert score == 0.5
    
    def test_calculate_fertilizer_compatibility_score(self, service):
        """Test fertilizer compatibility score calculation."""
        from src.models.application_models import FertilizerForm
        
        score = service._calculate_fertilizer_compatibility_score(
            [FertilizerForm.LIQUID], FertilizerForm.LIQUID
        )
        assert score == 1.0
        
        score = service._calculate_fertilizer_compatibility_score(
            [FertilizerForm.GRANULAR], FertilizerForm.LIQUID
        )
        assert score == 0.0


class TestEquipmentAssessmentService:
    """Test cases for EquipmentAssessmentService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return EquipmentAssessmentService()
    
    @pytest.fixture
    def sample_equipment(self):
        """Create sample equipment."""
        return Equipment(
            equipment_id="sprayer_001",
            name="John Deere Sprayer",
            category=EquipmentCategory.SPRAYING,
            manufacturer="John Deere",
            model="R4038",
            year=2020,
            capacity=500.0,
            capacity_unit="gallons",
            status=EquipmentStatus.OPERATIONAL,
            purchase_price=150000.0,
            current_value=120000.0
        )
    
    def test_categorize_farm_size(self, service):
        """Test farm size categorization."""
        assert service._categorize_farm_size(50.0) == "small"
        assert service._categorize_farm_size(250.0) == "medium"
        assert service._categorize_farm_size(1000.0) == "large"
        assert service._categorize_farm_size(3000.0) == "very_large"
    
    def test_calculate_suitability_score(self, service, sample_equipment):
        """Test equipment suitability score calculation."""
        farm_analysis = {
            "farm_size_category": "medium",
            "maintenance_capability": "basic"
        }
        
        score = service._calculate_suitability_score(sample_equipment, farm_analysis)
        assert 0.0 <= score <= 1.0
    
    def test_assess_capacity_adequacy(self, service, sample_equipment):
        """Test capacity adequacy assessment."""
        farm_analysis = {"farm_size_category": "medium"}
        
        adequacy = service._assess_capacity_adequacy(sample_equipment, farm_analysis)
        assert adequacy in ["insufficient", "adequate", "excessive", "unknown"]
    
    def test_calculate_efficiency_rating(self, service, sample_equipment):
        """Test efficiency rating calculation."""
        rating = service._calculate_efficiency_rating(sample_equipment)
        assert 0.0 <= rating <= 1.0
    
    def test_calculate_cost_effectiveness(self, service, sample_equipment):
        """Test cost effectiveness calculation."""
        effectiveness = service._calculate_cost_effectiveness(sample_equipment)
        assert 0.0 <= effectiveness <= 1.0


class TestCostAnalysisService:
    """Test cases for CostAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CostAnalysisService()
    
    @pytest.fixture
    def sample_application_method(self):
        """Create sample application method."""
        from src.models.application_models import ApplicationMethod, ApplicationMethodType
        
        return ApplicationMethod(
            method_id="foliar_001",
            method_type=ApplicationMethodType.FOLIAR,
            recommended_equipment=EquipmentSpecification(
                equipment_type="sprayer",
                capacity=500.0,
                capacity_unit="gallons"
            ),
            application_rate=2.5,
            rate_unit="gallons/acre",
            application_timing="Early morning",
            efficiency_score=0.9,
            cost_per_acre=30.0,
            labor_requirements="high",
            environmental_impact="low",
            pros=["High efficiency"],
            cons=["Weather sensitive"]
        )
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions."""
        return FieldConditions(
            field_size_acres=100.0,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.5,
            irrigation_available=True
        )
    
    @pytest.fixture
    def sample_crop_requirements(self):
        """Create sample crop requirements."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="vegetative",
            target_yield=180.0,
            nutrient_requirements={"nitrogen": 150.0}
        )
    
    @pytest.fixture
    def sample_fertilizer_specification(self):
        """Create sample fertilizer specification."""
        return FertilizerSpecification(
            fertilizer_type="liquid",
            npk_ratio="28-0-0",
            form="liquid",
            cost_per_unit=0.85,
            unit="lbs"
        )
    
    @pytest.mark.asyncio
    async def test_analyze_application_costs(
        self, 
        service, 
        sample_application_method,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification
    ):
        """Test application cost analysis."""
        cost_analysis = await service.analyze_application_costs(
            [sample_application_method],
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            []
        )
        
        assert "method_costs" in cost_analysis
        assert "comparative_analysis" in cost_analysis
        assert "optimization_recommendations" in cost_analysis
        assert "roi_analysis" in cost_analysis
        assert "sensitivity_analysis" in cost_analysis
        assert cost_analysis["processing_time_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_calculate_fertilizer_costs(
        self,
        service,
        sample_application_method,
        sample_fertilizer_specification,
        sample_crop_requirements
    ):
        """Test fertilizer cost calculation."""
        costs = await service._calculate_fertilizer_costs(
            sample_application_method,
            sample_fertilizer_specification,
            sample_crop_requirements
        )
        
        assert "base_cost_per_unit" in costs
        assert "application_rate" in costs
        assert "efficiency_factor" in costs
        assert "cost_per_acre" in costs
        assert "total_cost" in costs
        assert costs["cost_per_acre"] > 0
    
    @pytest.mark.asyncio
    async def test_calculate_equipment_costs(
        self,
        service,
        sample_application_method,
        sample_field_conditions
    ):
        """Test equipment cost calculation."""
        costs = await service._calculate_equipment_costs(
            sample_application_method,
            sample_field_conditions,
            []
        )
        
        assert "equipment_type" in costs
        assert "total_cost" in costs
        assert "cost_per_acre" in costs
        assert costs["cost_per_acre"] >= 0
    
    @pytest.mark.asyncio
    async def test_calculate_labor_costs(
        self,
        service,
        sample_application_method,
        sample_field_conditions,
        sample_crop_requirements
    ):
        """Test labor cost calculation."""
        costs = await service._calculate_labor_costs(
            sample_application_method,
            sample_field_conditions,
            sample_crop_requirements
        )
        
        assert "skill_level" in costs
        assert "labor_rate" in costs
        assert "labor_hours" in costs
        assert "total_cost" in costs
        assert "cost_per_acre" in costs
        assert costs["total_cost"] > 0
    
    def test_determine_labor_skill_level(self, service):
        """Test labor skill level determination."""
        from src.models.application_models import ApplicationMethodType
        
        skill_level = service._determine_labor_skill_level(ApplicationMethodType.BROADCAST)
        assert skill_level in ["skilled", "semi_skilled", "unskilled"]
        
        skill_level = service._determine_labor_skill_level(ApplicationMethodType.FOLIAR)
        assert skill_level == "skilled"
    
    def test_determine_fuel_type(self, service):
        """Test fuel type determination."""
        fuel_type = service._determine_fuel_type("sprayer")
        assert fuel_type in ["diesel", "gasoline", "electric"]
        
        fuel_type = service._determine_fuel_type("drip_system")
        assert fuel_type == "electric"


class TestGuidanceService:
    """Test cases for GuidanceService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return GuidanceService()
    
    @pytest.fixture
    def sample_application_method(self):
        """Create sample application method."""
        from src.models.application_models import ApplicationMethod, ApplicationMethodType
        
        return ApplicationMethod(
            method_id="foliar_001",
            method_type=ApplicationMethodType.FOLIAR,
            recommended_equipment=EquipmentSpecification(
                equipment_type="sprayer",
                capacity=500.0,
                capacity_unit="gallons"
            ),
            application_rate=2.5,
            rate_unit="gallons/acre",
            application_timing="Early morning",
            efficiency_score=0.9,
            cost_per_acre=30.0,
            labor_requirements="high",
            environmental_impact="low",
            pros=["High efficiency"],
            cons=["Weather sensitive"]
        )
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions."""
        return FieldConditions(
            field_size_acres=100.0,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.5,
            irrigation_available=True
        )
    
    @pytest.fixture
    def sample_guidance_request(self, sample_application_method, sample_field_conditions):
        """Create sample guidance request."""
        from src.models.application_models import GuidanceRequest
        
        return GuidanceRequest(
            application_method=sample_application_method,
            field_conditions=sample_field_conditions,
            weather_conditions={
                "temperature_celsius": 22.0,
                "humidity_percent": 65.0,
                "wind_speed_kmh": 8.0,
                "precipitation_mm": 0.0
            },
            application_date="2024-05-15",
            experience_level="intermediate"
        )
    
    @pytest.mark.asyncio
    async def test_provide_application_guidance(self, service, sample_guidance_request):
        """Test application guidance provision."""
        response = await service.provide_application_guidance(sample_guidance_request)
        
        assert response.request_id is not None
        assert response.guidance is not None
        assert response.processing_time_ms > 0
        
        guidance = response.guidance
        assert guidance.guidance_id is not None
        assert len(guidance.pre_application_checklist) > 0
        assert len(guidance.application_instructions) > 0
        assert len(guidance.safety_precautions) > 0
        assert len(guidance.troubleshooting_tips) > 0
    
    @pytest.mark.asyncio
    async def test_get_method_guidance(self, service, sample_application_method):
        """Test method-specific guidance retrieval."""
        guidance = await service._get_method_guidance(sample_application_method)
        
        assert "pre_application" in guidance
        assert "application" in guidance
        assert "post_application" in guidance
        assert "safety" in guidance
        assert "calibration" in guidance
        assert "troubleshooting" in guidance
        
        assert len(guidance["pre_application"]) > 0
        assert len(guidance["application"]) > 0
        assert len(guidance["safety"]) > 0
    
    @pytest.mark.asyncio
    async def test_generate_weather_advisories(self, service, sample_application_method):
        """Test weather advisory generation."""
        weather_conditions = {
            "temperature_celsius": 35.0,
            "humidity_percent": 20.0,
            "wind_speed_kmh": 20.0,
            "precipitation_mm": 5.0
        }
        
        advisories = await service._generate_weather_advisories(
            weather_conditions, sample_application_method
        )
        
        assert advisories is not None
        assert len(advisories) > 0
        assert any("High temperature" in advisory for advisory in advisories)
        assert any("High wind" in advisory for advisory in advisories)
        assert any("Precipitation" in advisory for advisory in advisories)
    
    @pytest.mark.asyncio
    async def test_generate_equipment_preparation(self, service, sample_application_method, sample_field_conditions):
        """Test equipment preparation generation."""
        preparation = await service._generate_equipment_preparation(
            sample_application_method, sample_field_conditions
        )
        
        assert preparation is not None
        assert len(preparation) > 0
        assert any("Inspect equipment" in step for step in preparation)
        assert any("Check" in step for step in preparation)
    
    @pytest.mark.asyncio
    async def test_generate_quality_control_measures(self, service, sample_application_method, sample_field_conditions):
        """Test quality control measures generation."""
        measures = await service._generate_quality_control_measures(
            sample_application_method, sample_field_conditions
        )
        
        assert measures is not None
        assert len(measures) > 0
        assert any("Monitor" in measure for measure in measures)
        assert any("Verify" in measure for measure in measures)
    
    def test_determine_optimal_conditions(self, service, sample_application_method, sample_field_conditions):
        """Test optimal conditions determination."""
        weather_conditions = {
            "temperature_celsius": 22.0,
            "humidity_percent": 65.0,
            "wind_speed_kmh": 8.0
        }
        
        conditions = service._determine_optimal_conditions(
            sample_application_method, sample_field_conditions, weather_conditions
        )
        
        assert "temperature_range" in conditions
        assert "humidity_range" in conditions
        assert "wind_speed_max" in conditions
        assert "soil_moisture" in conditions
    
    def test_generate_timing_recommendations(self, service, sample_application_method, sample_field_conditions):
        """Test timing recommendations generation."""
        recommendations = service._generate_timing_recommendations(
            sample_application_method, sample_field_conditions, "2024-05-15"
        )
        
        assert recommendations is not None
        assert "early morning" in recommendations.lower()
        assert "late evening" in recommendations.lower()