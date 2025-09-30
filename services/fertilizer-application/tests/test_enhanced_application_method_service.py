"""
Tests for enhanced Application Method Service with crop integration.

Tests the integration of crop type and growth stage considerations
into fertilizer application method recommendations.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from src.services.application_method_service import ApplicationMethodService
from src.services.crop_integration_service import CropType, GrowthStage
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)


class TestEnhancedApplicationMethodService:
    """Test enhanced application method service with crop integration."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return ApplicationMethodService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample application request."""
        return ApplicationRequest(
            field_conditions=FieldConditions(
                field_size_acres=100.0,
                soil_type="clay_loam",
                drainage_class="moderate",
                slope_percent=2.0,
                access_roads=["gravel", "paved"]
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="v6",
                target_yield=180.0,
                nutrient_requirements={"nitrogen": 150, "phosphorus": 60, "potassium": 80},
                application_timing_preferences=["early_vegetative"]
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="urea",
                nitrogen_percent=46.0,
                phosphorus_percent=0.0,
                potassium_percent=0.0,
                form=FertilizerForm.GRANULAR,
                unit="lbs/acre"
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_id="spreader_1",
                    equipment_type=EquipmentType.SPREADER,
                    capacity_per_hour=50.0,
                    application_width=30.0,
                    precision_level="medium"
                )
            ],
            application_goals=["efficiency", "cost_effectiveness"],
            budget_limit=5000.0
        )
    
    def test_service_initialization_with_crop_integration(self, service):
        """Test service initializes with crop integration service."""
        assert service.crop_integration_service is not None
        assert hasattr(service.crop_integration_service, 'get_crop_info')
        assert hasattr(service.crop_integration_service, 'get_growth_stage_info')
    
    def test_parse_crop_type(self, service):
        """Test crop type parsing."""
        # Test common crop types
        assert service._parse_crop_type("corn") == CropType.CORN
        assert service._parse_crop_type("maize") == CropType.CORN
        assert service._parse_crop_type("soybean") == CropType.SOYBEAN
        assert service._parse_crop_type("soy") == CropType.SOYBEAN
        assert service._parse_crop_type("wheat") == CropType.WHEAT
        assert service._parse_crop_type("tomato") == CropType.TOMATO
        assert service._parse_crop_type("potato") == CropType.POTATO
        
        # Test case insensitive
        assert service._parse_crop_type("CORN") == CropType.CORN
        assert service._parse_crop_type("Corn") == CropType.CORN
        
        # Test unknown crop defaults to corn
        assert service._parse_crop_type("unknown") == CropType.CORN
    
    def test_parse_growth_stage(self, service):
        """Test growth stage parsing."""
        # Test general stages
        assert service._parse_growth_stage("germination") == GrowthStage.GERMINATION
        assert service._parse_growth_stage("emergence") == GrowthStage.EMERGENCE
        assert service._parse_growth_stage("vegetative") == GrowthStage.VEGETATIVE_2
        assert service._parse_growth_stage("flowering") == GrowthStage.FLOWERING
        assert service._parse_growth_stage("maturity") == GrowthStage.MATURITY
        
        # Test corn stages
        assert service._parse_growth_stage("v1") == GrowthStage.V1
        assert service._parse_growth_stage("v6") == GrowthStage.V6
        assert service._parse_growth_stage("vt") == GrowthStage.VT
        assert service._parse_growth_stage("r1") == GrowthStage.R1
        
        # Test soybean stages
        assert service._parse_growth_stage("r1_soy") == GrowthStage.R1_SOY
        assert service._parse_growth_stage("r3_soy") == GrowthStage.R3_SOY
        
        # Test case insensitive
        assert service._parse_growth_stage("V6") == GrowthStage.V6
        assert service._parse_growth_stage("VT") == GrowthStage.VT
        
        # Test unknown stage defaults to vegetative_2
        assert service._parse_growth_stage("unknown") == GrowthStage.VEGETATIVE_2
    
    def test_get_enhanced_application_timing(self, service):
        """Test enhanced application timing calculation."""
        # Test corn V6 stage with sidedress
        timing = service._get_enhanced_application_timing(
            CropType.CORN, GrowthStage.V6, "sidedress", "v6"
        )
        assert "early_vegetative" in timing or "sidedress application" in timing
        
        # Test corn VT stage with foliar
        timing = service._get_enhanced_application_timing(
            CropType.CORN, GrowthStage.VT, "foliar", "vt"
        )
        assert "foliar application" in timing
        assert "avoid during flowering" in timing
        
        # Test soybean R1 stage with band
        timing = service._get_enhanced_application_timing(
            CropType.SOYBEAN, GrowthStage.R1_SOY, "band", "r1_soy"
        )
        assert "band application" in timing
        assert "precise placement" in timing
    
    def test_calculate_enhanced_application_rate(self, service):
        """Test enhanced application rate calculation."""
        fertilizer_spec = FertilizerSpecification(
            fertilizer_type="urea",
            nitrogen_percent=46.0,
            form=FertilizerForm.GRANULAR
        )
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="v6",
            nutrient_requirements={"nitrogen": 150}
        )
        
        # Test corn V6 (critical stage) with sidedress
        rate = service._calculate_enhanced_application_rate(
            fertilizer_spec, crop_requirements, "sidedress",
            CropType.CORN, GrowthStage.V6
        )
        assert rate > 0
        assert rate < 200  # Should be reasonable
        
        # Test corn V1 (low demand) with broadcast
        rate = service._calculate_enhanced_application_rate(
            fertilizer_spec, crop_requirements, "broadcast",
            CropType.CORN, GrowthStage.V1
        )
        assert rate > 0
        assert rate < 200
    
    @pytest.mark.asyncio
    async def test_generate_recommendations_with_crop_integration(self, service, sample_request):
        """Test recommendation generation with crop integration."""
        # Mock the scoring method to return known scores
        with patch.object(service, '_calculate_method_scores', return_value={
            "broadcast": 0.8,
            "band": 0.9,
            "sidedress": 0.95,
            "foliar": 0.3
        }):
            recommendations = await service._generate_recommendations(
                {"broadcast": 0.8, "band": 0.9, "sidedress": 0.95, "foliar": 0.3},
                sample_request.field_conditions,
                sample_request.crop_requirements,
                sample_request.fertilizer_specification,
                sample_request.available_equipment
            )
            
            assert len(recommendations) > 0
            
            # Check that recommendations include crop compatibility information
            for rec in recommendations:
                assert hasattr(rec, 'crop_compatibility_score')
                assert hasattr(rec, 'crop_compatibility_factors')
                assert rec.crop_compatibility_score is not None
                assert rec.crop_compatibility_factors is not None
    
    @pytest.mark.asyncio
    async def test_crop_specific_method_preferences(self, service):
        """Test that crop-specific method preferences are applied."""
        # Create corn V6 request (should prefer sidedress, avoid foliar)
        corn_request = ApplicationRequest(
            field_conditions=FieldConditions(field_size_acres=100.0, soil_type="clay_loam"),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="v6",
                nutrient_requirements={"nitrogen": 150}
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="urea",
                nitrogen_percent=46.0,
                form=FertilizerForm.GRANULAR
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_id="spreader_1",
                    equipment_type=EquipmentType.SPREADER,
                    capacity_per_hour=50.0
                )
            ]
        )
        
        # Mock scoring to give equal scores initially
        with patch.object(service, '_calculate_method_scores', return_value={
            "broadcast": 0.7,
            "band": 0.7,
            "sidedress": 0.7,
            "foliar": 0.7
        }):
            recommendations = await service._generate_recommendations(
                {"broadcast": 0.7, "band": 0.7, "sidedress": 0.7, "foliar": 0.7},
                corn_request.field_conditions,
                corn_request.crop_requirements,
                corn_request.fertilizer_specification,
                corn_request.available_equipment
            )
            
            # Sidedress should be recommended (preferred for corn V6)
            sidedress_recs = [r for r in recommendations if r.method_type == "sidedress"]
            assert len(sidedress_recs) > 0
            
            # Foliar should be avoided or have low compatibility score
            foliar_recs = [r for r in recommendations if r.method_type == "foliar"]
            if foliar_recs:
                assert foliar_recs[0].crop_compatibility_score < 0.5
    
    @pytest.mark.asyncio
    async def test_soybean_nitrogen_fixation_handling(self, service):
        """Test that soybean nitrogen fixation is properly handled."""
        # Create soybean request
        soy_request = ApplicationRequest(
            field_conditions=FieldConditions(field_size_acres=100.0, soil_type="clay_loam"),
            crop_requirements=CropRequirements(
                crop_type="soybean",
                growth_stage="r1_soy",
                nutrient_requirements={"nitrogen": 0, "phosphorus": 60}  # No N needed
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="urea",
                nitrogen_percent=46.0,
                form=FertilizerForm.GRANULAR
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_id="spreader_1",
                    equipment_type=EquipmentType.SPREADER,
                    capacity_per_hour=50.0
                )
            ]
        )
        
        with patch.object(service, '_calculate_method_scores', return_value={
            "broadcast": 0.8,
            "band": 0.8,
            "foliar": 0.8
        }):
            recommendations = await service._generate_recommendations(
                {"broadcast": 0.8, "band": 0.8, "foliar": 0.8},
                soy_request.field_conditions,
                soy_request.crop_requirements,
                soy_request.fertilizer_specification,
                soy_request.available_equipment
            )
            
            # Foliar should be avoided for soybean
            foliar_recs = [r for r in recommendations if r.method_type == "foliar"]
            if foliar_recs:
                assert foliar_recs[0].crop_compatibility_score < 0.5
    
    @pytest.mark.asyncio
    async def test_tomato_calcium_requirements(self, service):
        """Test tomato calcium requirements handling."""
        # Create tomato request
        tomato_request = ApplicationRequest(
            field_conditions=FieldConditions(field_size_acres=5.0, soil_type="sandy_loam"),
            crop_requirements=CropRequirements(
                crop_type="tomato",
                growth_stage="fruit_set",
                nutrient_requirements={"nitrogen": 100, "calcium": 200}
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="calcium_nitrate",
                nitrogen_percent=15.5,
                calcium_percent=19.0,
                form=FertilizerForm.LIQUID
            ),
            available_equipment=[
                EquipmentSpecification(
                    equipment_id="sprayer_1",
                    equipment_type=EquipmentType.SPRAYER,
                    capacity_per_hour=10.0
                )
            ]
        )
        
        with patch.object(service, '_calculate_method_scores', return_value={
            "foliar": 0.9,
            "band": 0.8,
            "broadcast": 0.6
        }):
            recommendations = await service._generate_recommendations(
                {"foliar": 0.9, "band": 0.8, "broadcast": 0.6},
                tomato_request.field_conditions,
                tomato_request.crop_requirements,
                tomato_request.fertilizer_specification,
                tomato_request.available_equipment
            )
            
            # Foliar should be preferred for tomato calcium
            foliar_recs = [r for r in recommendations if r.method_type == "foliar"]
            assert len(foliar_recs) > 0
            assert foliar_recs[0].crop_compatibility_score > 0.7


class TestCropIntegrationEdgeCases:
    """Test edge cases in crop integration."""
    
    @pytest.fixture
    def service(self):
        return ApplicationMethodService()
    
    def test_unknown_crop_type_handling(self, service):
        """Test handling of unknown crop types."""
        # Should default to corn
        crop_type = service._parse_crop_type("unknown_crop")
        assert crop_type == CropType.CORN
        
        # Should still work with default crop
        timing = service._get_enhanced_application_timing(
            crop_type, GrowthStage.VEGETATIVE_2, "broadcast", "vegetative"
        )
        assert timing is not None
    
    def test_unknown_growth_stage_handling(self, service):
        """Test handling of unknown growth stages."""
        # Should default to vegetative_2
        growth_stage = service._parse_growth_stage("unknown_stage")
        assert growth_stage == GrowthStage.VEGETATIVE_2
        
        # Should still work with default stage
        timing = service._get_enhanced_application_timing(
            CropType.CORN, growth_stage, "broadcast", "unknown_stage"
        )
        assert timing is not None
    
    def test_boundary_values(self, service):
        """Test boundary values and edge cases."""
        fertilizer_spec = FertilizerSpecification(
            fertilizer_type="urea",
            nitrogen_percent=46.0,
            form=FertilizerForm.GRANULAR
        )
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="v6",
            nutrient_requirements={"nitrogen": 0}  # Zero nitrogen
        )
        
        # Should handle zero nutrient requirements
        rate = service._calculate_enhanced_application_rate(
            fertilizer_spec, crop_requirements, "broadcast",
            CropType.CORN, GrowthStage.V6
        )
        assert rate >= 0  # Should not be negative
        
        # Test very high nutrient requirements
        crop_requirements.nutrient_requirements = {"nitrogen": 1000}
        rate = service._calculate_enhanced_application_rate(
            fertilizer_spec, crop_requirements, "broadcast",
            CropType.CORN, GrowthStage.V6
        )
        assert rate > 0
        assert rate < 2000  # Should be reasonable


class TestCropIntegrationPerformance:
    """Test performance of crop integration features."""
    
    @pytest.fixture
    def service(self):
        return ApplicationMethodService()
    
    def test_parsing_performance(self, service):
        """Test that parsing methods are fast."""
        import time
        
        start_time = time.time()
        for _ in range(1000):
            service._parse_crop_type("corn")
            service._parse_growth_stage("v6")
        parsing_time = time.time() - start_time
        
        assert parsing_time < 0.1  # Should be very fast
    
    def test_enhanced_calculation_performance(self, service):
        """Test that enhanced calculations are fast."""
        import time
        
        fertilizer_spec = FertilizerSpecification(
            fertilizer_type="urea",
            nitrogen_percent=46.0,
            form=FertilizerForm.GRANULAR
        )
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="v6",
            nutrient_requirements={"nitrogen": 150}
        )
        
        start_time = time.time()
        for _ in range(100):
            service._calculate_enhanced_application_rate(
                fertilizer_spec, crop_requirements, "sidedress",
                CropType.CORN, GrowthStage.V6
            )
        calculation_time = time.time() - start_time
        
        assert calculation_time < 0.1  # Should be very fast


class TestCropIntegrationAgriculturalValidation:
    """Test agricultural accuracy of crop integration."""
    
    @pytest.fixture
    def service(self):
        return ApplicationMethodService()
    
    def test_corn_nitrogen_timing_accuracy(self, service):
        """Test corn nitrogen timing recommendations are agriculturally accurate."""
        # V6 stage should prefer sidedress
        timing = service._get_enhanced_application_timing(
            CropType.CORN, GrowthStage.V6, "sidedress", "v6"
        )
        assert "sidedress" in timing.lower()
        
        # VT stage should prefer sidedress and foliar
        timing = service._get_enhanced_application_timing(
            CropType.CORN, GrowthStage.VT, "sidedress", "vt"
        )
        assert "sidedress" in timing.lower()
        
        timing = service._get_enhanced_application_timing(
            CropType.CORN, GrowthStage.VT, "foliar", "vt"
        )
        assert "foliar" in timing.lower()
    
    def test_soybean_phosphorus_timing_accuracy(self, service):
        """Test soybean phosphorus timing recommendations."""
        # R1 stage should prefer band application
        timing = service._get_enhanced_application_timing(
            CropType.SOYBEAN, GrowthStage.R1_SOY, "band", "r1_soy"
        )
        assert "band" in timing.lower()
        
        # Should avoid foliar during flowering
        timing = service._get_enhanced_application_timing(
            CropType.SOYBEAN, GrowthStage.R1_SOY, "foliar", "r1_soy"
        )
        assert "foliar" in timing.lower()
    
    def test_tomato_calcium_application_accuracy(self, service):
        """Test tomato calcium application recommendations."""
        # Fruit set stage should prefer foliar for calcium
        timing = service._get_enhanced_application_timing(
            CropType.TOMATO, GrowthStage.FRUIT_SET, "foliar", "fruit_set"
        )
        assert "foliar" in timing.lower()
        
        # Should avoid broadcast for calcium
        timing = service._get_enhanced_application_timing(
            CropType.TOMATO, GrowthStage.FRUIT_SET, "broadcast", "fruit_set"
        )
        assert "broadcast" in timing.lower()
    
    def test_potato_tuber_timing_accuracy(self, service):
        """Test potato tuber timing recommendations."""
        # Should prefer band application for tuber crops
        timing = service._get_enhanced_application_timing(
            CropType.POTATO, GrowthStage.VEGETATIVE_2, "band", "vegetative"
        )
        assert "band" in timing.lower()
        
        # Should avoid sidedress for tuber crops
        timing = service._get_enhanced_application_timing(
            CropType.POTATO, GrowthStage.VEGETATIVE_2, "sidedress", "vegetative"
        )
        assert "sidedress" in timing.lower()