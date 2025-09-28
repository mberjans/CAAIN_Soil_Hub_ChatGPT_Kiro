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

try:
    from .crop_attribute_service import CropAttributeTaggingService
except ImportError:  # pragma: no cover
    CropAttributeTaggingService = None

try:
    from .crop_preference_service import CropPreferenceService, crop_preference_service
except ImportError:  # pragma: no cover
    CropPreferenceService = None
    crop_preference_service = None


try:
    from .filter_engine import FilterCombinationEngine, filter_combination_engine
except ImportError:  # pragma: no cover
    FilterCombinationEngine = None
    filter_combination_engine = None

try:
    from .smart_filter_suggestion_service import SmartFilterSuggestionService, smart_filter_suggestion_service
except ImportError:  # pragma: no cover
    SmartFilterSuggestionService = None
    smart_filter_suggestion_service = None

try:
    from .result_processor import FilterResultProcessor
except ImportError: # pragma: no cover
    FilterResultProcessor = None

__all__ = []
for _name in [
    "CropTaxonomyService",
    "CropSearchService",
    "VarietyRecommendationService",
    "RegionalAdaptationService",
    "CropAttributeTaggingService",
    "CropPreferenceService",
    "FilterCombinationEngine",
    "SmartFilterSuggestionService",
    "FilterResultProcessor"
]:
    if globals().get(_name) is not None:
        __all__.append(_name)

if crop_preference_service is not None:
    __all__.append('crop_preference_service')
if filter_combination_engine is not None:
    __all__.append('filter_combination_engine')
if smart_filter_suggestion_service is not None:
    __all__.append('smart_filter_suggestion_service')
