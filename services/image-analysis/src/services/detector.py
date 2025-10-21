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
        self.load_models()

    def load_models(self):
        """Load pre-trained models for deficiency detection

        This method handles model loading with the following priority:
        1. Try to load actual trained models from disk
        2. Fall back to placeholder models for development
        3. Handle errors gracefully and ensure all crop types have models

        Models are stored in self.models dictionary with crop type as key.
        """
        logger.info("Starting to load deficiency detection models...")

        for crop in self.deficiency_classes.keys():
            model_loaded = False

            # Try multiple possible model paths
            possible_paths = [
                f"src/ml_models/{crop}_deficiency_v1.h5",
                f"ml_models/{crop}_deficiency_v1.h5",
                f"services/image-analysis/src/ml_models/{crop}_deficiency_v1.h5",
                f"./{crop}_deficiency_v1.h5"
            ]

            for model_path in possible_paths:
                try:
                    logger.debug(f"Attempting to load model from: {model_path}")
                    self.models[crop] = tf.keras.models.load_model(model_path)
                    logger.info(f"Successfully loaded trained model for {crop} from {model_path}")
                    model_loaded = True
                    break
                except (OSError, IOError, ImportError) as e:
                    logger.debug(f"Could not load model from {model_path}: {str(e)}")
                    continue
                except Exception as e:
                    logger.warning(f"Unexpected error loading model from {model_path}: {str(e)}")
                    continue

            # If no model file was found, create a placeholder model
            if not model_loaded:
                logger.warning(f"No trained model found for {crop}, creating placeholder model")
                try:
                    self.models[crop] = self._create_placeholder_model(len(self.deficiency_classes[crop]))
                    logger.info(f"Successfully created placeholder model for {crop}")
                except Exception as e:
                    logger.error(f"Failed to create placeholder model for {crop}: {str(e)}")
                    raise RuntimeError(f"Could not load or create model for {crop}: {str(e)}")

        # Verify all models are loaded
        loaded_crops = list(self.models.keys())
        expected_crops = list(self.deficiency_classes.keys())

        if set(loaded_crops) != set(expected_crops):
            missing_crops = set(expected_crops) - set(loaded_crops)
            logger.error(f"Failed to load models for crops: {missing_crops}")
            raise RuntimeError(f"Could not load models for: {missing_crops}")

        logger.info(f"Successfully loaded {len(self.models)} models for crops: {list(self.models.keys())}")

        # Log model information for debugging
        for crop, model in self.models.items():
            try:
                input_shape = model.input_shape if hasattr(model, 'input_shape') else 'Unknown'
                output_shape = model.output_shape if hasattr(model, 'output_shape') else 'Unknown'
                logger.debug(f"{crop} model - Input: {input_shape}, Output: {output_shape}")
            except Exception as e:
                logger.debug(f"Could not get shape info for {crop} model: {str(e)}")

    def _load_models(self):
        """Private method to maintain backward compatibility

        This method calls the public load_models() method to ensure
        compatibility with existing tests and code that might call
        the private method directly.
        """
        self.load_models()

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