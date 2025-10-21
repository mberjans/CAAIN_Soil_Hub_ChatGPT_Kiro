import numpy as np
import cv2
from typing import Tuple

class ImagePreprocessor:
    """Handles preprocessing of crop images for analysis."""

    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size

    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Loads, resizes, and normalizes an image from bytes.

        Args:
            image_data: Raw image bytes.

        Returns:
            A preprocessed NumPy array ready for model input.
        """
        # Decode image from bytes
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Could not decode image. Invalid image data.")

        # Resize image
        image = cv2.resize(image, self.target_size)

        # Convert BGR to RGB (OpenCV loads as BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Normalize pixel values to [0, 1]
        image = image.astype(np.float32) / 255.0

        # Add batch dimension (expected by most deep learning models)
        image = np.expand_dims(image, axis=0)

        return image

    def assess_image_quality(self, image_data: bytes) -> dict:
        """
        Assesses the quality of an image, identifying potential issues.

        Args:
            image_data: Raw image bytes.

        Returns:
            A dictionary with quality score and a list of issues.
        """
        issues = []
        score = 1.0 # Start with perfect score

        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            issues.append("Corrupt or unreadable image file.")
            score -= 0.5
            return {"score": max(0.0, score), "issues": issues}

        # Check for blurriness (using Laplacian variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        if fm < 100: # Threshold can be adjusted
            issues.append("Image might be blurry.")
            score -= 0.2

        # Check for underexposure/overexposure (simple brightness check)
        brightness = np.mean(image)
        if brightness < 50: # Dark image
            issues.append("Image is underexposed (too dark).")
            score -= 0.15
        elif brightness > 200: # Bright image
            issues.append("Image is overexposed (too bright).")
            score -= 0.15

        # Check for dominant single color (might indicate poor lighting or background)
        # This is a very basic check and can be improved
        hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        if np.max(hist) / np.sum(hist) > 0.5: # More than 50% of pixels in one color bin
            issues.append("Image has a dominant color, possibly due to poor lighting or uniform background.")
            score -= 0.1

        return {"score": max(0.0, score), "issues": issues}
