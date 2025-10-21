from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from ..models.tissue_test_models import TissueTestRequest, TissueTestAnalysisResponse
from ..services.tissue_test_service import TissueTestService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tissue-tests", tags=["Tissue Tests"])

# Dependency to get TissueTestService instance
async def get_tissue_test_service() -> TissueTestService:
    return TissueTestService()

@router.post(
    "/analyze",
    response_model=TissueTestAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Tissue Test Results",
    description="Submits raw tissue test results for analysis and receives detailed nutrient deficiency detection and recommendations."
)
async def analyze_tissue_test_endpoint(
    request: TissueTestRequest,
    service: TissueTestService = Depends(get_tissue_test_service)
):
    """
    Analyzes a given tissue test request to identify nutrient deficiencies.

    - **farm_id**: Unique identifier for the farm.
    - **field_id**: Unique identifier for the field.
    - **crop_type**: The type of crop (e.g., 'corn', 'soybean').
    - **growth_stage**: The current growth stage of the crop (e.g., 'V6', 'R1').
    - **test_date**: The date the tissue test was performed.
    - **results**: A list of `TissueTestResult` objects, each containing nutrient, value, unit, and optional optimal ranges.
    - **notes**: Optional notes about the test.

    Returns a `TissueTestAnalysisResponse` with detected deficiencies, their severity, and recommendations.
    """
    try:
        analysis_response = await service.analyze_tissue_test(request)
        return analysis_response
    except ValueError as e:
        logger.error(f"Validation error during tissue test analysis: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during tissue test analysis: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during analysis.")
