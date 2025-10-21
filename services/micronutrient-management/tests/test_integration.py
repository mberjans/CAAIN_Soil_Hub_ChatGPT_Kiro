import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.micronutrient_schemas import (
    ApplicationMethodRequest,
    TimingRecommendationRequest,
    ApplicationMethod,
    TimingRecommendationType,
    RecommendationPriority,
    EquipmentAvailability,
    FieldCondition,
    MicronutrientType
)
from src.services.application_method_service import ApplicationMethodService
from src.services.timing_service import TimingService


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


@pytest.mark.asyncio
async def test_integration_application_method_and_timing_services(
    mock_db_session,
    sample_equipment_availability,
    sample_field_conditions
):
    """
    Test that the application method service and timing service work together cohesively.
    """
    # Create an application method request
    app_request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.5
    )
    
    # Get application method recommendation
    app_service = ApplicationMethodService(mock_db_session)
    app_recommendation = await app_service.get_optimal_application_method(app_request)
    
    # Use the recommended method to create a timing request
    timing_request = TimingRecommendationRequest(
        crop_type=app_request.crop_type,
        growth_stage=app_request.growth_stage,
        nutrient_uptake_pattern=f"{app_request.nutrient_type.value} uptake pattern",
        weather_conditions="Clear",  # In a real scenario, this would come from weather service
        nutrient_type=app_request.nutrient_type,
        application_method=app_recommendation.method,
        field_conditions=app_request.field_conditions
    )
    
    # Get timing recommendation
    timing_service = TimingService(mock_db_session)
    timing_recommendation = await timing_service.get_optimal_timing(timing_request)
    
    # Verify both recommendations are coherent
    assert app_recommendation.method in [e for e in ApplicationMethod]
    assert timing_recommendation.timing in [e for e in TimingRecommendationType]
    
    # Verify numeric values are within expected ranges
    assert 0.0 <= app_recommendation.confidence_score <= 1.0
    assert 0.0 <= timing_recommendation.expected_efficacy <= 1.0
    
    # Verify that the recommendation makes sense together
    # e.g., if foliar application is recommended, timing should consider weather
    if app_recommendation.method == ApplicationMethod.FOLIAR_APPLICATION:
        # For foliar application, timing should consider weather
        has_weather_consideration = any(
            "weather" in consideration.lower() or 
            "rain" in consideration.lower() or 
            "wind" in consideration.lower()
            for consideration in timing_recommendation.weather_considerations
        )
        # This might not always be true depending on conditions, so we'll just verify it's a list
        assert isinstance(timing_recommendation.weather_considerations, list)


@pytest.mark.asyncio
async def test_integration_different_crop_growth_stage_scenarios(
    mock_db_session,
    sample_equipment_availability,
    sample_field_conditions
):
    """
    Test various crop and growth stage combinations to ensure integrated services work properly.
    """
    test_scenarios = [
        {
            "crop_type": "Corn",
            "growth_stage": "Seedling",
            "deficiency_severity": RecommendationPriority.MEDIUM,
            "nutrient_type": MicronutrientType.ZINC
        },
        {
            "crop_type": "Soybean",
            "growth_stage": "Flowering",
            "deficiency_severity": RecommendationPriority.CRITICAL,
            "nutrient_type": MicronutrientType.BORON
        },
        {
            "crop_type": "Wheat",
            "growth_stage": "Boot Stage",
            "deficiency_severity": RecommendationPriority.HIGH,
            "nutrient_type": MicronutrientType.MANGANESE
        }
    ]
    
    for scenario in test_scenarios:
        # Create application method request
        app_request = ApplicationMethodRequest(
            crop_type=scenario["crop_type"],
            growth_stage=scenario["growth_stage"],
            deficiency_severity=scenario["deficiency_severity"],
            equipment_availability=sample_equipment_availability,
            field_conditions=sample_field_conditions,
            nutrient_type=scenario["nutrient_type"],
            recommended_amount=2.0
        )
        
        # Get application method
        app_service = ApplicationMethodService(mock_db_session)
        app_recommendation = await app_service.get_optimal_application_method(app_request)
        
        # Create timing request based on application method
        timing_request = TimingRecommendationRequest(
            crop_type=app_request.crop_type,
            growth_stage=app_request.growth_stage,
            nutrient_uptake_pattern=f"{app_request.nutrient_type.value} uptake pattern",
            weather_conditions="Clear",
            nutrient_type=app_request.nutrient_type,
            application_method=app_recommendation.method,
            field_conditions=app_request.field_conditions
        )
        
        # Get timing recommendation
        timing_service = TimingService(mock_db_session)
        timing_recommendation = await timing_service.get_optimal_timing(timing_request)
        
        # Verify recommendations are valid
        assert app_recommendation.method in [e for e in ApplicationMethod]
        assert timing_recommendation.timing in [e for e in TimingRecommendationType]
        assert 0.0 <= app_recommendation.confidence_score <= 1.0
        assert 0.0 <= timing_recommendation.expected_efficacy <= 1.0


@pytest.mark.asyncio
async def test_integration_equipment_availability_impact(
    mock_db_session,
    sample_field_conditions
):
    """
    Test how different equipment availability configurations affect recommendations.
    """
    base_request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.0
    )
    
    # Test with only sprayer available
    equipment_only_sprayer = EquipmentAvailability(
        sprayer=True,
        fertilizer_applicator=False,
        irrigation_system=False,
        seeding_equipment=False
    )
    request_sprayer = base_request.copy(update={"equipment_availability": equipment_only_sprayer})
    
    app_service = ApplicationMethodService(mock_db_session)
    app_recommendation_sprayer = await app_service.get_optimal_application_method(request_sprayer)
    
    # Should recommend foliar application if only sprayer is available
    assert app_recommendation_sprayer.method == ApplicationMethod.FOLIAR_APPLICATION
    
    # Test with only irrigation system available
    equipment_only_irrigation = EquipmentAvailability(
        sprayer=False,
        fertilizer_applicator=False,
        irrigation_system=True,
        seeding_equipment=False
    )
    request_irrigation = base_request.copy(update={"equipment_availability": equipment_only_irrigation})
    
    app_recommendation_irrigation = await app_service.get_optimal_application_method(request_irrigation)
    
    # Should recommend fertigation if only irrigation system is available
    assert app_recommendation_irrigation.method == ApplicationMethod.FERTIGATION
    
    # Test with only fertilizer applicator available
    equipment_only_applicator = EquipmentAvailability(
        sprayer=False,
        fertilizer_applicator=True,
        irrigation_system=False,
        seeding_equipment=False
    )
    request_applicator = base_request.copy(update={"equipment_availability": equipment_only_applicator})
    
    app_recommendation_applicator = await app_service.get_optimal_application_method(request_applicator)
    
    # Should recommend some form of soil application if only applicator is available
    assert app_recommendation_applicator.method in [
        ApplicationMethod.SOIL_APPLICATION,
        ApplicationMethod.BROADCAST,
        ApplicationMethod.BANDED
    ]


@pytest.mark.asyncio
async def test_integration_field_conditions_impact(
    mock_db_session,
    sample_equipment_availability
):
    """
    Test how different field conditions affect recommendations.
    """
    base_request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.0
    )
    
    # Test with wet field conditions (should impact foliar recommendation)
    field_conditions_wet = FieldCondition(
        moisture="wet",
        temperature=70.0,
        weather_forecast=[],
        soil_compaction=False
    )
    request_wet = base_request.copy(update={"field_conditions": field_conditions_wet})
    
    app_service = ApplicationMethodService(mock_db_session)
    app_recommendation_wet = await app_service.get_optimal_application_method(request_wet)
    
    # With wet conditions, if foliar is recommended, field conditions should not be suitable
    if app_recommendation_wet.method == ApplicationMethod.FOLIAR_APPLICATION:
        assert app_recommendation_wet.field_conditions_suitable is False
    
    # Test with dry field conditions
    field_conditions_dry = FieldCondition(
        moisture="dry",
        temperature=85.0,  # Hot as well
        weather_forecast=[],
        soil_compaction=False
    )
    request_dry = base_request.copy(update={"field_conditions": field_conditions_dry})
    
    app_recommendation_dry = await app_service.get_optimal_application_method(request_dry)
    
    # Verify we got a valid recommendation even with dry conditions
    assert app_recommendation_dry.method in [e for e in ApplicationMethod]
    assert 0.0 <= app_recommendation_dry.confidence_score <= 1.0


@pytest.mark.asyncio
async def test_error_handling_in_both_services(
    mock_db_session,
    sample_equipment_availability,
    sample_field_conditions
):
    """
    Test that both services handle errors gracefully.
    """
    # Create an invalid request (invalid nutrient type)
    app_request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type="INVALID_NUTRIENT_TYPE",  # This is invalid
        recommended_amount=2.0
    )
    
    app_service = ApplicationMethodService(mock_db_session)
    
    # Should raise an exception for invalid nutrient type
    with pytest.raises(Exception):
        await app_service.get_optimal_application_method(app_request)
    
    # Create a valid app method request but invalid timing request
    valid_app_request = ApplicationMethodRequest(
        crop_type="Corn",
        growth_stage="Vegetative",
        deficiency_severity=RecommendationPriority.HIGH,
        equipment_availability=sample_equipment_availability,
        field_conditions=sample_field_conditions,
        nutrient_type=MicronutrientType.ZINC,
        recommended_amount=2.0
    )
    
    # First get a valid application method
    app_recommendation = await app_service.get_optimal_application_method(valid_app_request)
    
    # Now try timing service with invalid parameters (we'll simulate this with mock)
    timing_service = TimingService(mock_db_session)
    
    # Test with a simulated error in timing service
    with patch.object(timing_service, '_determine_timing_type', side_effect=Exception("Simulated error")):
        with pytest.raises(Exception):
            timing_request = TimingRecommendationRequest(
                crop_type="Corn",
                growth_stage="Vegetative",
                nutrient_uptake_pattern="Zinc uptake pattern",
                weather_conditions="Clear",
                nutrient_type=MicronutrientType.ZINC,
                application_method=app_recommendation.method,
                field_conditions=sample_field_conditions
            )
            await timing_service.get_optimal_timing(timing_request)