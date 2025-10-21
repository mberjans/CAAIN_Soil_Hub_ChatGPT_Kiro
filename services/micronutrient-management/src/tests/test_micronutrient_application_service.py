import pytest
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any

from ..services.micronutrient_application_service import MicronutrientApplicationService
from ..models.micronutrient_models import (
    MicronutrientApplicationRequest,
    MicronutrientApplicationResponse,
    MicronutrientApplication,
    ApplicationMethod,
    TimingStage
)

@pytest.fixture
def service():
    return MicronutrientApplicationService()

@pytest.fixture
def corn_request_deficient_zinc():
    return MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 0.8, "Boron": 0.4},
        target_micronutrient_levels={"Zinc": 2.0, "Boron": 1.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR, ApplicationMethod.SOIL_BANDED]
    )

@pytest.fixture
def corn_request_no_deficiency():
    return MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 2.5, "Boron": 1.5},
        target_micronutrient_levels={"Zinc": 2.0, "Boron": 1.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )

@pytest.fixture
def corn_request_limited_equipment():
    return MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 0.8},
        target_micronutrient_levels={"Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR] # Only foliar available
    )

@pytest.fixture
def corn_request_wrong_growth_stage():
    return MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.GRAIN_FILL, # Zinc foliar not recommended for grain_fill
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 0.8},
        target_micronutrient_levels={"Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )

@pytest.fixture
def unknown_crop_request():
    return MicronutrientApplicationRequest(
        crop_type="Wheat",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 0.8},
        target_micronutrient_levels={"Zinc": 2.0},
        application_goals=["maximize_yield"]
    )

@pytest.mark.asyncio
async def test_get_application_recommendations_success(service, corn_request_deficient_zinc):
    """Test successful recommendation generation for deficient micronutrients."""
    response = await service.get_application_recommendations(corn_request_deficient_zinc)

    assert isinstance(response, MicronutrientApplicationResponse)
    assert len(response.recommendations) > 0
    assert response.overall_efficiency is not None
    assert response.notes is None

    # Check for Zinc recommendation
    zinc_rec = next((r for r in response.recommendations if r.micronutrient == "Zinc"), None)
    assert zinc_rec is not None
    assert zinc_rec.method == ApplicationMethod.FOLIAR # Foliar has higher efficiency for vegetative stage in mock rules
    assert zinc_rec.timing == TimingStage.VEGETATIVE
    assert zinc_rec.rate > 0

    # Check for Boron recommendation
    boron_rec = next((r for r in response.recommendations if r.micronutrient == "Boron"), None)
    assert boron_rec is not None
    assert boron_rec.method == ApplicationMethod.FOLIAR
    assert boron_rec.timing == TimingStage.VEGETATIVE
    assert boron_rec.rate > 0


@pytest.mark.asyncio
async def test_get_application_recommendations_no_deficiency(service, corn_request_no_deficiency):
    """Test that no recommendations are made if no deficiency is detected."""
    response = await service.get_application_recommendations(corn_request_no_deficiency)

    assert isinstance(response, MicronutrientApplicationResponse)
    assert len(response.recommendations) == 0
    assert response.overall_efficiency is None
    assert response.notes is None


@pytest.mark.asyncio
async def test_get_application_recommendations_limited_equipment(service, corn_request_limited_equipment):
    """Test filtering recommendations based on available equipment."""
    response = await service.get_application_recommendations(corn_request_limited_equipment)

    assert isinstance(response, MicronutrientApplicationResponse)
    assert len(response.recommendations) == 1
    assert response.recommendations[0].micronutrient == "Zinc"
    assert response.recommendations[0].method == ApplicationMethod.FOLIAR # Only foliar was available


@pytest.mark.asyncio
async def test_get_application_recommendations_wrong_growth_stage(service, corn_request_wrong_growth_stage):
    """Test filtering recommendations based on growth stage compatibility."""
    response = await service.get_application_recommendations(corn_request_wrong_growth_stage)

    assert isinstance(response, MicronutrientApplicationResponse)
    assert len(response.recommendations) == 0
    assert "Could not find suitable application method/timing for Zinc given constraints." in response.notes


@pytest.mark.asyncio
async def test_get_application_recommendations_unknown_crop(service, unknown_crop_request):
    """Test handling of unknown crop types."""
    response = await service.get_application_recommendations(unknown_crop_request)

    assert isinstance(response, MicronutrientApplicationResponse)
    assert len(response.recommendations) == 0
    assert "No specific rules found for crop type: Wheat" in response.notes


@pytest.mark.asyncio
async def test_get_application_recommendations_unknown_micronutrient(service, corn_request_deficient_zinc):
    """Test handling of unknown micronutrients for a known crop."""
    # Modify request to include an unknown micronutrient
    corn_request_deficient_zinc.current_micronutrient_levels["Molybdenum"] = 0.1
    corn_request_deficient_zinc.target_micronutrient_levels["Molybdenum"] = 0.5

    response = await service.get_application_recommendations(corn_request_deficient_zinc)

    assert isinstance(response, MicronutrientApplicationResponse)
    assert len(response.recommendations) == 2 # Zinc and Boron should still be recommended
    assert "No specific rules found for micronutrient Molybdenum for Corn" in response.notes


@pytest.mark.asyncio
async def test_get_application_recommendations_prioritize_yield(service):
    """Test that recommendations prioritize 'maximize_yield' goal."""
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 0.8},
        target_micronutrient_levels={"Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR, ApplicationMethod.SOIL_BANDED] # Both available
    )

    # In mock rules, Zinc foliar has efficiency 0.7, soil_banded has 0.9
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 1
    assert response.recommendations[0].micronutrient == "Zinc"
    assert response.recommendations[0].method == ApplicationMethod.FOLIAR # Foliar is chosen due to timing compatibility
    assert response.recommendations[0].efficiency_score == 0.7


@pytest.mark.asyncio
async def test_get_application_recommendations_no_equipment_available(service):
    """Test scenario where no suitable equipment is available."""
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 0.8},
        target_micronutrient_levels={"Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[] # No equipment available
    )

    response = await service.get_application_recommendations(request)
    assert len(response.recommendations) == 0
