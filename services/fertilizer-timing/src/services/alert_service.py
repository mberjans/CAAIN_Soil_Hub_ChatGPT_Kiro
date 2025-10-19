"""
Alert generation service for fertilizer timing optimization.
"""

from datetime import datetime
from typing import List

from ..database import TimingAlertRecord
from ..models import (
    ApplicationTiming,
    TimingAlert,
    TimingAlertResponse,
    TimingOptimizationResult,
)


class TimingAlertService:
    """Generate actionable alerts derived from optimization outputs."""

    def generate_alerts(self, result: TimingOptimizationResult) -> TimingAlertResponse:
        alerts: List[TimingAlert] = []

        if result.risk_score > 0.75:
            alerts.append(
                self._build_alert(
                    result.request_id,
                    "critical",
                    "High overall application risk",
                    "Overall risk score exceeds safe threshold. Review weather and operational constraints before applying fertilizer.",
                    "Re-evaluate scheduling, consider additional split applications, and ensure contingency plans are in place."
                )
            )

        for timing in result.optimal_timings:
            timing_alert = self._analyze_timing_risks(result.request_id, timing)
            if timing_alert is not None:
                alerts.append(timing_alert)

        if result.weather_suitability_score < 0.6:
            alerts.append(
                self._build_alert(
                    result.request_id,
                    "warning",
                    "Limited suitable weather windows",
                    "Weather suitability score is low. Application opportunities may be disrupted by forecast conditions.",
                    "Monitor short-term forecasts closely and prepare backup field operations."
                )
            )

        if result.cost_per_acre > 150:
            alerts.append(
                self._build_alert(
                    result.request_id,
                    "info",
                    "High cost per acre",
                    f"Cost per acre estimated at ${result.cost_per_acre:.2f}.",
                    "Validate fertilizer pricing and consider alternative nutrient sources if budgets are constrained."
                )
            )

        response = TimingAlertResponse(
            request_id=result.request_id,
            generated_at=datetime.utcnow(),
            alerts=alerts,
        )
        return response

    def to_records(self, response: TimingAlertResponse) -> List[TimingAlertRecord]:
        records: List[TimingAlertRecord] = []
        for alert in response.alerts:
            record = TimingAlertRecord(
                request_id=response.request_id,
                severity=alert.severity,
                title=alert.title,
                message=alert.message,
                action=alert.action,
            )
            records.append(record)
        return records

    def _analyze_timing_risks(
        self,
        request_id: str,
        timing: ApplicationTiming,
    ) -> TimingAlert | None:
        factors: List[str] = []
        severity = None
        title = None
        message = None
        action = None

        if timing.weather_risk > 0.6:
            severity = "warning"
            title = f"Weather risk for {timing.fertilizer_type} application"
            message = (
                f"Weather risk score of {timing.weather_risk:.2f} indicates potential delays "
                f"around {timing.recommended_date}."
            )
            action = (
                "Monitor hourly forecasts and prepare to adjust the application window. "
                "Consider using equipment suitable for marginal conditions."
            )
            factors.append("High weather risk score")

        if timing.equipment_risk > 0.6:
            severity = "warning"
            title = f"Equipment availability constraint for {timing.fertilizer_type}"
            message = (
                "Equipment availability risk is elevated. Confirm machinery readiness and labor schedules."
            )
            action = "Coordinate with equipment managers to secure necessary applicators and staff."
            factors.append("Equipment availability risk")

        if timing.timing_risk > 0.7:
            severity = "critical"
            title = f"Critical timing window for {timing.fertilizer_type}"
            message = (
                "Timing risk exceeds safe threshold. Missing this window may reduce crop response."
            )
            action = "Commit resources to ensure application occurs on schedule. Prepare contingency labor."
            factors.append("High timing risk")

        if severity is None:
            return None

        alert = TimingAlert(
            request_id=request_id,
            severity=severity,
            title=title,
            message=message,
            action=action,
            factors=factors,
        )
        return alert

    def _build_alert(
        self,
        request_id: str,
        severity: str,
        title: str,
        message: str,
        action: str,
    ) -> TimingAlert:
        alert = TimingAlert(
            request_id=request_id,
            severity=severity,
            title=title,
            message=message,
            action=action,
        )
        return alert


__all__ = ["TimingAlertService"]
