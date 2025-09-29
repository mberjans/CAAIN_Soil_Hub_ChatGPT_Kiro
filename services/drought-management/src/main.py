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
soil_assessment_service = None
soil_weather_integration_service = None
practice_effectiveness_service = None
cover_crop_mulch_optimization_service = None
water_usage_monitoring_service = None
water_usage_reporting_service = None
farm_infrastructure_service = None
equipment_optimization_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global drought_assessment_service, moisture_conservation_service, drought_monitoring_service, soil_assessment_service, soil_weather_integration_service, practice_effectiveness_service, cover_crop_mulch_optimization_service, water_usage_monitoring_service, water_usage_reporting_service, farm_infrastructure_service, equipment_optimization_service
    try:
        logger.info("Initializing Drought Management Service...")
        
        # Initialize core services
        drought_assessment_service = DroughtAssessmentService()
        await drought_assessment_service.initialize()
        
        # Import and initialize other services
        from .services.moisture_conservation_service import MoistureConservationService
        from .services.drought_monitoring_service import DroughtMonitoringService
        from .services.soil_assessment_service import SoilManagementAssessmentService
        from .services.soil_weather_service import SoilWeatherIntegrationService
        from .services.practice_effectiveness_service import PracticeEffectivenessService
        
        moisture_conservation_service = MoistureConservationService()
        await moisture_conservation_service.initialize()
        
        drought_monitoring_service = DroughtMonitoringService()
        await drought_monitoring_service.initialize()
        
        soil_assessment_service = SoilManagementAssessmentService()
        await soil_assessment_service.initialize()
        
        soil_weather_integration_service = SoilWeatherIntegrationService()
        await soil_weather_integration_service.initialize()
        
        practice_effectiveness_service = PracticeEffectivenessService()
        await practice_effectiveness_service.initialize()
        
        # Initialize cover crop and mulch optimization service
        from .services.cover_crop_mulch_optimization_service import CoverCropMulchOptimizationService
        cover_crop_mulch_optimization_service = CoverCropMulchOptimizationService()
        await cover_crop_mulch_optimization_service.initialize()
        
        # Initialize water usage monitoring services
        from .services.water_usage_monitoring_service import WaterUsageMonitoringService
        from .services.water_usage_reporting_service import WaterUsageReportingService
        
        water_usage_monitoring_service = WaterUsageMonitoringService()
        await water_usage_monitoring_service.initialize()
        
        water_usage_reporting_service = WaterUsageReportingService()
        await water_usage_reporting_service.initialize()
        
        # Initialize farm infrastructure assessment service
        from .services.infrastructure_service import FarmInfrastructureAssessmentService
        farm_infrastructure_service = FarmInfrastructureAssessmentService()
        await farm_infrastructure_service.initialize()
        
        # Initialize equipment optimization service
        from .services.equipment_optimization_service import EquipmentOptimizationService
        equipment_optimization_service = EquipmentOptimizationService()
        await equipment_optimization_service.initialize()
        
        logger.info("Drought Management Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Drought Management Service: {str(e)}")
        # Don't fail startup, but log the error for monitoring
        pass

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global drought_assessment_service, moisture_conservation_service, drought_monitoring_service, soil_assessment_service, soil_weather_integration_service, practice_effectiveness_service, cover_crop_mulch_optimization_service, water_usage_monitoring_service, water_usage_reporting_service, farm_infrastructure_service, equipment_optimization_service
    try:
        if drought_assessment_service:
            await drought_assessment_service.cleanup()
        if moisture_conservation_service:
            await moisture_conservation_service.cleanup()
        if drought_monitoring_service:
            await drought_monitoring_service.cleanup()
        if soil_assessment_service:
            await soil_assessment_service.cleanup()
        if soil_weather_integration_service:
            await soil_weather_integration_service.cleanup()
        if practice_effectiveness_service:
            await practice_effectiveness_service.cleanup()
        if cover_crop_mulch_optimization_service:
            await cover_crop_mulch_optimization_service.cleanup()
        if water_usage_monitoring_service:
            await water_usage_monitoring_service.cleanup()
        if water_usage_reporting_service:
            await water_usage_reporting_service.cleanup()
        if farm_infrastructure_service:
            await farm_infrastructure_service.cleanup()
        if equipment_optimization_service:
            await equipment_optimization_service.cleanup()
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
    global drought_assessment_service, moisture_conservation_service, drought_monitoring_service, soil_assessment_service, practice_effectiveness_service, cover_crop_mulch_optimization_service, farm_infrastructure_service, equipment_optimization_service
    
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
    
    if soil_assessment_service:
        try:
            components["soil_assessment"] = "healthy"
        except Exception as e:
            logger.error(f"Soil assessment service health check failed: {str(e)}")
            components["soil_assessment"] = "unhealthy"
            service_healthy = False
    else:
        components["soil_assessment"] = "not_initialized"
        service_healthy = False
    
    if soil_weather_integration_service:
        try:
            components["soil_weather_integration"] = "healthy"
        except Exception as e:
            logger.error(f"Soil-weather integration service health check failed: {str(e)}")
            components["soil_weather_integration"] = "unhealthy"
            service_healthy = False
    else:
        components["soil_weather_integration"] = "not_initialized"
        service_healthy = False
    
    if practice_effectiveness_service:
        try:
            components["practice_effectiveness"] = "healthy"
        except Exception as e:
            logger.error(f"Practice effectiveness service health check failed: {str(e)}")
            components["practice_effectiveness"] = "unhealthy"
            service_healthy = False
    else:
        components["practice_effectiveness"] = "not_initialized"
        service_healthy = False
    
    if cover_crop_mulch_optimization_service:
        try:
            components["cover_crop_mulch_optimization"] = "healthy"
        except Exception as e:
            logger.error(f"Cover crop mulch optimization service health check failed: {str(e)}")
            components["cover_crop_mulch_optimization"] = "unhealthy"
            service_healthy = False
    else:
        components["cover_crop_mulch_optimization"] = "not_initialized"
        service_healthy = False
    
    if farm_infrastructure_service:
        try:
            components["farm_infrastructure"] = "healthy"
        except Exception as e:
            logger.error(f"Farm infrastructure service health check failed: {str(e)}")
            components["farm_infrastructure"] = "unhealthy"
            service_healthy = False
    else:
        components["farm_infrastructure"] = "not_initialized"
        service_healthy = False
    
    if equipment_optimization_service:
        try:
            components["equipment_optimization"] = "healthy"
        except Exception as e:
            logger.error(f"Equipment optimization service health check failed: {str(e)}")
            components["equipment_optimization"] = "unhealthy"
            service_healthy = False
    else:
        components["equipment_optimization"] = "not_initialized"
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
            "soil_assessment": "/api/v1/drought/soil-assessment",
            "practice_effectiveness": "/api/v1/drought/practice-effectiveness",
            "cover_crop_mulch_optimization": "/api/v1/optimization",
            "farm_infrastructure": "/api/v1/infrastructure",
            "equipment_optimization": "/api/v1/equipment-optimization",
            "health": "/health",
            "docs": "/docs"
        },
        "features": [
            "drought_risk_assessment",
            "moisture_conservation_recommendations",
            "water_savings_calculations",
            "drought_monitoring_alerts",
            "soil_management_assessment",
            "weather_integration",
            "soil_moisture_modeling",
            "crop_water_requirements",
            "practice_effectiveness_tracking",
            "performance_measurement_collection",
            "effectiveness_validation",
            "adaptive_recommendations",
            "cover_crop_species_optimization",
            "mulch_material_optimization",
            "comprehensive_optimization",
            "timing_optimization",
            "performance_insights",
            "farm_infrastructure_assessment",
            "equipment_inventory_management",
            "capacity_assessment",
            "upgrade_recommendations",
            "equipment_optimization",
            "investment_planning",
            "cost_benefit_analysis",
            "financing_options",
            "risk_assessment"
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