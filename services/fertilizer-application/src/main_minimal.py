from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import only the essential routes for testing
from src.api.fertilizer_routes import router as fertilizer_router
from src.api.equipment_routes import router as equipment_router
from src.api.guidance_routes import router as guidance_router
from src.api.economic_optimization_routes import router as economic_router

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("Starting AFAS Fertilizer Application Service (Minimal)...")
    
    try:
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down AFAS Fertilizer Application Service...")


app = FastAPI(
    title="AFAS Fertilizer Application Service (Minimal)",
    description="Minimal fertilizer application method selection service for testing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the essential routes for testing
app.include_router(fertilizer_router, prefix="/api/v1", tags=["fertilizer-application-methods"])
app.include_router(equipment_router, prefix="/api/v1/equipment", tags=["equipment-assessment"])
app.include_router(guidance_router, prefix="/api/v1", tags=["guidance"])
app.include_router(economic_router, prefix="/api/v1/cost-analysis", tags=["cost-analysis"])

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "service": "fertilizer-application-minimal",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "fertilizer_application_method_recommendations",
            "method_comparison",
            "application_guidance",
            "timing_optimization"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Fertilizer Application Service (Minimal) is running",
        "service": "fertilizer-application-minimal",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("FERTILIZER_APPLICATION_PORT", 8008))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)