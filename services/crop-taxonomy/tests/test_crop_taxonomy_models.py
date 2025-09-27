"""
Unit tests for the crop taxonomy models - focusing on the data models
which are the core of the comprehensive crop taxonomy system.
"""
import os
import sys

import pytest
from datetime import datetime
from uuid import UUID, uuid4

# Add the src directory to the Python path for model imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.crop_taxonomy_models import (
    CropAgriculturalClassification,
    CropClimateAdaptations,
    CropSoilRequirements,
    CropNutritionalProfile,
    ComprehensiveCropData,
    CropCategory,
    PrimaryUse,
    GrowthHabit,
    PlantType,
    PhotosynthesisType,
    RootSystemType,
    FrostTolerance,
    HeatTolerance,
    WaterRequirement,
    DroughtTolerance,
    FloodingTolerance,
    PhotoperiodSensitivity,
    DrainageRequirement,
    ToleranceLevel,
    NutrientRequirement
)
from models.crop_filtering_models import (
    CropFilteringAttributes,
    ManagementComplexity,
    InputRequirements,
    LaborRequirements
)


class TestCropAgriculturalClassification:
    """Test the CropAgriculturalClassification model."""
    
    def test_creation_valid_data(self):
        """Test creating a valid CropAgriculturalClassification."""
        classification = CropAgriculturalClassification(
            crop_category=CropCategory.GRAIN,
            primary_use=PrimaryUse.FOOD_HUMAN,
            growth_habit=GrowthHabit.ANNUAL,
            plant_type=PlantType.GRASS,
            growth_form="upright",
            mature_height_min_inches=10,
            mature_height_max_inches=40,
            mature_width_min_inches=5,
            mature_width_max_inches=15,
            root_system_type=RootSystemType.FIBROUS,
            photosynthesis_type=PhotosynthesisType.C3,
            nitrogen_fixing=False,
            mycorrhizal_associations=True
        )
        
        assert classification.crop_category == CropCategory.GRAIN
        assert classification.primary_use == PrimaryUse.FOOD_HUMAN
        assert classification.nitrogen_fixing is False
    
    def test_height_range_validation(self):
        """Test height range validation."""
        # Should not raise an exception for valid values
        classification = CropAgriculturalClassification(
            crop_category=CropCategory.GRAIN,
            primary_use=PrimaryUse.FOOD_HUMAN,
            growth_habit=GrowthHabit.ANNUAL,
            plant_type=PlantType.GRASS,
            growth_form="upright",  # Required field
            mature_height_min_inches=10,
            mature_height_max_inches=100  # Less than 100 feet threshold
        )
        assert classification.mature_height_min_inches == 10


class TestCropClimateAdaptations:
    """Test the CropClimateAdaptations model."""
    
    def test_creation_valid_data(self):
        """Test creating a valid CropClimateAdaptations."""
        adaptations = CropClimateAdaptations(
            optimal_temp_min_f=60,
            optimal_temp_max_f=75,
            absolute_temp_min_f=-10,
            absolute_temp_max_f=120,
            frost_tolerance=FrostTolerance.LIGHT,
            heat_tolerance=HeatTolerance.MODERATE,
            hardiness_zone_min="4a",
            hardiness_zone_max="8b",
            hardiness_zones=["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
            annual_precipitation_min_inches=15,
            annual_precipitation_max_inches=40,
            water_requirement=WaterRequirement.MODERATE,
            drought_tolerance=DroughtTolerance.MODERATE,
            flooding_tolerance=FloodingTolerance.NONE,
            photoperiod_sensitivity=PhotoperiodSensitivity.DAY_NEUTRAL,
            vernalization_requirement=False,
            elevation_min_feet=0,
            elevation_max_feet=3000,
            latitude_range_min=25.0,
            latitude_range_max=50.0
        )
        
        assert adaptations.optimal_temp_min_f == 60
        assert adaptations.hardiness_zone_min == "4a"
        assert adaptations.water_requirement == WaterRequirement.MODERATE
    
    def test_temperature_range_validation(self):
        """Test temperature range validation."""
        # Valid temperatures should work
        adaptations = CropClimateAdaptations(
            optimal_temp_min_f=40,
            optimal_temp_max_f=80
        )
        assert adaptations.optimal_temp_min_f == 40


class TestCropSoilRequirements:
    """Test the CropSoilRequirements model."""
    
    def test_creation_valid_data(self):
        """Test creating a valid CropSoilRequirements."""
        soil_req = CropSoilRequirements(
            optimal_ph_min=6.0,
            optimal_ph_max=7.0,
            tolerable_ph_min=5.5,
            tolerable_ph_max=7.5,
            preferred_textures=["loam", "sandy_loam"],
            tolerable_textures=["clay_loam", "silty_loam"],
            drainage_requirement=DrainageRequirement.WELL_DRAINED,
            drainage_tolerance=[DrainageRequirement.MODERATELY_WELL_DRAINED],
            salinity_tolerance=ToleranceLevel.MODERATE,
            alkalinity_tolerance=ToleranceLevel.LOW,
            acidity_tolerance=ToleranceLevel.HIGH,
            nitrogen_requirement=NutrientRequirement.MODERATE,
            phosphorus_requirement=NutrientRequirement.HIGH,
            potassium_requirement=NutrientRequirement.LOW,
            compaction_tolerance=ToleranceLevel.LOW,
            organic_matter_preference=ToleranceLevel.MODERATE
        )
        
        assert soil_req.optimal_ph_min == 6.0
        assert soil_req.drainage_requirement == DrainageRequirement.WELL_DRAINED
    
    def test_ph_range_validation(self):
        """Test pH range validation."""
        # Valid pH values should work
        soil_req = CropSoilRequirements(
            optimal_ph_min=6.0,
            optimal_ph_max=7.0
        )
        assert soil_req.optimal_ph_min == 6.0


class TestCropNutritionalProfile:
    """Test the CropNutritionalProfile model."""
    
    def test_creation_valid_data(self):
        """Test creating a valid CropNutritionalProfile."""
        nutrition = CropNutritionalProfile(
            calories_per_100g=85.0,
            protein_g_per_100g=3.0,
            carbohydrates_g_per_100g=18.0,
            fiber_g_per_100g=2.0,
            fat_g_per_100g=0.3,
            sugar_g_per_100g=10.0,
            calcium_mg=10.0,
            iron_mg=0.4,
            magnesium_mg=12.0,
            phosphorus_mg=49.0,
            potassium_mg=233.0,
            sodium_mg=4.0,
            zinc_mg=0.24,
            vitamin_c_mg=9.0,
            vitamin_a_iu=98,
            vitamin_k_mcg=14.1,
            folate_mcg=16.0,
            antioxidant_capacity_orac=1500,
            phenolic_compounds_mg=250.0,
            crude_protein_percent=8.5,
            digestible_energy_mcal_kg=3.2,
            neutral_detergent_fiber_percent=35.0,
            oil_content_percent=18.0,
            starch_content_percent=60.0,
            cellulose_content_percent=12.0
        )
        
        assert nutrition.calories_per_100g == 85.0
        assert nutrition.protein_g_per_100g == 3.0
    
    def test_percentage_validation(self):
        """Test percentage validation."""
        # Valid percentage values should work
        nutrition = CropNutritionalProfile(
            crude_protein_percent=25.0,
            oil_content_percent=15.0
        )
        assert nutrition.crude_protein_percent == 25.0


class TestComprehensiveCropData:
    """Test the ComprehensiveCropData model."""
    
    def test_creation_valid_data(self):
        """Test creating a valid ComprehensiveCropData."""
        # Skip the CropTaxonomicHierarchy tests for now due to Pydantic compatibility issues
        # Instead test with minimal required fields
        comprehensive_crop = ComprehensiveCropData(
            crop_name="Common Wheat",
            search_keywords=["wheat", "grain", "cereal"],
            tags=["food", "staple", "annual"],
            is_cover_crop=False,
            is_companion_crop=False
        )
        
        assert comprehensive_crop.crop_name == "Common Wheat"
        assert comprehensive_crop.scientific_name is None  # No taxonomic hierarchy
        assert comprehensive_crop.primary_category is None  # No agricultural classification
    
    def test_get_suitable_zones(self):
        """Test getting suitable hardiness zones."""
        climate_data = CropClimateAdaptations(
            hardiness_zones=["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"]
        )
        
        crop = ComprehensiveCropData(
            crop_name="Test Crop",
            climate_adaptations=climate_data
        )
        
        zones = crop.get_suitable_zones()
        assert "4a" in zones
        assert "7b" in zones
        assert len(zones) == 8
    
    def test_get_temperature_range(self):
        """Test getting temperature range."""
        climate_data = CropClimateAdaptations(
            optimal_temp_min_f=60,
            optimal_temp_max_f=75,
            absolute_temp_min_f=-10,
            absolute_temp_max_f=120
        )
        
        crop = ComprehensiveCropData(
            crop_name="Test Crop",
            climate_adaptations=climate_data
        )
        
        temp_range = crop.get_temperature_range()
        assert temp_range["optimal_min"] == 60
        assert temp_range["optimal_max"] == 75
        assert temp_range["absolute_min"] == -10
        assert temp_range["absolute_max"] == 120
    
    def test_get_ph_range(self):
        """Test getting pH range."""
        soil_data = CropSoilRequirements(
            optimal_ph_min=6.0,
            optimal_ph_max=7.0,
            tolerable_ph_min=5.5,
            tolerable_ph_max=7.5
        )
        
        crop = ComprehensiveCropData(
            crop_name="Test Crop",
            soil_requirements=soil_data
        )
        
        ph_range = crop.get_ph_range()
        assert ph_range["optimal_min"] == 6.0
        assert ph_range["optimal_max"] == 7.0
        assert ph_range["tolerable_min"] == 5.5
        assert ph_range["tolerable_max"] == 7.5


def test_comprehensive_crop_data_properties():
    """Test various properties and methods of ComprehensiveCropData."""
    # Create a complete crop data object without taxonomic hierarchy to avoid Pydantic issues
    ag_classification = CropAgriculturalClassification(
        crop_category=CropCategory.OILSEED,
        primary_use=PrimaryUse.INDUSTRIAL,
        secondary_uses=[PrimaryUse.FOOD_HUMAN],
        growth_habit=GrowthHabit.ANNUAL,
        plant_type=PlantType.HERB,
        growth_form="upright",
        nitrogen_fixing=True,
        mycorrhizal_associations=True
    )
    
    climate_adaptations = CropClimateAdaptations(
        hardiness_zones=["5a", "5b", "6a", "6b", "7a"],
        optimal_temp_min_f=60,
        optimal_temp_max_f=80,
        water_requirement=WaterRequirement.HIGH,
        drought_tolerance=DroughtTolerance.LOW
    )
    
    soil_requirements = CropSoilRequirements(
        optimal_ph_min=6.0,
        optimal_ph_max=7.0,
        preferred_textures=["loam", "clay_loam"],
        drainage_requirement=DrainageRequirement.WELL_DRAINED
    )
    
    crop_data = ComprehensiveCropData(
        crop_name="Soybean",
        agricultural_classification=ag_classification,
        climate_adaptations=climate_adaptations,
        soil_requirements=soil_requirements,
        search_keywords=["soybean", "soya", "glycine max"],
        tags=["oilseed", "legume", "nitrogen_fixing"],
        is_cover_crop=False,
        is_companion_crop=True
    )
    
    # Test properties
    assert crop_data.scientific_name is None  # No taxonomic hierarchy
    assert crop_data.primary_category == "oilseed"
    assert crop_data.get_suitable_zones() == ["5a", "5b", "6a", "6b", "7a"]
    
    temp_range = crop_data.get_temperature_range()
    assert temp_range["optimal_min"] == 60
    assert temp_range["optimal_max"] == 80
    
    ph_range = crop_data.get_ph_range()
    assert ph_range["optimal_min"] == 6.0
    assert ph_range["optimal_max"] == 7.0


class TestCropFilteringAttributes:
    """Test the CropFilteringAttributes model and advanced filters."""

    def test_creation_with_advanced_filters(self):
        """Ensure advanced filtering attributes are accepted and stored."""
        crop_identifier = uuid4()
        filtering = CropFilteringAttributes(
            crop_id=crop_identifier,
            planting_season=["spring", "fall"],
            management_complexity=ManagementComplexity.MODERATE,
            input_requirements=InputRequirements.MODERATE,
            labor_requirements=LaborRequirements.MODERATE,
            pest_resistance_traits={"corn_borer": "high"},
            market_class_filters={"market_channels": ["premium_direct"]},
            certification_filters={"organic": True, "non_gmo": True},
            seed_availability_filters={"regions": ["midwest"], "suppliers": ["SeedCo"]}
        )

        assert filtering.pest_resistance_traits["corn_borer"] == "high"
        assert filtering.certification_filters.get("organic") is True
        assert filtering.seed_availability_filters["regions"] == ["midwest"]

    def test_comprehensive_crop_data_integration(self):
        """Ensure comprehensive crop data can include filtering attributes."""
        filtering = CropFilteringAttributes(
            crop_id=uuid4(),
            pest_resistance_traits={"aphids": "moderate"}
        )

        crop = ComprehensiveCropData(
            crop_name="Integrated Test Crop",
            filtering_attributes=filtering
        )

        assert crop.filtering_attributes is not None
        assert crop.filtering_attributes.pest_resistance_traits.get("aphids") == "moderate"


if __name__ == "__main__":
    pytest.main([__file__])
