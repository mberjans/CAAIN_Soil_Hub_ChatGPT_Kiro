"""Tests for the crop planting integration service."""

import sys
from pathlib import Path

import pytest


_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

from services.crop_integration_service import (  # pylint: disable=import-error
    CropIntegrationResult,
    CropPlantingIntegrationService,
)


class TestCropPlantingIntegrationService:
    """Validation of crop integration logic."""

    def test_service_initializes(self) -> None:
        service = CropPlantingIntegrationService()
        assert service is not None

    @pytest.mark.asyncio
    async def test_fetch_crop_metadata_returns_taxonomy(self) -> None:
        service = CropPlantingIntegrationService()
        metadata = await service.fetch_crop_metadata("corn")
        assert "display_name" in metadata
        assert metadata["display_name"].lower() == "corn"
        assert "taxonomic_hierarchy" in metadata

    @pytest.mark.asyncio
    async def test_optimize_planting_date_produces_window(self) -> None:
        service = CropPlantingIntegrationService()
        location = {"latitude": 41.0, "longitude": -93.0}
        window = await service.optimize_planting_date("corn", location)
        assert window.crop_name.lower() == "corn"
        assert window.optimal_date is not None
        assert window.earliest_safe_date is not None

    @pytest.mark.asyncio
    async def test_build_integration_profile_contains_timeline(self) -> None:
        service = CropPlantingIntegrationService()
        location = {"latitude": 41.0, "longitude": -93.0, "state": "IA"}
        result = await service.build_integration_profile("corn", location)
        assert isinstance(result, CropIntegrationResult)
        assert "vt" in result.growth_stage_timeline
        assert len(result.extension_recommendations) > 0
        assert len(result.planting_risk_notes) >= 0

    @pytest.mark.asyncio
    async def test_build_profile_handles_soybean(self) -> None:
        service = CropPlantingIntegrationService()
        location = {"latitude": 33.0, "longitude": -84.0, "state": "GA"}
        result = await service.build_integration_profile("soybean", location)
        assert isinstance(result, CropIntegrationResult)
        assert "r3" in result.growth_stage_timeline
        guidance_found = False
        for note in result.extension_recommendations:
            if "soybean" in note.lower() or "pod" in note.lower():
                guidance_found = True
                break
        assert guidance_found
