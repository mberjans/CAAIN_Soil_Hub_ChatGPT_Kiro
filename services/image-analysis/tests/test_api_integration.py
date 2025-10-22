import pytest
import io
import time
import os
from unittest.mock import patch, Mock
from PIL import Image
import numpy as np

# Try to import opencv for image enhancement
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# Try to import tensorflow, skip tests if not available
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

# Try to import required modules
try:
    from fastapi.testclient import TestClient
    from src.main import app
    from src.services.image_preprocessor import ImagePreprocessor
    from src.services.detector import DeficiencyDetector
except ImportError as e:
    pytest.skip(f"Cannot import required modules: {e}", allow_module_level=True)

client = TestClient(app)


def create_test_image(width=224, height=224, format="JPEG", color_mode="RGB"):
    """Create a high-quality test image for integration testing that passes quality checks"""
    # Create a more realistic plant-like image with proper lighting and contrast
    image = Image.new(color_mode, (width, height), color=(34, 139, 34))  # Forest green background

    # Add some variation and texture to make it less uniform and more realistic
    pixels = np.array(image)

    # Add some random noise to simulate natural leaf texture
    noise = np.random.normal(0, 15, pixels.shape)
    pixels = pixels.astype(np.int16) + noise
    pixels = np.clip(pixels, 0, 255).astype(np.uint8)

    # Add some brighter spots to simulate lighting variation
    for _ in range(width * height // 100):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        # Create small bright patches
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 <= x+dx < width and 0 <= y+dy < height:
                    pixels[y+dy, x+dx] = np.minimum(pixels[y+dy, x+dx] + 30, 255)

    # Add some darker spots for contrast
    for _ in range(width * height // 150):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if 0 <= x+dx < width and 0 <= y+dy < height:
                    pixels[y+dy, x+dx] = np.maximum(pixels[y+dy, x+dx] - 20, 0)

    textured_image = Image.fromarray(pixels)

    # Apply slight sharpening to improve blur score if cv2 is available
    if CV2_AVAILABLE:
        img_array = np.array(textured_image)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        img_uint8 = img_array.astype(np.uint8)
        sharpened = cv2.filter2D(img_uint8, -1, kernel)
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        final_image = Image.fromarray(sharpened)
    else:
        # Fallback: use PIL's built-in enhancement if cv2 is not available
        from PIL import ImageFilter
        final_image = textured_image.filter(ImageFilter.SHARPEN)

    img_byte_arr = io.BytesIO()
    # Save with high quality for JPEG
    if format.upper() == "JPEG":
        final_image.save(img_byte_arr, format=format, quality=95)
    else:
        final_image.save(img_byte_arr, format=format)
    img_byte_arr.seek(0)
    return img_byte_arr


def create_low_quality_image():
    """Create a low quality test image that passes size requirements but fails quality assessment"""
    # Create an image that meets size requirements but is intentionally low quality
    # Use PNG to avoid JPEG compression artifacts that can increase blur score

    # Create a very dark, nearly uniform image
    img_array = np.full((300, 300, 3), 5, dtype=np.uint8)  # Very dark uniform array

    # Apply extreme blur to minimize Laplacian variance
    if CV2_AVAILABLE:
        img_array = cv2.GaussianBlur(img_array, (101, 101), 0)
        # Add another blur pass for good measure
        img_array = cv2.GaussianBlur(img_array, (51, 51), 0)

    noisy_image = Image.fromarray(img_array)

    img_byte_arr = io.BytesIO()
    # Save as PNG to avoid compression artifacts that increase blur score
    noisy_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


@pytest.mark.integration
@pytest.mark.skipif(not TENSORFLOW_AVAILABLE, reason="TensorFlow not available")
class TestAPIIntegration:
    """Integration tests for the complete image analysis API workflow"""

    def test_full_analysis_workflow_success(self):
        """Test complete successful analysis workflow from upload to results"""
        # Create a test image
        test_image = create_test_image(300, 300, "JPEG")

        # Start timer for performance testing
        start_time = time.time()

        # Make the API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test_corn.jpg", test_image, "image/jpeg")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Measure response time
        response_time = time.time() - start_time

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "success" in data
        assert "analysis_id" in data
        assert "image_quality" in data
        assert "analysis" in data
        assert "recommendations" in data

        # Verify success flag
        assert data["success"] is True

        # Verify analysis structure
        analysis = data["analysis"]
        assert "crop_type" in analysis
        assert "growth_stage" in analysis
        assert "deficiencies" in analysis
        assert "healthy_probability" in analysis
        assert "model_version" in analysis

        # Verify crop type and growth stage
        assert analysis["crop_type"] == "corn"
        assert analysis["growth_stage"] == "V6"

        # Verify deficiencies structure (could be empty or have entries)
        deficiencies = analysis["deficiencies"]
        assert isinstance(deficiencies, list)
        for deficiency in deficiencies:
            assert "nutrient" in deficiency
            assert "confidence" in deficiency
            assert "severity" in deficiency
            assert "affected_area_percent" in deficiency
            assert "symptoms_detected" in deficiency
            assert isinstance(deficiency["symptoms_detected"], list)

        # Verify recommendations
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        for recommendation in recommendations:
            assert "action" in recommendation
            assert "priority" in recommendation
            assert "timing" in recommendation
            assert "details" in recommendation

        # Performance requirement: should complete within 10 seconds
        assert response_time < 10.0, f"Analysis took {response_time:.2f}s, should be under 10s"

        # Verify image quality assessment
        image_quality = data["image_quality"]
        assert "score" in image_quality
        assert "resolution_ok" in image_quality
        assert "brightness_ok" in image_quality
        assert "blur_ok" in image_quality
        assert "issues" in image_quality
        assert isinstance(image_quality["issues"], list)

    def test_full_analysis_workflow_low_quality_image(self):
        """Test workflow with low quality image that should be rejected"""
        # Create a low quality image
        low_quality_image = create_low_quality_image()

        # Make the API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("blurry_corn.png", low_quality_image, "image/png")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Should indicate failure due to low quality
        assert data["success"] is False
        assert "message" in data
        assert "quality too low" in data["message"].lower()

        # Should include image quality info
        assert "image_quality" in data
        assert data["image_quality"]["score"] < 0.5

        # Should include suggestions for improvement
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0

    def test_full_analysis_workflow_different_crop_types(self):
        """Test workflow with different supported crop types"""
        crop_types = ["corn", "soybean", "wheat"]

        for crop_type in crop_types:
            # Create a test image for each crop type
            test_image = create_test_image(300, 300, "JPEG")

            # Make the API request
            response = client.post(
                "/api/v1/deficiency/image-analysis",
                files={"image": (f"test_{crop_type}.jpg", test_image, "image/jpeg")},
                data={"crop_type": crop_type, "growth_stage": "V6"}
            )

            # Verify response
            assert response.status_code == 200
            data = response.json()

            # Verify crop type in analysis
            assert data["analysis"]["crop_type"] == crop_type

    def test_full_analysis_workflow_with_png_image(self):
        """Test workflow with PNG image format"""
        # Create a PNG test image
        test_image = create_test_image(300, 300, "PNG")

        # Make the API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test_corn.png", test_image, "image/png")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_analysis_performance_requirement(self):
        """Test that analysis meets performance requirement (<10s per image)"""
        # Create a test image
        test_image = create_test_image(400, 400, "JPEG")  # Slightly larger image

        # Run multiple analyses to check average performance
        times = []
        num_runs = 3

        for i in range(num_runs):
            # Create fresh image for each run
            fresh_image = create_test_image(400, 400, "JPEG")

            start_time = time.time()
            response = client.post(
                "/api/v1/deficiency/image-analysis",
                files={"image": (f"perf_test_{i}.jpg", fresh_image, "image/jpeg")},
                data={"crop_type": "corn", "growth_stage": "V6"}
            )
            response_time = time.time() - start_time
            times.append(response_time)

            # Verify each request succeeded
            assert response.status_code == 200

        # Check performance requirements
        avg_time = sum(times) / len(times)
        max_time = max(times)

        # All runs should be under 10 seconds
        assert all(t < 10.0 for t in times), f"Analysis times: {times}"
        assert avg_time < 10.0, f"Average analysis time {avg_time:.2f}s exceeds 10s limit"
        assert max_time < 10.0, f"Maximum analysis time {max_time:.2f}s exceeds 10s limit"

    def test_full_workflow_error_handling_invalid_crop_type(self):
        """Test error handling with invalid crop type"""
        # Create a test image
        test_image = create_test_image(300, 300, "JPEG")

        # Make API request with invalid crop type
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"crop_type": "invalid_crop", "growth_stage": "V6"}
        )

        # Should return error
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_full_workflow_error_handling_missing_parameters(self):
        """Test error handling with missing required parameters"""
        # Create a test image
        test_image = create_test_image(300, 300, "JPEG")

        # Test missing crop_type
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"growth_stage": "V6"}
        )
        assert response.status_code == 422  # Validation error

        # Test missing image file
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            data={"crop_type": "corn", "growth_stage": "V6"}
        )
        assert response.status_code == 422  # Validation error

    def test_full_workflow_error_handling_invalid_file_format(self):
        """Test error handling with invalid file format"""
        # Create a non-image file
        invalid_file = io.BytesIO(b"This is not an image file")

        # Make API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("not_an_image.txt", invalid_file, "text/plain")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Should return error
        assert response.status_code == 400
        assert "detail" in response.json()

    def test_full_workflow_large_file_handling(self):
        """Test handling of large files (should reject files > 10MB)"""
        # Create a large "image" (just simulate large file)
        large_file = io.BytesIO(b"x" * (11 * 1024 * 1024))  # 11MB file

        # Make API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("large_image.jpg", large_file, "image/jpeg")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Should return error for file too large
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_full_workflow_small_image_handling(self):
        """Test handling of images that are too small (< 224x224)"""
        # Create a small image
        small_image = create_test_image(100, 100, "JPEG")  # Too small

        # Make API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("small_image.jpg", small_image, "image/jpeg")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Should return error for image too small
        assert response.status_code == 400
        assert "too small" in response.json()["detail"].lower()

    def test_full_workflow_optional_growth_stage(self):
        """Test workflow with optional growth_stage parameter"""
        # Create a test image
        test_image = create_test_image(300, 300, "JPEG")

        # Make API request without growth_stage
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"crop_type": "corn"}  # No growth_stage
        )

        # Should succeed without growth_stage
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis"]["growth_stage"] is None

    @pytest.mark.parametrize("crop_type,growth_stage", [
        ("corn", "V6"),
        ("corn", "R1"),
        ("soybean", "V2"),
        ("soybean", "R2"),
        ("wheat", "Tillering"),
        ("wheat", "Heading")
    ])
    def test_full_workflow_various_scenarios(self, crop_type, growth_stage):
        """Test workflow with various crop and growth stage combinations"""
        # Create a test image
        test_image = create_test_image(300, 300, "JPEG")

        # Make the API request
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"crop_type": crop_type, "growth_stage": growth_stage}
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["analysis"]["crop_type"] == crop_type
        assert data["analysis"]["growth_stage"] == growth_stage


# Test class for when TensorFlow is not available
@pytest.mark.integration
class TestAPIIntegrationNoTensorFlow:
    """Integration tests that run even when TensorFlow is not available"""

    def test_health_endpoint_integration(self):
        """Test health endpoint integration"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

    def test_deficiency_health_endpoint_integration(self):
        """Test deficiency service health endpoint"""
        response = client.get("/api/v1/deficiency/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "deficiency-detection"

    def test_error_handling_no_tensorflow(self):
        """Test error handling when TensorFlow is not available"""
        # Create a test image
        test_image = create_test_image(300, 300, "JPEG")

        # Make API request - should handle TensorFlow unavailability gracefully
        response = client.post(
            "/api/v1/deficiency/image-analysis",
            files={"image": ("test.jpg", test_image, "image/jpeg")},
            data={"crop_type": "corn", "growth_stage": "V6"}
        )

        # Should either succeed (if mocked) or fail gracefully
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])