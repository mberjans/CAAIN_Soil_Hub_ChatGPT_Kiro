from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import structlog

from .api.routes import router

load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="AFAS Data Integration Service",
    description="External agricultural data source integration and management service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
    return {
        "service": "data-integration",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/weather/current",
            "/api/v1/weather/forecast", 
            "/api/v1/weather/agricultural-metrics",
            "/api/v1/soil/survey-data",
            "/api/v1/crops/varieties/{crop_name}",
            "/api/v1/market/prices"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Data Integration Service is running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting AFAS Data Integration Service")
    try:
        # Initialize the ingestion service
        from .services.ingestion_service import get_ingestion_service
        await get_ingestion_service()
        logger.info("Data ingestion framework initialized")
    except Exception as e:
        logger.error("Failed to initialize ingestion service", error=str(e))
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AFAS Data Integration Service")
    try:
        # Shutdown the ingestion service
        from .services.ingestion_service import shutdown_ingestion_service
        await shutdown_ingestion_service()
        logger.info("Data ingestion framework shutdown complete")
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))

if __name__ == "__main__":
    port = int(os.getenv("DATA_INTEGRATION_PORT", 8003))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)