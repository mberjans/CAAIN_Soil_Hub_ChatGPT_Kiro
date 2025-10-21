from fastapi import FastAPI

app = FastAPI(
    title="Micronutrient Management Service",
    description="Service for managing micronutrient data and recommendations.",
    version="0.1.0",
)

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}
