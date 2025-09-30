"""
Agricultural Analysis API Routes
CAAIN Soil Hub - TICKET-008_farm-location-input-8.2

API endpoints for comprehensive agricultural analysis including:
- Slope analysis and topographic assessment
- Drainage evaluation and flood risk assessment
- Field accessibility evaluation
- Soil survey data integration (SSURGO)
- Watershed information and water management
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from ..services.agricultural_analysis_service import (
    agricultural_analysis_service,
    SlopeAnalysisRequest,
    SlopeAnalysisResult,
    DrainageAssessmentRequest,
    DrainageAssessmentResult,
    AccessibilityEvaluationRequest,
    AccessibilityEvaluationResult,
    SoilSurveyRequest,
    SoilSurveyResult,
    WatershedInfoRequest,
    WatershedInfoResult,
    AgriculturalAnalysisError
)
from ..auth.auth_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/fields", tags=["agricultural-analysis"])


class CoordinatesModel(BaseModel):
    """Coordinates model for API requests."""
    latitude: float
    longitude: float


class BoundaryModel(BaseModel):
    """Boundary model for API requests."""
    type: str
    coordinates: list


@router.post("/{field_id}/slope-analysis", response_model=SlopeAnalysisResult)
async def perform_slope_analysis(
    field_id: str,
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> SlopeAnalysisResult:
    """
    Perform comprehensive slope analysis for a field.
    
    This endpoint analyzes the topographic characteristics of a field including:
    - Average, maximum, and minimum slope percentages
    - Slope classification (nearly level, gentle, moderate, strong, very strong)
    - Erosion risk assessment (low, medium, high, very high)
    - Management recommendations for slope-related issues
    
    Args:
        field_id: Unique identifier for the field
        request_data: Request data containing coordinates and boundary information
        current_user: Current authenticated user
        
    Returns:
        SlopeAnalysisResult with comprehensive slope analysis data
        
    Raises:
        HTTPException: If analysis fails or field not found
    """
    try:
        logger.info(f"Performing slope analysis for field {field_id}")
        
        # Extract coordinates and boundary from request
        coordinates = CoordinatesModel(**request_data.get('coordinates', {}))
        boundary = request_data.get('boundary', {})
        
        # Create analysis request
        analysis_request = SlopeAnalysisRequest(
            field_id=field_id,
            coordinates=coordinates,
            boundary=boundary
        )
        
        # Perform slope analysis
        result = await agricultural_analysis_service.perform_slope_analysis(analysis_request)
        
        logger.info(f"Slope analysis completed for field {field_id}")
        return result
        
    except AgriculturalAnalysisError as e:
        logger.error(f"Agricultural analysis error for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "error_code": "SLOPE_ANALYSIS_FAILED",
                    "error_message": str(e),
                    "agricultural_context": "Slope analysis is essential for erosion control and field management planning",
                    "suggested_actions": [
                        "Verify field coordinates are accurate",
                        "Ensure field boundary is properly defined",
                        "Check if field is in a supported geographic area"
                    ]
                }
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in slope analysis for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during slope analysis"
        )


@router.post("/{field_id}/drainage-assessment", response_model=DrainageAssessmentResult)
async def perform_drainage_assessment(
    field_id: str,
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> DrainageAssessmentResult:
    """
    Perform comprehensive drainage assessment for a field.
    
    This endpoint evaluates the drainage characteristics of a field including:
    - USDA drainage class classification
    - Water table depth assessment
    - Flood risk evaluation based on FEMA data
    - Drainage suitability rating
    - Management recommendations for drainage issues
    
    Args:
        field_id: Unique identifier for the field
        request_data: Request data containing coordinates, boundary, and area
        current_user: Current authenticated user
        
    Returns:
        DrainageAssessmentResult with comprehensive drainage assessment data
        
    Raises:
        HTTPException: If assessment fails or field not found
    """
    try:
        logger.info(f"Performing drainage assessment for field {field_id}")
        
        # Extract data from request
        coordinates = CoordinatesModel(**request_data.get('coordinates', {}))
        boundary = request_data.get('boundary', {})
        area = request_data.get('area', 0.0)
        
        # Create assessment request
        assessment_request = DrainageAssessmentRequest(
            field_id=field_id,
            coordinates=coordinates,
            boundary=boundary,
            area=area
        )
        
        # Perform drainage assessment
        result = await agricultural_analysis_service.perform_drainage_assessment(assessment_request)
        
        logger.info(f"Drainage assessment completed for field {field_id}")
        return result
        
    except AgriculturalAnalysisError as e:
        logger.error(f"Agricultural analysis error for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "error_code": "DRAINAGE_ASSESSMENT_FAILED",
                    "error_message": str(e),
                    "agricultural_context": "Drainage assessment is critical for crop selection and field management",
                    "suggested_actions": [
                        "Verify field coordinates are accurate",
                        "Ensure field boundary and area are properly defined",
                        "Check if field is in a supported geographic area"
                    ]
                }
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in drainage assessment for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during drainage assessment"
        )


@router.post("/{field_id}/accessibility-evaluation", response_model=AccessibilityEvaluationResult)
async def evaluate_field_accessibility(
    field_id: str,
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> AccessibilityEvaluationResult:
    """
    Evaluate field accessibility for agricultural operations.
    
    This endpoint assesses the accessibility of a field for agricultural operations including:
    - Road access quality (excellent, good, fair, poor)
    - Equipment access evaluation
    - Distance to nearest roads
    - Overall accessibility score (0-10)
    - Recommendations for improving accessibility
    
    Args:
        field_id: Unique identifier for the field
        request_data: Request data containing coordinates, boundary, and area
        current_user: Current authenticated user
        
    Returns:
        AccessibilityEvaluationResult with comprehensive accessibility evaluation data
        
    Raises:
        HTTPException: If evaluation fails or field not found
    """
    try:
        logger.info(f"Evaluating accessibility for field {field_id}")
        
        # Extract data from request
        coordinates = CoordinatesModel(**request_data.get('coordinates', {}))
        boundary = request_data.get('boundary', {})
        area = request_data.get('area', 0.0)
        
        # Create evaluation request
        evaluation_request = AccessibilityEvaluationRequest(
            field_id=field_id,
            coordinates=coordinates,
            boundary=boundary,
            area=area
        )
        
        # Perform accessibility evaluation
        result = await agricultural_analysis_service.evaluate_field_accessibility(evaluation_request)
        
        logger.info(f"Accessibility evaluation completed for field {field_id}")
        return result
        
    except AgriculturalAnalysisError as e:
        logger.error(f"Agricultural analysis error for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "error_code": "ACCESSIBILITY_EVALUATION_FAILED",
                    "error_message": str(e),
                    "agricultural_context": "Accessibility evaluation is important for operational planning and equipment selection",
                    "suggested_actions": [
                        "Verify field coordinates are accurate",
                        "Ensure field boundary and area are properly defined",
                        "Check if field is in a supported geographic area"
                    ]
                }
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in accessibility evaluation for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during accessibility evaluation"
        )


@router.post("/{field_id}/soil-survey", response_model=SoilSurveyResult)
async def get_soil_survey_data(
    field_id: str,
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> SoilSurveyResult:
    """
    Retrieve comprehensive soil survey data for a field.
    
    This endpoint retrieves detailed soil information from USDA SSURGO database including:
    - Soil series identification
    - Soil texture classification
    - pH range and organic matter content
    - Cation exchange capacity (CEC)
    - Soil limitations and management recommendations
    
    Args:
        field_id: Unique identifier for the field
        request_data: Request data containing coordinates and boundary
        current_user: Current authenticated user
        
    Returns:
        SoilSurveyResult with comprehensive soil survey data
        
    Raises:
        HTTPException: If soil survey retrieval fails or field not found
    """
    try:
        logger.info(f"Retrieving soil survey data for field {field_id}")
        
        # Extract data from request
        coordinates = CoordinatesModel(**request_data.get('coordinates', {}))
        boundary = request_data.get('boundary', {})
        
        # Create soil survey request
        survey_request = SoilSurveyRequest(
            field_id=field_id,
            coordinates=coordinates,
            boundary=boundary
        )
        
        # Retrieve soil survey data
        result = await agricultural_analysis_service.get_soil_survey_data(survey_request)
        
        logger.info(f"Soil survey data retrieved for field {field_id}")
        return result
        
    except AgriculturalAnalysisError as e:
        logger.error(f"Agricultural analysis error for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "error_code": "SOIL_SURVEY_RETRIEVAL_FAILED",
                    "error_message": str(e),
                    "agricultural_context": "Soil survey data is essential for crop selection and fertility management",
                    "suggested_actions": [
                        "Verify field coordinates are accurate",
                        "Ensure field boundary is properly defined",
                        "Check if field is in a supported geographic area"
                    ]
                }
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in soil survey retrieval for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during soil survey retrieval"
        )


@router.post("/{field_id}/watershed-info", response_model=WatershedInfoResult)
async def get_watershed_information(
    field_id: str,
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> WatershedInfoResult:
    """
    Retrieve watershed information for a field.
    
    This endpoint retrieves comprehensive watershed information including:
    - Watershed name and area
    - Stream order classification
    - Water quality assessment
    - Watershed features and characteristics
    - Water management recommendations
    
    Args:
        field_id: Unique identifier for the field
        request_data: Request data containing coordinates and boundary
        current_user: Current authenticated user
        
    Returns:
        WatershedInfoResult with comprehensive watershed information
        
    Raises:
        HTTPException: If watershed information retrieval fails or field not found
    """
    try:
        logger.info(f"Retrieving watershed information for field {field_id}")
        
        # Extract data from request
        coordinates = CoordinatesModel(**request_data.get('coordinates', {}))
        boundary = request_data.get('boundary', {})
        
        # Create watershed info request
        watershed_request = WatershedInfoRequest(
            field_id=field_id,
            coordinates=coordinates,
            boundary=boundary
        )
        
        # Retrieve watershed information
        result = await agricultural_analysis_service.get_watershed_information(watershed_request)
        
        logger.info(f"Watershed information retrieved for field {field_id}")
        return result
        
    except AgriculturalAnalysisError as e:
        logger.error(f"Agricultural analysis error for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "error_code": "WATERSHED_INFO_RETRIEVAL_FAILED",
                    "error_message": str(e),
                    "agricultural_context": "Watershed information is important for water management and environmental compliance",
                    "suggested_actions": [
                        "Verify field coordinates are accurate",
                        "Ensure field boundary is properly defined",
                        "Check if field is in a supported geographic area"
                    ]
                }
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in watershed information retrieval for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during watershed information retrieval"
        )


@router.get("/{field_id}/analysis-summary")
async def get_field_analysis_summary(
    field_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get a summary of all available agricultural analyses for a field.
    
    This endpoint provides an overview of all agricultural analysis capabilities
    available for a specific field, including analysis types, data requirements,
    and expected outcomes.
    
    Args:
        field_id: Unique identifier for the field
        current_user: Current authenticated user
        
    Returns:
        Dictionary with analysis summary information
        
    Raises:
        HTTPException: If field not found or access denied
    """
    try:
        logger.info(f"Retrieving analysis summary for field {field_id}")
        
        analysis_summary = {
            "field_id": field_id,
            "available_analyses": [
                {
                    "analysis_type": "slope_analysis",
                    "endpoint": f"/api/v1/fields/{field_id}/slope-analysis",
                    "description": "Comprehensive slope analysis including erosion risk assessment",
                    "required_data": ["coordinates", "boundary"],
                    "outputs": ["average_slope", "max_slope", "slope_classification", "erosion_risk", "recommendations"]
                },
                {
                    "analysis_type": "drainage_assessment",
                    "endpoint": f"/api/v1/fields/{field_id}/drainage-assessment",
                    "description": "Drainage evaluation including flood risk and suitability assessment",
                    "required_data": ["coordinates", "boundary", "area"],
                    "outputs": ["drainage_class", "water_table_depth", "flood_risk", "suitability", "recommendations"]
                },
                {
                    "analysis_type": "accessibility_evaluation",
                    "endpoint": f"/api/v1/fields/{field_id}/accessibility-evaluation",
                    "description": "Field accessibility assessment for agricultural operations",
                    "required_data": ["coordinates", "boundary", "area"],
                    "outputs": ["road_access", "equipment_access", "distance_to_roads", "accessibility_score", "recommendations"]
                },
                {
                    "analysis_type": "soil_survey",
                    "endpoint": f"/api/v1/fields/{field_id}/soil-survey",
                    "description": "Comprehensive soil survey data from USDA SSURGO database",
                    "required_data": ["coordinates", "boundary"],
                    "outputs": ["soil_series", "texture", "ph_range", "organic_matter", "cec", "limitations", "recommendations"]
                },
                {
                    "analysis_type": "watershed_info",
                    "endpoint": f"/api/v1/fields/{field_id}/watershed-info",
                    "description": "Watershed information and water management recommendations",
                    "required_data": ["coordinates", "boundary"],
                    "outputs": ["watershed_name", "watershed_area", "stream_order", "water_quality", "features", "recommendations"]
                }
            ],
            "data_sources": [
                "USDA SSURGO Soil Survey",
                "USGS Elevation Data",
                "FEMA Flood Maps",
                "USGS Watershed Data",
                "Road Network Data"
            ],
            "agricultural_context": "These analyses provide comprehensive field assessment for agricultural planning, crop selection, and management decisions."
        }
        
        return analysis_summary
        
    except Exception as e:
        logger.error(f"Error retrieving analysis summary for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving analysis summary"
        )