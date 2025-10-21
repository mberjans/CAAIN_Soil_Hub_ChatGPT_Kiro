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

    def analyze_image(
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