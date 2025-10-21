import pytest
from datetime import datetime
from uuid import uuid4

from services.nutrient_deficiency.src.services.tissue_test_service import TissueTestService
from services.nutrient_deficiency.src.models.tissue_test_models import (
    TissueTestRequest,
    TissueTestResult,
    Nutrient,
    DeficiencySeverity,
    NutrientDeficiency
)

@pytest.fixture
def tissue_test_service():
    return TissueTestService()

@pytest.mark.asyncio
async def test_analyze_tissue_test_no_deficiencies(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="corn",
        growth_stage="V6",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.NITROGEN, value=3.5, unit="%", optimal_min=3.0, optimal_max=4.0),
            TissueTestResult(nutrient=Nutrient.PHOSPHORUS, value=0.4, unit="%", optimal_min=0.3, optimal_max=0.5),
            TissueTestResult(nutrient=Nutrient.POTASSIUM, value=2.5, unit="%", optimal_min=2.0, optimal_max=3.0),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.farm_id == farm_id
    assert response.field_id == field_id
    assert response.crop_type == "corn"
    assert response.growth_stage == "V6"
    assert response.overall_status == "Healthy"
    assert len(response.deficiencies) == 0
    assert "No specific recommendations" in response.recommendations_summary

@pytest.mark.asyncio
async def test_analyze_tissue_test_moderate_deficiency(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="corn",
        growth_stage="V6",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.NITROGEN, value=2.8, unit="%", optimal_min=3.0, optimal_max=4.0),
            TissueTestResult(nutrient=Nutrient.PHOSPHORUS, value=0.4, unit="%", optimal_min=0.3, optimal_max=0.5),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Deficiencies Detected"
    assert len(response.deficiencies) == 1
    deficiency = response.deficiencies[0]
    assert deficiency.nutrient == Nutrient.NITROGEN
    assert deficiency.severity == DeficiencySeverity.MODERATE
    assert deficiency.measured_value == 2.8
    assert "Moderate deficiency of N" in deficiency.recommendation
    assert "Moderate deficiency of N" in response.recommendations_summary

@pytest.mark.asyncio
async def test_analyze_tissue_test_severe_deficiency(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="soybean",
        growth_stage="R2",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.POTASSIUM, value=0.9, unit="%", optimal_min=1.5, optimal_max=2.3),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Deficiencies Detected"
    assert len(response.deficiencies) == 1
    deficiency = response.deficiencies[0]
    assert deficiency.nutrient == Nutrient.POTASSIUM
    assert deficiency.severity == DeficiencySeverity.SEVERE
    assert deficiency.measured_value == 0.9
    assert "Severe deficiency of K" in deficiency.recommendation
    assert "Severe deficiency of K" in response.recommendations_summary

@pytest.mark.asyncio
async def test_analyze_tissue_test_excess(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="corn",
        growth_stage="V6",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.ZINC, value=75.0, unit="ppm", optimal_min=20.0, optimal_max=60.0),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Deficiencies Detected"
    assert len(response.deficiencies) == 1
    deficiency = response.deficiencies[0]
    assert deficiency.nutrient == Nutrient.ZINC
    assert deficiency.severity == DeficiencySeverity.SEVERE
    assert deficiency.measured_value == 75.0
    assert "Excess of Zn" in deficiency.recommendation

@pytest.mark.asyncio
async def test_analyze_tissue_test_slightly_high(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="corn",
        growth_stage="V6",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.ZINC, value=65.0, unit="ppm", optimal_min=20.0, optimal_max=60.0),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Deficiencies Detected"
    assert len(response.deficiencies) == 1
    deficiency = response.deficiencies[0]
    assert deficiency.nutrient == Nutrient.ZINC
    assert deficiency.severity == DeficiencySeverity.MILD
    assert deficiency.measured_value == 65.0
    assert "Slightly high level of Zn" in deficiency.recommendation

@pytest.mark.asyncio
async def test_analyze_tissue_test_unsupported_crop_type(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="wheat",
        growth_stage="tillering",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.NITROGEN, value=3.0, unit="%"),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Analysis Incomplete: Crop type not supported for detailed analysis."
    assert len(response.deficiencies) == 0

@pytest.mark.asyncio
async def test_analyze_tissue_test_unsupported_growth_stage(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="corn",
        growth_stage="VT",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.NITROGEN, value=3.0, unit="%"),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Analysis Incomplete: Growth stage not supported for detailed analysis."
    assert len(response.deficiencies) == 0

@pytest.mark.asyncio
async def test_analyze_tissue_test_missing_nutrient_range(tissue_test_service):
    farm_id = uuid4()
    field_id = uuid4()
    request = TissueTestRequest(
        farm_id=farm_id,
        field_id=field_id,
        crop_type="corn",
        growth_stage="V6",
        test_date=datetime.now(),
        results=[
            TissueTestResult(nutrient=Nutrient.CALCIUM, value=0.5, unit="%"), # Calcium not in hardcoded ranges
            TissueTestResult(nutrient=Nutrient.NITROGEN, value=3.5, unit="%"),
        ]
    )

    response = await tissue_test_service.analyze_tissue_test(request)

    assert response.overall_status == "Healthy"
    assert len(response.deficiencies) == 0 # Only Nitrogen is within range, Calcium is ignored
    assert "No specific recommendations" in response.recommendations_summary
