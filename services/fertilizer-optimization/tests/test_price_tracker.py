import pytest
from src.providers.mock_price_provider import MockPriceProvider

@pytest.mark.asyncio
async def test_mock_price_provider():
    """Test MockPriceProvider returns correct mock price data for fertilizers."""
    provider = MockPriceProvider()
    
    # Test with a valid fertilizer
    price_data = await provider.get_current_price("Urea")
    assert price_data is not None
    assert "price" in price_data
    assert "unit" in price_data
    assert "region" in price_data
    assert "currency" in price_data
    assert price_data["unit"] == "ton"
    assert price_data["region"] == "US"
    assert price_data["currency"] == "USD"
    assert isinstance(price_data["price"], (int, float))
    assert 400 <= price_data["price"] <= 500  # Based on base price 450 with ±10% variation
    
    # Test with another fertilizer
    price_data_dap = await provider.get_current_price("DAP")
    assert price_data_dap is not None
    assert 580 <= price_data_dap["price"] <= 720  # Base 650 with ±10%
    
    # Test with non-existent fertilizer
    none_data = await provider.get_current_price("NonExistent")
    assert none_data is None