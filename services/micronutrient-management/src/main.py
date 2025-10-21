from fastapi import FastAPI
import uvicorn

from .api import application_routes, timing_routes

app = FastAPI(title="Micronutrient Management Service")

app.include_router(application_routes.router)
app.include_router(timing_routes.router)

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "micronutrient-management"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8009)
