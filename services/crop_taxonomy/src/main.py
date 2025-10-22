from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models.filtering_models import Base # Assuming Base is defined here or in a common models file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost/test_crop_taxonomy" # Use test DB for now
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables checked/created.")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Crop Taxonomy Service")
    # No explicit engine shutdown needed for most applications,
    # as connections are managed by the pool.

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

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import and include routers
from src.api import crop_routes
app.include_router(crop_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
