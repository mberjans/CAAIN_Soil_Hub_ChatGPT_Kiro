import random
import asyncio
from typing import Optional


class MockPriceProvider:
    """
    Mock price provider for fertilizer optimization service.
    Provides simulated price data for common fertilizers with random variation.
    """

    def __init__(self):
        """Initialize base prices for common fertilizers (price per kg)."""
        self.base_prices = {
            'Urea': 0.50,
            'DAP': 0.60,  # Diammonium Phosphate
            'MAP': 0.55,  # Monoammonium Phosphate
            'Potash': 0.45,
            'Ammonium Nitrate': 0.40,
            'Superphosphate': 0.35,
            'Calcium Nitrate': 0.65,
            'Magnesium Sulfate': 0.30,
        }

    async def get_current_price(self, fertilizer_name: str) -> Optional[dict]:
        """
        Get the current price for a given fertilizer with ±10% random variation.

        Args:
            fertilizer_name (str): Name of the fertilizer.

        Returns:
            Optional[dict]: Price data dict if fertilizer exists, None otherwise.
        """
        if fertilizer_name not in self.base_prices:
            return None

        base_price = self.base_prices[fertilizer_name]
        # Apply ±10% random variation
        variation = random.uniform(-0.1, 0.1)
        current_price = base_price * (1 + variation)

        # Simulate async operation (e.g., API call delay)
        await asyncio.sleep(0.01)

        return {
            "price": round(current_price, 2),
            "unit": "kg",
            "region": "US",
            "currency": "USD"
        }