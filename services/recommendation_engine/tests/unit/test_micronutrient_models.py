
import pytest
from pydantic import ValidationError
from datetime import date

from services.recommendation_engine.src.models.micronutrient_models import (
    MicronutrientType,
    SoilTestResult,
    MicronutrientApplication,
    CropYieldData,
    MicronutrientYieldResponse,
    EconomicReturnPrediction,
    YieldEconomicPredictionRequest,
    YieldEconomicPredictionResponse
)

class TestMicronutrientType:
    def test_enum_members(self):
        assert MicronutrientType.BORON == "Boron"
        assert MicronutrientType.ZINC == "Zinc"

    def test_invalid_enum_value(self):
        with pytest.raises(ValueError):
            MicronutrientType("InvalidType")

class TestSoilTestResult:
    def test_valid_soil_test_result(self):
        result = SoilTestResult(
            micronutrient_type=MicronutrientType.BORON,
            level_ppm=0.5,
            sufficiency_range_min_ppm=0.3,
            sufficiency_range_max_ppm=1.0
        )
        assert result.micronutrient_type == MicronutrientType.BORON
        assert result.level_ppm == 0.5

    def test_invalid_level_ppm(self):
        with pytest.raises(ValidationError):
            SoilTestResult(
                micronutrient_type=MicronutrientType.COPPER,
                level_ppm=0,
                sufficiency_range_min_ppm=0.2,
                sufficiency_range_max_ppm=0.8
            )

    def test_invalid_sufficiency_range_min_ppm(self):
        with pytest.raises(ValidationError):
            SoilTestResult(
                micronutrient_type=MicronutrientType.IRON,
                level_ppm=10.0,
                sufficiency_range_min_ppm=0,
                sufficiency_range_max_ppm=20.0
            )

    def test_invalid_sufficiency_range_max_ppm(self):
        with pytest.raises(ValidationError):
            SoilTestResult(
                micronutrient_type=MicronutrientType.MANGANESE,
                level_ppm=5.0,
                sufficiency_range_min_ppm=5.0,
                sufficiency_range_max_ppm=4.0
            )

class TestMicronutrientApplication:
    def test_valid_application(self):
        app = MicronutrientApplication(
            micronutrient_type=MicronutrientType.ZINC,
            application_rate_kg_ha=2.5,
            cost_per_kg=15.0
        )
        assert app.application_rate_kg_ha == 2.5

    def test_invalid_application_rate(self):
        with pytest.raises(ValidationError):
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.MOLYBDENUM,
                application_rate_kg_ha=0,
                cost_per_kg=50.0
            )

    def test_invalid_cost_per_kg(self):
        with pytest.raises(ValidationError):
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.CHLORINE,
                application_rate_kg_ha=1.0,
                cost_per_kg=-10.0
            )

class TestCropYieldData:
    def test_valid_crop_yield_data(self):
        data = CropYieldData(
            crop_type="Corn",
            expected_yield_baseline_kg_ha=10000.0,
            unit_price_per_kg=0.25
        )
        assert data.crop_type == "Corn"

    def test_invalid_crop_type(self):
        with pytest.raises(ValidationError):
            CropYieldData(
                crop_type="",
                expected_yield_baseline_kg_ha=5000.0,
                unit_price_per_kg=0.5
            )

    def test_invalid_expected_yield_baseline(self):
        with pytest.raises(ValidationError):
            CropYieldData(
                crop_type="Soybean",
                expected_yield_baseline_kg_ha=0,
                unit_price_per_kg=0.6
            )

    def test_invalid_unit_price(self):
        with pytest.raises(ValidationError):
            CropYieldData(
                crop_type="Wheat",
                expected_yield_baseline_kg_ha=7000.0,
                unit_price_per_kg=-0.1
            )

class TestMicronutrientYieldResponse:
    def test_valid_yield_response(self):
        response = MicronutrientYieldResponse(
            micronutrient_type=MicronutrientType.ZINC,
            predicted_yield_increase_kg_ha=500.0,
            predicted_total_yield_kg_ha=10500.0,
            confidence_score=0.85
        )
        assert response.predicted_yield_increase_kg_ha == 500.0

    def test_invalid_predicted_yield_increase(self):
        with pytest.raises(ValidationError):
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.BORON,
                predicted_yield_increase_kg_ha=-100.0,
                predicted_total_yield_kg_ha=9900.0,
                confidence_score=0.7
            )

    def test_invalid_predicted_total_yield(self):
        with pytest.raises(ValidationError):
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.COPPER,
                predicted_yield_increase_kg_ha=100.0,
                predicted_total_yield_kg_ha=0,
                confidence_score=0.9
            )

    def test_invalid_confidence_score_low(self):
        with pytest.raises(ValidationError):
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.IRON,
                predicted_yield_increase_kg_ha=200.0,
                predicted_total_yield_kg_ha=10200.0,
                confidence_score=-0.1
            )

    def test_invalid_confidence_score_high(self):
        with pytest.raises(ValidationError):
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.MANGANESE,
                predicted_yield_increase_kg_ha=300.0,
                predicted_total_yield_kg_ha=10300.0,
                confidence_score=1.1
            )

class TestEconomicReturnPrediction:
    def test_valid_economic_return(self):
        prediction = EconomicReturnPrediction(
            micronutrient_type=MicronutrientType.ZINC,
            total_application_cost=250.0,
            additional_revenue_from_yield_increase=1250.0,
            net_economic_return=1000.0,
            roi_percentage=400.0,
            currency="USD"
        )
        assert prediction.net_economic_return == 1000.0

    def test_invalid_total_application_cost(self):
        with pytest.raises(ValidationError):
            EconomicReturnPrediction(
                micronutrient_type=MicronutrientType.BORON,
                total_application_cost=-10.0,
                additional_revenue_from_yield_increase=100.0,
                net_economic_return=90.0,
                roi_percentage=900.0
            )

    def test_invalid_additional_revenue(self):
        with pytest.raises(ValidationError):
            EconomicReturnPrediction(
                micronutrient_type=MicronutrientType.COPPER,
                total_application_cost=50.0,
                additional_revenue_from_yield_increase=-20.0,
                net_economic_return=-70.0,
                roi_percentage=-140.0
            )

    def test_invalid_currency_length(self):
        with pytest.raises(ValidationError):
            EconomicReturnPrediction(
                micronutrient_type=MicronutrientType.IRON,
                total_application_cost=100.0,
                additional_revenue_from_yield_increase=300.0,
                net_economic_return=200.0,
                roi_percentage=200.0,
                currency=""
            )
        with pytest.raises(ValidationError):
            EconomicReturnPrediction(
                micronutrient_type=MicronutrientType.IRON,
                total_application_cost=100.0,
                additional_revenue_from_yield_increase=300.0,
                net_economic_return=200.0,
                roi_percentage=200.0,
                currency="EURO"
            )

class TestYieldEconomicPredictionRequest:
    def test_valid_request(self):
        request = YieldEconomicPredictionRequest(
            farm_id="farm123",
            field_id="field456",
            crop_yield_data=CropYieldData(
                crop_type="Corn",
                expected_yield_baseline_kg_ha=10000.0,
                unit_price_per_kg=0.25
            ),
            soil_test_results=[
                SoilTestResult(
                    micronutrient_type=MicronutrientType.ZINC,
                    level_ppm=0.5,
                    sufficiency_range_min_ppm=0.3,
                    sufficiency_range_max_ppm=1.0
                )
            ],
            micronutrient_applications=[
                MicronutrientApplication(
                    micronutrient_type=MicronutrientType.ZINC,
                    application_rate_kg_ha=2.5,
                    cost_per_kg=15.0
                )
            ],
            application_date=date(2025, 5, 1),
            area_ha=10.0
        )
        assert request.farm_id == "farm123"

    def test_invalid_area_ha(self):
        with pytest.raises(ValidationError):
            YieldEconomicPredictionRequest(
                farm_id="farm123",
                field_id="field456",
                crop_yield_data=CropYieldData(
                    crop_type="Corn",
                    expected_yield_baseline_kg_ha=10000.0,
                    unit_price_per_kg=0.25
                ),
                soil_test_results=[],
                micronutrient_applications=[],
                application_date=date(2025, 5, 1),
                area_ha=0
            )

class TestYieldEconomicPredictionResponse:
    def test_valid_response(self):
        response = YieldEconomicPredictionResponse(
            request_id="req789",
            micronutrient_yield_responses=[
                MicronutrientYieldResponse(
                    micronutrient_type=MicronutrientType.ZINC,
                    predicted_yield_increase_kg_ha=500.0,
                    predicted_total_yield_kg_ha=10500.0,
                    confidence_score=0.85
                )
            ],
            economic_return_predictions=[
                EconomicReturnPrediction(
                    micronutrient_type=MicronutrientType.ZINC,
                    total_application_cost=250.0,
                    additional_revenue_from_yield_increase=1250.0,
                    net_economic_return=1000.0,
                    roi_percentage=400.0
                )
            ],
            overall_status="SUCCESS",
            message="Prediction successful"
        )
        assert response.request_id == "req789"
        assert response.overall_status == "SUCCESS"

    def test_response_with_no_message(self):
        response = YieldEconomicPredictionResponse(
            request_id="req790",
            micronutrient_yield_responses=[],
            economic_return_predictions=[],
            overall_status="NO_DATA"
        )
        assert response.message is None
