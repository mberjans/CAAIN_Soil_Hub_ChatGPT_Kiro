from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from api.application_routes import router as application_router
from api.method_routes import router as method_router
from api.guidance_routes import router as guidance_router
from database.fertilizer_db import initialize_database, shutdown_database

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
    logger.info("Starting AFAS Fertilizer Application Service...")
    
    try:
        # Initialize database connections
        await initialize_database()
        logger.info("Database connections initialized")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down AFAS Fertilizer Application Service...")
        await shutdown_database()
        logger.info("Database connections closed")


app = FastAPI(
    title="AFAS Fertilizer Application Service",
    description="Comprehensive fertilizer application method selection, equipment assessment, and guidance service",
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

# Include API routes
app.include_router(application_router, prefix="/api/v1", tags=["application"])
app.include_router(method_router, prefix="/api/v1", tags=["methods"])
app.include_router(guidance_router, prefix="/api/v1", tags=["guidance"])

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "service": "fertilizer-application",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "application_method_selection",
            "equipment_assessment",
            "cost_analysis",
            "application_guidance",
            "method_optimization",
            "equipment_compatibility",
            "farm_size_assessment"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Fertilizer Application Service is running",
        "service": "fertilizer-application",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("FERTILIZER_APPLICATION_PORT", 8008))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)