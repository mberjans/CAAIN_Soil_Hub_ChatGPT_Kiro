import pytest
import io
from unittest.mock import Mock, patch

# Try to import tensorflow, skip tests if not available
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# Skip all tests if TensorFlow is not available (required for imports)
if not TENSORFLOW_AVAILABLE:
    pytest.skip("TensorFlow not available - install with: pip install tensorflow", allow_module_level=True)

try:
    from fastapi.testclient import TestClient
    from src.main import app
    from src.models.image_analysis_models import DeficiencyAnalysisResponse, DeficiencySymptom, Recommendation, ImageQuality
except ImportError as e:
    pytest.skip(f"Cannot import required modules: {e}", allow_module_level=True)

client = TestClient(app)


def test_image_analysis_endpoint_success():
    """Test successful image analysis with valid image data"""
    # Create a mock image file
    mock_image_content = b"fake_image_data"
    mock_image_file = io.BytesIO(mock_image_content)
    mock_image_file.name = "test_image.jpg"

    # Mock the analysis response
    mock_response = DeficiencyAnalysisResponse(
        image_quality=ImageQuality(score=0.8, issues=[]),
        deficiencies=[
            DeficiencySymptom(
                nutrient="Nitrogen Deficiency",
                confidence=0.75,
                severity="moderate",
                affected_area_percent=52.5,
                symptoms_detected=["Yellowing of older leaves", "Stunted growth"]
            )
        ],
        recommendations=[
            Recommendation(
                action="Apply nitrogen fertilizer soon.",
                priority="medium",
                timing="within 1 week",
                details="Address Nitrogen Deficiency imbalance"
            )
        ],
        metadata={
            "crop_type": "corn",
            "model_used": "sequential_1",
            "raw_probabilities": [0.1, 0.75, 0.1, 0.05]
        }
    )

    # Mock the CropPhotoAnalyzer
    with patch('src.api.image_analysis_routes.CropPhotoAnalyzer') as mock_analyzer_class:
        mock_analyzer = Mock()
        mock_analyzer.analyze_image.return_value = mock_response
        mock_analyzer_class.return_value = mock_analyzer

        # Test the endpoint
        response = client.post(
            "/api/v1/image-analysis/analyze-photo",
            files={"file": ("test_image.jpg", mock_image_file, "image/jpeg")},
            data={"crop_type": "corn"}
        )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "analysis_id" in data
    assert "image_quality" in data
    assert "deficiencies" in data
    assert "recommendations" in data
    assert "metadata" in data

    # Verify image quality
    assert data["image_quality"]["score"] == 0.8
    assert data["image_quality"]["issues"] == []

    # Verify deficiencies
    assert len(data["deficiencies"]) == 1
    assert data["deficiencies"][0]["nutrient"] == "Nitrogen Deficiency"
    assert data["deficiencies"][0]["confidence"] == 0.75
    assert data["deficiencies"][0]["severity"] == "moderate"

    # Verify recommendations
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["action"] == "Apply nitrogen fertilizer soon."
    assert data["recommendations"][0]["priority"] == "medium"


def test_image_analysis_endpoint_low_quality():
    """Test image analysis with low quality image"""
    # Create a mock image file
    mock_image_content = b"low_quality_image_data"
    mock_image_file = io.BytesIO(mock_image_content)
    mock_image_file.name = "blurry_image.jpg"

    # Mock the analysis response for low quality image
    mock_response = DeficiencyAnalysisResponse(
        image_quality=ImageQuality(score=0.3, issues=["Image is blurry", "Poor lighting"]),
        deficiencies=[],
        recommendations=[
            Recommendation(
                action="Retake photo with better lighting and focus.",
                priority="high",
                timing="immediate",
                details="Image quality is too low for accurate analysis."
            )
        ],
        metadata={"message": "Image quality too low for analysis."}
    )

    # Mock the CropPhotoAnalyzer
    with patch('src.api.image_analysis_routes.CropPhotoAnalyzer') as mock_analyzer_class:
        mock_analyzer = Mock()
        mock_analyzer.analyze_image.return_value = mock_response
        mock_analyzer_class.return_value = mock_analyzer

        # Test the endpoint
        response = client.post(
            "/api/v1/image-analysis/analyze-photo",
            files={"file": ("blurry_image.jpg", mock_image_file, "image/jpeg")},
            data={"crop_type": "soybean"}
        )

    assert response.status_code == 200
    data = response.json()

    # Verify low quality response
    assert data["image_quality"]["score"] == 0.3
    assert "Image is blurry" in data["image_quality"]["issues"]
    assert len(data["deficiencies"]) == 0
    assert len(data["recommendations"]) == 1
    assert "Retake photo" in data["recommendations"][0]["action"]


def test_image_analysis_endpoint_healthy_crop():
    """Test image analysis with healthy crop (no deficiencies)"""
    # Create a mock image file
    mock_image_content = b"healthy_crop_image_data"
    mock_image_file = io.BytesIO(mock_image_content)
    mock_image_file.name = "healthy_corn.jpg"

    # Mock the analysis response for healthy crop
    mock_response = DeficiencyAnalysisResponse(
        image_quality=ImageQuality(score=0.9, issues=[]),
        deficiencies=[
            DeficiencySymptom(
                nutrient="No specific deficiency detected",
                confidence=0.9,
                severity="none",
                affected_area_percent=0.0,
                symptoms_detected=[]
            )
        ],
        recommendations=[
            Recommendation(
                action="Monitor crop regularly.",
                priority="low",
                timing="ongoing",
                details="No clear deficiency symptoms observed. Continue monitoring."
            )
        ],
        metadata={
            "crop_type": "corn",
            "model_used": "sequential_1",
            "raw_probabilities": [0.9, 0.05, 0.03, 0.02]
        }
    )

    # Mock the CropPhotoAnalyzer
    with patch('src.api.image_analysis_routes.CropPhotoAnalyzer') as mock_analyzer_class:
        mock_analyzer = Mock()
        mock_analyzer.analyze_image.return_value = mock_response
        mock_analyzer_class.return_value = mock_analyzer

        # Test the endpoint
        response = client.post(
            "/api/v1/image-analysis/analyze-photo",
            files={"file": ("healthy_corn.jpg", mock_image_file, "image/jpeg")},
            data={"crop_type": "corn"}
        )

    assert response.status_code == 200
    data = response.json()

    # Verify healthy crop response
    assert data["image_quality"]["score"] == 0.9
    assert len(data["deficiencies"]) == 1
    assert data["deficiencies"][0]["nutrient"] == "No specific deficiency detected"
    assert data["deficiencies"][0]["severity"] == "none"


def test_image_analysis_endpoint_invalid_file_type():
    """Test image analysis with invalid file type"""
    # Create a mock non-image file
    mock_file_content = b"this is not an image"
    mock_file = io.BytesIO(mock_file_content)
    mock_file.name = "not_an_image.txt"

    # Test the endpoint
    response = client.post(
        "/api/v1/image-analysis/analyze-photo",
        files={"file": ("not_an_image.txt", mock_file, "text/plain")},
        data={"crop_type": "corn"}
    )

    # The endpoint should still accept it but the analyzer will handle the validation
    # For now, we expect it to reach the analyzer and let it handle validation
    assert response.status_code in [200, 400, 422]


def test_image_analysis_endpoint_missing_file():
    """Test image analysis without file upload"""
    response = client.post(
        "/api/v1/image-analysis/analyze-photo",
        data={"crop_type": "corn"}
    )

    assert response.status_code == 422  # Validation error


def test_image_analysis_endpoint_missing_crop_type():
    """Test image analysis without crop type"""
    # Create a mock image file
    mock_image_content = b"fake_image_data"
    mock_image_file = io.BytesIO(mock_image_content)
    mock_image_file.name = "test_image.jpg"

    response = client.post(
        "/api/v1/image-analysis/analyze-photo",
        files={"file": ("test_image.jpg", mock_image_file, "image/jpeg")}
    )

    assert response.status_code == 422  # Validation error


def test_image_analysis_endpoint_invalid_crop_type():
    """Test image analysis with invalid crop type"""
    # Create a mock image file
    mock_image_content = b"fake_image_data"
    mock_image_file = io.BytesIO(mock_image_content)
    mock_image_file.name = "test_image.jpg"

    # Mock the analyzer to raise a ValueError for invalid crop type
    with patch('src.api.image_analysis_routes.CropPhotoAnalyzer') as mock_analyzer_class:
        mock_analyzer = Mock()
        mock_analyzer.analyze_image.side_effect = ValueError("Invalid crop type: invalid_crop")
        mock_analyzer_class.return_value = mock_analyzer

        response = client.post(
            "/api/v1/image-analysis/analyze-photo",
            files={"file": ("test_image.jpg", mock_image_file, "image/jpeg")},
            data={"crop_type": "invalid_crop"}
        )

    assert response.status_code == 400
    assert "Invalid crop type" in response.json()["detail"]


def test_image_analysis_endpoint_internal_error():
    """Test image analysis with internal server error"""
    # Create a mock image file
    mock_image_content = b"fake_image_data"
    mock_image_file = io.BytesIO(mock_image_content)
    mock_image_file.name = "test_image.jpg"

    # Mock the analyzer to raise an unexpected error
    with patch('src.api.image_analysis_routes.CropPhotoAnalyzer') as mock_analyzer_class:
        mock_analyzer = Mock()
        mock_analyzer.analyze_image.side_effect = Exception("Unexpected error")
        mock_analyzer_class.return_value = mock_analyzer

        response = client.post(
            "/api/v1/image-analysis/analyze-photo",
            files={"file": ("test_image.jpg", mock_image_file, "image/jpeg")},
            data={"crop_type": "corn"}
        )

    assert response.status_code == 500
    assert "Failed to analyze photo" in response.json()["detail"]


def test_image_analysis_endpoint_different_crop_types():
    """Test image analysis with different crop types"""
    crop_types = ["corn", "soybean", "wheat"]

    for crop_type in crop_types:
        # Create a mock image file
        mock_image_content = b"fake_image_data"
        mock_image_file = io.BytesIO(mock_image_content)
        mock_image_file.name = f"{crop_type}_image.jpg"

        # Mock the analysis response
        mock_response = DeficiencyAnalysisResponse(
            image_quality=ImageQuality(score=0.7, issues=[]),
            deficiencies=[
                DeficiencySymptom(
                    nutrient="Phosphorus Deficiency",
                    confidence=0.6,
                    severity="mild",
                    affected_area_percent=42.0,
                    symptoms_detected=["Purple or reddish leaves"]
                )
            ],
            recommendations=[
                Recommendation(
                    action="Consider phosphorus fertilizer.",
                    priority="low",
                    timing="next application",
                    details="Address Phosphorus Deficiency imbalance"
                )
            ],
            metadata={
                "crop_type": crop_type,
                "model_used": "sequential_1",
                "raw_probabilities": [0.2, 0.1, 0.6, 0.1]
            }
        )

        # Mock the CropPhotoAnalyzer
        with patch('src.api.image_analysis_routes.CropPhotoAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.analyze_image.return_value = mock_response
            mock_analyzer_class.return_value = mock_analyzer

            # Test the endpoint
            response = client.post(
                "/api/v1/image-analysis/analyze-photo",
                files={"file": (f"{crop_type}_image.jpg", mock_image_file, "image/jpeg")},
                data={"crop_type": crop_type}
            )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["crop_type"] == crop_type