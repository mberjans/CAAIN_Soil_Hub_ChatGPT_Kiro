from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

class FarmContext(BaseModel):
    location: Dict[str, float]
    soil_data: Dict[str, Any]
    climate_zone: str
    field_size_acres: int
    irrigation_available: bool

class FarmerPreferences(BaseModel):
    risk_tolerance: str
    management_intensity: str
    organic_focus: bool
    yield_priority: float
    sustainability_priority: float

class Constraints(BaseModel):
    max_seed_cost_per_acre: int
    required_traits: List[str]
    excluded_traits: List[str]

class AdvancedVarietyRecommendationRequest(BaseModel):
    crop_id: UUID
    farm_context: FarmContext
    farmer_preferences: FarmerPreferences
    constraints: Constraints
    recommendation_count: int = 10
