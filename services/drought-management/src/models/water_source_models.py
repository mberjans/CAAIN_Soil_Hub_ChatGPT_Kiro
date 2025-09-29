"""
Water Source Analysis Models

Data models for water source and availability analysis system.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

from .drought_models import WaterSourceType, WaterSourceAssessment

class WaterSourceAnalysisRequest(BaseModel):
    """Request model for water source analysis."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: UUID = Field(..., description="Field identifier")
    water_sources: List[Dict[str, Any]] = Field(..., description="Water source data for analysis")
    water_requirements: Dict[str, Any] = Field(..., description="Water requirements and usage patterns")
    field_characteristics: Dict[str, Any] = Field(..., description="Field characteristics and constraints")
    forecast_days: int = Field(default=30, ge=1, le=365, description="Number of days for availability forecast")
    analysis_depth: str = Field(default="comprehensive", description="Analysis depth level")

class WaterAvailabilityForecast(BaseModel):
    """Water availability forecast data."""
    forecast_period_days: int = Field(..., description="Forecast period in days")
    forecast_data: List[Dict[str, Any]] = Field(..., description="Daily availability forecast data")
    confidence_score: float = Field(..., ge=0, le=1, description="Forecast confidence score")
    last_updated: datetime = Field(..., description="Last forecast update timestamp")

class WaterBudgetPlan(BaseModel):
    """Water budget planning data."""
    total_available_capacity_gpm: float = Field(..., ge=0, description="Total available capacity in GPM")
    daily_requirement_gallons: float = Field(..., ge=0, description="Daily water requirement in gallons")
    capacity_utilization_percent: float = Field(..., ge=0, le=100, description="Capacity utilization percentage")
    seasonal_budget: Dict[str, Dict[str, Any]] = Field(..., description="Seasonal budget breakdown")
    annual_cost_estimate: Decimal = Field(..., description="Annual cost estimate")
    budget_period_months: int = Field(..., ge=1, le=12, description="Budget period in months")
    last_updated: datetime = Field(..., description="Last budget update timestamp")

class DroughtContingencyPlan(BaseModel):
    """Drought contingency planning data."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: UUID = Field(..., description="Field identifier")
    reliable_sources: List[WaterSourceType] = Field(..., description="Most reliable water sources")
    alternative_sources: List[WaterSourceType] = Field(..., description="Alternative water sources")
    contingency_scenarios: List[Dict[str, Any]] = Field(..., description="Drought contingency scenarios")
    emergency_contacts: List[Dict[str, str]] = Field(..., description="Emergency contact information")
    plan_created_date: datetime = Field(..., description="Plan creation date")
    last_reviewed_date: datetime = Field(..., description="Last plan review date")

class AlternativeWaterSource(BaseModel):
    """Alternative water source information."""
    source_type: WaterSourceType = Field(..., description="Type of alternative water source")
    description: str = Field(..., description="Description of the water source")
    feasibility_score: float = Field(..., ge=0, le=1, description="Feasibility score for implementation")
    estimated_cost_per_gallon: Decimal = Field(..., description="Estimated cost per gallon")
    implementation_timeline_days: int = Field(..., ge=0, description="Implementation timeline in days")
    required_infrastructure: List[str] = Field(..., description="Required infrastructure components")
    regulatory_requirements: List[str] = Field(..., description="Regulatory requirements")
    sustainability_score: float = Field(..., ge=0, le=1, description="Sustainability score")

class WaterUsageOptimization(BaseModel):
    """Water usage optimization recommendations."""
    optimization_plan: List[Dict[str, Any]] = Field(..., description="Optimized usage plan by source")
    total_daily_cost: float = Field(..., ge=0, description="Total daily cost for optimized usage")
    potential_savings_per_day: float = Field(..., description="Potential daily savings")
    savings_percent: float = Field(..., ge=0, le=100, description="Savings percentage")
    optimization_factors: List[str] = Field(..., description="Factors considered in optimization")
    last_optimized: datetime = Field(..., description="Last optimization timestamp")

class WaterSourceAnalysisResponse(BaseModel):
    """Response model for water source analysis."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: UUID = Field(..., description="Field identifier")
    analysis_date: datetime = Field(..., description="Analysis completion date")
    source_assessments: List[WaterSourceAssessment] = Field(..., description="Individual source assessments")
    availability_forecast: WaterAvailabilityForecast = Field(..., description="Water availability forecast")
    water_budget_plan: WaterBudgetPlan = Field(..., description="Water budget plan")
    drought_contingency_plan: DroughtContingencyPlan = Field(..., description="Drought contingency plan")
    alternative_sources: List[AlternativeWaterSource] = Field(..., description="Alternative water sources")
    usage_optimization: WaterUsageOptimization = Field(..., description="Usage optimization recommendations")
    overall_reliability_score: float = Field(..., ge=0, le=1, description="Overall reliability score")
    recommendations: List[str] = Field(..., description="General recommendations")

class WaterSourceReliability(BaseModel):
    """Water source reliability assessment."""
    source_type: WaterSourceType = Field(..., description="Type of water source")
    reliability_score: float = Field(..., ge=0, le=1, description="Overall reliability score")
    drought_resilience: float = Field(..., ge=0, le=1, description="Drought resilience score")
    seasonal_reliability: Dict[str, float] = Field(..., description="Seasonal reliability scores")
    historical_uptime_percent: float = Field(..., ge=0, le=100, description="Historical uptime percentage")
    maintenance_requirements: List[str] = Field(..., description="Maintenance requirements")

class WaterQualityAssessment(BaseModel):
    """Water quality assessment data."""
    source_type: WaterSourceType = Field(..., description="Type of water source")
    quality_score: float = Field(..., ge=0, le=1, description="Overall quality score")
    ph_level: float = Field(..., ge=0, le=14, description="pH level")
    salinity_ppm: float = Field(..., ge=0, description="Salinity in parts per million")
    nitrates_ppm: float = Field(..., ge=0, description="Nitrates in parts per million")
    pathogens_detected: bool = Field(..., description="Pathogen contamination detected")
    iron_content_ppm: float = Field(..., ge=0, description="Iron content in parts per million")
    hardness_level: str = Field(..., description="Water hardness level")
    quality_issues: List[str] = Field(..., description="Identified quality issues")
    regulatory_compliance: bool = Field(..., description="Regulatory compliance status")

class WaterCostAnalysis(BaseModel):
    """Water cost analysis data."""
    source_type: WaterSourceType = Field(..., description="Type of water source")
    cost_per_gallon: Decimal = Field(..., description="Cost per gallon")
    annual_cost_estimate: Decimal = Field(..., description="Annual cost estimate")
    cost_breakdown: Dict[str, Decimal] = Field(..., description="Cost breakdown by component")
    energy_cost_per_gallon: Decimal = Field(..., description="Energy cost per gallon")
    treatment_cost_per_gallon: Decimal = Field(..., description="Treatment cost per gallon")
    maintenance_cost_per_gallon: Decimal = Field(..., description="Maintenance cost per gallon")
    infrastructure_cost: Decimal = Field(..., description="Infrastructure cost")
    payback_period_years: float = Field(..., ge=0, description="Payback period in years")
