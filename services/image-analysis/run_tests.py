#!/usr/bin/env python3
"""
Direct test runner for detector tests to bypass pytest collection issues
"""

import sys
import os
import numpy as np
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.services.detector import DeficiencyDetector
    import tensorflow as tf
    print("✓ Successfully imported required modules")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

def run_confidence_scorer_tests():
    """Run the confidence scoring tests specifically for JOB3-009.4.verify"""

    print("\n=== Running Confidence Scorer Tests ===")

    # Test 1: Test _calculate_confidence method
    print("\n1. Testing _calculate_confidence method...")

    # Mock the model loading to avoid requiring actual model files
    with patch.object(DeficiencyDetector, 'load_models'):
        detector = DeficiencyDetector()
        # Set up mock models manually
        detector.models = {}
        detector.deficiency_classes = {
            "corn": ["healthy", "nitrogen", "phosphorus", "potassium", "sulfur", "iron", "zinc"],
            "soybean": ["healthy", "nitrogen", "phosphorus", "potassium", "iron", "manganese"],
            "wheat": ["healthy", "nitrogen", "phosphorus", "potassium", "sulfur"]
        }

    # Test confidence calculation
    raw_confidence = 0.75
    prediction_distribution = np.array([0.1, 0.75, 0.1, 0.05])  # healthy, nitrogen, phosphorus, potassium
    class_index = 1  # nitrogen class

    try:
        result = detector._calculate_confidence(
            raw_confidence,
            prediction_distribution,
            class_index
        )

        # Verify result structure
        required_keys = [
            "enhanced_confidence", "confidence_level", "prediction_certainty",
            "competing_classes", "distribution_analysis", "confidence_factors", "raw_confidence"
        ]

        for key in required_keys:
            if key not in result:
                raise AssertionError(f"Missing key '{key}' in confidence result")

        # Verify values
        if result["raw_confidence"] != raw_confidence:
            raise AssertionError(f"Expected raw_confidence {raw_confidence}, got {result['raw_confidence']}")

        if not (0.0 <= result["enhanced_confidence"] <= 1.0):
            raise AssertionError(f"enhanced_confidence out of range: {result['enhanced_confidence']}")

        if result["confidence_level"] not in ["high", "medium", "low"]:
            raise AssertionError(f"Invalid confidence_level: {result['confidence_level']}")

        print("   ✓ _calculate_confidence method works correctly")

    except Exception as e:
        print(f"   ✗ _calculate_confidence method failed: {e}")
        return False

    # Test 2: Test severity determination
    print("\n2. Testing severity determination...")

    test_cases = [
        (0.8, "severe"),
        (0.71, "severe"),
        (0.7, "moderate"),
        (0.5, "moderate"),
        (0.41, "moderate"),
        (0.4, "mild"),
        (0.2, "mild"),
        (0.1, "mild")
    ]

    for confidence, expected_severity in test_cases:
        try:
            severity = detector._determine_severity(confidence)
            if severity != expected_severity:
                raise AssertionError(f"Expected {expected_severity}, got {severity} for confidence {confidence}")
        except Exception as e:
            print(f"   ✗ Severity determination failed for confidence {confidence}: {e}")
            return False

    print("   ✓ Severity determination works correctly")

    # Test 3: Test affected area estimation
    print("\n3. Testing affected area estimation...")

    area_test_cases = [
        (0.5, None, None, 50.0),  # Simple case without severity/crop
        (0.8, None, None, 80.0),  # Simple case without severity/crop
        (1.2, None, None, 100.0), # Edge case - should cap at 100%
        (0.5, "moderate", "corn", 50.0),   # With severity and crop
        (0.8, "severe", "corn", None),     # Severe with enhancement - will be calculated
    ]

    for confidence, severity, crop_type, expected in area_test_cases:
        try:
            result = detector._estimate_affected_area(confidence, severity, crop_type)
            if expected is not None:
                if abs(result - expected) > 1.0:  # Allow small tolerance
                    raise AssertionError(f"Expected ~{expected}, got {result} for confidence={confidence}, severity={severity}, crop={crop_type}")
            else:
                # Just verify it's in valid range
                if not (0.0 <= result <= 100.0):
                    raise AssertionError(f"Result out of range: {result}")
        except Exception as e:
            print(f"   ✗ Affected area estimation failed: {e}")
            return False

    print("   ✓ Affected area estimation works correctly")

    # Test 4: Test enhanced confidence calculation scenarios
    print("\n4. Testing enhanced confidence calculation...")

    scenarios = [
        ("high_confidence", np.array([0.05, 0.85, 0.05, 0.05]), 1, True),
        ("low_confidence", np.array([0.3, 0.35, 0.25, 0.1]), 1, True),
        ("equal_distribution", np.array([0.25, 0.25, 0.25, 0.25]), 1, True),
    ]

    for scenario_name, dist, class_idx, should_work in scenarios:
        try:
            result = detector._calculate_enhanced_confidence(0.35, dist, class_idx)
            if not (0.0 <= result <= 1.0):
                raise AssertionError(f"Enhanced confidence out of range: {result}")
            print(f"   ✓ {scenario_name} scenario: {result:.3f}")
        except Exception as e:
            if should_work:
                print(f"   ✗ {scenario_name} scenario failed: {e}")
                return False
            else:
                print(f"   ○ {scenario_name} scenario skipped: {e}")

    # Test 5: Test confidence level categorization
    print("\n5. Testing confidence level categorization...")

    category_tests = [
        (0.9, "high"),
        (0.8, "high"),
        (0.7, "medium"),
        (0.5, "medium"),
        (0.4, "low"),
        (0.1, "low")
    ]

    for confidence, expected_category in category_tests:
        try:
            category = detector._categorize_confidence_level(confidence)
            if category != expected_category:
                raise AssertionError(f"Expected {expected_category}, got {category} for confidence {confidence}")
        except Exception as e:
            print(f"   ✗ Confidence categorization failed for {confidence}: {e}")
            return False

    print("   ✓ Confidence level categorization works correctly")

    # Test 6: Test full analysis with confidence scoring
    print("\n6. Testing full analysis with confidence scoring...")

    # Create a mock model with predictable output
    mock_model = Mock()
    mock_predictions = np.array([0.1, 0.6, 0.2, 0.1, 0.0, 0.0, 0.0])  # healthy, nitrogen, phosphorus, etc.
    mock_model.predict.return_value = np.array([mock_predictions])

    detector.models["corn"] = mock_model

    # Create test image data (224x224x3)
    test_image = np.random.rand(224, 224, 3).astype(np.float32)

    try:
        result = detector.analyze_image(test_image, "corn", "V6")

        # Verify result structure
        required_keys = ["crop_type", "growth_stage", "deficiencies", "healthy_probability", "model_version"]
        for key in required_keys:
            if key not in result:
                raise AssertionError(f"Missing key '{key}' in analysis result")

        # Verify deficiencies have confidence scoring
        if len(result["deficiencies"]) > 0:
            deficiency = result["deficiencies"][0]
            req_def_keys = ["nutrient", "confidence", "severity", "affected_area_percent", "symptoms_detected"]
            for key in req_def_keys:
                if key not in deficiency:
                    raise AssertionError(f"Missing key '{key}' in deficiency result")

        print("   ✓ Full analysis with confidence scoring works correctly")
        print(f"   ✓ Found {len(result['deficiencies'])} deficiencies")

    except Exception as e:
        print(f"   ✗ Full analysis failed: {e}")
        return False

    return True

def main():
    """Main test runner"""
    print("JOB3-009.4.verify - Running Confidence Scorer Tests")
    print("=" * 60)

    success = run_confidence_scorer_tests()

    print("\n" + "=" * 60)
    if success:
        print("✓ ALL CONFIDENCE SCORER TESTS PASSED")
        print("✓ JOB3-009.4.verify completed successfully")
        return 0
    else:
        print("✗ SOME CONFIDENCE SCORER TESTS FAILED")
        print("✗ JOB3-009.4.verify failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())