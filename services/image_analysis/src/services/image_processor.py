import numpy as np
from PIL import Image
import io
from typing import Tuple, List

from ..exceptions import InvalidImageError
from ..models.image_models import ImageQuality, ImageQualityIssue

class ImageProcessor:
    """Handles image preprocessing and quality assessment."""

    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size

    async def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """
        Loads, resizes, and normalizes an image for model input.
        Args:
            image_data: Raw image bytes.
        Returns:
            A numpy array representing the preprocessed image.
        Raises:
            InvalidImageError: If the image data is invalid or corrupted.
        """
        try:
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image = image.resize(self.target_size)
            image_array = np.array(image)
            # Normalize pixel values to [0, 1]
            image_array = image_array / 255.0
            return image_array
        except Exception as e:
            raise InvalidImageError(f"Failed to preprocess image: {e}")

    async def assess_image_quality(self, image_data: bytes) -> ImageQuality:
        """
        Assesses the quality of the input image.
        This is a placeholder and should be replaced with actual CV algorithms.
        Args:
            image_data: Raw image bytes.
        Returns:
            An ImageQuality object.
        """
        issues: List[ImageQualityIssue] = []
        feedback: str = ""
        score: float = 1.0

        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size

            if min(width, height) < 100: # Example: very small image
                issues.append(ImageQualityIssue.TOO_SMALL)
                feedback += "Image resolution is very low. "
                score -= 0.2

            # Placeholder for more advanced checks
            # if is_blurry(image): issues.append(ImageQualityIssue.BLURRY)
            # if is_poor_lighting(image): issues.append(ImageQualityIssue.POOR_LIGHTING)

            if not issues:
                feedback = "Image quality is good for analysis."
                score = 0.95
            elif score < 0.5:
                feedback = "Image quality is poor and may affect analysis accuracy. " + feedback
            else:
                feedback = "Image quality has some issues but may still be usable. " + feedback

        except Exception as e:
            # If image can't even be opened, it's poor quality
            issues.append(ImageQualityIssue.INVALID_FORMAT)
            feedback = f"Could not process image for quality assessment: {e}. Please ensure it's a valid image file." # type: ignore
            score = 0.1

        return ImageQuality(score=max(0.0, score), issues=issues, feedback=feedback)
