# Parallel Job 3: Nutrient Deficiency Detection

**TICKET-007: Visual Symptom Analysis System**  
**Estimated Timeline**: 4-5 weeks  
**Priority**: High  
**Can Start**: Immediately (No blocking dependencies)

## Executive Summary

This job implements crop photo analysis using computer vision and machine learning to detect nutrient deficiencies. Includes image preprocessing, CNN model integration, and confidence scoring. This work is **completely independent** of other parallel jobs.

## Related Tickets from Checklist

- **TICKET-007_nutrient-deficiency-detection-2.1**: Implement crop photo analysis
- **TICKET-007_nutrient-deficiency-detection-2.2**: Create image preprocessing pipeline
- **TICKET-007_nutrient-deficiency-detection-2.3**: Develop deficiency classification models
- **TICKET-007_nutrient-deficiency-detection-3.1**: Build confidence scoring system
- **TICKET-007_nutrient-deficiency-detection-3.2**: Create symptom description processing
- **TICKET-007_nutrient-deficiency-detection-4.1**: Implement multi-source deficiency identification

## Technical Stack

```yaml
Languages: Python 3.11+
Framework: FastAPI
ML/CV: TensorFlow 2.14+, OpenCV 4.8+, Pillow
Storage: AWS S3 or local filesystem
Database: PostgreSQL + MongoDB (for image metadata)
Testing: pytest, pytest-asyncio
Model Serving: TensorFlow Serving (optional)
```

## Service Architecture

**Service Location**: `services/image-analysis/`  
**Port**: 8004 (already defined in architecture)  
**Reference Pattern**: Follow `services/recommendation-engine/` structure

```
services/image-analysis/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── analysis_models.py
│   │   └── image_metadata.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_preprocessor.py
│   │   ├── deficiency_detector.py
│   │   ├── confidence_scorer.py
│   │   └── symptom_analyzer.py
│   ├── ml_models/
│   │   ├── __init__.py
│   │   ├── corn_deficiency_v1.h5
│   │   ├── soybean_deficiency_v1.h5
│   │   └── model_loader.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── analysis_routes.py
│   └── schemas/
│       ├── __init__.py
│       └── analysis_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_preprocessor.py
│   ├── test_detector.py
│   └── test_api.py
├── sample_images/
│   └── test_images/
├── requirements.txt
└── README.md
```

## Week 1-2: Image Processing Foundation (Days 1-10)

### Day 1-2: Service Setup

**requirements.txt**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
tensorflow==2.14.0
opencv-python==4.8.1.78
Pillow==10.1.0
numpy==1.26.2
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
aiofiles==23.2.1
pytest==7.4.3
```

**Setup Commands**:
```bash
mkdir -p services/image-analysis/src/{models,services,ml_models,api,schemas}
mkdir -p services/image-analysis/tests
mkdir -p services/image-analysis/sample_images/test_images
cd services/image-analysis
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Day 3-5: Image Preprocessing Service

**File**: `services/image-analysis/src/services/image_preprocessor.py`

```python
import cv2
import numpy as np
from PIL import Image
import io
from typing import Tuple, Dict, Any

class ImagePreprocessor:
    """Image preprocessing for deficiency detection (TICKET-007_nutrient-deficiency-detection-2.2)"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.min_quality_score = 0.5
    
    def preprocess_image(self, image_bytes: bytes) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Preprocess image for model input
        
        Returns:
            - Preprocessed image array
            - Quality assessment dict
        """
        # Load image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Quality assessment
        quality = self._assess_image_quality(image)
        
        # Resize to target size
        image = image.resize(self.target_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Normalize pixel values to [0, 1]
        img_array = img_array.astype(np.float32) / 255.0
        
        # Apply color correction if needed
        if quality['needs_color_correction']:
            img_array = self._apply_color_correction(img_array)
        
        # Enhance features
        img_array = self._enhance_features(img_array)
        
        return img_array, quality
    
    def _assess_image_quality(self, image: Image.Image) -> Dict[str, Any]:
        """Assess image quality for analysis"""
        img_array = np.array(image)
        
        # Check resolution
        width, height = image.size
        resolution_ok = width >= 224 and height >= 224
        
        # Check brightness
        brightness = np.mean(img_array)
        brightness_ok = 50 < brightness < 200
        
        # Check blur (Laplacian variance)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_ok = blur_score > 100
        
        # Overall quality score
        quality_score = (
            (0.3 if resolution_ok else 0) +
            (0.4 if brightness_ok else 0) +
            (0.3 if blur_ok else 0)
        )
        
        issues = []
        if not resolution_ok:
            issues.append("Low resolution")
        if not brightness_ok:
            issues.append("Poor lighting" if brightness < 50 else "Overexposed")
        if not blur_ok:
            issues.append("Image is blurry")
        
        return {
            "score": quality_score,
            "resolution_ok": resolution_ok,
            "brightness_ok": brightness_ok,
            "blur_ok": blur_ok,
            "issues": issues,
            "needs_color_correction": not brightness_ok
        }
    
    def _apply_color_correction(self, img_array: np.ndarray) -> np.ndarray:
        """Apply color correction to improve analysis"""
        # Simple histogram equalization
        img_uint8 = (img_array * 255).astype(np.uint8)
        
        # Convert to LAB color space
        lab = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge and convert back
        lab = cv2.merge([l, a, b])
        corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
        return corrected.astype(np.float32) / 255.0
    
    def _enhance_features(self, img_array: np.ndarray) -> np.ndarray:
        """Enhance features for better deficiency detection"""
        # Slight sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        img_uint8 = (img_array * 255).astype(np.uint8)
        sharpened = cv2.filter2D(img_uint8, -1, kernel)
        
        return sharpened.astype(np.float32) / 255.0
```

### Day 6-10: Deficiency Detection Service

**File**: `services/image-analysis/src/services/deficiency_detector.py`

```python
import numpy as np
import tensorflow as tf
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class DeficiencyDetector:
    """CNN-based deficiency detection (TICKET-007_nutrient-deficiency-detection-2.3)"""
    
    def __init__(self):
        self.models = {}
        self.deficiency_classes = {
            "corn": ["healthy", "nitrogen", "phosphorus", "potassium", "sulfur", "iron", "zinc"],
            "soybean": ["healthy", "nitrogen", "phosphorus", "potassium", "iron", "manganese"],
            "wheat": ["healthy", "nitrogen", "phosphorus", "potassium", "sulfur"]
        }
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models"""
        # For development, create simple models
        # In production, load actual trained models
        for crop in ["corn", "soybean", "wheat"]:
            try:
                # Try to load existing model
                model_path = f"src/ml_models/{crop}_deficiency_v1.h5"
                self.models[crop] = tf.keras.models.load_model(model_path)
                logger.info(f"Loaded model for {crop}")
            except:
                # Create simple placeholder model for development
                self.models[crop] = self._create_placeholder_model(len(self.deficiency_classes[crop]))
                logger.warning(f"Using placeholder model for {crop}")
    
    def _create_placeholder_model(self, num_classes: int):
        """Create placeholder model for development"""
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(224, 224, 3)),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        return model
    
    async def analyze_image(
        self,
        preprocessed_image: np.ndarray,
        crop_type: str,
        growth_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze image for nutrient deficiencies
        
        Returns deficiency predictions with confidence scores
        """
        if crop_type not in self.models:
            raise ValueError(f"Unsupported crop type: {crop_type}")
        
        model = self.models[crop_type]
        
        # Add batch dimension
        img_batch = np.expand_dims(preprocessed_image, axis=0)
        
        # Run inference
        predictions = model.predict(img_batch, verbose=0)[0]
        
        # Get deficiency classes for this crop
        classes = self.deficiency_classes[crop_type]
        
        # Build results
        deficiencies = []
        for i, (class_name, confidence) in enumerate(zip(classes, predictions)):
            if class_name != "healthy" and confidence > 0.1:  # Threshold for reporting
                severity = self._determine_severity(confidence)
                deficiencies.append({
                    "nutrient": class_name,
                    "confidence": float(confidence),
                    "severity": severity,
                    "affected_area_percent": self._estimate_affected_area(confidence),
                    "symptoms_detected": self._get_symptoms(class_name, crop_type)
                })
        
        # Sort by confidence
        deficiencies.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "deficiencies": deficiencies,
            "healthy_probability": float(predictions[0]) if classes[0] == "healthy" else 0.0,
            "model_version": "v1.0"
        }
    
    def _determine_severity(self, confidence: float) -> str:
        """Determine deficiency severity from confidence"""
        if confidence > 0.7:
            return "severe"
        elif confidence > 0.4:
            return "moderate"
        else:
            return "mild"
    
    def _estimate_affected_area(self, confidence: float) -> float:
        """Estimate percentage of plant affected"""
        # Simplified estimation
        return min(confidence * 100, 100)
    
    def _get_symptoms(self, nutrient: str, crop_type: str) -> List[str]:
        """Get typical symptoms for deficiency"""
        symptom_database = {
            "nitrogen": ["Yellowing of older leaves", "Stunted growth", "Pale green color"],
            "phosphorus": ["Purple or reddish leaves", "Delayed maturity", "Poor root development"],
            "potassium": ["Leaf edge burn", "Yellowing between veins", "Weak stalks"],
            "sulfur": ["Yellowing of young leaves", "Stunted growth"],
            "iron": ["Interveinal chlorosis", "Yellowing of young leaves"],
            "zinc": ["White or yellow bands", "Shortened internodes"],
            "manganese": ["Interveinal chlorosis", "Brown spots on leaves"]
        }
        return symptom_database.get(nutrient, ["Consult agricultural expert"])
```

## Week 3: API & Testing (Days 11-15)

### API Implementation

**File**: `services/image-analysis/src/api/analysis_routes.py`

```python
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from typing import Optional
from ..services.image_preprocessor import ImagePreprocessor
from ..services.deficiency_detector import DeficiencyDetector
from ..services.confidence_scorer import ConfidenceScorer

router = APIRouter(prefix="/api/v1/deficiency", tags=["deficiency-detection"])

preprocessor = ImagePreprocessor()
detector = DeficiencyDetector()
scorer = ConfidenceScorer()

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
        
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
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
                    "Get closer to the plant"
                ]
            }
        
        # Analyze for deficiencies
        analysis = await detector.analyze_image(preprocessed_img, crop_type, growth_stage)
        
        # Generate recommendations
        recommendations = _generate_recommendations(analysis)
        
        return {
            "success": True,
            "analysis_id": "generated_uuid_here",
            "image_quality": quality,
            "analysis": analysis,
            "recommendations": recommendations
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def _generate_recommendations(analysis: Dict) -> List[Dict]:
    """Generate action recommendations based on analysis"""
    recommendations = []
    
    for deficiency in analysis['deficiencies']:
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
```

## Definition of Done

### Functional Requirements
- [ ] Image preprocessing pipeline working
- [ ] Deficiency detection models loaded
- [ ] API accepts and processes images
- [ ] Confidence scoring implemented
- [ ] Quality assessment functional

### Testing Requirements
- [ ] Unit tests for preprocessing
- [ ] Model inference tests
- [ ] API integration tests
- [ ] Test with sample crop images
- [ ] Performance: <10s per image

### Agricultural Validation
- [ ] Test with known deficiency images
- [ ] Validate symptom descriptions
- [ ] Expert review of recommendations

## Integration Points

Integrates with:
- **Recommendation Engine**: For fertilizer recommendations
- **User Management**: For image storage and history
- **Mobile App**: For camera integration

## Common Pitfalls

1. **Model Size**: Large models may cause memory issues
2. **Image Quality**: Poor images lead to false positives
3. **Lighting Variations**: Outdoor lighting affects color analysis
4. **Growth Stage**: Symptoms vary by growth stage

## Next Steps

After completion, integrate with fertilizer optimization (Job 2) for complete deficiency → recommendation workflow.

