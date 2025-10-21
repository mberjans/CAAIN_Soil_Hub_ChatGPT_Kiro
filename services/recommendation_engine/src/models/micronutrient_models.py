
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date
from enum import Enum

class MicronutrientType(str, Enum):
    BORON = "Boron"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    ZINC = "Zinc"
    MOLYBDENUM = "Molybdenum"
    CHLORINE = "Chlorine"
    NICKEL = "Nickel"

class SoilTestResult(BaseModel):
    micronutrient_type: MicronutrientType
    level_ppm: float = Field(..., gt=0, description="Micronutrient level in parts per million")
    sufficiency_range_min_ppm: float = Field(..., gt=0)
    sufficiency_range_max_ppm: float = Field(..., gt=0)

    @validator('sufficiency_range_max_ppm')
    def check_sufficiency_range(cls, v, values):
        if 'sufficiency_range_min_ppm' in values and v < values['sufficiency_range_min_ppm']:
            raise ValueError('sufficiency_range_max_ppm must be greater than or equal to sufficiency_range_min_ppm')
        return v

class MicronutrientApplication(BaseModel):
    micronutrient_type: MicronutrientType
    application_rate_kg_ha: float = Field(..., gt=0, description="Application rate in kilograms per hectare")
    cost_per_kg: float = Field(..., gt=0, description="Cost per kilogram of micronutrient")

class CropYieldData(BaseModel):
    crop_type: str = Field(..., min_length=1)
    expected_yield_baseline_kg_ha: float = Field(..., gt=0, description="Baseline yield without specific micronutrient intervention")
    unit_price_per_kg: float = Field(..., gt=0, description="Market price per kilogram of crop yield")

class MicronutrientYieldResponse(BaseModel):
    micronutrient_type: MicronutrientType
    predicted_yield_increase_kg_ha: float = Field(..., ge=0, description="Predicted yield increase due to micronutrient application")
    predicted_total_yield_kg_ha: float = Field(..., gt=0, description="Predicted total yield after application")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the yield prediction (0-1)")

class EconomicReturnPrediction(BaseModel):
    micronutrient_type: MicronutrientType
    total_application_cost: float = Field(..., ge=0, description="Total cost of micronutrient application")
    additional_revenue_from_yield_increase: float = Field(..., ge=0, description="Revenue generated from predicted yield increase")
    net_economic_return: float = Field(..., description="Net profit/loss from micronutrient application")
    roi_percentage: float = Field(..., description="Return on Investment as a percentage")
    currency: str = Field("CAD", min_length=1, max_length=3)

class YieldEconomicPredictionRequest(BaseModel):
    farm_id: str
    field_id: str
    crop_yield_data: CropYieldData
    soil_test_results: List[SoilTestResult]
    micronutrient_applications: List[MicronutrientApplication]
    application_date: date
    area_ha: float = Field(..., gt=0, description="Area of the field in hectares")

class YieldEconomicPredictionResponse(BaseModel):
    request_id: str
    micronutrient_yield_responses: List[MicronutrientYieldResponse]
    economic_return_predictions: List[EconomicReturnPrediction]
    overall_status: str
    message: Optional[str] = None
