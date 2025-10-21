from fastapi import FastAPI
from .api import micronutrient_routes

app = FastAPI(title="Micronutrient Management Service")

app.include_router(micronutrient_routes.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
