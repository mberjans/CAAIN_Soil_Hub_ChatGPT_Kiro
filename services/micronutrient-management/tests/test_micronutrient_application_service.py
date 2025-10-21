import pytest
from unittest.mock import AsyncMock, patch
from src.services.micronutrient_application_service import MicronutrientApplicationService
from src.models.micronutrient_models import (
    MicronutrientApplicationRequest,
    MicronutrientApplicationResponse,
    ApplicationMethod,
    TimingStage
)

@pytest.fixture
def service():
    return MicronutrientApplicationService()

@pytest.mark.asyncio
async def test_recommend_boron_for_corn_foliar(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Boron": 0.4, "Zinc": 1.5},
        target_micronutrient_levels={"Boron": 1.0, "Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR, ApplicationMethod.SOIL_BROADCAST]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 1
    assert response.recommendations[0].micronutrient == "Boron"
    assert response.recommendations[0].method == ApplicationMethod.FOLIAR
    assert response.recommendations[0].timing == TimingStage.VEGETATIVE
    assert response.recommendations[0].rate > 0
    assert response.recommendations[0].efficiency_score == 0.8
    assert response.overall_efficiency == 0.8
    assert response.notes is None

@pytest.mark.asyncio
async def test_recommend_zinc_for_corn_soil_banded(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.PLANTING,
        soil_type="sandy_loam",
        current_micronutrient_levels={"Boron": 1.0, "Zinc": 1.0},
        target_micronutrient_levels={"Boron": 1.0, "Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.SOIL_BANDED, ApplicationMethod.SEED_TREATMENT]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 1
    assert response.recommendations[0].micronutrient == "Zinc"
    assert response.recommendations[0].method == ApplicationMethod.SOIL_BANDED
    assert response.recommendations[0].timing == TimingStage.PLANTING
    assert response.recommendations[0].rate > 0
    assert response.recommendations[0].efficiency_score == 0.9

@pytest.mark.asyncio
async def test_no_recommendation_if_no_deficiency(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Boron": 1.5, "Zinc": 2.5},
        target_micronutrient_levels={"Boron": 1.0, "Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 0
    assert response.overall_efficiency is None
    assert response.notes is None

@pytest.mark.asyncio
async def test_no_recommendation_if_no_equipment(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Boron": 0.4},
        target_micronutrient_levels={"Boron": 1.0},
        application_goals=["maximize_yield"],
        equipment_available=[] # No equipment available
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 0
    assert response.overall_efficiency is None
    assert "Could not find suitable application method/timing for Boron given constraints." in response.notes

@pytest.mark.asyncio
async def test_no_recommendation_if_inappropriate_timing(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.FRUITING, # Boron foliar is vegetative/flowering
        soil_type="loam",
        current_micronutrient_levels={"Boron": 0.4},
        target_micronutrient_levels={"Boron": 1.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 0
    assert response.overall_efficiency is None
    assert "Could not find suitable application method/timing for Boron given constraints." in response.notes

@pytest.mark.asyncio
async def test_unknown_crop_type(service):
    request = MicronutrientApplicationRequest(
        crop_type="Wheat", # Not in rules
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Boron": 0.4},
        target_micronutrient_levels={"Boron": 1.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 0
    assert response.overall_efficiency is None
    assert "No specific rules found for crop type: Wheat" in response.notes

@pytest.mark.asyncio
async def test_unknown_micronutrient(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Molybdenum": 0.1},
        target_micronutrient_levels={"Molybdenum": 0.2},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 0
    assert response.overall_efficiency is None
    assert "No specific rules found for micronutrient Molybdenum for Corn" in response.notes

@pytest.mark.asyncio
async def test_multiple_micronutrients_and_methods(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.VEGETATIVE,
        soil_type="loam",
        current_micronutrient_levels={"Boron": 0.4, "Zinc": 1.0},
        target_micronutrient_levels={"Boron": 1.0, "Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR, ApplicationMethod.SOIL_BANDED]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 2
    assert any(r.micronutrient == "Boron" for r in response.recommendations)
    assert any(r.micronutrient == "Zinc" for r in response.recommendations)
    assert response.overall_efficiency is not None
    assert response.notes is None

@pytest.mark.asyncio
async def test_soybean_manganese_foliar(service):
    request = MicronutrientApplicationRequest(
        crop_type="Soybean",
        growth_stage=TimingStage.FLOWERING,
        soil_type="sandy_loam",
        current_micronutrient_levels={"Manganese": 15.0},
        target_micronutrient_levels={"Manganese": 30.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.FOLIAR]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 1
    assert response.recommendations[0].micronutrient == "Manganese"
    assert response.recommendations[0].method == ApplicationMethod.FOLIAR
    assert response.recommendations[0].timing == TimingStage.FLOWERING
    assert response.recommendations[0].rate > 0
    assert response.recommendations[0].efficiency_score == 0.85

@pytest.mark.asyncio
async def test_zinc_seed_treatment_pre_plant(service):
    request = MicronutrientApplicationRequest(
        crop_type="Corn",
        growth_stage=TimingStage.PRE_PLANT,
        soil_type="loam",
        current_micronutrient_levels={"Zinc": 1.0},
        target_micronutrient_levels={"Zinc": 2.0},
        application_goals=["maximize_yield"],
        equipment_available=[ApplicationMethod.SEED_TREATMENT]
    )
    response = await service.get_application_recommendations(request)

    assert len(response.recommendations) == 1
    assert response.recommendations[0].micronutrient == "Zinc"
    assert response.recommendations[0].method == ApplicationMethod.SEED_TREATMENT
    assert response.recommendations[0].timing == TimingStage.PRE_PLANT
    assert response.recommendations[0].rate > 0
    assert response.recommendations[0].efficiency_score == 0.85
