class FertilizerPriceTracker:
    """
    A service class for tracking fertilizer prices using a provided price provider.
    """

    def __init__(self, price_provider):
        """
        Initialize the FertilizerPriceTracker with a price provider.

        Args:
            price_provider: An object that implements an async get_prices method
                           to fetch prices for a list of fertilizer names.
        """
        if not price_provider:
            raise ValueError("Price provider is required")
        self.price_provider = price_provider

    async def fetch_current_prices(self, fertilizer_names):
        """
        Fetch current prices for the given list of fertilizer names.

        Args:
            fertilizer_names (list): List of fertilizer names to fetch prices for.

        Returns:
            dict: A dictionary mapping fertilizer names to their current prices.
                  Returns an empty dict if no names provided or on error.

        Raises:
            No exceptions are raised; errors are handled internally.
        """
        if not fertilizer_names:
            return {}

        try:
            prices = await self.price_provider.get_prices(fertilizer_names)
            return prices
        except Exception as e:
            # Handle provider failures gracefully
            print(f"Error fetching prices for {fertilizer_names}: {str(e)}")
            return {}