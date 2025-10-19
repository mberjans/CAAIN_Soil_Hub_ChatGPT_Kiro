"""Tests for the crop planting integration service skeleton."""

import sys
from pathlib import Path

import pytest


_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

from services.crop_integration_service import CropPlantingIntegrationService  # pylint: disable=import-error


class TestCropPlantingIntegrationServiceSkeleton:
    """Basic tests validating service scaffolding."""

    def test_service_initializes(self) -> None:
        service = CropPlantingIntegrationService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_metadata_method_not_implemented(self) -> None:
        service = CropPlantingIntegrationService()
        with pytest.raises(NotImplementedError):
            await service.fetch_crop_metadata("corn")

    @pytest.mark.asyncio
    async def test_optimize_method_not_implemented(self) -> None:
        service = CropPlantingIntegrationService()
        with pytest.raises(NotImplementedError):
            await service.optimize_planting_date("corn", {"latitude": 41.0, "longitude": -93.0})

    @pytest.mark.asyncio
    async def test_profile_method_not_implemented(self) -> None:
        service = CropPlantingIntegrationService()
        with pytest.raises(NotImplementedError):
            await service.build_integration_profile("corn", {"latitude": 41.0, "longitude": -93.0})
