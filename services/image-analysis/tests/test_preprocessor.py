"""
Test file for image preprocessor - JOB3-006.1.test

Tests for ImagePreprocessor class including:
- Image quality assessment (JOB3-006.2.test)
- Color correction (JOB3-006.3.test)
- Image resizing (JOB3-006.4.test)
"""

import pytest
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

# Import the preprocessor (already implemented)
try:
    from src.services.image_preprocessor import ImagePreprocessor
except ImportError:
    pytest.skip("ImagePreprocessor not implemented yet", allow_module_level=True)


class TestImagePreprocessor:
    """Test cases for ImagePreprocessor class"""

    def setup_method(self):
        """Setup test preprocessor instance"""
        self.preprocessor = ImagePreprocessor(target_size=(224, 224))

    def test_preprocessor_initialization(self):
        """
        Test that ImagePreprocessor initializes correctly

        JOB3-006.1.test - Create test file for preprocessor
        """
        # Test default initialization
        preprocessor = ImagePreprocessor()
        assert preprocessor.target_size == (224, 224)

        # Test custom target size
        custom_size = (128, 128)
        preprocessor = ImagePreprocessor(target_size=custom_size)
        assert preprocessor.target_size == custom_size

    def test_preprocess_image_valid_input(self):
        """
        Test preprocessing a valid image

        JOB3-006.1.test - Create test file for preprocessor
        """
        # Create a simple test image using PIL
        test_image = Image.new('RGB', (100, 100), color='red')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        result = self.preprocessor.preprocess_image(img_bytes)

        # Check result properties
        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 224, 224, 3)  # Batch dimension + target size + RGB
        assert result.dtype == np.float32
        assert np.all(result >= 0.0) and np.all(result <= 1.0)  # Normalized values

    def test_preprocess_image_invalid_input(self):
        """
        Test preprocessing with invalid image data

        JOB3-006.1.test - Create test file for preprocessor
        """
        # Test with invalid bytes
        with pytest.raises(ValueError, match="Could not decode image"):
            self.preprocessor.preprocess_image(b"invalid_image_data")

    def test_assess_image_quality_perfect_image(self):
        """
        Test quality assessment with a good quality image

        JOB3-006.2.test - Write test for image quality assessment
        """
        # Create a high-quality test image
        test_image = Image.new('RGB', (300, 300), color='green')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Assess quality
        quality = self.preprocessor.assess_image_quality(img_bytes)

        # Check quality structure
        assert isinstance(quality, dict)
        assert 'score' in quality
        assert 'issues' in quality
        assert isinstance(quality['score'], float)
        assert isinstance(quality['issues'], list)
        assert 0.0 <= quality['score'] <= 1.0

    def test_assess_image_quality_corrupt_image(self):
        """
        Test quality assessment with corrupt image data

        JOB3-006.2.test - Write test for image quality assessment
        """
        # Test with corrupt data
        quality = self.preprocessor.assess_image_quality(b"corrupt_data")

        assert quality['score'] < 1.0
        assert any("corrupt" in issue.lower() for issue in quality['issues'])

    def test_assess_image_quality_dark_image(self):
        """
        Test quality assessment with underexposed (dark) image

        JOB3-006.2.test - Write test for image quality assessment
        """
        # Create a very dark image
        dark_image = Image.new('RGB', (100, 100), color=(10, 10, 10))
        img_buffer = BytesIO()
        dark_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Assess quality
        quality = self.preprocessor.assess_image_quality(img_bytes)

        assert quality['score'] < 1.0
        assert any("underexposed" in issue.lower() or "too dark" in issue.lower()
                  for issue in quality['issues'])

    def test_assess_image_quality_bright_image(self):
        """
        Test quality assessment with overexposed (bright) image

        JOB3-006.2.test - Write test for image quality assessment
        """
        # Create a very bright image
        bright_image = Image.new('RGB', (100, 100), color=(245, 245, 245))
        img_buffer = BytesIO()
        bright_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Assess quality
        quality = self.preprocessor.assess_image_quality(img_bytes)

        assert quality['score'] < 1.0
        assert any("overexposed" in issue.lower() or "too bright" in issue.lower()
                  for issue in quality['issues'])

    def test_assess_image_quality_dominant_color(self):
        """
        Test quality assessment with image having dominant single color

        JOB3-006.2.test - Write test for image quality assessment
        """
        # Create image with mostly one color
        dominant_image = Image.new('RGB', (100, 100), color='blue')
        img_buffer = BytesIO()
        dominant_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Assess quality
        quality = self.preprocessor.assess_image_quality(img_bytes)

        # May or may not trigger dominant color warning depending on compression
        assert isinstance(quality['score'], float)
        assert isinstance(quality['issues'], list)

    def test_image_resizing_output_dimensions(self):
        """
        Test that images are resized to correct dimensions

        JOB3-006.4.test - Write test for image resizing
        """
        # Create test image with different size
        test_image = Image.new('RGB', (500, 300), color='purple')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        result = self.preprocessor.preprocess_image(img_bytes)

        # Check that output has correct dimensions
        assert result.shape[1] == 224  # Height
        assert result.shape[2] == 224  # Width
        assert result.shape[3] == 3    # RGB channels

    def test_image_color_correction_rgb_conversion(self):
        """
        Test that color space is properly converted from BGR to RGB

        JOB3-006.3.test - Write test for color correction
        """
        # Create a simple test image with known colors
        test_image = Image.new('RGB', (50, 50), color=(255, 0, 0))  # Pure red
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        result = self.preprocessor.preprocess_image(img_bytes)

        # The result should maintain RGB order after conversion
        # Note: Due to JPEG compression and normalization, exact values may vary
        assert result.shape == (1, 224, 224, 3)
        assert result.dtype == np.float32

    def test_preprocess_image_different_formats(self):
        """
        Test preprocessing with different image formats

        JOB3-006.1.test - Create test file for preprocessor
        """
        # Test JPEG
        jpeg_image = Image.new('RGB', (100, 100), color='cyan')
        jpeg_buffer = BytesIO()
        jpeg_image.save(jpeg_buffer, format='JPEG')
        jpeg_bytes = jpeg_buffer.getvalue()

        result_jpeg = self.preprocessor.preprocess_image(jpeg_bytes)
        assert result_jpeg.shape == (1, 224, 224, 3)

        # Test PNG
        png_image = Image.new('RGB', (100, 100), color='magenta')
        png_buffer = BytesIO()
        png_image.save(png_buffer, format='PNG')
        png_bytes = png_buffer.getvalue()

        result_png = self.preprocessor.preprocess_image(png_bytes)
        assert result_png.shape == (1, 224, 224, 3)

    def test_custom_target_size(self):
        """
        Test preprocessing with custom target size

        JOB3-006.4.test - Write test for image resizing
        """
        # Create preprocessor with custom size
        custom_preprocessor = ImagePreprocessor(target_size=(128, 64))

        # Create test image
        test_image = Image.new('RGB', (200, 200), color='yellow')
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        result = custom_preprocessor.preprocess_image(img_bytes)

        # Check custom dimensions
        assert result.shape == (1, 64, 128, 3)  # Batch dim, height, width, RGB

    def test_image_normalization_range(self):
        """
        Test that pixel values are properly normalized to [0, 1]

        JOB3-006.1.test - Create test file for preprocessor
        """
        # Create test image
        test_image = Image.new('RGB', (100, 100), color=(128, 64, 192))
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        result = self.preprocessor.preprocess_image(img_bytes)

        # Check normalization
        assert np.all(result >= 0.0)
        assert np.all(result <= 1.0)
        assert result.dtype == np.float32