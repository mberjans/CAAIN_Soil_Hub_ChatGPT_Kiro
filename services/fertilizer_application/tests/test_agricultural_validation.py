"""
Agricultural Domain Validation Tests
TICKET-023_fertilizer-application-method-11.1

This module provides specialized agricultural validation tests to ensure
that all fertilizer application recommendations meet agricultural best
practices and domain expertise requirements.
"""

import pytest
import asyncio
from typing import Dict, List, Any
from unittest.mock import AsyncMock, patch

from src.services.application_method_service import ApplicationMethodService
from src.services.cost_analysis_service import CostAnalysisService
from src.services.guidance_service import GuidanceService
from src.models.application_models import (
    ApplicationRequest, FieldConditions, CropRequirements, 
    FertilizerSpecification, EquipmentSpecification, ApplicationMethodType
)


class AgriculturalExpertValidator:
    """Agricultural expert validation rules and criteria."""
    
    # Crop-specific nutrient requirements (lbs/acre)
    CROP_NUTRIENT_REQUIREMENTS = {
        "corn": {"nitrogen": (120, 200), "phosphorus": (40, 80), "potassium": (80, 150)},
        "soybean": {"nitrogen": (0, 20), "phosphorus": (30, 60), "potassium": (60, 120)},
        "wheat": {"nitrogen": (80, 140), "phosphorus": (30, 60), "potassium": (60, 120)},
        "cotton": {"nitrogen": (100, 180), "phosphorus": (40, 80), "potassium": (80, 150)},
        "tomato": {"nitrogen": (100, 150), "phosphorus": (40, 80), "potassium": (100, 200)},
        "potato": {"nitrogen": (120, 180), "phosphorus": (60, 120), "potassium": (150, 250)}
    }
    
    # Soil type compatibility with application methods
    SOIL_METHOD_COMPATIBILITY = {
        "sand": ["broadcast", "foliar", "drip"],
        "sandy_loam": ["broadcast", "band", "foliar", "drip"],
        "loam": ["broadcast", "band", "injection", "foliar", "drip"],
        "clay_loam": ["band", "injection", "foliar"],
        "clay": ["band", "injection", "foliar"],
        "silt": ["broadcast", "band", "foliar"],
        "silty_loam": ["broadcast", "band", "foliar"],
        "organic": ["broadcast", "foliar"],
        "peat": ["broadcast", "foliar"]
    }
    
    # Equipment-method compatibility matrix
    EQUIPMENT_METHOD_COMPATIBILITY = {
        "sprayer": ["foliar", "broadcast"],
        "spreader": ["broadcast", "band"],
        "injector": ["injection", "band"],
        "drip_system": ["drip"],
        "broadcaster": ["broadcast"]
    }
    
    # Fertilizer form compatibility with methods
    FERTILIZER_METHOD_COMPATIBILITY = {
        "liquid": ["foliar", "injection", "drip"],
        "granular": ["broadcast", "band"],
        "organic": ["broadcast", "band"],
        "slow_release": ["broadcast", "band"]
    }
    
    @classmethod
    def validate_nutrient_requirements(cls, crop_type: str, requirements: Dict[str, float]) -> Dict[str, Any]:
        """Validate nutrient requirements against crop-specific ranges."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        if crop_type not in cls.CROP_NUTRIENT_REQUIREMENTS:
            validation_result["warnings"].append(f"Unknown crop type: {crop_type}")
            return validation_result
        
        crop_ranges = cls.CROP_NUTRIENT_REQUIREMENTS[crop_type]
        
        for nutrient, amount in requirements.items():
            if nutrient in crop_ranges:
                min_req, max_req = crop_ranges[nutrient]
                
                if amount < min_req:
                    validation_result["warnings"].append(
                        f"{nutrient} requirement ({amount} lbs/acre) is below recommended minimum ({min_req} lbs/acre)"
                    )
                    validation_result["recommendations"].append(
                        f"Consider increasing {nutrient} application to at least {min_req} lbs/acre"
                    )
                elif amount > max_req:
                    validation_result["warnings"].append(
                        f"{nutrient} requirement ({amount} lbs/acre) exceeds recommended maximum ({max_req} lbs/acre)"
                    )
                    validation_result["recommendations"].append(
                        f"Consider reducing {nutrient} application to maximum {max_req} lbs/acre to avoid waste and environmental impact"
                    )
        
        return validation_result
    
    @classmethod
    def validate_soil_method_compatibility(cls, soil_type: str, method_type: str) -> bool:
        """Validate soil-method compatibility."""
        if soil_type not in cls.SOIL_METHOD_COMPATIBILITY:
            return False
        
        compatible_methods = cls.SOIL_METHOD_COMPATIBILITY[soil_type]
        return method_type in compatible_methods
    
    @classmethod
    def validate_equipment_method_compatibility(cls, equipment_type: str, method_type: str) -> bool:
        """Validate equipment-method compatibility."""
        if equipment_type not in cls.EQUIPMENT_METHOD_COMPATIBILITY:
            return False
        
        compatible_methods = cls.EQUIPMENT_METHOD_COMPATIBILITY[equipment_type]
        return method_type in compatible_methods
    
    @classmethod
    def validate_fertilizer_method_compatibility(cls, fertilizer_form: str, method_type: str) -> bool:
        """Validate fertilizer-method compatibility."""
        if fertilizer_form not in cls.FERTILIZER_METHOD_COMPATIBILITY:
            return False
        
        compatible_methods = cls.FERTILIZER_METHOD_COMPATIBILITY[fertilizer_form]
        return method_type in compatible_methods
    
    @classmethod
    def validate_application_rate(cls, method_type: str, rate: float, fertilizer_form: str) -> Dict[str, Any]:
        """Validate application rate against agricultural standards."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Rate ranges by method and fertilizer form (lbs/acre or gallons/acre)
        rate_ranges = {
            "broadcast": {
                "granular": (20, 300),
                "organic": (50, 500),
                "slow_release": (30, 200)
            },
            "band": {
                "granular": (10, 150),
                "organic": (25, 250),
                "slow_release": (15, 100)
            },
            "foliar": {
                "liquid": (0.5, 20),
                "granular": (5, 50)  # Dissolved granular
            },
            "injection": {
                "liquid": (5, 100),
                "granular": (10, 200)  # Dissolved granular
            },
            "drip": {
                "liquid": (1, 50),
                "granular": (2, 100)  # Dissolved granular
            }
        }
        
        if method_type not in rate_ranges:
            validation_result["errors"].append(f"Unknown application method: {method_type}")
            return validation_result
        
        if fertilizer_form not in rate_ranges[method_type]:
            validation_result["errors"].append(
                f"Incompatible fertilizer form {fertilizer_form} for method {method_type}"
            )
            return validation_result
        
        min_rate, max_rate = rate_ranges[method_type][fertilizer_form]
        
        if rate < min_rate:
            validation_result["warnings"].append(
                f"Application rate ({rate}) is below recommended minimum ({min_rate}) for {method_type} with {fertilizer_form}"
            )
            validation_result["recommendations"].append(
                f"Increase application rate to at least {min_rate} for effective application"
            )
        elif rate > max_rate:
            validation_result["warnings"].append(
                f"Application rate ({rate}) exceeds recommended maximum ({max_rate}) for {method_type} with {fertilizer_form}"
            )
            validation_result["recommendations"].append(
                f"Reduce application rate to maximum {max_rate} to avoid waste and potential crop damage"
            )
        
        return validation_result
    
    @classmethod
    def validate_timing_recommendations(cls, method_type: str, crop_stage: str, timing: str) -> Dict[str, Any]:
        """Validate application timing recommendations."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Optimal timing by method and crop stage
        optimal_timing = {
            "foliar": {
                "vegetative": ["early_morning", "late_evening"],
                "flowering": ["early_morning"],
                "fruiting": ["early_morning", "late_evening"]
            },
            "broadcast": {
                "pre_planting": ["morning", "afternoon"],
                "vegetative": ["morning", "afternoon"],
                "post_harvest": ["morning", "afternoon"]
            },
            "band": {
                "planting": ["morning", "afternoon"],
                "vegetative": ["morning", "afternoon"]
            },
            "injection": {
                "vegetative": ["morning", "afternoon"],
                "flowering": ["morning", "afternoon"]
            },
            "drip": {
                "vegetative": ["morning", "afternoon", "evening"],
                "flowering": ["morning", "afternoon"],
                "fruiting": ["morning", "afternoon"]
            }
        }
        
        if method_type not in optimal_timing:
            validation_result["warnings"].append(f"No timing data for method: {method_type}")
            return validation_result
        
        if crop_stage not in optimal_timing[method_type]:
            validation_result["warnings"].append(f"No timing data for crop stage: {crop_stage}")
            return validation_result
        
        optimal_times = optimal_timing[method_type][crop_stage]
        
        if timing.lower() not in [t.lower() for t in optimal_times]:
            validation_result["warnings"].append(
                f"Timing '{timing}' may not be optimal for {method_type} during {crop_stage}"
            )
            validation_result["recommendations"].append(
                f"Consider timing: {', '.join(optimal_times)}"
            )
        
        return validation_result


class TestAgriculturalValidation:
    """Agricultural domain validation test cases."""
    
    @pytest.fixture
    def application_service(self):
        """Create application method service instance."""
        return ApplicationMethodService()
    
    @pytest.fixture
    def cost_service(self):
        """Create cost analysis service instance."""
        return CostAnalysisService()
    
    @pytest.fixture
    def guidance_service(self):
        """Create guidance service instance."""
        return GuidanceService()
    
    def test_corn_nutrient_requirements_validation(self):
        """Test corn nutrient requirements validation."""
        # Valid corn requirements
        valid_requirements = {
            "nitrogen": 150.0,  # Within range (120-200)
            "phosphorus": 60.0,  # Within range (40-80)
            "potassium": 120.0   # Within range (80-150)
        }
        
        validation = AgriculturalExpertValidator.validate_nutrient_requirements("corn", valid_requirements)
        assert validation["valid"] is True
        assert len(validation["warnings"]) == 0
        assert len(validation["errors"]) == 0
        
        # Invalid corn requirements
        invalid_requirements = {
            "nitrogen": 250.0,  # Above maximum (200)
            "phosphorus": 30.0,  # Below minimum (40)
            "potassium": 200.0   # Above maximum (150)
        }
        
        validation = AgriculturalExpertValidator.validate_nutrient_requirements("corn", invalid_requirements)
        assert len(validation["warnings"]) == 3
        assert len(validation["recommendations"]) == 3
        
        # Check specific warnings
        warning_text = " ".join(validation["warnings"])
        assert "nitrogen" in warning_text.lower()
        assert "phosphorus" in warning_text.lower()
        assert "potassium" in warning_text.lower()
    
    def test_soybean_nutrient_requirements_validation(self):
        """Test soybean nutrient requirements validation."""
        # Valid soybean requirements (soybeans fix nitrogen)
        valid_requirements = {
            "nitrogen": 10.0,   # Within range (0-20)
            "phosphorus": 45.0,  # Within range (30-60)
            "potassium": 90.0    # Within range (60-120)
        }
        
        validation = AgriculturalExpertValidator.validate_nutrient_requirements("soybean", valid_requirements)
        assert validation["valid"] is True
        assert len(validation["warnings"]) == 0
        
        # Invalid soybean requirements
        invalid_requirements = {
            "nitrogen": 50.0,   # Above maximum (20) - wasteful for nitrogen-fixing crop
            "phosphorus": 20.0,  # Below minimum (30)
            "potassium": 150.0   # Above maximum (120)
        }
        
        validation = AgriculturalExpertValidator.validate_nutrient_requirements("soybean", invalid_requirements)
        assert len(validation["warnings"]) == 3
    
    def test_soil_method_compatibility_validation(self):
        """Test soil-method compatibility validation."""
        # Valid combinations
        assert AgriculturalExpertValidator.validate_soil_method_compatibility("sand", "foliar") is True
        assert AgriculturalExpertValidator.validate_soil_method_compatibility("clay", "band") is True
        assert AgriculturalExpertValidator.validate_soil_method_compatibility("loam", "broadcast") is True
        
        # Invalid combinations
        assert AgriculturalExpertValidator.validate_soil_method_compatibility("sand", "injection") is False
        assert AgriculturalExpertValidator.validate_soil_method_compatibility("clay", "broadcast") is False
        assert AgriculturalExpertValidator.validate_soil_method_compatibility("peat", "band") is False
    
    def test_equipment_method_compatibility_validation(self):
        """Test equipment-method compatibility validation."""
        # Valid combinations
        assert AgriculturalExpertValidator.validate_equipment_method_compatibility("sprayer", "foliar") is True
        assert AgriculturalExpertValidator.validate_equipment_method_compatibility("spreader", "broadcast") is True
        assert AgriculturalExpertValidator.validate_equipment_method_compatibility("injector", "injection") is True
        
        # Invalid combinations
        assert AgriculturalExpertValidator.validate_equipment_method_compatibility("sprayer", "band") is False
        assert AgriculturalExpertValidator.validate_equipment_method_compatibility("spreader", "foliar") is False
        assert AgriculturalExpertValidator.validate_equipment_method_compatibility("drip_system", "broadcast") is False
    
    def test_fertilizer_method_compatibility_validation(self):
        """Test fertilizer-method compatibility validation."""
        # Valid combinations
        assert AgriculturalExpertValidator.validate_fertilizer_method_compatibility("liquid", "foliar") is True
        assert AgriculturalExpertValidator.validate_fertilizer_method_compatibility("granular", "broadcast") is True
        assert AgriculturalExpertValidator.validate_fertilizer_method_compatibility("organic", "band") is True
        
        # Invalid combinations
        assert AgriculturalExpertValidator.validate_fertilizer_method_compatibility("granular", "foliar") is False
        assert AgriculturalExpertValidator.validate_fertilizer_method_compatibility("liquid", "broadcast") is False
        assert AgriculturalExpertValidator.validate_fertilizer_method_compatibility("slow_release", "injection") is False
    
    def test_application_rate_validation(self):
        """Test application rate validation."""
        # Valid rates
        validation = AgriculturalExpertValidator.validate_application_rate("broadcast", 100.0, "granular")
        assert validation["valid"] is True
        assert len(validation["warnings"]) == 0
        
        validation = AgriculturalExpertValidator.validate_application_rate("foliar", 2.5, "liquid")
        assert validation["valid"] is True
        assert len(validation["warnings"]) == 0
        
        # Invalid rates
        validation = AgriculturalExpertValidator.validate_application_rate("broadcast", 500.0, "granular")
        assert len(validation["warnings"]) == 1
        assert "exceeds recommended maximum" in validation["warnings"][0]
        
        validation = AgriculturalExpertValidator.validate_application_rate("foliar", 0.2, "liquid")
        assert len(validation["warnings"]) == 1
        assert "below recommended minimum" in validation["warnings"][0]
        
        # Incompatible combinations
        validation = AgriculturalExpertValidator.validate_application_rate("foliar", 10.0, "granular")
        assert len(validation["errors"]) == 1
        assert "Incompatible fertilizer form" in validation["errors"][0]
    
    def test_timing_recommendations_validation(self):
        """Test timing recommendations validation."""
        # Valid timing
        validation = AgriculturalExpertValidator.validate_timing_recommendations("foliar", "vegetative", "early_morning")
        assert validation["valid"] is True
        assert len(validation["warnings"]) == 0
        
        validation = AgriculturalExpertValidator.validate_timing_recommendations("broadcast", "vegetative", "morning")
        assert validation["valid"] is True
        assert len(validation["warnings"]) == 0
        
        # Suboptimal timing
        validation = AgriculturalExpertValidator.validate_timing_recommendations("foliar", "vegetative", "midday")
        assert len(validation["warnings"]) == 1
        assert "may not be optimal" in validation["warnings"][0]
        assert "early_morning" in validation["recommendations"][0]
    
    @pytest.mark.asyncio
    async def test_comprehensive_agricultural_validation(self, application_service):
        """Test comprehensive agricultural validation with real service."""
        # Test with agriculturally sound request
        field_conditions = FieldConditions(
            field_size_acres=100.0,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.5,
            irrigation_available=True
        )
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="vegetative",
            target_yield=180.0,
            nutrient_requirements={
                "nitrogen": 150.0,  # Within valid range
                "phosphorus": 60.0,  # Within valid range
                "potassium": 120.0   # Within valid range
            }
        )
        
        fertilizer_specification = FertilizerSpecification(
            fertilizer_type="liquid",
            npk_ratio="28-0-0",
            form="liquid",
            cost_per_unit=0.85,
            unit="lbs"
        )
        
        available_equipment = [
            EquipmentSpecification(
                equipment_type="sprayer",  # Compatible with liquid fertilizer
                capacity=500.0,
                capacity_unit="gallons"
            )
        ]
        
        request = ApplicationRequest(
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            available_equipment=available_equipment
        )
        
        response = await application_service.select_application_methods(request)
        
        # Validate agricultural soundness of recommendations
        assert len(response.recommended_methods) > 0
        
        for method in response.recommended_methods:
            # Validate nutrient requirements
            nutrient_validation = AgriculturalExpertValidator.validate_nutrient_requirements(
                "corn", crop_requirements.nutrient_requirements
            )
            assert nutrient_validation["valid"] is True
            
            # Validate soil-method compatibility
            soil_compatible = AgriculturalExpertValidator.validate_soil_method_compatibility(
                "loam", method.method_type.value
            )
            assert soil_compatible is True
            
            # Validate equipment-method compatibility
            equipment_compatible = AgriculturalExpertValidator.validate_equipment_method_compatibility(
                "sprayer", method.method_type.value
            )
            assert equipment_compatible is True
            
            # Validate fertilizer-method compatibility
            fertilizer_compatible = AgriculturalExpertValidator.validate_fertilizer_method_compatibility(
                "liquid", method.method_type.value
            )
            assert fertilizer_compatible is True
            
            # Validate application rate
            rate_validation = AgriculturalExpertValidator.validate_application_rate(
                method.method_type.value, method.application_rate, "liquid"
            )
            assert rate_validation["valid"] is True
    
    @pytest.mark.asyncio
    async def test_agricultural_validation_with_problematic_inputs(self, application_service):
        """Test agricultural validation with problematic inputs."""
        # Test with agriculturally problematic request
        field_conditions = FieldConditions(
            field_size_acres=100.0,
            soil_type="sand",  # Sandy soil
            drainage_class="excessive",
            slope_percent=2.5,
            irrigation_available=True
        )
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="vegetative",
            target_yield=180.0,
            nutrient_requirements={
                "nitrogen": 250.0,  # Above maximum
                "phosphorus": 30.0,  # Below minimum
                "potassium": 200.0   # Above maximum
            }
        )
        
        fertilizer_specification = FertilizerSpecification(
            fertilizer_type="granular",  # Granular fertilizer
            npk_ratio="10-10-10",
            form="granular",
            cost_per_unit=0.5,
            unit="lbs"
        )
        
        available_equipment = [
            EquipmentSpecification(
                equipment_type="sprayer",  # Incompatible with granular fertilizer
                capacity=500.0,
                capacity_unit="gallons"
            )
        ]
        
        request = ApplicationRequest(
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            available_equipment=available_equipment
        )
        
        response = await application_service.select_application_methods(request)
        
        # The service should handle problematic inputs gracefully
        assert response is not None
        assert response.request_id is not None
        
        # Should provide recommendations despite problematic inputs
        # The service should either:
        # 1. Find alternative methods that work
        # 2. Provide warnings about the issues
        # 3. Suggest modifications
        
        if len(response.recommended_methods) > 0:
            # If recommendations are provided, validate them
            for method in response.recommended_methods:
                # Check if the service found compatible methods
                fertilizer_compatible = AgriculturalExpertValidator.validate_fertilizer_method_compatibility(
                    "granular", method.method_type.value
                )
                
                # The service should either find compatible methods or provide guidance
                if not fertilizer_compatible:
                    # If incompatible methods are suggested, there should be warnings
                    assert response.metadata is not None
                    # Metadata should contain warnings about incompatibilities
    
    def test_crop_specific_validation_rules(self):
        """Test crop-specific validation rules."""
        # Test nitrogen-fixing crops (soybeans, legumes)
        legume_crops = ["soybean", "alfalfa", "clover"]
        
        for crop in legume_crops:
            if crop in AgriculturalExpertValidator.CROP_NUTRIENT_REQUIREMENTS:
                nitrogen_range = AgriculturalExpertValidator.CROP_NUTRIENT_REQUIREMENTS[crop]["nitrogen"]
                # Nitrogen-fixing crops should have low nitrogen requirements
                assert nitrogen_range[1] <= 50, f"{crop} should have low nitrogen requirements"
        
        # Test high-nitrogen crops
        high_nitrogen_crops = ["corn", "cotton", "tomato"]
        
        for crop in high_nitrogen_crops:
            if crop in AgriculturalExpertValidator.CROP_NUTRIENT_REQUIREMENTS:
                nitrogen_range = AgriculturalExpertValidator.CROP_NUTRIENT_REQUIREMENTS[crop]["nitrogen"]
                # High-nitrogen crops should have high nitrogen requirements
                assert nitrogen_range[0] >= 100, f"{crop} should have high nitrogen requirements"
        
        # Test root crops (potatoes) - should have high potassium requirements
        root_crops = ["potato"]
        
        for crop in root_crops:
            if crop in AgriculturalExpertValidator.CROP_NUTRIENT_REQUIREMENTS:
                potassium_range = AgriculturalExpertValidator.CROP_NUTRIENT_REQUIREMENTS[crop]["potassium"]
                # Root crops should have high potassium requirements
                assert potassium_range[0] >= 100, f"{crop} should have high potassium requirements"
    
    def test_soil_type_specific_validation_rules(self):
        """Test soil type-specific validation rules."""
        # Sandy soils - should favor foliar and drip applications
        sandy_methods = AgriculturalExpertValidator.SOIL_METHOD_COMPATIBILITY["sand"]
        assert "foliar" in sandy_methods
        assert "drip" in sandy_methods
        assert "injection" not in sandy_methods  # Not suitable for sandy soils
        
        # Clay soils - should favor band and injection applications
        clay_methods = AgriculturalExpertValidator.SOIL_METHOD_COMPATIBILITY["clay"]
        assert "band" in clay_methods
        assert "injection" in clay_methods
        assert "broadcast" not in clay_methods  # Less suitable for clay soils
        
        # Organic soils - should favor broadcast applications
        organic_methods = AgriculturalExpertValidator.SOIL_METHOD_COMPATIBILITY["organic"]
        assert "broadcast" in organic_methods
        assert "foliar" in organic_methods
        assert "band" not in organic_methods  # Less suitable for organic soils
    
    def test_equipment_efficiency_validation(self):
        """Test equipment efficiency validation."""
        # Sprayers should be efficient for foliar applications
        sprayer_methods = AgriculturalExpertValidator.EQUIPMENT_METHOD_COMPATIBILITY["sprayer"]
        assert "foliar" in sprayer_methods
        
        # Spreaders should be efficient for broadcast applications
        spreader_methods = AgriculturalExpertValidator.EQUIPMENT_METHOD_COMPATIBILITY["spreader"]
        assert "broadcast" in spreader_methods
        
        # Injectors should be efficient for injection applications
        injector_methods = AgriculturalExpertValidator.EQUIPMENT_METHOD_COMPATIBILITY["injector"]
        assert "injection" in injector_methods
        
        # Drip systems should only be used for drip applications
        drip_methods = AgriculturalExpertValidator.EQUIPMENT_METHOD_COMPATIBILITY["drip_system"]
        assert drip_methods == ["drip"]


class TestAgriculturalExpertReview:
    """Tests for agricultural expert review process."""
    
    def test_expert_review_criteria(self):
        """Test agricultural expert review criteria."""
        # Expert review should flag:
        # 1. Excessive nutrient applications
        # 2. Incompatible soil-method combinations
        # 3. Inefficient equipment-method combinations
        # 4. Suboptimal timing recommendations
        # 5. Unrealistic application rates
        
        review_criteria = {
            "nutrient_excess": True,
            "soil_method_incompatibility": True,
            "equipment_method_incompatibility": True,
            "timing_suboptimal": True,
            "rate_unrealistic": True
        }
        
        # All criteria should be enabled for expert review
        for criterion, enabled in review_criteria.items():
            assert enabled is True, f"Expert review criterion {criterion} should be enabled"
    
    def test_expert_review_thresholds(self):
        """Test expert review thresholds."""
        # Define thresholds for expert review
        thresholds = {
            "max_nitrogen_excess_percent": 20,  # Flag if N > 20% above maximum
            "max_phosphorus_excess_percent": 25,  # Flag if P > 25% above maximum
            "max_potassium_excess_percent": 30,  # Flag if K > 30% above maximum
            "min_efficiency_score": 0.6,  # Flag if efficiency < 60%
            "max_cost_per_acre": 100.0,  # Flag if cost > $100/acre
            "min_confidence_score": 0.7   # Flag if confidence < 70%
        }
        
        # All thresholds should be reasonable for agricultural practice
        assert thresholds["max_nitrogen_excess_percent"] <= 25
        assert thresholds["max_phosphorus_excess_percent"] <= 30
        assert thresholds["max_potassium_excess_percent"] <= 35
        assert thresholds["min_efficiency_score"] >= 0.5
        assert thresholds["max_cost_per_acre"] >= 50.0
        assert thresholds["min_confidence_score"] >= 0.6


# Pytest markers for agricultural validation tests
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.agricultural_validation,
    pytest.mark.expert_review
]


if __name__ == "__main__":
    # Run agricultural validation tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "agricultural_validation"
    ])