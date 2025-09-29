"""
Drought Management Service

FastAPI microservice for drought assessment, moisture conservation,
and water management following agricultural best practices.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

try:
    from .api.routes import router
    from .services.drought_assessment_service import DroughtAssessmentService
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from api.routes import router
    from services.drought_assessment_service import DroughtAssessmentService

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AFAS Drought Management Service",
    description="Agricultural drought assessment, moisture conservation, and water management service with weather and soil integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Service instances for health checks
drought_assessment_service = None
moisture_conservation_service = None
drought_monitoring_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global drought_assessment_service, moisture_conservation_service, drought_monitoring_service
    try:
        logger.info("Initializing Drought Management Service...")
        
        # Initialize core services
        drought_assessment_service = DroughtAssessmentService()
        await drought_assessment_service.initialize()
        
        # Import and initialize other services
        from .services.moisture_conservation_service import MoistureConservationService
        from .services.drought_monitoring_service import DroughtMonitoringService
        
        moisture_conservation_service = MoistureConservationService()
        await moisture_conservation_service.initialize()
        
        drought_monitoring_service = DroughtMonitoringService()
        await drought_monitoring_service.initialize()
        
        logger.info("Drought Management Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Drought Management Service: {str(e)}")
        # Don't fail startup, but log the error for monitoring
        pass

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global drought_assessment_service, moisture_conservation_service, drought_monitoring_service
    try:
        if drought_assessment_service:
            await drought_assessment_service.cleanup()
        if moisture_conservation_service:
            await moisture_conservation_service.cleanup()
        if drought_monitoring_service:
            await drought_monitoring_service.cleanup()
        logger.info("Drought Management Service shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    global drought_assessment_service, moisture_conservation_service, drought_monitoring_service
    
    service_healthy = True
    service_status = "healthy"
    
    # Check each service component
    components = {}
    
    if drought_assessment_service:
        try:
            components["drought_assessment"] = "healthy"
        except Exception as e:
            logger.error(f"Drought assessment service health check failed: {str(e)}")
            components["drought_assessment"] = "unhealthy"
            service_healthy = False
    else:
        components["drought_assessment"] = "not_initialized"
        service_healthy = False
    
    if moisture_conservation_service:
        try:
            components["moisture_conservation"] = "healthy"
        except Exception as e:
            logger.error(f"Moisture conservation service health check failed: {str(e)}")
            components["moisture_conservation"] = "unhealthy"
            service_healthy = False
    else:
        components["moisture_conservation"] = "not_initialized"
        service_healthy = False
    
    if drought_monitoring_service:
        try:
            components["drought_monitoring"] = "healthy"
        except Exception as e:
            logger.error(f"Drought monitoring service health check failed: {str(e)}")
            components["drought_monitoring"] = "unhealthy"
            service_healthy = False
    else:
        components["drought_monitoring"] = "not_initialized"
        service_healthy = False
    
    if not service_healthy:
        service_status = "unhealthy"
    
    return {
        "service": "drought-management",
        "status": service_status,
        "version": "1.0.0",
        "description": "Agricultural drought assessment, moisture conservation, and water management service",
        "timestamp": datetime.utcnow().isoformat(),
        "components": components,
        "integration": {
            "weather_data": "available",
            "soil_data": "available",
            "crop_data": "available"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Drought Management Service is running",
        "service": "drought-management",
        "version": "1.0.0",
        "description": "Agricultural drought assessment, moisture conservation, and water management with weather and soil integration",
        "endpoints": {
            "drought_assessment": "/api/v1/drought/assess",
            "moisture_conservation": "/api/v1/drought/conservation",
            "drought_monitoring": "/api/v1/drought/monitor",
            "water_savings": "/api/v1/drought/water-savings",
            "drought_risk": "/api/v1/drought/risk-assessment",
            "health": "/health",
            "docs": "/docs"
        },
        "features": [
            "drought_risk_assessment",
            "moisture_conservation_recommendations",
            "water_savings_calculations",
            "drought_monitoring_alerts",
            "weather_integration",
            "soil_moisture_modeling",
            "crop_water_requirements"
        ],
        "integration": {
            "weather_services": "NOAA, OpenWeatherMap integration",
            "soil_data": "Soil moisture, texture, organic matter analysis",
            "crop_data": "Water requirements, drought tolerance, growth stages"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("DROUGHT_MANAGEMENT_PORT", 8007))
    logger.info(f"Starting Drought Management Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)