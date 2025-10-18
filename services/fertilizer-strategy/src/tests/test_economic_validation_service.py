"""
Tests for the economic model validation service.

These tests ensure the validation framework verifies price, cost, and ROI
assumptions against curated historical scenarios and respects threshold
configuration.
"""

import pytest

from ..models.economic_validation_models import ValidationThresholds
from ..services.economic_validation_service import EconomicModelValidationService


class TestEconomicModelValidationService:
    """Test suite for economic model validation."""

    def test_validation_passes_with_default_thresholds(self):
        """Economic validation should pass using default thresholds."""
        service = EconomicModelValidationService()
        summary = service.validate_models()

        assert summary.passed is True
        assert summary.price_accuracy is not None
        assert summary.cost_accuracy is not None
        assert summary.roi_accuracy is not None

        assert summary.price_accuracy >= summary.threshold_configuration.price_accuracy
        assert summary.cost_accuracy >= summary.threshold_configuration.cost_accuracy
        assert summary.roi_accuracy >= summary.threshold_configuration.roi_accuracy

        scenario_ids = list(summary.scenario_metrics.keys())
        assert len(scenario_ids) > 0

        for scenario_id in scenario_ids:
            metrics = summary.scenario_metrics[scenario_id]
            assert metrics.passed is True
            assert metrics.price_accuracy is not None
            assert metrics.cost_accuracy is not None
            assert metrics.roi_accuracy is not None

    def test_validation_detects_threshold_failure(self):
        """Validation should fail when thresholds exceed dataset accuracy."""
        strict_thresholds = ValidationThresholds(
            price_accuracy=0.999,
            cost_accuracy=0.999,
            roi_accuracy=0.999
        )
        service = EconomicModelValidationService(thresholds=strict_thresholds)
        summary = service.validate_models()

        assert summary.passed is False

        failure_detected = False
        scenario_ids = list(summary.scenario_metrics.keys())
        for scenario_id in scenario_ids:
            metrics = summary.scenario_metrics[scenario_id]
            if metrics.passed is False:
                failure_detected = True
        assert failure_detected is True

