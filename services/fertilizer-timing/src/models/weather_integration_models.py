"""
Weather and soil integration models for fertilizer timing workflows.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .strategy_integration import WeatherWindow


class SoilConditionSnapshot(BaseModel):
    """
    Snapshot of soil conditions relevant to fertilizer timing decisions.
    """

    soil_texture: Optional[str] = Field(
        None,
        description="Soil texture classification when available.",
    )
    drainage_class: Optional[str] = Field(
        None,
        description="Soil drainage classification when available.",
    )
    soil_moisture: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relative soil moisture level on a 0-1 scale.",
    )
    soil_temperature_f: Optional[float] = Field(
        None,
        description="Estimated soil temperature in degrees Fahrenheit.",
    )
    trafficability: str = Field(
        ...,
        description="Field trafficability status for equipment operations.",
    )
    compaction_risk: str = Field(
        ...,
        description="Risk of soil compaction under current conditions.",
    )
    limiting_factors: List[str] = Field(
        default_factory=list,
        description="Soil-related factors that could limit application success.",
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Actions to improve soil readiness or mitigate risks.",
    )


class WeatherConditionSummary(BaseModel):
    """
    Summary of weather drivers that influence application timing.
    """

    forecast_days: int = Field(
        ...,
        ge=0,
        description="Number of days evaluated in the forecast horizon.",
    )
    precipitation_outlook: str = Field(
        ...,
        description="Qualitative precipitation outlook for the horizon.",
    )
    temperature_trend: str = Field(
        ...,
        description="General temperature trend description.",
    )
    wind_risk: str = Field(
        ...,
        description="Wind speed related application risk.",
    )
    humidity_trend: str = Field(
        ...,
        description="Humidity trend impacting drying and volatilization.",
    )
    advisory_notes: List[str] = Field(
        default_factory=list,
        description="Weather advisories relevant to fertilizer timing.",
    )


class WeatherSoilWindow(BaseModel):
    """
    Combined weather and soil assessment for a specific application window.
    """

    window: WeatherWindow = Field(
        ...,
        description="Weather window produced by the timing optimizer.",
    )
    soil_snapshot: SoilConditionSnapshot = Field(
        ...,
        description="Soil condition snapshot aligned with the window.",
    )
    combined_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Combined suitability score blending weather and soil readiness.",
    )
    limiting_factor: str = Field(
        ...,
        description="Primary factor limiting the window suitability.",
    )
    recommended_action: str = Field(
        ...,
        description="Actionable guidance for this application window.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the combined assessment.",
    )


class WeatherSoilIntegrationReport(BaseModel):
    """
    Aggregated integration result aligning weather and soil conditions.
    """

    request_id: str = Field(
        ...,
        description="Identifier matching the originating timing request.",
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the report was generated.",
    )
    soil_summary: SoilConditionSnapshot = Field(
        ...,
        description="General soil condition summary for the field.",
    )
    weather_summary: WeatherConditionSummary = Field(
        ...,
        description="Summary of key forecast drivers.",
    )
    application_windows: List[WeatherSoilWindow] = Field(
        default_factory=list,
        description="Combined application window assessments.",
    )
    forecast_generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the forecast data was evaluated.",
    )


__all__ = [
    "SoilConditionSnapshot",
    "WeatherConditionSummary",
    "WeatherSoilIntegrationReport",
    "WeatherSoilWindow",
]
