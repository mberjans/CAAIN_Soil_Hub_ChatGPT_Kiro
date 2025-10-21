"""
Integration Tests for Fertilizer Type Selection Service

Tests the integration of the FertilizerTypeSelectionService with other services,
especially the database service for fetching fertilizer data.

Implements TICKET-023_fertilizer-type-selection-13.1
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.recommendation_engine.src.services.fertilizer_type_selection_service import FertilizerTypeSelectionService
from services.recommendation_engine.src.models.fertilizer_models import FarmerPriorities, FarmerConstraints

class TestFertilizerTypeIntegration:
    """Test integration of the FertilizerTypeSelectionService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FertilizerTypeSelectionService()

    @pytest.mark.asyncio
    async def test_get_available_fertilizer_types_integration(self, service):
        """
        Test that get_available_fertilizer_types fetches data from the database
        instead of a hardcoded list.
        """
        mock_fertilizers = [
            {
                "product_id": "db_urea_46_0_0",
                "name": "DB Urea (46-0-0)",
                "fertilizer_type": "synthetic",
                "cost_per_unit": 500,
                "organic_certified": False,
            },
            {
                "product_id": "db_composted_manure",
                "name": "DB Composted Manure",
                "fertilizer_type": "organic",
                "cost_per_unit": 60,
                "organic_certified": True,
            },
        ]

        with patch.object(service.db_service, 'get_fertilizers', new_callable=AsyncMock) as mock_get_fertilizers:
            mock_get_fertilizers.return_value = mock_fertilizers

            fertilizers = await service.get_available_fertilizer_types()

            assert len(fertilizers) == 2
            assert fertilizers[0]['product_id'] == "db_urea_46_0_0"
            assert fertilizers[1]['product_id'] == "db_composted_manure"
            
            mock_get_fertilizers.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
