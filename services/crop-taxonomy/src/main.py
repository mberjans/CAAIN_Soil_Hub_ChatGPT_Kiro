import logging
import sys
from logging import handlers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure comprehensive logging
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Set up comprehensive logging configuration for the application.
    
    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to log to a file as well
    """
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters for different log levels
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler with detailed formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(detailed_formatter)
    
    # Add console handler to the logger
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5 backups
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Also configure the uvicorn loggers to use the same format
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    uvicorn_logger.addHandler(console_handler)
    if log_file:
        uvicorn_logger.addHandler(file_handler)
    uvicorn_logger.setLevel(getattr(logging, log_level.upper()))
    
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.addHandler(console_handler)
    if log_file:
        access_logger.addHandler(file_handler)
    access_logger.setLevel(getattr(logging, log_level.upper()))
    
    error_logger = logging.getLogger("uvicorn.error")
    error_logger.handlers.clear()
    error_logger.addHandler(console_handler)
    if log_file:
        error_logger.addHandler(file_handler)
    error_logger.setLevel(getattr(logging, log_level.upper()))

# Set up logging with INFO level and no file logging by default
setup_logging(log_level="INFO")

# Get the main logger for the application
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
# from .api import crop_routes
# app.include_router(crop_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
