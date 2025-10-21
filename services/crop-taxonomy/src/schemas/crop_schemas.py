from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class PestResistanceFilter(BaseModel):
    """Pest resistance filtering criteria"""
    pest_name: str = Field(..., description="Name of pest (e.g., 'corn_borer')")
    min_resistance_level: str = Field("moderate", description="Minimum resistance: susceptible, moderate, resistant")


class DiseaseResistanceFilter(BaseModel):
    """Disease resistance filtering criteria"""
    disease_name: str = Field(..., description="Name of disease")
    min_resistance_level: str = Field("moderate", description="Minimum resistance level")


class MarketClassFilter(BaseModel):
    """Market class filtering criteria"""
    market_class: Optional[str] = Field(None, description="Market class (e.g., 'yellow_dent', 'white_corn')")
    organic_certified: Optional[bool] = Field(None, description="Organic certification required")
    non_gmo: Optional[bool] = Field(None, description="Non-GMO required")


class CropFilterRequest(BaseModel):
    """Request for filtered crop search"""
    crop_type: str = Field(..., description="Crop type (corn, soybean, wheat)")

    # Basic filters
    maturity_days_min: Optional[int] = Field(None, ge=0, le=200)
    maturity_days_max: Optional[int] = Field(None, ge=0, le=200)

    # Advanced filters
    pest_resistance: Optional[List[PestResistanceFilter]] = Field(None)
    disease_resistance: Optional[List[DiseaseResistanceFilter]] = Field(None)
    market_class: Optional[MarketClassFilter] = Field(None)

    # Performance filters
    min_yield_stability: Optional[int] = Field(None, ge=0, le=100)
    min_drought_tolerance: Optional[int] = Field(None, ge=0, le=100)

    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    # Sorting
    sort_by: Optional[str] = Field("relevance", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="asc or desc")

    @field_validator('crop_type')
    @classmethod
    def validate_crop_type(cls, v):
        allowed = ['corn', 'soybean', 'wheat', 'cotton', 'rice']
        if v.lower() not in allowed:
            raise ValueError(f'crop_type must be one of {allowed}')
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "crop_type": "corn",
                "maturity_days_min": 90,
                "maturity_days_max": 120,
                "pest_resistance": [
                    {"pest_name": "corn_borer", "min_resistance_level": "resistant"}
                ],
                "min_yield_stability": 80,
                "page": 1,
                "page_size": 20
            }
        }


class VarietyResult(BaseModel):
    """Single variety in search results"""
    variety_id: UUID
    variety_name: str
    maturity_days: int
    yield_potential: Optional[float]
    pest_resistance_summary: Dict[str, str]
    disease_resistance_summary: Dict[str, str]
    market_class: Optional[str]
    relevance_score: float = Field(..., ge=0, le=1)


class CropSearchResponse(BaseModel):
    """Response for crop search"""
    varieties: List[VarietyResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: Dict[str, Any]
    search_time_ms: int


class PreferenceUpdate(BaseModel):
    """Update farmer preferences"""
    user_id: UUID
    preferred_filters: Dict[str, Any]
    filter_weights: Optional[Dict[str, float]] = Field(None)


class PreferenceResponse(BaseModel):
    """Response for preference operations"""
    user_id: UUID
    preferences_saved: bool
    message: str