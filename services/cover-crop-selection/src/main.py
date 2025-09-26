"""
Cover Crop Selection Service

FastAPI microservice for cover crop selection and recommendations
following agricultural best practices and soil conservation principles.
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
    from .services.cover_crop_selection_service import CoverCropSelectionService
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from api.routes import router
    from services.cover_crop_selection_service import CoverCropSelectionService

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AFAS Cover Crop Selection Service",
    description="Agricultural cover crop selection and recommendation service with climate zone and soil integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Service instance for health checks
cover_crop_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global cover_crop_service
    try:
        logger.info("Initializing Cover Crop Selection Service...")
        cover_crop_service = CoverCropSelectionService()
        await cover_crop_service.initialize()
        logger.info("Cover Crop Selection Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Cover Crop Selection Service: {str(e)}")
        # Don't fail startup, but log the error for monitoring
        pass

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global cover_crop_service
    try:
        if cover_crop_service:
            await cover_crop_service.cleanup()
        logger.info("Cover Crop Selection Service shutdown completed")
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
    global cover_crop_service
    
    service_healthy = True
    service_status = "healthy"
    
    if cover_crop_service:
        try:
            service_healthy = await cover_crop_service.health_check()
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            service_healthy = False
            service_status = "unhealthy"
    else:
        service_healthy = False
        service_status = "not_initialized"
    
    return {
        "service": "cover-crop-selection",
        "status": service_status,
        "version": "1.0.0",
        "description": "Agricultural cover crop selection and recommendation service",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "cover_crop_service": "healthy" if service_healthy else "unhealthy",
            "climate_integration": "available",
            "soil_integration": "available"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Cover Crop Selection Service is running",
        "service": "cover-crop-selection",
        "version": "1.0.0",
        "description": "Agricultural cover crop selection with climate zone and soil integration",
        "endpoints": {
            "cover_crop_selection": "/api/v1/cover-crops/select",
            "species_lookup": "/api/v1/cover-crops/species",
            "seasonal_recommendations": "/api/v1/cover-crops/seasonal",
            "soil_improvement": "/api/v1/cover-crops/soil-improvement",
            "rotation_integration": "/api/v1/cover-crops/rotation",
            "health": "/health",
            "docs": "/docs"
        },
        "integration": {
            "climate_zones": "USDA Hardiness Zones with Köppen classification",
            "soil_data": "pH, organic matter, drainage, texture analysis",
            "agricultural_practices": "Conservation tillage, nitrogen fixation, erosion control"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("COVER_CROP_SERVICE_PORT", 8006))
    logger.info(f"Starting Cover Crop Selection Service on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)