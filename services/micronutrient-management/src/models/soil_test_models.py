from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import date

from .micronutrient_models import MicronutrientName

class SoilTestMicronutrientResult(BaseModel):
    micronutrient: MicronutrientName = Field(..., description="Name of the micronutrient")
    concentration_ppm: float = Field(..., description="Concentration of the micronutrient in ppm")
    unit: str = Field("ppm", description="Unit of concentration")
    method: Optional[str] = Field(None, description="Extraction method used for the test")

class SoilTestResult(BaseModel):
    test_id: str = Field(..., description="Unique identifier for the soil test")
    farm_id: str = Field(..., description="ID of the farm where the test was conducted")
    field_id: str = Field(..., description="ID of the field where the test was conducted")
    test_date: date = Field(..., description="Date the soil test was performed")
    lab_name: Optional[str] = Field(None, description="Name of the laboratory that performed the test")
    ph: Optional[float] = Field(None, description="Soil pH value")
    organic_matter_percent: Optional[float] = Field(None, description="Organic matter percentage")
    micronutrients: Dict[MicronutrientName, SoilTestMicronutrientResult] = Field(default_factory=dict, description="Micronutrient test results")
    notes: Optional[str] = Field(None, description="Additional notes about the soil test")
