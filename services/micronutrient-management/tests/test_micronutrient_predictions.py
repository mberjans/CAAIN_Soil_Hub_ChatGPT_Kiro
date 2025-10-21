import pytest
from httpx import AsyncClient
from datetime import date
from uuid import UUID

from services.micronutrient_management.src.main import app
from services.micronutrient_management.src.models.micronutrient_models import (
    FarmContext,
    MicronutrientApplication,
    CropDetails,
    YieldPredictionRequest,
    EconomicReturnPredictionRequest,
    YieldPredictionResponse
)
from services.micronutrient_management.src.services.yield_prediction_service import YieldPredictionService
from services.micronutrient_management.src.services.economic_prediction_service import EconomicPredictionService

# --- Fixtures for Test Data ---
@pytest.fixture
def sample_farm_context():
    return FarmContext(
        farm_location_id=UUID("a1b2c3d4-e5f6-7890-1234-567890abcdef"),
        soil_ph=6.5,
        soil_organic_matter_percent=3.0,
        soil_type="loam",
        climate_zone="5a",
        historical_yield_data=[150.0, 155.0, 148.0],
        historical_micronutrient_application=[]
    )

@pytest.fixture
def sample_micronutrient_application():
    return MicronutrientApplication(
        micronutrient_type="Zinc",
        application_rate_per_acre=5.0,
        application_unit="lbs",
        cost_per_unit=2.5,
        total_acres_applied=100.0,
        application_method="soil_broadcast",
        application_date=date(2024, 5, 1)
    )

@pytest.fixture
def sample_crop_details():
    return CropDetails(
        crop_type="Corn",
        variety="DKC67-44",
        planting_date=date(2024, 4, 15),
        expected_market_price_per_unit=4.0,
        yield_unit="bushels",
        micronutrient_deficiency_level="medium",
        growth_stage_at_application="V6"
    )

@pytest.fixture
def sample_yield_prediction_request(
    sample_farm_context,
    sample_micronutrient_application,
    sample_crop_details
):
    return YieldPredictionRequest(
        farm_context=sample_farm_context,
        micronutrient_application=sample_micronutrient_application,
        crop_details=sample_crop_details
    )

@pytest.fixture
def sample_yield_prediction_response():
    return YieldPredictionResponse(
        predicted_yield_per_acre=165.0,
        predicted_total_yield=16500.0,
        baseline_yield_per_acre=150.0,
        yield_increase_percent=10.0,
        confidence_score=0.85,
        explanation="Test explanation for yield prediction."
    )

@pytest.fixture
def sample_economic_return_prediction_request(
    sample_farm_context,
    sample_micronutrient_application,
    sample_crop_details,
    sample_yield_prediction_response
):
    return EconomicReturnPredictionRequest(
        farm_context=sample_farm_context,
        micronutrient_application=sample_micronutrient_application,
        crop_details=sample_crop_details,
        predicted_yield_response=sample_yield_prediction_response
    )

# --- Unit Tests for YieldPredictionService ---
@pytest.mark.asyncio
async def test_yield_prediction_service_success(
    sample_yield_prediction_request
):
    service = YieldPredictionService()
    response = await service.predict_yield_response(sample_yield_prediction_request)

    assert response.predicted_yield_per_acre > 0
    assert response.baseline_yield_per_acre > 0
    assert response.yield_increase_percent >= 0
    assert 0.0 <= response.confidence_score <= 1.0
    assert "explanation" in response.explanation.lower()

@pytest.mark.asyncio
async def test_yield_prediction_service_high_deficiency(
    sample_yield_prediction_request
):
    request = sample_yield_prediction_request.copy(deep=True)
    request.crop_details.micronutrient_deficiency_level = "high"
    service = YieldPredictionService()
    response = await service.predict_yield_response(request)

    # Expect a higher yield increase for high deficiency
    assert response.yield_increase_percent > 8.0 # Medium was 8%

@pytest.mark.asyncio
async def test_yield_prediction_service_no_deficiency(
    sample_yield_prediction_request
):
    request = sample_yield_prediction_request.copy(deep=True)
    request.crop_details.micronutrient_deficiency_level = "none"
    service = YieldPredictionService()
    response = await service.predict_yield_response(request)

    # Expect a very low or zero yield increase for no deficiency
    assert response.yield_increase_percent < 3.0 # Low was 3%

@pytest.mark.asyncio
async def test_yield_prediction_service_high_ph_zinc(
    sample_yield_prediction_request
):
    request = sample_yield_prediction_request.copy(deep=True)
    request.farm_context.soil_ph = 7.5 # High pH
    request.micronutrient_application.micronutrient_type = "Zinc"
    request.crop_details.micronutrient_deficiency_level = "medium"

    service = YieldPredictionService()
    response = await service.predict_yield_response(request)

    # Expect a slightly lower increase due to high pH affecting Zinc availability
    # Original medium deficiency + zinc bonus = 0.08 + 0.05 = 0.13 (13%)
    # With pH penalty = 0.13 - 0.02 = 0.11 (11%)
    assert response.yield_increase_percent < 12.0
    assert response.yield_increase_percent > 10.0

# --- Unit Tests for EconomicPredictionService ---
@pytest.mark.asyncio
async def test_economic_prediction_service_success(
    sample_economic_return_prediction_request
):
    service = EconomicPredictionService()
    response = await service.predict_economic_return(sample_economic_return_prediction_request)

    assert response.total_micronutrient_cost > 0
    assert response.additional_revenue_from_yield_increase > 0
    assert isinstance(response.net_economic_return, float)
    assert isinstance(response.roi_percentage, float)
    assert response.break_even_yield_increase_per_acre >= 0
    assert "explanation" in response.explanation.lower()

@pytest.mark.asyncio
async def test_economic_prediction_service_zero_cost(
    sample_economic_return_prediction_request
):
    request = sample_economic_return_prediction_request.copy(deep=True)
    request.micronutrient_application.cost_per_unit = 0.0
    service = EconomicPredictionService()
    response = await service.predict_economic_return(request)

    assert response.total_micronutrient_cost == 0.0
    assert response.roi_percentage == 0.0 # ROI is 0 if cost is 0 (or infinite, but 0 is safer for calculation)
    assert response.net_economic_return == response.additional_revenue_from_yield_increase

@pytest.mark.asyncio
async def test_economic_prediction_service_negative_net_return(
    sample_economic_return_prediction_request
):
    request = sample_economic_return_prediction_request.copy(deep=True)
    # Make cost very high to ensure negative net return
    request.micronutrient_application.cost_per_unit = 100.0
    service = EconomicPredictionService()
    response = await service.predict_economic_return(request)

    assert response.net_economic_return < 0
    assert response.roi_percentage < 0

# --- Integration Tests for API Endpoints ---
@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "micronutrient-management"}

@pytest.mark.asyncio
async def test_api_predict_yield_success(
    sample_yield_prediction_request
):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/predict-yield",
            json=sample_yield_prediction_request.model_dump(mode='json')
        )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_yield_per_acre"] > 0
    assert data["baseline_yield_per_acre"] > 0
    assert data["yield_increase_percent"] >= 0
    assert "explanation" in data["explanation"].lower()

@pytest.mark.asyncio
async def test_api_predict_economic_return_success(
    sample_economic_return_prediction_request
):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/predict-economic-return",
            json=sample_economic_return_prediction_request.model_dump(mode='json')
        )
    assert response.status_code == 200
    data = response.json()
    assert data["total_micronutrient_cost"] > 0
    assert data["additional_revenue_from_yield_increase"] > 0
    assert "explanation" in data["explanation"].lower()

@pytest.mark.asyncio
async def test_api_predict_yield_invalid_input():
    async with AsyncClient(app=app, base_url="http://test") as client:
        invalid_request = {
            "farm_context": {
                "farm_location_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "soil_ph": 15.0, # Invalid pH
                "soil_organic_matter_percent": 3.0,
                "soil_type": "loam",
                "climate_zone": "5a"
            },
            "micronutrient_application": {
                "micronutrient_type": "Zinc",
                "application_rate_per_acre": 5.0,
                "application_unit": "lbs",
                "cost_per_unit": 2.5,
                "total_acres_applied": 100.0,
                "application_method": "soil_broadcast",
                "application_date": "2024-05-01"
            },
            "crop_details": {
                "crop_type": "Corn",
                "variety": "DKC67-44",
                "planting_date": "2024-04-15",
                "expected_market_price_per_unit": 4.0,
                "yield_unit": "bushels"
            }
        }
        response = await client.post("/predict-yield", json=invalid_request)
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error

# --- Agricultural Validation Tests ---
@pytest.mark.asyncio
async def test_agricultural_yield_increase_range(
    sample_yield_prediction_request
):
    service = YieldPredictionService()
    response = await service.predict_yield_response(sample_yield_prediction_request)

    # Agricultural validation: yield increase should be within a reasonable range (e.g., 0-30%)
    assert 0.0 <= response.yield_increase_percent <= 30.0

@pytest.mark.asyncio
async def test_agricultural_roi_reasonableness(
    sample_economic_return_prediction_request
):
    service = EconomicPredictionService()
    response = await service.predict_economic_return(sample_economic_return_prediction_request)

    # Agricultural validation: ROI should be within a reasonable range for micronutrients (e.g., -100% to 500%)
    assert -100.0 <= response.roi_percentage <= 500.0

@pytest.mark.asyncio
async def test_agricultural_break_even_yield_increase(
    sample_economic_return_prediction_request
):
    service = EconomicPredictionService()
    response = await service.predict_economic_return(sample_economic_return_prediction_request)

    # Agricultural validation: Break-even yield increase should be a realistic value
    # For corn at $4/bushel, a $250 cost/acre would need 62.5 bushels/acre increase to break even.
    # Our sample cost is 5 lbs * $2.5/lb = $12.5/acre. Market price $4/bushel.
    # Break even = $12.5 / $4 = 3.125 bushels/acre.
    assert response.break_even_yield_increase_per_acre > 0
    assert response.break_even_yield_increase_per_acre < 10.0 # Should be a relatively small increase
