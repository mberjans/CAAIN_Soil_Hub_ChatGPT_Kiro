"""
Comprehensive unit tests for the crop taxonomy system.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from uuid import UUID, uuid4

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.crop_taxonomy_models import (
    CropTaxonomicHierarchy,
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

# Import the service with the correct path
try:
    from services.crop_taxonomy_service import CropTaxonomyService
except ImportError:
    # Handle cases where the services module isn't directly importable
    from src.services.crop_taxonomy_service import CropTaxonomyService


class TestCropTaxonomicHierarchy:
    """Test the CropTaxonomicHierarchy model."""
    
    def test_creation_valid_data(self):
        """Test creating a valid CropTaxonomicHierarchy."""
        hierarchy = CropTaxonomicHierarchy(
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order_name="Poales",
            family="Poaceae",
            genus="Triticum",
            species="aestivum"
        )
        
        assert hierarchy.kingdom == "Plantae"
        assert hierarchy.scientific_name == "Triticum aestivum"
        assert hierarchy.binomial_name == "Triticum aestivum"
    
    def test_creation_with_subspecies_variety(self):
        """Test creating hierarchy with subspecies and variety."""
        hierarchy = CropTaxonomicHierarchy(
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order_name="Fabales",
            family="Fabaceae",
            genus="Glycine",
            species="max",
            subspecies="subsp._us",
            variety="var._meridian"
        )
        
        assert hierarchy.scientific_name == "Glycine max subsp. subsp._us var. var._meridian"
    
    def test_scientific_name_property(self):
        """Test the scientific_name property."""
        hierarchy = CropTaxonomicHierarchy(
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order_name="Poales",
            family="Poaceae",
            genus="Triticum",
            species="aestivum"
        )
        
        assert hierarchy.scientific_name == "Triticum aestivum"
    
    def test_binomial_name_property(self):
        """Test the binomial_name property."""
        hierarchy = CropTaxonomicHierarchy(
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order_name="Poales",
            family="Poaceae",
            genus="Triticum",
            species="aestivum"
        )
        
        assert hierarchy.binomial_name == "Triticum aestivum"


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
            mature_height_min_inches=10,
            mature_height_max_inches=100  # Less than 100 feet threshold
        )
        assert classification.mature_height_min_inches == 10
    
    def test_height_range_invalid(self):
        """Test that very large height values are rejected."""
        # Since the validation is in the validator, we need to properly trigger it
        with pytest.raises(ValueError):
            CropAgriculturalClassification(
                crop_category=CropCategory.GRAIN,
                primary_use=PrimaryUse.FOOD_HUMAN,
                growth_habit=GrowthHabit.ANNUAL,
                plant_type=PlantType.GRASS,
                mature_height_min_inches=1500  # This would exceed 100 feet threshold
            )


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
        crop_tax = CropTaxonomicHierarchy(
            kingdom="Plantae",
            phylum="Tracheophyta",
            class_name="Magnoliopsida",
            order_name="Poales",
            family="Poaceae",
            genus="Triticum",
            species="aestivum"
        )
        
        ag_class = CropAgriculturalClassification(
            crop_category=CropCategory.GRAIN,
            primary_use=PrimaryUse.FOOD_HUMAN,
            growth_habit=GrowthHabit.ANNUAL,
            plant_type=PlantType.GRASS
        )
        
        comprehensive_crop = ComprehensiveCropData(
            crop_name="Common Wheat",
            taxonomic_hierarchy=crop_tax,
            agricultural_classification=ag_class,
            search_keywords=["wheat", "grain", "cereal"],
            tags=["food", "staple", "annual"],
            is_cover_crop=False,
            is_companion_crop=False
        )
        
        assert comprehensive_crop.crop_name == "Common Wheat"
        assert comprehensive_crop.scientific_name == "Triticum aestivum"
        assert comprehensive_crop.primary_category == "grain"
    
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


class TestCropTaxonomyService:
    """Test the CropTaxonomyService."""
    
    @pytest.fixture
    def service(self):
        """Create a CropTaxonomyService instance for testing."""
        # Mock the database to avoid requiring actual database connection
        patch_target = f"{CropTaxonomyService.__module__}.CropTaxonomyDatabase"
        with patch(patch_target, create=True) as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.test_connection.return_value = False  # No DB available
            mock_db.return_value = mock_db_instance
            
            service = CropTaxonomyService()
            service.db = mock_db_instance
            service.database_available = False
            return service
    
    def test_initialization_with_mocked_db(self):
        """Test service initialization with mocked database."""
        patch_target = f"{CropTaxonomyService.__module__}.CropTaxonomyDatabase"
        with patch(patch_target, create=True) as mock_db:
            mock_db_instance = Mock()
            mock_db_instance.test_connection.return_value = True
            mock_db.return_value = mock_db_instance
            
            service = CropTaxonomyService()
            assert service.database_available is True
            assert service.db == mock_db_instance
    
    def test_classify_crop_wheat_from_common_name(self, service):
        """Test classifying wheat from common name."""
        # Mock the private method that handles classification
        with patch.object(service, '_classify_from_common_name') as mock_method:
            mock_taxonomy = CropTaxonomicHierarchy(
                kingdom="Plantae",
                phylum="Tracheophyta",
                class_name="Magnoliopsida",
                order_name="Poales",
                family="Poaceae",
                genus="Triticum",
                species="aestivum"
            )
            mock_method.return_value = mock_taxonomy
            
            from src.models.service_models import (
                CropClassificationRequest,
                ConfidenceLevel
            )
            
            request = CropClassificationRequest(request_id="test-req", crop_name="wheat")
            result = service._classify_from_common_name("wheat")
            
            # Check that the taxonomic knowledge base was properly initialized
            assert "wheat" in service.genus_species_map
            assert service.genus_species_map["wheat"]["genus"] == "Triticum"
            assert service.genus_species_map["wheat"]["species"] == "aestivum"
    
    def test_get_family_from_genus_species(self, service):
        """Test the _get_family_from_genus_species method."""
        family = service._get_family_from_genus_species("Triticum", "aestivum")
        assert family == "Poaceae"
        
        family = service._get_family_from_genus_species("Glycine", "max")
        assert family == "Fabaceae"
    
    def test_get_order_from_family(self, service):
        """Test the _get_order_from_family method."""
        order = service._get_order_from_family("Poaceae")
        assert order == "Poales"
        
        order = service._get_order_from_family("Fabaceae")
        assert order == "Fabales"
    
    def test_get_botanical_authority(self, service):
        """Test the _get_botanical_authority method."""
        authority = service._get_botanical_authority("Triticum", "aestivum")
        assert authority == "L."
        
        authority = service._get_botanical_authority("Glycine", "max")
        assert authority == "(L.) Merr."

    def test_reference_dataset_loaded(self, service):
        """Ensure the reference dataset loads comprehensive crop entries."""
        assert len(service.reference_crops) >= 10
        names = []
        for crop in service.reference_crops:
            names.append(crop.crop_name.lower())
        assert "sorghum" in names

    @pytest.mark.asyncio
    async def test_classify_uses_reference_dataset(self, service):
        """Classification should succeed for crops supplied by the reference dataset."""
        taxonomy = await service._classify_from_common_name("sorghum")
        assert taxonomy is not None
        assert taxonomy.genus == "Sorghum"

    @pytest.mark.asyncio
    async def test_list_reference_crops_filters_by_category(self, service):
        """Verify category filtering works with the reference dataset."""
        crops = await service.list_reference_crops(category="grain", limit=20)
        assert len(crops) > 0
        found_wheat = False
        for crop in crops:
            assert crop.agricultural_classification is not None
            assert crop.agricultural_classification.crop_category.value == "grain"
            if crop.crop_name.lower() == "wheat":
                found_wheat = True
        assert found_wheat is True
    
    def test_get_typical_ploidy(self, service):
        """Test the _get_typical_ploidy method."""
        ploidy = service._get_typical_ploidy("wheat")
        assert ploidy == 6  # Hexaploid
        
        ploidy = service._get_typical_ploidy("corn")
        assert ploidy == 2  # Diploid
    
    def test_get_chromosome_count(self, service):
        """Test the _get_chromosome_count method."""
        count = service._get_chromosome_count("wheat")
        assert count == 42  # 2n = 6x = 42
        
        count = service._get_chromosome_count("corn")
        assert count == 20  # 2n = 20
    
    def test_calculate_similarity(self, service):
        """Test the _calculate_similarity method."""
        # Test exact match
        similarity = service._calculate_similarity("wheat", "wheat")
        assert similarity == 1.0
        
        # Test partial match
        similarity = service._calculate_similarity("wheat", "wheats")
        assert 0.8 < similarity < 1.0
        
        # Test no match
        similarity = service._calculate_similarity("wheat", "corn")
        assert similarity < 0.5


def test_comprehensive_crop_data_properties():
    """Test various properties and methods of ComprehensiveCropData."""
    # Create a complete crop data object
    tax_hierarchy = CropTaxonomicHierarchy(
        kingdom="Plantae",
        phylum="Tracheophyta", 
        class_name="Magnoliopsida",
        order_name="Fabales",
        family="Fabaceae",
        genus="Glycine",
        species="max",
        common_synonyms=["soybean", "soya"]
    )
    
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
        taxonomic_hierarchy=tax_hierarchy,
        agricultural_classification=ag_classification,
        climate_adaptations=climate_adaptations,
        soil_requirements=soil_requirements,
        search_keywords=["soybean", "soya", "glycine max"],
        tags=["oilseed", "legume", "nitrogen_fixing"],
        is_cover_crop=False,
        is_companion_crop=True
    )
    
    # Test properties
    assert crop_data.scientific_name == "Glycine max"
    assert crop_data.primary_category == "oilseed"
    assert crop_data.get_suitable_zones() == ["5a", "5b", "6a", "6b", "7a"]
    
    temp_range = crop_data.get_temperature_range()
    assert temp_range["optimal_min"] == 60
    assert temp_range["optimal_max"] == 80
    
    ph_range = crop_data.get_ph_range()
    assert ph_range["optimal_min"] == 6.0
    assert ph_range["optimal_max"] == 7.0


if __name__ == "__main__":
    pytest.main([__file__])
