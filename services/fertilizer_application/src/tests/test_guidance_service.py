"""
Comprehensive test suite for the Enhanced Guidance Service.

This test suite validates the comprehensive fertilizer application guidance system including
step-by-step guidance, timing recommendations, calibration support, troubleshooting,
interactive guides, video tutorials, expert consultation, regulatory compliance,
and educational content.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, datetime
from typing import Dict, Any, List

from src.services.guidance_service import GuidanceService, ExperienceLevel, GuidanceType
from src.models.application_models import (
    GuidanceRequest, GuidanceResponse, ApplicationGuidance,
    ApplicationMethod, FieldConditions
)


class TestGuidanceService:
    """Test suite for GuidanceService functionality."""

    @pytest.fixture
    def guidance_service(self):
        """Create guidance service instance for testing."""
        return GuidanceService()

    @pytest.fixture
    def sample_application_method(self):
        """Create sample application method for testing."""
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        return ApplicationMethod(
            method_id="test_method_1",
            method_type="broadcast",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=1000.0,
                capacity_unit="lbs",
                application_width=30.0,
                application_rate_range={"min": 50.0, "max": 300.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=15.0
            ),
            application_rate=150.0,
            rate_unit="lbs/acre",
            application_timing="flexible",
            efficiency_score=0.85,
            cost_per_acre=25.0,
            labor_requirements="medium",
            environmental_impact="low",
            pros=["Uniform coverage", "Fast application", "Equipment availability"],
            cons=["Wind sensitivity", "Potential drift", "Higher fertilizer loss"]
        )

    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions for testing."""
        return FieldConditions(
            field_size_acres=50.0,
            soil_type="clay_loam",
            slope_percent=3.0,
            drainage_class="well_drained",
            irrigation_available=True,
            field_shape="rectangular",
            access_roads=["main_road", "field_access"]
        )

    @pytest.fixture
    def sample_weather_conditions(self):
        """Create sample weather conditions for testing."""
        return {
            "temperature_celsius": 22.0,
            "humidity_percent": 65.0,
            "wind_speed_kmh": 8.0,
            "precipitation_mm": 0.0,
            "conditions": "clear"
        }

    @pytest.fixture
    def sample_guidance_request(self, sample_application_method, sample_field_conditions, sample_weather_conditions):
        """Create sample guidance request for testing."""
        return GuidanceRequest(
            application_method=sample_application_method,
            field_conditions=sample_field_conditions,
            weather_conditions=sample_weather_conditions,
            application_date=date(2024, 6, 15),
            experience_level="intermediate"
        )

    def test_guidance_service_initialization(self, guidance_service):
        """Test guidance service initialization."""
        assert guidance_service is not None
        assert hasattr(guidance_service, 'guidance_database')
        assert isinstance(guidance_service.guidance_database, dict)
        
        # Check that all application methods are in the database
        expected_methods = ["broadcast", "band", "sidedress", "foliar", "injection", "drip"]
        for method in expected_methods:
            assert method in guidance_service.guidance_database

    def test_guidance_database_structure(self, guidance_service):
        """Test guidance database structure and content."""
        for method_type, guidance_data in guidance_service.guidance_database.items():
            # Check required guidance categories
            required_categories = [
                "pre_application", "application", "post_application",
                "safety", "calibration", "troubleshooting"
            ]
            
            for category in required_categories:
                assert category in guidance_data
                assert isinstance(guidance_data[category], list)
                assert len(guidance_data[category]) > 0
                
                # Check that each item is a string
                for item in guidance_data[category]:
                    assert isinstance(item, str)
                    assert len(item.strip()) > 0

    @pytest.mark.asyncio
    async def test_provide_application_guidance_success(self, guidance_service, sample_guidance_request):
        """Test successful application guidance provision."""
        response = await guidance_service.provide_application_guidance(sample_guidance_request)
        
        # Validate response structure
        assert isinstance(response, GuidanceResponse)
        assert response.request_id is not None
        assert isinstance(response.guidance, ApplicationGuidance)
        assert response.processing_time_ms > 0
        
        # Validate guidance content
        guidance = response.guidance
        assert guidance.guidance_id is not None
        assert len(guidance.pre_application_checklist) > 0
        assert len(guidance.application_instructions) > 0
        assert len(guidance.safety_precautions) > 0
        assert len(guidance.calibration_instructions) > 0
        assert len(guidance.troubleshooting_tips) > 0
        assert len(guidance.post_application_tasks) > 0
        assert isinstance(guidance.optimal_conditions, dict)
        assert guidance.timing_recommendations is not None

    @pytest.mark.asyncio
    async def test_provide_application_guidance_different_methods(self, guidance_service, sample_field_conditions, sample_weather_conditions):
        """Test guidance provision for different application methods."""
        methods_to_test = ["broadcast", "band", "sidedress", "foliar", "injection", "drip"]
        
        for method_type in methods_to_test:
            from src.models.application_models import EquipmentSpecification, EquipmentType
            
            # Map method types to appropriate equipment types
            equipment_type_map = {
                "broadcast": EquipmentType.SPREADER,
                "band": EquipmentType.SPREADER,
                "sidedress": EquipmentType.INJECTOR,
                "foliar": EquipmentType.SPRAYER,
                "injection": EquipmentType.INJECTOR,
                "drip": EquipmentType.DRIP_SYSTEM
            }
            
            application_method = ApplicationMethod(
                method_id=f"test_{method_type}",
                method_type=method_type,
                recommended_equipment=EquipmentSpecification(
                    equipment_type=equipment_type_map.get(method_type, EquipmentType.SPREADER),
                    capacity=500.0,
                    capacity_unit="lbs",
                    application_width=20.0,
                    application_rate_range={"min": 25.0, "max": 200.0},
                    fuel_efficiency=0.7,
                    maintenance_cost_per_hour=10.0
                ),
                application_rate=100.0,
                rate_unit="lbs/acre",
                application_timing="flexible",
                efficiency_score=0.8,
                cost_per_acre=20.0,
                labor_requirements="medium",
                environmental_impact="low",
                pros=[],
                cons=[]
            )
            
            request = GuidanceRequest(
                application_method=application_method,
                field_conditions=sample_field_conditions,
                weather_conditions=sample_weather_conditions,
                application_date=date(2024, 6, 15)
            )
            
            response = await guidance_service.provide_application_guidance(request)
            
            # Validate that guidance is method-specific
            assert response.guidance is not None
            assert len(response.guidance.pre_application_checklist) > 0
            assert len(response.guidance.application_instructions) > 0

    @pytest.mark.asyncio
    async def test_get_method_guidance_existing_method(self, guidance_service, sample_application_method):
        """Test getting guidance for existing application method."""
        guidance = await guidance_service._get_method_guidance(sample_application_method)
        
        assert isinstance(guidance, dict)
        assert "pre_application" in guidance
        assert "application" in guidance
        assert "post_application" in guidance
        assert "safety" in guidance
        assert "calibration" in guidance
        assert "troubleshooting" in guidance
        
        # Check that guidance is specific to broadcast method
        assert len(guidance["pre_application"]) > 0
        assert any("spreader" in item.lower() for item in guidance["pre_application"])

    @pytest.mark.asyncio
    async def test_get_method_guidance_unknown_method(self, guidance_service):
        """Test getting guidance for unknown application method."""
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        # Create a method with a type that's not in the guidance database
        unknown_method = ApplicationMethod(
            method_id="unknown",
            method_type="broadcast",  # Use valid enum value
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=100.0,
                capacity_unit="lbs",
                application_width=10.0,
                application_rate_range={"min": 10.0, "max": 50.0},
                fuel_efficiency=0.5,
                maintenance_cost_per_hour=5.0
            ),
            application_rate=0,
            rate_unit="lbs/acre",
            application_timing="flexible",
            efficiency_score=0.0,
            cost_per_acre=0.0,
            labor_requirements="low",
            environmental_impact="low",
            pros=[],
            cons=[]
        )
        
        # Mock the method_type to simulate an unknown method
        unknown_method.method_type = "unknown_method"
        
        guidance = await guidance_service._get_method_guidance(unknown_method)
        
        # Should return generic guidance
        assert isinstance(guidance, dict)
        assert "pre_application" in guidance
        assert "application" in guidance
        assert "post_application" in guidance
        assert "safety" in guidance
        assert "calibration" in guidance
        assert "troubleshooting" in guidance

    @pytest.mark.asyncio
    async def test_generate_weather_advisories_optimal_conditions(self, guidance_service, sample_application_method):
        """Test weather advisories generation for optimal conditions."""
        optimal_weather = {
            "temperature_celsius": 20.0,
            "humidity_percent": 60.0,
            "wind_speed_kmh": 5.0,
            "precipitation_mm": 0.0
        }
        
        advisories = await guidance_service._generate_weather_advisories(optimal_weather, sample_application_method)
        
        # Should have minimal or no advisories for optimal conditions
        assert advisories is None or len(advisories) == 0

    @pytest.mark.asyncio
    async def test_generate_weather_advisories_adverse_conditions(self, guidance_service, sample_application_method):
        """Test weather advisories generation for adverse conditions."""
        adverse_weather = {
            "temperature_celsius": 35.0,
            "humidity_percent": 85.0,
            "wind_speed_kmh": 20.0,
            "precipitation_mm": 5.0
        }
        
        advisories = await guidance_service._generate_weather_advisories(adverse_weather, sample_application_method)
        
        assert advisories is not None
        assert len(advisories) > 0
        
        # Check for specific advisories
        advisory_text = " ".join(advisories).lower()
        assert "high wind" in advisory_text or "wind" in advisory_text
        assert "temperature" in advisory_text or "hot" in advisory_text
        assert "precipitation" in advisory_text or "rain" in advisory_text

    @pytest.mark.asyncio
    async def test_generate_weather_advisories_foliar_specific(self, guidance_service):
        """Test weather advisories generation for foliar application."""
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        foliar_method = ApplicationMethod(
            method_id="foliar_test",
            method_type="foliar",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPRAYER,
                capacity=200.0,
                capacity_unit="gallons",
                application_width=25.0,
                application_rate_range={"min": 10.0, "max": 100.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=12.0
            ),
            application_rate=50.0,
            rate_unit="lbs/acre",
            application_timing="flexible",
            efficiency_score=0.8,
            cost_per_acre=15.0,
            labor_requirements="medium",
            environmental_impact="low",
            pros=[],
            cons=[]
        )
        
        hot_dry_weather = {
            "temperature_celsius": 30.0,
            "humidity_percent": 25.0,
            "wind_speed_kmh": 6.0,
            "precipitation_mm": 0.0
        }
        
        advisories = await guidance_service._generate_weather_advisories(hot_dry_weather, foliar_method)
        
        assert advisories is not None
        assert len(advisories) > 0
        
        # Check for foliar-specific advisories
        advisory_text = " ".join(advisories).lower()
        assert "leaf burn" in advisory_text or "burn" in advisory_text

    @pytest.mark.asyncio
    async def test_generate_equipment_preparation(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test equipment preparation steps generation."""
        preparation = await guidance_service._generate_equipment_preparation(sample_application_method, sample_field_conditions)
        
        assert preparation is not None
        assert isinstance(preparation, list)
        assert len(preparation) > 0
        
        # Check for general preparation steps
        preparation_text = " ".join(preparation).lower()
        assert "inspect" in preparation_text
        assert "check" in preparation_text
        assert "test" in preparation_text

    @pytest.mark.asyncio
    async def test_generate_quality_control_measures(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test quality control measures generation."""
        quality_measures = await guidance_service._generate_quality_control_measures(sample_application_method, sample_field_conditions)
        
        assert quality_measures is not None
        assert isinstance(quality_measures, list)
        assert len(quality_measures) > 0
        
        # Check for general quality control measures
        measures_text = " ".join(quality_measures).lower()
        assert "monitor" in measures_text
        assert "check" in measures_text
        assert "verify" in measures_text

    def test_determine_optimal_conditions(self, guidance_service, sample_application_method, sample_field_conditions, sample_weather_conditions):
        """Test optimal conditions determination."""
        optimal_conditions = guidance_service._determine_optimal_conditions(
            sample_application_method, sample_field_conditions, sample_weather_conditions
        )
        
        assert isinstance(optimal_conditions, dict)
        assert "temperature_range" in optimal_conditions
        assert "humidity_range" in optimal_conditions
        assert "wind_speed_max" in optimal_conditions
        assert "soil_moisture" in optimal_conditions
        assert "soil_temperature" in optimal_conditions

    def test_determine_optimal_conditions_foliar(self, guidance_service, sample_field_conditions):
        """Test optimal conditions determination for foliar application."""
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        foliar_method = ApplicationMethod(
            method_id="foliar_test",
            method_type="foliar",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPRAYER,
                capacity=200.0,
                capacity_unit="gallons",
                application_width=25.0,
                application_rate_range={"min": 10.0, "max": 100.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=12.0
            ),
            application_rate=50.0,
            rate_unit="lbs/acre",
            application_timing="flexible",
            efficiency_score=0.8,
            cost_per_acre=15.0,
            labor_requirements="medium",
            environmental_impact="low",
            pros=[],
            cons=[]
        )
        
        optimal_conditions = guidance_service._determine_optimal_conditions(
            foliar_method, sample_field_conditions, None
        )
        
        # Check for foliar-specific optimal conditions
        assert optimal_conditions["temperature_range"] == "18-25°C"
        assert optimal_conditions["humidity_range"] == "50-80%"
        assert optimal_conditions["wind_speed_max"] == "8 km/h"
        assert "application_time" in optimal_conditions

    def test_generate_timing_recommendations(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test timing recommendations generation."""
        timing_rec = guidance_service._generate_timing_recommendations(
            sample_application_method, sample_field_conditions, date(2024, 6, 15)
        )
        
        assert timing_rec is not None
        assert isinstance(timing_rec, str)
        assert len(timing_rec) > 0
        
        # Check for general timing recommendations
        timing_text = timing_rec.lower()
        assert "morning" in timing_text or "evening" in timing_text

    def test_generate_timing_recommendations_foliar(self, guidance_service, sample_field_conditions):
        """Test timing recommendations generation for foliar application."""
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        foliar_method = ApplicationMethod(
            method_id="foliar_test",
            method_type="foliar",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPRAYER,
                capacity=200.0,
                capacity_unit="gallons",
                application_width=25.0,
                application_rate_range={"min": 10.0, "max": 100.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=12.0
            ),
            application_rate=50.0,
            rate_unit="lbs/acre",
            application_timing="flexible",
            efficiency_score=0.8,
            cost_per_acre=15.0,
            labor_requirements="medium",
            environmental_impact="low",
            pros=[],
            cons=[]
        )
        
        timing_rec = guidance_service._generate_timing_recommendations(
            foliar_method, sample_field_conditions, None
        )
        
        # Check for foliar-specific timing recommendations
        timing_text = timing_rec.lower()
        assert "hot" in timing_text or "sunny" in timing_text
        assert "humidity" in timing_text

    @pytest.mark.asyncio
    async def test_provide_application_guidance_without_weather(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test guidance provision without weather conditions."""
        request = GuidanceRequest(
            application_method=sample_application_method,
            field_conditions=sample_field_conditions,
            weather_conditions=None,
            application_date=date(2024, 6, 15)
        )
        
        response = await guidance_service.provide_application_guidance(request)
        
        assert isinstance(response, GuidanceResponse)
        assert response.guidance is not None
        assert response.weather_advisories is None

    @pytest.mark.asyncio
    async def test_provide_application_guidance_without_date(self, guidance_service, sample_application_method, sample_field_conditions, sample_weather_conditions):
        """Test guidance provision without application date."""
        request = GuidanceRequest(
            application_method=sample_application_method,
            field_conditions=sample_field_conditions,
            weather_conditions=sample_weather_conditions,
            application_date=None
        )
        
        response = await guidance_service.provide_application_guidance(request)
        
        assert isinstance(response, GuidanceResponse)
        assert response.guidance is not None

    @pytest.mark.asyncio
    async def test_provide_application_guidance_error_handling(self, guidance_service):
        """Test error handling in guidance provision."""
        # Test with invalid request data - this will fail at Pydantic validation level
        with pytest.raises(Exception):  # Pydantic validation error
            invalid_request = GuidanceRequest(
                application_method=None,  # This should cause an error
                field_conditions=None,
                weather_conditions=None,
                application_date=None
            )

    def test_guidance_database_completeness(self, guidance_service):
        """Test that guidance database contains comprehensive information."""
        for method_type, guidance_data in guidance_service.guidance_database.items():
            # Check that each method has substantial guidance
            total_items = sum(len(items) for items in guidance_data.values())
            assert total_items >= 20, f"Method {method_type} has insufficient guidance items"
            
            # Check for specific important guidance categories
            assert len(guidance_data["safety"]) >= 3, f"Method {method_type} needs more safety guidance"
            assert len(guidance_data["calibration"]) >= 3, f"Method {method_type} needs more calibration guidance"
            assert len(guidance_data["troubleshooting"]) >= 3, f"Method {method_type} needs more troubleshooting guidance"

    def test_guidance_content_quality(self, guidance_service):
        """Test quality of guidance content."""
        for method_type, guidance_data in guidance_service.guidance_database.items():
            for category, items in guidance_data.items():
                for item in items:
                    # Check that guidance items are meaningful
                    assert len(item.strip()) >= 10, f"Guidance item too short: {item}"
                    assert not item.startswith(" "), f"Guidance item has leading whitespace: {item}"
                    assert not item.endswith(" "), f"Guidance item has trailing whitespace: {item}"
                    
                    # Check for proper sentence structure (some items may not have punctuation)
                    # This is acceptable for checklist-style items

    @pytest.mark.asyncio
    async def test_performance_requirements(self, guidance_service, sample_guidance_request):
        """Test that guidance provision meets performance requirements."""
        import time
        
        start_time = time.time()
        response = await guidance_service.provide_application_guidance(sample_guidance_request)
        end_time = time.time()
        
        # Should complete within reasonable time (less than 1 second)
        assert (end_time - start_time) < 1.0, "Guidance provision took too long"
        
        # Response should include processing time
        assert response.processing_time_ms > 0
        assert response.processing_time_ms < 1000  # Less than 1 second in milliseconds


class TestComprehensiveGuidanceFeatures:
    """Test suite for comprehensive guidance features."""
    
    @pytest.fixture
    def guidance_service(self):
        """Create guidance service instance for testing."""
        return GuidanceService()
    
    @pytest.fixture
    def sample_application_method(self):
        """Create sample application method for testing."""
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        return ApplicationMethod(
            method_id="test_method_1",
            method_type="broadcast",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=1000.0,
                capacity_unit="lbs",
                application_width=30.0,
                application_rate_range={"min": 50.0, "max": 300.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=15.0
            ),
            application_rate=150.0,
            rate_unit="lbs/acre",
            application_timing="flexible",
            efficiency_score=0.85,
            cost_per_acre=25.0,
            labor_requirements="medium",
            environmental_impact="low",
            pros=["Uniform coverage", "Fast application", "Equipment availability"],
            cons=["Wind sensitivity", "Potential drift", "Higher fertilizer loss"]
        )
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions for testing."""
        return FieldConditions(
            field_size_acres=50.0,
            soil_type="clay_loam",
            slope_percent=3.0,
            drainage_class="well_drained",
            irrigation_available=True,
            field_shape="rectangular",
            access_roads=["main_road", "field_access"]
        )
    
    def test_equipment_database_initialization(self, guidance_service):
        """Test that equipment database is properly initialized."""
        assert hasattr(guidance_service, 'equipment_database')
        assert isinstance(guidance_service.equipment_database, dict)
        
        # Check that key equipment types are present
        expected_equipment = ["spreader", "sprayer", "injector"]
        for equipment in expected_equipment:
            assert equipment in guidance_service.equipment_database
            assert "specifications" in guidance_service.equipment_database[equipment]
            assert "compatibility" in guidance_service.equipment_database[equipment]
            assert "maintenance_schedule" in guidance_service.equipment_database[equipment]
    
    def test_video_tutorials_initialization(self, guidance_service):
        """Test that video tutorials database is properly initialized."""
        assert hasattr(guidance_service, 'video_tutorials')
        assert isinstance(guidance_service.video_tutorials, dict)
        
        # Check that key methods have tutorials
        expected_methods = ["broadcast", "foliar", "injection"]
        for method in expected_methods:
            assert method in guidance_service.video_tutorials
            assert "calibration" in guidance_service.video_tutorials[method]
            assert "application" in guidance_service.video_tutorials[method]
    
    def test_expert_contacts_initialization(self, guidance_service):
        """Test that expert contacts database is properly initialized."""
        assert hasattr(guidance_service, 'expert_contacts')
        assert isinstance(guidance_service.expert_contacts, dict)
        
        # Check that key expert categories are present
        expected_categories = ["equipment_specialists", "agronomists", "safety_experts"]
        for category in expected_categories:
            assert category in guidance_service.expert_contacts
            assert isinstance(guidance_service.expert_contacts[category], list)
            assert len(guidance_service.expert_contacts[category]) > 0
    
    def test_regulatory_database_initialization(self, guidance_service):
        """Test that regulatory database is properly initialized."""
        assert hasattr(guidance_service, 'regulatory_database')
        assert isinstance(guidance_service.regulatory_database, dict)
        
        # Check that key regulatory areas are present
        assert "federal_regulations" in guidance_service.regulatory_database
        assert "state_regulations" in guidance_service.regulatory_database
        assert "compliance_checklist" in guidance_service.regulatory_database
    
    def test_educational_content_initialization(self, guidance_service):
        """Test that educational content database is properly initialized."""
        assert hasattr(guidance_service, 'educational_content')
        assert isinstance(guidance_service.educational_content, dict)
        
        # Check that key educational areas are present
        expected_areas = ["best_practices", "safety_guidelines", "environmental_stewardship"]
        for area in expected_areas:
            assert area in guidance_service.educational_content
            assert isinstance(guidance_service.educational_content[area], dict)
    
    @pytest.mark.asyncio
    async def test_adaptive_method_guidance_beginner(self, guidance_service, sample_application_method):
        """Test adaptive guidance for beginner experience level."""
        guidance = await guidance_service._get_adaptive_method_guidance(
            sample_application_method, "beginner"
        )
        
        # Beginner guidance should have more detailed explanations
        for category, steps in guidance.items():
            for step in steps:
                assert "(Detailed explanation:" in step or "This step is important" in step
    
    @pytest.mark.asyncio
    async def test_adaptive_method_guidance_expert(self, guidance_service, sample_application_method):
        """Test adaptive guidance for expert experience level."""
        guidance = await guidance_service._get_adaptive_method_guidance(
            sample_application_method, "expert"
        )
        
        # Expert guidance should be concise without extra explanations
        for category, steps in guidance.items():
            for step in steps:
                assert "(Detailed explanation:" not in step
    
    @pytest.mark.asyncio
    async def test_comprehensive_weather_advisories(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test comprehensive weather advisories generation."""
        weather_conditions = {
            "temperature_celsius": 25.0,
            "humidity_percent": 70.0,
            "wind_speed_kmh": 12.0,
            "precipitation_mm": 0.0
        }
        
        advisories = await guidance_service._generate_comprehensive_weather_advisories(
            weather_conditions, sample_application_method, sample_field_conditions
        )
        
        assert advisories is not None
        assert isinstance(advisories, list)
        assert len(advisories) > 0
        
        # Should include real-time weather integration recommendations
        assert any("real-time weather updates" in advisory for advisory in advisories)
        assert any("backup application window" in advisory for advisory in advisories)
    
    @pytest.mark.asyncio
    async def test_equipment_specific_preparation(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test equipment-specific preparation generation."""
        preparation = await guidance_service._generate_equipment_specific_preparation(
            sample_application_method, sample_field_conditions
        )
        
        assert preparation is not None
        assert isinstance(preparation, list)
        assert len(preparation) > 0
        
        # Should include equipment maintenance information
        assert any("Equipment maintenance:" in step for step in preparation)
        assert any("Check compatibility:" in step for step in preparation)
    
    @pytest.mark.asyncio
    async def test_enhanced_quality_control(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test enhanced quality control measures generation."""
        quality_measures = await guidance_service._generate_enhanced_quality_control(
            sample_application_method, sample_field_conditions
        )
        
        assert quality_measures is not None
        assert isinstance(quality_measures, list)
        assert len(quality_measures) > 0
        
        # Should include enhanced monitoring protocols
        assert any("Document application rate every 15 minutes" in measure for measure in quality_measures)
        assert any("Take photos of application quality" in measure for measure in quality_measures)
    
    @pytest.mark.asyncio
    async def test_relevant_video_tutorials(self, guidance_service, sample_application_method):
        """Test relevant video tutorials retrieval."""
        tutorials = await guidance_service._get_relevant_video_tutorials(
            sample_application_method, "intermediate"
        )
        
        assert tutorials is not None
        assert isinstance(tutorials, list)
        
        if tutorials:
            for tutorial in tutorials:
                assert "type" in tutorial
                assert "title" in tutorial
                assert "duration" in tutorial
                assert "difficulty" in tutorial
                assert "topics" in tutorial
                assert "url" in tutorial
    
    @pytest.mark.asyncio
    async def test_expert_consultation_recommendations(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test expert consultation recommendations."""
        experts = await guidance_service._get_expert_consultation_recommendations(
            sample_application_method, sample_field_conditions
        )
        
        assert experts is not None
        assert isinstance(experts, list)
        
        if experts:
            for expert in experts:
                assert "name" in expert
                assert "title" in expert
                assert "expertise" in expert
                assert "contact" in expert
                assert "phone" in expert
                assert "availability" in expert
    
    @pytest.mark.asyncio
    async def test_regulatory_compliance_check(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test regulatory compliance checking."""
        compliance = await guidance_service._check_regulatory_compliance(
            sample_application_method, sample_field_conditions
        )
        
        assert compliance is not None
        assert isinstance(compliance, dict)
        
        # Should include compliance status
        assert "federal_compliance" in compliance
        assert "state_compliance" in compliance
        assert "environmental_compliance" in compliance
        assert "required_actions" in compliance
        assert "recommendations" in compliance
    
    @pytest.mark.asyncio
    async def test_educational_content_retrieval(self, guidance_service, sample_application_method):
        """Test educational content retrieval."""
        content = await guidance_service._get_educational_content(
            sample_application_method, "intermediate"
        )
        
        assert content is not None
        assert isinstance(content, dict)
        
        # Should include key educational areas
        assert "best_practices" in content
        assert "safety_guidelines" in content
        assert "environmental_stewardship" in content
        assert "method_specific_content" in content
    
    def test_interactive_guides_retrieval(self, guidance_service, sample_application_method):
        """Test interactive guides retrieval."""
        guides = guidance_service._get_interactive_guides(sample_application_method)
        
        assert guides is not None
        assert isinstance(guides, list)
        
        if guides:
            for guide in guides:
                assert "title" in guide
                assert "type" in guide
                assert "description" in guide
                assert "url" in guide
    
    def test_equipment_maintenance_schedule(self, guidance_service, sample_application_method):
        """Test equipment maintenance schedule retrieval."""
        maintenance = guidance_service._get_equipment_maintenance_schedule(sample_application_method)
        
        if maintenance:
            assert isinstance(maintenance, dict)
            assert "daily" in maintenance
            assert "weekly" in maintenance
            assert "monthly" in maintenance
    
    @pytest.mark.asyncio
    async def test_comprehensive_guidance_response(self, guidance_service, sample_application_method, sample_field_conditions):
        """Test comprehensive guidance response with all new features."""
        request = GuidanceRequest(
            application_method=sample_application_method,
            field_conditions=sample_field_conditions,
            weather_conditions={
                "temperature_celsius": 22.0,
                "humidity_percent": 65.0,
                "wind_speed_kmh": 8.0,
                "precipitation_mm": 0.0
            },
            application_date=date(2024, 6, 15),
            experience_level="intermediate"
        )
        
        response = await guidance_service.provide_application_guidance(request)
        
        # Test that response includes all comprehensive features
        assert response.video_tutorials is not None
        assert response.expert_recommendations is not None
        assert response.compliance_check is not None
        assert response.educational_content is not None
        assert response.interactive_guides is not None
        assert response.maintenance_schedule is not None
        
        # Test that enhanced features are properly populated
        if response.video_tutorials:
            assert len(response.video_tutorials) > 0
        
        if response.expert_recommendations:
            assert len(response.expert_recommendations) > 0
        
        assert response.compliance_check is not None
        assert response.educational_content is not None
        
        if response.interactive_guides:
            assert len(response.interactive_guides) > 0
        
        if response.maintenance_schedule:
            assert isinstance(response.maintenance_schedule, dict)


class TestGuidanceServiceIntegration:
    """Integration tests for guidance service with external dependencies."""

    @pytest.fixture
    def guidance_service(self):
        """Create guidance service instance for integration testing."""
        return GuidanceService()

    @pytest.mark.asyncio
    async def test_guidance_service_with_real_data(self, guidance_service):
        """Test guidance service with realistic agricultural data."""
        # Create realistic application method
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        broadcast_method = ApplicationMethod(
            method_id="broadcast_real",
            method_type="broadcast",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=2000.0,
                capacity_unit="lbs",
                application_width=40.0,
                application_rate_range={"min": 100.0, "max": 400.0},
                fuel_efficiency=0.85,
                maintenance_cost_per_hour=20.0
            ),
            application_rate=200.0,
            rate_unit="lbs/acre",
            application_timing="pre_plant",
            efficiency_score=0.85,
            cost_per_acre=30.0,
            labor_requirements="medium",
            environmental_impact="medium",
            pros=["Uniform coverage", "Fast application", "Equipment availability"],
            cons=["Wind sensitivity", "Potential drift", "Higher fertilizer loss"]
        )
        
        # Create realistic field conditions
        field_conditions = FieldConditions(
            field_size_acres=120.0,
            soil_type="silt_loam",
            slope_percent=2.0,
            drainage_class="well_drained",
            irrigation_available=False,
            field_shape="rectangular",
            access_roads=["main_road", "field_access", "secondary_road"]
        )
        
        # Create realistic weather conditions
        weather_conditions = {
            "temperature_celsius": 18.0,
            "humidity_percent": 70.0,
            "wind_speed_kmh": 6.0,
            "precipitation_mm": 0.0,
            "conditions": "partly_cloudy"
        }
        
        # Create guidance request
        request = GuidanceRequest(
            application_method=broadcast_method,
            field_conditions=field_conditions,
            weather_conditions=weather_conditions,
            application_date=date(2024, 4, 15),
            experience_level="experienced"
        )
        
        # Get guidance
        response = await guidance_service.provide_application_guidance(request)
        
        # Validate comprehensive response
        assert response.guidance is not None
        assert len(response.guidance.pre_application_checklist) > 0
        assert len(response.guidance.application_instructions) > 0
        assert len(response.guidance.safety_precautions) > 0
        assert len(response.guidance.calibration_instructions) > 0
        assert len(response.guidance.troubleshooting_tips) > 0
        assert len(response.guidance.post_application_tasks) > 0
        
        # Validate weather advisories
        assert response.weather_advisories is None or len(response.weather_advisories) >= 0
        
        # Validate equipment preparation
        assert response.equipment_preparation is not None
        assert len(response.equipment_preparation) > 0
        
        # Validate quality control measures
        assert response.quality_control_measures is not None
        assert len(response.quality_control_measures) > 0

    @pytest.mark.asyncio
    async def test_guidance_service_edge_cases(self, guidance_service):
        """Test guidance service with edge case scenarios."""
        # Test with minimal field conditions
        minimal_field = FieldConditions(
            field_size_acres=1.0,
            soil_type="unknown",
            slope_percent=0.0,
            drainage_class="unknown",
            irrigation_available=False,
            field_shape="irregular",
            access_roads=[]
        )
        
        from src.models.application_models import EquipmentSpecification, EquipmentType
        
        minimal_method = ApplicationMethod(
            method_id="minimal_method",
            method_type="broadcast",
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=100.0,
                capacity_unit="lbs",
                application_width=10.0,
                application_rate_range={"min": 10.0, "max": 50.0},
                fuel_efficiency=0.5,
                maintenance_cost_per_hour=5.0
            ),
            application_rate=0.0,
            rate_unit="lbs/acre",
            application_timing="unknown",
            efficiency_score=0.0,
            cost_per_acre=0.0,
            labor_requirements="unknown",
            environmental_impact="unknown",
            pros=[],
            cons=[]
        )
        
        request = GuidanceRequest(
            application_method=minimal_method,
            field_conditions=minimal_field,
            weather_conditions=None,
            application_date=None
        )
        
        response = await guidance_service.provide_application_guidance(request)
        
        # Should still provide guidance even with minimal data
        assert response.guidance is not None
        assert len(response.guidance.pre_application_checklist) > 0
        assert len(response.guidance.application_instructions) > 0
        assert len(response.guidance.safety_precautions) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])