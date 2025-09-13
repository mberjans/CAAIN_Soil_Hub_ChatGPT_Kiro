"""
Recommendation Engine Services

Core agricultural recommendation logic and calculations.
"""

from .crop_recommendation_service import CropRecommendationService
from .fertilizer_recommendation_service import FertilizerRecommendationService
from .soil_management_service import SoilManagementService

__all__ = [
    "CropRecommendationService",
    "FertilizerRecommendationService", 
    "SoilManagementService"
]