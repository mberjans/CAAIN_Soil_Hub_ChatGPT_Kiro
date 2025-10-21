from pydantic import BaseModel, Field, UUID4, validator
from typing import Optional, Dict, Any
from datetime import date, datetime

class NutrientValue(BaseModel):
    value: Optional[float] = Field(None, description="Measured value of the nutrient/property")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., ppm, %)")
    optimal_min: Optional[float] = Field(None, description="Optimal minimum value")
    optimal_max: Optional[float] = Field(None, description="Optimal maximum value")
    deficiency_threshold: Optional[float] = Field(None, description="Threshold below which it's considered deficient")
    toxicity_threshold: Optional[float] = Field(None, description="Threshold above which it's considered toxic")
    notes: Optional[str] = Field(None, description="Any specific notes for this nutrient/property")

class MacroNutrients(BaseModel):
    nitrogen_total_n: Optional[NutrientValue] = Field(None, description="Total Nitrogen (N)")
    phosphorus_p: Optional[NutrientValue] = Field(None, description="Phosphorus (P)")
    potassium_k: Optional[NutrientValue] = Field(None, description="Potassium (K)")
    sulfur_s: Optional[NutrientValue] = Field(None, description="Sulfur (S)")
    calcium_ca: Optional[NutrientValue] = Field(None, description="Calcium (Ca)")
    magnesium_mg: Optional[NutrientValue] = Field(None, description="Magnesium (Mg)")

class MicroNutrients(BaseModel):
    boron_b: Optional[NutrientValue] = Field(None, description="Boron (B)")
    copper_cu: Optional[NutrientValue] = Field(None, description="Copper (Cu)")
    iron_fe: Optional[NutrientValue] = Field(None, description="Iron (Fe)")
    manganese_mn: Optional[NutrientValue] = Field(None, description="Manganese (Mn)")
    zinc_zn: Optional[NutrientValue] = Field(None, description="Zinc (Zn)")
    molybdenum_mo: Optional[NutrientValue] = Field(None, description="Molybdenum (Mo)")
    chlorine_cl: Optional[NutrientValue] = Field(None, description="Chlorine (Cl)")
    sodium_na: Optional[NutrientValue] = Field(None, description="Sodium (Na)") # Added Sodium
    silicon_si: Optional[NutrientValue] = Field(None, description="Silicon (Si)") # Added Silicon

class OtherSoilProperties(BaseModel):
    ph: Optional[NutrientValue] = Field(None, description="Soil pH")
    organic_matter_percent: Optional[NutrientValue] = Field(None, description="Organic Matter percentage")
    cation_exchange_capacity_cec: Optional[NutrientValue] = Field(None, description="Cation Exchange Capacity (CEC)")
    electrical_conductivity_ec: Optional[NutrientValue] = Field(None, description="Electrical Conductivity (EC)")
    soil_texture: Optional[str] = Field(None, description="Soil texture (e.g., 'loam', 'clay', 'sand')")
    buffer_ph: Optional[NutrientValue] = Field(None, description="Buffer pH") # Added Buffer pH
    base_saturation_calcium: Optional[NutrientValue] = Field(None, description="Base Saturation Calcium (%)") # Added Base Saturation Calcium
    base_saturation_magnesium: Optional[NutrientValue] = Field(None, description="Base Saturation Magnesium (%)") # Added Base Saturation Magnesium
    base_saturation_potassium: Optional[NutrientValue] = Field(None, description="Base Saturation Potassium (%)") # Added Base Saturation Potassium
    base_saturation_sodium: Optional[NutrientValue] = Field(None, description="Base Saturation Sodium (%)") # Added Base Saturation Sodium

class SoilNutrientAnalysisBase(BaseModel):
    farm_id: UUID4 = Field(..., description="ID of the farm where the soil sample was taken")
    field_id: UUID4 = Field(..., description="ID of the field where the soil sample was taken")
    analysis_date: date = Field(..., description="Date when the soil analysis was performed")
    lab_name: Optional[str] = Field(None, description="Name of the laboratory that performed the analysis")
    sample_id: Optional[str] = Field(None, description="Unique identifier for the soil sample from the lab")
    
    macro_nutrients: Optional[MacroNutrients] = Field(None, description="Macronutrient levels")
    micro_nutrients: Optional[MicroNutrients] = Field(None, description="Micronutrient levels")
    other_properties: Optional[OtherSoilProperties] = Field(None, description="Other soil properties like pH, OM, CEC")

    notes: Optional[str] = Field(None, description="Any additional notes about the analysis")

    @validator('analysis_date')
    def validate_analysis_date(cls, v):
        if v > date.today():
            raise ValueError('Analysis date cannot be in the future')
        return v

class SoilNutrientAnalysisCreate(SoilNutrientAnalysisBase):
    pass

class SoilNutrientAnalysisResponse(SoilNutrientAnalysisBase):
    id: UUID4 = Field(..., description="Unique ID of the soil nutrient analysis record")
    created_at: datetime = Field(..., description="Timestamp when the record was created")
    updated_at: datetime = Field(..., description="Timestamp when the record was last updated")

    class Config:
        from_attributes = True
