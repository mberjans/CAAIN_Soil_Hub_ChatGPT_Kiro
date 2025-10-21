"""
Test file for filtering models
This file will contain tests for CropFilteringAttributes, FarmerPreference, and FilterCombination models
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from src.models.crop_filtering_models import CropFilteringAttributes


def test_crop_filtering_attributes_creation():
    """Test that CropFilteringAttributes model can be created with valid data"""
    # Create a valid CropFilteringAttributes instance
    crop_filter = CropFilteringAttributes(
        crop_id=uuid4(),
        planting_season=["spring", "early_spring"],
        growing_season=["summer"],
        harvest_season=["fall"],
        farming_systems=["organic"],
        rotation_compatibility=["corn", "soybean"],
        intercropping_compatible=True,
        cover_crop_compatible=True,
        management_complexity="moderate",
        input_requirements="moderate",
        labor_requirements="low",
        precision_ag_compatible=True,
        gps_guidance_recommended=False,
        sensor_monitoring_beneficial=True,
        carbon_sequestration_potential="moderate",
        biodiversity_support="high",
        pollinator_value="high",
        water_use_efficiency="good",
        market_stability="stable",
        price_premium_potential=True,
        value_added_opportunities=["food", "feed"],
        pest_resistance_traits={"corn_borer": "resistant", "aphids": "susceptible"},
        market_class_filters={"organic": True, "non_gmo": True},
        certification_filters={"usda_organic": True, "non_gmo_project": False},
        seed_availability_filters={"supplier_a": True, "supplier_b": False},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Verify all attributes are set correctly
    assert crop_filter.crop_id is not None
    assert isinstance(crop_filter.crop_id, UUID)
    assert crop_filter.planting_season == ["spring", "early_spring"]
    assert crop_filter.growing_season == ["summer"]
    assert crop_filter.harvest_season == ["fall"]
    assert crop_filter.farming_systems == ["organic"]
    assert crop_filter.rotation_compatibility == ["corn", "soybean"]
    assert crop_filter.intercropping_compatible is True
    assert crop_filter.cover_crop_compatible is True
    assert crop_filter.management_complexity == "moderate"
    assert crop_filter.input_requirements == "moderate"
    assert crop_filter.labor_requirements == "low"
    assert crop_filter.precision_ag_compatible is True
    assert crop_filter.gps_guidance_recommended is False
    assert crop_filter.sensor_monitoring_beneficial is True
    assert crop_filter.carbon_sequestration_potential == "moderate"
    assert crop_filter.biodiversity_support == "high"
    assert crop_filter.pollinator_value == "high"
    assert crop_filter.water_use_efficiency == "good"
    assert crop_filter.market_stability == "stable"
    assert crop_filter.price_premium_potential is True
    assert crop_filter.value_added_opportunities == ["food", "feed"]
    assert crop_filter.pest_resistance_traits == {"corn_borer": "resistant", "aphids": "susceptible"}
    assert crop_filter.market_class_filters == {"organic": True, "non_gmo": True}
    assert crop_filter.certification_filters == {"usda_organic": True, "non_gmo_project": False}
    assert crop_filter.seed_availability_filters == {"supplier_a": True, "supplier_b": False}
    assert crop_filter.created_at is not None
    assert crop_filter.updated_at is not None


def test_crop_filtering_attributes_default_values():
    """Test that CropFilteringAttributes model has proper default values"""
    crop_filter = CropFilteringAttributes(
        crop_id=uuid4()
    )
    
    # Check default values
    assert crop_filter.planting_season == ["spring"]
    assert crop_filter.growing_season == ["summer"]
    assert crop_filter.harvest_season == ["fall"]
    assert crop_filter.farming_systems == ["conventional"]
    assert crop_filter.rotation_compatibility == []
    assert crop_filter.intercropping_compatible is False
    assert crop_filter.cover_crop_compatible is True
    assert crop_filter.management_complexity is None
    assert crop_filter.input_requirements is None
    assert crop_filter.labor_requirements is None
    assert crop_filter.precision_ag_compatible is True
    assert crop_filter.gps_guidance_recommended is False
    assert crop_filter.sensor_monitoring_beneficial is False
    assert crop_filter.carbon_sequestration_potential is None
    assert crop_filter.biodiversity_support is None
    assert crop_filter.pollinator_value is None
    assert crop_filter.water_use_efficiency is None
    assert crop_filter.market_stability is None
    assert crop_filter.price_premium_potential is False
    assert crop_filter.value_added_opportunities == []
    assert crop_filter.pest_resistance_traits == {}
    assert crop_filter.market_class_filters == {}
    assert crop_filter.certification_filters == {}
    assert crop_filter.seed_availability_filters == {}


def test_crop_filtering_attributes_optional_fields():
    """Test that optional fields in CropFilteringAttributes work correctly"""
    crop_filter = CropFilteringAttributes(
        crop_id=uuid4(),
        filter_id=uuid4(),
        created_at=None,
        updated_at=None
    )
    
    # Verify optional fields can be None
    assert crop_filter.filter_id is not None  # Since we passed a value
    assert crop_filter.created_at is None  # Since we passed None
    assert crop_filter.updated_at is None  # Since we passed None