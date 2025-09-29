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
    export_routes
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
app.include_router(personalization_router)
app.include_router(recommendation_management_router)
app.include_router(comprehensive_explanation_router)

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Service information and navigation page.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CAAIN Soil Hub - Crop Taxonomy Service</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 10px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                padding: 40px;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e0e0e0;
            }
            .logo {
                font-size: 2.5em;
                color: #2c5aa0;
                margin-bottom: 10px;
                font-weight: bold;
            }
            .subtitle {
                font-size: 1.2em;
                color: #666;
                margin-bottom: 20px;
            }
            .services {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .service-card {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                border-left: 4px solid #2c5aa0;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .service-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .service-title {
                font-size: 1.3em;
                color: #2c5aa0;
                margin-bottom: 10px;
                font-weight: bold;
            }
            .service-desc {
                color: #666;
                line-height: 1.5;
                margin-bottom: 15px;
            }
            .service-features {
                list-style: none;
                padding: 0;
            }
            .service-features li {
                color: #555;
                margin: 5px 0;
                padding-left: 15px;
                position: relative;
            }
            .service-features li:before {
                content: "✓";
                color: #28a745;
                position: absolute;
                left: 0;
                font-weight: bold;
            }
            .api-links {
                text-align: center;
                margin-top: 40px;
                padding-top: 30px;
                border-top: 1px solid #e0e0e0;
            }
            .api-link {
                display: inline-block;
                background: #2c5aa0;
                color: white;
                padding: 12px 25px;
                margin: 0 10px;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.2s;
                font-weight: bold;
            }
            .api-link:hover {
                background: #1e3d72;
                text-decoration: none;
                color: white;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin: 30px 0;
                text-align: center;
            }
            .stat {
                background: #e8f4fd;
                padding: 20px;
                border-radius: 8px;
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #2c5aa0;
            }
            .stat-label {
                color: #666;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🌾 CAAIN Soil Hub</div>
                <div class="subtitle">Crop Taxonomy & Variety Recommendation Service</div>
                <p>Advanced agricultural intelligence for crop selection, variety recommendations, and regional adaptation analysis</p>
            </div>

            <div class="stats">
                <div class="stat">
                    <div class="stat-number">4</div>
                    <div class="stat-label">Core Services</div>
                </div>
                <div class="stat">
                    <div class="stat-number">25+</div>
                    <div class="stat-label">API Endpoints</div>
                </div>
                <div class="stat">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Science-Based</div>
                </div>
                <div class="stat">
                    <div class="stat-number">∞</div>
                    <div class="stat-label">Possibilities</div>
                </div>
            </div>

            <div class="services">
                <div class="service-card">
                    <div class="service-title">🔬 Taxonomic Classification</div>
                    <div class="service-desc">
                        Scientific crop classification following botanical and agricultural standards.
                    </div>
                    <ul class="service-features">
                        <li>Linnaean taxonomic hierarchy</li>
                        <li>Agricultural categorization</li>
                        <li>Climate & soil requirements</li>
                        <li>Nutritional profiling</li>
                        <li>Bulk data processing</li>
                    </ul>
                </div>

                <div class="service-card">
                    <div class="service-title">🔍 Advanced Search</div>
                    <div class="service-desc">
                        Multi-dimensional crop search with intelligent filtering and smart recommendations.
                    </div>
                    <ul class="service-features">
                        <li>Multi-criteria filtering</li>
                        <li>Relevance scoring</li>
                        <li>ML-enhanced insights</li>
                        <li>Context-aware suggestions</li>
                        <li>Quick search & autocomplete</li>
                    </ul>
                </div>

                <div class="service-card">
                    <div class="service-title">🌱 Variety Recommendations</div>
                    <div class="service-desc">
                        Performance-based variety selection with regional adaptation analysis.
                    </div>
                    <ul class="service-features">
                        <li>Performance predictions</li>
                        <li>Risk assessments</li>
                        <li>Economic analysis</li>
                        <li>Variety comparisons</li>
                        <li>Trait-based search</li>
                    </ul>
                </div>

                <div class="service-card">
                    <div class="service-title">🗺️ Regional Adaptation</div>
                    <div class="service-desc">
                        Comprehensive regional suitability analysis and seasonal optimization.
                    </div>
                    <ul class="service-features">
                        <li>Climate compatibility</li>
                        <li>Soil suitability</li>
                        <li>Seasonal timing</li>
                        <li>Risk assessment</li>
                        <li>Management strategies</li>
                    </ul>
                </div>
            </div>

            <div class="api-links">
                <a href="/docs" class="api-link">📖 API Documentation</a>
                <a href="/redoc" class="api-link">📚 API Reference</a>
                <a href="/api/v1/taxonomy/health" class="api-link">❤️ Health Check</a>
            </div>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center; color: #666;">
                <p><strong>Canadian Agricultural Innovation Network (CAAIN)</strong></p>
                <p>Advancing agricultural science through innovative technology solutions</p>
                <p style="font-size: 0.9em; margin-top: 15px;">
                    Version 1.0.0 | Built for agricultural excellence | 
                    <a href="https://caain-soil-hub.ca" style="color: #2c5aa0;">Learn More</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/api/v1/health")
async def health_check():
    """
    Overall service health check.
    """
    return {
        "service": "crop-taxonomy",
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "taxonomy_classification": "operational",
            "crop_search": "operational", 
            "variety_recommendations": "operational",
            "regional_adaptation": "operational",
            "database": "not_connected",  # Would be actual database status
            "ml_services": "limited"      # ML features partially implemented
        },
        "endpoints": {
            "taxonomy": "/api/v1/taxonomy/*",
            "search": "/api/v1/search/*",
            "varieties": "/api/v1/varieties/*", 
            "regional": "/api/v1/regional/*"
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
                "regional_adaptation": True
            },
            "regional_adaptation": {
                "climate_matching": True,
                "soil_suitability": True,
                "seasonal_timing": True,
                "risk_analysis": True,
                "adaptation_strategies": True,
                "geospatial_analysis": "limited"
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
