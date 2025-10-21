import pytest
from httpx import AsyncClient
from datetime import datetime
from uuid import uuid4

from services.nutrient_deficiency.src.main import app
from services.nutrient_deficiency.src.models.tissue_test_models import Nutrient, TissueTestResult

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "nutrient-deficiency-detection"}

@pytest.mark.asyncio
async def test_analyze_tissue_test_success(tissue_test_service_mock):
    farm_id = uuid4()
    field_id = uuid4()
    test_date = datetime.now().isoformat()
    request_payload = {
        "farm_id": str(farm_id),
        "field_id": str(field_id),
        "crop_type": "corn",
        "growth_stage": "V6",
        "test_date": test_date,
        "results": [
            {"nutrient": "N", "value": 3.5, "unit": "%"},
            {"nutrient": "P", "value": 0.4, "unit": "%"},
        ]
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/tissue-tests/analyze", json=request_payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["farm_id"] == str(farm_id)
    assert response_data["crop_type"] == "corn"
    assert response_data["overall_status"] == "Healthy"
    assert len(response_data["deficiencies"]) == 0

@pytest.mark.asyncio
async def test_analyze_tissue_test_with_deficiency(tissue_test_service_mock):
    farm_id = uuid4()
    field_id = uuid4()
    test_date = datetime.now().isoformat()
    request_payload = {
        "farm_id": str(farm_id),
        "field_id": str(field_id),
        "crop_type": "corn",
        "growth_stage": "V6",
        "test_date": test_date,
        "results": [
            {"nutrient": "N", "value": 2.0, "unit": "%"},
            {"nutrient": "P", "value": 0.4, "unit": "%"},
        ]
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/tissue-tests/analyze", json=request_payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["overall_status"] == "Deficiencies Detected"
    assert len(response_data["deficiencies"]) == 1
    assert response_data["deficiencies"][0]["nutrient"] == "N"
    assert response_data["deficiencies"][0]["severity"] == "severe"

@pytest.mark.asyncio
async def test_analyze_tissue_test_invalid_input():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/tissue-tests/analyze", json={})
    assert response.status_code == 422  # Unprocessable Entity for Pydantic validation error

@pytest.fixture
def tissue_test_service_mock():
    """Mock the TissueTestService to isolate API tests from service logic."""
    from unittest.mock import AsyncMock, patch
    from services.nutrient_deficiency.src.services.tissue_test_service import TissueTestService
    from services.nutrient_deficiency.src.models.tissue_test_models import TissueTestAnalysisResponse, DeficiencySeverity

    mock_service = AsyncMock(spec=TissueTestService)

    async def mock_analyze_tissue_test(request):
        if request.crop_type == "corn" and request.growth_stage == "V6":
            if any(r.nutrient == Nutrient.NITROGEN and r.value < 2.5 for r in request.results):
                return TissueTestAnalysisResponse(
                    analysis_id=uuid4(),
                    farm_id=request.farm_id,
                    field_id=request.field_id,
                    crop_type=request.crop_type,
                    growth_stage=request.growth_stage,
                    test_date=request.test_date,
                    deficiencies=[
                        NutrientDeficiency(
                            nutrient=Nutrient.NITROGEN,
                            severity=DeficiencySeverity.SEVERE,
                            measured_value=2.0,
                            optimal_range={"optimal_min": 3.0, "optimal_max": 4.0},
                            recommendation="Severe N deficiency"
                        )
                    ],
                    overall_status="Deficiencies Detected",
                    recommendations_summary="Severe N deficiency detected.",
                    raw_results=request.results
                )
            else:
                return TissueTestAnalysisResponse(
                    analysis_id=uuid4(),
                    farm_id=request.farm_id,
                    field_id=request.field_id,
                    crop_type=request.crop_type,
                    growth_stage=request.growth_stage,
                    test_date=request.test_date,
                    deficiencies=[],
                    overall_status="Healthy",
                    recommendations_summary="No specific recommendations.",
                    raw_results=request.results
                )
        else:
            return TissueTestAnalysisResponse(
                analysis_id=uuid4(),
                farm_id=request.farm_id,
                field_id=request.field_id,
                crop_type=request.crop_type,
                growth_stage=request.growth_stage,
                test_date=request.test_date,
                deficiencies=[],
                overall_status="Analysis Incomplete: Crop type not supported.",
                recommendations_summary="Analysis Incomplete: Crop type not supported.",
                raw_results=request.results
            )

    mock_service.analyze_tissue_test.side_effect = mock_analyze_tissue_test

    with patch('services.nutrient_deficiency.src.api.tissue_test_routes.get_tissue_test_service', return_value=mock_service):
        yield mock_service
