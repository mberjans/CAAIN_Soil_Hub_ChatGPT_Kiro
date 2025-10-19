"""
Program analysis models for the fertilizer timing microservice.

Defines request and response structures used by the program analysis service.
"""

from datetime import date, datetime
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class FertilizerApplicationRecord(BaseModel):
    """Historical or planned fertilizer application record."""

    application_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique application identifier")
    fertilizer_type: str = Field(..., description="Type of fertilizer applied")
    application_method: str = Field(..., description="Application method used")
    applied_date: date = Field(..., description="Date fertilizer was applied")
    amount_lbs_per_acre: float = Field(..., ge=0.0, description="Amount applied per acre")
    target_nutrient: Optional[str] = Field(None, description="Primary nutrient addressed by the application")
    crop_stage: Optional[str] = Field(None, description="Crop growth stage at application")
    weather_condition: Optional[str] = Field(None, description="Weather condition summary")
    field_condition: Optional[str] = Field(None, description="Field condition summary")
    efficiency_estimate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Estimated efficiency score (0-1)")
    notes: Optional[str] = Field(None, description="Additional notes or context")


class SoilTestResult(BaseModel):
    """Soil test snapshot for the field."""

    sample_date: date = Field(..., description="Date the soil sample was collected")
    lab_name: Optional[str] = Field(None, description="Laboratory performing the analysis")
    ph: Optional[float] = Field(None, ge=3.0, le=10.0, description="Soil pH value")
    organic_matter_percent: Optional[float] = Field(None, ge=0.0, le=20.0, description="Organic matter percentage")
    cation_exchange_capacity: Optional[float] = Field(None, ge=0.0, description="CEC value")
    nutrient_levels: Dict[str, float] = Field(default_factory=dict, description="Nutrient levels by element (ppm)")
    texture_class: Optional[str] = Field(None, description="Soil texture classification")


class YieldRecord(BaseModel):
    """Yield outcome record for the field."""

    season: str = Field(..., description="Season identifier, e.g., 2023")
    harvested_acres: float = Field(..., ge=0.0, description="Acres harvested")
    yield_per_acre: float = Field(..., ge=0.0, description="Harvested yield per acre")
    target_yield_per_acre: Optional[float] = Field(None, ge=0.0, description="Target yield per acre")
    notes: Optional[str] = Field(None, description="Context on yield performance")


class ProgramAnalysisContext(BaseModel):
    """Context for the fertilizer program analysis."""

    field_id: str = Field(..., description="Field identifier for the analysis")
    crop_name: str = Field(..., description="Crop grown on the field")
    planting_date: date = Field(..., description="Planting date for the crop")
    expected_harvest_date: Optional[date] = Field(None, description="Expected harvest date")
    fertilizer_requirements: Dict[str, float] = Field(..., description="Nutrient requirements (lbs/acre) by fertilizer type")
    soil_type: str = Field(..., description="Dominant soil type for the field")
    soil_moisture_capacity: float = Field(..., ge=0.0, le=1.0, description="Soil moisture holding capacity (0-1)")
    drainage_class: str = Field(..., description="Soil drainage class")
    slope_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Average slope percentage")
    location: Dict[str, float] = Field(..., description="Field location with keys 'lat' and 'lng'")

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: Dict[str, float]) -> Dict[str, float]:
        """Ensure location contains latitude and longitude within valid bounds."""
        if "lat" not in value or "lng" not in value:
            raise ValueError("Location must include 'lat' and 'lng' values")
        latitude = value["lat"]
        longitude = value["lng"]
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return value


class ProgramAnalysisRequest(BaseModel):
    """Program analysis request payload."""

    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique request identifier")
    context: ProgramAnalysisContext = Field(..., description="Field and crop context")
    current_program: List[FertilizerApplicationRecord] = Field(default_factory=list, description="Current fertilizer program applications")
    soil_tests: List[SoilTestResult] = Field(default_factory=list, description="Relevant soil test results")
    yield_history: List[YieldRecord] = Field(default_factory=list, description="Historical yield performance")
    operational_notes: List[str] = Field(default_factory=list, description="Operational notes impacting the program")
    environmental_incidents: List[str] = Field(default_factory=list, description="Environmental incidents (runoff, leaching, etc.)")


class ApplicationTimingDeviation(BaseModel):
    """Timing deviation summary for applications compared to recommendations."""

    application_id: str = Field(..., description="Identifier of the analyzed application")
    fertilizer_type: str = Field(..., description="Fertilizer type evaluated")
    application_method: str = Field(..., description="Application method used")
    actual_date: date = Field(..., description="Actual application date")
    recommended_date: Optional[date] = Field(None, description="Recommended application date")
    days_difference: Optional[int] = Field(None, description="Difference in days between actual and recommended dates")
    crop_stage_alignment: Optional[str] = Field(None, description="Assessment of crop stage alignment")
    risk_flag: Optional[str] = Field(None, description="Risk classification for the deviation")


class TimingAssessment(BaseModel):
    """Aggregated timing assessment metrics."""

    average_deviation_days: float = Field(..., description="Average absolute deviation in days")
    on_time_percentage: float = Field(..., ge=0.0, le=1.0, description="Fraction of applications within tolerance window")
    early_applications: int = Field(..., ge=0, description="Number of early applications")
    late_applications: int = Field(..., ge=0, description="Number of late applications")
    critical_risk_events: int = Field(..., ge=0, description="Number of deviations flagged as critical")
    deviations: List[ApplicationTimingDeviation] = Field(default_factory=list, description="Detailed deviation records")


class NutrientSynchronizationAssessment(BaseModel):
    """Nutrient synchronization assessment details."""

    nutrient_balance: Dict[str, float] = Field(default_factory=dict, description="Ratio of applied to required nutrients by type")
    soil_sufficiency_flags: Dict[str, str] = Field(default_factory=dict, description="Soil sufficiency status by nutrient")
    synchronization_score: float = Field(..., ge=0.0, le=1.0, description="Overall synchronization score (0-1)")
    observations: List[str] = Field(default_factory=list, description="Key observations for nutrient synchronization")


class LossRiskAssessment(BaseModel):
    """Assessment of nutrient loss or environmental risk."""

    runoff_risk_score: float = Field(..., ge=0.0, le=1.0, description="Runoff risk score (0-1)")
    volatilization_risk_score: float = Field(..., ge=0.0, le=1.0, description="Volatilization risk score (0-1)")
    leaching_risk_score: float = Field(..., ge=0.0, le=1.0, description="Leaching risk score (0-1)")
    incident_notes: List[str] = Field(default_factory=list, description="Relevant incident notes")


class EfficiencyAssessment(BaseModel):
    """Comprehensive efficiency evaluation."""

    yield_trend_percent: float = Field(..., description="Yield trend percentage across seasons")
    efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Overall efficiency score")
    cost_effectiveness_index: float = Field(..., ge=0.0, le=1.0, description="Cost effectiveness index")
    recommended_focus_areas: List[str] = Field(default_factory=list, description="Key focus areas for efficiency gains")


class ImprovementRecommendation(BaseModel):
    """Actionable improvement recommendation."""

    title: str = Field(..., description="Short recommendation title")
    description: str = Field(..., description="Detailed recommendation")
    expected_benefit: str = Field(..., description="Expected agronomic or economic benefit")
    priority: str = Field(default="medium", description="Priority level (low, medium, high)")


class ProgramAssessmentReport(BaseModel):
    """Top-level program assessment response."""

    request_id: str = Field(..., description="Identifier matching the analysis request")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of report generation")
    timing_assessment: TimingAssessment = Field(..., description="Timing assessment")
    nutrient_assessment: NutrientSynchronizationAssessment = Field(..., description="Nutrient synchronization assessment")
    loss_assessment: LossRiskAssessment = Field(..., description="Loss risk assessment")
    efficiency_assessment: EfficiencyAssessment = Field(..., description="Efficiency assessment")
    recommendations: List[ImprovementRecommendation] = Field(default_factory=list, description="Actionable recommendations")
    key_takeaways: List[str] = Field(default_factory=list, description="Summary bullet points for stakeholders")


__all__ = [
    "ApplicationTimingDeviation",
    "EfficiencyAssessment",
    "FertilizerApplicationRecord",
    "ImprovementRecommendation",
    "LossRiskAssessment",
    "NutrientSynchronizationAssessment",
    "ProgramAnalysisContext",
    "ProgramAnalysisRequest",
    "ProgramAssessmentReport",
    "SoilTestResult",
    "TimingAssessment",
    "YieldRecord",
]
