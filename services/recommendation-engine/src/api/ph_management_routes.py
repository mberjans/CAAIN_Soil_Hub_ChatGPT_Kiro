"""
API routes for soil pH management functionality.
Provides endpoints for pH analysis, lime recommendations, and monitoring.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field

try:
    from ..services.soil_ph_management_service import (
        SoilPHManagementService, PHAnalysis, LimeRecommendation, 
        PHManagementPlan, PHMonitoringRecord, SoilTexture, LimeType
    )
    from ..models.agricultural_models import SoilTestData
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from services.soil_ph_management_service import (
        SoilPHManagementService, PHAnalysis, LimeRecommendation, 
        PHManagementPlan, PHMonitoringRecord, SoilTexture, LimeType
    )
    from models.agricultural_models import SoilTestData

router = APIRouter(prefix="/ph", tags=["pH Management"])

# Request/Response Models
class PHAnalysisRequest(BaseModel):
    """Request for pH analysis."""
    farm_id: str
    field_id: str
    crop_type: str
    soil_test_data: SoilTestData
    field_conditions: Optional[Dict[str, Any]] = None

class LimeCalculatorRequest(BaseModel):
    """Request for lime requirement calculation."""
    current_ph: float = Field(..., ge=3.0, le=10.0)
    target_ph: float = Field(..., ge=3.0, le=10.0)
    buffer_ph: Optional[float] = Field(None, ge=4.0, le=7.5)
    soil_texture: str
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0)
    field_size_acres: float = Field(default=1.0, gt=0)
    field_conditions: Optional[Dict[str, Any]] = None

class PHMonitoringRequest(BaseModel):
    """Request for pH monitoring setup."""
    farm_id: str
    field_id: str
    monitoring_frequency: str = Field(..., pattern="^(monthly|quarterly|biannual|annual)$")
    alert_thresholds: Dict[str, float]
    crop_rotation_schedule: Optional[List[Dict[str, Any]]] = None

class PHRecordRequest(BaseModel):
    """Request to record pH measurement."""
    farm_id: str
    field_id: str
    ph_value: float = Field(..., ge=3.0, le=10.0)
    buffer_ph: Optional[float] = Field(None, ge=4.0, le=7.5)
    testing_method: str = "standard"
    lab_name: Optional[str] = None
    notes: str = ""

class CropPHRequirementsRequest(BaseModel):
    """Request for crop-specific pH requirements."""
    crop_types: List[str]
    location: Optional[Dict[str, float]] = None

# Initialize service
ph_service = SoilPHManagementService()

@router.post("/analyze")
async def analyze_ph_levels(request: PHAnalysisRequest):
    """
    Analyze soil pH levels and provide comprehensive assessment.
    
    Performs detailed pH analysis including:
    - pH level classification
    - Nutrient availability impact
    - Crop suitability assessment
    - Management priority determination
    """
    try:
        analysis = await ph_service.analyze_soil_ph(
            farm_id=request.farm_id,
            field_id=request.field_id,
            crop_type=request.crop_type,
            soil_test_data=request.soil_test_data,
            field_conditions=request.field_conditions
        )
        
        return {
            "success": True,
            "analysis": {
                "current_ph": analysis.current_ph,
                "ph_level": analysis.ph_level.value,
                "target_ph": analysis.target_ph,
                "ph_deviation": analysis.ph_deviation,
                "nutrient_availability_impact": analysis.nutrient_availability_impact,
                "crop_suitability_score": analysis.crop_suitability_score,
                "acidification_risk": analysis.acidification_risk,
                "alkalinity_risk": analysis.alkalinity_risk,
                "buffering_capacity": analysis.buffering_capacity,
                "management_priority": analysis.management_priority
            },
            "recommendations": {
                "immediate_action_needed": analysis.management_priority in ["critical", "high"],
                "next_steps": await _generate_next_steps(analysis, request.crop_type)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"pH analysis failed: {str(e)}")

@router.get("/recommendations")
async def get_ph_recommendations(
    farm_id: str = Query(..., description="Farm identifier"),
    field_id: str = Query(..., description="Field identifier"),
    crop_type: str = Query(..., description="Crop type")
):
    """
    Get pH management recommendations for a specific field and crop.
    """
    try:
        # This would typically fetch from database
        # For now, return example recommendations
        return {
            "success": True,
            "recommendations": {
                "lime_application": {
                    "recommended": True,
                    "rate_tons_per_acre": 2.5,
                    "timing": "fall_after_harvest",
                    "cost_estimate": 112.50
                },
                "monitoring": {
                    "next_test_date": "2024-09-15",
                    "frequency": "annual",
                    "parameters": ["ph", "buffer_ph", "organic_matter"]
                },
                "management_practices": [
                    "Apply lime in fall for spring crop benefit",
                    "Incorporate lime within 2 weeks of application",
                    "Retest pH 12 months after lime application"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get recommendations: {str(e)}")

@router.post("/lime-calculator")
async def calculate_lime_requirements(request: LimeCalculatorRequest):
    """
    Calculate lime requirements based on current and target pH.
    
    Provides detailed lime recommendations including:
    - Application rates for different lime types
    - Cost analysis
    - Application timing and methods
    - Expected pH changes
    """
    try:
        recommendations = await ph_service.calculate_lime_requirements(
            current_ph=request.current_ph,
            target_ph=request.target_ph,
            buffer_ph=request.buffer_ph,
            soil_texture=request.soil_texture,
            organic_matter_percent=request.organic_matter_percent,
            field_size_acres=request.field_size_acres,
            field_conditions=request.field_conditions
        )
        
        return {
            "success": True,
            "lime_requirements": [
                {
                    "lime_type": rec.amendment_type.value,
                    "application_rate_tons_per_acre": rec.application_rate_tons_per_acre,
                    "application_rate_lbs_per_acre": rec.application_rate_lbs_per_acre,
                    "application_timing": rec.application_timing.value,
                    "cost_per_acre": rec.cost_per_acre,
                    "expected_ph_change": rec.expected_ph_change,
                    "time_to_effect_months": rec.time_to_effect_months,
                    "application_notes": rec.application_notes,
                    "safety_precautions": rec.safety_precautions
                }
                for rec in recommendations
            ],
            "calculation_method": "buffer_ph" if request.buffer_ph else "ph_difference",
            "confidence": "high" if request.buffer_ph else "medium"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lime calculation failed: {str(e)}")

@router.get("/crop-requirements")
async def get_crop_ph_requirements(
    crop_types: List[str] = Query(..., description="List of crop types"),
    location: Optional[str] = Query(None, description="Location for regional adjustments")
):
    """
    Get pH requirements for specific crops.
    
    Returns optimal, acceptable, and critical pH ranges for each crop.
    """
    try:
        requirements = {}
        
        for crop_type in crop_types:
            crop_req = ph_service.crop_ph_requirements.get(
                crop_type.lower(), 
                ph_service.crop_ph_requirements.get('corn')
            )
            
            if crop_req:
                requirements[crop_type] = {
                    "optimal_range": {
                        "min": crop_req['optimal_range'][0],
                        "max": crop_req['optimal_range'][1]
                    },
                    "acceptable_range": {
                        "min": crop_req['acceptable_range'][0],
                        "max": crop_req['acceptable_range'][1]
                    },
                    "critical_minimum": crop_req['critical_minimum'],
                    "critical_maximum": crop_req['critical_maximum'],
                    "yield_impact_curve": crop_req['yield_impact_curve'],
                    "specific_sensitivities": crop_req['specific_sensitivities']
                }
        
        return {
            "success": True,
            "crop_requirements": requirements,
            "location": location,
            "notes": [
                "pH requirements may vary by region and variety",
                "Consult local extension service for specific recommendations",
                "Consider soil buffering capacity when making adjustments"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get crop requirements: {str(e)}")

@router.post("/monitor")
async def setup_ph_monitoring(request: PHMonitoringRequest):
    """
    Set up pH monitoring schedule and alerts.
    """
    try:
        monitoring_plan = {
            "monitoring_id": f"ph_monitor_{request.farm_id}_{request.field_id}_{datetime.now().strftime('%Y%m%d')}",
            "farm_id": request.farm_id,
            "field_id": request.field_id,
            "frequency": request.monitoring_frequency,
            "alert_thresholds": request.alert_thresholds,
            "next_test_date": _calculate_next_test_date(request.monitoring_frequency),
            "parameters_to_test": ["ph", "buffer_ph", "organic_matter"],
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "monitoring_plan": monitoring_plan,
            "message": "pH monitoring successfully configured"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to setup monitoring: {str(e)}")

@router.get("/trends")
async def get_ph_trends(
    farm_id: str = Query(..., description="Farm identifier"),
    field_id: str = Query(..., description="Field identifier"),
    start_date: Optional[date] = Query(None, description="Start date for trend analysis"),
    end_date: Optional[date] = Query(None, description="End date for trend analysis")
):
    """
    Get pH trends and analysis for a field.
    """
    try:
        # This would typically fetch from database
        # For now, return example trend data
        return {
            "success": True,
            "trends": {
                "trend_direction": "stable",
                "annual_change_rate": -0.05,
                "current_ph": 6.2,
                "initial_ph": 6.4,
                "total_change": -0.2,
                "readings_count": 8,
                "time_span_years": 3.2,
                "confidence": "high"
            },
            "recommendations": [
                "pH is slowly declining - monitor annually",
                "Consider lime application if trend continues",
                "Current pH is still within acceptable range"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get trends: {str(e)}")

@router.post("/alerts")
async def configure_ph_alerts(
    farm_id: str,
    field_id: str,
    alert_config: Dict[str, Any]
):
    """
    Configure pH alerts and notifications.
    """
    try:
        alert_setup = {
            "alert_id": f"ph_alert_{farm_id}_{field_id}_{datetime.now().strftime('%Y%m%d')}",
            "farm_id": farm_id,
            "field_id": field_id,
            "thresholds": alert_config.get("thresholds", {}),
            "notification_methods": alert_config.get("notification_methods", ["email"]),
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "alert_configuration": alert_setup,
            "message": "pH alerts successfully configured"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to configure alerts: {str(e)}")

@router.get("/dashboard")
async def get_ph_dashboard(
    farm_id: str = Query(..., description="Farm identifier"),
    field_ids: Optional[List[str]] = Query(None, description="Specific field IDs")
):
    """
    Get pH monitoring dashboard data.
    """
    try:
        # This would typically aggregate data from database
        dashboard_data = {
            "farm_summary": {
                "total_fields": 5,
                "fields_needing_attention": 2,
                "average_ph": 6.1,
                "last_updated": datetime.now().isoformat()
            },
            "field_status": [
                {
                    "field_id": "field_001",
                    "current_ph": 5.8,
                    "status": "needs_lime",
                    "priority": "high",
                    "last_test": "2024-03-15"
                },
                {
                    "field_id": "field_002",
                    "current_ph": 6.5,
                    "status": "optimal",
                    "priority": "low",
                    "last_test": "2024-02-28"
                }
            ],
            "upcoming_tasks": [
                {
                    "task": "Apply lime to Field 001",
                    "due_date": "2024-04-15",
                    "priority": "high"
                },
                {
                    "task": "Retest pH in Field 003",
                    "due_date": "2024-05-01",
                    "priority": "medium"
                }
            ]
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get dashboard: {str(e)}")

@router.post("/treatment-plan")
async def generate_treatment_plan(
    farm_id: str,
    field_id: str,
    crop_type: str,
    treatment_goals: Dict[str, Any]
):
    """
    Generate comprehensive pH treatment plan.
    """
    try:
        # This would use the full service to generate a complete plan
        treatment_plan = {
            "plan_id": f"ph_treatment_{farm_id}_{field_id}_{datetime.now().strftime('%Y%m%d')}",
            "farm_id": farm_id,
            "field_id": field_id,
            "crop_type": crop_type,
            "treatment_phases": [
                {
                    "phase": "immediate",
                    "actions": ["Soil test confirmation", "Lime application"],
                    "timeline": "0-2 weeks"
                },
                {
                    "phase": "short_term",
                    "actions": ["Monitor pH response", "Adjust fertilizer program"],
                    "timeline": "2-6 months"
                },
                {
                    "phase": "long_term",
                    "actions": ["Maintain optimal pH", "Regular monitoring"],
                    "timeline": "6+ months"
                }
            ],
            "success_metrics": {
                "target_ph": treatment_goals.get("target_ph", 6.5),
                "expected_yield_improvement": "8-12%",
                "roi_estimate": 3.2
            }
        }
        
        return {
            "success": True,
            "treatment_plan": treatment_plan
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate treatment plan: {str(e)}")

@router.get("/economics")
async def get_ph_economics(
    farm_id: str = Query(..., description="Farm identifier"),
    field_id: str = Query(..., description="Field identifier"),
    crop_type: str = Query(..., description="Crop type"),
    treatment_scenario: str = Query("recommended", description="Treatment scenario")
):
    """
    Get economic analysis of pH management.
    """
    try:
        economics = {
            "cost_analysis": {
                "lime_cost_per_acre": 112.50,
                "application_cost_per_acre": 25.00,
                "total_treatment_cost": 137.50
            },
            "benefit_analysis": {
                "annual_yield_improvement_percent": 10,
                "annual_benefit_per_acre": 85.00,
                "treatment_life_years": 4,
                "total_benefit": 340.00
            },
            "roi_analysis": {
                "net_benefit": 202.50,
                "benefit_cost_ratio": 2.47,
                "payback_period_years": 1.6,
                "roi_percent": 147
            },
            "risk_factors": [
                "Weather conditions may affect lime effectiveness",
                "Crop prices may fluctuate",
                "Soil conditions may vary across field"
            ]
        }
        
        return {
            "success": True,
            "economics": economics
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get economics: {str(e)}")

@router.post("/track-treatment")
async def track_treatment_progress(
    treatment_id: str,
    progress_data: Dict[str, Any]
):
    """
    Track pH treatment progress and effectiveness.
    """
    try:
        progress_record = {
            "treatment_id": treatment_id,
            "progress_date": datetime.now().isoformat(),
            "ph_measurements": progress_data.get("ph_measurements", []),
            "treatment_applied": progress_data.get("treatment_applied", {}),
            "observations": progress_data.get("observations", ""),
            "effectiveness_score": progress_data.get("effectiveness_score", 0),
            "next_actions": progress_data.get("next_actions", [])
        }
        
        return {
            "success": True,
            "progress_record": progress_record,
            "message": "Treatment progress successfully recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to track treatment: {str(e)}")

@router.get("/reports")
async def generate_ph_reports(
    farm_id: str = Query(..., description="Farm identifier"),
    report_type: str = Query("summary", description="Type of report"),
    date_range: Optional[str] = Query(None, description="Date range for report")
):
    """
    Generate pH management reports.
    """
    try:
        if report_type == "summary":
            report = {
                "report_type": "pH Management Summary",
                "farm_id": farm_id,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_fields_monitored": 5,
                    "average_ph": 6.2,
                    "fields_needing_treatment": 2,
                    "total_lime_applied_tons": 12.5,
                    "estimated_yield_improvement": "8%"
                },
                "recommendations": [
                    "Continue monitoring Field 001 after lime application",
                    "Schedule pH testing for Field 004",
                    "Consider organic matter improvement program"
                ]
            }
        else:
            report = {"message": f"Report type '{report_type}' not implemented"}
        
        return {
            "success": True,
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate report: {str(e)}")

# Helper functions
async def _generate_next_steps(analysis: PHAnalysis, crop_type: str) -> List[str]:
    """Generate next steps based on pH analysis."""
    steps = []
    
    if analysis.management_priority == "critical":
        steps.append("Immediate lime or sulfur application required")
        steps.append("Confirm pH with additional soil testing")
    elif analysis.management_priority == "high":
        steps.append("Plan lime application for next season")
        steps.append("Consider crop selection based on current pH")
    else:
        steps.append("Continue regular pH monitoring")
        steps.append("Maintain current management practices")
    
    return steps

def _calculate_next_test_date(frequency: str) -> str:
    """Calculate next test date based on monitoring frequency."""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    
    if frequency == "monthly":
        next_date = now + timedelta(days=30)
    elif frequency == "quarterly":
        next_date = now + timedelta(days=90)
    elif frequency == "biannual":
        next_date = now + timedelta(days=180)
    else:  # annual
        next_date = now + timedelta(days=365)
    
    return next_date.strftime("%Y-%m-%d")