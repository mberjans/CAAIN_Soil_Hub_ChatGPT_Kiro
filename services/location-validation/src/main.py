"""
Location Validation Service Main Application
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI application for location validation service.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from api.routes import router, location_management_router
from api.agricultural_analysis_routes import router as agricultural_analysis_router
from api.agricultural_intelligence_routes import router as agricultural_intelligence_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AFAS Location Validation Service",
    description="Location validation service for the Autonomous Farm Advisory System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for monitoring and debugging."""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Include API routes
app.include_router(router)  # Location validation routes
app.include_router(location_management_router)  # Location management routes
app.include_router(agricultural_analysis_router)  # Agricultural analysis routes

# Import and include field management routes
from api.field_routes import router as field_management_router
app.include_router(field_management_router)  # Field management routes

# Import and include field productivity analysis routes
from api.field_productivity_routes import router as field_productivity_router
app.include_router(field_productivity_router)  # Field productivity analysis routes

# Import and include field optimization routes
from api.field_optimization_routes import router as field_optimization_router
app.include_router(field_optimization_router)  # Field optimization routes

# Import and include mobile location routes
from api.mobile_location_routes import router as mobile_location_router
app.include_router(mobile_location_router)  # Mobile location features routes

# Import and include security routes
from api.security_routes import router as security_router
app.include_router(security_router)  # Location security and privacy routes

# Include agricultural intelligence routes
app.include_router(agricultural_intelligence_router)  # Agricultural intelligence routes

# Import and include production monitoring routes
from api.production_monitoring_routes import router as production_monitoring_router
app.include_router(production_monitoring_router)  # Production monitoring and analytics routes

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "AFAS Location Validation Service",
        "version": "1.0.0",
        "description": "Validates farm locations for agricultural suitability",
        "endpoints": {
            "coordinate_validation": "/api/v1/validation/coordinates",
            "agricultural_validation": "/api/v1/validation/agricultural",
            "health_check": "/api/v1/validation/health",
            "location_management": "/api/v1/locations/",
            "agricultural_analysis": "/api/v1/fields/{field_id}/analysis-summary",
            "mobile_location": "/api/v1/mobile/",
            "location_security": "/api/v1/security/",
            "agricultural_intelligence": "/api/v1/agricultural-intelligence/",
            "production_monitoring": "/api/v1/monitoring/",
            "documentation": "/docs"
        },
        "agricultural_features": [
            "GPS coordinate range validation",
            "Agricultural area detection",
            "Climate zone identification",
            "Ocean/water body detection",
            "Agricultural suitability scoring",
            "Geographic information lookup",
            "Farm location management",
            "Location CRUD operations",
            "Agricultural context validation",
            "Dependency checking and safe deletion",
            "Advanced mapping features and agricultural overlays",
            "Slope analysis and topographic assessment",
            "Drainage evaluation and flood risk assessment",
            "Field accessibility evaluation",
            "Soil survey data integration (SSURGO)",
            "Watershed information and water management",
            "Mobile field boundary recording with GPS tracking",
            "Field photo capture with automatic geotagging",
            "Voice notes for field annotations",
            "Offline field mapping with background synchronization",
            "Enhanced mobile UX with touch gestures and haptic feedback",
            "Comprehensive location data security and encryption",
            "Access control and audit logging for location data",
            "Location data anonymization and privacy protection",
            "GDPR compliance for location data management",
            "Security monitoring and breach detection",
            "Location-based agricultural intelligence and insights",
            "Regional best practices and recommendations",
            "Local expert recommendations and insights",
            "Peer farmer insights and experiences",
            "Market insights and opportunities",
            "Success patterns and regional adaptations",
            "Location-specific personalization and optimization",
            "Production monitoring and optimization",
            "Location accuracy monitoring and validation",
            "Service performance tracking and optimization",
            "User experience analytics and improvement",
            "Automated optimization recommendations",
            "Real-time monitoring dashboards and alerts",
            "Comprehensive analytics and reporting",
            "Prometheus metrics integration",
            "Business intelligence and KPI tracking"
        ]
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "error_code": "INTERNAL_SERVER_ERROR",
                "error_message": "An unexpected error occurred",
                "agricultural_context": "Unable to process location validation request",
                "suggested_actions": [
                    "Try the request again",
                    "Check that coordinates are valid",
                    "Contact support if the problem persists"
                ]
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )