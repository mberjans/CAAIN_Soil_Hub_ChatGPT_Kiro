from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from datetime import datetime
from ..services.price_tracker import FertilizerPriceTracker
from ..providers.mock_price_provider import MockPriceProvider
from ..schemas.optimization_schemas import PriceData
from pydantic import BaseModel

# Create the router
router = APIRouter()

# Response model for current prices
class CurrentPricesResponse(BaseModel):
    prices: Dict[str, PriceData]

# Dependency to get the price tracker service
def get_price_tracker() -> FertilizerPriceTracker:
    """
    Dependency to provide the FertilizerPriceTracker instance.
    """
    provider = MockPriceProvider()
    return FertilizerPriceTracker(provider)

@router.get("/prices/fertilizer-current", response_model=CurrentPricesResponse)
async def get_current_fertilizer_prices(
    fertilizer_names: Optional[List[str]] = Query(None, description="List of fertilizer names to fetch prices for. If not provided, fetches for all available fertilizers."),
    tracker: FertilizerPriceTracker = Depends(get_price_tracker)
):
    """
    Get current fertilizer prices for the specified fertilizers.

    - **fertilizer_names**: Optional list of fertilizer names. If not provided, returns prices for all available fertilizers.
    - **Returns**: A dictionary mapping fertilizer names to their current price data.
    - **Raises**: HTTPException if there's an error fetching prices.
    """
    try:
        # If no fertilizer names provided, use all available from the provider
        if not fertilizer_names:
            fertilizer_names = list(MockPriceProvider().base_prices.keys())

        # Fetch prices using the service
        prices = await tracker.fetch_current_prices(fertilizer_names)

        # Convert to PriceData objects
        price_data_dict = {}
        for name, data in prices.items():
            if data:
                # Create PriceData with current timestamp
                price_data = PriceData(
                    fertilizer_name=name,
                    price=data["price"],
                    source=data.get("source", "mock"),
                    date=datetime.utcnow()
                )
                price_data_dict[name] = price_data

        return CurrentPricesResponse(prices=price_data_dict)

    except Exception as e:
        # Handle service failures with proper error response
        raise HTTPException(status_code=500, detail=f"Error fetching fertilizer prices: {str(e)}")