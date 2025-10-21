from fastapi import FastAPI
from .api.application_routes import router as application_router

app = FastAPI(
    title="Micronutrient Application Service",
    description="Service for providing comprehensive micronutrient application method and timing recommendations.",
    version="1.0.0",
)

app.include_router(application_router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Micronutrient Application Service is running. Visit /docs for API documentation."}