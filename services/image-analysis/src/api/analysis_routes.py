from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from typing import Optional, Dict, Any
import logging
import uuid
import io
from PIL import Image

# Import the existing services
from ..services.image_preprocessor import ImagePreprocessor
from ..services.detector import DeficiencyDetector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/deficiency", tags=["deficiency-detection"])

# Initialize services
preprocessor = ImagePreprocessor()
detector = DeficiencyDetector()

@router.post("/image-analysis")
async def analyze_crop_image(
    image: UploadFile = File(..., description="Crop image (JPEG/PNG)"),
    crop_type: str = Form(..., description="Crop type (corn, soybean, wheat)"),
    growth_stage: Optional[str] = Form(None, description="Growth stage")
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

        # Additional file size validation (max 10MB) - check first before expensive operations
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image file too large. Maximum size is 10MB")

        # Enhanced file validation
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Validate supported formats
        supported_formats = ['image/jpeg', 'image/jpg', 'image/png']
        if image.content_type not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Supported formats: {', '.join(supported_formats)}"
            )

        # Validate file is actually an image by trying to open it
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()  # Verify it's a valid image
            # Reopen for processing since verify() closes the file
            img = Image.open(io.BytesIO(image_bytes))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or corrupt image file")

        # Validate image dimensions
        width, height = img.size
        if width < 224 or height < 224:
            raise HTTPException(
                status_code=400,
                detail="Image too small. Minimum resolution is 224x224 pixels"
            )

        # Preprocess image
        preprocessed_img, quality = preprocessor.preprocess_image(image_bytes)

        # Check quality
        if quality['score'] < preprocessor.min_quality_score:
            return {
                "success": False,
                "message": "Image quality too low for analysis",
                "image_quality": quality,
                "suggestions": [
                    "Ensure good lighting",
                    "Hold camera steady to avoid blur",
                    "Get closer to the plant",
                    "Ensure minimum resolution of 224x224 pixels"
                ]
            }

        # Analyze for deficiencies
        analysis = detector.analyze_image(preprocessed_img, crop_type, growth_stage)

        # Generate recommendations
        recommendations = _generate_recommendations(analysis)

        return {
            "success": True,
            "analysis_id": str(uuid.uuid4()),
            "image_quality": quality,
            "analysis": analysis,
            "recommendations": recommendations
        }

    except FastAPIHTTPException:
        # Re-raise HTTPExceptions (like validation errors) without modification
        raise
    except ValueError as e:
        logger.error(f"Validation error during image analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing crop image: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def _generate_recommendations(analysis: Dict) -> list:
    """Generate action recommendations based on analysis"""
    recommendations = []

    for deficiency in analysis.get('deficiencies', []):
        nutrient = deficiency['nutrient']
        severity = deficiency['severity']

        if severity == "severe":
            priority = "high"
            timing = "immediate"
        elif severity == "moderate":
            priority = "medium"
            timing = "within 1 week"
        else:
            priority = "low"
            timing = "within 2 weeks"

        recommendations.append({
            "action": f"Apply {nutrient} fertilizer",
            "priority": priority,
            "timing": timing,
            "details": f"Address {nutrient} deficiency detected with {deficiency['confidence']:.0%} confidence"
        })

    return recommendations

@router.get("/health")
async def health_check():
    """Health check endpoint for deficiency detection service"""
    return {
        "status": "healthy",
        "service": "deficiency-detection",
        "version": "1.0.0"
    }