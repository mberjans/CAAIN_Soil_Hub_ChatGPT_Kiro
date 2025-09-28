"""
Unit tests for enhanced crop filtering attributes model.

This test file verifies that the extended crop filtering attributes model 
works correctly with both legacy dictionary formats and the new enhanced 
data structures for pest resistance, market class, certification, and 
seed availability.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import pytest
from datetime import date
from uuid import UUID, uuid4

# Using relative import since we're in the project root
from services.crop_taxonomy.src.models.crop_filtering_models import (
    # Existing enums
    ManagementComplexity, 
    InputRequirements, 
    LaborRequirements,
    CarbonSequestrationPotential,
    BiodiversitySupport,
    PollinatorValue,
    WaterUseEfficiency,
    MarketStability,
    # New enums
    PestResistanceLevel,
    PestResistanceEffectiveness,
    MarketClassType,
    CertificationType,
    AvailabilityStatus,
    SeedSource,
    SeedTreatment,
    MarketPremiumType,
    ComplianceStatus,
    PestType,
    # Models
    CropFilteringAttributes,
    EnhancedPestResistanceData,
    EnhancedMarketClassData,
    EnhancedCertificationData,
    EnhancedSeedAvailabilityData,
    PestResistanceProfile,
    MarketClassProfile,
    CertificationProfile,
    SupplierInfo,
    RegionalAvailability,
    SeedVarietyAvailability
)


def test_legacy_pest_resistance_compatibility():
    """Test that legacy dictionary format still works with the enhanced model."""
    legacy_data = {
        "corn_borer": {"level": "high", "genes": ["Bt1", "Bt2"]},
        "aphids": {"level": "moderate", "rating": "good"}
    }

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        pest_resistance_traits=legacy_data
    )

    # Test pest resistance methods on legacy data
    assert attrs.get_pest_resistance_level("corn borer") == "high"
    assert attrs.get_pest_resistance_level("aphids") == "good"
    assert attrs.resists_pest_at_least("corn borer", "moderate") is True


def test_enhanced_pest_resistance_data():
    """Test the new enhanced pest resistance data structure."""
    pest_profile = PestResistanceProfile(
        pest_name="corn borer",
        pest_type=PestType.INSECT,
        resistance_level=PestResistanceLevel.HIGH,
        resistance_genes=["Bt1", "Bt2"],
        effectiveness=PestResistanceEffectiveness.EXCELLENT,
        research_status="Field tested",
        notes="Excellent resistance in field trials"
    )

    enhanced_data = EnhancedPestResistanceData(
        pest_profiles={"corn_borer": pest_profile},
        overall_resistance_score=0.9,
        resistance_strengths=["insect resistance", "high durability"],
        resistance_weaknesses=["limited spectrum"]
    )

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        pest_resistance_traits=enhanced_data
    )

    # Test methods on enhanced data
    assert attrs.get_pest_resistance_level("corn borer") == "high"
    assert attrs.get_enhanced_pest_overall_score() == 0.9
    assert attrs.get_enhanced_pest_profiles() is not None
    assert len(attrs.get_enhanced_pest_profiles()) == 1


def test_legacy_market_class_compatibility():
    """Test that legacy market class dictionary format still works."""
    legacy_data = {
        "organic": True,
        "non_gmo": True,
        "heirloom": False
    }

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        market_class_filters=legacy_data
    )

    assert attrs.supports_market_class("organic") is True
    assert attrs.supports_market_class("non_gmo") is True
    assert attrs.supports_market_class("heirloom") is False


def test_enhanced_market_class_data():
    """Test the new enhanced market class data structure."""
    market_profile = MarketClassProfile(
        market_class=MarketClassType.ORGANIC,
        certification_details="USDA Certified Organic",
        market_premium={MarketPremiumType.PRICE_PREMIUM: 1.2},
        target_audience="Health-conscious consumers",
        availability_restrictions=["no synthetic pesticides"],
        special_handling_requirements=["separate storage", "organic certification"]
    )

    enhanced_data = EnhancedMarketClassData(
        market_profiles={"organic": market_profile},
        specialty_markets=["organic", "health food"],
        premium_opportunities=["price premium", "market loyalty"],
        certification_pathways=["USDA organic", "Non-GMO Project"]
    )

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        market_class_filters=enhanced_data
    )

    assert attrs.supports_market_class("organic") is True
    assert attrs.get_enhanced_market_profiles() is not None
    assert len(attrs.get_enhanced_market_profiles()) == 1
    assert "organic" in attrs.get_enhanced_market_specialty_markets()


def test_legacy_certification_compatibility():
    """Test that legacy certification dictionary format still works."""
    legacy_data = {
        "usda_organic": {"status": "certified", "expires": "2025-12-31"},
        "non_gmo_project": True
    }

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        certification_filters=legacy_data
    )

    assert attrs.has_certification("usda organic") is True
    assert attrs.has_certification("non_gmo_project") is True


def test_enhanced_certification_data():
    """Test the new enhanced certification data structure."""
    cert_profile = CertificationProfile(
        certification_type=CertificationType.USDA_ORGANIC,
        certification_number="ORG-12345",
        expiration_date=date(2025, 12, 31),
        issuing_body="USDA",
        compliance_status=ComplianceStatus.CERTIFIED,
        audit_schedule={"annual": True, "inspections": 2},
        notes="Certified since 2020"
    )

    enhanced_data = EnhancedCertificationData(
        certification_profiles={"usda_organic": cert_profile},
        compliance_status_summary={ComplianceStatus.CERTIFIED: 1},
        upcoming_renewals=[date(2025, 12, 31)],
        audit_schedule={"annual": True}
    )

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        certification_filters=enhanced_data
    )

    assert attrs.has_certification("usda organic") is True
    assert attrs.get_enhanced_certification_profiles() is not None
    assert len(attrs.get_enhanced_certification_profiles()) == 1
    assert attrs.get_enhanced_certification_status_summary() is not None


def test_legacy_seed_availability_compatibility():
    """Test that legacy seed availability dictionary format still works."""
    legacy_data = {
        "status": "available",
        "regions": ["midwest", "great plains"],
        "suppliers": ["company_a", "company_b"]
    }

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        seed_availability_filters=legacy_data
    )

    assert attrs.is_seed_available() is True
    assert attrs.is_seed_available(region="midwest") is True
    assert attrs.is_seed_available(supplier="company_a") is True


def test_enhanced_seed_availability_data():
    """Test the new enhanced seed availability data structure."""
    supplier_info = SupplierInfo(
        supplier_name="AgriSeed Co",
        contact_info={"phone": "555-1234", "email": "info@agriseed.com"},
        product_line="Organic varieties",
        minimum_order_quantity=10,
        availability_status=AvailabilityStatus.AVAILABLE,
        lead_time_days=5,
        shipping_options=["overnight", "ground"]
    )

    region_info = RegionalAvailability(
        region="midwest",
        availability_status=AvailabilityStatus.AVAILABLE,
        local_varieties=["var1", "var2"],
        regional_restrictions=[],
        shipping_restrictions=[]
    )

    variety_info = SeedVarietyAvailability(
        variety_name="Premium Corn VT123",
        availability_status=AvailabilityStatus.AVAILABLE,
        source_type=SeedSource.COMMERCIAL,
        treatment=SeedTreatment.FUNGICIDAL,
        germination_rate=0.95,
        purity_percentage=99.5,
        regional_availability=[region_info],
        suppliers=[supplier_info]
    )

    enhanced_data = EnhancedSeedAvailabilityData(
        seed_varieties={"vt123": variety_info},
        overall_availability_score=0.85,
        regional_supply_distributions={"midwest": 0.6, "south": 0.4},
        supplier_diversity_score=0.7
    )

    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        seed_availability_filters=enhanced_data
    )

    assert attrs.is_seed_available() is True
    assert attrs.is_seed_available(region="midwest") is True
    assert attrs.is_seed_available(supplier="AgriSeed") is True
    assert attrs.get_enhanced_seed_varieties() is not None
    assert len(attrs.get_enhanced_seed_varieties()) == 1
    assert attrs.get_enhanced_seed_overall_availability_score() == 0.85


def test_mixed_legacy_and_enhanced_compatibility():
    """Test that the model supports mixed use of legacy and enhanced formats."""
    # Use legacy for one field, enhanced for another
    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        pest_resistance_traits={  # Legacy format
            "aphids": {"level": "high"}
        },
        market_class_filters=EnhancedMarketClassData(  # Enhanced format
            market_profiles={
                "organic": MarketClassProfile(
                    market_class=MarketClassType.ORGANIC,
                    certification_details="USDA Certified"
                )
            }
        )
    )

    # Both should work
    assert attrs.get_pest_resistance_level("aphids") == "high"
    assert attrs.supports_market_class("organic") is True
    assert attrs.get_enhanced_market_profiles() is not None


def test_backward_compatibility():
    """Test that the enhanced model maintains full backward compatibility."""
    # This should work exactly as before with all legacy fields
    attrs = CropFilteringAttributes(
        crop_id=uuid4(),
        management_complexity=ManagementComplexity.MODERATE,
        input_requirements=InputRequirements.MODERATE,
        labor_requirements=LaborRequirements.LOW,
        carbon_sequestration_potential=CarbonSequestrationPotential.HIGH,
        biodiversity_support=BiodiversitySupport.MODERATE,
        pollinator_value=PollinatorValue.HIGH,
        water_use_efficiency=WaterUseEfficiency.EXCELLENT,
        market_stability=MarketStability.STABLE,
        pest_resistance_traits={"aphids": {"level": "high"}},
        market_class_filters={"organic": True},
        certification_filters={"usda_organic": True},
        seed_availability_filters={"status": "available"}
    )

    # Test that all legacy fields are still properly accessible
    assert attrs.management_complexity == ManagementComplexity.MODERATE
    assert attrs.input_requirements == InputRequirements.MODERATE
    assert attrs.labor_requirements == LaborRequirements.LOW
    assert attrs.get_pest_resistance_level("aphids") == "high"
    assert attrs.supports_market_class("organic") is True
    assert attrs.has_certification("usda organic") is True
    assert attrs.is_seed_available() is True


if __name__ == "__main__":
    # Run the tests
    test_legacy_pest_resistance_compatibility()
    test_enhanced_pest_resistance_data()
    test_legacy_market_class_compatibility()
    test_enhanced_market_class_data()
    test_legacy_certification_compatibility()
    test_enhanced_certification_data()
    test_legacy_seed_availability_compatibility()
    test_enhanced_seed_availability_data()
    test_mixed_legacy_and_enhanced_compatibility()
    test_backward_compatibility()
    
    print("All tests passed!")