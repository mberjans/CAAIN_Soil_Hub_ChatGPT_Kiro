
import pytest
from datetime import date
from uuid import uuid4

from services.recommendation_engine.src.models.micronutrient_models import (
    MicronutrientType,
    SoilTestResult,
    MicronutrientApplication,
    CropYieldData,
    MicronutrientYieldResponse,
    YieldEconomicPredictionRequest
)
from services.recommendation_engine.src.services.micronutrient_yield_prediction_service import MicronutrientYieldPredictionService

class TestMicronutrientYieldPredictionService:

    @pytest.fixture
    def service(self):
        return MicronutrientYieldPredictionService()

    @pytest.fixture
    def base_request(self):
        return YieldEconomicPredictionRequest(
            farm_id=str(uuid4()),
            field_id=str(uuid4()),
            crop_yield_data=CropYieldData(
                crop_type="Corn",
                expected_yield_baseline_kg_ha=10000.0,
                unit_price_per_kg=0.25
            ),
            soil_test_results=[],
            micronutrient_applications=[],
            application_date=date(2025, 5, 1),
            area_ha=10.0
        )

    def test_predict_yield_response_deficient_micronutrient(self, service, base_request):
        # Zinc is deficient
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=0.2,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            )
        ]
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.5,
                cost_per_kg=15.0
            )
        ]

        responses = service.predict_yield_response(base_request)

        assert len(responses) == 1
        assert responses[0].micronutrient_type == MicronutrientType.ZINC
        assert responses[0].predicted_yield_increase_kg_ha > 0
        assert responses[0].predicted_total_yield_kg_ha > base_request.crop_yield_data.expected_yield_baseline_kg_ha
        assert responses[0].confidence_score == pytest.approx(0.8)

    def test_predict_yield_response_sufficient_micronutrient(self, service, base_request):
        # Zinc is sufficient
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=0.7,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            )
        ]
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.5,
                cost_per_kg=15.0
            )
        ]

        responses = service.predict_yield_response(base_request)

        assert len(responses) == 1
        assert responses[0].micronutrient_type == MicronutrientType.ZINC
        assert responses[0].predicted_yield_increase_kg_ha == 0
        assert responses[0].predicted_total_yield_kg_ha == base_request.crop_yield_data.expected_yield_baseline_kg_ha
        assert responses[0].confidence_score == pytest.approx(0.9)

    def test_predict_yield_response_multiple_micronutrients(self, service, base_request):
        # Zinc deficient, Boron sufficient
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=0.3,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            ),
            SoilTestResult(
                micronutrient_type=MicronutrientType.BORON,
                level_ppm=1.2,
                sufficiency_range_min_ppm=1.0,
                sufficiency_range_max_ppm=2.0
            )
        ]
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.5,
                cost_per_kg=15.0
            ),
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.BORON,
                application_rate_kg_ha=1.0,
                cost_per_kg=20.0
            )
        ]

        responses = service.predict_yield_response(base_request)

        assert len(responses) == 2

        zinc_response = next(r for r in responses if r.micronutrient_type == MicronutrientType.ZINC)
        assert zinc_response.predicted_yield_increase_kg_ha > 0
        assert zinc_response.confidence_score == pytest.approx(0.8)

        boron_response = next(r for r in responses if r.micronutrient_type == MicronutrientType.BORON)
        assert boron_response.predicted_yield_increase_kg_ha == 0
        assert boron_response.confidence_score == pytest.approx(0.9)

    def test_predict_yield_response_no_soil_test_results(self, service, base_request):
        # No soil test results, but application planned
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.5,
                cost_per_kg=15.0
            )
        ]

        responses = service.predict_yield_response(base_request)

        assert len(responses) == 1
        assert responses[0].micronutrient_type == MicronutrientType.ZINC
        assert responses[0].predicted_yield_increase_kg_ha == 0 # No deficiency detected without soil test
        assert responses[0].confidence_score == pytest.approx(0.2)

    def test_predict_yield_response_no_micronutrient_applications(self, service, base_request):
        # Deficient Zinc, but no application planned
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=0.2,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            )
        ]
        base_request.micronutrient_applications = []

        responses = service.predict_yield_response(base_request)

        assert len(responses) == 0 # No applications, so no yield response predictions

    def test_predict_yield_response_level_at_boundary_min(self, service, base_request):
        # Zinc level exactly at min sufficiency
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=0.5,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            )
        ]
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.5,
                cost_per_kg=15.0
            )
        ]

        responses = service.predict_yield_response(base_request)
        assert responses[0].predicted_yield_increase_kg_ha == 0
        assert responses[0].confidence_score == pytest.approx(0.9)

    def test_predict_yield_response_level_at_boundary_max(self, service, base_request):
        # Zinc level exactly at max sufficiency
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=1.0,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            )
        ]
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.5,
                cost_per_kg=15.0
            )
        ]

        responses = service.predict_yield_response(base_request)
        assert responses[0].predicted_yield_increase_kg_ha == 0
        assert responses[0].confidence_score == pytest.approx(0.9)

    def test_predict_yield_response_no_relevant_application(self, service, base_request):
        # Soil test shows Zinc deficient, but application is for Boron
        base_request.soil_test_results = [
            SoilTestResult(
                micronutrient_type=MicronutrientType.ZINC,
                level_ppm=0.2,
                sufficiency_range_min_ppm=0.5,
                sufficiency_range_max_ppm=1.0
            )
        ]
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.BORON,
                application_rate_kg_ha=1.0,
                cost_per_kg=20.0
            )
        ]

        responses = service.predict_yield_response(base_request)
        assert len(responses) == 1
        assert responses[0].micronutrient_type == MicronutrientType.BORON
        assert responses[0].predicted_yield_increase_kg_ha == 0 # Boron not deficient
        assert responses[0].confidence_score == pytest.approx(0.2) # Low confidence as no soil test for Boron
