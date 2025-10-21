from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List
import logging

from ..services.crop_photo_analyzer import CropPhotoAnalyzer
from ..schemas.image_schemas import DeficiencyAnalysisResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/image-analysis", tags=["Image Analysis"])

# Dependency injection for analyzer
async def get_analyzer() -> CropPhotoAnalyzer:
    return CropPhotoAnalyzer()

@router.post("/analyze-photo", response_model=DeficiencyAnalysisResponse)
async def analyze_crop_photo(
    file: UploadFile = File(..., description="Crop photo to analyze"),
    crop_type: str = Form(..., description="Type of crop (e.g., 'corn', 'soybean')"),
    analyzer: CropPhotoAnalyzer = Depends(get_analyzer)
):
    """
    Analyzes a crop photo for nutrient deficiency symptoms.

    Accepts an image file and crop type, returning a detailed analysis
    of potential nutrient deficiencies, confidence scores, and recommendations.
    """
    try:
        image_data = await file.read()
        analysis_result = await analyzer.analyze_image(image_data, crop_type)
        return analysis_result
    except ValueError as e:
        logger.error(f"Validation error during photo analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing crop photo: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze photo: {str(e)}")
