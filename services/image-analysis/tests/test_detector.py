"""
Test file for deficiency detector - JOB3-007.1.test

Tests for DeficiencyDetector class including:
- Model loading (JOB3-007.2.test)
- Deficiency detection (JOB3-007.3.test)
"""

import pytest
import numpy as np
import tensorflow as tf
from unittest.mock import Mock, patch, MagicMock

# Import the detector (not implemented yet)
try:
    from src.services.detector import DeficiencyDetector
except ImportError:
    pytest.skip("DeficiencyDetector not implemented yet", allow_module_level=True)


class TestDeficiencyDetector:
    """Test cases for DeficiencyDetector class"""

    def setup_method(self):
        """Setup test detector instance"""
        # Mock the model loading to avoid requiring actual model files
        with patch.object(DeficiencyDetector, '_load_models'):
            self.detector = DeficiencyDetector()
            # Set up mock models manually
            self.detector.models = {}
            self.detector.deficiency_classes = {
                "corn": ["healthy", "nitrogen", "phosphorus", "potassium", "sulfur", "iron", "zinc"],
                "soybean": ["healthy", "nitrogen", "phosphorus", "potassium", "iron", "manganese"],
                "wheat": ["healthy", "nitrogen", "phosphorus", "potassium", "sulfur"]
            }

    def test_detector_initialization(self):
        """
        Test that DeficiencyDetector initializes correctly

        JOB3-007.1.test - Create test file for detector
        """
        with patch.object(DeficiencyDetector, '_load_models'):
            detector = DeficiencyDetector()

            # Check that deficiency classes are defined
            assert "corn" in detector.deficiency_classes
            assert "soybean" in detector.deficiency_classes
            assert "wheat" in detector.deficiency_classes

            # Check that models dictionary is initialized
            assert isinstance(detector.models, dict)

    def test_load_models(self):
        """
        Test that models are loaded correctly

        JOB3-007.2.test - Write test for model loading
        """
        with patch('src.services.detector.tf.keras.models.load_model') as mock_load_model:
            # Mock successful model loading
            mock_model = Mock()
            mock_load_model.return_value = mock_model

            detector = DeficiencyDetector()

            # Verify that load_model was called for each crop
            expected_calls = [
                f"src/ml_models/{crop}_deficiency_v1.h5"
                for crop in ["corn", "soybean", "wheat"]
            ]

            # Check that models are loaded
            assert len(detector.models) == 3
            assert "corn" in detector.models
            assert "soybean" in detector.models
            assert "wheat" in detector.models

    def test_load_models_with_fallback(self):
        """
        Test that placeholder models are created when actual models fail to load

        JOB3-007.2.test - Write test for model loading
        """
        with patch('src.services.detector.tf.keras.models.load_model', side_effect=Exception("Model not found")):
            with patch.object(DeficiencyDetector, '_create_placeholder_model') as mock_placeholder:
                mock_model = Mock()
                mock_placeholder.return_value = mock_model

                detector = DeficiencyDetector()

                # Verify placeholder model creation is called for each crop
                assert mock_placeholder.call_count == 3

                # Verify models are still created
                assert len(detector.models) == 3

    def test_create_placeholder_model(self):
        """
        Test placeholder model creation

        JOB3-007.2.test - Write test for model loading
        """
        with patch.object(DeficiencyDetector, '_load_models'):
            detector = DeficiencyDetector()

            # Test placeholder model creation
            num_classes = 7
            model = detector._create_placeholder_model(num_classes)

            # Verify model structure
            assert isinstance(model, tf.keras.Model)
            assert model.input_shape == (None, 224, 224, 3)
            assert model.output_shape == (None, num_classes)

    def test_detect_deficiency_valid_input(self):
        """
        Test deficiency detection with valid input

        JOB3-007.3.test - Write test for deficiency detection
        """
        # Create a mock model with predictable output
        mock_model = Mock()
        # Mock prediction: [healthy=0.1, nitrogen=0.8, phosphorus=0.05, potassium=0.02, sulfur=0.01, iron=0.01, zinc=0.01]
        mock_predictions = np.array([0.1, 0.8, 0.05, 0.02, 0.01, 0.01, 0.01])
        mock_model.predict.return_value = np.array([mock_predictions])

        self.detector.models["corn"] = mock_model

        # Create test image data (224x224x3)
        test_image = np.random.rand(224, 224, 3).astype(np.float32)

        # Test detection
        result = self.detector.analyze_image(test_image, "corn", "V6")

        # Verify result structure
        assert "crop_type" in result
        assert "growth_stage" in result
        assert "deficiencies" in result
        assert "healthy_probability" in result
        assert "model_version" in result

        # Verify values
        assert result["crop_type"] == "corn"
        assert result["growth_stage"] == "V6"
        assert result["model_version"] == "v1.0"
        assert result["healthy_probability"] == 0.1

        # Verify deficiencies
        assert len(result["deficiencies"]) > 0
        assert result["deficiencies"][0]["nutrient"] == "nitrogen"
        assert result["deficiencies"][0]["confidence"] == 0.8
        assert result["deficiencies"][0]["severity"] == "severe"

    def test_detect_deficiency_unsupported_crop(self):
        """
        Test deficiency detection with unsupported crop type

        JOB3-007.3.test - Write test for deficiency detection
        """
        test_image = np.random.rand(224, 224, 3).astype(np.float32)

        # Test with unsupported crop
        with pytest.raises(ValueError, match="Unsupported crop type"):
            self.detector.analyze_image(test_image, "unsupported_crop")

    def test_detect_deficiency_no_deficiencies(self):
        """
        Test deficiency detection when plant is healthy

        JOB3-007.3.test - Write test for deficiency detection
        """
        # Create a mock model with healthy prediction
        mock_model = Mock()
        # Mock prediction: [healthy=0.9, nitrogen=0.05, phosphorus=0.02, potassium=0.01, sulfur=0.01, iron=0.005, zinc=0.005]
        mock_predictions = np.array([0.9, 0.05, 0.02, 0.01, 0.01, 0.005, 0.005])
        mock_model.predict.return_value = np.array([mock_predictions])

        self.detector.models["corn"] = mock_model

        test_image = np.random.rand(224, 224, 3).astype(np.float32)

        result = self.detector.analyze_image(test_image, "corn")

        # Should have no deficiencies (all below 0.1 threshold)
        assert len(result["deficiencies"]) == 0
        assert result["healthy_probability"] == 0.9

    def test_determine_severity(self):
        """
        Test severity determination logic

        JOB3-007.3.test - Write test for deficiency detection
        """
        # Test severe confidence
        assert self.detector._determine_severity(0.8) == "severe"
        assert self.detector._determine_severity(0.71) == "severe"

        # Test moderate confidence
        assert self.detector._determine_severity(0.5) == "moderate"
        assert self.detector._determine_severity(0.41) == "moderate"

        # Test mild confidence
        assert self.detector._determine_severity(0.2) == "mild"
        assert self.detector._determine_severity(0.1) == "mild"

    def test_estimate_affected_area(self):
        """
        Test affected area estimation

        JOB3-007.3.test - Write test for deficiency detection
        """
        # Test normal values
        assert self.detector._estimate_affected_area(0.5) == 50.0
        assert self.detector._estimate_affected_area(0.8) == 80.0

        # Test edge case (should not exceed 100%)
        assert self.detector._estimate_affected_area(1.2) == 100.0
        assert self.detector._estimate_affected_area(1.0) == 100.0

    def test_get_symptoms(self):
        """
        Test symptom retrieval for different nutrients

        JOB3-007.3.test - Write test for deficiency detection
        """
        # Test known nutrients
        nitrogen_symptoms = self.detector._get_symptoms("nitrogen", "corn")
        assert isinstance(nitrogen_symptoms, list)
        assert len(nitrogen_symptoms) > 0
        assert any("yellow" in symptom.lower() or "Yellowing" in symptom for symptom in nitrogen_symptoms)

        phosphorus_symptoms = self.detector._get_symptoms("phosphorus", "corn")
        assert isinstance(phosphorus_symptoms, list)
        assert len(phosphorus_symptoms) > 0

        # Test unknown nutrient
        unknown_symptoms = self.detector._get_symptoms("unknown_nutrient", "corn")
        assert unknown_symptoms == ["Consult agricultural expert"]

    def test_deficiency_confidence_ordering(self):
        """
        Test that deficiencies are ordered by confidence (highest first)

        JOB3-007.3.test - Write test for deficiency detection
        """
        # Create mock model with multiple deficiencies
        mock_model = Mock()
        # Mock prediction: [healthy=0.1, nitrogen=0.3, phosphorus=0.6, potassium=0.8, sulfur=0.4, iron=0.2, zinc=0.1]
        mock_predictions = np.array([0.1, 0.3, 0.6, 0.8, 0.4, 0.2, 0.1])
        mock_model.predict.return_value = np.array([mock_predictions])

        self.detector.models["corn"] = mock_model

        test_image = np.random.rand(224, 224, 3).astype(np.float32)

        result = self.detector.analyze_image(test_image, "corn")

        # Verify deficiencies are sorted by confidence (highest first)
        confidences = [deficiency["confidence"] for deficiency in result["deficiencies"]]
        assert confidences == sorted(confidences, reverse=True)

        # Verify the highest confidence deficiency is first
        assert result["deficiencies"][0]["nutrient"] == "potassium"
        assert result["deficiencies"][0]["confidence"] == 0.8

    def test_different_crop_types(self):
        """
        Test detection with different crop types

        JOB3-007.3.test - Write test for deficiency detection
        """
        test_image = np.random.rand(224, 224, 3).astype(np.float32)

        # Test each supported crop type
        for crop_type in ["corn", "soybean", "wheat"]:
            mock_model = Mock()
            # Create predictions appropriate for each crop's deficiency classes
            num_classes = len(self.detector.deficiency_classes[crop_type])
            mock_predictions = np.random.rand(num_classes)
            mock_predictions[0] = 0.1  # Set healthy to low confidence
            mock_model.predict.return_value = np.array([mock_predictions])

            self.detector.models[crop_type] = mock_model

            result = self.detector.analyze_image(test_image, crop_type)

            assert result["crop_type"] == crop_type
            assert isinstance(result["deficiencies"], list)