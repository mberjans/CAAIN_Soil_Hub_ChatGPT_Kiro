from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID

class FarmContext(BaseModel):
    """
    Contextual information about the farm for predictions.
    """
    farm_location_id: UUID = Field(..., description="Unique identifier for the farm location.")
    soil_ph: float = Field(..., ge=0.0, le=14.0, description="Current soil pH.")
    soil_organic_matter_percent: float = Field(..., ge=0.0, le=100.0, description="Soil organic matter percentage.")
    soil_type: str = Field(..., description="Soil type (e.g., 'loam', 'clay', 'sandy').")
    climate_zone: str = Field(..., description="Climate zone of the farm (e.g., '5a', 'humid subtropical').")
    historical_yield_data: Optional[List[float]] = Field(None, description="List of historical yields for the crop in similar conditions.")
    historical_micronutrient_application: Optional[List[dict]] = Field(None, description="Historical micronutrient application data.")

class MicronutrientApplication(BaseModel):
    """
    Details of the micronutrient application.
    """
    micronutrient_type: str = Field(..., description="Type of micronutrient (e.g., 'Zinc', 'Boron', 'Manganese').")
    application_rate_per_acre: float = Field(..., gt=0.0, description="Rate of application per acre.")
    application_unit: str = Field(..., description="Unit of application rate (e.g., 'lbs', 'kg', 'oz').")
    cost_per_unit: float = Field(..., gt=0.0, description="Cost per unit of the micronutrient.")
    total_acres_applied: float = Field(..., gt=0.0, description="Total acres to which the micronutrient is applied.")
    application_method: str = Field(..., description="Method of application (e.g., 'foliar', 'soil_broadcast', 'fertigation').")
    application_date: date = Field(..., description="Date of application.")

class CropDetails(BaseModel):
    """
    Crop-specific information relevant for predictions.
    """
    crop_type: str = Field(..., description="Type of crop (e.g., 'corn', 'soybean', 'wheat').")
    variety: str = Field(..., description="Specific variety of the crop.")
    planting_date: date = Field(..., description="Date when the crop was planted.")
    expected_market_price_per_unit: float = Field(..., gt=0.0, description="Expected market price per unit of yield (e.g., per bushel, per ton).")
    yield_unit: str = Field(..., description="Unit of yield (e.g., 'bushels', 'tons', 'kg').")
    micronutrient_deficiency_level: Optional[str] = Field(None, description="Current micronutrient deficiency level (e.g., 'low', 'medium', 'high').")
    growth_stage_at_application: Optional[str] = Field(None, description="Growth stage of the crop at the time of micronutrient application.")

class YieldPredictionRequest(BaseModel):
    """
    Request model for predicting yield response to micronutrient application.
    """
    farm_context: FarmContext
    crop_details: CropDetails
    micronutrient_application: MicronutrientApplication

class YieldPredictionResponse(BaseModel):
    """
    Response model for yield prediction.
    """
    predicted_yield_per_acre: float = Field(..., gt=0.0, description="Predicted yield per acre after micronutrient application.")
    predicted_total_yield: float = Field(..., gt=0.0, description="Predicted total yield for the applied area.")
    baseline_yield_per_acre: float = Field(..., gt=0.0, description="Baseline yield per acre without micronutrient application.")
    yield_increase_percent: float = Field(..., description="Percentage increase in yield due to micronutrient application.")
    confidence_score: float = Field(..., ge=00.0, le=1.0, description="Confidence score of the yield prediction.")
    explanation: str = Field(..., description="Explanation of the yield prediction.")

class EconomicReturnPredictionRequest(BaseModel):
    """
    Request model for predicting economic return and ROI of micronutrient application.
    """
    farm_context: FarmContext
    crop_details: CropDetails
    micronutrient_application: MicronutrientApplication
    predicted_yield_response: YieldPredictionResponse # Includes predicted yield and yield increase

class EconomicReturnPredictionResponse(BaseModel):
    """
    Response model for economic return prediction.
    """
    total_micronutrient_cost: float = Field(..., description="Total cost of micronutrient application.")
    additional_revenue_from_yield_increase: float = Field(..., description="Additional revenue generated from the predicted yield increase.")
    net_economic_return: float = Field(..., description="Net economic return (additional revenue - total cost).")
    roi_percentage: float = Field(..., description="Return on Investment (ROI) percentage.")
    break_even_yield_increase_per_acre: float = Field(..., description="Yield increase per acre required to break even on micronutrient cost.")
    explanation: str = Field(..., description="Explanation of the economic return prediction.")