from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime


class FertilizerInfo(BaseModel):
    """Model for available fertilizer information."""
    name: str
    price_per_ton: float
    nutrients: Dict[str, float]  # e.g., {"N": 10.0, "P": 5.0, "K": 3.0}


class OptimizationRequest(BaseModel):
    """Model for fertilizer optimization request."""
    field_acres: float
    nutrient_requirements: Dict[str, float]  # e.g., {"N": 100.0, "P": 50.0, "K": 80.0}
    yield_goal_bu_acre: float
    available_fertilizers: List[FertilizerInfo]
    budget_per_acre: float
    crop_price_per_bu: float


class FertilizerRecommendation(BaseModel):
    """Model for a single fertilizer recommendation."""
    fertilizer_name: str
    application_rate: float
    cost: float
    nutrients_applied: Dict[str, float]  # e.g., {"N": 50.0, "P": 25.0, "K": 40.0}


class OptimizationResponse(BaseModel):
    """Model for fertilizer optimization response."""
    recommendations: List[FertilizerRecommendation]
    total_cost: float
    expected_yield: float
    roi: float


class PriceData(BaseModel):
    """Model for fertilizer price data."""
    fertilizer_name: str
    price: float
    source: str
    date: datetime