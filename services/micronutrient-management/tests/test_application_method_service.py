import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.micronutrient_schemas import (
    ApplicationMethodRequest,
    ApplicationMethod,
    RecommendationPriority,
    EquipmentAvailability,
    FieldCondition,
    MicronutrientType
)
from src.services.application_method_service import ApplicationMethodService


@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_equipment_availability():
    return EquipmentAvailability(
        sprayer=True,
        fertilizer_applicator=True,
        irrigation_system=True,
        seeding_equipment=True
    )


@pytest.fixture
def sample_field_conditions():
    return FieldCondition(
        moisture="adequate",
        temperature=70.0,
        weather_forecast=[],
        soil_compaction=False
    )


@pytest.fixture
def sample_application_method_request(sample_equipment_availability, sample_field_conditions):
    return ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.5
    )


@pytest.mark.asyncio
async def test_get_optimal_application_method_foliar_for_critical_deficiency(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Modify equipment to have sprayer available
    sample_equipment_availability.sprayer = True
    sample_equipment_availability.fertilizer_applicator = False
    sample_equipment_availability.irrigation_system = False
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.CRITICAL,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.5
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    assert recommendation.method == ApplicationMethod.FOLIAR_APPLICATION
    assert recommendation.confidence_score > 0.5
    assert "sprayer" in recommendation.equipment_required
    assert recommendation.field_conditions_suitable is True


@pytest.mark.asyncio
async def test_get_optimal_application_method_fertigation_when_available(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Modify equipment to have only irrigation system
    sample_equipment_availability.sprayer = False
    sample_equipment_availability.fertilizer_applicator = False
    sample_equipment_availability.irrigation_system = True
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.MEDIUM,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.IRON,
        recommended_amount=1.5
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    assert recommendation.method == ApplicationMethod.FERTIGATION
    assert "irrigation_system" in recommendation.equipment_required


@pytest.mark.asyncio
async def test_get_optimal_application_method_seed_treatment_early_growth(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Modify equipment to have only seeding equipment
    sample_equipment_availability.sprayer = False
    sample_equipment_availability.fertilizer_applicator = False
    sample_equipment_availability.irrigation_system = False
    sample_equipment_availability.seeding_equipment = True
    
    request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Seedling",
        deficiency_severity=RecommendationPriority.LOW,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=0.5
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    assert recommendation.method == ApplicationMethod.SEED_TREATMENT
    assert "seeding_equipment" in recommendation.equipment_required


@pytest.mark.asyncio
async def test_get_optimal_application_method_soil_application_default(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Modify to have no specialized equipment
    sample_equipment_availability.sprayer = False
    sample_equipment_availability.fertilizer_applicator = True
    sample_equipment_availability.irrigation_system = False
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Soybean",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.MANGANESE,
        recommended_amount=2.0
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    assert recommendation.method == ApplicationMethod.SOIL_APPLICATION
    assert "fertilizer_applicator" in recommendation.equipment_required


@pytest.mark.asyncio
async def test_get_optimal_application_method_field_conditions_suitability(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Test with unsuitable field conditions for foliar application
    sample_field_conditions.moisture = "wet"
    sample_equipment_availability.sprayer = True
    sample_equipment_availability.fertilizer_applicator = False
    sample_equipment_availability.irrigation_system = False
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.0
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    # Even though foliar might be recommended, field conditions should be unsuitable
    assert recommendation.method == ApplicationMethod.FOLIAR_APPLICATION
    assert recommendation.field_conditions_suitable is False


@pytest.mark.asyncio
async def test_get_optimal_application_method_iron_with_foliar_preferred(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Set up for iron with critical deficiency and sprayer available
    sample_equipment_availability.sprayer = True
    sample_equipment_availability.fertilizer_applicator = False
    sample_equipment_availability.irrigation_system = False
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Soybean",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.CRITICAL,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.IRON,
        recommended_amount=2.0
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    # Iron with critical deficiency should prefer foliar application
    assert recommendation.method == ApplicationMethod.FOLIAR_APPLICATION
    assert recommendation.confidence_score > 0.6


@pytest.mark.asyncio
async def test_get_optimal_application_method_compacted_soil_consideration(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Set up compacted soil condition
    sample_field_conditions.soil_compaction = True
    sample_equipment_availability.sprayer = False
    sample_equipment_availability.fertilizer_applicator = True
    sample_equipment_availability.irrigation_system = False
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Seedling",
        deficiency_severity=RecommendationPriority.MEDIUM,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=1.0
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    # Should still recommend soil application but field conditions may not be suitable
    assert recommendation.method in [ApplicationMethod.SOIL_APPLICATION, ApplicationMethod.BROADCAST, ApplicationMethod.BANDED]
    # For banded application, compacted soil would make it unsuitable
    if recommendation.method in [ApplicationMethod.BROADCAST, ApplicationMethod.BANDED]:
        assert recommendation.field_conditions_suitable is False


@pytest.mark.asyncio
async def test_get_optimal_application_method_alternative_methods(
    mock_db_session, 
    sample_equipment_availability, 
    sample_field_conditions
):
    # Set up multiple equipment types to test alternatives
    sample_equipment_availability.sprayer = True
    sample_equipment_availability.fertilizer_applicator = True
    sample_equipment_availability.irrigation_system = True
    sample_equipment_availability.seeding_equipment = False
    
    request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.0
    )
    
    service = ApplicationMethodService(mock_db_session)
    recommendation = await service.get_optimal_application_method(request)
    
    # Should have alternative methods available
    assert len(recommendation.alternative_methods) > 0
    # The primary method should not be in alternatives
    assert recommendation.method not in recommendation.alternative_methods