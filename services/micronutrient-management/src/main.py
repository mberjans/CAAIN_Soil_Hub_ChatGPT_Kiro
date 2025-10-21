from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
import logging

from ..models.micronutrient_models import (
    YieldPredictionRequest,
    YieldPredictionResponse,
    EconomicReturnPredictionRequest,
    EconomicReturnPredictionResponse,
    FarmContext,
    MicronutrientApplication,
    CropDetails
)
from ..services.yield_prediction_service import YieldPredictionService
from ..services.economic_prediction_service import EconomicPredictionService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Micronutrient Management Service",
    description="API for predicting yield response and economic return from micronutrient applications.",
    version="1.0.0",
)

# Dependency injection for services
async def get_yield_prediction_service() -> YieldPredictionService:
    return YieldPredictionService()

async def get_economic_prediction_service() -> EconomicPredictionService:
    return EconomicPredictionService()

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "micronutrient-management"}

@app.post("/predict-yield", response_model=YieldPredictionResponse, tags=["Yield Prediction"])
async def predict_yield(
    request: YieldPredictionRequest,
    yield_service: YieldPredictionService = Depends(get_yield_prediction_service)
):
    """
    Predicts the yield response to a micronutrient application.

    This endpoint takes detailed farm context, crop details, and micronutrient application
    information to estimate the potential yield increase.
    """
    try:
        # --- Integration with other services would happen here ---
        # Example: Fetch more detailed soil data from soil-ph-management service
        # Example: Fetch real-time climate data from weather-impact-analysis service
        # Example: Validate crop variety against crop-taxonomy service

        response = await yield_service.predict_yield_response(request)
        return response
    except Exception as e:
        logger.error(f"Error predicting yield: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to predict yield: {str(e)}")

@app.post("/predict-economic-return", response_model=EconomicReturnPredictionResponse, tags=["Economic Prediction"])
async def predict_economic_return(
    request: EconomicReturnPredictionRequest,
    economic_service: EconomicPredictionService = Depends(get_economic_prediction_service)
):
    """
    Predicts the economic return and ROI of a micronutrient application.

    This endpoint uses predicted yield response, market prices, and application costs
    to calculate the financial viability of the micronutrient application.
    """
    try:
        # --- Integration with other services would happen here ---
        # Example: Fetch real-time market prices from market-price-integration service
        # (For this placeholder, market price is part of CropDetails in the request)

        response = await economic_service.predict_economic_return(request)
        return response
    except Exception as e:
        logger.error(f"Error predicting economic return: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to predict economic return: {str(e)}")