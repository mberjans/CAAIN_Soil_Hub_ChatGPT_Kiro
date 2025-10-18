"""
Economic model validation service for fertilizer strategy optimization.

This service evaluates the accuracy of economic assumptions by comparing
model predictions to curated historical scenarios. It verifies price,
cost, and ROI projections against thresholds required by agricultural
economists and generates structured validation reports.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from ..data.economic_validation_dataset import get_economic_validation_dataset
from ..models.economic_validation_models import (
    EconomicScenarioMetrics,
    EconomicValidationSummary,
    ValidationThresholds
)


class EconomicModelValidationService:
    """Validate economic models using curated historical scenarios."""

    def __init__(
        self,
        dataset: Optional[List[Dict[str, Any]]] = None,
        thresholds: Optional[ValidationThresholds] = None
    ) -> None:
        self.logger = logging.getLogger(__name__)
        if dataset is None:
            dataset = get_economic_validation_dataset()
        if thresholds is None:
            thresholds = ValidationThresholds()
        self.dataset = dataset
        self.thresholds = thresholds

    def validate_models(self) -> EconomicValidationSummary:
        """Run full validation and return structured summary results."""
        summary = EconomicValidationSummary()
        summary.threshold_configuration = self.thresholds

        scenario_metrics: Dict[str, EconomicScenarioMetrics] = {}
        price_accuracy_total = 0.0
        price_observation_count = 0
        cost_accuracy_total = 0.0
        cost_observation_count = 0
        roi_accuracy_total = 0.0
        roi_observation_count = 0
        aggregate_issues: List[str] = []
        aggregate_warnings: List[str] = []

        if len(self.dataset) == 0:
            message = "Economic validation dataset is empty"
            aggregate_issues.append(message)
            summary.scenario_metrics = scenario_metrics
            summary.issues = aggregate_issues
            summary.warnings = aggregate_warnings
            summary.passed = False
            return summary

        scenario_index = 0
        for scenario in self.dataset:
            scenario_index = scenario_index + 1
            scenario_id = scenario.get("scenario_id")
            if scenario_id is None:
                scenario_id = f"scenario_{scenario_index}"

            scenario_result = EconomicScenarioMetrics(scenario_id=scenario_id)

            price_accuracy_sum = 0.0
            price_count = 0
            price_observations = scenario.get("price_observations")
            if isinstance(price_observations, list):
                for observation in price_observations:
                    price_accuracy, warning = self._evaluate_price_observation(observation)
                    if price_accuracy is not None:
                        price_accuracy_sum = price_accuracy_sum + price_accuracy
                        price_count = price_count + 1
                        price_accuracy_total = price_accuracy_total + price_accuracy
                        price_observation_count = price_observation_count + 1
                    if warning is not None:
                        scenario_result.warnings.append(warning)

            if price_count > 0:
                scenario_result.price_accuracy = price_accuracy_sum / float(price_count)
                if scenario_result.price_accuracy < self.thresholds.price_accuracy:
                    message = (
                        f"Price accuracy {scenario_result.price_accuracy:.3f} "
                        f"below threshold {self.thresholds.price_accuracy:.3f}"
                    )
                    scenario_result.issues.append(message)
            else:
                scenario_result.warnings.append("No price observations available for validation")

            cost_summary = scenario.get("cost_summary")
            if isinstance(cost_summary, dict):
                cost_accuracy_metrics = self._evaluate_cost_summary(cost_summary)
                if cost_accuracy_metrics is not None:
                    cost_accuracy_value, warning = cost_accuracy_metrics
                    scenario_result.cost_accuracy = cost_accuracy_value
                    cost_accuracy_total = cost_accuracy_total + cost_accuracy_value
                    cost_observation_count = cost_observation_count + 1
                    if cost_accuracy_value < self.thresholds.cost_accuracy:
                        message = (
                            f"Cost accuracy {cost_accuracy_value:.3f} "
                            f"below threshold {self.thresholds.cost_accuracy:.3f}"
                        )
                        scenario_result.issues.append(message)
                    if warning is not None:
                        scenario_result.warnings.append(warning)
            else:
                scenario_result.warnings.append("Cost summary missing from validation scenario")

            roi_summary = scenario.get("roi_summary")
            if isinstance(roi_summary, dict):
                roi_accuracy_metrics = self._evaluate_roi_summary(roi_summary)
                if roi_accuracy_metrics is not None:
                    roi_accuracy_value, warning = roi_accuracy_metrics
                    scenario_result.roi_accuracy = roi_accuracy_value
                    roi_accuracy_total = roi_accuracy_total + roi_accuracy_value
                    roi_observation_count = roi_observation_count + 1
                    if roi_accuracy_value < self.thresholds.roi_accuracy:
                        message = (
                            f"ROI accuracy {roi_accuracy_value:.3f} "
                            f"below threshold {self.thresholds.roi_accuracy:.3f}"
                        )
                        scenario_result.issues.append(message)
                    if warning is not None:
                        scenario_result.warnings.append(warning)
            else:
                scenario_result.warnings.append("ROI summary missing from validation scenario")

            scenario_passed = True
            if scenario_result.price_accuracy is None:
                scenario_passed = False
                scenario_result.issues.append("Price validation not completed")
            if scenario_result.cost_accuracy is None:
                scenario_passed = False
                scenario_result.issues.append("Cost validation not completed")
            if scenario_result.roi_accuracy is None:
                scenario_passed = False
                scenario_result.issues.append("ROI validation not completed")

            if scenario_passed:
                if scenario_result.price_accuracy < self.thresholds.price_accuracy:
                    scenario_passed = False
                if scenario_result.cost_accuracy < self.thresholds.cost_accuracy:
                    scenario_passed = False
                if scenario_result.roi_accuracy < self.thresholds.roi_accuracy:
                    scenario_passed = False

            scenario_result.passed = scenario_passed
            if len(scenario_result.issues) > 0:
                for issue_text in scenario_result.issues:
                    formatted_issue = f"{scenario_id}: {issue_text}"
                    aggregate_issues.append(formatted_issue)
            if len(scenario_result.warnings) > 0:
                for warning_text in scenario_result.warnings:
                    formatted_warning = f"{scenario_id}: {warning_text}"
                    aggregate_warnings.append(formatted_warning)
            scenario_metrics[scenario_id] = scenario_result

        summary.scenario_metrics = scenario_metrics

        if price_observation_count > 0:
            summary.price_accuracy = price_accuracy_total / float(price_observation_count)
            if summary.price_accuracy < self.thresholds.price_accuracy:
                message = (
                    f"Aggregate price accuracy {summary.price_accuracy:.3f} "
                    f"below threshold {self.thresholds.price_accuracy:.3f}"
                )
                aggregate_issues.append(message)
        else:
            summary.price_accuracy = None
            aggregate_issues.append("No price observations found in validation dataset")

        if cost_observation_count > 0:
            summary.cost_accuracy = cost_accuracy_total / float(cost_observation_count)
            if summary.cost_accuracy < self.thresholds.cost_accuracy:
                message = (
                    f"Aggregate cost accuracy {summary.cost_accuracy:.3f} "
                    f"below threshold {self.thresholds.cost_accuracy:.3f}"
                )
                aggregate_issues.append(message)
        else:
            summary.cost_accuracy = None
            aggregate_issues.append("No cost summaries found in validation dataset")

        if roi_observation_count > 0:
            summary.roi_accuracy = roi_accuracy_total / float(roi_observation_count)
            if summary.roi_accuracy < self.thresholds.roi_accuracy:
                message = (
                    f"Aggregate ROI accuracy {summary.roi_accuracy:.3f} "
                    f"below threshold {self.thresholds.roi_accuracy:.3f}"
                )
                aggregate_issues.append(message)
        else:
            summary.roi_accuracy = None
            aggregate_issues.append("No ROI summaries found in validation dataset")

        summary.issues = aggregate_issues
        summary.warnings = aggregate_warnings

        overall_passed = True
        if summary.price_accuracy is None or summary.price_accuracy < self.thresholds.price_accuracy:
            overall_passed = False
        if summary.cost_accuracy is None or summary.cost_accuracy < self.thresholds.cost_accuracy:
            overall_passed = False
        if summary.roi_accuracy is None or summary.roi_accuracy < self.thresholds.roi_accuracy:
            overall_passed = False

        summary.passed = overall_passed
        return summary

    def _evaluate_price_observation(self, observation: Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]:
        """Evaluate individual price observation."""
        if not isinstance(observation, dict):
            return None, "Invalid price observation structure"

        predicted = observation.get("predicted_price")
        actual = observation.get("actual_price")

        if predicted is None or actual is None:
            return None, "Price observation missing predicted or actual value"

        try:
            predicted_value = float(predicted)
            actual_value = float(actual)
        except (TypeError, ValueError):
            return None, "Price observation contains non-numeric values"

        accuracy = self._calculate_accuracy(predicted_value, actual_value)
        warning = None
        if actual_value == 0.0 and predicted_value != 0.0:
            warning = "Actual price is zero; accuracy may be misleading"

        return accuracy, warning

    def _evaluate_cost_summary(self, cost_summary: Dict[str, Any]) -> Optional[Tuple[float, Optional[str]]]:
        """Evaluate cost accuracy for a scenario."""
        predicted_total = cost_summary.get("predicted_total_cost")
        actual_total = cost_summary.get("actual_total_cost")
        predicted_per_acre = cost_summary.get("predicted_cost_per_acre")
        actual_per_acre = cost_summary.get("actual_cost_per_acre")

        if predicted_total is None or actual_total is None:
            return None

        try:
            predicted_total_value = float(predicted_total)
            actual_total_value = float(actual_total)
        except (TypeError, ValueError):
            return None

        total_accuracy = self._calculate_accuracy(predicted_total_value, actual_total_value)

        per_acre_accuracy = None
        if predicted_per_acre is not None and actual_per_acre is not None:
            try:
                predicted_per_acre_value = float(predicted_per_acre)
                actual_per_acre_value = float(actual_per_acre)
                per_acre_accuracy = self._calculate_accuracy(predicted_per_acre_value, actual_per_acre_value)
            except (TypeError, ValueError):
                per_acre_accuracy = None

        combined_accuracy = total_accuracy
        if per_acre_accuracy is not None:
            combined_accuracy = (total_accuracy + per_acre_accuracy) / 2.0

        warning = None
        if actual_total_value == 0.0 and predicted_total_value != 0.0:
            warning = "Actual total cost is zero; accuracy result may be distorted"

        return combined_accuracy, warning

    def _evaluate_roi_summary(self, roi_summary: Dict[str, Any]) -> Optional[Tuple[float, Optional[str]]]:
        """Evaluate ROI prediction accuracy."""
        predicted_roi = roi_summary.get("predicted_roi")
        actual_roi = roi_summary.get("actual_roi")

        if predicted_roi is None or actual_roi is None:
            return None

        try:
            predicted_value = float(predicted_roi)
            actual_value = float(actual_roi)
        except (TypeError, ValueError):
            return None

        accuracy = self._calculate_accuracy(predicted_value, actual_value)
        warning = None
        if actual_value == 0.0 and predicted_value != 0.0:
            warning = "Actual ROI is zero; accuracy result may not be meaningful"

        return accuracy, warning

    def _calculate_accuracy(self, predicted: float, actual: float) -> float:
        """Calculate accuracy as one minus relative error."""
        if actual == 0.0:
            if predicted == 0.0:
                return 1.0
            return 0.0

        error = predicted - actual
        if error < 0.0:
            error = -error

        accuracy = 1.0 - (error / abs(actual))
        if accuracy < 0.0:
            accuracy = 0.0
        if accuracy > 1.0:
            accuracy = 1.0

        return accuracy
