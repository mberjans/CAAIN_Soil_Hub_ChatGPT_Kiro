import numpy as np
import cv2
from PIL import Image
import io
from typing import Tuple, Dict, Any, Union

class ImagePreprocessor:
    """
    Image preprocessing for deficiency detection (TICKET-007_nutrient-deficiency-detection-2.2)

    Handles image quality assessment, color correction, resizing, and normalization.
    """

    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
        self.min_quality_score = 0.5

    def preprocess_image(self, image_data: bytes) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Loads, resizes, and normalizes an image from bytes.
        Enhanced version with color correction and feature enhancement.

        Args:
            image_data: Raw image bytes.

        Returns:
            Tuple containing:
            - A preprocessed NumPy array ready for model input
            - Quality assessment dictionary
        """
        try:
            # Load image using PIL for better format support
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Quality assessment
            quality = self.assess_image_quality(image_data)

            # Resize to target size
            image = image.resize(self.target_size, Image.Resampling.LANCZOS)

            # Convert to numpy array
            img_array = np.array(image)

            # Normalize pixel values to [0, 1]
            img_array = img_array.astype(np.float32) / 255.0

            # Apply color correction if needed
            if quality.get('needs_color_correction', False):
                img_array = self._apply_color_correction(img_array)

            # Enhance features
            img_array = self._enhance_features(img_array)

            # Add batch dimension (expected by most deep learning models)
            img_array = np.expand_dims(img_array, axis=0)

            return img_array, quality

        except Exception as e:
            raise ValueError(f"Could not decode image: {str(e)}")

    def assess_image_quality(self, image_data: bytes) -> Dict[str, Any]:
        """
        Assesses the quality of an image, identifying potential issues.
        Enhanced version compatible with test expectations.

        Args:
            image_data: Raw image bytes.

        Returns:
            A dictionary with quality score, issues, and assessment flags.
        """
        issues = []
        score = 1.0  # Start with perfect score

        try:
            # Try to load with PIL first for better error handling
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            img_array = np.array(image)

            # Get image dimensions
            width, height = image.size
            resolution_ok = width >= 224 and height >= 224

            # Check for blurriness using Laplacian variance
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_ok = blur_score > 100

            # Check brightness
            brightness = np.mean(img_array)
            brightness_ok = 50 < brightness < 200

            # Overall quality score calculation
            quality_score = (
                (0.3 if resolution_ok else 0) +
                (0.4 if brightness_ok else 0) +
                (0.3 if blur_ok else 0)
            )

            # Collect issues
            if not resolution_ok:
                issues.append("Low resolution")
            if not brightness_ok:
                if brightness < 50:
                    issues.append("Image is underexposed (too dark)")
                else:
                    issues.append("Image is overexposed (too bright)")
            if not blur_ok:
                issues.append("Image might be blurry")

            # Determine if color correction is needed
            needs_color_correction = not brightness_ok

            return {
                "score": float(quality_score),
                "resolution_ok": bool(resolution_ok),
                "brightness_ok": bool(brightness_ok),
                "blur_ok": bool(blur_ok),
                "issues": issues,
                "needs_color_correction": bool(needs_color_correction)
            }

        except Exception as e:
            # Handle corrupt/invalid image data
            issues.append("Corrupt or unreadable image file")
            score -= 0.5
            return {
                "score": float(max(0.0, score)),
                "resolution_ok": bool(False),
                "brightness_ok": bool(False),
                "blur_ok": bool(False),
                "issues": issues,
                "needs_color_correction": bool(False)
            }

    def _apply_color_correction(self, img_array: np.ndarray) -> np.ndarray:
        """
        Apply color correction to improve analysis using CLAHE.

        Args:
            img_array: Normalized RGB image array (float32, values 0-1)

        Returns:
            Color-corrected image array
        """
        # Convert to uint8 for OpenCV operations
        img_uint8 = (img_array * 255).astype(np.uint8)

        # Convert to LAB color space for better color correction
        lab = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel (lightness)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge channels and convert back to RGB
        lab = cv2.merge([l, a, b])
        corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        return corrected.astype(np.float32) / 255.0

    def _enhance_features(self, img_array: np.ndarray) -> np.ndarray:
        """
        Enhance features for better deficiency detection using sharpening.

        Args:
            img_array: Normalized RGB image array (float32, values 0-1)

        Returns:
            Feature-enhanced image array
        """
        # Convert to uint8 for OpenCV operations
        img_uint8 = (img_array * 255).astype(np.uint8)

        # Apply sharpening kernel
        sharpening_kernel = np.array([[-1, -1, -1],
                                     [-1,  9, -1],
                                     [-1, -1, -1]])

        # Apply the kernel
        sharpened = cv2.filter2D(img_uint8, -1, sharpening_kernel)

        # Convert back to float32 and normalize
        return sharpened.astype(np.float32) / 255.0

    def resize_image(self, image: Union[Image.Image, np.ndarray],
                    target_size: Tuple[int, int] = None) -> Union[Image.Image, np.ndarray]:
        """
        Resize an image to the specified target dimensions.

        Args:
            image: PIL Image or numpy array to resize
            target_size: Target size as (width, height). If None, uses self.target_size

        Returns:
            Resized image in the same format as input
        """
        if target_size is None:
            target_size = self.target_size

        # Handle PIL Image input
        if isinstance(image, Image.Image):
            return image.resize(target_size, Image.Resampling.LANCZOS)

        # Handle numpy array input
        elif isinstance(image, np.ndarray):
            # If array is normalized (0-1), convert to uint8 for PIL
            if image.dtype == np.float32 and np.max(image) <= 1.0:
                img_uint8 = (image * 255).astype(np.uint8)
            else:
                img_uint8 = image.astype(np.uint8)

            # Convert to PIL, resize, then back to numpy
            pil_image = Image.fromarray(img_uint8)
            resized_pil = pil_image.resize(target_size, Image.Resampling.LANCZOS)
            resized_array = np.array(resized_pil)

            # Convert back to original format
            if image.dtype == np.float32:
                return resized_array.astype(np.float32) / 255.0
            else:
                return resized_array

        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
