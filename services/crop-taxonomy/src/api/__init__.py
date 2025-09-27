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

__all__ = [
    "taxonomy_router",
    "search_router", 
    "variety_router",
    "regional_router",
    "preference_router",
    "learning_router"
]
