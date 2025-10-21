class ImageAnalysisError(Exception):
    """Custom exception for image analysis errors."""
    pass

class InvalidImageError(ImageAnalysisError):
    """Exception raised for invalid image format or content."""
    pass

class ModelInferenceError(ImageAnalysisError):
    """Exception raised when the ML model fails to perform inference."""
    pass
