"""
Test file for crop schemas
"""
import pytest
from pydantic import ValidationError
from typing import Dict, Any


def test_crop_schema_imports():
    """Test that we can import schema classes"""
    from src.schemas.crop_schemas import (
        CropFilterRequest, 
        CropSearchResponse, 
        PestResistanceFilter, 
        DiseaseResistanceFilter, 
        MarketClassFilter,
        VarietyResult,
        PreferenceUpdate,
        PreferenceResponse
    )
    assert CropFilterRequest is not None
    assert CropSearchResponse is not None
    assert PestResistanceFilter is not None
    assert DiseaseResistanceFilter is not None
    assert MarketClassFilter is not None
    assert VarietyResult is not None
    assert PreferenceUpdate is not None
    assert PreferenceResponse is not None

    
def test_crop_filter_request_valid():
    """Test CropFilterRequest schema with valid data"""
    from src.schemas.crop_schemas import CropFilterRequest, PestResistanceFilter, DiseaseResistanceFilter, MarketClassFilter
    
    # Test with minimal valid data
    request = CropFilterRequest(crop_type="corn")
    assert request.crop_type == "corn"
    assert request.page == 1
    assert request.page_size == 20
    
    # Test with more complete data
    request = CropFilterRequest(
        crop_type="soybean",
        maturity_days_min=90,
        maturity_days_max=120,
        pest_resistance=[PestResistanceFilter(pest_name="aphids", min_resistance_level="moderate")],
        disease_resistance=[DiseaseResistanceFilter(disease_name="rust", min_resistance_level="resistant")],
        market_class=MarketClassFilter(organic_certified=True),
        min_yield_stability=80,
        page=1,
        page_size=10
    )
    
    assert request.crop_type == "soybean"
    assert request.maturity_days_min == 90
    assert request.maturity_days_max == 120
    assert len(request.pest_resistance) == 1
    assert request.pest_resistance[0].pest_name == "aphids"
    assert request.min_yield_stability == 80
    assert request.page_size == 10


def test_crop_filter_request_invalid_crop_type():
    """Test CropFilterRequest schema validation errors"""
    from src.schemas.crop_schemas import CropFilterRequest
    from pydantic import ValidationError
    
    # Test invalid crop type
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="invalid_crop")
    
    assert "crop_type must be one of" in str(exc_info.value)
    
    # Test invalid maturity day values (out of range)
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="corn", maturity_days_min=-10)
    
    assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="corn", maturity_days_max=300)
    
    assert "Input should be less than or equal to 200" in str(exc_info.value)
    
    # Test invalid page size (out of range)
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="corn", page_size=0)
    
    assert "Input should be greater than or equal to 1" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="corn", page_size=150)
    
    assert "Input should be less than or equal to 100" in str(exc_info.value)
    
    # Test invalid yield stability values
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="corn", min_yield_stability=-10)
    
    assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        CropFilterRequest(crop_type="corn", min_yield_stability=150)
    
    assert "Input should be less than or equal to 100" in str(exc_info.value)


def test_crop_search_response():
    """Test CropSearchResponse schema"""
    from src.schemas.crop_schemas import CropSearchResponse, VarietyResult
    from uuid import uuid4
    
    # Test with valid data
    variety = VarietyResult(
        variety_id=uuid4(),
        variety_name="Test Variety",
        maturity_days=100,
        yield_potential=180.0,
        pest_resistance_summary={"corn_borer": "resistant"},
        disease_resistance_summary={"rust": "moderate"},
        market_class="yellow_dent",
        relevance_score=0.85
    )
    
    response = CropSearchResponse(
        varieties=[variety],
        total_count=1,
        page=1,
        page_size=20,
        total_pages=1,
        filters_applied={"crop_type": "corn"},
        search_time_ms=150
    )
    
    assert len(response.varieties) == 1
    assert response.total_count == 1
    assert response.page == 1
    assert response.page_size == 20
    assert response.total_pages == 1
    assert response.filters_applied == {"crop_type": "corn"}
    assert response.search_time_ms == 150


if __name__ == "__main__":
    pytest.main()