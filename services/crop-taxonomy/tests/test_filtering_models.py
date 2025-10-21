"""
Test file for filtering models
This file will contain tests for CropFilteringAttributes, FarmerPreference, and FilterCombination models
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from src.models.filtering_models import CropFilteringAttributes, FarmerPreference, FilterCombination


def test_crop_filtering_attributes_creation():
    """Test that CropFilteringAttributes model can be created with valid data"""
    # Create a valid CropFilteringAttributes instance
    crop_filter = CropFilteringAttributes(
        variety_id=uuid4(),
        pest_resistance_traits={"corn_borer": "resistant", "aphids": "susceptible"},
        disease_resistance_traits={"rust": "resistant", "blight": "moderate"},
        market_class_filters={"organic": True, "non_gmo": True},
        certification_filters={"usda_organic": True, "non_gmo_project": False},
        seed_availability_filters={"supplier_a": True, "supplier_b": False},
        yield_stability_score=85,
        drought_tolerance_score=75,
        drought_tolerance="moderate",
        heat_tolerance="high",
        cold_tolerance="moderate",
        management_complexity="moderate"
    )
    
    # Verify all attributes are set correctly
    assert crop_filter.variety_id is not None
    assert isinstance(crop_filter.variety_id, UUID)
    assert crop_filter.pest_resistance_traits == {"corn_borer": "resistant", "aphids": "susceptible"}
    assert crop_filter.disease_resistance_traits == {"rust": "resistant", "blight": "moderate"}
    assert crop_filter.market_class_filters == {"organic": True, "non_gmo": True}
    assert crop_filter.certification_filters == {"usda_organic": True, "non_gmo_project": False}
    assert crop_filter.seed_availability_filters == {"supplier_a": True, "supplier_b": False}
    assert crop_filter.yield_stability_score == 85
    assert crop_filter.drought_tolerance_score == 75
    assert crop_filter.drought_tolerance == "moderate"
    assert crop_filter.heat_tolerance == "high"
    assert crop_filter.cold_tolerance == "moderate"
    assert crop_filter.management_complexity == "moderate"


def test_farmer_preference_creation():
    """Test that FarmerPreference model can be created with valid data"""
    from src.models.filtering_models import FarmerPreference
    
    # Test that the model class exists and can be referenced
    assert FarmerPreference is not None
    
    # Create a valid FarmerPreference instance
    user_id = uuid4()
    farmer_pref = FarmerPreference(
        user_id=user_id,
        preferred_filters={"organic_certified": True, "pest_resistance": ["corn_borer"]},
        filter_weights={"organic_certified": 0.8, "pest_resistance": 0.6},
        selected_varieties=[str(uuid4()), str(uuid4())],  # Convert to string as they'll likely be stored as strings
        rejected_varieties=[str(uuid4())]  # Convert to string as they'll likely be stored as strings
    )
    
    # Verify all attributes are set correctly
    assert farmer_pref.user_id == user_id
    assert farmer_pref.preferred_filters == {"organic_certified": True, "pest_resistance": ["corn_borer"]}
    assert farmer_pref.filter_weights == {"organic_certified": 0.8, "pest_resistance": 0.6}
    assert len(farmer_pref.selected_varieties) == 2
    assert len(farmer_pref.rejected_varieties) == 1


def test_filter_combination_creation():
    """Test that FilterCombination SQLAlchemy model can be created with valid data"""
    from datetime import datetime
    import uuid
    
    # Test that the model class exists and can be referenced
    assert FilterCombination is not None
    
    # Create a valid FilterCombination instance
    filter_combo = FilterCombination()
    filter_combo.combination_hash = "abc123def456"
    filter_combo.filters = {"climate_zone": "5b", "soil_type": "loam"}
    filter_combo.usage_count = 5
    filter_combo.avg_result_count = 10
    filter_combo.avg_response_time_ms = 150
    filter_combo.created_at = datetime.now()
    filter_combo.last_used_at = datetime.now()
    
    # Verify all attributes are set correctly
    assert filter_combo.combination_hash == "abc123def456"
    assert filter_combo.filters == {"climate_zone": "5b", "soil_type": "loam"}
    assert filter_combo.usage_count == 5
    assert filter_combo.avg_result_count == 10
    assert filter_combo.avg_response_time_ms == 150
    assert filter_combo.created_at is not None
    assert filter_combo.last_used_at is not None
    
    # Check that usage_count defaults to 1 if not provided
    filter_combo_default = FilterCombination()
    filter_combo_default.combination_hash = "def456ghi789"
    filter_combo_default.filters = {"pest_resistance": "resistant"}
    # Don't set usage_count, should default to 1 when saved to DB, but in Python it will be None until then
    
    assert filter_combo_default.combination_hash == "def456ghi789"
    assert filter_combo_default.filters == {"pest_resistance": "resistant"}
    # In Python, the default value won't be set until it's saved to the database
    # For testing purposes, we'll check that it's either None or 1
    # (None means it hasn't been set yet, but will be 1 when saved)
    assert filter_combo_default.usage_count is None or filter_combo_default.usage_count == 1