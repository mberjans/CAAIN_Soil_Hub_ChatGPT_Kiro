"""
Crop Taxonomy API Routes

FastAPI routes for crop taxonomy classification, search, variety recommendations,
and regional adaptation services.
"""

from .taxonomy_routes import router as taxonomy_router
from .search_routes import router as search_router  
from .variety_routes import router as variety_router
from .regional_routes import router as regional_router
from .preference_routes import router as preference_router
from .learning_routes import router as learning_router
from .smart_filter_routes import router as smart_filter_router
from .personalization_routes import router as personalization_router
from .comprehensive_explanation_routes import router as comprehensive_explanation_router
from .timing_filter_routes import router as timing_filter_router
from .economic_analysis_routes import router as economic_analysis_router
from .pest_resistance_routes import router as pest_resistance_router
from .resistance_explanation_routes import router as resistance_explanation_router
from .trial_data_routes import router as trial_data_router
from .regional_performance_routes import router as regional_performance_router
from .drought_resilient_routes import router as drought_resilient_router

__all__ = [
    "taxonomy_router",
    "search_router", 
    "variety_router",
    "regional_router",
    "preference_router",
    "learning_router",
    "smart_filter_router",
    "personalization_router",
    "comprehensive_explanation_router",
    "timing_filter_router",
    "economic_analysis_router",
    "pest_resistance_router",
    "resistance_explanation_router",
    "trial_data_router",
    "regional_performance_router",
    "drought_resilient_router"
]
