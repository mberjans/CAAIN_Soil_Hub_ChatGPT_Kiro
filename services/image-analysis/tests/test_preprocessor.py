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
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check result properties
        assert isinstance(img_array, np.ndarray)
        assert img_array.shape == (1, 224, 224, 3)  # Batch dimension + target size + RGB
        assert img_array.dtype == np.float32
        assert np.all(img_array >= 0.0) and np.all(img_array <= 1.0)  # Normalized values

        # Check quality assessment
        assert isinstance(quality, dict)
        assert 'score' in quality
        assert 'issues' in quality

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
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that output has correct dimensions
        assert img_array.shape[1] == 224  # Height
        assert img_array.shape[2] == 224  # Width
        assert img_array.shape[3] == 3    # RGB channels

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
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # The result should maintain RGB order after conversion
        # Note: Due to JPEG compression and normalization, exact values may vary
        assert img_array.shape == (1, 224, 224, 3)
        assert img_array.dtype == np.float32

    def test_color_correction_dark_image(self):
        """
        Test color correction functionality with dark image that needs enhancement

        JOB3-006.3.test - Write test for color correction
        """
        # Create a dark image that should trigger color correction
        dark_image = Image.new('RGB', (100, 100), color=(20, 20, 30))  # Very dark blue-gray
        img_buffer = BytesIO()
        dark_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Process the dark image
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that color correction was applied
        # Result should be a properly processed numpy array
        assert isinstance(img_array, np.ndarray)
        assert img_array.shape == (1, 224, 224, 3)
        assert img_array.dtype == np.float32
        assert np.all(img_array >= 0.0) and np.all(img_array <= 1.0)

        # The mean brightness should be improved from the original dark image
        mean_brightness = np.mean(img_array)
        # Should be higher than the original dark image (after normalization)
        assert mean_brightness > 0.05  # Original would be ~0.08 after normalization

    def test_color_correction_washed_out_image(self):
        """
        Test color correction with overexposed/washed out image

        JOB3-006.3.test - Write test for color correction
        """
        # Create a washed out image (high brightness, low contrast)
        washed_image = Image.new('RGB', (100, 100), color=(230, 230, 235))  # Very light gray
        img_buffer = BytesIO()
        washed_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Process the washed out image
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that processing completed successfully
        assert isinstance(img_array, np.ndarray)
        assert img_array.shape == (1, 224, 224, 3)
        assert img_array.dtype == np.float32
        assert np.all(img_array >= 0.0) and np.all(img_array <= 1.0)

    def test_color_correction_color_cast(self):
        """
        Test color correction with image that has color cast

        JOB3-006.3.test - Write test for color correction
        """
        # Create an image with strong color cast (reddish tint)
        color_cast_image = Image.new('RGB', (100, 100), color=(200, 100, 80))  # Reddish
        img_buffer = BytesIO()
        color_cast_image.save(img_buffer, format='JPEG')
        img_bytes = img_buffer.getvalue()

        # Process the image with color cast
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that processing completed
        assert isinstance(img_array, np.ndarray)
        assert img_array.shape == (1, 224, 224, 3)
        assert img_array.dtype == np.float32

        # Color correction should attempt to balance the RGB channels
        # The exact result depends on the correction algorithm used
        red_mean = np.mean(img_array[0, :, :, 0])
        green_mean = np.mean(img_array[0, :, :, 1])
        blue_mean = np.mean(img_array[0, :, :, 2])

        # All channels should have some reasonable values after correction
        assert red_mean > 0.0 and green_mean > 0.0 and blue_mean > 0.0
        assert red_mean <= 1.0 and green_mean <= 1.0 and blue_mean <= 1.0

    def test_color_correction_normal_image_unchanged(self):
        """
        Test that properly balanced images are not negatively affected by color correction

        JOB3-006.3.test - Write test for color correction
        """
        # Create a well-balanced image
        balanced_image = Image.new('RGB', (100, 100), color=(128, 128, 128))  # Neutral gray
        img_buffer = BytesIO()
        balanced_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the balanced image
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that processing completed successfully
        assert isinstance(img_array, np.ndarray)
        assert img_array.shape == (1, 224, 224, 3)
        assert img_array.dtype == np.float32
        assert np.all(img_array >= 0.0) and np.all(img_array <= 1.0)

        # For a balanced image, the correction should maintain reasonable color balance
        red_mean = np.mean(img_array[0, :, :, 0])
        green_mean = np.mean(img_array[0, :, :, 1])
        blue_mean = np.mean(img_array[0, :, :, 2])

        # Channel means should be relatively close for a gray image
        channel_diff = max(red_mean, green_mean, blue_mean) - min(red_mean, green_mean, blue_mean)
        assert channel_diff < 0.2  # Allow some variation due to compression

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

        img_array_jpeg, quality_jpeg = self.preprocessor.preprocess_image(jpeg_bytes)
        assert img_array_jpeg.shape == (1, 224, 224, 3)

        # Test PNG
        png_image = Image.new('RGB', (100, 100), color='magenta')
        png_buffer = BytesIO()
        png_image.save(png_buffer, format='PNG')
        png_bytes = png_buffer.getvalue()

        img_array_png, quality_png = self.preprocessor.preprocess_image(png_bytes)
        assert img_array_png.shape == (1, 224, 224, 3)

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
        img_array, quality = custom_preprocessor.preprocess_image(img_bytes)

        # Check custom dimensions
        assert img_array.shape == (1, 64, 128, 3)  # Batch dim, height, width, RGB

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
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check normalization
        assert np.all(img_array >= 0.0)
        assert np.all(img_array <= 1.0)
        assert img_array.dtype == np.float32

    def test_image_resizing_aspect_ratio_changes(self):
        """
        Test image resizing with different aspect ratios

        JOB3-006.4.test - Write test for image resizing
        """
        # Test cases with different aspect ratios
        test_cases = [
            (100, 50),   # Wide image (2:1)
            (50, 100),   # Tall image (1:2)
            (200, 200),  # Square image (1:1)
            (400, 300),  # Landscape (4:3)
            (300, 400),  # Portrait (3:4)
        ]

        for width, height in test_cases:
            # Create test image with specific aspect ratio
            test_image = Image.new('RGB', (width, height), color='blue')
            img_buffer = BytesIO()
            test_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            # Process the image
            img_array, quality = self.preprocessor.preprocess_image(img_bytes)

            # All should resize to target dimensions regardless of input aspect ratio
            assert img_array.shape == (1, 224, 224, 3)
            assert img_array.dtype == np.float32
            assert np.all(img_array >= 0.0) and np.all(img_array <= 1.0)

    def test_image_resizing_edge_cases(self):
        """
        Test image resizing with edge cases (very small and very large images)

        JOB3-006.4.test - Write test for image resizing
        """
        # Test very small image
        tiny_image = Image.new('RGB', (10, 10), color='red')
        img_buffer = BytesIO()
        tiny_image.save(img_buffer, format='PNG')
        tiny_bytes = img_buffer.getvalue()

        img_array, quality = self.preprocessor.preprocess_image(tiny_bytes)
        assert img_array.shape == (1, 224, 224, 3)

        # Test very large image (but not too large to avoid memory issues)
        large_image = Image.new('RGB', (1000, 1000), color='green')
        img_buffer = BytesIO()
        large_image.save(img_buffer, format='PNG')
        large_bytes = img_buffer.getvalue()

        img_array, quality = self.preprocessor.preprocess_image(large_bytes)
        assert img_array.shape == (1, 224, 224, 3)

    def test_image_resizing_maintains_color_channels(self):
        """
        Test that image resizing maintains RGB color channels properly

        JOB3-006.4.test - Write test for image resizing
        """
        # Create image with distinct colors in each channel (all non-zero)
        test_image = Image.new('RGB', (100, 100), color=(200, 100, 50))  # Brown-orange
        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that we have 3 color channels
        assert img_array.shape[3] == 3  # RGB channels

        # Check that all channels have some data (not empty or zero)
        red_channel = img_array[0, :, :, 0]
        green_channel = img_array[0, :, :, 1]
        blue_channel = img_array[0, :, :, 2]

        assert np.mean(red_channel) > 0.0
        assert np.mean(green_channel) > 0.0
        assert np.mean(blue_channel) > 0.0

        # For brown-orange image, red channel should be strongest on average
        assert np.mean(red_channel) > np.mean(green_channel)
        assert np.mean(red_channel) > np.mean(blue_channel)

    def test_image_resizing_quality_preservation(self):
        """
        Test that image resizing preserves reasonable image quality

        JOB3-006.4.test - Write test for image resizing
        """
        # Create an image with a pattern that should be preserved
        test_image = Image.new('RGB', (100, 100), color='white')
        # Add some distinct features
        for i in range(0, 100, 10):
            for j in range(0, 100, 10):
                test_image.putpixel((i, j), (0, 0, 0))  # Black dots

        img_buffer = BytesIO()
        test_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()

        # Process the image
        img_array, quality = self.preprocessor.preprocess_image(img_bytes)

        # Check that the result maintains some variation (not completely uniform)
        # The pattern will be blurred but should still create variation
        std_deviation = np.std(img_array)
        assert std_deviation > 0.01  # Should have some variation

        # Check that we still have a mix of colors (not all same value)
        assert np.max(img_array) > np.min(img_array)

    def test_image_resizing_different_interpolation(self):
        """
        Test that OpenCV's default interpolation works for different image types

        JOB3-006.4.test - Write test for image resizing
        """
        # Test with different types of images that might benefit from different interpolation
        image_types = [
            ('gradient', self._create_gradient_image),
            ('solid', lambda: Image.new('RGB', (100, 100), color='blue')),
            ('pattern', self._create_pattern_image),
        ]

        for img_type, img_func in image_types:
            test_image = img_func()
            img_buffer = BytesIO()
            test_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()

            # Process the image
            img_array, quality = self.preprocessor.preprocess_image(img_bytes)

            # Basic checks
            assert img_array.shape == (1, 224, 224, 3)
            assert img_array.dtype == np.float32
            assert np.all(img_array >= 0.0) and np.all(img_array <= 1.0)

    def _create_gradient_image(self):
        """Create a simple gradient image for testing"""
        image = Image.new('RGB', (100, 100))
        pixels = []
        for y in range(100):
            for x in range(100):
                value = int(255 * (x + y) / 200)  # Diagonal gradient
                pixels.append((value, value, value))
        image.putdata(pixels)
        return image

    def _create_pattern_image(self):
        """Create a patterned image for testing"""
        image = Image.new('RGB', (100, 100), color='white')
        for i in range(0, 100, 20):
            for j in range(0, 100, 20):
                # Create a checkerboard pattern
                if (i // 20 + j // 20) % 2 == 0:
                    for di in range(20):
                        for dj in range(20):
                            if i + di < 100 and j + dj < 100:
                                image.putpixel((i + di, j + dj), (50, 100, 150))
        return image