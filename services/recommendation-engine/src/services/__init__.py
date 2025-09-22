"""
Recommendation Engine Services

Core agricultural recommendation services and algorithms.
"""

from .recommendation_engine import RecommendationEngine
from .crop_recommendation_service import CropRecommendationService
from .fertilizer_recommendation_service import FertilizerRecommendationService
from .soil_management_service import SoilManagementService
from .nutrient_deficiency_service import NutrientDeficiencyService
from .crop_rotation_service import CropRotationService

__all__ = [
    "RecommendationEngine",
    "CropRecommendationService", 
    "FertilizerRecommendationService",
    "SoilManagementService",
    "NutrientDeficiencyService",
    "CropRotationService"
]