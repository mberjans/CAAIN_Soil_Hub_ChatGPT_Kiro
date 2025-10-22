from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Location Management Service",
    description="Farm location management API with geospatial capabilities",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint for the service"""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "message": "Location Management Service is running"}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        status_code=200,
        content={"message": "Location Management Service", "version": "1.0.0"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
