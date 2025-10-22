#!/usr/bin/env python3
"""
Main Application
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

from fastapi import FastAPI
from datetime import datetime
from src.api import weather_routes

# Create FastAPI app instance
app = FastAPI(
    title="Weather Impact Analysis Service",
    description="Service for analyzing weather data and its impact on agricultural operations",
    version="1.0.0"
)

# Include weather routes
app.include_router(weather_routes.router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Weather Impact Analysis Service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)