import logging

from ..schemas.micronutrient_schemas import EconomicReturnPredictionRequest, EconomicReturnPredictionResponse

logger = logging.getLogger(__name__)

class EconomicPredictionService:
    """
    Service to predict the economic return and ROI of micronutrient application.
    """

    async def predict_economic_return(
        self, request: EconomicReturnPredictionRequest
    ) -> EconomicReturnPredictionResponse:
        """
        Predicts the economic return and ROI based on micronutrient application costs
        and predicted yield increase.

        Args:
            request: An EconomicReturnPredictionRequest object containing all necessary input data.

        Returns:
            An EconomicReturnPredictionResponse object with economic metrics.
        """
        logger.info(f"Predicting economic return for farm {request.farm_context.farm_location_id}")

        # Calculate total micronutrient cost
        total_micronutrient_cost = (
            request.micronutrient_application.cost_per_unit
            * request.micronutrient_application.application_rate_per_acre
            * request.micronutrient_application.total_acres_applied
        )

        # Calculate additional revenue from yield increase
        additional_revenue_from_yield_increase = (
            request.predicted_yield_response.predicted_yield_per_acre
            - request.predicted_yield_response.baseline_yield_per_acre
        ) * request.micronutrient_application.total_acres_applied * request.crop_details.expected_market_price_per_unit

        # Calculate net economic return
        net_economic_return = additional_revenue_from_yield_increase - total_micronutrient_cost

        # Calculate ROI percentage
        roi_percentage = (
            (net_economic_return / total_micronutrient_cost) * 100
            if total_micronutrient_cost > 0
            else 0.0
        )

        # Calculate break-even yield increase per acre
        break_even_yield_increase_per_acre = (
            total_micronutrient_cost
            / (request.micronutrient_application.total_acres_applied * request.crop_details.expected_market_price_per_unit)
            if (request.micronutrient_application.total_acres_applied * request.crop_details.expected_market_price_per_unit) > 0
            else 0.0
        )

        explanation = self._generate_explanation(
            request,
            total_micronutrient_cost,
            additional_revenue_from_yield_increase,
            net_economic_return,
            roi_percentage,
            break_even_yield_increase_per_acre
        )

        return EconomicReturnPredictionResponse(
            total_micronutrient_cost=total_micronutrient_cost,
            additional_revenue_from_yield_increase=additional_revenue_from_yield_increase,
            net_economic_return=net_economic_return,
            roi_percentage=roi_percentage,
            break_even_yield_increase_per_acre=break_even_yield_increase_per_acre,
            explanation=explanation,
        )

    def _generate_explanation(
        self,
        request: EconomicReturnPredictionRequest,
        total_cost: float,
        additional_revenue: float,
        net_return: float,
        roi: float,
        break_even: float
    ) -> str:
        """
        Generates a human-readable explanation for the economic prediction.
        """
        explanation_parts = [
            f"The total estimated cost for the {request.micronutrient_application.micronutrient_type} application across {request.micronutrient_application.total_acres_applied:.2f} acres is ${total_cost:.2f}.",
            f"Based on the predicted yield increase and an expected market price of ${request.crop_details.expected_market_price_per_unit:.2f} per {request.crop_details.yield_unit},",
            f"you could expect an additional revenue of ${additional_revenue:.2f}.",
            f"This results in a net economic return of ${net_return:.2f} and an ROI of {roi:.2f}%\n",
            f"To break even on the cost of this micronutrient application, you would need a yield increase of {break_even:.2f} {request.crop_details.yield_unit} per acre."
        ]

        return " ".join(explanation_parts)