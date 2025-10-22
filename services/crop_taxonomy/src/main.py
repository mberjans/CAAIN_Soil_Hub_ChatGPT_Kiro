from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from src.database import get_db
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CAAIN Crop Taxonomy Service",
    description="Advanced crop filtering and variety recommendation service",
    version="1.0.0",
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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Crop Taxonomy Service on port 8007")
    # TODO: Initialize database connection pool
    # TODO: Load ML models if needed

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Crop Taxonomy Service")
    # TODO: Close database connections

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crop-taxonomy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CAAIN Crop Taxonomy Service",
        "docs": "/docs",
        "health": "/health"
    }

# Import and include routers (will be added later)
from .api import crop_routes
app.include_router(crop_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
