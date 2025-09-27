"""
Crop Taxonomy Service Layer

Core business logic services for crop taxonomy classification, 
search, and variety recommendations.
"""

try:
    from .crop_taxonomy_service import CropTaxonomyService
except ImportError:
    from crop_taxonomy_service import CropTaxonomyService

try:
    from .crop_search_service import CropSearchService
except ImportError:  # pragma: no cover - optional during standalone tests
    CropSearchService = None

try:
    from .variety_recommendation_service import VarietyRecommendationService
except ImportError:  # pragma: no cover
    VarietyRecommendationService = None

try:
    from .regional_adaptation_service import RegionalAdaptationService
except ImportError:  # pragma: no cover
    RegionalAdaptationService = None

__all__ = []
for _name in [
    "CropTaxonomyService",
    "CropSearchService",
    "VarietyRecommendationService",
    "RegionalAdaptationService"
]:
    if globals().get(_name) is not None:
        __all__.append(_name)
