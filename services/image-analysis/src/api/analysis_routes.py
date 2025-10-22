from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List, Dict, Any
import logging
import uuid
import io
from PIL import Image

# Import the existing analyzer and services
from ..services.crop_photo_analyzer import CropPhotoAnalyzer
from ..services.image_preprocessor import ImagePreprocessor
from ..schemas.image_schemas import DeficiencyAnalysisResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/deficiency", tags=["deficiency-detection"])

# Dependency injection for analyzer
async def get_analyzer() -> CropPhotoAnalyzer:
    return CropPhotoAnalyzer()

@router.post("/image-analysis")
async def analyze_crop_image(
    image: UploadFile = File(..., description="Crop image (JPEG/PNG)"),
    crop_type: str = Form(..., description="Crop type (corn, soybean, wheat)"),
    growth_stage: Optional[str] = Form(None, description="Growth stage"),
    analyzer: CropPhotoAnalyzer = Depends(get_analyzer)
):
    """
    Analyze crop image for nutrient deficiencies

    **Requirements**:
    - Image format: JPEG or PNG
    - Minimum resolution: 224x224 pixels
    - Clear view of plant leaves
    - Good lighting conditions

    **Returns**:
    - Detected deficiencies with confidence scores
    - Severity assessment
    - Recommended actions
    """
    try:
        # Read image bytes
        image_bytes = await image.read()

        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Validate file is actually an image by trying to open it
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()  # Verify it's a valid image
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Use the analyzer to process the image
        analysis_result = await analyzer.analyze_image(image_bytes, crop_type)

        # Add analysis ID for tracking
        if hasattr(analysis_result, 'dict'):
            response_data = {
                "analysis_id": str(uuid.uuid4()),
                "success": True,
                **analysis_result.dict()
            }
        else:
            response_data = {
                "analysis_id": str(uuid.uuid4()),
                "success": True,
                **analysis_result
            }

        return response_data

    except ValueError as e:
        logger.error(f"Validation error during image analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing crop image: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint for deficiency detection service"""
    return {
        "status": "healthy",
        "service": "deficiency-detection",
        "version": "1.0.0"
    }