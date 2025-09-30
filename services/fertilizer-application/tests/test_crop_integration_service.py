"""
Comprehensive tests for the Crop Integration Service.

Tests the advanced crop type and growth stage integration functionality
for fertilizer application method selection and optimization.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from src.services.crop_integration_service import (
    CropIntegrationService, CropType, GrowthStage,
    CropGrowthStageInfo, CropApplicationPreferences
)


class TestCropIntegrationService:
    """Test suite for CropIntegrationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return CropIntegrationService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly with crop database."""
        assert service.crop_database is not None
        assert len(service.crop_database) > 0
        assert CropType.CORN in service.crop_database
        assert CropType.SOYBEAN in service.crop_database
        assert CropType.WHEAT in service.crop_database
    
    def test_get_crop_info(self, service):
        """Test getting crop information."""
        corn_info = service.get_crop_info(CropType.CORN)
        assert corn_info is not None
        assert corn_info["name"] == "Corn (Maize)"
        assert corn_info["scientific_name"] == "Zea mays"
        assert corn_info["category"] == "grain"
        assert "nutrient_requirements" in corn_info
        assert "application_sensitivity" in corn_info
    
    def test_get_growth_stage_info(self, service):
        """Test getting growth stage information."""
        # Test corn V6 stage
        v6_info = service.get_growth_stage_info(CropType.CORN, GrowthStage.V6)
        assert v6_info is not None
        assert v6_info.stage_name == "Sixth Leaf"
        assert v6_info.stage_code == "V6"
        assert v6_info.nutrient_demand_level == "critical"
        assert "sidedress" in v6_info.recommended_methods
        
        # Test soybean R1 stage
        r1_soy_info = service.get_growth_stage_info(CropType.SOYBEAN, GrowthStage.R1_SOY)
        assert r1_soy_info is not None
        assert r1_soy_info.stage_name == "Beginning Bloom"
        assert r1_soy_info.nutrient_demand_level == "critical"
    
    def test_get_application_preferences(self, service):
        """Test getting crop application preferences."""
        corn_prefs = service.get_application_preferences(CropType.CORN)
        assert corn_prefs is not None
        assert corn_prefs.crop_type == CropType.CORN
        assert "band" in corn_prefs.preferred_methods
        assert "foliar" in corn_prefs.avoided_methods
        assert "nitrogen" in corn_prefs.nutrient_uptake_pattern
        
        soybean_prefs = service.get_application_preferences(CropType.SOYBEAN)
        assert soybean_prefs is not None
        assert soybean_prefs.crop_type == CropType.SOYBEAN
        assert "foliar" in soybean_prefs.avoided_methods
    
    def test_get_recommended_methods_for_stage(self, service):
        """Test getting recommended methods for specific crop and growth stage."""
        # Corn V6 stage should recommend sidedress
        corn_v6_methods = service.get_recommended_methods_for_stage(CropType.CORN, GrowthStage.V6)
        assert "sidedress" in corn_v6_methods
        assert "band" in corn_v6_methods
        
        # Corn VT stage should recommend sidedress and foliar
        corn_vt_methods = service.get_recommended_methods_for_stage(CropType.CORN, GrowthStage.VT)
        assert "sidedress" in corn_vt_methods
        assert "foliar" in corn_vt_methods
        
        # Soybean R1 stage should recommend band and foliar
        soy_r1_methods = service.get_recommended_methods_for_stage(CropType.SOYBEAN, GrowthStage.R1_SOY)
        assert "band" in soy_r1_methods
        assert "foliar" in soy_r1_methods
    
    def test_get_avoided_methods_for_stage(self, service):
        """Test getting avoided methods for specific crop and growth stage."""
        # Corn V6 stage should avoid foliar
        corn_v6_avoided = service.get_avoided_methods_for_stage(CropType.CORN, GrowthStage.V6)
        assert "foliar" in corn_v6_avoided
        
        # Corn R1 stage should avoid broadcast and sidedress
        corn_r1_avoided = service.get_avoided_methods_for_stage(CropType.CORN, GrowthStage.R1)
        assert "broadcast" in corn_r1_avoided
        assert "sidedress" in corn_r1_avoided
    
    def test_calculate_application_timing_score(self, service):
        """Test calculating application timing scores."""
        # Test optimal timing for corn V6 with sidedress
        score = service.calculate_application_timing_score(
            CropType.CORN, GrowthStage.V6, "sidedress", 40
        )
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be high for optimal timing
        
        # Test suboptimal timing for corn V6 with foliar
        score = service.calculate_application_timing_score(
            CropType.CORN, GrowthStage.V6, "foliar", 40
        )
        assert 0.0 <= score <= 1.0
        assert score < 0.8  # Should be lower for avoided method
        
        # Test timing outside optimal window
        score = service.calculate_application_timing_score(
            CropType.CORN, GrowthStage.V6, "sidedress", 100
        )
        assert score <= 0.91  # Should be lower for timing outside window (with floating point tolerance)
    
    def test_get_nutrient_uptake_curve(self, service):
        """Test getting nutrient uptake curves."""
        # Test nitrogen uptake for corn
        nitrogen_curve = service.get_nutrient_uptake_curve(CropType.CORN, "nitrogen")
        assert len(nitrogen_curve) == 10
        assert all(0.0 <= val <= 1.0 for val in nitrogen_curve)
        assert nitrogen_curve[-1] == 1.0  # Should reach 100% at end
        
        # Test phosphorus uptake for soybean
        phosphorus_curve = service.get_nutrient_uptake_curve(CropType.SOYBEAN, "phosphorus")
        assert len(phosphorus_curve) == 10
        assert all(0.0 <= val <= 1.0 for val in phosphorus_curve)
        
        # Test unknown nutrient returns default
        unknown_curve = service.get_nutrient_uptake_curve(CropType.CORN, "unknown")
        assert len(unknown_curve) == 10
        assert all(val == 0.1 for val in unknown_curve)
    
    def test_assess_crop_method_compatibility(self, service):
        """Test assessing crop-method compatibility."""
        # Test corn with band application (preferred)
        compatibility = service.assess_crop_method_compatibility(CropType.CORN, "band")
        assert compatibility["compatibility_score"] > 0.7
        assert "Method is preferred for this crop" in compatibility["factors"]
        
        # Test corn with foliar application (avoided)
        compatibility = service.assess_crop_method_compatibility(CropType.CORN, "foliar")
        assert compatibility["compatibility_score"] < 0.5
        assert "Method is avoided for this crop" in compatibility["factors"]
        
        # Test soybean with broadcast application (neutral)
        compatibility = service.assess_crop_method_compatibility(CropType.SOYBEAN, "broadcast")
        assert 0.4 <= compatibility["compatibility_score"] <= 1.0
    
    def test_get_critical_application_windows(self, service):
        """Test getting critical application windows."""
        windows = service.get_critical_application_windows(CropType.CORN)
        assert "pre_plant" in windows
        assert "at_planting" in windows
        assert "early_vegetative" in windows
        assert "reproductive" in windows
        
        # Check window ranges are reasonable
        pre_plant_window = windows["pre_plant"]
        assert pre_plant_window[0] >= 0
        assert pre_plant_window[1] <= 30
    
    def test_get_supported_crops(self, service):
        """Test getting list of supported crops."""
        crops = service.get_supported_crops()
        assert len(crops) >= 5  # Should have at least 5 crops
        assert CropType.CORN in crops
        assert CropType.SOYBEAN in crops
        assert CropType.WHEAT in crops
        assert CropType.TOMATO in crops
        assert CropType.POTATO in crops
    
    def test_get_supported_growth_stages(self, service):
        """Test getting supported growth stages for crops."""
        # Test corn stages
        corn_stages = service.get_supported_growth_stages(CropType.CORN)
        assert GrowthStage.V1 in corn_stages
        assert GrowthStage.V6 in corn_stages
        assert GrowthStage.VT in corn_stages
        assert GrowthStage.R1 in corn_stages
        
        # Test soybean stages
        soy_stages = service.get_supported_growth_stages(CropType.SOYBEAN)
        assert GrowthStage.V1_SOY in soy_stages
        assert GrowthStage.R1_SOY in soy_stages
        assert GrowthStage.R3_SOY in soy_stages


class TestCropGrowthStageInfo:
    """Test CropGrowthStageInfo dataclass."""
    
    def test_crop_growth_stage_info_creation(self):
        """Test creating CropGrowthStageInfo instance."""
        stage_info = CropGrowthStageInfo(
            stage_name="Test Stage",
            stage_code="TS",
            description="Test description",
            days_from_planting=(10, 20),
            nutrient_demand_level="high",
            application_sensitivity="medium",
            recommended_methods=["band", "sidedress"],
            avoided_methods=["foliar"],
            timing_preferences=["early_vegetative"]
        )
        
        assert stage_info.stage_name == "Test Stage"
        assert stage_info.stage_code == "TS"
        assert stage_info.nutrient_demand_level == "high"
        assert stage_info.application_sensitivity == "medium"
        assert "band" in stage_info.recommended_methods
        assert "foliar" in stage_info.avoided_methods


class TestCropApplicationPreferences:
    """Test CropApplicationPreferences dataclass."""
    
    def test_crop_application_preferences_creation(self):
        """Test creating CropApplicationPreferences instance."""
        prefs = CropApplicationPreferences(
            crop_type=CropType.CORN,
            preferred_methods=["band", "sidedress"],
            avoided_methods=["foliar"],
            sensitivity_factors={"root_damage": 0.8, "foliar_burn": 0.9},
            nutrient_uptake_pattern={"nitrogen": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]},
            application_timing_critical_stages=["V6", "VT"]
        )
        
        assert prefs.crop_type == CropType.CORN
        assert "band" in prefs.preferred_methods
        assert "foliar" in prefs.avoided_methods
        assert prefs.sensitivity_factors["root_damage"] == 0.8
        assert len(prefs.nutrient_uptake_pattern["nitrogen"]) == 10


class TestCropTypeEnum:
    """Test CropType enum values."""
    
    def test_crop_type_values(self):
        """Test CropType enum has expected values."""
        assert CropType.CORN == "corn"
        assert CropType.SOYBEAN == "soybean"
        assert CropType.WHEAT == "wheat"
        assert CropType.TOMATO == "tomato"
        assert CropType.POTATO == "potato"
        assert CropType.RICE == "rice"
        assert CropType.BARLEY == "barley"
        assert CropType.OATS == "oats"
        assert CropType.SORGHUM == "sorghum"
        assert CropType.MILLET == "millet"


class TestGrowthStageEnum:
    """Test GrowthStage enum values."""
    
    def test_growth_stage_values(self):
        """Test GrowthStage enum has expected values."""
        assert GrowthStage.GERMINATION == "germination"
        assert GrowthStage.EMERGENCE == "emergence"
        assert GrowthStage.VEGETATIVE_1 == "vegetative_1"
        assert GrowthStage.VEGETATIVE_2 == "vegetative_2"
        assert GrowthStage.VEGETATIVE_3 == "vegetative_3"
        assert GrowthStage.FLOWERING == "flowering"
        assert GrowthStage.MATURITY == "maturity"
        assert GrowthStage.V1 == "v1"
        assert GrowthStage.V6 == "v6"
        assert GrowthStage.VT == "vt"
        assert GrowthStage.R1 == "r1"


class TestCropIntegrationEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def service(self):
        return CropIntegrationService()
    
    def test_unknown_crop_type(self, service):
        """Test handling of unknown crop types."""
        # Should return empty dict for unknown crop
        unknown_crop_info = service.get_crop_info("unknown_crop")
        assert unknown_crop_info == {}
        
        # Should return None for unknown crop preferences
        unknown_prefs = service.get_application_preferences("unknown_crop")
        assert unknown_prefs is None
    
    def test_unknown_growth_stage(self, service):
        """Test handling of unknown growth stages."""
        # Should return None for unknown growth stage
        unknown_stage_info = service.get_growth_stage_info(CropType.CORN, "unknown_stage")
        assert unknown_stage_info is None
        
        # Should return empty list for unknown stage methods
        methods = service.get_recommended_methods_for_stage(CropType.CORN, "unknown_stage")
        assert methods == []
    
    def test_boundary_values(self, service):
        """Test boundary values and edge cases."""
        # Test very early timing
        score = service.calculate_application_timing_score(
            CropType.CORN, GrowthStage.V6, "sidedress", 0
        )
        assert 0.0 <= score <= 1.0
        
        # Test very late timing
        score = service.calculate_application_timing_score(
            CropType.CORN, GrowthStage.V6, "sidedress", 200
        )
        assert 0.0 <= score <= 1.0
        
        # Test compatibility with unknown method
        compatibility = service.assess_crop_method_compatibility(CropType.CORN, "unknown_method")
        assert compatibility["compatibility_score"] == 0.5  # Default neutral score


class TestCropIntegrationPerformance:
    """Test performance characteristics."""
    
    @pytest.fixture
    def service(self):
        return CropIntegrationService()
    
    def test_service_initialization_performance(self, service):
        """Test that service initializes quickly."""
        import time
        start_time = time.time()
        new_service = CropIntegrationService()
        init_time = time.time() - start_time
        assert init_time < 1.0  # Should initialize in less than 1 second
    
    def test_lookup_performance(self, service):
        """Test that lookups are fast."""
        import time
        
        # Test multiple lookups
        start_time = time.time()
        for _ in range(100):
            service.get_crop_info(CropType.CORN)
            service.get_growth_stage_info(CropType.CORN, GrowthStage.V6)
            service.get_application_preferences(CropType.SOYBEAN)
        lookup_time = time.time() - start_time
        
        assert lookup_time < 0.1  # 100 lookups should be very fast


class TestCropIntegrationAgriculturalValidation:
    """Test agricultural accuracy and domain validation."""
    
    @pytest.fixture
    def service(self):
        return CropIntegrationService()
    
    def test_corn_nitrogen_timing_accuracy(self, service):
        """Test that corn nitrogen timing recommendations are agriculturally accurate."""
        # V6 stage should be critical for nitrogen
        v6_info = service.get_growth_stage_info(CropType.CORN, GrowthStage.V6)
        assert v6_info.nutrient_demand_level == "critical"
        assert "sidedress" in v6_info.recommended_methods
        
        # VT stage should also be critical
        vt_info = service.get_growth_stage_info(CropType.CORN, GrowthStage.VT)
        assert vt_info.nutrient_demand_level == "critical"
        
        # R1 stage should be high demand but avoid sidedress
        r1_info = service.get_growth_stage_info(CropType.CORN, GrowthStage.R1)
        assert r1_info.nutrient_demand_level == "high"
        assert "sidedress" in r1_info.avoided_methods
    
    def test_soybean_nitrogen_fixation_accuracy(self, service):
        """Test that soybean nitrogen fixation is properly handled."""
        soybean_prefs = service.get_application_preferences(CropType.SOYBEAN)
        nitrogen_curve = soybean_prefs.nutrient_uptake_pattern["nitrogen"]
        
        # Soybean nitrogen curve should be all zeros (N fixation)
        assert all(val == 0.0 for val in nitrogen_curve)
        
        # Soybean should avoid foliar nitrogen applications
        assert "foliar" in soybean_prefs.avoided_methods
    
    def test_tomato_calcium_requirements(self, service):
        """Test that tomato calcium requirements are properly handled."""
        tomato_info = service.get_crop_info(CropType.TOMATO)
        nutrient_reqs = tomato_info["nutrient_requirements"]
        
        # Tomato should have high calcium requirements
        assert "calcium" in nutrient_reqs
        assert nutrient_reqs["calcium"]["high"] is True
        assert "fruit_set" in nutrient_reqs["calcium"]["critical_stages"]
    
    def test_potato_tuber_timing_accuracy(self, service):
        """Test that potato tuber timing is agriculturally accurate."""
        potato_info = service.get_crop_info(CropType.POTATO)
        critical_windows = potato_info["critical_application_windows"]
        
        # Should have tuber-specific timing windows
        assert "tuber_initiation" in critical_windows
        assert "tuber_bulking" in critical_windows
        
        # Tuber initiation should be around 35-45 days
        tuber_init_window = critical_windows["tuber_initiation"]
        assert 30 <= tuber_init_window[0] <= 40
        assert 40 <= tuber_init_window[1] <= 50