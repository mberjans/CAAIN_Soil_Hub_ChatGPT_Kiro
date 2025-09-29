"""
Disease Pressure API Routes

FastAPI routes for disease pressure mapping, analysis, and recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime
import logging

from models.disease_pressure_models import (
    DiseasePressureRequest,
    DiseasePressureResponse,
    RegionalDiseasePressure,
    DiseaseData,
    DiseaseSeverity,
    DiseaseRiskLevel,
    PathogenType,
    DataSource
)
from services.disease_service import DiseasePressureService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/disease-pressure", tags=["disease-pressure"])

# Dependency injection
async def get_disease_service() -> DiseasePressureService:
    """Get disease pressure service instance."""
    return DiseasePressureService()


@router.post("/analyze", response_model=DiseasePressureResponse)
async def analyze_disease_pressure(
    request: DiseasePressureRequest,
    background_tasks: BackgroundTasks,
    service: DiseasePressureService = Depends(get_disease_service)
):
    """
    Analyze disease pressure for a specific location and crop.
    
    This endpoint provides comprehensive disease pressure analysis including:
    - Regional disease pressure mapping
    - Current disease severity assessment
    - Variety-specific disease resistance analysis
    - Management recommendations
    - Timing guidance
    - Disease forecasting
    - Historical trend analysis
    
    **Agricultural Use Cases:**
    - Crop variety selection based on disease resistance
    - Disease management planning and timing
    - Risk assessment for field operations
    - Integrated pest management (IPM) planning
    - Economic analysis of disease management costs
    """
    try:
        logger.info(f"Disease pressure analysis request for {request.crop_type} at {request.coordinates}")
        
        # Validate request
        if not request.coordinates or len(request.coordinates) != 2:
            raise HTTPException(status_code=400, detail="Invalid coordinates format")
        
        if not request.crop_type:
            raise HTTPException(status_code=400, detail="Crop type is required")
        
        # Perform analysis
        result = await service.analyze_disease_pressure(request)
        
        # Log analysis completion
        logger.info(f"Disease pressure analysis completed for request {result.request_id}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in disease pressure analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in disease pressure analysis: {e}")
        raise HTTPException(status_code=500, detail="Disease pressure analysis failed")


@router.get("/regional-data", response_model=RegionalDiseasePressure)
async def get_regional_disease_data(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    radius_km: float = Query(50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers"),
    service: DiseasePressureService = Depends(get_disease_service)
):
    """
    Get regional disease pressure data for a specific location and crop.
    
    This endpoint provides regional disease pressure information including:
    - Active diseases in the region
    - Disease severity levels
    - Risk assessments
    - Environmental factors
    - Seasonal trends
    
    **Agricultural Use Cases:**
    - Regional disease monitoring
    - Risk assessment for new fields
    - Disease pressure mapping
    - Regional trend analysis
    """
    try:
        # Create request object
        request = DiseasePressureRequest(
            coordinates=(latitude, longitude),
            region_radius_km=radius_km,
            crop_type=crop_type,
            analysis_period_days=30,
            include_forecast=False,
            include_historical=False,
            include_management_recommendations=False,
            include_variety_recommendations=False,
            include_timing_guidance=False
        )
        
        # Get regional data
        regional_data = await service._gather_regional_disease_data(request)
        
        return regional_data
        
    except Exception as e:
        logger.error(f"Error getting regional disease data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get regional disease data")


@router.get("/disease-info/{disease_id}", response_model=DiseaseData)
async def get_disease_information(
    disease_id: str,
    service: DiseasePressureService = Depends(get_disease_service)
):
    """
    Get detailed information about a specific disease.
    
    This endpoint provides comprehensive disease information including:
    - Disease characteristics and symptoms
    - Environmental requirements
    - Geographic distribution
    - Management options
    - Economic impact
    
    **Agricultural Use Cases:**
    - Disease identification and diagnosis
    - Management strategy development
    - Educational purposes
    - Research and extension work
    """
    try:
        # Search for disease in knowledge base
        disease_info = None
        for crop_type, diseases in service.disease_knowledge.items():
            for disease_key, disease_data in diseases.items():
                if disease_data.get("disease_id") == disease_id:
                    disease_info = disease_data
                    break
            if disease_info:
                break
        
        if not disease_info:
            raise HTTPException(status_code=404, detail="Disease not found")
        
        # Convert to DiseaseData model
        disease_data = DiseaseData(
            disease_id=disease_info["disease_id"],
            disease_name=disease_info["disease_name"],
            scientific_name=disease_info.get("scientific_name"),
            pathogen_type=disease_info["pathogen_type"],
            crop_affected=disease_info.get("crop_affected", "unknown"),
            symptoms=disease_info.get("symptoms", []),
            transmission_methods=disease_info.get("transmission_methods", []),
            environmental_factors=disease_info.get("environmental_factors", {}),
            geographic_distribution=disease_info.get("geographic_distribution", []),
            seasonal_patterns=disease_info.get("seasonal_patterns", {}),
            yield_loss_potential=disease_info.get("yield_loss_potential"),
            quality_impact=disease_info.get("quality_impact"),
            cultural_controls=disease_info.get("cultural_controls", []),
            chemical_controls=disease_info.get("chemical_controls", []),
            biological_controls=disease_info.get("biological_controls", []),
            data_source=DataSource.UNIVERSITY_EXTENSION,
            confidence_score=0.9
        )
        
        return disease_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting disease information: {e}")
        raise HTTPException(status_code=500, detail="Failed to get disease information")


@router.get("/diseases-by-crop/{crop_type}")
async def get_diseases_by_crop(
    crop_type: str,
    pathogen_type: Optional[PathogenType] = Query(None, description="Filter by pathogen type"),
    severity_threshold: Optional[DiseaseSeverity] = Query(None, description="Minimum severity threshold"),
    service: DiseasePressureService = Depends(get_disease_service)
):
    """
    Get all diseases associated with a specific crop type.
    
    This endpoint provides a list of diseases that affect the specified crop,
    with optional filtering by pathogen type and severity threshold.
    
    **Agricultural Use Cases:**
    - Crop-specific disease planning
    - Disease risk assessment
    - Management strategy development
    - Educational resources
    """
    try:
        crop_diseases = service.disease_knowledge.get(crop_type.lower(), {})
        
        if not crop_diseases:
            raise HTTPException(status_code=404, detail=f"No diseases found for crop type: {crop_type}")
        
        # Convert to DiseaseData models
        diseases = []
        for disease_key, disease_info in crop_diseases.items():
            # Apply filters
            if pathogen_type and disease_info.get("pathogen_type") != pathogen_type:
                continue
            
            disease_data = DiseaseData(
                disease_id=disease_info["disease_id"],
                disease_name=disease_info["disease_name"],
                scientific_name=disease_info.get("scientific_name"),
                pathogen_type=disease_info["pathogen_type"],
                crop_affected=crop_type,
                symptoms=disease_info.get("symptoms", []),
                transmission_methods=disease_info.get("transmission_methods", []),
                environmental_factors=disease_info.get("environmental_factors", {}),
                geographic_distribution=disease_info.get("geographic_distribution", []),
                seasonal_patterns=disease_info.get("seasonal_patterns", {}),
                yield_loss_potential=disease_info.get("yield_loss_potential"),
                quality_impact=disease_info.get("quality_impact"),
                cultural_controls=disease_info.get("cultural_controls", []),
                chemical_controls=disease_info.get("chemical_controls", []),
                biological_controls=disease_info.get("biological_controls", []),
                data_source=DataSource.UNIVERSITY_EXTENSION,
                confidence_score=0.9
            )
            diseases.append(disease_data)
        
        return {
            "crop_type": crop_type,
            "diseases": diseases,
            "total_count": len(diseases),
            "pathogen_types": list(set(d.pathogen_type for d in diseases))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting diseases by crop: {e}")
        raise HTTPException(status_code=500, detail="Failed to get diseases by crop")


@router.get("/risk-assessment")
async def get_disease_risk_assessment(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    growth_stage: Optional[str] = Query(None, description="Current growth stage"),
    service: DiseasePressureService = Depends(get_disease_service)
):
    """
    Get disease risk assessment for a specific location and crop.
    
    This endpoint provides a quick disease risk assessment including:
    - Overall risk level
    - High-risk diseases
    - Risk factors
    - Recommendations
    
    **Agricultural Use Cases:**
    - Quick risk assessment
    - Field scouting prioritization
    - Management decision support
    - Risk communication
    """
    try:
        # Create request for risk assessment
        request = DiseasePressureRequest(
            coordinates=(latitude, longitude),
            region_radius_km=25.0,  # Smaller radius for risk assessment
            crop_type=crop_type,
            growth_stage=growth_stage,
            analysis_period_days=14,  # Shorter period for risk assessment
            include_forecast=True,
            include_historical=False,
            include_management_recommendations=True,
            include_variety_recommendations=False,
            include_timing_guidance=False
        )
        
        # Perform analysis
        result = await service.analyze_disease_pressure(request)
        
        # Extract risk assessment information
        risk_assessment = {
            "overall_risk_level": result.overall_risk_level,
            "risk_factors": [],
            "high_risk_diseases": [],
            "recommendations": [],
            "confidence_level": result.confidence_level,
            "analysis_date": result.analysis_timestamp
        }
        
        # Extract risk factors from active diseases
        for disease_entry in result.active_diseases:
            risk_assessment["risk_factors"].extend(disease_entry.risk_factors)
            if disease_entry.risk_level in [DiseaseRiskLevel.HIGH, DiseaseRiskLevel.VERY_HIGH, DiseaseRiskLevel.CRITICAL]:
                risk_assessment["high_risk_diseases"].append({
                    "disease_name": disease_entry.disease_name,
                    "risk_level": disease_entry.risk_level,
                    "severity": disease_entry.current_severity,
                    "management_priority": disease_entry.management_priority
                })
        
        # Extract recommendations
        if result.management_recommendations:
            risk_assessment["recommendations"] = result.management_recommendations.cultural_practices[:3]
        
        # Remove duplicates
        risk_assessment["risk_factors"] = list(set(risk_assessment["risk_factors"]))
        
        return risk_assessment
        
    except Exception as e:
        logger.error(f"Error in disease risk assessment: {e}")
        raise HTTPException(status_code=500, detail="Disease risk assessment failed")


@router.get("/health")
async def health_check():
    """Health check endpoint for disease pressure service."""
    return {
        "status": "healthy",
        "service": "disease-pressure",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }


@router.get("/supported-crops")
async def get_supported_crops(
    service: DiseasePressureService = Depends(get_disease_service)
):
    """
    Get list of crops supported by the disease pressure service.
    
    This endpoint provides a list of all crops for which disease pressure
    analysis is available.
    
    **Agricultural Use Cases:**
    - Service capability discovery
    - Crop selection validation
    - API integration planning
    """
    try:
        supported_crops = list(service.disease_knowledge.keys())
        
        # Add crop information
        crop_info = []
        for crop_type in supported_crops:
            diseases = service.disease_knowledge[crop_type]
            crop_info.append({
                "crop_type": crop_type,
                "disease_count": len(diseases),
                "pathogen_types": list(set(d.get("pathogen_type") for d in diseases.values())),
                "diseases": [d.get("disease_name") for d in diseases.values()]
            })
        
        return {
            "supported_crops": crop_info,
            "total_crops": len(supported_crops),
            "total_diseases": sum(len(diseases) for diseases in service.disease_knowledge.values())
        }
        
    except Exception as e:
        logger.error(f"Error getting supported crops: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported crops")


@router.get("/data-sources")
async def get_data_sources():
    """
    Get information about data sources used by the disease pressure service.
    
    This endpoint provides information about the data sources and their
    reliability for disease pressure analysis.
    """
    return {
        "data_sources": [
            {
                "source": "university_extension",
                "name": "University Extension Services",
                "description": "Disease data from university extension services and agricultural research stations",
                "reliability": "high",
                "update_frequency": "weekly"
            },
            {
                "source": "usda_survey",
                "name": "USDA Disease Surveys",
                "description": "Official disease survey data from USDA",
                "reliability": "high",
                "update_frequency": "monthly"
            },
            {
                "source": "weather_model",
                "name": "Weather-Based Models",
                "description": "Disease predictions based on weather models and disease development models",
                "reliability": "moderate",
                "update_frequency": "daily"
            },
            {
                "source": "field_observation",
                "name": "Field Observations",
                "description": "Disease observations from field scouts and farmers",
                "reliability": "moderate",
                "update_frequency": "weekly"
            },
            {
                "source": "research_trial",
                "name": "Research Trials",
                "description": "Disease data from research trials and variety testing",
                "reliability": "high",
                "update_frequency": "seasonal"
            }
        ],
        "total_sources": 5,
        "last_updated": datetime.utcnow()
    }