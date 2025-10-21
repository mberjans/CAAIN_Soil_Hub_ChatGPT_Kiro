"""
Crop Taxonomy Service

Main FastAPI application for comprehensive crop taxonomy, classification, 
variety recommendations, and regional adaptation services.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import sys
from pathlib import Path
import logging

from .api import (
    taxonomy_routes,
    search_routes,
    filtering_routes,
    preference_routes,
    learning_routes,
    smart_filter_routes,
    regional_routes,
    variety_routes,
    community_routes,
    filter_analytics_routes,
    explanation_routes,
    result_processor_routes,
    export_routes,
    growing_season_routes,
    economic_analysis_routes,
    market_intelligence_endpoints,
    disease_routes,
    pest_resistance_routes,
    resistance_explanation_routes,
    trial_data_routes,
    regional_performance_routes,
    scalability_routes,
    integration_routes,
    monitoring_analytics_routes,
    reporting_routes,
    monitoring_integration_routes,
    drought_resilient_routes
)

# Add services to Python path for imports
services_path = Path(__file__).parent / "services"
sys.path.insert(0, str(services_path))

# Setup performance optimizations
from .services.performance_optimization import setup_performance_optimizations

# Add src to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Initialize performance optimizations
try:
    from services.performance_optimization import setup_performance_optimizations
    setup_performance_optimizations()
except Exception as e:
    logging.error(f"Performance optimization setup error: {e}")

try:
    from api.taxonomy_routes import router as taxonomy_router
    from api.search_routes import router as search_router
    from api.variety_routes import router as variety_router
    from api.regional_routes import router as regional_router
    from api.preference_routes import router as preference_router
    from api.filter_routes import router as filter_router
    from api.learning_routes import router as learning_router
    from api.preference_recommendation_routes import router as preference_recommendation_router
    from api.filtering_routes import router as filtering_router
    from api.smart_filter_routes import router as smart_filter_router
    from api.filter_analytics_routes import router as analytics_router
    from api.personalization_routes import router as personalization_router
    from api.recommendation_management_routes import router as recommendation_management_router
    from api.comprehensive_explanation_routes import router as comprehensive_explanation_router
    from api.timing_filter_routes import router as timing_filter_router
    from api.market_intelligence_endpoints import router as market_intelligence_router
    from api.disease_routes import router as disease_router
except ImportError as e:
    logging.error(f"Import error: {e}")
    # Create placeholder routers if imports fail
    from fastapi import APIRouter
    taxonomy_router = APIRouter()
    search_router = APIRouter()
    variety_router = APIRouter()
    regional_router = APIRouter()
    preference_router = APIRouter()
    filter_router = APIRouter()
    learning_router = APIRouter()
    preference_recommendation_router = APIRouter()
    filtering_router = APIRouter()
    smart_filter_router = APIRouter()
    analytics_router = APIRouter()
    personalization_router = APIRouter()
    recommendation_management_router = APIRouter()
    comprehensive_explanation_router = APIRouter()
    timing_filter_router = APIRouter()
    market_intelligence_router = APIRouter()
    disease_router = APIRouter()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="CAAIN Soil Hub - Crop Taxonomy Service",
    description="""
    ## Comprehensive Crop Taxonomy and Variety Recommendation Service

    The Crop Taxonomy Service provides advanced agricultural intelligence through:

    ### 🌾 **Core Features**

    #### **Taxonomic Classification**
    - Botanical classification following Linnaean taxonomy
    - Agricultural categorization and crop characteristics
    - Climate and soil requirement analysis
    - Nutritional profile and quality attributes

    #### **Advanced Search & Filtering**
    - Multi-dimensional crop search (climate, soil, agricultural, economic)
    - Intelligent scoring and relevance ranking
    - Smart recommendations with ML insights
    - Context-aware suggestions and autocomplete

    #### **Variety Recommendations** 
    - Performance-based variety selection
    - Regional adaptation analysis
    - Risk assessment and mitigation strategies
    - Economic analysis and ROI projections

    #### **Regional Adaptation**
    - Climate compatibility analysis
    - Soil suitability assessment
    - Seasonal timing optimization
    - Risk factors and management strategies

    ### 📊 **Agricultural Intelligence**

    **Scientific Foundation**: Built on established agricultural science principles with comprehensive validation against extension data and expert knowledge.

    **Data Integration**: Combines taxonomic data, variety performance trials, climate information, soil surveys, and regional expertise.

    **Decision Support**: Provides actionable recommendations for farmers, agronomists, researchers, and agricultural professionals.

    ### 🎯 **Use Cases**

    - **Farmers**: Crop and variety selection for specific fields and conditions
    - **Agronomists**: Evidence-based recommendations and risk assessment
    - **Researchers**: Crop adaptation studies and breeding program support  
    - **Extension**: Educational resources and decision support tools
    - **Agribusiness**: Market analysis and product development insights

    ### 🔬 **Technical Features**

    - **RESTful API**: Complete REST API with comprehensive documentation
    - **Data Validation**: Rigorous validation against agricultural standards
    - **Performance Optimization**: Efficient search algorithms and caching
    - **Extensible Architecture**: Modular design for easy enhancement
    - **Integration Ready**: Compatible with existing agricultural systems

    ---

    **Version**: 1.0.0  
    **License**: Agricultural Research License  
    **Support**: Canadian Agricultural Innovation Network
    """,
    version="1.0.0",
    contact={
        "name": "CAAIN Soil Hub Development Team",
        "email": "support@caain-soil-hub.ca",
        "url": "https://caain-soil-hub.ca"
    },
    license_info={
        "name": "Agricultural Research License",
        "url": "https://caain-soil-hub.ca/license"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(taxonomy_routes.router)
app.include_router(search_routes.router)
app.include_router(filtering_routes.router)
app.include_router(preference_routes.router)
app.include_router(learning_routes.router)
app.include_router(smart_filter_routes.router)
app.include_router(regional_routes.router)
app.include_router(variety_routes.router)
app.include_router(community_routes.router)
app.include_router(filter_analytics_routes.router)
app.include_router(explanation_routes.router)
app.include_router(result_processor_routes.router)
app.include_router(export_routes.router)
app.include_router(growing_season_routes.router)
app.include_router(personalization_router)
app.include_router(recommendation_management_router)
app.include_router(comprehensive_explanation_router)
app.include_router(timing_filter_router)
app.include_router(economic_analysis_routes.router)
app.include_router(market_intelligence_router)
app.include_router(disease_router)
app.include_router(pest_resistance_routes.router)
app.include_router(resistance_explanation_routes.router)
app.include_router(trial_data_routes.router)
app.include_router(regional_performance_routes.router)
app.include_router(scalability_routes.router)
app.include_router(integration_routes.router)
app.include_router(monitoring_analytics_routes.router)
app.include_router(reporting_routes.router)
app.include_router(monitoring_integration_routes.router)
app.include_router(drought_resilient_routes.router)

@app.get("/")
async def root():
    """
    Root endpoint for the Crop Taxonomy Service.
    """
    return {
        "service": "CAAIN Crop Taxonomy Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "crop-taxonomy",
        "version": "1.0.0"
    }


@app.get("/api/v1/health")
async def detailed_health_check():
    """
    Overall service health check.
    """
    # Get integration status
    integration_status = "operational"
    try:
        from .services.caain_integration_service import get_integration_service
        integration_service = get_integration_service()
        integration_status_data = await integration_service.get_integration_status()
        integration_status = integration_status_data["overall_status"]
    except Exception as e:
        logger.warning(f"Could not get integration status: {e}")
        integration_status = "degraded"
    
    return {
        "service": "crop-taxonomy",
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "taxonomy_classification": "operational",
            "crop_search": "operational", 
            "variety_recommendations": "operational",
            "regional_adaptation": "operational",
            "timing_based_filtering": "operational",
            "market_intelligence": "operational",
            "disease_pressure_analysis": "operational",
            "caain_integration": integration_status,
            "database": "not_connected",  # Would be actual database status
            "ml_services": "limited"      # ML features partially implemented
        },
        "endpoints": {
            "taxonomy": "/api/v1/taxonomy/*",
            "search": "/api/v1/search/*",
            "varieties": "/api/v1/varieties/*", 
            "regional": "/api/v1/regional/*",
            "timing_filter": "/api/v1/timing-filter/*",
            "market_intelligence": "/api/v1/market-intelligence/*",
            "disease_pressure": "/api/v1/disease-pressure/*",
            "integration": "/api/v1/integration/*"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        }
    }

@app.get("/api/v1/info")
async def service_info():
    """
    Detailed service information and capabilities.
    """
    return {
        "service_name": "CAAIN Soil Hub - Crop Taxonomy Service",
        "version": "1.0.0",
        "description": "Comprehensive crop taxonomy, variety recommendations, and regional adaptation service",
        "capabilities": {
            "taxonomic_classification": {
                "botanical_hierarchy": True,
                "agricultural_categories": True,
                "climate_requirements": True,
                "soil_preferences": True,
                "nutritional_profiles": True,
                "bulk_processing": True
            },
            "crop_search": {
                "multi_criteria_filtering": True,
                "intelligent_scoring": True,
                "ml_recommendations": "limited",
                "context_awareness": True,
                "quick_search": True,
                "autocomplete": True
            },
            "variety_recommendations": {
                "performance_prediction": True,
                "risk_assessment": True,
                "economic_analysis": True,
                "variety_comparison": True,
                "trait_based_search": True,
                "regional_adaptation": True,
                "timing_based_filtering": True,
                "market_intelligence": True,
                "disease_resistance_analysis": True
            },
            "regional_adaptation": {
                "climate_matching": True,
                "soil_suitability": True,
                "seasonal_timing": True,
                "risk_analysis": True,
                "adaptation_strategies": True,
                "geospatial_analysis": "limited"
            },
            "disease_pressure_analysis": {
                "regional_disease_mapping": True,
                "disease_severity_assessment": True,
                "variety_resistance_analysis": True,
                "management_recommendations": True,
                "timing_guidance": True,
                "disease_forecasting": True,
                "historical_trend_analysis": True,
                "risk_assessment": True
            }
        },
        "data_sources": {
            "taxonomic_data": "Integrated botanical and agricultural databases",
            "variety_data": "Breeding institution and trial data",
            "climate_data": "Historical weather and climate models", 
            "soil_data": "Soil surveys and field measurements",
            "performance_data": "Multi-year, multi-location trials"
        },
        "api_features": {
            "rest_api": True,
            "json_responses": True,
            "error_handling": True,
            "input_validation": True,
            "rate_limiting": False,  # Not implemented yet
            "authentication": False,  # Not implemented yet
            "caching": "basic"
        },
        "contact": {
            "organization": "Canadian Agricultural Innovation Network",
            "email": "support@caain-soil-hub.ca",
            "website": "https://caain-soil-hub.ca"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Crop Taxonomy Service...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        reload=True  # Enable for development
    )
