
import pytest
from datetime import date
from uuid import uuid4

from services.recommendation_engine.src.models.micronutrient_models import (
    MicronutrientType,
    MicronutrientApplication,
    CropYieldData,
    MicronutrientYieldResponse,
    YieldEconomicPredictionRequest,
    EconomicReturnPrediction
)
from services.recommendation_engine.src.services.economic_return_calculation_service import EconomicReturnCalculationService

class TestEconomicReturnCalculationService:

    @pytest.fixture
    def service(self):
        return EconomicReturnCalculationService()

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
            soil_test_results=[], # Not directly used by this service, but part of request
            micronutrient_applications=[],
            application_date=date(2025, 5, 1),
            area_ha=10.0
        )

    def test_calculate_economic_returns_positive_net_return(self, service, base_request):
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.0,
                cost_per_kg=10.0
            )
        ]
        yield_responses = [
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.ZINC,
                predicted_yield_increase_kg_ha=200.0,
                predicted_total_yield_kg_ha=10200.0,
                confidence_score=0.8
            )
        ]

        returns = service.calculate_economic_returns(base_request, yield_responses)

        assert len(returns) == 1
        assert returns[0].micronutrient_type == MicronutrientType.ZINC
        # Total application cost: 2.0 kg/ha * 10.0 $/kg * 10.0 ha = 200.0 $
        assert returns[0].total_application_cost == pytest.approx(200.0)
        # Additional revenue: 200.0 kg/ha * 0.25 $/kg * 10.0 ha = 500.0 $
        assert returns[0].additional_revenue_from_yield_increase == pytest.approx(500.0)
        # Net economic return: 500.0 - 200.0 = 300.0 $
        assert returns[0].net_economic_return == pytest.approx(300.0)
        # ROI: (300.0 / 200.0) * 100 = 150.0 %
        assert returns[0].roi_percentage == pytest.approx(150.0)

    def test_calculate_economic_returns_negative_net_return(self, service, base_request):
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.BORON,
                application_rate_kg_ha=1.0,
                cost_per_kg=25.0
            )
        ]
        yield_responses = [
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.BORON,
                predicted_yield_increase_kg_ha=50.0,
                predicted_total_yield_kg_ha=10050.0,
                confidence_score=0.7
            )
        ]

        returns = service.calculate_economic_returns(base_request, yield_responses)

        assert len(returns) == 1
        assert returns[0].micronutrient_type == MicronutrientType.BORON
        # Total application cost: 1.0 kg/ha * 25.0 $/kg * 10.0 ha = 250.0 $
        assert returns[0].total_application_cost == pytest.approx(250.0)
        # Additional revenue: 50.0 kg/ha * 0.25 $/kg * 10.0 ha = 125.0 $
        assert returns[0].additional_revenue_from_yield_increase == pytest.approx(125.0)
        # Net economic return: 125.0 - 250.0 = -125.0 $
        assert returns[0].net_economic_return == pytest.approx(-125.0)
        # ROI: (-125.0 / 250.0) * 100 = -50.0 %
        assert returns[0].roi_percentage == pytest.approx(-50.0)

    def test_calculate_economic_returns_zero_yield_increase(self, service, base_request):
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.COPPER,
                application_rate_kg_ha=0.5,
                cost_per_kg=30.0
            )
        ]
        yield_responses = [
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.COPPER,
                predicted_yield_increase_kg_ha=0.0,
                predicted_total_yield_kg_ha=10000.0,
                confidence_score=0.9
            )
        ]

        returns = service.calculate_economic_returns(base_request, yield_responses)

        assert len(returns) == 1
        assert returns[0].micronutrient_type == MicronutrientType.COPPER
        # Total application cost: 0.5 kg/ha * 30.0 $/kg * 10.0 ha = 150.0 $
        assert returns[0].total_application_cost == pytest.approx(150.0)
        # Additional revenue: 0.0 kg/ha * 0.25 $/kg * 10.0 ha = 0.0 $
        assert returns[0].additional_revenue_from_yield_increase == pytest.approx(0.0)
        # Net economic return: 0.0 - 150.0 = -150.0 $
        assert returns[0].net_economic_return == pytest.approx(-150.0)
        # ROI: (-150.0 / 150.0) * 100 = -100.0 %
        assert returns[0].roi_percentage == pytest.approx(-100.0)

    def test_calculate_economic_returns_multiple_micronutrients(self, service, base_request):
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.0,
                cost_per_kg=10.0
            ),
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.BORON,
                application_rate_kg_ha=1.0,
                cost_per_kg=25.0
            )
        ]
        yield_responses = [
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.ZINC,
                predicted_yield_increase_kg_ha=200.0,
                predicted_total_yield_kg_ha=10200.0,
                confidence_score=0.8
            ),
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.BORON,
                predicted_yield_increase_kg_ha=50.0,
                predicted_total_yield_kg_ha=10050.0,
                confidence_score=0.7
            )
        ]

        returns = service.calculate_economic_returns(base_request, yield_responses)

        assert len(returns) == 2

        zinc_return = next(r for r in returns if r.micronutrient_type == MicronutrientType.ZINC)
        assert zinc_return.net_economic_return == pytest.approx(300.0)
        assert zinc_return.roi_percentage == pytest.approx(150.0)

        boron_return = next(r for r in returns if r.micronutrient_type == MicronutrientType.BORON)
        assert boron_return.net_economic_return == pytest.approx(-125.0)
        assert boron_return.roi_percentage == pytest.approx(-50.0)

    def test_calculate_economic_returns_no_applications(self, service, base_request):
        base_request.micronutrient_applications = []
        yield_responses = []

        returns = service.calculate_economic_returns(base_request, yield_responses)
        assert len(returns) == 0

    def test_calculate_economic_returns_mismatched_applications_and_yield_responses(self, service, base_request):
        # Application for Zinc, but yield response only for Boron (should not happen in real flow)
        base_request.micronutrient_applications = [
            MicronutrientApplication(
                micronutrient_type=MicronutrientType.ZINC,
                application_rate_kg_ha=2.0,
                cost_per_kg=10.0
            )
        ]
        yield_responses = [
            MicronutrientYieldResponse(
                micronutrient_type=MicronutrientType.BORON,
                predicted_yield_increase_kg_ha=50.0,
                predicted_total_yield_kg_ha=10050.0,
                confidence_score=0.7
            )
        ]

        # The service should only calculate for applications it has yield responses for
        # Or, more robustly, it should match applications to yield responses
        # For this test, we expect it to calculate for Zinc, but with 0 yield increase if not found in yield_responses
        # Let's adjust the service logic to handle this gracefully.
        # For now, the test expects it to calculate for Zinc, but with 0 additional revenue if no matching yield response.

        returns = service.calculate_economic_returns(base_request, yield_responses)
        assert len(returns) == 1
        assert returns[0].micronutrient_type == MicronutrientType.ZINC
        assert returns[0].total_application_cost == pytest.approx(200.0)
        assert returns[0].additional_revenue_from_yield_increase == pytest.approx(0.0) # No matching yield response
        assert returns[0].net_economic_return == pytest.approx(-200.0)
        assert returns[0].roi_percentage == pytest.approx(-100.0)
