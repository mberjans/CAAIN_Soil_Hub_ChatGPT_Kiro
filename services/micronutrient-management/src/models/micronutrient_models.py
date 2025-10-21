from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Micronutrient(BaseModel):
    """Represents a single micronutrient."""
    name: str = Field(..., description="Name of the micronutrient (e.g., 'Boron', 'Zinc')")
    symbol: str = Field(..., description="Chemical symbol of the micronutrient (e.g., 'B', 'Zn')")
    unit: str = Field("kg/ha", description="Standard unit for application rate (e.g., 'kg/ha', 'lb/acre')")

class MicronutrientPrice(BaseModel):
    """Represents the price of a micronutrient product."""
    micronutrient_name: str = Field(..., description="Name of the micronutrient product")
    price_per_unit: float = Field(..., gt=0, description="Price per unit of the product")
    unit: str = Field(..., description="Unit of the product (e.g., 'kg', 'liter', 'bag')")
    currency: str = Field("USD", description="Currency of the price")
    source: Optional[str] = Field(None, description="Source of the price data")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last price update")

class ApplicationCost(BaseModel):
    """Represents costs associated with applying micronutrients."""
    description: str = Field(..., description="Description of the cost (e.g., 'Labor', 'Equipment Rental', 'Fuel')")
    cost_per_unit: float = Field(..., gt=0, description="Cost per unit (e.g., per hectare, per hour)")
    unit: str = Field(..., description="Unit of cost (e.g., 'ha', 'hour')")
    quantity: float = Field(..., gt=0, description="Quantity of units (e.g., 10 ha, 5 hours)")
    total_cost: float = Field(..., gt=0, description="Total cost for this item")

class MicronutrientBudgetAnalysisResult(BaseModel):
    """Represents the comprehensive budget and cost analysis for micronutrients."""
    farm_id: str = Field(..., description="ID of the farm for which the analysis is performed")
    field_id: str = Field(..., description="ID of the field for which the analysis is performed")
    micronutrient_recommendations: List[dict] = Field(..., description="List of recommended micronutrients and their rates")
    micronutrient_product_costs: List[MicronutrientPrice] = Field(..., description="Costs of micronutrient products")
    application_costs: List[ApplicationCost] = Field(..., description="Costs associated with application")
    total_micronutrient_cost: float = Field(..., ge=0, description="Total cost of all micronutrient products")
    total_application_cost: float = Field(..., ge=0, description="Total cost of all application-related expenses")
    overall_total_cost: float = Field(..., ge=0, description="Overall total cost (products + application)")
    cost_per_hectare: float = Field(..., ge=0, description="Total cost per hectare")
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Date of the analysis")
    notes: Optional[str] = Field(None, description="Any additional notes or considerations")
