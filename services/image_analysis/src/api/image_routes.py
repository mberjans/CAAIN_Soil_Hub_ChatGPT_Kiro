from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from typing import List, Dict, Any, Optional
import logging
from uuid import uuid4

from ..schemas.image_schemas import ImageAnalysisResponse
from ..services.image_processor import ImageProcessor
from ..services.deficiency_analyzer import DeficiencyAnalyzer
from ..exceptions import InvalidImageError, ModelInferenceError
from ..models.image_models import ImageQuality

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/deficiency", tags=["deficiency-detection"])

# Dependency injection
async def get_image_processor() -> ImageProcessor:
    return ImageProcessor()

async def get_deficiency_analyzer() -> DeficiencyAnalyzer:
    return DeficiencyAnalyzer()

@router.post("/image-analysis", response_model=ImageAnalysisResponse)
async def analyze_crop_image(
    image: UploadFile = File(..., description="Crop photo for analysis"),
    crop_type: str = Form(..., description="Type of crop (e.g., 'corn', 'soybean')"),
    growth_stage: Optional[str] = Form(None, description="Growth stage of the crop"),
    field_conditions: Optional[str] = Form(None, description="Additional field conditions as JSON string"),
    image_processor: ImageProcessor = Depends(get_image_processor),
    deficiency_analyzer: DeficiencyAnalyzer = Depends(get_deficiency_analyzer)
):
    """
    Analyzes a crop photo for nutrient deficiencies.

    Accepts a crop image and crop-specific metadata to detect potential nutrient deficiencies
    and provide recommendations.

    Agricultural Use Cases:
    - Early detection of nutrient stress
    - Targeted fertilizer application
    - Monitoring crop health over time
    """
    logger.info(f"Received image for analysis: {image.filename} for crop {crop_type}")
    image_data = await image.read()

    # 1. Assess image quality
    try:
        image_quality = await image_processor.assess_image_quality(image_data)
        if image_quality.score < 0.3: # Example threshold for very poor quality
            raise InvalidImageError(f"Image quality too low for reliable analysis: {image_quality.feedback}")
    except InvalidImageError as e:
        logger.warning(f"Image quality assessment failed or too low: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during image quality assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to assess image quality")

    # 2. Preprocess image
    try:
        preprocessed_image = await image_processor.preprocess_image(image_data)
    except InvalidImageError as e:
        logger.warning(f"Image preprocessing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during image preprocessing: {e}")
        raise HTTPException(status_code=500, detail="Failed to preprocess image")

    # 3. Analyze deficiencies
    try:
        analysis_result = await deficiency_analyzer.analyze_deficiencies(
            preprocessed_image=preprocessed_image,
            crop_type=crop_type,
            growth_stage=growth_stage,
            image_quality=image_quality
        )
        return ImageAnalysisResponse(**analysis_result.model_dump())
    except ModelInferenceError as e:
        logger.warning(f"Deficiency analysis failed: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during deficiency analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform deficiency analysis")

@router.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "image-analysis"}
