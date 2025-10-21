import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import UploadFile
import io
import numpy as np
from PIL import Image

from services.image_analysis.main import app
from services.image_analysis.src.services.image_processor import ImageProcessor
from services.image_analysis.src.services.deficiency_analyzer import DeficiencyAnalyzer
from services.image_analysis.src.models.image_models import DeficiencyAnalysis, ImageQuality, DeficiencyDetail, RecommendationAction, Severity, ImageQualityIssue
from services.image_analysis.src.exceptions import InvalidImageError, ModelInferenceError

import sys
print("sys.path:", sys.path)
from fastapi.testclient import TestClient
print("TestClient object:", TestClient)

client = TestClient(app)

@pytest.fixture
def mock_image_data():
    # Create a dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    byte_arr.seek(0)
    return byte_arr.getvalue()

@pytest.fixture
def mock_preprocessed_image():
    return np.zeros((224, 224, 3))

@pytest.fixture
def mock_image_quality():
    return ImageQuality(score=0.9, feedback="Good quality")

@pytest.fixture
def mock_deficiency_analysis():
    return DeficiencyAnalysis(
        analysis_id="test_id",
        crop_type="corn",
        growth_stage="V6",
        image_quality=ImageQuality(score=0.9, feedback="Good quality"),
        deficiencies=[
            DeficiencyDetail(
                nutrient="Nitrogen",
                confidence=0.8,
                severity=Severity.MODERATE,
                symptoms_detected=["Yellowing"],
                visual_cues=["V-shaped yellowing"]
            )
        ],
        recommendations=[
            RecommendationAction(
                action="Apply N",
                priority="high",
                timing="immediate"
            )
        ],
        overall_confidence=0.85,
        message="Nitrogen deficiency detected."
    )

class TestImageProcessor:
    @pytest.mark.asyncio
    async def test_preprocess_image_success(self, mock_image_data):
        processor = ImageProcessor()
        preprocessed = await processor.preprocess_image(mock_image_data)
        assert isinstance(preprocessed, np.ndarray)
        assert preprocessed.shape == (224, 224, 3)

    @pytest.mark.asyncio
    async def test_preprocess_image_invalid_data(self):
        processor = ImageProcessor()
        with pytest.raises(InvalidImageError):
            await processor.preprocess_image(b"invalid image data")

    @pytest.mark.asyncio
    async def test_assess_image_quality_good(self, mock_image_data):
        processor = ImageProcessor()
        quality = await processor.assess_image_quality(mock_image_data)
        assert quality.score > 0.8
        assert not quality.issues

    @pytest.mark.asyncio
    async def test_assess_image_quality_invalid_format(self):
        processor = ImageProcessor()
        quality = await processor.assess_image_quality(b"invalid data")
        assert quality.score < 0.2
        assert ImageQualityIssue.INVALID_FORMAT in quality.issues

class TestDeficiencyAnalyzer:
    @pytest.mark.asyncio
    async def test_analyze_deficiencies_corn(self, mock_preprocessed_image, mock_image_quality):
        analyzer = DeficiencyAnalyzer()
        analysis = await analyzer.analyze_deficiencies(mock_preprocessed_image, "corn", image_quality=mock_image_quality)
        assert analysis.crop_type == "corn"
        assert len(analysis.deficiencies) > 0
        assert analysis.deficiencies[0].nutrient == "Nitrogen"

    @pytest.mark.asyncio
    async def test_analyze_deficiencies_unknown_crop(self, mock_preprocessed_image, mock_image_quality):
        analyzer = DeficiencyAnalyzer()
        with pytest.raises(ModelInferenceError):
            await analyzer.analyze_deficiencies(mock_preprocessed_image, "unknown_crop", image_quality=mock_image_quality)

class TestImageAnalysisAPI:
    def test_health_check(self):
        response = client.get("/api/v1/deficiency/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "image-analysis"}

    @patch('services.image_analysis.src.services.image_processor.ImageProcessor.assess_image_quality', new_callable=AsyncMock)
    @patch('services.image_analysis.src.services.image_processor.ImageProcessor.preprocess_image', new_callable=AsyncMock)
    @patch('services.image_analysis.src.services.deficiency_analyzer.DeficiencyAnalyzer.analyze_deficiencies', new_callable=AsyncMock)
    def test_analyze_crop_image_success(
        self,
        mock_analyze_deficiencies,
        mock_preprocess_image,
        mock_assess_image_quality,
        mock_image_data,
        mock_image_quality,
        mock_deficiency_analysis
    ):
        mock_assess_image_quality.return_value = mock_image_quality
        mock_preprocess_image.return_value = np.zeros((224, 224, 3))
        mock_analyze_deficiencies.return_value = mock_deficiency_analysis

        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={
                "image": ("test.png", mock_image_data, "image/png")
            },
            data={
                "crop_type": "corn",
                "growth_stage": "V6"
            }
        )

        assert response.status_code == 200
        assert response.json()["analysis_id"] == "test_id"
        assert response.json()["crop_type"] == "corn"
        assert len(response.json()["deficiencies"]) > 0
        mock_assess_image_quality.assert_called_once()
        mock_preprocess_image.assert_called_once()
        mock_analyze_deficiencies.assert_called_once()

    @patch('services.image_analysis.src.services.image_processor.ImageProcessor.assess_image_quality', new_callable=AsyncMock)
    def test_analyze_crop_image_poor_quality(
        self,
        mock_assess_image_quality,
        mock_image_data
    ):
        mock_assess_image_quality.return_value = ImageQuality(score=0.1, feedback="Very blurry", issues=[ImageQualityIssue.BLURRY])

        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={
                "image": ("test.png", mock_image_data, "image/png")
            },
            data={
                "crop_type": "corn"
            }
        )
        assert response.status_code == 400
        assert "Image quality too low" in response.json()["detail"]

    @patch('services.image_analysis.src.services.image_processor.ImageProcessor.assess_image_quality', new_callable=AsyncMock)
    @patch('services.image_analysis.src.services.image_processor.ImageProcessor.preprocess_image', new_callable=AsyncMock)
    def test_analyze_crop_image_model_inference_error(
        self,
        mock_preprocess_image,
        mock_assess_image_quality,
        mock_image_data
    ):
        mock_assess_image_quality.return_value = ImageQuality(score=0.9, feedback="Good quality")
        mock_preprocess_image.return_value = np.zeros((224, 224, 3))

        with patch('services.image_analysis.src.services.deficiency_analyzer.DeficiencyAnalyzer.analyze_deficiencies', side_effect=ModelInferenceError("Model not found")):
            response = client.post(
                "/api/v1/deficiency/image-analysis",
                files={
                    "image": ("test.png", mock_image_data, "image/png")
                },
                data={
                    "crop_type": "unknown_crop"
                }
            )
            assert response.status_code == 404
            assert "Model not found" in response.json()["detail"]
